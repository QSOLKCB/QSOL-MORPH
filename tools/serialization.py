#!/usr/bin/env python3
"""Lossless canonical model transports, profile 1.0.0. No execution or lowering."""
from __future__ import annotations

import argparse
from decimal import Decimal, DecimalException
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

try:
    from .check_model import Invalid, require, unique_object, validate
except ImportError:
    from check_model import Invalid, require, unique_object, validate

VERSION = '1.0.0'
TAG = '$qsol_string'
FORMATS = ('json', 'jsonl', 'xml')
PROFILE = Path(__file__).resolve().parents[1] / 'spec/serialization-profile.json'
PROFILE_HISTORY = PROFILE.parent / 'history/serialization-profile-1.0.0.json'
PROFILE_SHA256 = 'd0ebff808b83a888b7d41c9971eb02c1bc07596d8c0863b235d7b9d3cf586c01'


def _profile():
    historical = PROFILE_HISTORY.read_bytes()
    require(hashlib.sha256(historical).hexdigest() == PROFILE_SHA256,
            'historical serialization profile changed; migration required')
    require(PROFILE.read_bytes() == historical,
            'serialization profile differs from frozen history; migration required')


class ResourceLimit(Invalid):
    """The host cannot process this valid-size-unbounded model, not nonconformance."""


def _integer_bound(node):
    limit = sys.get_int_max_str_digits()
    if limit and abs(node) >= 10 ** limit:
        raise ResourceLimit('integer digit resource limit exceeded')
    return node


