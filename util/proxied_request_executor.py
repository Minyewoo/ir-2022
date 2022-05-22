'''helpers to execute requests through proxy'''

import logging
import random
import requests
from util.proxy_repository import ProxyRepository


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
        retry_count=5
    ):
        self.headers = {'User-Agent': user_agent}

        self.proxy_repository = ProxyRepository(
            headers=self.headers,
            logger=logger,
        )

        self.retry_count = retry_count

        self.available_proxies = self._pick_random_proxies()

        self.logger = logger
        self.logger.info('number of proxies picked: %d',
                         len(self.available_proxies),
                         )

    def get(self, url: str,  params: dict = None):
        '''send proxied request ignoring exceptions'''
        try:
            return self.unsafe_get(url, params)
        except Exception:
            return None

    def unsafe_get(self, url: str,  params: dict = None):
        '''send proxied request'''
        for _ in range(self.retry_count):
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
                self.available_proxies = self._pick_random_proxies()

        return None

    def _pick_random_proxies(self):
        return random.sample(
            self.proxy_repository.proxies,
            int(len(self.proxy_repository.proxies) * 0.1),
        )
