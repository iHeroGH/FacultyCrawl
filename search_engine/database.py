from bs4 import BeautifulSoup
from pymongo import MongoClient

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymongo.database import Database


class DBCon:

    CLIENT = None
    DB = None

    DB_NAME = "faculty_crawl"
    DB_HOST = "localhost"
    DB_PORT = 27017

    def __init__(self):
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

        if not DBCon.CLIENT:
            DBCon._connect()

        assert bool(DBCon.CLIENT)
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

        if not DBCon.DB:
            DBCon._connect()

        assert bool(DBCon.DB)
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

        if DBCon.DB:
            return DBCon.DB

        try:
            CLIENT = MongoClient(host=DBCon.DB_NAME, port=DBCon.DB_PORT)
            DB = CLIENT[DBCon.DB_NAME]

            return DB
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
        return not (bool(DBCon.CLIENT) ^ bool(DBCon.DB))


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
    print(DBCon.get_db())
