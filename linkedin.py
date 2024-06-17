from bs4 import BeautifulSoup 
import requests
import json

import requests
from bs4 import BeautifulSoup

url = 'https://realpython.github.io/fake-jobs/'
html = requests.get(url)

s = BeautifulSoup(html.content, 'html.parser')

results = s.find(id='ResultsContainer')
job_title = results.find_all('h2', class_='title is-5')

for job in job_title:
    print(job.text)

if __name__ == "__linkedin__":
    test_beautifulsoup()