'''retrieves and stores proxy adresses'''
import logging
import os
import json
from util.helpers import scrape_hydemyname_proxies
from util.proxy_address import ProxyAddress


class ProxyRepository:
    '''proxy repo with caching capabilities'''
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
        '''crawl proxies from hidemy.name proxy list'''
        proxies = scrape_hydemyname_proxies(headers=self.headers)
        return proxies

    def retrieve_from_cache(self):
        '''gets cached proxies'''
        proxies = []
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r', encoding='UTF-8') as cache_file:
                for encoded_json in cache_file.readlines():
                    proxies.append(
                        ProxyAddress.from_json(json.loads(encoded_json))
                    )
        return proxies

    def cache_proxies(self):
        '''saves proxies to file'''
        with open(self.cache_path, 'w', encoding='UTF-8') as cache_file:
            for proxy in self.proxies:
                cache_file.write(f'{json.dumps(proxy.to_json())}\n')
