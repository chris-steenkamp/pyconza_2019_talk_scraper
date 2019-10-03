from contextlib import closing
from json import dump
from urllib.parse import quote_plus

from scraper import scrape_url

base_url = 'https://za.pycon.org/talks/'

talks = scrape_url(base_url)

with closing(open('talk_details.json', 'w')) as f:
    dump(talks, f, indent=4)
