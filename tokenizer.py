from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup

def is_alphanumeric(token: str) -> bool:
    # Check if the token is alphanumeric
    for char in token:
        if char.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789":
            return False
    return True


def get_tokens(document) -> list:
    try:
        current_doc = document['content']  # Copy current document
        soup = BeautifulSoup(current_doc, 'xml')  # Parse the document with BeautifulSoup
        for script in soup(["script", "style"]):
            script.extract()
        clean_text = soup.get_text()  # Get the text from the document

        return tokenize(clean_text)
    except Exception as e:
        print(document['content'])
        print(f"Error: {e}")
        return []


def tokenize(text: str) -> list:
    tokens = word_tokenize(text)

    tokens = [token.lower() for token in tokens if
              is_alphanumeric(token) or (
                          is_alphanumeric(token.replace(".", "")) and len(token) > 1)]
    p_stemmer = PorterStemmer()
    tokens = [p_stemmer.stem(word) for word in tokens]  # Stem using PorterStemmer
    # bigram_tokens = []
    # for i in range(len(tokens) - 1):
    #     bigram_tokens.append(tokens[i] + " " + tokens[i + 1])
    return tokens  # , bigram_tokens