from bs4 import BeautifulSoup 
from datetime import datetime
import requests
import json
import cloudscraper

def load_config():
    with open('config.json') as file:
        config = json.load(file)
        queries = config["queries"]
        locations = config["locations"]
        include = config["includes"]
        must_include = config["must_include"]
        exclude = config["excludes"]
        age_limit = config["age_limit"]
        distance = config["distance"]

    return queries, locations, include, must_include, exclude, age_limit, distance

def get_titles(soup, includes, must_include, excludes):
    titles_list = []
    titles = soup.find_all("span", {"class": "sr-only"})
    for t in titles:
        if (any(include in t.get_text().strip().lower() for include in includes) 
            and any(must in t.get_text().strip().lower() for must in must_include) 
            and not any(exclude in t.get_text().strip().lower() for exclude in excludes)):
            titles_list.append(t)
    return titles_list

def get_links(titles):
    link_list = []
    for title in titles:
        if title.parent.has_attr('href'):
            link = title.parent['href']
            link_list.append(link)
    return link_list

def get_locations(titles):
    location_list = []
    for title in titles:
        location = title.parent.parent.find(class_='job-search-card__location')
        location_list.append(location.get_text().strip())
    return location_list

def get_dates(titles):
    date_list = []
    for title in titles:
        try:
            date = title.parent.parent.find(class_='job-search-card__listdate')
            date_list.append(date['datetime'])
        except Exception as e:
            print(f'Error adding date: {e}')
            date_list.append('failed to fetch date')

    return date_list

def clear_old_jobs(jobs, age_limit):
    jobs_to_delete = []
    today = datetime.today()
    for title, details in jobs['jobs'].items():
        if details["date"] != 'failed to fetch date':
            date = datetime.strptime(details["date"], '%Y-%m-%d')
            difference = (today - date).days
            if difference > age_limit:
                jobs_to_delete.append(title)

    for title in jobs_to_delete:
        del jobs['jobs'][title]

    return jobs

def scrape_indeed():
    queries, locations, include, must_include, exclude, age_limit, distance = load_config()

    # load old jobs
    with open('jobs.json', 'r') as job_json:
        jobs = json.load(job_json)

    jobs = clear_old_jobs(jobs, age_limit)

    for query in queries:
        for location in locations:
            page = 0
            html = requests.get(f'https://ca.indeed.com/jobs?q={query}&l={location}&radius={distance}')
            soup = BeautifulSoup(html.text, 'html.parser')
            while len(soup.find_all('li')) > 0:
                title_list = get_titles(soup, include, must_include, exclude)
                link_list = get_links(title_list)
                locations = get_locations(title_list)
                dates = get_dates(title_list)
                page += 10

                for i in range(len(title_list)):
                    print(title_list[i].get_text().strip())
                    new_job = {
                        title_list[i].get_text().strip(): {
                            "link": link_list[i],
                            "location": locations[i],
                            "date": dates[i],
                        }
                    }
                    # only add jobs within the age limit
                    if new_job[title_list[i].get_text().strip()]["date"] != 'failed to fetch date':
                        if (datetime.today() - datetime.strptime((new_job[title_list[i].get_text().strip()])["date"], '%Y-%m-%d')).days < age_limit: 
                            jobs['jobs'].update(new_job) 

                html = requests.get(f'https://ca.indeed.com/jobs?q={query}&l={location}&radius={distance}&start={page}')
                soup = BeautifulSoup(html.text, 'html.parser')

    # write new job
    with open('jobs.json', 'w') as job_json:
        json.dump(jobs, job_json, indent=4)

def test_scraper():
    scraper = cloudscraper.create_scraper()  
    html = scraper.get("https://ca.indeed.com/jobs?q=intern&l=Toronto, ON&radius=15")
    soup = BeautifulSoup(html.text, 'html.parser')
    print(soup.find_all('span', id = "jobTitle-6366d8cf6b4c1110"))