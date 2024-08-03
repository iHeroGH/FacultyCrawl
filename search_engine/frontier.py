class Frontier:
    """
    The Frontier object acts like a queue of requests, keeping track
    of the URLS to visit and the order to visit them in.
    """

    def __init__(self) -> None:
        self.request_queue: list[str] = []

    @property
    def done(self) -> bool:
        """
        A boolean property denoting whether or not we are done
        (ie; the request queue is empty)
        """
        return not self.request_queue

    def next_url(self) -> str:
        """
        Retrieves the next URL from the queueu (the 0th index of the queue)

        Returns
        -------
        str
            The URL retrieved from the queue

        Raises
        ------
        ValueError
            if we try to retrieve a URL but the queue is empty
        """
        if self.done:
            raise ValueError("Frontier is empty, but next_url was called.")

        return self.request_queue.pop(0)

    def add_url(self, url: str) -> None:
        """
        Adds a URL to the queue

        Parameters
        ----------
        url : str
            The URl to add to the request queue
        """
        self.request_queue.append(url)

    def clear(self) -> None:
        """
        Clears the queue of all URLs
        """
        self.request_queue.clear()

    def get_queue(self) -> list[str]:
        """
        Retrieves the entirety of the request queue

        Returns
        -------
        list[str]
            The request queue itself
        """
        return self.request_queue

    def __contains__(self, item: str) -> bool:
        """
        Returns whether or not item is in the request queue
        (simply use as follows: `if item in frontier`)

        Parameters
        ----------
        item : str
            The item to check in the queue

        Returns
        -------
        bool
            Whether or not the item is in the queue
        """
        return item in self.request_queue
