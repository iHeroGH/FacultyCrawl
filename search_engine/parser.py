import re
from urllib.parse import urljoin
from urllib.request import urlopen

from bs4 import BeautifulSoup


def retrieve_url(url: str) -> BeautifulSoup:
    """
    Retrieves the HTML of a given URL

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
    soup = BeautifulSoup(html.read(), 'html.parser')
    return soup


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

    if faculty:
        print(faculty.get_text().strip("\n"))

    return faculty is not None


def parse(html: BeautifulSoup):
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
