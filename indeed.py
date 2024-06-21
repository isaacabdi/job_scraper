from bs4 import BeautifulSoup 
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
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
    titles = soup.select('span[title]')
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
            link_list.append(f'https://ca.indeed.com{link}')
    return link_list

def get_locations(titles):
    location_list = []
    for title in titles:
        parent = title.find_parent('td', {'class': 'resultContent css-1qwrrf0 eu4oa1w0'})
        location = parent.find('div', {'class': 'css-1p0sjhy eu4oa1w0'}).text
        location_list.append(location)
    return location_list

def get_dates(titles):
    date_list = []
    date_format = '%Y-%m-%d'
    for title in titles:
        parent = title.find_parent('div', {'class': 'job_seen_beacon'})
        date_info = parent.find('span', {'class': 'css-qvloho eu4oa1w0'}).text.replace('+', '')
        days_ago = [int(s) for s in date_info.split() if s.isdigit()]
        if len(days_ago) > 0:
            today = datetime.today()
            date_t = timedelta(days=days_ago[0])
            final_date = (today - date_t).strftime(date_format)
            date_list.append(final_date)

    return date_list
def count_jobs(jobs):
    count = 0
    for title, details in jobs['jobs'].items():
        count += 1
    return count

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
    options = Options()         
    options.headless = True 
    driver = webdriver.Firefox(options=options)
    # load old jobs
    with open('jobs.json', 'r') as job_json:
        jobs = json.load(job_json)

    jobs = clear_old_jobs(jobs, age_limit)
    old_count = count_jobs(jobs)

    for query in queries:
        for location in locations:
            page = 0
            driver.get(f'https://ca.indeed.com/jobs?q={query}&l={location}&radius={distance}&start={page}')
            driver.implicitly_wait(3)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            while True:
                title_list = get_titles(soup, include, must_include, exclude)
                link_list = get_links(title_list)
                locations = get_locations(title_list)
                dates = get_dates(title_list)
                page += 10

                for i in range(len(title_list)):
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
                            print(title_list[i].get_text().strip())
                                # if no next page
                if not driver.find_elements(By.XPATH, '/html/body/main/div/div[2]/div/div[5]/div/div[1]/nav/ul/li[6]/a'):
                    break

                driver.get(f'https://ca.indeed.com/jobs?q={query}&l={location}&radius={distance}&start={page}')
                driver.implicitly_wait(3)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
    driver.quit()
    # write new job
    with open('jobs.json', 'w') as job_json:
        json.dump(jobs, job_json, indent=4)
        
    new_count = count_jobs(jobs)
    print(f'Found {abs(old_count - new_count)} new jobs on Indeed')
