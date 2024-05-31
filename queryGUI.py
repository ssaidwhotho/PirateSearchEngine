import streamlit as st
import time
from query import search_engine as se, check_files_exist
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
import html


tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")


def fetch_content(url):
    # Fetch the webpage
    response = requests.get(url, verify=False)

    # If the request was successful, extract the content
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the textual content of the webpage
        content = soup.get_text()

        # Remove any lines that are empty or only contain whitespace
        content = '\n'.join(line for line in content.splitlines() if line.strip())

        # Remove extra whitespace and line breaks
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n', content)

        # Decode HTML entities
        content = html.unescape(content)

        return content, False
    else:
        error_message = f"Unable to fetch content from the given URL. (The json contains all of the relevant data.)"
        return error_message, True


def split_content(content, max_length):
    # Split the content into chunks of the specified maximum length
    chunks = [content[i:i + max_length] for i in range(0, len(content), max_length)]

    return chunks


def summarize_content(content_chunks):
    input_texts = ["Summarize: " + chunk for chunk in content_chunks]
    inputs = tokenizer(input_texts, return_tensors="pt", padding="longest", truncation=True)
    summaries = model.generate(inputs["input_ids"], max_length=100, num_beams=4)
    summarized_texts = [tokenizer.decode(summary, skip_special_tokens=True) for summary in summaries]
    return ' '.join(summarized_texts)


def gui():
    st.title("Search Engine")

    # Allow user to click search or press enter to submit the form
    with st.form("search_form"):
        query = st.text_input("Enter your search query", "")
        submit_button = st.form_submit_button("Search")

    # Load the inverted index and bookkeeping lists once when the app starts
    if not check_files_exist():
        st.error("Necessary files not found. Please check the instructions and try again.")
        st.stop()

    search_engine = se()

    if submit_button:
        if len(query) == 0:
            st.error("Query cannot be empty.")
        else:
            start_time = time.time()

            # Run query using the loaded bookkeeping lists
            with open("inverted_index.txt", "r") as f:
                result, test_res = search_engine.run_query(f, query)

            end_time = time.time()
            st.markdown(f"**{len(result)} results found in {end_time - start_time:.10f} seconds.**")

            # Fetch and summarize the content of the pages
            for i, doc_id in enumerate(result[:min(10, len(result))]):
                url = search_engine.url_dict[doc_id]
                content_or_error, error_flag = fetch_content(url)  # Get the content and error flag

                if not error_flag:  # Content was successfully fetched
                    content_chunks = split_content(content_or_error, 2048)
                    summary = summarize_content(content_chunks)
                else:  # An error occurred while fetching the content
                    summary = content_or_error

                st.markdown(f"**{i + 1}.** [{url}]({url})", unsafe_allow_html=False)
                st.markdown(f"**Summary:** {summary}")

            # Display test results - Uncomment for testing
            # for i, res in enumerate(test_res[:min(10, len(test_res))]):
            #     st.markdown(f"**Test {i + 1}.** {res}")


if __name__ == "__main__":
    # Run code using streamlit run "path to queryGUI.py"
    gui()
