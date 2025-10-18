#!/usr/bin/env python3
"""
Merge new questions into questions.json with validation and deduplication.

Usage:
  Dry-run (default):
    python merge_questions.py

  Apply changes (write to questions.json with timestamped backup):
    python merge_questions.py --apply

  Custom source/target files:
    python merge_questions.py --source tobeAddedQuestions.json --target questions.json --apply

What it does:
- Validates structure and fields of incoming questions
- Normalizes domain/difficulty to match their category key
- Skips duplicates (same domain+difficulty+title+question)
- Appends new valid questions to the proper category
- Creates a timestamped backup of the target file on --apply
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Repository-relative defaults
DEFAULT_SOURCE = os.path.join(os.path.dirname(__file__), 'tobeAddedQuestions.json')
DEFAULT_TARGET = os.path.join(os.path.dirname(__file__), 'questions.json')


REQUIRED_FIELDS = {
    'title': str,
    'context': str,
    'question': str,
    'options': list,
    'correct': int,
    'explanation': str,
    'learningPoints': list,
    'sources': list,
    'difficulty': str,
    'domain': str,
}


def _strip_json_comments_and_trailing_commas(text: str) -> str:
    """Allow JSON with // and /* */ comments and trailing commas."""
    # Remove /* block comments */
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    # Remove // line comments (not inside quotes)
    def _strip_line_comment(line: str) -> str:
        in_str = False
        esc = False
        for i, ch in enumerate(line):
            if ch == '"' and not esc:
                in_str = not in_str
            if not in_str and ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                return line[:i]
            esc = (ch == '\\' and not esc)
        return line
    text = "\n".join(_strip_line_comment(l) for l in text.splitlines())
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*(\}|\])", r"\1", text)
    return text


def load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f'File not found: {path}')
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try permissive parsing
        cleaned = _strip_json_comments_and_trailing_commas(raw)
        return json.loads(cleaned)


def save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def backup_file(path: str) -> str:
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = f"{path}.bak.{ts}"
    with open(path, 'rb') as src, open(backup_path, 'wb') as dst:
        dst.write(src.read())
    return backup_path


def norm_text(s: str) -> str:
    return ' '.join((s or '').strip().lower().split())


def category_key(domain: str, difficulty: str) -> str:
    return f"{domain.strip()}_{difficulty.strip()}"


