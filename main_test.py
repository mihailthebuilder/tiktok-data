import unittest
import json

from main import parse_popular_hashtags_json, is_high_growth_hashtag, produce_report


class TestParsePopularHashtagsJson(unittest.TestCase):
    def test_happy_path(self):
        with open("test.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            self.assertEqual(len(hashtags), 50)


class TestIsHighGrowthHashtag(unittest.TestCase):
    def test_happy_path(self):
        with open("popular_hashtags_api_response.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            high_growth_hashtags = [
                hashtag for hashtag in hashtags if is_high_growth_hashtag(hashtag)
            ]
            hashtags_length = len(high_growth_hashtags)

            self.assertLess(hashtags_length, 50, hashtags)
            self.assertGreater(hashtags_length, 0)


class TestWriteReport(unittest.TestCase):
    def test_happy_path(self):
        with open("test.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            high_growth_hashtags = [
                hashtag for hashtag in hashtags if is_high_growth_hashtag(hashtag)
            ]
            produce_report(high_growth_hashtags)
