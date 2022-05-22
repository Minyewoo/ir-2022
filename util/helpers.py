'''miscellaneous helper functions'''

import os
import random
from time import sleep

import requests
from parsel import Selector

from util.proxy_address import ProxyAddress


def get_filenames_batched(root_dir, batch_size=1000):
    '''yields filenames batch by batch'''
    batch = []
    for file in os.scandir(root_dir):
        if file.name.endswith('.html'):
            batch.append(os.path.join(root_dir, file.name))
            if len(batch) == batch_size:
                yield batch
                batch = []

    if len(batch) != 0:
        yield batch


def isnt_space_string(string: str):
    '''reports whether a string is whitespace'''
    return string != ' '


def parse_proxies_from_table(text):
    '''parses proxies from table tag'''
    selector = Selector(text=text)
    search_path = 'div.services_proxylist.services > div > div.table_block > table > tbody > tr'
    rows = selector.css(search_path).getall()
    return parse_proxies_from_rows(rows)


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
    '''fetches proxy list from hidemy.name website'''

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
