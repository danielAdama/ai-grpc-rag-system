import pathlib
import sys

current_dir = pathlib.Path(__file__).parent
previous_dir = current_dir.parent.parent.parent
sys.path.append(str(previous_dir))

import pymupdf
import spacy
from io import BytesIO
import os
import uuid
import subprocess
from datetime import datetime as dt
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from gen_ai.RAGLLM import AIGenerator

from typing import List, Dict, Any, Union
from config import BASE_DIR, PROMPT_DIR, client, redis_client
import re
from config.qdrant_client import vector_db
from config.logger import Logger

logger = Logger(__name__)

class PDFService:
    SOURCE_PATTERN = r'(https?://[^\s]+|www\.[^\s]+)'
    ISSN_PATTERN = r'ISSN:\s*[^\s]+'
    TITLE_PATTERN = r'^\s*([^\n]+)\s*$'
    AUTHOR_PATTERN = r'^\s*(?:\d+\s*)?(author[s]?:?)\s*\n*(.+)$'
    KEYWORD_PATTERN = r'^Keywords:\s*(.*)$'

    def __init__(self):
        self.check_model_downloaded()
        self.__system_template = self.load_file(PROMPT_DIR / "system_template.txt")
        self.__user_template = self.load_file(PROMPT_DIR / "user_template.txt")
        self.__nlp = spacy.load("en_core_web_sm")
        self.source_pattern = self.SOURCE_PATTERN
        self.issn_pattern = self.ISSN_PATTERN
        self.title_pattern = self.TITLE_PATTERN
        self.author_pattern = self.AUTHOR_PATTERN
        self.keyword_pattern = self.KEYWORD_PATTERN
        self.source = ''
        self.title = ''
        self.metadata = None
        self.cleandocs = []
    @staticmethod
    def load_file(path: pathlib.Path):
        with open(str(path), 'r') as file:
            return file.read()

    @staticmethod
    def check_model_downloaded():
        if not spacy.util.is_package("en_core_web_sm"):
            logger.warning("'en_core_web_sm' model not found. Downloading it now...")
            makefile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
            subprocess.check_call(["make", "-C", makefile_dir, "download_spacy_packages"])
            logger.info("'en_core_web_sm' model downloaded.")

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

    def lemmatize(self, token):
        tag = token.tag_
        if tag.startswith('NN') or tag.startswith('VB') or tag.startswith('RB') or tag.startswith('JJ'):
            return token.lemma_
        return token.text
    
    def clean_text(
            self,
            document_type: str,
            collection_name: str, 
            filepath: str
        ):
        loader = PyMuPDFLoader(filepath)
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
                doc = self.__nlp(chunk.page_content)
                tokens = (' '.join(self.lemmatize(token) for token in doc if not token.is_stop and not token.is_punct and not token.is_space))

                # Split the tokens into chunks and generate a new ID for each chunk
                token_chunks = text_splitter.split_text(tokens)
                for token_chunk in token_chunks:
                    _id = self.generate_id(token_chunk)
                    metadata['document_type'] = document_type
                    metadata['_collection_name'] = collection_name
                    metadata['_id'] = _id

                    self.cleandocs.append(Document(
                        page_content=token_chunk,
                        metadata=metadata.copy()
                    ))

        return self.cleandocs
    
    def embed_document(
            self,
            collection_name: Union[str, None],
            filename: Union[str, None],
            document_type: Union[str, None]
        ):
        """
        Upload and encode PDF document.
        """
        if not collection_name or not filename or not document_type:
            logger.error(f"Please specify the collection, filename, and document_type")
            return
        filepath = str(BASE_DIR / "src" / "pdf" /"uploads" / filename)
        documents = self.clean_text(document_type, collection_name, filepath)
        try:
            vector_db.run(documents)
            logger.info(f"{filename} embedded and inserted successfully")
        except Exception as ex:
            logger.error(f"{filename} not inserted {ex}")
        
        return {"message": f"{filename} embedded successfully"}
    
    def search(
            self, 
            query
        ):
        """
        Search for a document using the vector database.
        """
        if not query:
            logger.error(f"Please specify the query")
            return
        result = vector_db.search(query)
        logger.info("Results retrieved successfully")
        return {"result": result}
    
    def summarize(
        self,
        query: str,
        user_id: str = "test-user"
    ):
        ai_init = AIGenerator(
            system_prompt=self.__system_template,
            context=self.search(query)["result"],
            client=client,
            redis_client=redis_client,
            tools=None,
            names_to_functions=None,
            user_id=user_id
        )
        summarizer = ai_init.run_conversation(
            self.__user_template,
            query
        )

        return {"result": summarizer}