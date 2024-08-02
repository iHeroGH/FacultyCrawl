from urllib.error import HTTPError

import search_engine.parser as parser

from .frontier import Frontier


def crawl(frontier: Frontier, num_targets: int):
    """
    Procedurally discovers and adds URLs to the given frontier

    Parameters
    ----------
    frontier : Frontier
        The frontier (request queue) to add and visit URLs to and from
    num_targets : int
        The number of targets to look for. We clear the frontier once we
        have hit this target
    """

    links_visited: set[str] = set()
    targets_found: int = 0

    while not frontier.done:
        try:
            url = frontier.next_url()
            links_visited.add(url)
            html = parser.retrieve_url(url)

            # ----insert store_page() here----

            if parser.is_target(html):
                targets_found += 1

            if targets_found == num_targets:
                frontier.clear()
            else:
                urls = parser.parse(html)
                for url in urls:
                    if url in links_visited:
                        continue
                    if url in frontier.get_queue():
                        continue

                    frontier.add_url(url)

        except HTTPError as e:
            print({e})
        except Exception as e:
            print({e})
