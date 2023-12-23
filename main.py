import asyncio
from playwright.async_api import async_playwright
import logging
import os
from pathlib import Path
from enum import Enum, StrEnum


class TikTokWebsiteURLs:
    popular_hashtags = (
        "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag"
    )


class TikTokAPIUrls:
    popular_hashtags = ""


class TikTokURLs:
    website = TikTokWebsiteURLs
    api = TikTokAPIUrls


async def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
    )

    log("START")

    async with async_playwright() as p:
        chrome_profile_dir = Path(os.getcwd()) / "chrome_profile"

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_dir,
            headless=False,
        )

        page = browser.pages[0]

        await page.goto(TikTokURLs.website.popular_hashtags)
        log(await page.title())

        await browser.close()

    log("END")


def log(log: object):
    logging.info(log)


asyncio.run(main())
