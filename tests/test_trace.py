"""Source-bound synthetic conformance tests, never runtime/research evidence."""
import copy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from trace_receipts import ROOT, build, model, protected, fail, trace, attributed, retained_partial, multiple_bindings

FIXTURES = ROOT / 'tests/fixtures/trace'


@lru_cache(maxsize=1)
def positives():
    return {
        'minimal': build(),
        'retained-partial-effect': retained_partial(),
        'multiple-result-bindings': multiple_bindings(),
        'attributed-input-cache-tool': attributed(),
        'reused-local-identities': build(model(repeated=True)),
        'scoped-contracts': build(model(repeated=True, scoped=True)),
        'fail-stop': fail(build(model(repeated=True))),
        'protected-completed': protected(),
        'protected-unknown': protected('UNKNOWN'),
        'protected-not-started': protected('NOT_STARTED'),
        'accounting-failure': protected(accounting=True),
    }


def assign(t, path, value):
    parent = t
    for part in path[:-1]: parent = parent[part]
    if value is DELETE: del parent[path[-1]]
    else: parent[path[-1]] = copy.deepcopy(value)


DELETE = object()
# Each case changes one concrete, source-bound fact unless it deliberately
# narrows a reciprocal closure. The unchanged positive is validated first.
MUTATIONS = [
 ('source-identity', 'minimal', ['input_representation_identity'], 'sha256:'+'c'*64),
 ('semantic-hash', 'minimal', ['semantic_ir_hash'], 'sha256:'+'c'*64),
 ('source-content', 'minimal', ['representation_records',0,'content','jobs',0,'decks',0,'cards',0,'value','value'], '5.2'),
 ('runtime-claim', 'minimal', ['receipt_kind'], 'EXECUTION_TRACE'),
 ('foreign-entry', 'minimal', ['input_representation'], 'QSOL_CORE'),
 ('missing-representation', 'minimal', ['representation_records'], []),
 ('missing-decks', 'minimal', ['deck_executions'], []),
 ('missing-cards', 'minimal', ['card_executions'], []),
 ('missing-outputs', 'minimal', ['outputs'], []),
 ('missing-class-bindings', 'minimal', ['epistemic_class_bindings'], []),
 ('wrong-job', 'minimal', ['job_id'], 'other'),
 ('wrong-job-status', 'minimal', ['job_status'], 'FAILED'),
 ('wrong-run-status', 'minimal', ['execution_status'], 'FAILED'),
 ('unknown-envelope-field', 'minimal', ['trust_me'], True),
 ('unsupported-lowering', 'minimal', ['lowering_provenance'], [{'claim':'self-attested'}]),
 ('wrong-deck', 'minimal', ['deck_executions',0,'deck_id'], 'other'),
 ('wrong-card', 'minimal', ['card_executions',0,'card_id'], 'other'),
 ('wrong-card-owner', 'minimal', ['card_executions',0,'deck_execution_id'], 'other'),
 ('orphan-card-member', 'minimal', ['deck_executions',0,'card_execution_ids'], []),
 ('card-before-deck', 'minimal', ['card_executions',0,'execution_order_index'], 9),
 ('duplicate-event', 'minimal', ['card_executions',0,'execution_order_index'], 10),
 ('boolean-event', 'minimal', ['card_executions',0,'execution_order_index'], True),
 ('negative-event', 'minimal', ['card_executions',0,'execution_order_index'], -1),
 ('no-event', 'minimal', ['card_executions',0,'execution_order_index'], DELETE),
 ('unproven-skip', 'minimal', ['card_executions',0,'card_status'], 'EXPLICIT_SKIP'),
 ('cause-free-block', 'minimal', ['card_executions',0,'card_status'], 'BLOCKED'),
 ('class-declassification', 'minimal', ['outputs',0,'semantic_class'], 'UNCLASSIFIED'),
 ('source-class-drift', 'minimal', ['epistemic_class_bindings',0,'semantic_class'], 'UNCLASSIFIED'),
 ('missing-output-binding', 'minimal', ['outputs',0,'result_binding_ref'], DELETE),
 ('wrong-output-binding', 'minimal', ['outputs',0,'result_binding_ref','binding_id'], 'other'),
 ('missing-output-class', 'minimal', ['outputs',0,'epistemic_class_binding_ids'], []),
 ('wrong-output-status', 'minimal', ['outputs',0,'status'], 'PARTIAL'),
 ('unhashed-output', 'minimal', ['outputs',0,'artifact_hash'], 'trust-me'),
 ('early-output', 'minimal', ['outputs',0,'publication_sequence_index'], 19),
 ('wrong-output-subject', 'minimal', ['outputs',0,'producer_execution_refs',0,'execution_id'], 'other'),
 ('wrong-output-projection', 'minimal', ['outputs',0,'producer_card_execution_ids'], []),
 ('wrong-output-owner', 'reused-local-identities', ['outputs',0,'producer_execution_refs',0,'owner_scope_path',1,'scope_id'], 'second'),
 ('publication-crosses-card', 'reused-local-identities', ['outputs',0,'publication_sequence_index'], 121),
 ('selection-omitted', 'minimal', ['backend_selection_scopes'], []),
 ('selection-no-final', 'minimal', ['backend_selection_scopes',0,'final_selection_decision_id'], DELETE),
 ('selection-wrong-final', 'minimal', ['backend_selection_scopes',0,'final_selection_decision_id'], 'other'),
 ('selection-target-substitution', 'minimal', ['backend_selection_decisions',0,'requested_target'], 'GPU'),
 ('selection-no-identity', 'minimal', ['backend_selection_decisions',0,'selected_backend_implementation_identity'], DELETE),
 ('selection-unhashed-identity', 'minimal', ['backend_selection_decisions',0,'selected_backend_implementation_identity'], 'version-only'),
 ('selection-after-card', 'minimal', ['backend_selection_decisions',0,'decision_sequence_index'], 21),
 ('selection-denied', 'minimal', ['backend_selection_decisions',0,'decision_status'], 'DENIED'),
 ('fabricated-fallback', 'minimal', ['backend_selection_decisions',0,'fallback_rule_id'], 'self-asserted-rule'),
 ('fail-stop-later-success', 'fail-stop', ['card_executions',1,'card_status'], 'SUCCESS'),
 ('fail-stop-wrong-cause', 'fail-stop', ['card_executions',1,'governing_failure_record_id'], 'other'),
 ('failure-lost', 'fail-stop', ['failure_records'], []),
 ('failure-before-card', 'fail-stop', ['failure_records',0,'sequence_index'], 19),
 ('failure-wrong-card', 'fail-stop', ['failure_records',0,'failure_card_execution_id'], 'card-1-0'),
 ('failure-wrong-primary', 'fail-stop', ['primary_failure_record_id'], 'other'),
 ('effect-declarations-narrowed', 'protected-completed', ['effect_requirements'], []),
 ('machinery-declarations-narrowed', 'protected-completed', ['machinery_requirements'], []),
 ('effect-attempts-omitted', 'protected-completed', ['effect_attempts'], []),
 ('machinery-use-omitted', 'protected-completed', ['machinery_use_records'], []),
 ('effect-caps-narrowed', 'protected-completed', ['effect_attempts',0,'required_capabilities'], ['FILESYSTEM_READ']),
 ('effect-grant-narrowed', 'protected-completed', ['effect_authorization_records',0,'granted_capabilities'], ['FILESYSTEM_READ']),
 ('effect-required-narrowed', 'protected-completed', ['effect_authorization_records',0,'required_capabilities'], ['FILESYSTEM_READ']),
 ('effect-wrong-owner', 'protected-completed', ['effect_attempts',0,'effect_requirement_ref','owner_scope_path',1,'scope_id'], 'second'),
 ('effect-wrong-invocation', 'protected-completed', ['effect_attempts',0,'execution_subject_ref','execution_id'], 'card-1-0'),
 ('effect-auth-late', 'protected-completed', ['effect_authorization_records',0,'authorization_sequence_index'], 29),
 ('effect-end-before-start', 'protected-completed', ['effect_attempts',0,'effect_end_sequence_index'], 23),
 ('effect-unknown-success', 'protected-completed', ['effect_attempts',0,'completion_state'], 'UNKNOWN'),
 ('effect-not-started-boundaries', 'protected-completed', ['effect_attempts',0,'completion_state'], 'NOT_STARTED'),
 ('unknown-missing-termination', 'protected-unknown', ['effect_attempts',0,'termination_known'], DELETE),
 ('unknown-false-termination', 'protected-unknown', ['effect_attempts',0,'effect_end_sequence_index'], 25),
 ('unknown-true-no-end', 'protected-unknown', ['effect_attempts',0,'termination_known'], True),
 ('non-attempt-wrong-cause', 'protected-unknown', ['effect_non_attempt_records',0,'governing_failure_record_id'], 'other'),
 ('non-attempt-invented-rule', 'protected-unknown', ['effect_non_attempt_records',0,'non_attempt_reason'], 'TRUST_MY_SKIP'),
 ('accounting-omitted', 'accounting-failure', ['effect_accounting_failure_records'], []),
 ('accounting-late', 'accounting-failure', ['effect_accounting_failure_records',0,'detected_sequence_index'], 101),
 ('accounting-missing-backlink', 'accounting-failure', ['failure_records',0,'effect_accounting_failure_record_ids'], []),
 ('machinery-caps-narrowed', 'protected-completed', ['machinery_authorization_records',0,'required_capabilities'], ['GPU']),
 ('machinery-grant-narrowed', 'protected-completed', ['machinery_authorization_records',0,'granted_capabilities'], ['GPU']),
 ('machinery-auth-late', 'protected-completed', ['machinery_authorization_records',0,'authorization_sequence_index'], 29),
 ('machinery-non-final-use', 'protected-completed', ['machinery_use_records',0,'backend_selection_decision_id'], 'other'),
 ('machinery-missing-stop', 'protected-completed', ['machinery_use_records',0,'protected_use_stop_sequence_index'], DELETE),
 ('machinery-empty-runtime-subject', 'protected-completed', ['machinery_use_records',0,'execution_subject_refs'], []),
 ('machinery-wrong-output', 'protected-completed', ['machinery_use_records',0,'output_ids'], ['output-1-0']),
]
MUTATIONS.extend([
 ('not-started-auth-after-failure','protected-not-started',['effect_authorization_records',0,'authorization_sequence_index'],999),
 ('second-deck-start-before-first','reused-local-identities',['deck_executions',1,'execution_order_index'],2),
 ('publication-crosses-next-deck','reused-local-identities',['outputs',0,'publication_sequence_index'],111),
 ('partial-artifact-promoted','retained-partial-effect',['outputs',0,'status'],'COMPLETE'),
 ('partial-observable-reciprocity-lost','retained-partial-effect',['effect_attempts',0,'observable_output_ids'],[]),
 ('partial-publication-before-effect-end','retained-partial-effect',['outputs',0,'publication_sequence_index'],24),
 ('multiple-binding-duplicate','multiple-result-bindings',['outputs',1,'result_binding_ref','binding_id'],'mass'),
 ('input-hash-mismatch','attributed-input-cache-tool',['inputs',0,'content_hash'],'sha256:'+'c'*64),
 ('input-wrong-invocation','attributed-input-cache-tool',['inputs',0,'consumer_execution_refs',0,'execution_id'],'card-1-0'),
 ('input-acquisition-missing','attributed-input-cache-tool',['effect_attempts',0,'acquired_input_ids'],[]),
 ('input-materiality-narrowed','attributed-input-cache-tool',['outputs',0,'input_ids'],[]),
 ('input-consumer-missing','attributed-input-cache-tool',['card_executions',0,'input_ids'],[]),
 ('cache-reuse-claims-authority','attributed-input-cache-tool',['cache_reuse_records',0,'classification'],'UNVERIFIED_HIT'),
 ('cache-wrong-invocation','attributed-input-cache-tool',['cache_reuse_records',0,'execution_subject_refs',0,'execution_id'],'card-1-0'),
 ('cache-output-relation-missing','attributed-input-cache-tool',['outputs',0,'cache_reuse_record_ids'],[]),
 ('tool-version-is-not-identity','attributed-input-cache-tool',['external_tool_versions',0,'material_identity_value'],'v1'),
 ('tool-attempt-relation-missing','attributed-input-cache-tool',['effect_attempts',0,'external_tool_ids'],[]),
 ('tool-output-relation-missing','attributed-input-cache-tool',['outputs',0,'external_tool_ids'],[]),
])
for ledger, (_, field) in trace.FAMILIES.items():
    MUTATIONS.extend([
        (ledger+'-omitted','scoped-contracts',[ledger],[]),
        (field+'-omitted','scoped-contracts',['outputs',1,field],[]),
        (ledger+'-wrong-owner','scoped-contracts',[ledger,0,'governed_scope_ref','owner_scope_path',0,'scope_id'],'other'),
    ])


