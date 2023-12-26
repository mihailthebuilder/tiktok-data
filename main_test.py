import unittest
import json

from main import parse_popular_hashtags_json


class TestParsePopularHashtagsJson(unittest.TestCase):
    def test_happy_path(self):
        with open("test.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            self.assertEqual(len(hashtags), 50)


class TestIsHighGrowthHashtag(unittest.TestCase):
    def test_happy_path(self):
        with open("test.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            hashtags_length = len(hashtags)

            self.assertLess(hashtags_length, 50, hashtags)
            self.assertGreater(hashtags_length, 0)
