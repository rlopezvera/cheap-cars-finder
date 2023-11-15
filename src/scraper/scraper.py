import asyncio
from typing import List
from config.settings import URL
from pyppeteer.page import Page
from icecream import ic
from scraper.utils import clean_link


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


# only needed for the first time
async def get_links(page: Page) -> List[str]:
    pages_counter = 1
    links = []

    while True:
        # dont load images, css, fonts, etc
        # go to the page
        ic(f"Scraping page {pages_counter}")
        await page.goto(URL + f"/?page={pages_counter}")

        # grab the <a href ...> elements from the variable results
        scraped_links = await page.querySelectorAllEval(
            ".c-results.c-results-used--premium",
            "nodes => nodes.map(n => n.querySelector('a').href)"
        )

        scraped_links = [clean_link(link) for link in list(set(scraped_links))]
        ic(f"Scraped {len(scraped_links)} links")
        if len(scraped_links) == 0:
            ic("No more pages to scrape")
            break

        pages_counter += 1
        links.extend(scraped_links)

    return links
