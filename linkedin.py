from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json

def load_config():
    """
    Load the configuration from 'config.json'.
    Returns the queries, locations, include, must_include, exclude, age_limit, and distance parameters.
    """
    with open('config.json') as file:
        config = json.load(file)
        queries = config["queries"]
        locations = config["locations"]
        include = config["includes"]
        must_include = config["must_include"]
        exclude = config["excludes"]
        distance = config["distance"]
        

    return queries, locations, include, must_include, exclude, distance

def get_titles(soup, includes, must_include, excludes):

    titles_filtered = []
    titles = soup.find_all("span", {"class": "sr-only"})
    for title in titles:
        if (
            any(include in title.get_text().strip().lower() for include in includes)
            and any(must in title.get_text().strip().lower() for must in must_include)  
            and not any(exclude in title.get_text().strip().lower() for exclude in excludes)
        ):
            titles_filtered.append(title)
    return titles_filtered

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



def count_jobs(jobs):

    c = 0
    for title, details in jobs['jobs'].items():
        c += 1
    return c

def scrape_linkedin():
    """
    Scrape job postings from LinkedIn based on the configuration parameters.
    Updates 'jobs.json' with new job postings.
    """
    queries, locations, include, must_include, exclude, distance = load_config()

    # Load old jobs
    with open('jobs.json', 'r') as job_json:
        jobs = json.load(job_json)
        print(jobs)
    old_count = count_jobs(jobs)

    for query in queries:
        for location in locations:
            page = 0
            html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&distance={distance}&start=0')
    
            soup = BeautifulSoup(html.text, 'html.parser')
            while len(soup.find_all('li')) > 0:  # Continue while there are job postings on the page
                title_list = get_titles(soup, include, must_include, exclude)
                link_list = get_links(title_list)
                locations = get_locations(title_list)

                page += 25

                for i in range(len(title_list)):
                    new_job = {
                        title_list[i].get_text().strip(): {
                            "link": link_list[i],
                            "location": locations[i]
                        }
                    }
                    jobs['jobs'].update(new_job) 
                    print(f'{title_list[i].get_text().strip()} (LinkedIn)')
 
                
                # Fetch next page of job postings
                html = requests.get(f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}&distance={distance}&start={page}')

                soup = BeautifulSoup(html.text, 'html.parser')

    # Write new jobs to jobs.json
    with open('jobs.json', 'w') as job_json:
        json.dump(jobs, job_json, indent=4)

    new_count = count_jobs(jobs)
    print(f'Found {abs(old_count - new_count)} new jobs')