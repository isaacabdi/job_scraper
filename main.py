from bs4 import BeautifulSoup 
from linkedin import scrape_linkedin
from indeed import scrape_indeed
import requests
import json


scrape_linkedin()
scrape_indeed()
'''
if __name__ == "__main__":
    test_beautifulsoup() 
'''