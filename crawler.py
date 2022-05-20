'''functions for crawling old.reddit.com'''

import re
import os
import logging
import signal
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from parsel import Selector
from data_extractor import parse_post_text
from proxied_request_executor import ProxiedRequestExecutor


def get_id_from_thing(thing):
    '''retrevies post id from div'''

    sel = Selector(text=thing)
    class_names = sel.css('.thing::attr(class)').get()
    expression = r'(?<=id-)(.+?)(?:(?=\s)|(?=^))'
    return re.search(expression, class_names).group(1)


def get_paginated(executor: ProxiedRequestExecutor, after=None, url='https://old.reddit.com/'):
    '''retrieves a number of posts previews from paginated old.reddit.com page'''
    items_per_page = 25
    #headers = {'User-Agent': 'Mozilla/5.0'}
    params = {'count': items_per_page}
    if after is not None:
        params['after'] = after

    return executor.get(url, params=params)


def get_items_batch(executor: ProxiedRequestExecutor, after=None, url='https://old.reddit.com/'):
    '''retrieves a batch of posts previews'''
    response = get_paginated(executor=executor, after=after, url=url)
    if response is not None:
        selector = Selector(text=response)
        return selector.css('#siteTable .thing').getall()
    return []


def generate_process_args(batch_count=20000, start=0, end=0):
    '''bruh'''
    for batch_start in range(start, end-1, -batch_count-1):
        batch_end = batch_start - batch_count
        batch_end = batch_end if batch_end > end else end

        yield (batch_start, batch_end)


def maybe_save(markup, save_path, logger: logging.Logger):
    '''bruh'''
    post_text = parse_post_text(markup)
    if len(post_text) >= 2000:
        with open(save_path, 'w', encoding='UTF-8') as file:
            file.write(markup)
            logger.info('Saved new big post to %s', save_path)
            return True
    return False


def setup_logger(
    log_dir=os.path.join('.', 'logs'),
    filename=f'{uuid.uuid4()}.log',
    level=logging.INFO
):
    '''sets up formatting and path for new logger'''
    log_format = '%(levelname)s %(asctime)s - %(message)s'

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        filename=os.path.join(log_dir, filename),
        format=log_format,
        level=level,
    )
    return logging.getLogger()


def scrape_posts_batch(args: tuple):
    '''bruh'''
    dataset_root = './posts'
    dataset_root = './posts'
    start, end = args

    logger = setup_logger(
        level=logging.INFO,
        log_dir=os.path.join('.', 'logs', 'processes'),
    )
    executor = ProxiedRequestExecutor(
        logger=logger,
        max_sleep_time=0,
    )

    files_saved = 0

    for number in range(start, end, -1):
        post_uid = np.base_repr(number=number, base=36).lower()

        post_link = f'https://old.reddit.com/{post_uid}'
        post = executor.get(post_link)
        if post is not None:
            save_path = os.path.join(dataset_root, f'{post_uid}.html')
            if maybe_save(post, save_path, logger):
                files_saved += 1
    return files_saved


def check_already_crawled(dataset_root):
    '''bruh'''
    batch = []
    for file in os.scandir(dataset_root):
        if file.name.endswith('.html'):
            batch.append(file.name.split('.')[0])

    last_parsed_id = None

    if len(batch) != 0:
        batch.sort()
        last_parsed_id = batch[0]

    return len(batch), last_parsed_id


def check_last_reddit_post_id(last_if_not_found):
    '''bruh'''
    executor = ProxiedRequestExecutor()
    batch = get_items_batch(executor, url='https://old.reddit.com/new')

    last_post_dirty_id = get_id_from_thing(batch[0]).split('_')
    last_post_id = None
    if len(last_post_dirty_id) == 2:
        last_post_id = last_post_dirty_id[-1]

    last_id_if_none = np.base_repr(number=last_if_not_found, base=36).lower()

    return last_post_id if last_post_id is not None else last_id_if_none


def is_available(url):
    '''checks if website isnt down'''
    executor = ProxiedRequestExecutor()
    page = executor.get(url)
    return page is not None


def scrape_reddit(first_post_number: int, last_post_number: int, dataset_root='./posts'):
    '''scraping posts from old.reddit.com subreddits'''

    if not os.path.exists(dataset_root):
        os.makedirs(dataset_root)

    batch_count = 5000
    logger = setup_logger(filename='crawler.log')

    reddit_first_post_ever = first_post_number

    crawled_count, last_crawled_id = check_already_crawled(dataset_root)

    logger.info('%d posts already crawled', crawled_count)

    if last_crawled_id is None:
        last_crawled_id = check_last_reddit_post_id(
            last_if_not_found=last_post_number
        )
        logger.info(
            'Starting crawling after hardcoded last post: %s',
            last_crawled_id,
        )
    else:
        logger.info(
            'Starting crawling after last saved post: %s',
            last_crawled_id,
        )

    if is_available(url='https://old.reddit.com'):
        max_workers = min(8, (os.cpu_count() or 1))
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            try:
                args_generator = generate_process_args(
                    batch_count=batch_count,
                    start=int(last_crawled_id, 36),
                    end=reddit_first_post_ever,
                )
                futures_buffer = [pool.submit(scrape_posts_batch, args)
                                  for args in args_generator]

                for future in as_completed(futures_buffer):
                    posts_saved = future.result()
                    logger.info(
                        '%d posts total saved from process',
                        posts_saved,
                    )

            except KeyboardInterrupt:
                for pid in pool._processes:
                    os.kill(pid, signal.SIGKILL)
    else:
        logger.error('old.reddit is not available')


if __name__ == '__main__':
    scrape_reddit(first_post_number=295, last_post_number=1847556708)
