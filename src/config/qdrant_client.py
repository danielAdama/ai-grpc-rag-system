from schemas.search_schema import MatchAnyOrInterval
from qdrant_client import QdrantClient
from qdrant_client.models import (
    UpdateStatus,
    models,
    Distance,
    PointStruct,
    Filter, 
    FieldCondition, 
    MatchAny, 
    DatetimeRange,
    Batch
)
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_fixed
from langchain.docstore.document import Document
import numpy as np
from datetime import datetime as dt
from tqdm import tqdm
import os
from sentence_transformers import SentenceTransformer
from config.config_helper import Configuration
from config.logger import Logger
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
logger = Logger(__name__)

config = Configuration().get_config('qdrant')

class QdrantVectorDB:
    CONTENT_KEY = "page_content"
    METADATA_KEY = "metadata"
    
    def __init__(
            self,
            model_name: str = config['model_name'],
            collection_name: str = config['collection_name'],
            max_attempts: int = config['max_attempts'], 
            wait_time_seconds: int = config['wait_time_seconds'],
            default_segment_number: int = config['default_segment_number'],
            indexing_threshold: int = config['indexing_threshold'],
            batch_size: int = config['batch_size'],
            limit: int = config['limit'],
            is_batch: bool = config['is_batch'],
            content_payload_key: str = CONTENT_KEY,
            metadata_payload_key: str = METADATA_KEY
        ):
        self.__model_name = model_name
        self.__collection_name = collection_name
        self.__client = QdrantClient(
            url=os.environ.get("QDRANT_URL"), 
            api_key=os.environ.get("QDRANT_API_KEY")
        )
        self.__sentence_model = SentenceTransformer(self.__model_name)
        self.__is_batch = is_batch
        self.__limit = limit
        self.__default_segment_number = default_segment_number
        self.__indexing_threshold = indexing_threshold
        self.__batch_size = batch_size
        self.__max_attempts = max_attempts
        self.__wait_time_seconds = wait_time_seconds
        self.__content_payload_key = content_payload_key
        self.__metadata_payload_key = metadata_payload_key

    def encode(self, docs: List[str]) -> np.ndarray:
        """
        Encode a list of documents in batches using the Ember model.

        :param docs: The list of documents to encode.
        :return: The embeddings for the documents as a NumPy array.
        """
        @retry(stop=stop_after_attempt(self.__max_attempts), wait=wait_fixed(self.__wait_time_seconds))
        def encode_batch(batch_docs: List[str]) -> np.ndarray:
            try:
                return self.__sentence_model.encode([doc.page_content for doc in batch_docs])
            except Exception:
                return self.__sentence_model.encode(batch_docs)
        
        embeddings = []
        try:
            for i in tqdm(range(0, len(docs), self.__batch_size)):
                batch_docs = docs[i:i+self.__batch_size]
                batch_embeddings = encode_batch(batch_docs)
                embeddings.append(batch_embeddings)

            embeddings = np.concatenate(embeddings)

            if self.__sentence_model.get_sentence_embedding_dimension() == embeddings.shape[1]:
                return embeddings
            else:
                raise logger.error(f"The embeddings have an incorrect dimension of {embeddings.shape[1]}.")
        except Exception as ex:
            raise logger.error(f"Attempt failed. Retrying Batch... Error: {str(ex)}")
        
    def generate_points(self, docs: List[Document]) -> List[Dict[str, Any]]:
        """
        Generate a list of points by encoding the documents using the Ember model and combining the embeddings with the metadata.

        :param docs: The list of documents to encode.
        :return: A list of points with the embeddings and metadata.
        """
        # Encode the documents in batches
        embeddings = self.encode([doc['page_content'] for doc in docs])
        logger.info("Embedding Completed")

        # Combine the embeddings with the metadata
        points_list = [
            {
                "id": doc.get('metadata')["_id"],
                "vector": content_embedding,
                "payload": {
                    self.__metadata_payload_key: doc['metadata'],
                    self.__content_payload_key: doc['page_content'],
                },
            }
            for (doc, content_embedding) in zip(docs, embeddings)
        ]
        logger.info("Generating points")

        return points_list

    def get_or_create_collection(self):
        try:
            self.__client.get_collection(collection_name=self.__collection_name)
            logger.info(f"Collection '{self.__collection_name}' already exists----- Using {self.__collection_name} collection.")
            
        except Exception:
            is_created = self.__client.create_collection(
                collection_name=self.__collection_name,
                vectors_config=models.VectorParams(
                    size=self.__sentence_model.get_sentence_embedding_dimension(), 
                    distance=Distance.COSINE
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    default_segment_number=self.__default_segment_number,
                    indexing_threshold=self.__indexing_threshold,
                ),
                quantization_config=models.BinaryQuantization(
                    binary=models.BinaryQuantizationConfig(always_ram=True),
                )
            )
            
            if is_created:
                logger.info(f"Collection '{self.__collection_name}' does not exist. Creating {self.__collection_name} collection.")
            else:
                logger.error(f"{self.__collection_name}' Collection was not created.")

    def upsert_points(self, points_list: List[Dict[str, Any]]) -> None:
        """
        Upsert a list of points into the specified collection with retry.

        :param points_list: The list of points to upsert.
        """
        @retry(stop=stop_after_attempt(self.__max_attempts), wait=wait_fixed(self.__wait_time_seconds))
        def upsert_batch(batch_data: List[Dict[str, Any]]) -> None:
            """
            Upsert a batch of points into the specified collection.

            :param batch_data: The batch of points to upsert.
            """
            try:
                batch_ids = [point['id'] for point in batch_data]
                existing_ids = self.__client.get_collection(collection_name=self.__collection_name).points_count
                new_ids = [id for id in batch_ids if id not in existing_ids]
                if not new_ids:
                    logger.info("All documents already exist in the collection. Skipping upsert.")
                    return
                batch_vectors = [point['vector'] for point in batch_data if point['id'] in new_ids]
                batch_payloads = [point['payload'] for point in batch_data if point['id'] in new_ids]
                upserted = self.__client.upsert(
                    collection_name=self.__collection_name,
                    points=Batch(
                        ids=new_ids,
                        vectors=batch_vectors,
                        payloads=batch_payloads
                    )
                )
                if upserted.status == UpdateStatus.COMPLETED:
                    logger.info("Records inserted successfully.")
            except Exception as ex:
                raise logger.error(f"Attempt failed. Retrying Batch... {str(ex)}")

        @retry(stop=stop_after_attempt(self.__max_attempts), wait=wait_fixed(self.__wait_time_seconds))
        def upsert(points_list: List[Dict[str, Any]]) -> None:
            """
            Upsert a list of points into the specified collection.

            :param points_list: The list of points to upsert.
            """
            try:
                points = [PointStruct(**point) for point in points_list]
                upserted = self.__client.upsert(collection_name=self.__collection_name, points=points)
                return upserted
            except Exception as ex:
                raise logger.error(f"Attempt failed. Retrying... {str(ex)}")
        
        if self.__is_batch:
            for i in tqdm(range(0, len(points_list), self.__batch_size)):
                batch_data = points_list[i:i+self.__batch_size]
                upsert_batch(batch_data)
        else:
            upsert(points_list)
    
    def refine_result(self, filters):
        if filters is None:
            return None

        filter_conds = []
        for field, value in filters.items():
            if value.any is not None:
                filter_conds.append(FieldCondition(key=field, match=MatchAny(any=value.any)))
            elif any([value.gt, value.gte, value.lt, value.lte]):
                range_params = {k: v for k, v in [
                    ("gt", value.gt), 
                    ("gte", value.gte), 
                    ("lt", value.lt), 
                    ("lte", value.lte)
                ] if v is not None}
                filter_conds.append(FieldCondition(key=field, range=DatetimeRange(**range_params)))

        return Filter(must=filter_conds) if filter_conds else None
        
    def search(self, query, filters: Dict[str, MatchAnyOrInterval] = None):
        query_vector = self.__sentence_model.encode(query)
        filter_obj = self.refine_result(filters)

        search_params = {
            "collection_name": self.__collection_name,
            "query_vector": query_vector,
            "with_payload": True,
            "with_vectors": False,
            "limit": self.__limit
        }

        if filter_obj:
            search_params["query_filter"] = filter_obj

        hits = self.__client.search(**search_params)

        # Convert the search results to a list of Document objects
        results = [
            Document(
                page_content=hit.payload[self.__content_payload_key],
                metadata=hit.payload[self.__metadata_payload_key],
            )
            for hit in hits
        ]

        return results

    def run(self, docs: List[Document]):
        self.get_or_create_collection()
        points_list = self.generate_points(docs)
        self.upsert_points(points_list)


vector_db = QdrantVectorDB()