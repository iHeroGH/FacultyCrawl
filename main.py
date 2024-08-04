from search_engine.crawler import crawl
from search_engine.frontier import Frontier
from search_engine.indexer import index_faculty_content
from search_engine.ranker import query_user


def main():
    """
    Drives the main functionality of the program, crawling, indexing, and
    querying
    """

    ###########################################################################
    # Simply change these variables!
    # ------------------------------
    # Whether or not to CRAWL starting from the seed. This will store every
    # encountered page in MongoDB `pages`
    _CRAWL = False
    # Which department to use as the initial SEED
    # Either bio, civ, or bus
    DEPARTMENT = "bio"

    # Whether or not to INDEX. This will retrieve targets from MongoDB,
    # calculate inverted indices for them, and store them to `faculty`
    _INDEX = False
    # The number of grams to use (connected strings of terms).
    # "cats love dogs"
    # 1-gram = "cats"
    # 2-gram = "cats", "cats love"
    # 3-gram = "cats", "cats love", "cats love dogs"
    _N_GRAMS = 3

    # Whether or not to ask for a user QUERY.
    _QUERY = True
    # The maximum number of results to return for each query
    _N_RESULTS = 5
    ###########################################################################

    # The base CPP URL
    CPP = r"https://www.cpp.edu/"

    # A map of a major's name to its website, the number of targets requested,
    # and the total number of targets
    DEPARTMENTS: dict[str, tuple[str, int, int]] = {
        'bio': (
            CPP + r"sci/biological-sciences/index.shtml", 10, 10
        ),
        "civ": (
            CPP + r"engineering/ce/index.shtml", 10, 25
        ),
        "bus": (
            CPP + r"cba/international-business-marketing/index.shtml", 10, 22
        )
    }

    seed, num_targets, total_targets = DEPARTMENTS[DEPARTMENT]
    assert num_targets <= total_targets

    if _CRAWL:
        print(
            f"Attempting to find {num_targets}/{total_targets} targets from " +
            f"seed {seed} of department {DEPARTMENT}."
        )
        frontier = Frontier()
        frontier.add_url(seed)
        crawl(frontier, num_targets)

    if _INDEX:
        print(
            f"Attempting to index {num_targets} targets " +
            f"using {_N_GRAMS} n-grams"
        )
        index_faculty_content(num_targets, _N_GRAMS)

    if _QUERY:
        query_user(_N_RESULTS, _N_GRAMS)


if __name__ == '__main__':
    main()
