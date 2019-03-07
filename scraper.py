import requests
from bs4 import BeautifulSoup as bs
default_url = 'https://www.guiamais.com.br/encontre?searchbox=true&'

class Scraper:
    different_pages = []

    def __init__(self, url=default_url, what, where):
        self.url = url
        self.what = what
        self.where = where

    def get_html(self):
        query_url = f'{self.url}what={self.what}&where={self.where}&page='
        for page in range(1, max_pages+1):
            different_pages.append(query_url+str(page))
