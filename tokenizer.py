from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup


def is_alphanumeric(token: str) -> bool:
    # Check if the token is alphanumeric
    for char in token:
        if char.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789":
            return False
    return True


def tokenize(text: str) -> list:
    """
    This function will take in a string and return a list of tokens.
    :param text: str
    :return: list of tokens
    """
    tokens = word_tokenize(text)

    tokens = [token.lower() for token in tokens if
              is_alphanumeric(token) or (
                      is_alphanumeric(token.replace(".", "")) and len(token) > 1)]
    p_stemmer = PorterStemmer()
    tokens = [p_stemmer.stem(word) for word in tokens]  # Stem using PorterStemmer
    return tokens


def get_tokens(document) -> dict and list[tuple]:
    """
    This function will take in the document, which is the json, and then will
    return the tokens and a dictionary of the tokens with bools marking if they are in the title, bold,
    """
    try:
        current_doc = document['content']  # Copy current document
        soup = BeautifulSoup(current_doc, 'lxml')  # Parse the document
        for script in soup(["script", "style"]):
            script.extract()
        # find all hyperlinks and their anchor text
        hyperlinks = []
        check_unique = set()
        for link in soup.find_all('a'):
            if link.get('href') in check_unique:
                for existing_link in hyperlinks:
                    if existing_link[0] == link.get('href'):
                        existing_link[1] += f" {link.text}"
            hyperlinks.append((link.get('href'), link.text))
            check_unique.add(link.get('href'))
        # find title and bold tags
        titles = tokenize(" ".join(tag.get_text() for tag in soup.find_all('title') if tag.get_text()))
        headers = tokenize(" ".join(tag.get_text() for tag in soup.find_all('header') if tag.get_text()))
        bold = tokenize(" ".join(tag.get_text() for tag in soup.find_all('b') if tag.get_text()))
        bold2 = tokenize(" ".join(tag.get_text() for tag in soup.find_all('strong') if tag.get_text()))
        # tokenize the text for the tags
        clean_text = soup.get_text()  # Get the text from the document
        tokens = tokenize(clean_text)  # Tokenize the text
        token_dict = {}  # Create a dictionary to store the tokens
        pos = 1
        for token in tokens:
            # token: (frequency, title?, bold?, positions)
            if token in token_dict:
                token_dict[token][0] += 1
                token_dict[token][4].append(pos)
            else:
                token_dict[token] = [1,
                                     token in titles,
                                     token in bold or token in bold2,
                                     token in headers,
                                     [pos]]
            pos += 1
        return token_dict, hyperlinks
    except Exception as e:
        print(document['content'])
        print(f"Error: {e}")
        return []
