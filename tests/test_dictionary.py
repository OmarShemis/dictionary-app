import unittest
from unittest.mock import patch
import requests
from dictionary_app.dictionary import DictionaryError, format_entries, lookup_word

ENTRY = [{"word": "test", "meanings": [{"partOfSpeech": "noun", "definitions": [
    {"definition": "A trial.", "example": "A short test."},
    {"definition": "An examination."}, {"definition": "A check."}]}]}]


class DictionaryTests(unittest.TestCase):
    def test_all_definitions_and_examples_are_displayed(self):
        result = format_entries(ENTRY)
        for text in ("TEST", "NOUN", "A short test.", "A check."):
            self.assertIn(text, result)

    def test_invalid_payloads(self):
        for payload in ([], {}, None, [{}], [None]):
            with self.subTest(payload=payload), self.assertRaises(DictionaryError):
                format_entries(payload)

    @patch("dictionary_app.dictionary.requests.get")
    def test_blank_input_does_not_request(self, get):
        with self.assertRaisesRegex(DictionaryError, "enter a word"):
            lookup_word("  ")
        get.assert_not_called()

    @patch("dictionary_app.dictionary.requests.get")
    def test_success_and_url_encoding(self, get):
        response = get.return_value.__enter__.return_value
        response.status_code = 200
        response.json.return_value = ENTRY
        self.assertIn("TEST", lookup_word(" a/b "))
        get.assert_called_once_with("https://api.dictionaryapi.dev/api/v2/entries/en/a%2Fb", timeout=(5, 10))

    @patch("dictionary_app.dictionary.requests.get")
    def test_http_errors(self, get):
        response = get.return_value.__enter__.return_value
        for status, message in ((404, "No definition"), (429, "Too many"), (503, "unavailable")):
            response.status_code = status
            response.raise_for_status.side_effect = requests.HTTPError() if status == 503 else None
            with self.subTest(status=status), self.assertRaisesRegex(DictionaryError, message):
                lookup_word("test")

    @patch("dictionary_app.dictionary.requests.get")
    def test_network_errors(self, get):
        for error, message in ((requests.Timeout(), "timed out"), (requests.ConnectionError(), "internet")):
            get.side_effect = error
            with self.subTest(error=error), self.assertRaisesRegex(DictionaryError, message):
                lookup_word("test")

    @patch("dictionary_app.dictionary.requests.get")
    def test_invalid_json(self, get):
        response = get.return_value.__enter__.return_value
        response.status_code = 200
        response.json.side_effect = requests.exceptions.JSONDecodeError("invalid", "x", 0)
        with self.assertRaisesRegex(DictionaryError, "invalid response"):
            lookup_word("test")


if __name__ == "__main__":
    unittest.main()

