import unittest
import json

from main import parse_popular_hashtags_json, export_hashtags


class TestParsePopularHashtagsJson(unittest.TestCase):
    def test_happy_path(self):
        with open("test.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            self.assertEqual(len(hashtags), 50)


class TestExportHashtags(unittest.TestCase):
    def test_happy_path(self):
        with open("test.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            export_hashtags(hashtags)
