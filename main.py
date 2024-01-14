from playwright.sync_api import sync_playwright, Request
import logging
import os
from pathlib import Path
import httpx
from pydantic import BaseModel
import psycopg
from dotenv import load_dotenv
from typing import Optional


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
    is_promoted: bool
    trending_type: Optional[int] = 0


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
    )
    load_dotenv()

    log("START")

    log("launching browser")

    headers = get_headers_for_api_calls()

    log("collecting data")
    hashtags = get_popular_hashtags_for_country(api_headers=headers, country_code="US")

    log("exporting hashtags")
    export_hashtags(hashtags)

    log("uploading data")
    upload_data(hashtags)

    log("END")


def get_popular_hashtags_for_country(
    api_headers: list[tuple[str, str]], country_code: str
) -> list[Hashtag]:
    url = f"https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?page=1&limit=50&country_code={country_code}&sort_by=popular"
    res = httpx.get(url, headers=api_headers)
    if res.status_code != 200:
        raise Exception(f"bas response, code: {res.status_code}, text: {res.text}")

    hashtags = parse_popular_hashtags_json(res.json())

    url = f"https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?page=2&limit=50&country_code={country_code}&sort_by=popular"
    res = httpx.get(url, headers=api_headers)
    if res.status_code != 200:
        raise Exception(f"bas response, code: {res.status_code}, text: {res.text}")

    hashtags = hashtags + parse_popular_hashtags_json(res.json())

    return hashtags


def get_headers_for_api_calls() -> list[tuple[str, str]]:
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
    return headers


def upload_data(hashtags: list[Hashtag]):
    db_url = os.environ["DATABASE_URL"]

    with psycopg.connect(db_url) as conn:
        cur = conn.cursor()

        cur.execute(
            """
                UPDATE hashtag
                SET "latest_trending" = FALSE
                WHERE 
                    "country_code" = %s
                    AND "latest_trending" = TRUE
            """,
            ["US"],
        )

        for hashtag in hashtags:
            inserted_hashtag = cur.execute(
                """
                    INSERT INTO hashtag 
                        ("name", "country_code", "posts", "rank", "latest_trending", "views", "is_promoted", "trending_type")
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING
                        id
                """,
                [
                    hashtag.hashtag_name,
                    "US",
                    hashtag.publish_cnt,
                    hashtag.rank,
                    True,
                    hashtag.video_views,
                    hashtag.is_promoted,
                    hashtag.trending_type,
                ],
            )
            inserted_hashtag_result = inserted_hashtag.fetchone()
            if inserted_hashtag_result == None:
                raise Exception(f"couldn't insert hashtag {hashtag.hashtag_name}")

            inserted_hashtag_id = str(inserted_hashtag_result[0])

            for trend in hashtag.trend:
                cur.execute(
                    """
                        INSERT INTO hashtag_trend
                            ("hashtag_id", "recorded_for_unix_time", "interest")
                        VALUES
                            (%s, %s, %s)
                    """,
                    [inserted_hashtag_id, trend.time, round(trend.value * 100)],
                )


def parse_popular_hashtags_json(input: dict) -> list[Hashtag]:
    return [Hashtag(**hashtag) for hashtag in input["data"]["list"]]


def set_tiktok_api_headers(req: Request, headers: list[tuple[str, str]]):
    if (
        "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
        in req.url
    ):
        for header in req.headers_array():
            if header["name"][0] != ":":
                headers.append((header["name"], header["value"]))


def export_hashtags(hashtags: list[Hashtag]):
    with open("output.txt", "w", encoding="utf-8") as f:
        for hashtag in hashtags:
            f.write(f"{hashtag.model_dump()}\n")


def log(log: object):
    logging.info(log)


if __name__ == "__main__":
    main()
