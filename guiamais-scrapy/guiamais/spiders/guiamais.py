#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import re
import csv

GUIAMAIS_URL = 'https://www.guiamais.com.br/encontre?searchbox=true&what={what}&where={where}&page={page}'
DEFAULT_MAX_PAGES = 1000
MAX_PHONES = 4

class GuiaMaisItem(scrapy.Item):
    nome = scrapy.Field()
    complemento = scrapy.Field()
    endereco = scrapy.Field()
    cep = scrapy.Field()
    cidade = scrapy.Field()
    categoria = scrapy.Field()

    # didnt find a better way to do this
    fone1 = scrapy.Field()
    fone2 = scrapy.Field()
    fone3 = scrapy.Field()
    fone4 = scrapy.Field()

class GuiaMaisSpider(scrapy.Spider):
    name = 'guiamais'
    
    def start_requests(self):
        f_cities = getattr(self, 'c', 'f_cities.txt')
        f_queries = getattr(self, 'q', 'f_queries.txt')
        max_pages = getattr(self, 'max', DEFAULT_MAX_PAGES)

        if max_pages != DEFAULT_MAX_PAGES:
            max_pages = int(max_pages)

        try:
            with open(f_cities, 'r') as f:
                cities = f.readlines()

            with open(f_queries, 'r') as f:
                queries = f.readlines()
        except FileNotFoundError as e:
            print(e, self.log('Input files f_cities.txt/f_queries.txt not found.'))
            exit(-1)

        for city in cities:
            for query in queries:
                for page in range(1, max_pages+1):
                    url = GUIAMAIS_URL.format(what=query, where=city, page=page)
                    yield scrapy.Request(url, callback=self.parse)
        
    def parse(self, response):
        item_urls = response.xpath('//*[@itemprop="itemListElement"]//*[@class="aTitle"]/a/@href').getall()
        yield from response.follow_all(item_urls, callback=self.parse_item)

    def parse_item(self, response):
        name = response.css('.tp-companyName::text').get().strip()
        category = response.css('.tp-category::text').get().strip()
        city = response.css('.tp-city::text').get().strip()
        address = response.css('.tp-address::text').get()
        postal = response.css('.tp-postalCode::text').get()

        phones = response.css('.phone.detail.tp-phone::text').getall()
        phones = [p.strip() for p in phones]

        def parse_address(address):
            if address is None:
                return '', '', ''

            contents = re.sub(r'\s\s+', '', address).split('-')
            st = contents[0]
            neigh = contents[-1]

            st_content = ' '.join(st.strip().split(' ')[1:])
            st_type = st.strip().split(' ')[0]

            if 'km' in st_content.lower() or st_type == 'rod':
                st_type = ''

            return st_type, st_content, neigh.strip()

        st_type, st_name, neigh = parse_address(address)
        
        if postal is None:
            postal = ''

        item = GuiaMaisItem()
        item['nome'] = name
        item["complemento"] = st_type
        item["endereco"] = st_name
        item["cep"] = postal
        item["cidade"] = city
        item["categoria"] = category

        for i in range(MAX_PHONES):
            if i >= len(phones):
                item[f'fone{i+1}'] = ''
            else:
                item[f'fone{i+1}'] = phones[i]
        
        print(f'{name}, {category}, {st_type}, {st_name}, {neigh}, {postal}, {phones}')
        yield item