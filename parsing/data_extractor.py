'''getting info from scraped markups'''

import os
import re
import json
from bs4 import BeautifulSoup


def parse_post_title(markup: str):
    '''parses post title from html page'''
    soup = BeautifulSoup(markup, 'html.parser')
    title_tag = soup.select_one(
        '#siteTable .thing .top-matter p.title a.title')

    title = ''
    if title_tag is not None:
        title_raw = title_tag.get_text()
        if title_raw is not None:
            title = re.sub(r'[^\w\s]', '', title_raw)

    return title


def parse_post_text(markup: str):
    '''parses and cleans up post content from html page'''
    soup = BeautifulSoup(markup, 'html.parser')

    url_pattern = r'''((?:(?<=[^a-zA-Z0-9])''' \
        r'''(?:(?:https?\:\/\/){0,1}(?:[a-zA-Z0-9\%]{1,}\:[a-zA-Z0-9\%]{1,}[@]){,1})'''\
        r'''(?:(?:\w{1,}\.{1}){1,5}(?:(?:[a-zA-Z]){1,})|'''\
        r'''(?:[a-zA-Z]{1,}\/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\:[0-9]{1,4}){1})){1}'''\
        r'''(?:(?:(?:\/{0,1}(?:[a-zA-Z0-9\-\_\=\-]){1,})*)(?:[?][a-zA-Z0-9\=\%\&\_\-]{1,}){0,1})'''\
        r'''(?:\.(?:[a-zA-Z0-9]){0,}){0,1})'''
    post_text = ''

    post_tag = soup.select_one(
        '#siteTable .thing .entry .expando form .usertext-body .md')
    if post_tag is not None:
        # removing <a> tags with link texts
        link_tags = post_tag.find_all('a')
        for link in link_tags:
            link_text = link.get_text()
            if re.search(url_pattern, link_text) is not None:
                link.decompose()

        # removing images
        img_tags = post_tag.find_all('img')
        for img in img_tags:
            img.decompose()

        # removing tables
        table_tags = post_tag.find_all('table')
        for table in table_tags:
            table.decompose()

        # removing code blocks
        code_tags = post_tag.find_all('code')
        for code in code_tags:
            code.decompose()

        post_text = post_tag.get_text()

        # revoving links in main content text
        post_text = re.sub(url_pattern, '', post_text)

        post_text = re.sub(r'[\-]', ' ', post_text)
        post_text = re.sub(r'[^\w\s]', '', post_text)
        post_text = re.sub(r'[\s]+', ' ', post_text)

    return post_text.strip()


def parse_post_score(markup: str):
    '''parses voting score from html page'''
    soup = BeautifulSoup(markup, 'html.parser')
    score_tag = soup.select_one('#siteTable .unvoted .unvoted')

    score = 0
    if score_tag is not None:
        try:
            score = int(score_tag.get_text())
        except Exception:
            score = 0

    return score


def parse_submission_time_utc(markup: str):
    '''parses post submission date as utc string from html page'''
    soup = BeautifulSoup(markup, 'html.parser')
    time_tag = soup.select_one('#siteTable  .top-matter .tagline time')

    time = None
    if time_tag is not None:
        time = time_tag.get('title')

    return time


def parse_comments_count(markup: str):
    '''parses comments cout of the post from html page'''
    soup = BeautifulSoup(markup, 'html.parser')
    comments_tag = soup.select_one('#siteTable .thing .entry .buttons .first')

    comments_count = 0
    if comments_tag is not None:
        comments_text = comments_tag.get_text()
        comments_words = comments_text.split(' ')
        if len(comments_words) == 2:
            comments_count = int(comments_words[0])

    return comments_count


def parse_awards(markup: str):
    '''parses award badges names of the post from html page'''
    soup = BeautifulSoup(markup, 'html.parser')
    awards_tags = soup.select(
        '#siteTable  .top-matter .tagline .awardings-bar .awarding-link')
    award_name_pattern = re.compile(
        r'([\w]+)[_][\d]+\.[a-z]+|([a-zA-Z0-9]+)\.[a-z]+')
    awards = {}
    for award_tag in awards_tags:
        count = int(award_tag.get('data-count'))
        image_tag = award_tag.select_one(
            '.awarding-icon-container .awarding-icon')
        award_name = ''
        if image_tag is not None:
            image_link = image_tag.get('src').split('/')[-1]
            groups = award_name_pattern.findall(image_link)[0]
            for group in groups:
                if len(group) > 0:
                    award_name = group
                    break
        awards[award_name] = count
    return awards


def extract_post_data(post_path):
    '''extracts data of main post content'''
    with open(post_path, 'r', encoding='UTF-8') as post_file:
        markup = post_file.read()

        return {
            'title': parse_post_title(markup),
            'text': parse_post_text(markup),
            'score': parse_post_score(markup),
            'submission_time': parse_submission_time_utc(markup),
            'comments_count': parse_comments_count(markup),
            'awards': parse_awards(markup),
        }


def extract_from_batch(posts_batch, cleaned_posts_root=os.path.join('.', 'cleaned_posts')):
    '''extracts data from batch of posts'''
    if not os.path.exists(cleaned_posts_root):
        os.makedirs(cleaned_posts_root)

    post_id_pattern = re.compile(r'([a-z0-9]+)\.html')

    for path in posts_batch:
        post_id = None

        post_id = post_id_pattern.findall(path)[0]

        save_path = os.path.join(cleaned_posts_root, f'{post_id}.json')
        parsed_post = extract_post_data(path)

        with open(save_path, 'w', encoding='UTF-8') as cleaned_post_file:
            json.dump(parsed_post, cleaned_post_file,
                      ensure_ascii=False, indent=4)
