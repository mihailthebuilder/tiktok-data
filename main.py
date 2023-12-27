from playwright.sync_api import sync_playwright, Request
import logging
import os
from pathlib import Path
import httpx
from pydantic import BaseModel


class TrendValueAtTimestamp(BaseModel):
    time: int
    value: float


class Hashtag(BaseModel):
    hashtag_id: str
    hashtag_name: str
    trend: list[TrendValueAtTimestamp]
    publish_cnt: int
    video_views: int
    rank: int


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

    hashtags = parse_popular_hashtags_json(res.json())

    url = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?page=2&limit=50&country_code=US&sort_by=popular"
    res = httpx.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"bas response, code: {res.status_code}, text: {res.text}")

    hashtags = hashtags + parse_popular_hashtags_json(res.json())

    log("finding high-growth hashtags")
    high_growth_hashtags = [
        hashtag for hashtag in hashtags if is_high_growth_hashtag(hashtag)
    ]

    produce_report(high_growth_hashtags)

    log("END")


def parse_popular_hashtags_json(input: dict) -> list[Hashtag]:
    return [Hashtag(**hashtag) for hashtag in input["data"]["list"]]


def is_high_growth_hashtag(hashtag: Hashtag) -> bool:
    if hashtag.trend[-1].value != 1:
        return False

    change_minus_1 = hashtag.trend[-1].value - hashtag.trend[-2].value
    if change_minus_1 < 0.2:
        return False

    change_minus_2 = hashtag.trend[-2].value - hashtag.trend[-3].value
    if change_minus_1 < change_minus_2:
        return False

    return True


def set_tiktok_api_headers(req: Request, headers: list[tuple[str, str]]):
    if (
        "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
        in req.url
    ):
        for header in req.headers_array():
            if header["name"][0] != ":":
                headers.append((header["name"], header["value"]))


def produce_report(hashtags: list[Hashtag]):
    with open("output.txt", "w", encoding="utf-8") as f:
        for hashtag in hashtags:
            f.write(f"{hashtag.model_dump()}\n")


def log(log: object):
    logging.info(log)


if __name__ == "__main__":
    main()
