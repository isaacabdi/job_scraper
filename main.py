from bs4 import BeautifulSoup 
import requests
import json

def test_beautifulsoup():
    url = "https://www.wikipedia.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup.title.text)
    print(response.url)
    #print(soup.prettify())
    for link in soup.find_all('a'):
        print(link.get('href'))

'''if __name__ == "__main__":
    test_beautifulsoup() '''