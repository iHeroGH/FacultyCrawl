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
    faculty = html.find('div',{'class':"fac-info"})   #this is the one!!!
    if faculty is not None:
        print(faculty.get_text().strip("\n"))
        #return True
    #return False
    return faculty is not None


# returns list of parsed urls 
def parse(html):
    possible_urls = html.find_all('a',href=True) 
    urls=[]
    for i in range(len(possible_urls)):
        possible_urls[i] = possible_urls[i].get('href')

    for url in possible_urls:
        if re.match('^\s*http',url):    #literally only one faculty website link starts with a whitespace char ugh 
            urls.append(url)   #should this be urljoin?
        elif re.match('^/',url):
            newURL = urljoin("https://www.cpp.edu",url)
            urls.append(newURL)
            #print("partial: ", url)
        else: 
            pass
    return urls    











