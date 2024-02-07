from enum import StrEnum
from playwright.sync_api import sync_playwright, Request
import logging
import os
from pathlib import Path
import httpx
from pydantic import BaseModel
import psycopg
from dotenv import load_dotenv
from typing import Literal, Optional
import json
import argparse


class TrendValueAtTimestamp(BaseModel):
    time: int
    value: float


class CountryCode(StrEnum):
    UnitedStates = "US"
    UnitedKingdom = "GB"
    Pakistan = "PK"


class CountryInfo(BaseModel):
    id: CountryCode


class HashtagJson(BaseModel):
    hashtag_id: str
    hashtag_name: str
    trend: list[TrendValueAtTimestamp]
    publish_cnt: int
    video_views: int
    rank: int
    country_info: CountryInfo
    is_promoted: bool
    trending_type: Optional[int] = 0


class Args(BaseModel):
    run_browser_headless: bool


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
    )
    load_dotenv()

    log("START")

    log("getting args")
    args = get_args()

    log("launching browser")

    headers = get_headers_for_api_calls(headless=args.run_browser_headless)

    log("collecting data")
    hashtags: list[HashtagJson] = []

    for code in CountryCode:
        hashtags = hashtags + get_popular_hashtags_for_country(
            api_headers=headers, country_code=code
        )

    log("exporting hashtags")
    export_hashtags(hashtags)

    log("uploading data")
    upload_data(hashtags)

    log("END")


def get_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--headless", type=bool, help="Specify whether to run headless using --headless"
    )
    args = parser.parse_args()
    return Args(run_browser_headless=args.headless)


def get_popular_hashtags_for_country(
    api_headers: list[tuple[str, str]], country_code: CountryCode
) -> list[HashtagJson]:
    hashtags = get_popular_hashtags_for_country_paginated(
        api_headers=api_headers, country_code=country_code, page=1
    )

    hashtags = hashtags + get_popular_hashtags_for_country_paginated(
        api_headers=api_headers, country_code=country_code, page=2
    )

    return hashtags


def get_popular_hashtags_for_country_paginated(
    api_headers: list[tuple[str, str]], country_code: CountryCode, page: Literal[1, 2]
) -> list[HashtagJson]:
    # can be 7, 30, and 120
    period = 30

    url = f"https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?page={page}&limit=50&country_code={country_code.value}&period={period}&sort_by=popular"
    res = httpx.get(url, headers=api_headers)
    if res.status_code != 200:
        raise Exception(f"bas response, code: {res.status_code}, text: {res.text}")

    return [HashtagJson(**hashtag) for hashtag in res.json()["data"]["list"]]


def get_headers_for_api_calls(headless: bool) -> list[tuple[str, str]]:
    with sync_playwright() as p:
        chrome_profile_dir = Path(os.getcwd()) / "chrome_profile"

        browser = p.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_dir,
            headless=headless,
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
    return headers


def upload_data(hashtags: list[HashtagJson]):
    db_url = os.environ["DATABASE_URL"]

    with psycopg.connect(db_url) as conn:
        cur = conn.cursor()

        cur.execute(
            """
                UPDATE hashtag
                SET "latest_trending" = FALSE
                WHERE "latest_trending" = TRUE
            """,
        )

        for hashtag in hashtags:
            cur.execute(
                """
                    INSERT INTO hashtag 
                        ("name", "country_code", "posts", "rank", "latest_trending", "views", "is_promoted", "trending_type", "trend")
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    hashtag.hashtag_name,
                    hashtag.country_info.id,
                    hashtag.publish_cnt,
                    hashtag.rank,
                    True,
                    hashtag.video_views,
                    hashtag.is_promoted,
                    hashtag.trending_type,
                    json.dumps([point.model_dump() for point in hashtag.trend]),
                ],
            )


def set_tiktok_api_headers(req: Request, headers: list[tuple[str, str]]):
    if (
        "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
        in req.url
    ):
        for header in req.headers_array():
            if header["name"][0] != ":":
                headers.append((header["name"], header["value"]))


def export_hashtags(hashtags: list[HashtagJson]):
    with open("output.txt", "w", encoding="utf-8") as f:
        for hashtag in hashtags:
            f.write(f"{hashtag.model_dump()}\n")


def log(log: object):
    logging.info(log)


if __name__ == "__main__":
    main()
