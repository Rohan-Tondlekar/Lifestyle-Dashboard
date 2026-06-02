#!/usr/bin/env python3
"""
One-time script: resolves Wger exercise image URLs and writes them to data/exercises.json.
Run from project root: python scripts/fetch_wger_images.py

Strategy: page through exerciseinfo (which includes both translations and images) and
find exercises whose English name contains our search term. Checks the first 300
exercises in the Wger database (~3 API calls), which covers all standard gym exercises.
"""
import json
import time
from pathlib import Path
from typing import Optional

import requests

EXERCISES_FILE = Path(__file__).parent.parent / 'data' / 'exercises.json'
WGER_INFO = 'https://wger.de/api/v2/exerciseinfo/'
WGER_BASE = 'https://wger.de'

_STRIP = ['DB ', '(mat)', '(Phase 2)', '(towel/band)']
_CACHE: dict = {}  # term -> image_url, shared across calls to avoid re-fetching pages


def _normalize(name: str) -> str:
    for token in _STRIP:
        name = name.replace(token, '')
    return name.strip().lower()


def _build_cache(pages: int = 3) -> None:
    """Fetch the first `pages` × 100 exercises and index them by English name."""
    if _CACHE:
        return
    print('  [building exercise index from Wger — one-time, ~3 API calls]')
    for page in range(pages):
        try:
            resp = requests.get(
                WGER_INFO,
                params={'format': 'json', 'language': 2, 'limit': 100, 'offset': page * 100},
                timeout=20,
            )
            resp.raise_for_status()
            for ex in resp.json().get('results', []):
                images = ex.get('images', [])
                if not images:
                    continue
                img_path = images[0].get('image', '')
                url = img_path if img_path.startswith('http') else WGER_BASE + img_path
                for t in ex.get('translations', []):
                    if t.get('language') == 2:
                        _CACHE[t['name'].lower()] = url
        except Exception as e:
            print(f'  [cache page {page} error: {e}]')
            break
        time.sleep(0.3)
    print(f'  [indexed {len(_CACHE)} named exercises with images]')


def find_image_url(name: str) -> Optional[str]:
    _build_cache(pages=6)
    term = _normalize(name)
    # Try exact match first, then substring
    if term in _CACHE:
        return _CACHE[term]
    for cached_name, url in _CACHE.items():
        if term in cached_name or cached_name in term:
            return url
    return None


def process_list(exercises: list) -> int:
    updated = 0
    for ex in exercises:
        if ex.get('image_url'):
            print(f'  Skip (cached): {ex["name"]}')
            continue
        print(f'Fetching: {ex["name"]}')
        url = find_image_url(ex['name'])
        ex['image_url'] = url
        print(f'  -> {url or "no image found in Wger"}')
        if url:
            updated += 1
    return updated


def main():
    with open(EXERCISES_FILE, encoding='utf-8') as f:
        data = json.load(f)

    total = 0
    for section in ('phase1', 'phase2_upper', 'phase2_lower'):
        print(f'\n=== {section} ===')
        total += process_list(data[section])

    with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'\nDone. Updated {total} exercises.')


if __name__ == '__main__':
    main()
