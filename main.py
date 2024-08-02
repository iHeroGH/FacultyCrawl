from search_engine.crawler import crawl
from search_engine.frontier import Frontier

"""
What still needs to be done:
- scrape data from faculty websites and store/index into database
- allow for user queury
- see if crawler works for business seed url
- parse faculty data
"""


def main():

    ###########################################################################
    # Simply change this variable!
    # Either bio, civ, or bus
    DEPARTMENT = "bus"
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

    print(
        f"Attempting to find {num_targets}/{total_targets} targets from " +
        f"seed {seed} of department {DEPARTMENT}."
    )

    frontier = Frontier()
    frontier.add_url(seed)

    crawl(frontier, num_targets)


if __name__ == '__main__':
    main()
