"""Isolated structural constraints, without claiming execution acceptance."""
import copy
import unittest

from jsonschema import Draft202012Validator
from trace_receipts import protected
from trace_schema import build_schema


class TraceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = build_schema()

    def valid(self, name, value):
        definitions = self.schema['$defs']
        return Draft202012Validator(dict(definitions[name], **{'$defs': definitions})).is_valid(value)

    def test_scope_path_requires_at_least_one_segment(self):
        self.assertFalse(self.valid('scope_path', []))
        path = [{'scope_kind': 'JOB', 'scope_id': 'job'}]
        self.assertTrue(self.valid('scope_path', path))
        endpoint = dict(endpoint_kind='DECLARED_EFFECT', owner_scope_path=path, endpoint_id='effect')
        self.assertTrue(self.valid('sequencing_endpoint', endpoint))
        endpoint['owner_scope_path'] = []
        self.assertFalse(self.valid('sequencing_endpoint', endpoint))

    def test_argument_references_are_exclusive_for_every_kind(self):
        references = ('input_id', 'generated_artifact_id', 'ir_hash', 'output_generated_artifact_id')
        kinds = {'INPUT': 'input_id', 'GENERATED_ARTIFACT_INPUT': 'generated_artifact_id',
                 'IR_INPUT': 'ir_hash', 'OUTPUT_GENERATED_ARTIFACT': 'output_generated_artifact_id',
                 'RESPONSE_FILE': 'input_id', 'LITERAL': None, 'SEPARATOR': None}
        for kind, required in kinds.items():
            argument = dict(argument_index=0, argument_kind=kind, argument_text='x')
            if required:
                self.assertFalse(self.valid('argument', argument))
                argument[required] = 'identity'
            self.assertTrue(self.valid('argument', argument))
            for reference in references:
                if reference != required:
                    with self.subTest(kind=kind, extra=reference):
                        self.assertFalse(self.valid('argument', dict(argument, **{reference: 'other'})))

    def test_unknown_requires_explicit_consistent_termination(self):
        attempt = protected('UNKNOWN')['effect_attempts'][0]
        attempt.pop('effect_end_sequence_index', None)
        for known, end, expected in ((None, False, False), (None, True, False),
                                     (False, False, True), (False, True, False),
                                     (True, False, False), (True, True, True)):
            candidate = copy.deepcopy(attempt)
            candidate.pop('termination_known', None)
            if known is not None:
                candidate['termination_known'] = known
            if end:
                candidate['effect_end_sequence_index'] = 25
            with self.subTest(known=known, end=end):
                self.assertEqual(self.valid('effect_attempt', candidate), expected)

    def test_definitive_states_forbid_termination_discriminator(self):
        for state in ('NOT_STARTED', 'COMPLETED', 'ABORTED_CLEAN', 'PARTIAL'):
            attempt = protected(state)['effect_attempts'][0]
            self.assertTrue(self.valid('effect_attempt', attempt))
            for known in (False, True):
                with self.subTest(state=state, known=known):
                    self.assertFalse(self.valid('effect_attempt', dict(attempt, termination_known=known)))
