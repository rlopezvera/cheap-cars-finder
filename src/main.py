import asyncio

from dotenv import load_dotenv


from bs4 import BeautifulSoup
from database.connection import make_connection
import requests
from scraper.scraper import get_links

from icecream import ic

import time

load_dotenv()


def format_log_message() -> str:
    return f"{time.strftime('%d/%m/%y %H:%M:%S')} |> "


def ic_log_timestamp() -> None:
    ic.configureOutput(prefix=format_log_message)
    pass


async def main():
    ic_log_timestamp()
    conn = await make_connection()
    links = get_links(days_ago="today")

    # links = ["https://neoauto.com/auto/usado/honda-cr-v-2017-1756405"]

    for link in links:
        ic(f"Scraping {link}")

        html_page = requests.get(link).text

        soup = BeautifulSoup(html_page, "html.parser")

        data = {
            "Año Modelo": None,
            "Transmisión": None,  # Note the accent in 'Transmisión'
            "Combustible": None,
            "Cilindrada": None,
            "Kilometraje": None,
            "Categoría": None,
            "Versión": None,
        }
        for div in soup.find_all("div", class_="flex items-start gap-[10px] py-2 box-border md:py-[10px]"):
            # Assuming the category is always in a div with class 'text-xs' and the value is in 'text-base'
            category = div.find("div", class_="text-xs")
            value = div.find("div", class_="text-base")

            # Check if both category and value are found
            if category and value:
                category_text = category.get_text(strip=True)
                value_text = value.get_text(strip=True)

                # Update the data map if the category is in the map
                if category_text in data:
                    data[category_text] = value_text

        title = soup.find("h1")

        title = title.get_text(
            strip=True) if title else "Sin Titulo Encontrado"

        price = soup.find(
            "p", class_="block font-ubuntu font-bold text-[1.375rem] leading-[1.875rem] md:text-4xl md:leading-[2.75rem]")

        if price == None:
            price = soup.find(
                "span", class_="block font-ubuntu font-bold text-[1.375rem] leading-[1.875rem] md:text-4xl md:leading-[2.75rem]")

        if price != None:
            price = price.get_text(strip=True)

        # some cleaning
        brand = title.split(" ")[0]
        year_of_manufacture = title.split(" ")[-1]
        model = title.split(" ")[1:-1][0]

        # ic(price, kms, ccs, fuel, transmission, category)
        # ic("Error")
        # break

        ccs = data["Cilindrada"]
        kms = data["Kilometraje"]
        fuel = data["Combustible"]
        transmission = data["Transmisión"]
        category = data["Categoría"]
        version = data["Versión"]
        parsed_at = time.strftime('%d/%m/%y %H:%M:%S')

        ic("Inserting into database")
        await conn.execute(f"""
            INSERT INTO cars (
            parsed_at, link, title, model, price, kilometers, cc, fuel_type,
            transmission_type, category, brand, version, year_of_manufacture)
            VALUES (
            '{parsed_at}', '{link}', '{title}', '{model}', '{price}', '{kms}', '{ccs}', '{fuel}',
            '{transmission}', '{category}', '{brand}', '{version}', '{year_of_manufacture}')
            """)

    await conn.close()
    pass


if __name__ == "__main__":
    asyncio.run(main())
