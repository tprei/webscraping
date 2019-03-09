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
        query_url = f'{self.url}&what={self.what}&where={self.where}{self.modifier}'
        for page in range(1, self.max_pages+1):
            self.different_pages.append(query_url+str(page))

    # scrape html strings and fetch info

    # navigates through pages
    def scrape_all(self):
        results = []
        info = []
        page_num = 1
        for url in self.different_pages:
            print(f'Page {page_num}\n')
            r = requests.get(url)
            soup = bs(r.text, 'html.parser')
            # finds every query result in the current page
            items = soup.findAll('div', {'itemprop': 'itemListElement'})

            # finds info from each query result
            for item in items:
                try:
                    name = item.find('h2', {'class':'aTitle'}).text.lstrip().rstrip()
                    address = item.find('div', {'class': 'advAdress'}).find('span').text.lstrip().rstrip()
                    phone_url = 'https://www.guiamais.com.br/' + item.find('h2', {'class':'aTitle'}).find('a')['href'].lstrip().rstrip()
                    results.append((name, address, phone_url))
                except:
                    continue
            
            # finds the phone number from each query result (for some reason it wasnt in the main query html)
            for result in results:
                phone_url = result[2]
                r = requests.get(phone_url)
                temp_soup = bs(r.text, 'html.parser')
                phone_objects = temp_soup.findAll('li', {'class':'detail'})
                phone_numbers = []
                for phones in phone_objects:
                    phone_numbers.append(phones.text.lstrip().rstrip())
                info.append((result[0], result[1], phone_numbers))

            # placing all info together, appending to the csv and printing to the output console
            for item in info:
                with open(f'{self.what}_{self.where}.csv', 'a') as fi:
                    print(f"{item[0]}\n{item[1]}\n{item[2]}\n".replace('[', '').replace(']', ''))
                    fi.write(f"{item[0]},{item[1]},{item[2]}\n".replace('[', '').replace(']', ''))
        
            page_num+=1        

if __name__ == '__main__':

    what = input('Whatchu looking for??\n')
    where = input('Where u looking for it tho????\n')

    try:
        bot = Scraper(what.rstrip().lstrip(), where.lstrip().rstrip())
        bot.get_html()
        bot.scrape_all()
    except:
        print('There was an error scraping the data\n')
    finally:
        print('\n\nData scraped successfully\n\n')
