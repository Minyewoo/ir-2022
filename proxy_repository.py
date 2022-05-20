'''retrieves and stores proxy adresses'''
import logging
import random
import os
import json
from time import sleep
import requests
from parsel import Selector
from proxy_address import ProxyAddress


def parse_proxies_from_table(text):
    '''parses proxies from table tag'''
    selector = Selector(text=text)
    search_path = 'div.services_proxylist.services > div > div.table_block > table > tbody > tr'
    rows = selector.css(search_path).getall()
    return parse_proxies_from_rows(rows)


def isnt_space_string(x):
    '''reports whether a string is whitespace'''
    return x != ' '


def parse_proxies_from_rows(rows):
    '''parses proxy from td tag'''

    proxies = []
    for row in rows:
        selector = Selector(text=row)
        fields = list(filter(isnt_space_string,
                      selector.css('td ::text').getall()))
        protocol_index = 4 if len(fields) <= 7 else 5
        proxies.append(
            ProxyAddress(
                ip_address=fields[0],
                port=int(fields[1]),
                protocol=fields[protocol_index].lower(),
            )
        )

    return proxies


def scrape_hydemyname_proxies(
    max_ping=500,
    protocol_type='h',
    start=0,
    headers: dict = None,
):
    '''retrieves proxy list from hidemy.name website'''
    url = 'https://hidemy.name/ru/proxy-list/'
    params = {
        'maxtime': max_ping,
        'type': protocol_type,
    }

    if start != 0:
        params['start'] = start

    sleep(random.uniform(0.1, 0.3))
    data = requests.get(url=url, params=params, headers=headers).text
    proxies = parse_proxies_from_table(data)

    proxy_count = len(proxies)
    if proxy_count != 0:
        return proxies + scrape_hydemyname_proxies(
            start=start+proxy_count,
            max_ping=max_ping,
            protocol_type=protocol_type,
            headers=headers
        )

    return proxies


class ProxyRepository:
    cache_path = os.path.join('.', 'proxy.cache')

    def __init__(self, headers: dict = None, logger: logging.Logger = logging.getLogger()):
        self.headers = headers
        self.logger = logger

        logger.info('Retrieving proxies from cache...')
        cached_proxies = self.retrieve_from_cache()
        if len(cached_proxies) == 0:
            logger.info('No cached proxies found')

            logger.info('Retrieving proxies from network...')
            proxies = self.fetch_from_net()
            logger.info('Proxies retrieved: %d', len(proxies))
            self.proxies = proxies

            logger.info('Chaching proxies to %s', self.cache_path)
            self.cache_proxies()
        else:
            logger.info('Proxies retrieved: %d', len(cached_proxies))
            self.proxies = cached_proxies

    def fetch_from_net(self):
        proxies = scrape_hydemyname_proxies(headers=self.headers)
        return proxies

    def retrieve_from_cache(self):
        proxies = []
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r', encoding='UTF-8') as cache_file:
                for encoded_json in cache_file.readlines():
                    proxies.append(
                        ProxyAddress.from_json(json.loads(encoded_json))
                    )
        return proxies

    def cache_proxies(self):
        with open(self.cache_path, 'w', encoding='UTF-8') as cache_file:
            for proxy in self.proxies:
                cache_file.write(f'{json.dumps(proxy.to_json())}\n')
