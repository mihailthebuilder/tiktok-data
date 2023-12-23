import asyncio
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
import os
from pathlib import Path


async def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
    )

    log("START")

    load_dotenv()

    async with async_playwright() as p:
        chrome_profile_dir = Path(os.getcwd()) / "chrome_profile"

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_dir,
            headless=False,
        )
        await asyncio.sleep(60000)

        page = await browser.new_page()
        await page.goto("http://playwright.dev")
        log(await page.title())

        await browser.close()

    log("END")


def log(log: object):
    logging.info(log)


asyncio.run(main())
