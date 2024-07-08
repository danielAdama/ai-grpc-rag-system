import pymupdf
import spacy
from io import BytesIO
import os
import uuid
from datetime import datetime as dt
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List, Dict, Any
from config import BASE_DIR
import re
# from src.schemas import faq_schemas
from config.qdrant_client import vector_db
from config.logger import Logger

logger = Logger(__name__)

class PDFService:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.source_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
        self.issn_pattern = r'ISSN:\s*[^\s]+'
        self.title_pattern = r'^\s*([^\n]+)\s*$'
        self.author_pattern = r'^\s*(?:\d+\s*)?(author[s]?:?)\s*\n*(.+)$'
        self.keyword_pattern = r'^Keywords:\s*(.*)$'
        self.source = ''
        self.title = ''
        self.metadata = None
        self.cleandocs = []

    @staticmethod
    def generate_id(content):
        namespace = uuid.UUID('12345678-1234-5678-1234-567812345678')
        return str(uuid.uuid5(namespace, content))

    def get_text_after(self, pattern, text):
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return text.split(match.group(0))[1].strip()
        return ''

    def extract_source_title(self, text):
        """
        Extract the source URL and title from the given text.

        Parameters:
        text (str): The text to extract the source and title from.

        Returns:
        tuple: A tuple containing the source URL and title.
        """

        try:
            source = re.search(self.source_pattern, text).group(0)
        except AttributeError:
            pass

        if source and "researchgate.net" in source:
            after_source_text = self.get_text_after(self.source_pattern, text)
            try:
                title = re.search(
                    self.title_pattern, 
                    after_source_text, 
                    re.MULTILINE
                ).group(1).strip()
            except AttributeError:
                pass
        else:
            after_issn_text = self.get_text_after(self.issn_pattern, text)
            if after_issn_text:
                for line in after_issn_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('DOI:'):
                        title = line
                        break

        return source, title

    def extract_author(self, text):
        """
        Extract the author name(s) from the given text.

        Parameters:
        text (str): The text to extract the author name(s) from.

        Returns:
        str: The author name(s).
        """
        try:
            author = re.search(
                self.author_pattern, 
                text, 
                re.IGNORECASE | re.MULTILINE
            ).group(2).strip()
        except AttributeError:
            author = ''
        return author

    def extract_keywords(self, text):
        """
        Extract the keywords from the given text.

        Parameters:
        text (str): The text to extract the keywords from.

        Returns:
        str: The keywords.
        """
        try:
            keywords = re.search(
                self.keyword_pattern, 
                text, 
                re.MULTILINE
            ).group(1).strip()
        except AttributeError:
            keywords = ''
        return keywords

    def clean_metadata(self, metadata, text, page_1_text):
        source, title = self.extract_source_title(text)
        author = self.extract_author(text) or self.extract_author(page_1_text)
        keywords = self.extract_keywords(text) or self.extract_keywords(page_1_text)

        update_fields = {
            'source': source,
            'title': title, 
            'author': author, 
            'keywords': keywords, 
            'uploaded_at': dt.now().strftime("%Y-%m-%d %H:%M")
        }
        remove_fields = {'modDate', 'producer', 'creator', 'creationDate'}

        filtered_metadata = {k: v for k, v in metadata.items() if k not in remove_fields}
        filtered_metadata.update({k: v for k, v in update_fields.items() if v})

        return filtered_metadata

    def clean_chunk(self, chunk, metadata):
        doc = self.nlp(chunk.page_content)
        tokens = [self.lemmatize(token) for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
        return Document(page_content=' '.join(tokens), metadata=metadata)

    def lemmatize(self, token):
        tag = token.tag_
        if tag.startswith('NN') or tag.startswith('VB') or tag.startswith('RB') or tag.startswith('JJ'):
            return token.lemma_
        return token.text
    
    def clean_text(self, collection_name: str, filename: str = "Education_in_Nigeria_A_Futuristic_Perspective.pdf"):
        loader = PyMuPDFLoader(str(BASE_DIR / "pdf" / "uploads" / filename))
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        batch_size = 20
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            metadata = self.clean_metadata(
                batch[0].metadata,
                batch[0].page_content,
                batch[1].page_content
            ) if batch[0].metadata.get("page") == 0 else metadata

            for chunk in batch:
                doc = self.nlp(chunk.page_content)
                tokens = (' '.join(self.lemmatize(token) for token in doc if not token.is_stop and not token.is_punct and not token.is_space))

                _id = self.generate_id(tokens)
                metadata['_collection_name'] = collection_name
                metadata['_id'] = _id

                self.cleandocs.append(Document(
                    page_content=tokens, 
                    metadata=metadata
                ))

        return self.cleandocs



    
    # def embed_document(
    #         self,
    #     ):
    #     try:
    #         details = info.model_dump()
    #         file_bytes = await file.read()
    #         file_type = os.path.splitext(filename)[1][1:]
    #         # if file_type not in ['pdf']:
    #         #     raise UnsupportedFileFormatException()
    #         df = self.read_file(file_bytes, file_type)

    #     except Exception as ex:
    #         pass
    #         # raise InternalServerException(str(ex))
        
    #     metadata_template = {
    #         'source': details.get('source'),
    #         'file_name': filename,
    #         'total_pages': len(df),
    #         'format': file_type,
    #         'title': details.get('title'),
    #         'uploaded_at': dt.now().strftime("%Y-%m-%d %H:%M"),
    #         '_collection_name': details.get('collection_name'),
    #     }

    #     documents = [
    #         {
    #             "page_content": self.format_text(
    #                 row['Category'], row['Question'], row['Answer']
    #             ),
    #             "metadata": {
    #                 **metadata_template,
    #                 '_id': self.generate_id(self.format_text(
    #                     row['Category'], row['Question'], row['Answer']
    #                 )), #generate deterministic id to prevent duplicates
    #                 'row': i
    #             }
    #         }
    #         for i, row in df.iterrows()
    #     ]

    #     vector_db.run(documents)
    #     logger.info("Documents embedded successfully")
        
    #     return {"message": "Documents embedded successfully"}