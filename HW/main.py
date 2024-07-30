import crawler

class Frontier: #the request queue object
    def __init__(self):
        self.request_queue = []

    def done(self):
        return len(self.request_queue) < 1

    def nextURL(self):
        next=self.request_queue[0]
        del self.request_queue[0]
        return next

    def addURL(self,url):
        #print("addURL: ",url)
        self.request_queue.append(url)

    def clear(self):
        self.request_queue.clear()
 
    def getQueue(self):
        return self.request_queue
        





def main():
    SEED ='https://www.cpp.edu/sci/biological-sciences/index.shtml'
    num_targets = 10
    frontier = Frontier()
    frontier.addURL(SEED)
    crawler.crawl(frontier,num_targets)



if __name__ == '__main__':
    main()


