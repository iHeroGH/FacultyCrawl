from .database import DBCon
from .frontier import Frontier
from .parser import fetch_html, is_target, parse_html


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
            html = fetch_html(url)

            if (target := is_target(html)):
                targets_found += 1
                print(f"Target found ({targets_found}/{num_targets}).")

            DBCon.store_page(url, html, target)

            if targets_found == num_targets:
                frontier.clear()
                print(f"{num_targets} targets found.")

            else:
                urls = parse_html(html)
                for url in urls:
                    if url in links_visited:
                        continue
                    if url in frontier.get_queue():
                        continue

                    frontier.add_url(url)

        except Exception as e:
            print(f"Skipping page: {e}")
