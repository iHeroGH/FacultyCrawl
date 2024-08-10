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


def paginate(
            ranking: list[tuple[str, float]],
            results_per: int
        ) -> list[list[tuple[str, float]]]:
    """
    Returns a paginated list of results given the original rankings and how
    many results to display on each page

    For example, a list like [doc1, doc2, doc3, doc3], with 2 results per page,
    would be [[doc1, doc2], [doc3, doc4]]

    Parameters
    ----------
    ranking : list[tuple[str, float]]
        The ordered list of URLs and their cosine similarities
    results_per : int
        How many results to display per page

    Returns
    -------
    list[list[tuple[str, float]]]
        A list of ranked pages where each sublist is of max size results_per
    """
    pages: list[list[tuple[str, float]]] = []

    curr_page: list[tuple[str, float]] = []
    for document in ranking:
        curr_page.append(document)

        if len(curr_page) >= results_per:
            pages.append(curr_page)
            curr_page = []

    if curr_page:
        pages.append(curr_page)

    return pages


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

    paginated_ranking: list[list[tuple[str, float]]] = []
    curr_page: int = 0
    while True:
        # Ask the user for a query
        print("**********")
        user_query = input(
            "Search Faculty Crawler " +
            "('-q' to quit, '-next' to go to the next page, " +
            "'-prev' to go to the previous page): "
        )

        # The user herby quits
        if user_query == "-q":
            break

        # Scrolling pages
        if user_query == "-next":
            curr_page += 1
        elif user_query == "-prev":
            curr_page -= 1
        # Retrieve the paginated and ranked results
        else:
            start = time()
            paginated_ranking = paginate(
                rank(user_query, n_grams), n_results
            )
            curr_page = 0

            if paginated_ranking:
                print(f"Results found in {time() - start:.4f}s")

        if not paginated_ranking:
            print("No results found!")
            continue

        # curr_page is between 0 and the number of pages we have
        curr_page = max(0, min(len(paginated_ranking) - 1, curr_page))

        # Display the results
        ranking = paginated_ranking[curr_page]
        for ind, ranking in enumerate(ranking):
            print(f"{ind + 1}) {ranking[0]}")
        print(f"Page {curr_page + 1}/{len(paginated_ranking)}")

        print()

    print("Thank you for using Faculty Crawler! <3")
