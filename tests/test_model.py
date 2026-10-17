"""Data-model shape, reference, composition, preservation and negative fixtures."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import check_model as model

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/model'


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.program = model.load(FIXTURES / 'positive/cross-deck-bindings.json')
        self.job = self.program['jobs'][0]
        self.first = self.job['decks'][0]['cards'][0]
        self.consumer = self.job['decks'][1]['cards'][0]
        self.last = self.job['decks'][1]['cards'][1]

    def reject(self, expected):
        with self.assertRaisesRegex(model.Invalid, expected):
            model.validate(self.program)

    def test_positive_fixtures_are_unchanged(self):
        for path in sorted((FIXTURES / 'positive').glob('*.json')):
            with self.subTest(path=path.name):
                program = model.load(path)
                original = copy.deepcopy(program)
                self.assertIsNone(model.validate(program))
                self.assertEqual(program, original)

    def test_full_negative_fixtures(self):
        cases = model.load(FIXTURES / 'negative/cases.json')
        self.assertEqual({entry['file'] for entry in cases},
                         {p.name for p in (FIXTURES / 'negative').glob('*.json')} - {'cases.json'})
        for case in cases:
            with self.subTest(file=case['file']):
                with self.assertRaisesRegex(model.Invalid, case['expected_error']):
                    model.validate(model.load(FIXTURES / 'negative' / case['file']))

    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'duplicate.json'
            path.write_text('{"jobs": [], "jobs": []}')
            with self.assertRaisesRegex(model.Invalid, 'duplicate object key'):
                model.load(path)

    def test_non_json_numeric_constants(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.json'
            for value in ('NaN', 'Infinity', '-Infinity'):
                path.write_text(value)
                with self.subTest(value=value), self.assertRaisesRegex(model.Invalid, 'non-JSON number'):
                    model.load(path)

    def test_missing_or_unknown_version(self):
        for value in ('2.0.0', 1, True, None):
            self.program['schema_version'] = value
            self.reject('schema:')
        del self.program['schema_version']
        self.reject('schema:')

    def test_schema_rejects_unknown_fields_at_every_boundary(self):
        for node in (self.program, self.job, self.job['decks'][0], self.first,
                     self.first['value'], self.first['result_bindings'][0],
                     self.first['effect_requirements'][0], self.consumer['operands'][0],
                     self.consumer['dependencies'][0]['producer_ref']):
            with self.subTest(fields=list(node)):
                node['private_backend_field'] = 'silently discard me'
                self.reject('schema:')
                del node['private_backend_field']

    def test_type_and_unit_are_exact(self):
        for field, value in (('type', 'INTEGER'), ('unit', 'g')):
            original = self.consumer['operands'][0][field]
            self.consumer['operands'][0][field] = value
            self.reject('operand type/unit differs')
            self.consumer['operands'][0][field] = original

    def test_invalid_reference_terminal(self):
        self.consumer['dependencies'][0]['producer_ref']['producer_card_id'] = 'other'
        self.reject('terminal CARD')

    def test_wrong_typed_scope_path(self):
        self.consumer['dependencies'][0]['producer_ref']['owner_scope_path'][0]['scope_kind'] = 'DECK'
        self.reject('schema:')

    def test_unknown_full_owner_path(self):
        self.consumer['dependencies'][0]['producer_ref']['owner_scope_path'][0]['scope_id'] = 'missing'
        self.reject('unknown owner-qualified')

    def test_cross_job_binding_rejected(self):
        other = copy.deepcopy(self.job)
        other['id'] = 'other'
        self.program['jobs'].append(other)
        self.consumer['dependencies'][0]['producer_ref']['owner_scope_path'][0]['scope_id'] = 'other'
        self.reject('cross-JOB')

    def test_later_producer_rejected(self):
        reference = copy.deepcopy(self.last['operands'][0]['producer_ref'])
        self.first['dependencies'] = [{'dependency_id': 'future', 'producer_ref': reference}]
        self.reject('dependency must precede')

    def test_duplicate_dependency_target(self):
        duplicate = copy.deepcopy(self.consumer['dependencies'][0])
        duplicate['dependency_id'] = 'second'
        self.consumer['dependencies'].append(duplicate)
        self.reject('duplicate dependency target')

    def test_duplicate_order_edge(self):
        duplicate = copy.deepcopy(self.consumer['sequencing_constraints'][0])
        duplicate['constraint_id'] = 'zduplicate'
        self.consumer['sequencing_constraints'].append(duplicate)
        self.reject('duplicate sequencing edge')

    def test_future_sequencing_rejected(self):
        reference = copy.deepcopy(self.last['sequencing_constraints'][1]['predecessor_ref'])
        self.first['sequencing_constraints'] = [{'constraint_id':'future', 'kind':'SOURCE_ORDER', 'predecessor_ref':reference}]
        self.reject('sequencing predecessor must precede')

    def test_effect_order_requires_effectful_endpoints(self):
        self.last['sequencing_constraints'][0]['predecessor_ref'] = copy.deepcopy(self.last['sequencing_constraints'][1]['predecessor_ref'])
        self.reject('EFFECT_ORDER endpoints')

    def test_no_declaration_order_repair(self):
        self.consumer['sequencing_constraints'].reverse()
        before = copy.deepcopy(self.program)
        self.reject('unique and sorted')
        self.assertEqual(self.program, before)

    def test_capability_sets_complete_nonempty_unique_sorted(self):
        for capabilities in ([], ['READ', 'READ'], ['Z', 'A']):
            with self.subTest(capabilities=capabilities):
                self.first['effect_requirements'][0]['required_capabilities'] = capabilities
                self.reject('schema:|capabilities must be sorted')

    def test_multiple_effect_capabilities_preserved(self):
        self.first['effect_requirements'] = [
            {'effect_id':'ai', 'effect_kind':'AI_MODEL', 'required_capabilities':['AI_MODEL','NETWORK']},
            {'effect_id':'read', 'effect_kind':'READ_FILE', 'required_capabilities':['FILESYSTEM_READ']}]
        original = copy.deepcopy(self.program)
        model.validate(self.program)
        self.assertEqual(self.program, original)

    def test_machinery_keeps_separate_owners_with_same_local_id(self):
        program = model.load(FIXTURES / 'positive/scoped-contracts.json')
        job = program['jobs'][0]
        self.assertEqual(job['machinery_requirements'][0]['machinery_requirement_id'],
                         job['decks'][1]['machinery_requirements'][0]['machinery_requirement_id'])
        before = copy.deepcopy(program)
        model.validate(program)
        self.assertEqual(program, before)
        self.assertNotEqual(job['machinery_requirements'], job['decks'][1]['machinery_requirements'])

    def test_machinery_cannot_substitute_card_capabilities(self):
        self.first['required_capabilities'] = ['GPU']
        self.reject('schema:')

    def test_contract_all_descendant_changes_rejected(self):
        for facet, replacement in (
            ('result_determinism', 'STRICT'),
            ('numeric_contract', {'contract_id':'changed','version':'1.0.0','definition_hash':'sha256:'+'d'*64,'parameters':[]}),
            ('randomness_contract', {'mode':'NONE'})):
            for depth in ('deck','card'):
                with self.subTest(facet=facet, depth=depth):
                    self.program = model.load(FIXTURES / 'positive/scoped-contracts.json')
                    deck = self.program['jobs'][0]['decks'][1]
                    target = deck if depth == 'deck' else deck['cards'][0]
                    target[facet] = replacement
                    self.reject('unsupported '+facet+' refinement')

    def test_rng_replay_identity_is_complete(self):
        for missing in ('rng_algorithm','rng_version','seed','stream_id','parallel_partitioning'):
            with self.subTest(missing=missing):
                self.program = model.load(FIXTURES / 'positive/scoped-contracts.json')
                del self.program['jobs'][0]['randomness_contract'][missing]
                self.reject('schema:')

    def test_unsupported_extension_ranges_rejected(self):
        self.program = model.load(FIXTURES / 'positive/scoped-contracts.json')
        self.program['jobs'][0]['extension_requirements'][0]['required_version'] = '>=1.0.0'
        self.reject('schema:')

    def test_boolean_and_text_units(self):
        for type_, value in (('BOOLEAN', True), ('TEXT', 'literal')):
            self.first['value'] = {'type':type_, 'unit':'kg', 'value':value}
            self.reject('must be dimensionless')
            self.first['value']['unit'] = '1'
            model.validate(self.program)

    def test_boolean_result_unit(self):
        self.first['result_bindings'][0].update(type='BOOLEAN', unit='kg')
        self.reject('binding must be dimensionless')

    def test_exact_numeric_scalar_grammar(self):
        for type_, bad_values in (
            ('INTEGER', ['-0','01','1.0','+1',1,True,'1\n']),
            ('DECIMAL', ['-0','01','1.0','1e2','NaN','Infinity','+1',1.2,'1\n'])):
            for value in bad_values:
                with self.subTest(type=type_, value=value):
                    self.first['value'] = {'type':type_, 'unit':'1', 'value':value}
                    self.reject('schema:|negative decimal zero')

    def test_exact_large_values_and_literal_operands_preserved(self):
        self.first['value'] = {'type':'INTEGER', 'unit':'1', 'value':'9'*400}
        self.first['operands'] = [
            {'operand_id':'second', 'value':{'type':'TEXT', 'unit':'1', 'value':'literal\ntext'}},
            {'operand_id':'first', 'value':{'type':'DECIMAL', 'unit':'m/s', 'value':'-0.00000000000001'}}]
        before = copy.deepcopy(self.program)
        model.validate(self.program)
        self.assertEqual(self.program, before)

    def test_identifiers_reject_newline_and_whitespace(self):
        for value in ('value\n',' value','value ','','1value'):
            self.first['id'] = value
            self.reject('schema:')

    def test_source_span_validation(self):
        location = self.first['source_location']
        location['end'] = {'line':1,'column':1}
        model.validate(self.program)  # An empty span is legal.
        location['start'] = {'line':2,'column':1}
        self.reject('reversed source span')
        location['start'] = {'line':True,'column':1}
        self.reject('schema:')

    def test_schema_history_cannot_be_silently_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'schema.json'
            path.write_text('{}')
            with mock.patch.object(model, 'HISTORY', path):
                self.reject('historical model schema changed')
            with mock.patch.object(model, 'SCHEMA', path):
                self.reject('differs from frozen history')

    def test_each_local_declaration_key_is_unique(self):
        for field, key in (('result_bindings', 'result_binding_id'),
                           ('effect_requirements', 'effect_id')):
            with self.subTest(field=field):
                original = copy.deepcopy(self.first[field])
                self.first[field].append(copy.deepcopy(original[0]))
                self.reject('unique and sorted')
                self.first[field] = original
        self.consumer['operands'].append(copy.deepcopy(self.consumer['operands'][0]))
        self.reject('duplicate operand_id')

    def test_default_and_explicit_fail_stop_are_equivalent(self):
        self.job['failure_behavior'] = {'policy':'FAIL_STOP'}
        self.consumer['failure_behavior'] = {'policy':'FAIL_STOP'}
        model.validate(self.program)
        self.consumer['failure_behavior']['policy'] = 'RETRY'
        self.reject('schema:')

    def test_cli_success_and_failure(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(model.main([str(FIXTURES / 'positive/minimal.json')]), 0)
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(model.main([str(FIXTURES / 'negative/unknown-field.json')]), 1)
        self.assertIn('canonical model check failed', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
