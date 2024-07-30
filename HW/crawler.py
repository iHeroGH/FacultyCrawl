from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError
import parser


# crawl thread procedure from template 
def crawl(frontier,num_targets):
    links_visited = []
    targets_found = 0
    while not frontier.done():
        try:
            url = frontier.nextURL()
            links_visited.append(url)
            #print("current: ",url)
            html = parser.retrieveURL(url)

            # ----insert storePage() here----

            if parser.target_page(html):
                targets_found +=1
                #print(f'************ TARGET FOUND {targets_found} *******************')
            if targets_found == num_targets:
                frontier.clear()
            else:
                urls = parser.parse(html)
                for url in urls:
                    if url not in links_visited and url not in frontier.getQueue():
                        frontier.addURL(url)

        except HTTPError as e:
            print({e})
        except Exception as e:
            print({e})
              
        


