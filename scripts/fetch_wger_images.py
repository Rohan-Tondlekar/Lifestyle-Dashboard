# Get a free key at https://rapidapi.com/justin-WFnsXH_t6/api/exercisedb
"""
Fetches exercise GIF URLs from ExerciseDB via RapidAPI and writes them to data/exercises.json.

Strategy:
  1. Load the local exercise name list from sample-set/exerciseList.json (no API calls).
  2. Match each of our exercises against that list using aliases + word-overlap scoring.
  3. Fetch GIF URLs from the API only for successfully matched exercises (1 call each).

Usage:
    Windows:    $env:EXERCISEDB_API_KEY="your_key"; python scripts/fetch_wger_images.py
    macOS/Linux: EXERCISEDB_API_KEY=your_key python scripts/fetch_wger_images.py

Free tier: ~500 requests/month. Only matched exercises consume quota.
Already-cached exercises (image_url is not null) are always skipped.
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
NAME_LIST_FILE = Path(__file__).parent.parent / 'sample-set' / 'exerciseList.json'
BASE_URL = 'https://exercisedb.p.rapidapi.com'
RAPIDAPI_HOST = 'exercisedb.p.rapidapi.com'

# Hardcoded aliases: our normalized exercise name → exact ExerciseDB exercise name
# Derived from sample-set/exerciseList.json
_ALIASES = {
    # Dumbbell exercises
    'dumbbell goblet squat':              'dumbbell goblet squat',
    'dumbbell bent over row':             'dumbbell bent over row',
    'dumbbell shoulder press':            'dumbbell seated shoulder press',
    'dumbbell bicep curl':                'dumbbell biceps curl',
    'dumbbell lateral raise':             'dumbbell lateral raise',
    'dumbbell romanian deadlift':         'dumbbell romanian deadlift',
    'dumbbell biceps curl':               'dumbbell biceps curl',
    'dumbbell bench press':               'dumbbell bench press',
    'dumbbell tricep overhead extension': 'dumbbell seated triceps extension',
    'dumbbell reverse lunge':             'dumbbell rear lunge',
    'dumbbell calf raise':                'dumbbell single leg calf raise',
    'dead bug':                           'dead bug',
    'hanging leg raise':                  'hanging leg raise',
    'hip thrust':                         'glute bridge two legs on bench (male)',
    'hip thrust mat':                     'glute bridge two legs on bench (male)',
    # Band exercises
    'band pull apart':                    'band reverse fly',
    'band face pull':                     'band standing rear delt row',
    'band hip thrust':                    'resistance band hip thrusts on knees',
    'band push up':                       'band close-grip push-up',
    'band goblet squat':                  'band squat',
    'band tricep pushdown':               'band side triceps extension',
    'band romanian deadlift':             'band stiff leg deadlift',
    'band chest fly':                     'cable cross-over reverse fly',  # closest concept
    'band lateral walk':                  'monster walk',
    # Bodyweight
    'bicycle crunches':                   'band bicycle crunch',  # best available
    'plank':                              'front plank with twist',
    'push up':                            'push-up',
    'incline push up':                    'incline push-up',
}

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


def find_db_name(name: str, db_names: list) -> Optional[str]:
    """Return the exact ExerciseDB name that best matches our exercise name."""
    term = _normalize(name)

    # 1. Hardcoded alias (highest priority)
    if term in _ALIASES:
        target = _ALIASES[term]
        if target is None:
            return None
        return target

    # 2. Exact match in the name list
    if term in db_names:
        return term

    # 3. Substring: our term is contained in a DB name
    for db in db_names:
        if term in db:
            return db

    # 4. Best word-overlap (min 3 shared words for safety)
    best, best_score = None, 0
    for db in db_names:
        s = _word_overlap(term, db)
        if s > best_score:
            best_score, best = s, db
    if best_score >= 3:
        return best

    return None


def fetch_gif_url(exact_name: str, api_key: str) -> Optional[str]:
    """Fetch gifUrl from ExerciseDB for an exact exercise name."""
    try:
        resp = requests.get(
            f'{BASE_URL}/exercises/name/{quote(exact_name)}',
            headers={'X-RapidAPI-Key': api_key, 'X-RapidAPI-Host': RAPIDAPI_HOST},
            timeout=10,
        )
        if resp.status_code == 429:
            print('  RATE LIMIT — daily quota exhausted. Try again tomorrow.')
            sys.exit(1)
        resp.raise_for_status()
        body = resp.json()
        if isinstance(body, dict):
            print(f'  API error: {body.get("message", body)}')
            return None
        if body and isinstance(body, list):
            return body[0].get('gifUrl')
    except Exception as e:
        print(f'  Request error: {e}')
    return None


def process_list(exercises: list, db_names: list, api_key: str) -> tuple:
    updated, skipped = 0, 0
    for ex in exercises:
        if ex.get('image_url'):
            print(f'  Skip (cached): {ex["name"]}')
            skipped += 1
            continue

        db_name = find_db_name(ex['name'], db_names)
        if db_name is None:
            print(f'  {ex["name"]:45s}  ->  no match in ExerciseDB')
            continue

        url = fetch_gif_url(db_name, api_key)
        if url:
            ex['image_url'] = url
            print(f'  {ex["name"]:45s}  ->  "{db_name}"')
            updated += 1
        else:
            print(f'  {ex["name"]:45s}  ->  matched "{db_name}" but no GIF returned')
        time.sleep(0.4)

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

    if not NAME_LIST_FILE.exists():
        print(f'Error: exercise name list not found at {NAME_LIST_FILE}')
        print('Expected sample-set/exerciseList.json in the project root.')
        sys.exit(1)

    with open(NAME_LIST_FILE, encoding='utf-8') as f:
        db_names = [n.lower() for n in json.load(f)]
    print(f'Loaded {len(db_names)} exercise names from local list.\n')

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
        print(f'=== {section_name} ===')
        u, s = process_list(exercises, db_names, api_key)
        total_updated += u
        total_skipped += s
        print()

    with open(EXERCISES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'Done. Updated {total_updated} exercises. Skipped {total_skipped} already cached.')


if __name__ == '__main__':
    main()
