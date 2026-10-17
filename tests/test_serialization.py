"""Golden bytes, complete-tree preservation, and hostile transport rejection."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import serialization as ser
from check_model import Invalid, load, validate

FIXTURES = ROOT / 'tests/fixtures/serialization'
POSITIVE = ROOT / 'tests/fixtures/model/positive'


def minimal():
    return load(POSITIVE / 'minimal.json')


def card(program):
    return program['jobs'][0]['decks'][0]['cards'][0]


def wire(program):
    return json.loads(ser.dumps(program))


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


class SerializationTests(unittest.TestCase):
    def test_profile_history(self):
        self.assertEqual(ser.PROFILE.read_bytes(), ser.PROFILE_HISTORY.read_bytes())
        self.assertEqual(hashlib.sha256(ser.PROFILE.read_bytes()).hexdigest(), ser.PROFILE_SHA256)
        for target in ('PROFILE', 'PROFILE_HISTORY'):
            with self.subTest(target=target), patch.object(ser, target) as path:
                path.read_bytes.return_value = b'{}'
                with self.assertRaises(Invalid):
                    ser.dumps(minimal())

    def test_all_golden_bytes_and_roundtrips(self):
        cases = json.loads((FIXTURES / 'manifest.json').read_text())
        for case in cases:
            program = ser.loads((FIXTURES / (case['name'] + '.json')).read_bytes())
            if case.get('model_fixture'):
                self.assertEqual(program, load(ROOT / case['model_fixture']))
            for fmt in ser.FORMATS:
                with self.subTest(case=case['name'], format=fmt):
                    data = (FIXTURES / (case['name'] + '.' + fmt)).read_bytes()
                    self.assertEqual(ser.dumps(program, fmt), data)
                    self.assertEqual(ser.loads(data, fmt), program)
                    self.assertEqual(ser.dumps(ser.loads(data, fmt), fmt), data)
                    self.assertEqual(ser.fingerprint(program), case['fingerprint'])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), case['files'][fmt])

    def test_model_positives_cross_format(self):
        for path in POSITIVE.glob('*.json'):
            program = load(path)
            original = copy.deepcopy(program)
            for src in ser.FORMATS:
                for dst in ser.FORMATS:
                    out = ser.loads(ser.dumps(ser.loads(ser.dumps(program, src), src), dst), dst)
                    self.assertEqual(out, original)
            self.assertEqual(program, original)

    def test_all_model_negatives_reject_each_encoder(self):
        for path in (ROOT / 'tests/fixtures/model/negative').glob('*.json'):
            for fmt in ser.FORMATS:
                with self.subTest(path=path.name, format=fmt), self.assertRaises(Invalid):
                    ser.dumps(load(path), fmt)

    def test_all_model_negatives_reject_each_decoder(self):
        for path in (ROOT / 'tests/fixtures/model/negative').glob('*.json'):
            bad = load(path)
            for fmt in ('json', 'xml'):
                data = (compact(ser._envelope(bad)) if fmt == 'json' else
                        ('<qsol-morph serialization-version="1.0.0">' +
                         ser._xml(ser._wire(bad)) + '</qsol-morph>').encode('ascii'))
                with self.subTest(path=path.name, format=fmt), self.assertRaises(Invalid):
                    ser.loads(data, fmt)

    def test_strings_exact_codepoints(self):
        values = ['', '\0\b\t\n\r\f\x1f\x7f', '"\\/&<>', '\u00e9', 'e\u0301',
                  '\u2028\u2029', '\ufffe\uffff', '\U00010000\U0010ffff',
                  '\ud800', '\udfff', '\ud800\udc00', '\udfff\ud800',
                  '\U00010000\ud800\udc00', '{"$qsol_string":[55296]}']
        fingerprints = []
        for value in values:
            program = minimal()
            card(program)['value'] = {'type': 'TEXT', 'unit': '1', 'value': value}
            validate(program)
            for fmt in ser.FORMATS:
                data = ser.dumps(program, fmt)
                self.assertTrue(data.isascii())
                self.assertEqual(ser.loads(data, fmt), program)
            fingerprints.append(ser.fingerprint(program))
        self.assertEqual(len(fingerprints), len(set(fingerprints)))

    def test_every_codepoint_boundary_and_surrogate(self):
        program = minimal()
        text = ''.join(map(chr, list(range(0xD800, 0xE000)) +
                           [0, 0x7f, 0x80, 0xD7FF, 0xE000, 0xFFFF, 0x10000, 0x10FFFF]))
        card(program)['value'] = {'type': 'TEXT', 'unit': '1', 'value': text}
        for fmt in ser.FORMATS:
            self.assertEqual(ser.loads(ser.dumps(program, fmt), fmt), program)

    def test_source_id_exceptional_text(self):
        program = minimal()
        for scope in (program['jobs'][0], program['jobs'][0]['decks'][0], card(program)):
            scope['source_location'] = {'source_id': 'x\0\ud800\udc00\r',
                                        'start': {'line': 1, 'column': 1},
                                        'end': {'line': 1, 'column': 2}}
        for fmt in ser.FORMATS:
            self.assertEqual(ser.loads(ser.dumps(program, fmt), fmt), program)

    def test_object_order_irrelevant_arrays_retained(self):
        program = load(POSITIVE / 'repeated-local-ids.json')
        def reverse(node):
            if isinstance(node, dict):
                return {k: reverse(v) for k, v in reversed(list(node.items()))}
            if isinstance(node, list):
                return [reverse(v) for v in node]
            return node
        for fmt in ser.FORMATS:
            self.assertEqual(ser.dumps(program, fmt), ser.dumps(reverse(program), fmt))
            self.assertEqual(ser.loads(ser.dumps(program, fmt), fmt), program)

    def test_absence_metadata_and_typed_values_change_identity(self):
        original = minimal()
        variants = []
        explicit = copy.deepcopy(original)
        explicit['jobs'][0]['failure_behavior'] = {'policy': 'FAIL_STOP'}
        variants.append(explicit)
        for kind, value in [('INTEGER', '1'), ('DECIMAL', '1'), ('TEXT', '1'), ('BOOLEAN', True)]:
            p = copy.deepcopy(original)
            card(p)['value'] = {'type': kind, 'unit': '1', 'value': value}
            variants.append(p)
        self.assertEqual(len(set(ser.fingerprint(p) for p in [original] + variants)), 6)

    def test_exact_source_integer_import(self):
        p = minimal()
        p['jobs'][0]['source_location'] = {'source_id': 'src', 'start': {'line': 1, 'column': 1},
                                          'end': {'line': 9007199254740993, 'column': 1}}
        data = json.dumps(p).replace('9007199254740993', '9007199254740993e0').encode()
        self.assertEqual(ser.read_model(data), p)
        p['jobs'][0]['source_location']['start']['line'] = 1.0
        self.assertEqual(ser.loads(ser.dumps(p))['jobs'][0]['source_location']['start']['line'], 1)
        self.assertEqual(type(ser.loads(ser.dumps(p))['jobs'][0]['source_location']['start']['line']), int)

    def test_huge_typed_numbers_not_coerced(self):
        p = minimal()
        for kind, number in [('INTEGER', '9' * 5000), ('DECIMAL', '9' * 5000 + '.0001')]:
            card(p)['value'] = {'type': kind, 'unit': 'm', 'value': number}
            for fmt in ser.FORMATS:
                self.assertEqual(ser.loads(ser.dumps(p, fmt), fmt), p)

    def test_json_strict_bytes(self):
        data = ser.dumps(minimal())
        for bad in (data + b'\n', b' ' + data, b'\xef\xbb\xbf' + data,
                    data.replace(b'"jobs"', b'"j\\u006fbs"'),
                    data.replace(b'"model":', b'"model":{},"model":'),
                    data.decode().encode('utf-16'), data + b'{}', b'null', b'[]', b'NaN'):
            with self.subTest(bad=bad[:50]), self.assertRaises(Invalid):
                ser.loads(bad)

    def test_unknown_envelope_fields_and_versions(self):
        original = wire(minimal())
        for key, val in [('format', 'unknown'), ('serialization_version', '2.0.0'), ('extra', 1)]:
            data = copy.deepcopy(original); data[key] = val
            with self.assertRaises(Invalid): ser.loads(compact(data))
        for key in original:
            data = copy.deepcopy(original); del data[key]
            with self.assertRaises(Invalid): ser.loads(compact(data))

    def test_malformed_exceptional_tags(self):
        p = minimal(); card(p)['value'] = {'type': 'TEXT', 'unit': '1', 'value': '\ud800'}
        original = wire(p)
        for tag in [{ser.TAG: []}, {ser.TAG: [True]}, {ser.TAG: [-1]},
                    {ser.TAG: [1114112]}, {ser.TAG: [65]}, {ser.TAG: '55296'},
                    {ser.TAG: [55296], 'extra': 1}, {ser.TAG: [55296, None]}]:
            data = copy.deepcopy(original)
            card(data['model'])['value']['value'] = tag
            with self.subTest(tag=tag), self.assertRaises(Invalid):
                ser.loads(compact(data))
        # An untagged lone surrogate is rejected, not silently normalized.
        data = copy.deepcopy(original); card(data['model'])['value']['value'] = '\ud800'
        with self.assertRaises(Invalid): ser.loads(compact(data))

    def test_tag_collision_and_wrong_field_type(self):
        data = wire(minimal()); data['model'][ser.TAG] = [55296]
        with self.assertRaises(Invalid): ser.loads(compact(data))
        data = wire(minimal()); data['model']['jobs'][0]['decks'] = {ser.TAG: [55296]}
        with self.assertRaises(Invalid): ser.loads(compact(data))

    def test_jsonl_stream_and_all_prefix_truncations(self):
        data = ser.dumps(minimal(), 'jsonl')
        self.assertEqual(ser.load_jsonl(io.BytesIO(data)), minimal())
        for end in range(len(data)):
            with self.subTest(end=end), self.assertRaises(Invalid):
                ser.loads(data[:end], 'jsonl')

    def test_jsonl_corruption_and_trailing_content(self):
        data = ser.dumps(minimal(), 'jsonl')
        lines = data.splitlines(keepends=True)
        bad = [b'\n' + data, data + b'\n', data + lines[-1], data.replace(b'\n', b'\r\n'),
               lines[0] + lines[1] + lines[1] + lines[-1],
               data.replace(b'"index":0', b'"index":1'),
               data.replace(b'"index":0', b'"index":false'),
               data.replace(b'"job_count":1', b'"job_count":true'),
               data.replace(b'"job_count":1', b'"job_count":2'),
               data.replace(b'"end":true', b'"end":false'),
               data.replace(b'sha256:', b'sha257:')]
        for value in bad:
            with self.subTest(value=value[:60]), self.assertRaises(Invalid):
                ser.loads(value, 'jsonl')

    def test_multi_job_order(self):
        p = minimal(); p['jobs'].append(copy.deepcopy(p['jobs'][0])); p['jobs'][1]['id'] = 'second'
        lines = ser.dumps(p, 'jsonl').splitlines(keepends=True)
        self.assertEqual(ser.loads(b''.join(lines), 'jsonl'), p)
        for bad in [lines[:1] + [lines[2], lines[1]] + lines[3:], lines[:2] + [lines[1]] + lines[3:]]:
            with self.assertRaises(Invalid): ser.loads(b''.join(bad), 'jsonl')
        reversed_p = copy.deepcopy(p); reversed_p['jobs'].reverse()
        self.assertNotEqual(ser.fingerprint(p), ser.fingerprint(reversed_p))

    def test_xml_rejects_unsafe_or_noncanonical_forms(self):
        data = ser.dumps(minimal(), 'xml')
        bad = [b'<?xml version="1.0"?>' + data, b'<!DOCTYPE x [<!ENTITY x "oops">]>' + data,
               b'<!--hello-->' + data, data + b'\n', data.replace(b'<object>', b'<object x="1">', 1),
               data.replace(b'<array>', b'<array>text', 1), data.replace(b'</string>', b'<array></array></string>', 1),
               data.replace(b'<string>', b'<unknown>', 1), data.replace(b'</string>', b'</string>tail', 1),
               data.replace(b'<array></array>', b'<array/>'),
               data.replace(b'&', b'&#38;'),
               data.replace(b'<string>"1.0.0"</string>', b'<string>&quot;1.0.0&quot;</string>')]
        for value in bad:
            if value == data: continue
            with self.subTest(value=value[:100]), self.assertRaises(Invalid):
                ser.loads(value, 'xml')

    def test_xml_duplicate_members(self):
        data = ser.dumps(minimal(), 'xml')
        member = b'<member name="schema_version"><string>"1.0.0"</string></member>'
        self.assertIn(member, data)
        with self.assertRaises(Invalid): ser.loads(data.replace(member, member * 2), 'xml')

    def test_nonfinite_and_fractional_import_rejected(self):
        p = minimal(); p['jobs'][0]['source_location'] = {'source_id': 'src',
             'start': {'line': 1, 'column': 1}, 'end': {'line': 2, 'column': 1}}
        data = json.dumps(p)
        for token in ['NaN', 'Infinity', '-Infinity', '1.00000000000000000000000000001', 'false']:
            with self.subTest(token=token), self.assertRaises(Invalid):
                ser.read_model(data.replace('"line": 1', '"line": ' + token).encode())

    def test_exponent_resource_limit_before_integer_allocation(self):
        if sys.get_int_max_str_digits():
            with self.assertRaisesRegex(Invalid, 'resource limit'):
                ser.read_model(b'{"source":1e999999999}')
        self.assertEqual(ser._parse(b'0e999999999'), 0)

    def test_exponents_beyond_decimal_host_range(self):
        for token in (b'1e9999999999999999999999999999999',
                      b'1e-9999999999999999999999999999999'):
            with self.assertRaisesRegex(ser.ResourceLimit, 'exponent resource limit'):
                ser.read_model(token)
            run = subprocess.run([sys.executable, str(ROOT / 'tools/serialization.py'), '-'],
                                 input=token, capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(run.stdout, b'')
            self.assertIn(b'resource limit', run.stderr)
            self.assertNotIn(b'Traceback', run.stderr)

    def test_valid_huge_source_integer_reports_resource_limit(self):
        limit = sys.get_int_max_str_digits()
        if not limit:
            self.skipTest('host integer conversion is unbounded')
        p = minimal()
        p['jobs'][0]['source_location'] = {'source_id': 'src',
            'start': {'line': 1, 'column': 1}, 'end': {'line': 10 ** limit, 'column': 1}}
        validate(p)  # This is valid model data, not a semantic rejection.
        with self.assertRaises(ser.ResourceLimit):
            ser.read_model(('1' + '0' * limit).encode())
        for fmt in ser.FORMATS:
            with self.assertRaisesRegex(ser.ResourceLimit, 'resource limit'):
                ser.dumps(p, fmt)
        with self.assertRaises(ser.ResourceLimit):
            ser.fingerprint(p)

    def test_wrong_input_types_and_format(self):
        for value in ('{}', {}, None):
            with self.assertRaises(Invalid): ser.loads(value)
        with self.assertRaises(Invalid): ser.dumps(minimal(), 'qsl')
        with self.assertRaises(Invalid): ser.loads(b'{}', 'qsl')

    def test_cli_pipeline_and_hash(self):
        script = str(ROOT / 'tools/serialization.py')
        src = str(POSITIVE / 'minimal.json')
        for fmt in ser.FORMATS:
            run = subprocess.run([sys.executable, script, src, '--to', fmt], capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout, ser.dumps(minimal(), fmt))
            result = subprocess.run([sys.executable, script, '-', '--from', fmt, '--hash'],
                                    input=run.stdout, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.decode().strip(), ser.fingerprint(minimal()))

    def test_cli_invalid_has_no_stdout(self):
        for source, data in [('model', b'{"jobs":[],"schema_version":"1.0.0"}'),
                             ('json', b'{}'), ('xml', b'<!DOCTYPE x><x/>'), ('jsonl', b'{}\n')]:
            run = subprocess.run([sys.executable, str(ROOT / 'tools/serialization.py'), '-',
                                  '--from', source], input=data, capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(run.stdout, b'')
            self.assertIn(b'serialization:', run.stderr)


if __name__ == '__main__':
    unittest.main()
