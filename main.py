from playwright.sync_api import sync_playwright, Request
import logging
import os
from pathlib import Path
import httpx


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

        headers: list[tuple[str, str]] = []

        page.on("request", lambda req: set_tiktok_api_headers(req, headers))

        log("fetching headers from website")
        page.goto(
            url="https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag",
            wait_until="networkidle",
        )

        if len(headers) == 0:
            raise Exception("no headers found")

        log("closing browser")
        browser.close()

    log("collecting data")

    url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?page=1&limit=50&country_code=US&sort_by=popular"
    res = httpx.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"bas response, code: {res.status_code}, text: {res.text}")

    results = res.json()["data"]["list"]

    url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?page=2&limit=50&country_code=US&sort_by=popular"
    res = httpx.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"bas response, code: {res.status_code}, text: {res.text}")

    results = results + res.json()["data"]["list"]

    log("finding high-growth hashtags")
    print(results)

    log("END")


def set_tiktok_api_headers(req: Request, headers: list[tuple[str, str]]):
    if (
        "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
        in req.url
    ):
        for header in req.headers_array():
            if header["name"][0] != ":":
                headers.append((header["name"], header["value"]))


def log(log: object):
    logging.info(log)


main()
