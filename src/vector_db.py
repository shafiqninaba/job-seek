"""
This module contains the VectorDB class which is responsible for interacting with Qdrant.
It provides methods to create a collection and upload vectors to Qdrant.
"""

from dotenv import load_dotenv
import os
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

logger.add("logs/vector_db.log", format="{time} {level} {message}", level="DEBUG")


class VectorDB:
    def __init__(self):
        """
        Initialize the VectorDB with a Qdrant client.
        """
        load_dotenv()
        self.QDRANT_URL = os.getenv("QDRANT_URL")

        if not self.QDRANT_URL:
            logger.error("QDRANT_URL is not set")
            self.client = None
        else:
            logger.debug("Initializing QdrantClient")
            self.client = QdrantClient(url=self.QDRANT_URL)

    def upload_vectors(self, document: str, metadata: dict, id: str):
        """
        This method uploads vectors to Qdrant using FastEmbed.

        Args:
            document (str): The document text to embed and store
            metadata (dict): Additional metadata to store with the document
            id (str): Unique identifier for the document
        """
        if not self.client:
            logger.error("QdrantClient is not initialized")
            return

        logger.debug("Adding document to collection")
        self.client.add(
            collection_name="demo_collection",
            documents=[document],
            metadata=[metadata],
            ids=[id],
        )

    def create_collection(self):
        """
        This method creates a new collection in Qdrant.
        """
        if not self.client:
            logger.error("QdrantClient is not initialized")
            return

        logger.debug("Creating collection")
        self.client.create_collection(
            collection_name="demo_collection",
            vectors_config=VectorParams(size=100, distance=Distance.COSINE),
        )


if __name__ == "__main__":
    vector_db = VectorDB()
    vector_db.create_collection()
    # Example usage:
    # vector_db.upload_vectors("Sample document", {"source": "test"}, str(uuid4()))
