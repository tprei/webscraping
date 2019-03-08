from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs

session = HTMLSession()
default_url = 'https://www.guiamais.com.br/encontre?searchbox=true'
default_modifier = '&page='

class Scraper:


    def __init__(self, what, where, url=default_url, modifier=default_modifier):
        self.url = url
        self.what = what
        self.where = where
        self.modifier = default_modifier
        self.different_pages = []

        r = session.get(f'{self.url}&what={self.what}&where={self.where}{self.modifier}9999')
        xpath = r.html.xpath('//*[@id="list"]/nav/a')[-1]
        final_url = min(xpath.links)
        self.max_pages = int(final_url.split('&page=')[-1])

    def get_html(self):
        query_url = f'{self.url}what={self.what}&where={self.where}{self.modifier}'
        for page in range(1, self.max_pages+1):
            self.different_pages.append(query_url+str(page))
            print(query_url+str(page))

    #def scrape_all(self):


if __name__ == '__main__':
    bot = Scraper('Restaurante', 'Campinas')
    bot.get_html()
