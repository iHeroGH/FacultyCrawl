from typing import TypedDict

from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.database import Database


class Page(TypedDict):
    """
    A TypedDict defining what a Page is

    A Page has a URL (url : str), the associated HTML content (html : str),
    and whether or not the page belongs to a faculty member (is_target : bool)
    """
    url: str
    html: str
    is_target: bool


class InvertedIndex(TypedDict):
    """
    A TypedDict defining what an Inverted Index is

    An Inverted Index has a Term (term : str) and a list of documents in which
    the term occurs (doc_list : list[str])
    """

    term: str
    doc_list: list[str]


class DBCon:
    """Maintains a static connection to the MongoDB database"""

    # The MongoDB Client
    CLIENT: MongoClient | None = None
    # The MongoDB Database
    DB: Database | None = None

    # The connection info for the database
    DB_NAME = "faculty_crawl"
    DB_HOST = "localhost"
    DB_PORT = 27017

    def __init__(self) -> None:
        """
        Technically, instance objects should not be made of DBCon,
        but go off I guess
        """
        DBCon._connect()

    @staticmethod
    def get_client() -> MongoClient:
        """
        Retrieves the static MongoClient instance

        Returns
        -------
        MongoClient
            The static CLIENT instance
        """
        if not DBCon.safe():
            raise RuntimeError(
                "Something went wrong maintaining both a Client and a DB"
            )

        if DBCon.CLIENT is None:
            DBCon._connect()

        assert DBCon.CLIENT is not None
        return DBCon.CLIENT

    @staticmethod
    def get_db() -> Database:
        """
        Retrieves the static Database instance

        Returns
        -------
        Database
            The static DB instance
        """
        if not DBCon.safe():
            raise RuntimeError(
                "Something went wrong maintaining both a Client and a DB"
            )

        if DBCon.DB is None:
            DBCon._connect()

        assert DBCon.DB is not None
        return DBCon.DB

    @staticmethod
    def _connect() -> Database:
        """
        Connects to the defined database and returns the connection

        This should technically never be called outside of this class, but it
        is available. To retrieve a client or database, use the respective
        `get_client()` or `get_db()` functions, which will additionally
        perform safety checks for the maintenance of the connection.

        Returns
        -------
        Database
            The established Database connection
        """

        if not DBCon.safe():
            raise RuntimeError(
                "Something went wrong maintaining both a Client and a DB"
            )

        if DBCon.DB is not None:
            return DBCon.DB

        try:
            DBCon.CLIENT = MongoClient(host=DBCon.DB_HOST, port=DBCon.DB_PORT)
            DBCon.DB = DBCon.CLIENT[DBCon.DB_NAME]

            return DBCon.DB
        except Exception as e:
            raise RuntimeError(f"DB not connected successfully {e}.")

    @staticmethod
    def safe() -> bool:
        """
        Assures us that we have both a Client and DB (meaning,
        there is not a case where we have one but not the other)

        Returns
        -------
        bool
            Whether or not this connection is safe
        """
        return not ((DBCon.CLIENT is not None) ^ (DBCon.DB is not None))

    @staticmethod
    def store_page(
                url: str,
                html: BeautifulSoup,
                is_target: bool = False
            ) -> None:
        """
        Stores the entirety of the HTML associated with a URL in a MongoDB

        Parameters
        ----------
        url : str
            The URL of the page given
        html : BeautifulSoup
            The HTML content of the page
        is_target : bool, default=False
            Whether or not this is a page belonging to a target
            (a faculty member)
        """
        db = DBCon.get_db()
        pages = db.pages

        pages.insert_one({
            "url": url,
            "html": html.decode(),
            "is_target": is_target
        })

    @staticmethod
    def store_inverted_index(term: str, doc_list: set[str]) -> None:
        """
        Stores the inverted index associated with a given term. Essentially,
        we store a set of documents in which the term occurs.

        We end up with the following schema:
        {
            str: set[str],
            cat: [url1, url2, url3],
            ...
        }

        Parameters
        ----------
        term : str
            The term whose indices we are storing
        doc_list : set[str]
            The set of document URLs in which this term occurs
        """
        db = DBCon.get_db()
        faculty = db.faculty

        faculty.insert_one({
            "term": term,
            "doc_list": list(doc_list)
        })

    @staticmethod
    def get_page(url: str) -> Page:
        """
        Retrieves a Page associated with a URL

        Parameters
        ----------
        url : str
            The URL to search for

        Returns
        -------
        Page
            The Page found (a dictionary containing the keys `url`, `html`, and
            `is_target`), or `{"url": "", "html": "", "is_target": False}` if
            no Page is found for this URL
        """
        db = DBCon.get_db()
        result = db.pages.find_one({'url': url})

        return result or {"url": "", "html": "", "is_target": False}

    @staticmethod
    def get_targets(num_targets: int) -> Cursor[Page]:
        """
        Retrieves a maximum of num_targets target pages. If we don't have that
        many targets, all of our targets will be returned

        Parameters
        ----------
        num_targets : int
            The (maximum) number of targets to retrieve

        Returns
        -------
        Cursor[Page]
            An iterable object that allows for iteration over the results of a
            query
        """
        db = DBCon.get_db()
        return db.pages.find({'is_target': True}).limit(num_targets)

    @staticmethod
    def get_inverted_index(term: str) -> InvertedIndex:
        """
        Retrieves the indices associated with the given term (ie, the
        URLs in which the term occurs)

        Parameters
        ----------
        term : str
            The term to search for

        Returns
        -------
        InvertedIndex
            A dictionary containing the keys `term` (which is the term) and
            `doc_list` (which is the list of documents in which `term` appears)
            If no indices are found, we return an empty InvertedIndex dict
            (meaning `{"term": "", "doc_list": []}`)
        """
        db = DBCon.get_db()
        result = db.faculty.find_one({'term': term})

        return result if result else {"term": "", "doc_list": []}
