import unittest
import json
from dotenv import load_dotenv


from main import parse_popular_hashtags_json, export_hashtags, upload_data


class TestParsePopularHashtagsJson(unittest.TestCase):
    def test_happy_path(self):
        with open("popular_hashtags_api_response.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            self.assertEqual(len(hashtags), 50)


class TestExportHashtags(unittest.TestCase):
    def test_happy_path(self):
        with open("popular_hashtags_api_response.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            export_hashtags(hashtags)


class TestUploadData(unittest.TestCase):
    def test_happy_path(self):
        load_dotenv()

        with open("popular_hashtags_api_response.json", "r", encoding="utf-8") as f:
            api_response = json.load(f)
            hashtags = parse_popular_hashtags_json(api_response)
            upload_data(hashtags)
