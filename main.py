import asyncio
from playwright.async_api import async_playwright
import logging
from dotenv import load_dotenv
import os


async def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
    )

    log("START")

    load_dotenv()

    async with async_playwright() as p:
        chrome_profile_dir = os.environ["CHROME_PROFILE_DIR"]
        log(f"chrome_profile_dir={chrome_profile_dir}")

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_dir,
            headless=False,
        )

        page = await browser.new_page()
        await page.goto("http://playwright.dev")
        log(await page.title())

        await asyncio.sleep(20)
        await browser.close()

    log("END")


def log(log: str):
    logging.info(log)


asyncio.run(main())
