from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup


 # returns html of url 
def retrieveURL(url):  
    html = urlopen(url)
    soup = BeautifulSoup(html.read(), 'html.parser')
    return soup



# <div class="col-md directory-listing"> indicates that the page lists faculty members
# <div class="fac-info">
def target_page(html):
    #directory = html.find('div',{'class':'col-md directory-listing'})
    #directory = html.find('i',{'title':'website'})
   # <img alt="Erin J Questad"
    test = html.find('img',{'alt':"Erin J Questad"})
    if test is not None:
        print(test.get_text())
    directory = html.find('div',{'class':"fac-info"})   #this is the one!!!
    if directory is not None:
        print(directory)
        return True
    return False

    #return directory is not None


# returns list of parsed urls 
def parse(html):
    possible_urls = html.find_all('a',href=True) 
    urls=[]
    for i in range(len(possible_urls)):
        possible_urls[i] = possible_urls[i].get('href')
    for url in possible_urls:
        #print(link)
        if re.match('^http',url):
            urls.append(url)   #should this be urljoin?
        elif re.match('^/',url):
            newURL = urljoin("https://www.cpp.edu",url)
            urls.append(newURL)
        else: ##..
            pass
    return urls    










