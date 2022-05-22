'''html parsing script'''

import argparse
import os

from tqdm import tqdm

from parsing.data_extractor import extract_from_batch
from util.helpers import get_filenames_batched


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Script for parsing info from crawled post pages from reddit.',
    )

    parser.add_argument(
        '--input_path',
        type=str,
        default=os.path.join('.', 'posts'),
        help=('path where crawled pages stored'),
    )

    parser.add_argument(
        '--save_path',
        type=str,
        default=os.path.join('.', 'cleaned_posts'),
        help=('path for storing parsed data'),
    )

    args = parser.parse_args()

    BATCH_SIZE = 10
    batches = get_filenames_batched(args.save_path, batch_size=BATCH_SIZE)

    file_count = len([
        name for name in os.listdir(args.save_path)
        if os.path.isfile(os.path.join(args.save_path, name))
    ])

    with tqdm(total=file_count, desc='Parsing posts info') as bar:
        for batch in batches:
            extract_from_batch(
                posts_batch=batch,
                cleaned_posts_root=args.save_path,
            )
            bar.update(BATCH_SIZE)
