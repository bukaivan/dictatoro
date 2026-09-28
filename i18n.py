import json
from pathlib import Path

_language = 'ru'
CATALOG = json.loads((Path(__file__).parent / 'translations.json').read_text('utf-8'))


def set_language(language):
    global _language
    _language = language if language in ('ru', 'en', 'pl', 'es', 'de', 'fr', 'ar', 'zh') else 'ru'


def tr(text):
    return CATALOG.get(text, {}).get(_language, text)
