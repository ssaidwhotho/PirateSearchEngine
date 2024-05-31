import streamlit as st
import time
from query import search_engine as se, check_files_exist
import requests
from bs4 import BeautifulSoup
import re
import html

## test
#from memory_profiler import profile


api_key = "sk-proj-Zte7OZtDW8CTRUyBaul4T3BlbkFJwb20WT0IGnSmsKZrekNM"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
}



def get_stop_words() -> list:
    stop_words = [
            'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
            'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before',
            'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot',
            'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing',
            "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
            "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd",
            "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him',
            'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if',
            'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me',
            'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off',
            'on', 'once', 'only', 'or', 'other', "ought", 'our', 'ours', 'ourselves',
            'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's",
            'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the',
            'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these',
            'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through',
            'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd",
            "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when',
            "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why',
            "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll",
            "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
    return stop_words


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


def summarize_with_chatgpt(text, query):
    prompt = f"Using pirate speak, Summarize the following search engine website text about {query}: {text}"
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 175,
            "temperature": 0.8,
        },
    )

    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return "Unable to generate summary. Please try again later."

    try:
        summary = response.json()["choices"][0]["message"]["content"]
    except KeyError:
        print(f"Unexpected response structure: {response.json()}")
        return "Unable to generate summary. Please try again later."

    return summary

#@profile
def gui():
    page_bg_img = """
            <style>
            [data-testid="stAppViewContainer"] {
            background-image: url("https://cdn.discordapp.com/attachments/1034912286487359538/1246004590948778074/PirateBackgroundLighter.png?ex=665acfb4&is=66597e34&hm=bc9c6c4d7b3ab7106334c8102ffa6026528912abb0e5331011532bf37ed52d40&");
            background-size: cover;
            }
            [data-testid="stHeader"] {
            background-image: url("https://cdn.discordapp.com/attachments/1034912286487359538/1246007400687865886/NewPirateBanner.png?ex=665ad252&is=665980d2&hm=1cde1845a618079b1f2c97230326aa44703a9ae92b47b5a3b2f96cb524945b7d&");
            </style>
            """



    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.title("Yar Piratey Search Engine")
    # Allow user to click search or press enter to submit the form
    form = st.form("search_form")
    query = form.text_input("Searchin' for treasure? Enter yer search plunder here!", placeholder="e.g. \"Yarrrr! Pirate ships\" or \"Ahoy! Maps o' treasure\"")
    submit_button = form.form_submit_button("Ponder yar query")

    #st.image("FishingRod.gif")
    #st.logo("PirateWheelSpin.gif")

    # Load the inverted index and bookkeeping lists once when the app starts
    if not check_files_exist():
        st.error("Necessary files not found. Please check the instructions and try again.")
        st.stop()

    search_engine = se()

    if submit_button:
        if len(query) == 0:
            st.error("Query cannot be empty.")
        else:
            pondering = st.html("<p>Yarrrr! Searching the seven seas...</p>")
            fishingrod = st.image("ShipBottle.gif")
            start_time = time.time()

            # Run query using the loaded bookkeeping lists
            with open("inverted_index.txt", "r") as f:
                if len(query.split()) > 12:  # too many stop words
                    split_query = query.split()
                    for word in split_query[:]:
                        if word in get_stop_words():
                            split_query.remove(word)
                    result = search_engine.run_query(f, " ".join(split_query))
                else:
                    result = search_engine.run_query(f, query)

            end_time = time.time()
            st.markdown(f"**{len(result)} results found in {end_time - start_time:.10f} seconds.**")

            # Fetch and summarize the content of the pages
            for i, doc_id in enumerate(result[:min(10, len(result))]):
                url = search_engine.url_dict[doc_id]
                content_or_error, error_flag = fetch_content(url)  # Get the content and error flag

                if not error_flag:  # Content was successfully fetched
                    # content_chunks = split_content(content_or_error, 2048)
                    # summary = summarize_content(content_chunks)
                    split_words = content_or_error.split()
                    for word in split_words[:]:
                        if word in get_stop_words():
                            split_words.remove(word)
                    summary = summarize_with_chatgpt(" ".join(split_words), query)
                else:  # An error occurred while fetching the content
                    summary = content_or_error

                st.markdown(f"**{i + 1}.** [{url}](url)", unsafe_allow_html=False)
                st.markdown(f"**Summary:** {summary}")

            fishingrod.empty()
            pondering.empty()





if __name__ == "__main__":
    # Run code using streamlit run "path to queryGUI.py"
    gui()
