"""
This is the main Streamlit app that uses the OpenAI API to create a chatbot and a website crawler.
"""

import streamlit as st
from openai import OpenAI
import asyncio
import nest_asyncio
from src.firecrawler import FireCrawler

# Show title and description.
st.title("💬 Job-Seek Assistant")
st.write(
    "This is a chatbot that can crawl websites and answer your questions. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Setup tabs for different functionalities
tab1, tab2 = st.tabs(["Chat", "Website Crawler"])

with tab1:
    # Ask user for their OpenAI API key via `st.text_input`.
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    else:
        # Create an OpenAI client.
        client = OpenAI(api_key=openai_api_key)

        # Create a session state variable to store the chat messages.
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the existing chat messages via `st.chat_message`.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message.
        if prompt := st.chat_input("What is up?"):
            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Stream the response to the chat using `st.write_stream`
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Website crawler tab
with tab2:
    st.header("Website Crawler")
    st.write("Enter a website URL to crawl and index its content.")

    # Input for URL and limit
    url = st.text_input("Website URL", placeholder="https://example.com")
    limit = st.slider("Maximum pages to crawl", 1, 100, 10)

    # Initialize session state for crawler results
    if "crawler_status" not in st.session_state:
        st.session_state.crawler_status = None

    if "crawl_results" not in st.session_state:
        st.session_state.crawl_results = []

    # Start crawling button
    if st.button("Start Crawling"):
        if url:
            st.session_state.crawler_status = "running"
            st.session_state.crawl_results = []

            # Create progress bar
            progress = st.progress(0)
            status_text = st.empty()
            status_text.text(f"Starting crawl of {url}...")

            # Define callbacks to update UI
            def on_document_ui(detail):
                current_url = detail["data"]["metadata"]["url"]
                st.session_state.crawl_results.append(f"Scraped: {current_url}")
                # Update progress (this is approximate)
                progress_value = min(len(st.session_state.crawl_results) / limit, 1.0)
                progress.progress(progress_value)
                status_text.text(
                    f"Currently crawling: {current_url} ({len(st.session_state.crawl_results)} pages so far)"
                )

            def on_done_ui(detail):
                st.session_state.crawler_status = "complete"
                status_text.text(
                    f"Crawling of {url} complete! Processed {len(st.session_state.crawl_results)} pages."
                )

            # Initialize and run crawler
            try:
                with st.spinner(f"Initializing crawler for {url}..."):
                    crawler = FireCrawler()

                    # Override callbacks to update UI
                    crawler.on_document = on_document_ui
                    crawler.on_done = on_done_ui

                    # Need to handle async correctly in Streamlit
                    nest_asyncio.apply()
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(crawler.crawl(url, limit))
            except Exception as e:
                st.error(f"Error crawling {url}: {str(e)}")
                st.session_state.crawler_status = "error"
        else:
            st.warning("Please enter a valid URL")

    # Display crawl results
    if st.session_state.crawler_status:
        st.subheader("Crawl Results")
        if st.session_state.crawler_status == "running":
            st.info("Crawling in progress...")
        elif st.session_state.crawler_status == "complete":
            st.success(
                f"Crawling complete! Processed {len(st.session_state.crawl_results)} pages."
            )
        elif st.session_state.crawler_status == "error":
            st.error("An error occurred during crawling.")

        # Show crawled pages
        if st.session_state.crawl_results:
            with st.expander("Show crawled pages", expanded=True):
                for result in st.session_state.crawl_results:
                    st.write(result)
