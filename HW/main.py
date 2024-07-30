import crawler
import frontier

'''
What still needs to be done:
- scrape data from faculty websites and store/index into database
- allow for user queury 
- see if crawler works for business seed url

'''



def main():
    #SEED ='https://www.cpp.edu/sci/biological-sciences/index.shtml'
    SEED = 'https://www.cpp.edu/engineering/ce/index.shtml'

    num_targets = 10
    request_queue = frontier.Frontier()
    request_queue.addURL(SEED)
    crawler.crawl(request_queue,num_targets)


if __name__ == '__main__':
    main()