def validate_question(q: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    # Required fields and types
    for field, tp in REQUIRED_FIELDS.items():
        if field not in q:
            errors.append(f"Missing required field '{field}'")
            continue
        if not isinstance(q[field], tp):
            errors.append(f"Field '{field}' must be of type {tp.__name__}")

    if errors:
        return errors

    # Options sanity
    options = q['options']
    if len(options) < 2:
        errors.append('Options must contain at least 2 choices')
    if len(options) > 8:
        errors.append('Options must not exceed 8 choices')
    # Typical convention is 4 options; warn if not 4
    if len(options) != 4:
        errors.append(f"Info: Non-standard option count ({len(options)}). Expected 4.")

    # Correct index bounds
    correct = q['correct']
    if not (0 <= correct < len(options)):
        errors.append(f"Correct index {correct} out of bounds for options length {len(options)}")

    # Strings not empty (basic sanity)
    for sf in ['title', 'context', 'question', 'explanation', 'difficulty', 'domain']:
        if not str(q[sf]).strip():
            errors.append(f"Field '{sf}' must not be empty")

    # Lists content type checks (optional but helpful)
    if not all(isinstance(o, str) for o in options):
        errors.append('All options must be strings')
    if not all(isinstance(lp, str) for lp in q['learningPoints']):
        errors.append('All learningPoints must be strings')
    if not all(isinstance(src, str) for src in q['sources']):
        errors.append('All sources must be strings')

    return errors


def build_existing_index(existing: Dict[str, Any]) -> Dict[Tuple[str, str, str, str], bool]:
    idx: Dict[Tuple[str, str, str, str], bool] = {}
    questions = existing.get('questions', {})
    for key, arr in questions.items():
        if not isinstance(arr, list):
            continue
        try:
            domain, difficulty = key.rsplit('_', 1)
        except ValueError:
            # Skip malformed keys
            continue
        for q in arr:
            title = norm_text(q.get('title', ''))
            qtext = norm_text(q.get('question', ''))
            idx[(domain, difficulty, title, qtext)] = True
    return idx


def ensure_category(existing: Dict[str, Any], key: str) -> None:
    if 'questions' not in existing or not isinstance(existing['questions'], dict):
        existing['questions'] = {}
    if key not in existing['questions'] or not isinstance(existing['questions'][key], list):
        existing['questions'][key] = []


def normalize_to_category(q: Dict[str, Any], cat_domain: str, cat_diff: str) -> Dict[str, Any]:
    q = dict(q)  # shallow copy
    # Normalize whitespace in strings
    for f in ['title', 'context', 'question', 'explanation', 'difficulty', 'domain']:
        if f in q and isinstance(q[f], str):
            q[f] = q[f].strip()
    # Trim options strings
    if 'options' in q and isinstance(q['options'], list):
        q['options'] = [str(o).strip() for o in q['options']]
    # Force domain/difficulty to match the category
    q['domain'] = cat_domain
    q['difficulty'] = cat_diff
    # Remove any runtime-only fields if present (e.g., id, timestamp)
    q.pop('id', None)
    q.pop('timestamp', None)
    return q


def merge(source_path: str, target_path: str, apply: bool = False) -> int:
    # Load files
    new_data = load_json(source_path)
    try:
        target_data = load_json(target_path)
    except FileNotFoundError:
        target_data = { 'questions': {} }

    existing_idx = build_existing_index(target_data)

    added = 0
    skipped_dupes = 0
    invalid = 0
    per_category_added: Dict[str, int] = {}

    new_questions = new_data.get('questions', {})
    for cat_key, arr in new_questions.items():
        if not isinstance(arr, list):
            continue
        try:
            cat_domain, cat_diff = cat_key.rsplit('_', 1)
        except ValueError:
            print(f"Warning: Skipping malformed category key '{cat_key}' (expected '<domain>_<difficulty>')")
            continue

        ensure_category(target_data, cat_key)

        for q in arr:
            # Validate raw question first
            errs = validate_question(q)
            # Normalize to category
            q_norm = normalize_to_category(q, cat_domain, cat_diff)

            # Duplicate check key
            key = (q_norm['domain'], q_norm['difficulty'], norm_text(q_norm['title']), norm_text(q_norm['question']))

            if any(e for e in errs if not e.startswith('Info:')):
                invalid += 1
                print(f"Invalid question skipped in '{cat_key}': {q.get('title','<no title>')}\n  - " + "\n  - ".join(errs))
                continue

            if key in existing_idx:
                skipped_dupes += 1
                continue

            # Append
            target_data['questions'][cat_key].append(q_norm)
            existing_idx[key] = True
            added += 1
            per_category_added[cat_key] = per_category_added.get(cat_key, 0) + 1

    # Summary
    print('Merge summary:')
    print(f'  Added: {added}')
    print(f'  Duplicates skipped: {skipped_dupes}')
    print(f'  Invalid skipped: {invalid}')
    if per_category_added:
        print('  Added per category:')
        for k, v in sorted(per_category_added.items()):
            print(f'    - {k}: {v}')

    if apply and added > 0:
        if os.path.exists(target_path):
            bkp = backup_file(target_path)
            print(f"  Backup created: {bkp}")
        save_json(target_path, target_data)
        print(f"  Wrote merged data to: {target_path}")
    else:
        print('  Dry-run (no files modified). Use --apply to write changes.')

    return 0


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description='Validate and merge questions into questions.json')
    parser.add_argument('--source', default=DEFAULT_SOURCE, help='Path to new questions file (default: tobeAddedQuestions.json)')
    parser.add_argument('--target', default=DEFAULT_TARGET, help='Path to target questions file (default: questions.json)')
    parser.add_argument('--apply', action='store_true', help='Write changes to target (creates a timestamped backup)')

    args = parser.parse_args(argv)

    try:
        return merge(args.source, args.target, apply=args.apply)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
