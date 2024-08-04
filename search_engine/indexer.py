from collections import defaultdict

from .database import DBCon
from .parser import retrieve_faculty_data, retrieve_soup


def index_faculty_content(num_targets: int, n_gram: int = 3) -> None:
    """
    Calculates the inverted indices for num_targets targets found via a
    MongoDB query for 1-n_gram sets of tokens

    An inverted index is essentially a list of documents in
    which the term occurs.

    We end up with the following schema:
    {
        str: list[str],
        cat: [url1, url2, url3],
        ...
    }

    Parameters
    ----------
    num_targets : int
        The (maximum) number of targets to retrieve from MongoDB
    n_gram : int, default=3
        The maximum number of words to put together for one phrase.
        Example: "cats love dogs". 1-gram would index "cats", 2-gram would
        index "cats" and "cats love", 3-gram would index "cats", "cats love",
        and "cats love dogs"
    """
    # The final map of inverted indices
    # term: set of URLs in which that term occurs
    # Use a defaultdict so when we first encounter a new term, an empty set
    # is created
    inverted_indices: dict[str, set[str]] = defaultdict(set)

    # Calculate the indices
    targets = DBCon.get_targets(num_targets)
    for target in targets:
        url, html = target['url'], target['html']
        tokens = retrieve_faculty_data(retrieve_soup(html))

        for curr_gram in range(1, n_gram + 1):
            terms = get_grams(tokens, curr_gram)

            for term in terms:
                inverted_indices[term].add(url)

    # Store the indices
    for term, doc_list in inverted_indices.items():
        DBCon.store_inverted_index(term, doc_list)

    print(f"{len(inverted_indices.keys()):,} terms indexed.")


def get_grams(tokens: list[str], gram: int = 1) -> list[str]:
    """
    Retrieves n-grams for a given list of tokens

    Example: ["cats", "love", "dogs"]
    1-gram: ["cats", "love", "dogs"]
    2-gram: ["cats love", "love dogs"]
    3-gram: ["cats love dogs"]

    You'll need a for-loop to get a range of n-grams if that's the goal

    Parameters
    ----------
    tokens : list[str]
        The initial list of tokens
    gram : int, default=1
        The number of grams to create. The default value, 1, will essentially
        return the same list given

    Returns
    -------
    list[str]
        The grams generated
    """
    grams = zip(*[tokens[i:] for i in range(gram)])
    return [' '.join(ngram) for ngram in grams]
