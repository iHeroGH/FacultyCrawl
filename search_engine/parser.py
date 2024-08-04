import re
import string
from urllib.parse import urljoin
from urllib.request import urlopen

import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download the required NLTK data files
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)


def fetch_html(url: str) -> BeautifulSoup:
    """
    Retrieves the HTML of a given URL (requires opening the URL)

    Parameters
    ----------
    url : str
        The URL to retrieve HTML for

    Returns
    -------
    BeautifulSoup
        The retrieved HTML

    """
    html = urlopen(url)
    return retrieve_soup(html.read())


def retrieve_soup(html: bytes | str) -> BeautifulSoup:
    """
    Retrieves a BeautifulSoup object based on provided HTML, which can be
    a string of HTML or HTMl retrieved via urlopen

    Parameters
    ----------
    html : bytes | str
        HTML, which is in bytes if retrieved via urllib or a str if retrieved
        via a MongoDB call
    """
    return BeautifulSoup(html, 'html.parser')


def is_target(html: BeautifulSoup) -> bool:
    """
    Whether or not the given HTML points to a target (a faculty member)
    via <div class="fac-info">

    <div class="col-md directory-listing">
    indicates that the page lists faculty members

    Parameter
    ---------
    html : BeautifulSoup
        The HTML to parse

    Returns
    -------
    bool
        Whether or not the HTML is of a page of a faculty member
    """
    faculty = html.find('div', {'class': "fac-info"})

    return faculty is not None


def parse_html(html: BeautifulSoup) -> list[str]:
    """
    Retrieves a list of URLs parsed from the given page

    Parameters
    ----------
    html : BeautifulSoup
        The given page to parse

    Returns
    -------
    list[str]
        The list of URLs found
    """

    possible_urls = [i.get('href') for i in html.find_all('a', href=True)]

    urls: list[str] = []
    for url in possible_urls:
        # literally only one faculty website link starts with a whitespace char
        # ugh
        if re.match(r'^\s*http', url):
            urls.append(url)

        elif re.match(r'^/', url):
            new_url = urljoin(r"https://www.cpp.edu", url)
            urls.append(new_url)

    return urls


def preprocess_text(text: str) -> list[str]:
    """
    Preprocesses the text by performing stopword removal and lemmatization.

    Parameters
    ----------
    text : str
        The text to preprocess.

    Returns
    -------
    list[str]
        The preprocessed text as a list of filtered tokens
    """

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text.lower())

    # Remove stopwords and perform lemmatization
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    filtered_tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token not in stop_words
    ]

    return filtered_tokens


def retrieve_faculty_data(html: BeautifulSoup) -> list[str]:
    """
    Extracts and preprocesses faculty data from HTML.

    Parameters
    ----------
    html : BeautifulSoup
        The HTML to parse.

    Returns
    -------
    list[str]
        Every pre-processed token found in the provided HTML
    """
    all_tokens: list[str] = []

    # Area of Search (left and right sides)
    left_column = html.find_all('div', {'class': 'col'})
    right_column = html.find_all('div', {'class': 'accolades'})

    for elem in left_column:
        text = re.sub(r"[\xa0\n\t]", " ", elem.text)
        all_tokens += preprocess_text(text)

    for elem in right_column:
        text = re.sub(r"[\xa0\n\t]", " ", elem.text)
        all_tokens += preprocess_text(text)

    return all_tokens
