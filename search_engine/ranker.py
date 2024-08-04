from time import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .database import DBCon
from .indexer import get_grams
from .parser import preprocess_text


def rank(query: str, n_grams: int) -> list[tuple[str, float]]:
    """
    Given a user query, return an ordered list of URLs ranked by how similar
    their HTML content is to the request using Cosine Similarity (scikit)

    Parameters
    ----------
    query : str
        The query provided by the user (this will be pre-processed via
        the same process used for indexing)
    n_grams : int
        The upper-bound of n-grams to use for TF-IDF calculations

    Returns
    -------
    list[tuple[str, float]]
        The ordered list of URLs and their cosine similarities
    """
    prelim_terms = preprocess_text(query)

    # Query terms will consist of the terms, and any additioanl grams
    query_terms = []
    for curr_gram in range(1, n_grams + 1):
        terms = get_grams(prelim_terms, curr_gram)
        query_terms += terms

    # Add every document found for every term in the query
    urls = set()
    for query_term in query_terms:
        inverted_index = DBCon.get_inverted_index(query_term)
        [urls.add(url) for url in inverted_index['doc_list']]

    # If we found no URLs, no results were found
    if not urls:
        return []

    # Two lists here, a list of the URLs in order and a list of documents
    # ordered_urls[i] = documents[i] (meaning the URL at index i is associated
    # with the pre-processed text content of the HTML in documents)
    ordered_urls: list[str] = []
    documents: list[str] = []
    for url in urls:
        document = DBCon.get_page(url)
        ordered_urls.append(url)
        documents.append(' '.join(preprocess_text(document['html'])))

    # Calculate TF-IDF features for the documents
    vectorizer = TfidfVectorizer(
        stop_words='english', ngram_range=(1, n_grams)
    )
    tf_idf_mat = vectorizer.fit_transform(
        documents + [' '.join(query_terms)]
    )

    # Calculate the cosine similarities between the Query and the Documents
    q_vector = tf_idf_mat.getrow(-1)
    d_vectors = tf_idf_mat[:-1]  # type: ignore
    similarity: list[float] = cosine_similarity(
        q_vector, d_vectors
    ).flatten().tolist()

    # Rank the URLs by the similarity of their documents
    return sorted(
        list(zip(ordered_urls, similarity)),
        key=lambda x: x[1],
        reverse=True
    )


def query_user(n_results: int, n_grams: int) -> None:
    """
    Infinitely queries the user until the user quits. Each query will be met
    with at most n_results results

    Parameters
    ----------
    n_results : int
        The maximum number of results to retrieve
    n_grams : int
        The number of grams to pass to the TF-IDF function eventually
    """

    while True:
        print("**********")
        user_query = input("Search Faculty Crawler (or '-q' to quit): ")

        if user_query == "-q":
            break

        start = time()
        ranking = rank(user_query, n_grams)[:n_results]

        if not ranking:
            print("No results found!")
            continue

        print(f"Results found in {time() - start:.4f}s")

        for ind, ranking in enumerate(ranking):
            print(f"{ind + 1}) {ranking[0]}")

        print()

    print("Thank you for using Faculty Crawler! <3")
