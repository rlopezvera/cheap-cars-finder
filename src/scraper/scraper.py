import asyncio
from typing import List
from config.settings import URL
from pyppeteer.page import Page
from icecream import ic
from scraper.utils import clean_link

import requests
from bs4 import BeautifulSoup


async def backoff_retry(func, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            return await func()
        except Exception as e:
            wait = 2 ** retries
            ic(f"Error: {e}, retrying in {wait} seconds.")
            await asyncio.sleep(wait)
            retries += 1
    raise Exception("Max retries reached")

DAYS_AGO_MAP = {
    "today": "hoy",
    "last_week": "7dias",
    "last_15_days": "15dias",
    "last_month": "30dias",
}

# only needed for the first time


def get_links(days_ago: str = "today") -> List[str]:
    pages_counter = 1
    links = []
    query_days = DAYS_AGO_MAP[days_ago]

    keep_scraping = True

    while keep_scraping:
        # dont load images, css, fonts, etc
        # go to the page
        ic(f"Scraping page {pages_counter}")

        page = requests.get(
            URL + f"/?page={pages_counter}&publicado={query_days}")

        soup = BeautifulSoup(page.content, 'html.parser')

        scraped_links = soup.select("s-results.js-container")
        articles = soup.select("article")
        # select all articles inside a div of class 's-results js-container'

        # select all the hrefs in 'a' scraped_links
        scraped_links = ['https://www.neoauto.com/' + link.select_one("a")["href"]
                         for link in articles if link.select_one("a") is not None]

        ic(scraped_links)

        # clean the links
        ic(f"Scraped {len(scraped_links)} links")
        if len(scraped_links) == 0:
            ic("No more pages to scrape")
            keep_scraping = False

        pages_counter += 1
        links.extend(scraped_links)

    return links
