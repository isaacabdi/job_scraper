job scraper test
import requirements.txt and run using jos.bat file and viewing on index.html or local server

Change config file parameters to alter your search

queries: what you want to search

        locations: where you want to search
        
        includes: at least one string must be in job title)
        
        must_include: more harsh search criteria than includes
        
        exlcudes: excludes jobs if the title contains any of the strings in the list
        
        age_limit (days): jobs older than this are not added and once jobs in jobs.json become older than this, they are deleted
        
        distance: distance from the location either km or miles


![gif_web_scraper](https://github.com/isaacabdi/job_scraper/assets/51185725/ebc26731-2478-40de-9562-7a64f1a0f5c2)



Note: Indeed.py will block if too many requests are searched in a row(too many visits)
