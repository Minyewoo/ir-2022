# ir-2022
# Setup
```
pip install -r requirements.txt
```
or
```
pip3 install -r requirements.txt
```
# Crawling
For reddit crawling use `crawl.py` script.
To start you can simply run `python3 crawl.py` from project directory.
For info about usage and additional parameters run `python3 crawl.py -h`. Here is the output of this command:
```
usage: crawl.py [-h] [--beginning_post BEGINNING_POST]
                [--ending_post ENDING_POST] [-w WORKERS_COUNT]
                [--save_path SAVE_PATH] [--main_log_debug] [--proc_logs_debug]

Script for crawling old reddit. It goes from recent post to latter. Also this
script checks last saved post to start from there.

optional arguments:
  -h, --help            show this help message and exit
  --beginning_post BEGINNING_POST
                        lower post number where parsing will end (will be
                        converted to base36 post id)
  --ending_post ENDING_POST
                        higher post number where parsing will start (will be
                        converted to base36 post id)
  -w WORKERS_COUNT, --workers_count WORKERS_COUNT
                        number of parsing workers
  --save_path SAVE_PATH
                        path for storing crawled pages
  --main_log_debug      makes crawler.log level as debug, defaults to info
  --proc_logs_debug     makes processes log files level as debug, defaults to
                        info
```

# Parsing
To parse crawled pages use `parse.py` script.
By default, script searches for pages in `./posts`. If it's not there, please, specify right dir in `--input_path` param. 
To start you can simply run `python3 parse.py` from project directory.
For info about usage and additional parameters run `python3 parse.py -h`. Here is the output of this command:
```
usage: parse.py [-h] [--input_path INPUT_PATH] [--save_path SAVE_PATH]

Script for parsing info from crawled post pages from reddit.

optional arguments:
  -h, --help            show this help message and exit
  --input_path INPUT_PATH
                        path where crawled pages stored
  --save_path SAVE_PATH
                        path for storing parsed data
```
