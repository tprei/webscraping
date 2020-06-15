import aiohttp
import asyncio
import threading

from bs4 import BeautifulSoup as soup
from queue import Queue
from time import time
from tqdm import tqdm

DEFAULT_URL = 'https://www.guiamais.com.br/encontre?searchbox=true'
PAGE_MODIFIER = '&page='

class Entry:

    def __init__(self, **kwargs):
        self.name = kwargs['name']

        if not kwargs['address']:
            self.address = ''
            self.type = ''
        else:
            self.address = kwargs['address'].replace(',', ' ')
            self.address = ' '.join(self.address.split())

            words = self.address.split(' ')
            self.type = words[0]
            self.address = ' '.join(words[1:-1])

        if not kwargs['cep']:
            self.cep = ''
        else:
            self.cep = kwargs['cep'].replace(',', ' ')
            self.cep = self.cep.replace('\n', '')

        self.city = kwargs['city'].replace('\n', '')
        self.query = kwargs['query'].replace('\n', '')
        self.phones = []
        self.ddd = ''
        
        for phone in kwargs['phones']:
            separated_phone = phone.split()
            ddd = separated_phone[0]
            number = separated_phone[1]

            self.ddd = ddd[1:-1]

            self.phones.append(number)

    def __str__(self):
        row = self.name + ',' 
        row += self.query + ','
        row += self.type + ','
        row += self.address + ','
        row += self.city + ','
        row += self.cep + ','
        row += self.ddd + ','
        row += ','.join(self.phones)
        return row

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

class FileHandlerThread(threading.Thread):

    def __init__(self, filename):
        super().__init__()
        self.q = Queue()
        self.filename = filename
        self.cache = set()

    def run(self):
        while True:
            item = self.q.get()

            with open(self.filename, 'a') as f:
                f.write(str(item) + '\n')

            self.q.task_done()

async def get_html(session, url):
    async with session.get(url) as response:
        return await response.text()
    
async def setup(query, city) -> int:
    WHAT = '&what='
    WHERE = '&where='
    MAX_PAGES = '9999'

    url = DEFAULT_URL
    url += WHAT + query 
    url += WHERE + city

    initial_url = url

    url += PAGE_MODIFIER + MAX_PAGES

    session = aiohttp.ClientSession()
    html = await get_html(session, url)
        
    parsed = soup(html, 'html.parser')

    no_results = parsed.find('section', {'class': 'notFound'})

    if no_results:
        return None, 0, None

    pagination = parsed.find('nav', {'class': 'pagination'})
    num_pages = int(pagination.text.split('\n')[-2])

    return initial_url, num_pages, session

async def get_entry(item, query, city, session):
    address = None
    cep = None
    
    name = item.find('h2', {'class':'aTitle'}).text
    name = name.lstrip().rstrip()

    phone_url = 'https://www.guiamais.com.br/' + item.find('h2', {'class':'aTitle'}).find('a')['href']
    phone_url = phone_url.lstrip().rstrip()

    phone_html = await get_html(session, phone_url)
    parsed = soup(phone_html, 'html.parser')

    phones = None
    phones = parsed.findAll('li', {'class':'detail'})
    phones = [phone.text.lstrip().rstrip() for phone in phones]

    address_div = parsed.find('span', {'class':'tp-address'})

    if address_div:
        address = address_div.text.lstrip().rstrip()

    cep_div = parsed.find('span', {'class': 'tp-postalCode'})

    if cep_div:
        cep = cep_div.text.lstrip().rstrip()

    return Entry (
            name=name,
            address=address,
            cep=cep,
            phones=phones,
            query=query,
            city=city
    )

async def get_pages(url, num_pages, session) -> list:
    pages = []
    for page in tqdm(range(1, num_pages + 1), desc='Pages'):
        full_url = url + PAGE_MODIFIER + str(page)
        html = await get_html(session, full_url)
        pages.append(html)

    return pages

async def main(queries, cities):
    thread = FileHandlerThread('output.csv')
    thread.start()

    session = None
    initial_time = time()
    count = 0
    stats = []

    for q in tqdm(queries, desc='Queries'):
        for c in tqdm(cities, desc='Cities'):
            url, num_pages, session = await setup(q, c)

            pages = await get_pages(url, num_pages, session)

            results = 0
            for html in pages:
                parsed = soup(html, 'html.parser')

                # get query results
                items = parsed.findAll('div', {'itemprop': 'itemListElement'})

                results += len(items)
                count += results

                for item in items:
                    entry = await get_entry(item, q, c, session)

                    if entry not in thread.cache:
                        thread.q.put(entry)
                        thread.cache.add(entry)
                        print(entry)

            stats.append((c.replace('\n', ''), q.replace('\n', ''), results))

            if session:
                await session.close()

    end_time = time()

    for stat in stats:
        print(f'City: {stat[0]} | Query: {stat[1]} | Count: {stat[2]}')

    print(f'Scraped {count} results in {round(end_time - initial_time, 2)}s')
    
    thread.join()

if __name__ == '__main__':
    with open('queries.txt', 'r') as f:
        queries = f.readlines()

    with open('cities.txt', 'r') as f:
        cities = f.readlines()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(queries, cities))

