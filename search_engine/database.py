from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.database import Database


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


def store_page(url: str, html: BeautifulSoup) -> None:
    """
    Stores the entirety of the HTML associated with a URL in a MongoDB

    Parameters
    ----------
    url : str
        The URL of the page given
    html : BeautifulSoup
        The HTML content of the page
    """
    db = DBCon.get_db()
    pages = db.pages

    pages.insert_one({
        "url": url,
        "html": html.decode()
    })
