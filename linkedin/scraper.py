from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager

class LinkedinScraper:

    def __init__(self, queries):
        self.setup()
        self.queries = queries

    def setup(self):
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())

    def scrape(self):
        for query in self.queries:
            lookup = 'site:linkedin.com/in ' + query
            users = self.search(lookup, num_pages=5)
    
    def search(self, query, num_pages=5):
        self.driver.get('http://www.google.com')
        search_box = self.driver.find_element_by_name('q')
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)
    
        URLs = set()
        for _ in range(num_pages - 1):
            # wait for results to show up
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'result-stats')))

            results = self.driver.find_elements_by_css_selector('div.g')

            # get href results
            for r in results:
                profile_element = r.find_element_by_css_selector('div.r')
                profile = profile_element.find_element_by_tag_name('a')
                URLs.add(profile.get_attribute('href'))
            
            next_button = self.driver.find_element_by_id('pnnext')
            next_button.click()
        
        return list(URLs)

if __name__ == '__main__':
    try:
        with open('queries.in', 'r') as f:
            queries = f.readlines()
    except FileNotFoundError:
        print(f'File queries.in should contain queries.')
        exit(-1)

    scraper = LinkedinScraper(queries)
    scraper.scrape()