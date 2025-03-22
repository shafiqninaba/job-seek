"""
This script is the main entry point for the Firecrawl scraper.
It initializes the FireCrawler class and starts the crawl job.
"""

from firecrawl import FirecrawlApp
import asyncio
import nest_asyncio
from dotenv import load_dotenv
import os
from loguru import logger
from src.vector_db import VectorDB
from uuid import uuid4


class FireCrawler:
    """
    A class to handle web crawling using the Firecrawl service.
    """

    def __init__(self):
        """
        Initialize the FireCrawler instance.
        Sets up logging, loads environment variables, and initializes required components.
        """
        # Set up logging
        logger.add(
            "logs/firecrawl.log", format="{time} {level} {message}", level="DEBUG"
        )

        # Load environment variables
        load_dotenv()

        # Initialize vector database
        self.qdrant = VectorDB()

        # Initialize FirecrawlApp if API URL is available
        firecrawl_api_url = os.getenv("FIRECRAWL_API_URL")
        if not firecrawl_api_url:
            logger.error("FIRECRAWL_API_URL is not set")
            self.app = None
        else:
            logger.debug("Initializing FirecrawlApp")
            self.app = FirecrawlApp(api_url=firecrawl_api_url)
            nest_asyncio.apply()

    def on_document(self, detail):
        """
        Event handler for document events.

        Args:
            detail (dict): Document details from the crawl.
        """
        logger.debug(f"Scraped: {detail['data']['metadata']['url']}")
        self.qdrant.upload_vectors(
            document=detail["data"]["markdown"],
            metadata=detail["data"]["metadata"],
            id=str(uuid4()),
        )

    def on_error(self, detail):
        """
        Event handler for error events.

        Args:
            detail (dict): Error details from the crawl.
        """
        logger.error(detail["error"])

    def on_done(self, detail):
        """
        Event handler for completion events.

        Args:
            detail (dict): Completion details from the crawl.
        """
        logger.info(f"DONE {detail['status']}")

    async def crawl(self, url, limit=100):
        """
        Start a crawl job for the given URL with specified limit.

        Args:
            url (str): The URL to crawl.
            limit (int): The maximum number of pages to crawl.

        Returns:
            bool: True if crawl was successful, False otherwise.
        """
        if not self.app:
            logger.error("FirecrawlApp not initialized. Check API URL.")
            return False

        # Initiate the crawl job and get the watcher
        watcher = self.app.crawl_url_and_watch(url, {"limit": limit})

        # Add event listeners
        watcher.add_event_listener("document", self.on_document)
        watcher.add_event_listener("error", self.on_error)
        watcher.add_event_listener("done", self.on_done)

        # Start the watcher
        await watcher.connect()
        return True


if __name__ == "__main__":
    # Create a crawler instance
    crawler = FireCrawler()

    # Define the URL to crawl
    url = "https://www.firecrawl.dev/"

    # Run the crawler
    asyncio.run(crawler.crawl(url))
