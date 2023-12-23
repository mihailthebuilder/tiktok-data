from playwright.sync_api import sync_playwright, Request
import logging
import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Header:
    name: str
    value: str


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
    )

    log("START")

    log("launching browser")

    with sync_playwright() as p:
        chrome_profile_dir = Path(os.getcwd()) / "chrome_profile"

        browser = p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_dir,
            headless=False,
        )

        page = browser.pages[0]

        headers: list[Header] = []

        page.on("request", lambda req: set_tiktok_api_headers(req, headers))

        popular_hashtags_web_url = (
            "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag"
        )

        log("fetching headers from website")
        page.goto(url=popular_hashtags_web_url, wait_until="networkidle")

        if len(headers) == 0:
            raise Exception("no headers found")

        browser.close()

    print(headers)

    log("END")


def set_tiktok_api_headers(req: Request, headers: list[Header]):
    popular_hashtags_api_url = (
        "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
    )
    if popular_hashtags_api_url in req.url:
        headers.extend(
            [Header(header["name"], header["value"]) for header in req.headers_array()]
        )


def log(log: object):
    logging.info(log)


main()
