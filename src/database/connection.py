import libsql_client
from dotenv import load_dotenv
import os
from icecream import ic

# connect to ../../test.db

# create a table
# insert some data

load_dotenv()


async def make_connection() -> libsql_client.Client:

    url = os.environ.get("DB_URL")
    auth_token = os.environ.get("DB_AUTH_TOKEN")

    if not url or not auth_token:
        raise ValueError("DB_URL or AUTH_TOKEN not found in .env")

    client = libsql_client.create_client(
        url=url,
        auth_token=auth_token,
    )

    ic("Creating table vehicles if not exists")
    _ = await client.execute("""
            CREATE TABLE IF NOT EXISTS
            cars (
            id INTEGER PRIMARY KEY,
            parsed_at TIMESTAMP,
            link VARCHAR(255),
            title VARCHAR(255),
            model VARCHAR(100),
            price VARCHAR(100),
            kilometers VARCHAR(100),
            cc VARCHAR(100),
            fuel_type VARCHAR(50),
            transmission_type VARCHAR(50),
            category VARCHAR(50),
            brand VARCHAR(50),
            version VARCHAR(50),
            year_of_manufacture YEAR
    );

    """)

    return client