class TraceTests(unittest.TestCase):
    def test_job_preflight_failure_has_no_fabricated_card_culprit(self):
        t = fail(build(model(repeated=True)))
        failure = t['failure_records'][0]
        failure.update(failing_scope_kind='JOB', failing_scope_id=t['job_id'], failure_stage='JOB_PREFLIGHT')
        for field in ('failure_card_id', 'failure_card_execution_id', 'deck_execution_id'):
            failure.pop(field, None)
        for card in t['card_executions']:
            card.update(card_status='BLOCKED', governing_failure_record_id='failed', input_ids=[])
            card.pop('failure_record_id', None)
            card.pop('execution_order_index', None)
        for deck in t['deck_executions']:
            deck.update(deck_status='BLOCKED', governing_failure_record_id='failed')
            deck.pop('failure_record_id', None)
            deck.pop('execution_order_index', None)
        t['outputs'] = []
        t['backend_selection_scopes'] = []
        t['backend_selection_decisions'] = []
        trace.validate(t)
        failure['failure_stage'] = 'CARD'
        with self.assertRaisesRegex(trace.Invalid, 'JOB_PREFLIGHT stage'):
            trace.validate(t)
        failure['failure_stage'] = 'JOB_PREFLIGHT'
        failure['failure_card_id'] = t['card_executions'][0]['card_id']
        with self.assertRaises(trace.Invalid):
            trace.validate(t)

    def test_material_input_acquisition_precedes_publication(self):
        for begin, end in ((94, 95), (24, 95), (24, 90)):
            with self.subTest(begin=begin, end=end):
                t = attributed()
                t['effect_attempts'][0].update(effect_begin_sequence_index=begin,
                                               effect_end_sequence_index=end)
                expected = 'output published before material input acquisition completed' if end > 90 else '.*'
                with self.assertRaisesRegex(trace.Invalid, expected):
                    trace.validate(t)
        t = attributed()
        t['effect_attempts'][0].update(effect_end_sequence_index=89)
        trace.validate(t)

    def test_card_failure_cannot_claim_job_preflight_stage(self):
        t = fail(build())
        t['failure_records'][0]['failure_stage'] = 'JOB_PREFLIGHT'
        with self.assertRaisesRegex(trace.Invalid, 'CARD stage'):
            trace.validate(t)

    def test_unknown_with_known_termination(self):
        t=protected('UNKNOWN')
        t['effect_attempts'][0].update(termination_known=True,effect_end_sequence_index=25)
        trace.validate(t)

    def test_clean_abort_without_observable_artifact(self):
        trace.validate(protected('ABORTED_CLEAN'))

    def test_unavailable_material_tool_identity_is_explicit(self):
        t=attributed();tool=t['external_tool_versions'][0]
        tool['material_identity_status']='UNAVAILABLE'
        del tool['material_identity_kind'];del tool['material_identity_value']
        trace.validate(t)

    def test_positive_receipts(self):
        for name,t in positives().items():
            with self.subTest(name=name): trace.validate(t)

    def test_coordinated_effect_narrowing_still_rejects_source(self):
        t=protected()
        for row in t['effect_requirements'] + t['effect_attempts'] + t['effect_authorization_records']:
            row['required_capabilities']=['FILESYSTEM_READ']
            if 'granted_capabilities' in row: row['granted_capabilities']=['FILESYSTEM_READ']
        with self.assertRaises(trace.Invalid): trace.validate(t)

    def test_coordinated_machinery_narrowing_still_rejects_source(self):
        t=protected()
        for row in t['machinery_requirements'] + t['machinery_authorization_records']:
            row['required_capabilities']=['GPU']
            if 'granted_capabilities' in row: row['granted_capabilities']=['GPU']
        with self.assertRaises(trace.Invalid): trace.validate(t)

    def test_one_of_multiple_named_bindings_cannot_disappear(self):
        t=multiple_bindings(); t['outputs'].pop()
        with self.assertRaises(trace.Invalid): trace.validate(t)

    def test_unclassified_cannot_launder_parameter_output(self):
        t=build(); t['epistemic_class_bindings']=[]
        t['outputs'][0].update(semantic_class='UNCLASSIFIED',epistemic_class_binding_ids=[])
        with self.assertRaises(trace.Invalid): trace.validate(t)

    def test_cli_batch_never_emits_partial_success(self):
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/'bad.json';bad.write_text('{}')
            r=subprocess.run([sys.executable,str(ROOT/'tools/check_trace.py'),str(FIXTURES/'positive/minimal.json'),str(bad)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,'')

    def test_validation_does_not_mutate_receipt(self):
        for t in positives().values():
            original=copy.deepcopy(t); trace.validate(t); self.assertEqual(t,original)

    def test_frozen_positive_receipts(self):
        for name,t in positives().items():
            frozen=trace.strict_load(FIXTURES/'positive'/f'{name}.json')
            self.assertEqual(frozen,t); trace.validate(frozen)

    def test_named_negative_fixtures(self):
        manifest=json.loads((FIXTURES/'manifest.json').read_text())
        for case in manifest['negative']:
            with self.subTest(case=case['name']), self.assertRaises(trace.Invalid):
                trace.validate(trace.strict_load(FIXTURES/'negative'/(case['name']+'.json')))

    def test_historical_contracts_unchanged(self):
        manifest=json.loads((FIXTURES/'manifest.json').read_text())
        for path,digest in manifest['historical_files'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)

    def test_non_json_python_payloads_rejected(self):
        cycle=[];cycle.append(cycle)
        for value in [float('nan'),float('inf'),float('-inf'),1.0,1.5,{1,2},b'bytes',(1,2),{1:'non-string key'},cycle]:
            t=attributed();t['inputs'][0].pop('content_hash')
            t['inputs'][0]['canonical_value']=value
            with self.subTest(type=type(value).__name__),self.assertRaises(trace.Invalid):trace.validate(t)

    def test_cli_overflow_number_rejected(self):
        t=attributed();t['inputs'][0].pop('content_hash');t['inputs'][0]['canonical_value']='OVERFLOW_SENTINEL'
        raw=json.dumps(t).replace('"OVERFLOW_SENTINEL"','1e99999999')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'overflow.json';p.write_text(raw)
            r=subprocess.run([sys.executable,str(ROOT/'tools/check_trace.py'),str(p)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,'')

    def test_exact_large_integer_json_payload(self):
        t=attributed();t['inputs'][0].pop('content_hash');t['inputs'][0]['canonical_value']='EXACT_SENTINEL'
        raw=json.dumps(t).replace('"EXACT_SENTINEL"','1e999')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'integer.json';p.write_text(raw)
            loaded=trace.strict_load(p)
            self.assertEqual(loaded['inputs'][0]['canonical_value'],10**999)
            trace.validate(loaded)

    def test_source_coordinate_cannot_alias_through_float_rounding(self):
        m=model();m['jobs'][0]['decks'][0]['cards'][0]['source_location']['end']['column']=9007199254740992
        t=build(m)
        raw=json.dumps(t).replace('9007199254740992','9007199254740993.0')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'alias.json';p.write_text(raw)
            with self.assertRaises(trace.Invalid):trace.validate(trace.strict_load(p))

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json'; p.write_text('{"trace_version":"1.0.0","trace_version":"1.0.0"}')
            with self.assertRaises(trace.Invalid): trace.strict_load(p)

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for literal in ['NaN','Infinity','-Infinity']:
                p=Path(d)/'bad.json'; p.write_text('{"value":'+literal+'}')
                with self.assertRaises(trace.Invalid): trace.strict_load(p)

    def test_cli_invalid_no_success_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json'; p.write_text('{}')
            r=subprocess.run([sys.executable,str(ROOT/'tools/check_trace.py'),str(p)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0); self.assertNotIn('OK',r.stdout); self.assertNotIn('VALID',r.stdout)

    def test_cli_positive(self):
        r=subprocess.run([sys.executable,str(ROOT/'tools/check_trace.py'),str(FIXTURES/'positive/minimal.json')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)


def make_test(case):
    def test(self):
        _,name,path,value=case
        t=copy.deepcopy(positives()[name]); trace.validate(t)
        assign(t,path,value)
        with self.assertRaises(trace.Invalid): trace.validate(t)
    return test
for case in MUTATIONS:
    setattr(TraceTests,'test_reject_'+case[0].replace('-','_'),make_test(case))

if __name__=='__main__': unittest.main()
