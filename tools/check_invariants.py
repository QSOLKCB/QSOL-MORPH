#!/usr/bin/env python3
"""Validate a deliberately narrow documentation/registry contract (stdlib only)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

REGISTRY = 'spec/core-invariants.json'
BASELINE = 'spec/history/core-invariants-1.0.0.json'
CORE = 'docs/CORE-INVARIANTS.md'
BEGIN = '<!-- BEGIN QSOL CORE INVARIANTS -->'
END = '<!-- END QSOL CORE INVARIANTS -->'
ID = re.compile(r'QM-INV-[0-9]{3}')
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')


class Invalid(ValueError):
    """Invalid registry or controlled documentation."""


def require(condition, message):
    if not condition:
        raise Invalid(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate JSON key: {key}')
        result[key] = value
    return result


def load_registry(path):
    try:
        data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid(f'{path}: {exc}') from exc
    require(isinstance(data, dict) and set(data) == {'schema_version', 'registry_version', 'invariants'}, 'invalid registry fields')
    require(type(data['schema_version']) is int and data['schema_version'] == 1, 'unsupported schema_version')
    require(isinstance(data['registry_version'], str) and VERSION.fullmatch(data['registry_version']), 'invalid registry_version')
    entries = data['invariants']
    require(isinstance(entries, list) and bool(entries), 'invariants must be a nonempty array')
    seen = set()
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == {'id', 'title', 'statement', 'documents'}, 'invalid invariant fields')
        ident = entry['id']
        require(isinstance(ident, str) and ID.fullmatch(ident), 'missing or malformed invariant ID')
        require(ident not in seen, f'duplicate invariant ID: {ident}')
        seen.add(ident)
        for key in ('title', 'statement'):
            value = entry[key]
            require(isinstance(value, str) and value.strip() == value and bool(value), f'{ident}: empty or untrimmed {key}')
            require(not any(c in value for c in '\r\n<>'), f'{ident}: {key} must be one plain-text line')
        require(re.search(r'\b(MUST|SHOULD)\b', entry['statement']), f'{ident}: missing requirement language')
        docs = entry['documents']
        require(isinstance(docs, list) and bool(docs), f'{ident}: documents must be a nonempty array')
        require(all(isinstance(p, str) for p in docs), f'{ident}: invalid document path')
        require(len(docs) == len(set(docs)), f'{ident}: duplicate document path')
        for name in docs:
            path = PurePosixPath(name)
            require(not path.is_absolute() and str(path) == name and '..' not in path.parts and '\\' not in name and name.endswith('.md') and name != CORE, f'{ident}: unsafe or invalid document path: {name}')
            require(len(path.parts) == 1 or path.parts[0] == 'docs', f'{ident}: document outside documentation scope: {name}')
    require([e['id'] for e in entries] == sorted(seen), 'invariants must be ordered by ID')
    return data


def check_compatibility(current, baseline):
    old = {e['id']: e for e in baseline['invariants']}
    new = {e['id']: e for e in current['invariants']}
    # This first contract deliberately rejects breaking edits. A later explicit
    # migration PR must introduce its own reviewed baseline and migration checks.
    for ident, entry in old.items():
        require(ident in new, f'missing frozen invariant ID: {ident}')
        require(all(new[ident][k] == entry[k] for k in ('title', 'statement')), f'{ident}: frozen normative statement/title changed; explicit migration required')
    before = tuple(map(int, baseline['registry_version'].split('.')))
    after = tuple(map(int, current['registry_version'].split('.')))
    require(after >= before, 'registry version regressed')
    require(after[0] == before[0], 'major-version migration requires separate reviewed tooling')
    if new.keys() != old.keys():
        require(after[1] > before[1], 'new invariants require a minor version increment')
        require(min(new.keys() - old.keys()) > max(old), 'new IDs must be appended, not reused or backfilled')


def render_block(registry, document):
    entries = registry['invariants'] if document == CORE else [e for e in registry['invariants'] if document in e['documents']]
    lines = [BEGIN, '', f"Registry version: {registry['registry_version']}", '']
    for entry in entries:
        lines += [f"### {entry['id']}: {entry['title']}", '', entry['statement'], '']
    return '\n'.join(lines + [END])


def documentation_paths(root):
    return sorted(set(root.glob('*.md')) | set((root / 'docs').rglob('*.md')))


def validate(root):
    root = root.resolve()
    registry = load_registry(root / REGISTRY)
    baseline = load_registry(root / BASELINE)
    check_compatibility(registry, baseline)
    required = {CORE} | {p for e in registry['invariants'] for p in e['documents']}
    known = {e['id'] for e in registry['invariants']}
    found = set()
    for path in documentation_paths(root):
        require(path.resolve().is_relative_to(root), f'document escapes repository: {path}')
        name = path.relative_to(root).as_posix()
        text = path.read_text(encoding='utf-8')
        for match in ID.finditer(text):
            require(match.group() in known, f'{name}: dangling invariant reference: {match.group()}')
        if name in required:
            found.add(name)
            require(text.count(BEGIN) == 1 and text.count(END) == 1, f'{name}: missing or duplicate controlled block')
            start, stop = text.index(BEGIN), text.index(END)
            require(stop > start, f'{name}: reversed controlled block')
            actual = text[start:stop + len(END)]
            require(actual == render_block(registry, name), f'{name}: controlled statements disagree with registry')
        else:
            require(BEGIN not in text and END not in text, f'{name}: unregistered controlled block')
    require(found == required, 'missing registered documents: ' + ', '.join(sorted(required - found)))
    return registry


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        registry = validate(args.root)
    except (Invalid, OSError, UnicodeError) as exc:
        print(f'invariant check failed: {exc}', file=sys.stderr)
        return 1
    print(f"Validated {len(registry['invariants'])} core invariants at registry {registry['registry_version']} (controlled documentation only).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
