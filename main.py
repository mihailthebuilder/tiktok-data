import asyncio
from playwright.async_api import async_playwright, Request
import logging
import os
from pathlib import Path


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

        headers = []

        page.on("request", lambda req: set_tiktok_api_headers(req, headers))

        popular_hashtags_web_url = (
            "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag"
        )
        await page.goto(url=popular_hashtags_web_url, wait_until="networkidle")
        print(headers)

        await browser.close()

    log("END")


async def set_tiktok_api_headers(req: Request, headers: list):
    popular_hashtags_api_url = (
        "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
    )
    if popular_hashtags_api_url in req.url:
        headers.extend(await req.headers_array())


def log(log: object):
    logging.info(log)


asyncio.run(main())
