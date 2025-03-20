from firecrawl import FirecrawlApp
import asyncio
import nest_asyncio

from dotenv import load_dotenv
import os
from loguru import logger

# set loguru logger
logger.add("logs/firecrawl.log", format="{time} {level} {message}", level="DEBUG")

# Define the main function
async def firecrawler(url: str, limit: int=50):

    # Check if FIRECRAWL_API_URL is set
    if not os.getenv("FIRECRAWL_API_URL"):
        logger.error("FIRECRAWL_API_URL is not set")
        return
    
    # Initialize the FirecrawlApp
    app = FirecrawlApp(api_url=os.getenv("FIRECRAWL_API_URL"))
    # inside an async function...
    nest_asyncio.apply()

    # Define event handlers
    def on_document(detail):
        logger.debug(f"Scraped: {detail["data"]["metadata"]["url"]}")

    def on_error(detail):
        logger.error(detail["error"])

    def on_done(detail):
        logger.info(f"DONE {detail["status"]}")

        # Function to start the crawl and watch process

    async def start_crawl_and_watch():
        # Initiate the crawl job and get the watcher
        watcher = app.crawl_url_and_watch(url, {"limit": limit})

        # Add event listeners
        watcher.add_event_listener("document", on_document)
        watcher.add_event_listener("error", on_error)
        watcher.add_event_listener("done", on_done)

        # Start the watcher
        await watcher.connect()

    # Run the event loop
    await start_crawl_and_watch()


if __name__ == "__main__":
    # Run the async main function
    load_dotenv()
    url = "https://www.firecrawl.dev/"
    asyncio.run(firecrawler())