def _integral(node):
    """JSON numbers here are mathematical integers, not binary float tokens."""
    if isinstance(node, dict):
        return {key: _integral(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_integral(value) for value in node]
    if isinstance(node, (float, Decimal)):
        require(math.isfinite(node) if isinstance(node, float) else node.is_finite(),
                'non-finite number')
        if isinstance(node, Decimal):
            # Match the host's existing integer-string resource bound before an
            # exponent token can allocate an enormous integer (e.g. 1e999999999).
            limit = sys.get_int_max_str_digits()
            if limit and node and node.adjusted() >= limit:
                raise ResourceLimit('integer digit resource limit exceeded')
        require(node == int(node), 'non-integral JSON number')
        return _integer_bound(int(node))
    if type(node) is int:
        return _integer_bound(node)
    return node


def _parse(data):
    def reject(value):
        raise Invalid('non-JSON number: ' + value)
    def decimal(token):
        try:
            return Decimal(token)
        except DecimalException as exc:
            raise ResourceLimit('decimal exponent resource limit exceeded') from exc
    def integer(token):
        limit = sys.get_int_max_str_digits()
        if limit and len(token.lstrip('-')) > limit:
            raise ResourceLimit('integer digit resource limit exceeded')
        return int(token)
    try:
        # Decode explicitly: json.loads(bytes) would also accept UTF-16/32.
        text = data.decode('utf-8') if isinstance(data, bytes) else data
        return _integral(json.loads(text, object_pairs_hook=unique_object,
                                    parse_int=integer, parse_float=decimal, parse_constant=reject))
    except ResourceLimit:
        raise
    except (UnicodeError, json.JSONDecodeError, ValueError, OverflowError,
            RecursionError) as exc:
        raise Invalid('invalid JSON: ' + str(exc)) from exc


def read_model(data):
    """Import ordinary model JSON; exact number parsing, no transport claim."""
    program = _parse(data)
    validate(program)
    return program


def _model(program):
    _profile()
    # Copy, validate and retain all arrays/fields/owners, including absent fields.
    result = _integral(program)
    validate(result)
    return result


def _wire(node):
    if isinstance(node, str):
        if any(0xD800 <= ord(ch) <= 0xDFFF for ch in node):
            return {TAG: [ord(ch) for ch in node]}
        return node
    if isinstance(node, dict):
        return {key: _wire(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_wire(value) for value in node]
    return node


def _unwire(node):
    if isinstance(node, dict):
        if TAG in node:
            require(set(node) == {TAG}, 'exceptional string tag has extra fields')
            points = node[TAG]
            require(isinstance(points, list) and points and
                    all(type(n) is int and 0 <= n <= 0x10FFFF for n in points),
                    'exceptional string requires valid integer code points')
            require(any(0xD800 <= n <= 0xDFFF for n in points),
                    'ordinary strings must not use exceptional string tag')
            return ''.join(chr(n) for n in points)
        return {key: _unwire(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_unwire(value) for value in node]
    if isinstance(node, str):
        require(not any(0xD800 <= ord(ch) <= 0xDFFF for ch in node),
                'surrogate code points require exceptional string tag')
    return node


def _json(node):
    return json.dumps(node, ensure_ascii=True, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('ascii')


def _envelope(program):
    return {'format': 'QSOL-MORPH-JSON', 'serialization_version': VERSION,
            'model': _wire(program)}


def fingerprint(program):
    """sha256 of canonical JSON envelope; includes metadata, not semantic equivalence."""
    return 'sha256:' + hashlib.sha256(_json(_envelope(_model(program)))).hexdigest()


def iter_jsonl(program):
    """Yield canonical byte lines after validating the full input model.

    Whole JOB records retain nested ownership and order. This is record streaming,
    not constant-memory model validation or permission to execute partial input.
    """
    program = _model(program)
    count = len(program['jobs'])
    yield _json({'format': 'QSOL-MORPH-JSONL', 'serialization_version': VERSION,
                 'schema_version': program['schema_version'], 'job_count': count}) + b'\n'
    for index, job in enumerate(program['jobs']):
        yield _json({'index': index, 'job': _wire(job)}) + b'\n'
    yield _json({'end': True, 'job_count': count,
                 'model_sha256': fingerprint(program)}) + b'\n'


def _xml(node):
    if isinstance(node, dict):
        return '<object>' + ''.join('<member name="' + key + '">' + _xml(node[key]) +
                                  '</member>' for key in sorted(node)) + '</object>'
    if isinstance(node, list):
        return '<array>' + ''.join(_xml(value) for value in node) + '</array>'
    if isinstance(node, str):
        return '<string>' + escape(_json(node).decode('ascii')) + '</string>'
    if type(node) is bool:
        return '<boolean>' + ('true' if node else 'false') + '</boolean>'
    if type(node) is int:
        return '<integer>' + str(node) + '</integer>'
    raise Invalid('unsupported XML value')


def dumps(program, format='json'):
    """Return canonical bytes. Validation does not modify the supplied model."""
    require(format in FORMATS, 'unknown serialization format')
    program = _model(program)
    if format == 'json':
        return _json(_envelope(program))
    if format == 'jsonl':
        return b''.join(iter_jsonl(program))
    return ('<qsol-morph serialization-version="' + VERSION + '">' +
            _xml(_wire(program)) + '</qsol-morph>').encode('ascii')


def load_jsonl(lines):
    """Consume byte lines; return only after end/count/digest and all model checks."""
    _profile()
    iterator = iter(lines)
    try:
        raw = next(iterator)
    except StopIteration as exc:
        raise Invalid('missing JSONL header') from exc

    def record(raw):
        require(type(raw) is bytes and raw.endswith(b'\n') and b'\n' not in raw[:-1],
                'JSONL requires one byte record with final LF per line')
        value = _parse(raw[:-1])
        require(_json(value) + b'\n' == raw, 'noncanonical JSONL record')
        require(isinstance(value, dict), 'JSONL record must be an object')
        return value

    header = record(raw)
    require(set(header) == {'format', 'serialization_version', 'schema_version', 'job_count'},
            'invalid JSONL header fields')
    require(header['format'] == 'QSOL-MORPH-JSONL' and
            header['serialization_version'] == VERSION and header['schema_version'] == VERSION,
            'unknown JSONL format/version')
    count = header['job_count']
    require(type(count) is int and count > 0, 'invalid JOB count')
    jobs = []
    for index in range(count):
        try:
            item = record(next(iterator))
        except StopIteration as exc:
            raise Invalid('truncated JSONL JOB records') from exc
        require(set(item) == {'index', 'job'} and type(item['index']) is int and
                item['index'] == index, 'missing, duplicate, or out-of-order JOB index')
        jobs.append(_unwire(item['job']))
    try:
        end = record(next(iterator))
    except StopIteration as exc:
        raise Invalid('missing JSONL end record') from exc
    program = {'schema_version': header['schema_version'], 'jobs': jobs}
    validate(program)
    require(set(end) == {'end', 'job_count', 'model_sha256'} and end['end'] is True and
            type(end['job_count']) is int and end['job_count'] == count and
            end['model_sha256'] == fingerprint(program), 'invalid JSONL end/count/digest')
    try:
        next(iterator)
    except StopIteration:
        return program
    raise Invalid('trailing JSONL content')


def _read_xml(data):
    # ASCII-only canonical XML has no declarations, DTDs, entities, comments,
    # processing instructions, namespaces, or external resolution paths.
    require(data.isascii(), 'canonical XML must be ASCII')
    require(b'<!' not in data and b'<?' not in data, 'XML declarations/DTD/comments/PI forbidden')
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise Invalid('invalid XML: ' + str(exc)) from exc
    require(root.tag == 'qsol-morph' and root.attrib == {'serialization-version': VERSION}
            and len(root) == 1 and not root.text and not root.tail, 'invalid XML envelope')

    def value(element):
        require(not element.attrib and not element.tail, 'unexpected XML attributes/tail')
        if element.tag == 'object':
            require(not element.text, 'mixed XML object text')
            pairs = []
            for member in element:
                require(member.tag == 'member' and set(member.attrib) == {'name'} and
                        not member.text and not member.tail and len(member) == 1,
                        'invalid XML member')
                pairs.append((member.attrib['name'], value(member[0])))
            return unique_object(pairs)
        if element.tag == 'array':
            require(not element.text, 'mixed XML array text')
            return [value(child) for child in element]
        require(len(element) == 0, 'XML scalar has children')
        text = element.text or ''
        if element.tag == 'string':
            result = _parse(text)
            require(type(result) is str, 'XML string requires a JSON-quoted string')
            return result
        if element.tag == 'integer':
            result = _parse(text)
            require(type(result) is int, 'invalid XML integer')
            return result
        if element.tag == 'boolean':
            require(text in ('true', 'false'), 'invalid XML boolean')
            return text == 'true'
        raise Invalid('unknown XML value type')

    return _unwire(value(root[0]))


def loads(data, format='json'):
    """Read strict canonical bytes; use read_model for ordinary model JSON import."""
    require(type(data) is bytes, 'transport input must be bytes')
    require(format in FORMATS, 'unknown serialization format')
    try:
        if format == 'jsonl':
            return load_jsonl(data.splitlines(keepends=True))
        if format == 'json':
            envelope = _parse(data)
            require(isinstance(envelope, dict) and
                    set(envelope) == {'format', 'serialization_version', 'model'},
                    'invalid JSON envelope')
            require(envelope['format'] == 'QSOL-MORPH-JSON' and
                    envelope['serialization_version'] == VERSION, 'unknown JSON format/version')
            program = _unwire(envelope['model'])
        else:
            program = _read_xml(data)
        validate(program)
        require(dumps(program, format) == data, 'noncanonical ' + format + ' bytes')
        return program
    except ResourceLimit:
        raise
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise Invalid(str(exc)) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='input path or - for stdin')
    parser.add_argument('--from', dest='source', choices=('model',) + FORMATS, default='model')
    parser.add_argument('--to', choices=FORMATS, default='json')
    parser.add_argument('--hash', action='store_true', help='print canonical JSON SHA-256 instead')
    args = parser.parse_args(argv)
    try:
        data = sys.stdin.buffer.read() if args.input == '-' else Path(args.input).read_bytes()
        program = read_model(data) if args.source == 'model' else loads(data, args.source)
        output = (fingerprint(program) + '\n').encode('ascii') if args.hash else dumps(program, args.to)
        sys.stdout.buffer.write(output)
    except (Invalid, OSError, ValueError, TypeError, RecursionError) as exc:
        print('serialization: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
