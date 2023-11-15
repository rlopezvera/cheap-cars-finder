import asyncio

from dotenv import load_dotenv

from database.connection import make_connection
from scraper.scraper import get_links

from pyppeteer import launch
from icecream import ic

import time

from scraper.utils import check_length_of_one


load_dotenv()


def format_log_message() -> str:
    return f"{time.strftime('%d/%m/%y %H:%M:%S')} |> "


def ic_log_timestamp() -> None:
    ic.configureOutput(prefix=format_log_message)
    pass


async def main():
    ic_log_timestamp()
    conn = await make_connection()
    browser = await launch()
    page = await browser.newPage()
    links = await get_links(page)

    for link in links:
        # await page.goto(URL + link)
        ic(f"Scraping {link}")

        await page.goto(link)

        # reload the page before scraping
        await page.reload()

        title = await page.querySelectorEval(
            "h1",
            "node => node.innerText"
        )

        price_1 = await page.xpath(
            """//*[@id="__next"]/div/main/div[2]/div[1]/article/div[1]/div[3]/div/div/p"""
        )

        price_2 = await page.xpath(
            """
            //*[@id="__next"]/div/main/div[2]/div[1]/article/div[1]/div[3]/div/div[2]/span[2]"""
        )

        price = price_1 + price_2

        kms = await page.xpath("""//*[@id="__next"]/div/main/div[2]/div[1]/article/div[2]/div[2]/div[2]/div[2]""")

        transmission = await page.xpath("""//*[@id="__next"]/div/main/div[2]/div[1]/article/div[2]/div[3]/div[2]/div[2]""")

        fuel = await page.xpath("""//*[@id="__next"]/div/main/div[2]/div[1]/article/div[2]/div[4]/div[2]/div[2]""")

        ccs = await page.xpath("""//*[@id="__next"]/div/main/div[2]/div[1]/article/div[2]/div[5]/div[2]/div[2]""")

        category = await page.xpath("""//*[@id="__next"]/div/main/div[2]/div[1]/article/div[2]/div[6]/div[2]/div[2]""")

        if check_length_of_one(price,
                               kms,
                               ccs,
                               fuel,
                               transmission,
                               category) is False:
            ic("Error")
            break

        price = await page.evaluate('(element) => element.textContent', price[0])
        kms = await page.evaluate('(element) => element.textContent', kms[0])
        ccs = await page.evaluate('(element) => element.textContent', ccs[0])
        fuel = await page.evaluate('(element) => element.textContent', fuel[0])
        transmission = await page.evaluate('(element) => element.textContent', transmission[0])
        category = await page.evaluate('(element) => element.textContent', category[0])

        # some cleaning
        brand = title.split(" ")[0]
        year_of_manufacture = title.split(" ")[-1]
        model = title.split(" ")[1:-1][0]

        ic("Inserting into database")
        async with conn:
            await conn.execute(f"""
                INSERT INTO vehicles (
    link, title, model, price, kilometers, cc, fuel_type,
                transmission_type, category, brand, year_of_manufacture)
                VALUES (
                '{link}', '{title}', '{model}', '{price}', '{kms}', '{ccs}', '{fuel}',
                '{transmission}', '{category}', '{brand}', '{year_of_manufacture}')
                """)

    await browser.close()
    await conn.close()
    pass


if __name__ == "__main__":
    asyncio.run(main())
