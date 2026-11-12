"""Dictionary API access, independent of the user interface."""
from urllib.parse import quote
import requests


class DictionaryError(Exception):
    """A lookup failure suitable for displaying to the user."""


def format_entries(entries: object) -> str:
    try:
        if not isinstance(entries, list) or not entries:
            raise ValueError
        sections = []
        for entry in entries:
            lines = [entry["word"].upper(), "=" * 35]
            for meaning in entry["meanings"]:
                lines.append(f"\n{meaning['partOfSpeech'].upper()}")
                for item in meaning["definitions"]:
                    lines.append(f"\u2022 {item['definition']}")
                    if item.get("example"):
                        lines.append(f"  Example: {item['example']}")
            sections.append("\n".join(lines))
        return "\n\n".join(sections)
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        raise DictionaryError("The dictionary returned an unexpected response. Please try again.") from exc


def lookup_word(word: str) -> str:
    word = word.strip()
    if not word:
        raise DictionaryError("Please enter a word.")
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word, safe='')}"
    try:
        with requests.get(url, timeout=(5, 10)) as response:
            if response.status_code == 404:
                raise DictionaryError(f'No definition found for "{word}".')
            if response.status_code == 429:
                raise DictionaryError("Too many searches. Please wait a moment and try again.")
            response.raise_for_status()
            return format_entries(response.json())
    except requests.exceptions.Timeout as exc:
        raise DictionaryError("The search timed out. Please try again.") from exc
    except requests.exceptions.JSONDecodeError as exc:
        raise DictionaryError("The dictionary returned an invalid response. Please try again.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise DictionaryError("Cannot connect to the dictionary. Check your internet connection.") from exc
    except requests.exceptions.RequestException as exc:
        raise DictionaryError("The dictionary service is unavailable. Please try again later.") from exc
