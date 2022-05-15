'''helpers to execute requests through proxy'''

from logging import Logger
import logging
import random
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
            ProxyAddress(ip_address=fields[0],
                         port=int(fields[1]),
                         protocol=fields[protocol_index].lower(),
                         )
        )

    return proxies


def scrape_hydemyname_proxies(
    max_ping=500,
    protocol_type='h',
    start=0,
    count=100,
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

    sleep(random.uniform(0.5, 1.0))
    data = requests.get(url=url, params=params, headers=headers).text
    proxies = parse_proxies_from_table(data)

    proxy_count = len(proxies)
    actual_count = start+proxy_count
    if proxy_count != 0 and actual_count < count:
        return proxies + scrape_hydemyname_proxies(start=start+actual_count)

    return proxies


class ProxiedRequestExecutor:
    '''executes requests through random proxy server'''
    dummy_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'\
        ' AppleWebKit/537.36 (KHTML, like Gecko)'\
        ' Chrome/101.0.4951.64'\
        ' Safari/537.36'

    def __init__(
        self,
        user_agent=dummy_user_agent,
        logger: Logger = logging.getLogger(),
        max_sleep_time=0.2,
        min_sleep_time=0.0,
        proxies_page=0,
        proxy_count=100,
        retry_count=5
    ):
        self.proxies_page = proxies_page
        self.proxy_count = proxy_count
        self.retry_count = retry_count
        self.available_proxies = scrape_hydemyname_proxies(
            headers={'User-Agent': user_agent},
            start=proxies_page*proxy_count,
            count=proxy_count,
        )
        self.headers = {'User-Agent': user_agent}
        self.logger = logger
        self.logger.info('number of proxies found: %d',
                         len(self.available_proxies))

        self.max_sleep_time = max_sleep_time
        self.min_sleep_time = min_sleep_time

    def get(self, url: str,  params: dict = None):
        '''send proxied request ignoring exceptions'''
        try:
            return self.unsafe_get(url, params)
        except Exception:
            return None

    def unsafe_get(self, url: str,  params: dict = None):
        '''send proxied request'''
        for _ in range(self.retry_count):
            sleep(random.uniform(self.min_sleep_time, self.max_sleep_time))
            index = random.randrange(0, len(self.available_proxies)-1)
            response = requests.get(
                url=url,
                proxies=self.available_proxies[index].as_map(),
                headers=self.headers,
                params=params
            )
            status = response.status_code
            if status == 200:
                return response.text

            if status not in (301, 302, 403, 404, 500, 503):
                banned = self.available_proxies.pop(index)
                self.logger.error(
                    'status: %s; banned: %s; url: %s', status, banned, url)

            if len(self.available_proxies) == 0:
                self.available_proxies = scrape_hydemyname_proxies(
                    headers=self.headers,
                    start=self.proxies_page*self.proxy_count
                )

        return None
