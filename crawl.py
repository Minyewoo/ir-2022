'''reddit crawling script'''
import argparse
import os
from crawling.crawler import crawl_reddit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Script for crawling old reddit.\n'
        'It goes from recent post to latter.\n'
        'Also this script checks last saved post to start from there.',
    )
    parser.add_argument(
        '--beginning_post',
        type=int,
        # first post ever
        default=295,
        help='lower post number where parsing will end (will be converted to base36 post id)',
    )
    parser.add_argument(
        '--ending_post',
        type=int,
        # hardcoded last post at the beginning of May 2022
        default=1847556708,
        help='higher post number where parsing will start (will be converted to base36 post id)',
    )
    parser.add_argument(
        '-w',
        '--workers_count',
        type=int,
        default=min(8, (os.cpu_count() or 1)),
        help=('number of parsing workers'),
    )
    parser.add_argument(
        '--save_path',
        type=str,
        default=os.path.join('.', 'posts'),
        help=('path for storing crawled pages'),
    )
    parser.add_argument(
        '--main_log_debug',
        action='store_true',
        help='makes crawler.log level as debug, defaults to info',
    )

    parser.add_argument(
        '--proc_logs_debug',
        action='store_true',
        help='makes processes log files level as debug, defaults to info',
    )

    args = parser.parse_args()

    assert args.beginning_post > 0 or args.ending_post > 0
    assert args.beginning_post < args.ending_post

    print('Crawling begins. Please, check logs directory for crawling status')

    crawl_reddit(
        first_post_number=args.beginning_post,
        last_post_number=args.ending_post,
        dataset_root=args.save_path,
        workers_count=args.workers_count,
        is_root_logger_in_debug=args.main_log_debug,
        is_proc_loggers_in_debug=args.proc_logs_debug,
    )
