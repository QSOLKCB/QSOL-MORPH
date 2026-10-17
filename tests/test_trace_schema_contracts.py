"""Conditional record-shape regressions; these do not authorize execution."""
import copy
import itertools
import unittest

from jsonschema import Draft202012Validator
from trace_receipts import attributed, build, protected
from trace_schema import build_schema


class TraceSchemaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = build_schema()
        Draft202012Validator.check_schema(cls.schema)

    def valid(self, name, value):
        definitions = self.schema['$defs']
        return Draft202012Validator(dict(definitions[name], **{'$defs': definitions})).is_valid(value)

    def check_triple(self, name, base, fields):
        for count in range(4):
            for members in itertools.combinations(fields, count):
                candidate = dict(base, **{field: field + '-identity' for field in members})
                with self.subTest(record=name, fields=members):
                    self.assertEqual(self.valid(name, candidate), count in (0, 3))

    def test_machinery_participant_and_setup_scope_are_exclusive(self):
        use = protected()['machinery_use_records'][0]
        self.assertTrue(self.valid('machinery_use_record', use))
        setup = {'scope_kind': 'RUN', 'scope_id': 'run'}
        self.assertFalse(self.valid('machinery_use_record', dict(use, initiating_scope_ref=setup)))
        empty = dict(use, execution_subject_refs=[])
        self.assertFalse(self.valid('machinery_use_record', empty))
        self.assertTrue(self.valid('machinery_use_record', dict(empty, initiating_scope_ref=setup)))

    def test_evidence_status_is_exclusive_to_evidence_classes(self):
        output = build()['outputs'][0]
        for semantic_class in self.schema['$defs']['semantic_class']['enum']:
            candidate = copy.deepcopy(output)
            candidate['semantic_class'] = semantic_class
            candidate['epistemic_class_binding_ids'] = [] if semantic_class == 'UNCLASSIFIED' else ['class']
            candidate.pop('evidence_status', None)
            evidence_bearing = semantic_class in ('TEST', 'VALIDATION', 'PROOF')
            with self.subTest(semantic_class=semantic_class):
                self.assertEqual(self.valid('output', candidate), not evidence_bearing)
                candidate['evidence_status'] = dict(evidence_class=semantic_class if evidence_bearing else 'TEST',
                    status='PASS', evidence_rule_id='rule', evidence_validation_id='validation')
                self.assertEqual(self.valid('output', candidate), evidence_bearing)

    def test_unavailable_tool_forbids_each_material_identity_field(self):
        tool = attributed()['external_tool_versions'][0]
        self.assertTrue(self.valid('external_tool', tool))
        tool['material_identity_status'] = 'UNAVAILABLE'
        fields = ('material_identity_kind', 'material_identity_value')
        for field in fields:
            tool.pop(field)
        self.assertTrue(self.valid('external_tool', tool))
        for count in (1, 2):
            for selected in itertools.combinations(fields, count):
                with self.subTest(fields=selected):
                    self.assertFalse(self.valid('external_tool', dict(tool, **{field: 'identity' for field in selected})))

    def test_clean_abort_cannot_claim_observable_outputs(self):
        attempt = protected('ABORTED_CLEAN')['effect_attempts'][0]
        self.assertTrue(self.valid('effect_attempt', attempt))
        self.assertFalse(self.valid('effect_attempt', dict(attempt, observable_output_ids=['output'])))
        for state in ('COMPLETED', 'PARTIAL'):
            candidate = dict(attempt, completion_state=state, observable_output_ids=['output'])
            self.assertTrue(self.valid('effect_attempt', candidate))

    def test_every_cache_class_requires_concrete_subject(self):
        base = attributed()['cache_reuse_records'][0]
        for classification in ('COLD_EXECUTION', 'VERIFIED_REUSE', 'UNVERIFIED_HIT'):
            candidate = dict(base, classification=classification)
            if classification == 'VERIFIED_REUSE':
                candidate.update(legality_rule_id='rule', verification_evidence_id='evidence')
            with self.subTest(classification=classification):
                self.assertTrue(self.valid('cache_reuse_record', candidate))
                self.assertFalse(self.valid('cache_reuse_record', dict(candidate, execution_subject_refs=[])))

    def test_transition_triple_co_present_for_every_boundary_family(self):
        scope = {'owner_scope_path': [{'scope_kind': 'JOB', 'scope_id': 'job'}]}
        first = dict(source_scope_ref=scope, core_scope_refs=[scope], source_card_ids=[], mapping_rule_id='rule')
        second = dict(core_scope_refs=[scope], vector_dataflow_scope_refs=[scope], source_card_ids=[], mapping_rule_id='rule')
        triple = ('transition_decision_id', 'transition_authorized_by', 'transition_evidence_id')
        # Test each boundary property, not merely the reused definition, so a
        # family accidentally wired to a weaker shape is also detected.
        for boundary, base in (('semantic_to_core', first), ('core_to_vector', second)):
            for family, shape in self.schema['$defs'][boundary]['properties'].items():
                item_ref = shape.get('items', {}).get('$ref', '')
                name = item_ref.rsplit('/', 1)[-1]
                if name not in ('first_scope_mapping', 'first_numeric_mapping', 'second_scope_mapping', 'second_numeric_mapping'):
                    continue
                with self.subTest(boundary=boundary, family=family):
                    self.check_triple(name, base, triple)

    def test_fallback_triple_co_present(self):
        decision = build()['backend_selection_decisions'][0]
        self.check_triple('backend_selection_decision', decision,
            ('predecessor_selection_decision_id', 'fallback_rule_id', 'fallback_evidence_id'))

    def test_optimized_artifact_requires_nonempty_record_inventory(self):
        artifact = dict(generated_artifact_id='artifact', artifact_kind='OBJECT', artifact_hash='hash',
            backend_unit_id='unit', backend_selection_scope_id='scope', backend_selection_decision_id='decision',
            direct_producer_toolchain_invocation_id='invocation', toolchain_invocation_chain_ids=['invocation'])
        self.assertTrue(self.valid('generated_artifact', artifact))
        optimized = dict(artifact, optimized_ir_hash='optimized')
        self.assertFalse(self.valid('generated_artifact', optimized))
        self.assertFalse(self.valid('generated_artifact', dict(optimized, optimization_record_ids=[])))
        self.assertTrue(self.valid('generated_artifact', dict(optimized, optimization_record_ids=['optimization'])))

    def test_failed_or_unavailable_evidence_cannot_claim_application(self):
        evidence = dict(validation_evidence_id='validation', rule_id='rule', subject_kind='OUTPUT',
            subject_id='output', evaluated_context_hash='context', verifier_identity='verifier',
            outcome='PASS', validation_sequence_index=1, evidence_hash='hash', evidence_content={})
        for outcome in ('PASS', 'FAIL', 'UNAVAILABLE'):
            candidate = dict(evidence, outcome=outcome)
            with self.subTest(outcome=outcome):
                self.assertTrue(self.valid('validation_evidence', candidate))
                self.assertEqual(self.valid('validation_evidence', dict(candidate, application_sequence_index=2)), outcome == 'PASS')


    def test_only_binding_refs_admit_contextual_representation_root(self):
        for name in ('source_binding_ref', 'lower_binding_ref', 'result_binding_ref'):
            binding = dict(owner_scope_path=[], binding_id='root-binding')
            if name == 'result_binding_ref':
                binding.update(representation_kind='QSOL_CORE', representation_identity='core')
            with self.subTest(record=name):
                self.assertTrue(self.valid(name, binding))
                del binding['owner_scope_path']
                self.assertFalse(self.valid(name, binding))
        self.assertFalse(self.valid('scope_path', []))
        self.assertFalse(self.valid('sequencing_endpoint', dict(
            owner_scope_path=[], endpoint_id='endpoint', endpoint_kind='CARD')))

    def test_result_split_is_not_confused_with_fusion(self):
        scope = [{'scope_kind': 'CARD', 'scope_id': 'card'}]
        source = dict(owner_scope_path=scope, binding_id='source')
        lower = dict(owner_scope_path=scope, binding_id='lower')
        mapping = dict(mapping_group_id='group', source_bindings=[source],
                       lower_bindings=[lower, dict(lower, binding_id='split')])
        self.assertTrue(self.valid('result_binding_map', mapping))
        mapping['source_bindings'].append(dict(source, binding_id='second-source'))
        self.assertFalse(self.valid('result_binding_map', mapping))
        self.assertTrue(self.valid('result_binding_map', dict(mapping, mapping_rule_id='rule')))

    def test_failed_execution_records_require_exact_failure_reference(self):
        trace = build()
        operation = dict(operation_execution_id='execution', operation_ref=dict(
            representation_kind='QSOL_CORE', representation_identity='core',
            owner_scope_path=[{'scope_kind': 'FUNCTION', 'scope_id': 'function'}], operation_id='op'),
            operation_kind='opaque', operation_status='SUCCESS', input_ids=[])
        cases = [('deck_execution', 'deck_status', trace['deck_executions'][0]),
                 ('card_execution', 'card_status', trace['card_executions'][0]),
                 ('operation_execution', 'operation_status', operation)]
        for name, status, base in cases:
            failed = dict(base, **{status: 'FAILED'})
            failed.pop('failure_record_id', None)
            with self.subTest(record=name):
                self.assertFalse(self.valid(name, failed))
                self.assertTrue(self.valid(name, dict(failed, failure_record_id='failure')))
            if name == 'deck_execution':
                continue
            skipped = dict(base, **{status: 'EXPLICIT_SKIP'})
            for members in ((), ('governing_skip_rule_id',), ('skip_verification_evidence_id',),
                            ('governing_skip_rule_id', 'skip_verification_evidence_id')):
                candidate = dict(skipped, **{field: 'identity' for field in members})
                with self.subTest(record=name, skip_fields=members):
                    self.assertEqual(self.valid(name, candidate), len(members) == 2)

    def test_execution_transition_authority_and_evidence_are_paired(self):
        governed = dict(representation_kind='SEMANTIC_IR', representation_identity='semantic',
                        owner_scope_path=[{'scope_kind': 'JOB', 'scope_id': 'job'}])
        cases = [('result_determinism_scope', dict(result_determinism_scope_id='determinism',
                    governed_scope_ref=governed, source_card_ids=[],
                    requested_result_determinism='STRICT', effective_result_determinism='NUMERIC')),
                 ('randomness_execution_scope', dict(randomness_scope_id='randomness',
                    governed_scope_ref=governed, source_card_ids=[],
                    requested_randomness_mode='SEEDED', effective_randomness_mode='NONE'))]
        fields = ('transition_authorized_by', 'transition_evidence_id')
        for name, base in cases:
            # Contract-value comparisons remain outside this raw shape check.
            for members in ((), (fields[0],), (fields[1],), fields):
                with self.subTest(record=name, fields=members):
                    candidate = dict(base, **{field: 'identity' for field in members})
                    self.assertEqual(self.valid(name, candidate), len(members) in (0, 2))

    def test_failure_transition_evidence_requires_authority(self):
        binding = build()['failure_behavior_bindings'][0]
        self.assertTrue(self.valid('failure_behavior_binding', binding))
        evidence = dict(binding, transition_evidence_id='evidence')
        self.assertFalse(self.valid('failure_behavior_binding', evidence))
        self.assertTrue(self.valid('failure_behavior_binding', dict(evidence, mapping_or_transition_rule_id='rule')))
        self.assertTrue(self.valid('failure_behavior_binding', dict(binding, mapping_or_transition_rule_id='representation-rule')))

    def test_semantic_subject_discriminator_requires_card(self):
        subject = build()['outputs'][0]['producer_execution_refs'][0]
        self.assertTrue(self.valid('execution_subject_ref', subject))
        for wrong in ('CORE_OPERATION', 'VECTOR_DATAFLOW_OPERATION'):
            with self.subTest(subject_kind=wrong):
                self.assertFalse(self.valid('execution_subject_ref', dict(subject, subject_kind=wrong)))
        lower = dict(subject, representation_kind='QSOL_CORE', subject_kind='CORE_OPERATION')
        self.assertTrue(self.valid('execution_subject_ref', lower))

    def test_semantic_effect_has_card_without_operation_identity(self):
        declaration = protected()['effect_requirements'][0]
        self.assertTrue(self.valid('effect_requirement', declaration))
        missing_card = dict(declaration)
        missing_card.pop('card_id')
        self.assertFalse(self.valid('effect_requirement', missing_card))
        self.assertFalse(self.valid('effect_requirement', dict(missing_card, operation_id='op')))
        self.assertFalse(self.valid('effect_requirement', dict(declaration, operation_id='op')))
        lower = dict(missing_card, representation_kind='QSOL_CORE', operation_id='op')
        self.assertTrue(self.valid('effect_requirement', lower))


    def test_classified_output_requires_class_binding(self):
        output = build()['outputs'][0]
        self.assertTrue(self.valid('output', output))
        self.assertFalse(self.valid('output', dict(output, epistemic_class_binding_ids=[])))

    def test_granted_authorizations_forbid_denied_capabilities(self):
        trace = protected()
        for name, ledger in (('effect_authorization_record', 'effect_authorization_records'),
                             ('machinery_authorization_record', 'machinery_authorization_records')):
            record = trace[ledger][0]
            with self.subTest(record=name):
                self.assertTrue(self.valid(name, record))
                self.assertFalse(self.valid(name, dict(record, denied_capabilities=['AUDIT'])))

    def test_semantic_effect_subject_requires_both_card_projections(self):
        trace = protected()
        attempt = trace['effect_attempts'][0]
        nonattempt = dict(effect_non_attempt_record_id='nonattempt', effect_requirement_ref=attempt['effect_requirement_ref'],
            execution_subject_ref=attempt['execution_subject_ref'], card_id=attempt['card_id'],
            card_execution_id=attempt['card_execution_id'], effect_kind=attempt['effect_kind'],
            non_attempt_reason='PRIOR_FAIL_STOP', governing_failure_record_id='failure')
        for name, base in (('effect_attempt', attempt), ('effect_authorization_record', trace['effect_authorization_records'][0]),
                           ('effect_non_attempt_record', nonattempt)):
            self.assertTrue(self.valid(name, base))
            for field in ('card_id', 'card_execution_id'):
                candidate = copy.deepcopy(base)
                candidate.pop(field)
                with self.subTest(record=name, missing=field):
                    self.assertFalse(self.valid(name, candidate))
            lower = copy.deepcopy(base)
            lower.pop('card_id'); lower.pop('card_execution_id')
            lower['execution_subject_ref'].update(representation_kind='QSOL_CORE', subject_kind='CORE_OPERATION')
            self.assertTrue(self.valid(name, lower))

    def test_semantic_participant_requires_nonempty_projection_arrays(self):
        trace = protected()
        for name, base, fields in (
            ('output', trace['outputs'][0], ('producer_card_ids', 'producer_card_execution_ids')),
            ('machinery_use_record', trace['machinery_use_records'][0], ('source_card_ids', 'card_execution_ids'))):
            self.assertTrue(self.valid(name, base))
            for field in fields:
                candidate = copy.deepcopy(base)
                candidate.pop(field)
                with self.subTest(record=name, field=field):
                    self.assertFalse(self.valid(name, candidate))
                    candidate[field] = []
                    self.assertFalse(self.valid(name, candidate))

    def test_nonreach_discriminators_and_skip_dependencies(self):
        card = build()['card_executions'][0]
        operation = dict(operation_execution_id='execution', operation_ref=dict(
            representation_kind='QSOL_CORE', representation_identity='core',
            owner_scope_path=[{'scope_kind': 'FUNCTION', 'scope_id': 'function'}], operation_id='op'),
            operation_kind='opaque', operation_status='SUCCESS', input_ids=[])
        attempt = protected()['effect_attempts'][0]
        nonattempt = dict(effect_non_attempt_record_id='nonattempt', effect_requirement_ref=attempt['effect_requirement_ref'],
            execution_subject_ref=attempt['execution_subject_ref'], card_id=attempt['card_id'],
            card_execution_id=attempt['card_execution_id'], effect_kind=attempt['effect_kind'], non_attempt_reason='NOT_REACHED')
        for name, status_field, base in (('card_execution', 'card_status', card),
                                        ('operation_execution', 'operation_status', operation),
                                        ('effect_non_attempt_record', 'non_attempt_reason', nonattempt)):
            for status, required in (('UNTAKEN_BRANCH', 'governing_control_decision_id'),
                    ('PRIOR_FAIL_STOP' if name == 'effect_non_attempt_record' else 'FAIL_STOP_BLOCKED', 'governing_failure_record_id')):
                candidate = dict(base, **{status_field: status})
                with self.subTest(record=name, status=status):
                    self.assertFalse(self.valid(name, candidate))
                    self.assertTrue(self.valid(name, dict(candidate, **{required: 'cause'})))
            for single in ('governing_skip_rule_id', 'skip_verification_evidence_id'):
                candidate = dict(base, **{status_field: 'NOT_REACHED', single: 'identity'})
                self.assertFalse(self.valid(name, candidate))
            skipped = dict(base, **{status_field: 'EXPLICIT_SKIP'})
            self.assertFalse(self.valid(name, skipped))
            self.assertTrue(self.valid(name, dict(skipped, governing_skip_rule_id='rule', skip_verification_evidence_id='evidence')))

    def test_failure_scope_discriminators_require_concrete_culprit(self):
        base = dict(failure_record_id='failure', failing_scope_kind='JOB', failing_scope_id='job',
            failure_behavior_binding_ids=[], result_determinism_scope_ids=[], numeric_scope_ids=[],
            randomness_scope_ids=[], failure_class='failure', failure_stage='stage')
        for scope, fields in (('CARD_EXECUTION', ('failure_card_id', 'failure_card_execution_id')),
                              ('CORE_OPERATION_EXECUTION', ('operation_execution_id',))):
            candidate = dict(base, failing_scope_kind=scope)
            self.assertFalse(self.valid('failure_record', candidate))
            complete = dict(candidate, **{field: 'identity' for field in fields})
            self.assertTrue(self.valid('failure_record', complete))
            for field in fields:
                missing = dict(complete)
                missing.pop(field)
                self.assertFalse(self.valid('failure_record', missing))


if __name__ == '__main__':
    unittest.main()
