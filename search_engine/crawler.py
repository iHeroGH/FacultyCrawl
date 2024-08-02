from .frontier import Frontier
from .parser import is_target, parse, retrieve_url
from .database import store_page


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
            html = retrieve_url(url)

            store_page(url, html)

            if is_target(html):
                targets_found += 1
                print(f"Target found ({targets_found}/{num_targets}).")

            if targets_found == num_targets:
                frontier.clear()
                print(f"{num_targets} targets found.")

            else:
                urls = parse(html)
                for url in urls:
                    if url in links_visited:
                        continue
                    if url in frontier.get_queue():
                        continue

                    frontier.add_url(url)

        except Exception as e:
            print(f"Skipping page: {e}")
