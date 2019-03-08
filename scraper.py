import requests
from bs4 import BeautifulSoup as bs

default_url = 'https://www.guiamais.com.br/encontre?searchbox=true'
default_modifier = '&page='

class Scraper:

    # constructor: what is the query keyword, where is the query place, url is the default guiamais url and modifier is the string that's
    # being added when you go to the next page in the website

    def __init__(self, what, where, url=default_url, modifier=default_modifier):
        self.url = url
        self.what = what
        self.where = where
        self.modifier = default_modifier
        self.different_pages = []

        r = requests.get(f'{self.url}&what={self.what}&where={self.where}{self.modifier}9999')
        soup = bs(r.text, 'html.parser')
        final_url = soup.findAll('nav', {'class': 'pagination'})
        self.max_pages = int(final_url[0].text.split('\n')[-2]) # if something doesnt work its probably this

    # fetch all urls (all pages)

    def get_html(self):
        query_url = f'{self.url}what={self.what}&where={self.where}{self.modifier}'
        for page in range(1, self.max_pages+1):
            self.different_pages.append(query_url+str(page))

    # scrape html strings and fetch info

    # navigates through pages
    def scrape_all(self):
        for url in self.different_pages:
            r = requests.get(url)
            soup = bs(r.text, 'html.parser')
            # finds every query result in the current page
            items = soup.findAll('div', {'itemprop': 'itemListElement'})
            

if __name__ == '__main__':

    what = input('Whatchu looking for??\n')
    where = input('Where u looking for it tho????\n')

    bot = Scraper(what, where)
    bot.get_html()
    bot.scrape_all()
