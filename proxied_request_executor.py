'''helpers to execute requests through proxy'''

import logging
import random
from time import sleep
from wsgiref import headers
import requests
from parsel import Selector
from proxy_address import ProxyAddress
from proxy_repository import ProxyRepository


class ProxiedRequestExecutor:
    '''executes requests through random proxy server'''
    dummy_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'\
        ' AppleWebKit/537.36 (KHTML, like Gecko)'\
        ' Chrome/101.0.4951.64'\
        ' Safari/537.36'

    def __init__(
        self,
        user_agent=dummy_user_agent,
        logger: logging.Logger = logging.getLogger(),
        max_sleep_time=0.2,
        min_sleep_time=0.0,
        proxy_count=100,
        retry_count=5
    ):
        self.headers = {'User-Agent': user_agent}
        self.proxy_repository = ProxyRepository(headers=self.headers)
        self.proxy_count = proxy_count
        self.retry_count = retry_count
        self.available_proxies = random.sample(
            self.proxy_repository.proxies,
            self.proxy_count
        )

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
                self.available_proxies = random.sample(
                    self.proxy_repository.proxies,
                    self.proxy_count
                )

        return None
