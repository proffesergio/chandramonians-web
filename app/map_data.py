import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def countries():
    path = Path(__file__).resolve().parent / 'data' / 'map_countries.json'
    return json.loads(path.read_text(encoding='utf-8'))


def country_choices():
    return [('', 'Choose a country (optional)')] + sorted(
        [(code, place['name']) for code, place in countries().items()], key=lambda row: row[1]
    )
