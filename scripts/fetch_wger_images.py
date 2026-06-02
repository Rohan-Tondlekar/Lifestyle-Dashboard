# Get a free key at https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb
"""
Fetches exercise image URLs (animated GIFs) from ExerciseDB via RapidAPI and writes
them to data/exercises.json. Covers all sections including band_exercises.

Usage:
    EXERCISEDB_API_KEY=your_key python scripts/fetch_wger_images.py

Free tier: 10 requests/day.
Already-cached exercises (image_url is not null) are skipped automatically.
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests

EXERCISES_FILE = Path(__file__).parent.parent / 'data' / 'exercises.json'
BASE_URL = 'https://exercisedb.p.rapidapi.com'
RAPIDAPI_HOST = 'exercisedb.p.rapidapi.com'

import re as _re

# Terms to expand before stripping — order matters
_EXPAND = [('db ', 'dumbbell '), ('banded ', 'band ')]
# Terms to remove
_REMOVE = ['(mat)', '(phase 2)', '(towel/band)', 'warm-up', 'superset', '+ clamshell']


def _normalize(name: str) -> str:
    n = name.lower()
    for old, new in _EXPAND:
        n = n.replace(old, new)
    for token in _REMOVE:
        n = n.replace(token, '')
    # Remove anything in parentheses
    n = _re.sub(r'\([^)]*\)', '', n)
    # Replace hyphens with spaces (ExerciseDB uses spaces, not hyphens)
    n = n.replace('-', ' ')
    # Collapse whitespace
    return ' '.join(n.split())


def _query(term: str, api_key: str) -> Optional[str]:
    """Single API call — returns gifUrl of first result, None if empty."""
    resp = requests.get(
        f'{BASE_URL}/exercises/name/{quote(term)}',
        headers={
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': RAPIDAPI_HOST,
        },
        timeout=10,
    )
    if resp.status_code == 429:
        print('  RATE LIMIT — daily quota exhausted. Try again tomorrow.')
        sys.exit(1)
    resp.raise_for_status()
    body = resp.json()
    # RapidAPI sometimes returns {"message": "..."} when quota is exhausted
    if isinstance(body, dict):
        print(f'  API error response: {body.get("message", body)}')
        sys.exit(1)
    if body and isinstance(body, list):
        return body[0].get('gifUrl')
    return None


def _check_quota(api_key: str) -> None:
    """Quick sanity-check against a known exercise. Exits if quota is gone."""
    print('Checking API connection...')
    resp = requests.get(
        f'{BASE_URL}/exercises/name/{quote("bicep curl")}',
        headers={'X-RapidAPI-Key': api_key, 'X-RapidAPI-Host': RAPIDAPI_HOST},
        timeout=10,
    )
    if resp.status_code == 429:
        print('Daily quota exhausted — try again tomorrow.')
        sys.exit(1)
    body = resp.json()
    if isinstance(body, dict) or not body:
        print('API returned no results for "bicep curl" — quota likely exhausted.')
        print('Check your usage at: https://rapidapi.com/developer/dashboard')
        sys.exit(1)
    print(f'API OK — {len(body)} results for "bicep curl"\n')


def fetch_gif_url(name: str, api_key: str) -> Optional[str]:
    term = _normalize(name)
    try:
        url = _query(term, api_key)
        if url:
            print(f'  (matched: "{term}")')
            return url
        # Fallback: drop the first word (e.g. "dumbbell goblet squat" -> "goblet squat")
        words = term.split()
        if len(words) > 2:
            fallback = ' '.join(words[1:])
            time.sleep(0.3)
            url = _query(fallback, api_key)
            if url:
                print(f'  (matched via fallback: "{fallback}")')
                return url
        print(f'  (searched: "{term}" — not found in ExerciseDB)')
    except Exception as e:
        print(f'  Error for "{name}": {e}')
    return None


def process_list(exercises: list, api_key: str) -> tuple:
    updated, skipped = 0, 0
    for ex in exercises:
        if ex.get('image_url'):
            print(f'  Skip (cached): {ex["name"]}')
            skipped += 1
            continue
        print(f'Fetching: {ex["name"]}')
        url = fetch_gif_url(ex['name'], api_key)
        ex['image_url'] = url
        if url:
            print(f'  -> {url}')
            updated += 1
        else:
            print(f'  -> not found')
        time.sleep(0.5)
    return updated, skipped


def main():
    api_key = os.environ.get('EXERCISEDB_API_KEY')
    if not api_key:
        print('Error: EXERCISEDB_API_KEY environment variable not set.')
        print()
        print('Steps to get a free key:')
        print('  1. Go to https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb')
        print('  2. Sign up / log in to RapidAPI')
        print('  3. Subscribe to the free tier (500 requests/month)')
        print('  4. Copy your X-RapidAPI-Key from the API page')
        print()
        print('Then run:')
        print('  Windows:  $env:EXERCISEDB_API_KEY="your_key"; python scripts/fetch_wger_images.py')
        print('  macOS/Linux: EXERCISEDB_API_KEY=your_key python scripts/fetch_wger_images.py')
        sys.exit(1)

    _check_quota(api_key)

    with open(EXERCISES_FILE, encoding='utf-8') as f:
        data = json.load(f)

    sections = [
        ('phase1',       data.get('phase1', [])),
        ('phase2_upper', data.get('phase2_upper', [])),
        ('phase2_lower', data.get('phase2_lower', [])),
    ]

    band = data.get('band_exercises', {})
    for key in ('phase1_additions', 'phase2_upper_additions', 'phase2_lower_additions'):
        if band.get(key):
            sections.append((f'band_exercises.{key}', band[key]))

    total_updated, total_skipped = 0, 0
    for section_name, exercises in sections:
        print(f'\n=== {section_name} ===')
        u, s = process_list(exercises, api_key)
        total_updated += u
        total_skipped += s

    with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'\nDone. Updated {total_updated} exercises. Skipped {total_skipped} already cached.')


if __name__ == '__main__':
    main()
