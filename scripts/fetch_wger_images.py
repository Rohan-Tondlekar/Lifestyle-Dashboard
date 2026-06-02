# Get a free key at https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb
"""
Fetches exercise GIF URLs from ExerciseDB via RapidAPI and writes them to data/exercises.json.

Strategy:
  1. Download full exercise database (~1300 exercises) with pagination
  2. Cache it locally to .exercisedb_cache.json (subsequent runs load instantly)
  3. Match our exercises against the cache by name (fuzzy matching with word overlap)
  4. Update exercises.json with image_url values

Usage:
    Windows:    $env:EXERCISEDB_API_KEY="your_key"; python scripts/fetch_wger_images.py --fresh
    macOS/Linux: EXERCISEDB_API_KEY=your_key python scripts/fetch_wger_images.py --fresh

Flags:
    --fresh     Force rebuild the cache (ignores existing .exercisedb_cache.json)

Free tier: ~500 requests/month. Full index = ~13 API calls, then zero calls for matching.
Already-cached exercises (image_url is not null) are skipped; use --fresh to override.
"""
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests

EXERCISES_FILE = Path(__file__).parent.parent / 'data' / 'exercises.json'
CACHE_FILE = Path(__file__).parent / '.exercisedb_cache.json'
BASE_URL = 'https://exercisedb.p.rapidapi.com'
RAPIDAPI_HOST = 'exercisedb.p.rapidapi.com'

_EXPAND = [('db ', 'dumbbell '), ('banded ', 'band ')]
_DROP = {'mat', 'warm-up', 'warmup', 'superset', 'clamshell', 'phase', 'v.', 'v'}


def _normalize(name: str) -> str:
    n = name.lower()
    for old, new in _EXPAND:
        n = n.replace(old, new)
    n = re.sub(r'\([^)]*\)', '', n)
    n = n.replace('-', ' ').replace('+', ' ')
    words = [w for w in n.split() if w not in _DROP and not w.startswith('(')]
    return ' '.join(words)


def _word_overlap(term: str, candidate: str) -> int:
    return len(set(term.split()) & set(candidate.split()))


def build_cache(api_key: str) -> list:
    """Download all exercises from ExerciseDB and return as list.

    Pagination: limit=100, increments offset. ~1300 exercises = ~13 calls.
    """
    print('Building fresh cache from ExerciseDB...')
    all_exercises = []
    offset = 0
    limit = 100

    while True:
        url = f'{BASE_URL}/exercises?limit={limit}&offset={offset}'
        try:
            resp = requests.get(
                url,
                headers={'X-RapidAPI-Key': api_key, 'X-RapidAPI-Host': RAPIDAPI_HOST},
                timeout=10,
            )
            if resp.status_code == 429:
                print('  RATE LIMIT — daily quota exhausted. Try again tomorrow.')
                sys.exit(1)
            resp.raise_for_status()
            batch = resp.json()

            if isinstance(batch, dict) and 'message' in batch:
                print(f'  API error: {batch.get("message")}')
                sys.exit(1)

            if not isinstance(batch, list) or not batch:
                break

            all_exercises.extend(batch)
            print(f'  Fetched offset {offset}: {len(batch)} exercises ({len(all_exercises)} total)')
            offset += limit
            time.sleep(0.2)

        except Exception as e:
            print(f'  Error fetching batch: {e}')
            sys.exit(1)

    print(f'Cache complete: {len(all_exercises)} exercises downloaded.\n')

    # Debug: check what fields are available
    if all_exercises:
        print(f'Sample exercise fields: {list(all_exercises[0].keys())}\n')

    return all_exercises


def find_best_match(name: str, index: list) -> Optional[dict]:
    """Find best exercise match in the index.

    Returns the full exercise dict (with gifUrl), or None if no good match.
    Matching priority: exact → substring → word-overlap (min 2 shared words).
    """
    term = _normalize(name)

    # 1. Exact match (after normalization)
    for ex in index:
        if _normalize(ex['name']) == term:
            return ex

    # 2. Substring match (our term contained in DB name)
    for ex in index:
        if term in _normalize(ex['name']):
            return ex

    # 3. Best word-overlap (minimum 2 shared words)
    best, best_score = None, 0
    for ex in index:
        s = _word_overlap(term, _normalize(ex['name']))
        if s > best_score:
            best_score, best = s, ex
    if best_score >= 2:
        return best

    return None


def process_exercises(exercises: list, index: list) -> tuple:
    """Match exercises against index and populate image_url.

    Returns (updated_count, skipped_count).
    """
    updated, skipped = 0, 0
    for ex in exercises:
        if ex.get('image_url'):
            print(f'  Skip (cached): {ex["name"]}')
            skipped += 1
            continue

        match = find_best_match(ex['name'], index)
        if match is None:
            print(f'  {ex["name"]:45s}  ->  no match in ExerciseDB')
            continue

        gif_url = match.get('gifUrl')
        if gif_url:
            ex['image_url'] = gif_url
            print(f'  {ex["name"]:45s}  ->  "{match["name"]}"')
            updated += 1
        else:
            print(f'  {ex["name"]:45s}  ->  matched "{match["name"]}" (no GIF available)')

    return updated, skipped


def main():
    api_key = os.environ.get('EXERCISEDB_API_KEY')
    if not api_key:
        print('Error: EXERCISEDB_API_KEY environment variable not set.')
        print()
        print('  Windows:  $env:EXERCISEDB_API_KEY="your_key"; python scripts/fetch_wger_images.py')
        print('  macOS/Linux: EXERCISEDB_API_KEY=your_key python scripts/fetch_wger_images.py')
        print()
        print('Get a free key at: https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb')
        sys.exit(1)

    # Check for --fresh flag to rebuild cache
    force_fresh = '--fresh' in sys.argv

    # Load or build cache
    if CACHE_FILE.exists() and not force_fresh:
        print(f'Loading cached exercises from {CACHE_FILE.name}...\n')
        with open(CACHE_FILE, encoding='utf-8') as f:
            index = json.load(f)
        print(f'Loaded {len(index)} exercises from cache.\n')
    else:
        index = build_cache(api_key)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False)
        print(f'Cached {len(index)} exercises to {CACHE_FILE.name}.\n')

    # Load exercises to update
    with open(EXERCISES_FILE, encoding='utf-8') as f:
        data = json.load(f)

    # Process all exercise sections
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
        print(f'=== {section_name} ===')
        u, s = process_exercises(exercises, index)
        total_updated += u
        total_skipped += s
        print()

    # Save updated exercises
    with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'Done. Updated {total_updated} exercises. Skipped {total_skipped} already cached.')
    print(f'  Cache file: {CACHE_FILE.name} ({len(index)} exercises)')


if __name__ == '__main__':
    main()
