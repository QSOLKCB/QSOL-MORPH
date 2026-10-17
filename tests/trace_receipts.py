"""Deterministic synthetic receipt builders. These assert no actual execution."""
import copy
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_trace as trace
import serialization


def model(repeated=False, scoped=False, protected=False):
    m = json.loads((ROOT / 'tests/fixtures/model/positive/minimal.json').read_text())
    j = m['jobs'][0]
    if repeated:
        d = copy.deepcopy(j['decks'][0]); d['id'] = 'second'
        j['decks'].append(d)
    if scoped:
        example = json.loads((ROOT / 'tests/fixtures/model/positive/scoped-contracts.json').read_text())['jobs'][0]
        for node in [j, j['decks'][-1], j['decks'][-1]['cards'][0]]:
            node['numeric_contract'] = copy.deepcopy(example['numeric_contract'])
            node['randomness_contract'] = copy.deepcopy(example['randomness_contract'])
            node['result_determinism'] = 'NUMERIC'
            node['failure_behavior'] = {'policy': 'FAIL_STOP'}
    if protected:
        j['machinery_requirements'] = [{'machinery_requirement_id': 'device', 'target_selector_or_class': 'GPU', 'required_capabilities': ['DEVICE', 'GPU']}]
        for d in j['decks']:
            d['cards'][0]['effect_requirements'] = [{'effect_id': 'read', 'effect_kind': 'READ_FILE', 'required_capabilities': ['AUDIT', 'FILESYSTEM_READ']}]
    if repeated:
        predecessor = dict(owner_scope_path=[dict(scope_kind='JOB', scope_id='study'), dict(scope_kind='DECK', scope_id='baseline'), dict(scope_kind='CARD', scope_id='value')], producer_card_id='value')
        kinds = ['SOURCE_ORDER', 'FAILURE_ORDER'] + (['EFFECT_ORDER'] if protected else [])
        j['decks'][1]['cards'][0]['sequencing_constraints'] = [dict(constraint_id=k.lower(), kind=k, predecessor_ref=copy.deepcopy(predecessor)) for k in sorted(kinds)]
    return m


def build(source=None):
    source = copy.deepcopy(source if source is not None else model())
    schema = json.loads(trace.SCHEMA.read_text())
    t = {k: [] for k, v in schema['properties'].items() if v.get('type') == 'array' and k in schema['required']}
    identity = serialization.fingerprint(source)
    j = source['jobs'][0]
    t.update(trace_version='1.0.0', receipt_kind='SYNTHETIC_CONFORMANCE_RECEIPT', run_id='synthetic-run',
             input_representation='SEMANTIC_IR', semantic_ir_hash=identity, input_representation_identity=identity, execution_status='SUCCESS',
             capability_policy_id='synthetic-policy', capability_policy_version='1', event_order_domain='RUN_SEQUENCE', job_id=j['id'], job_status='SUCCESS')
    t['deck_executions'] = []; t['card_executions'] = []
    t['representation_records'] = [dict(representation_kind='SEMANTIC_IR', representation_identity=identity,
                                        format='QSOL-MORPH-MODEL-1.0.0', content=source)]
    def ref(path):
        return dict(representation_kind='SEMANTIC_IR', representation_identity=identity, owner_scope_path=copy.deepcopy(path))
    jp = [dict(scope_kind='JOB', scope_id=j['id'])]
    nodes = [(j, jp)]
    cards = []
    for di, d in enumerate(j['decks']):
        dp = jp + [dict(scope_kind='DECK', scope_id=d['id'])]; nodes.append((d, dp))
        de = dict(deck_execution_id=f'deck-{di}', deck_id=d['id'], deck_status='SUCCESS', card_execution_ids=[], execution_order_index=10 + di * 100)
        t['deck_executions'].append(de)
        for ci, c in enumerate(d['cards']):
            cp = dp + [dict(scope_kind='CARD', scope_id=c['id'])]; nodes.append((c, cp))
            ce = dict(card_execution_id=f'card-{di}-{ci}', deck_execution_id=de['deck_execution_id'], card_id=c['id'], card_status='SUCCESS', input_ids=[], execution_order_index=20 + di * 100 + ci * 10)
            t['card_executions'].append(ce); de['card_execution_ids'].append(ce['card_execution_id'])
            cards.append((c, cp, ce))
    def descendants(path):
        return sorted({c['id'] for c,p,_ in cards if p[:len(path)] == path})
    for ni, (node, path) in enumerate(nodes):
        common = dict(governed_scope_ref=ref(path), source_card_ids=descendants(path))
        if 'result_determinism' in node:
            t['result_determinism_scopes'].append(dict(common, result_determinism_scope_id=f'determinism-{ni}', requested_result_determinism=node['result_determinism'], effective_result_determinism=node['result_determinism']))
        if 'numeric_contract' in node:
            n = node['numeric_contract']
            t['numeric_execution_scopes'].append(dict(common, numeric_scope_id=f'numeric-{ni}', numeric_contract_id=n['contract_id'], numeric_contract_hash=n['definition_hash'], material_numeric_mode=copy.deepcopy(n)))
        if 'randomness_contract' in node:
            n = node['randomness_contract']
            t['randomness_execution_scopes'].append(dict(common, randomness_scope_id=f'randomness-{ni}', requested_randomness_mode=n['mode'], effective_randomness_mode=n['mode'], **{k: v for k,v in n.items() if k != 'mode'}))
        if len(path) == 1 or 'failure_behavior' in node:
            t['failure_behavior_bindings'].append(dict(common, failure_behavior_binding_id=f'failure-{ni}', requested_failure_behavior_id=trace.FAIL_STOP, effective_failure_behavior_id=trace.FAIL_STOP))
        for r in node['machinery_requirements']:
            t['machinery_requirements'].append(dict(ref(path), **r, source_card_ids=descendants(path)))
    t['backend_selection_scopes'] = [dict(backend_selection_scope_id='backend-scope', governed_scope_ref=ref(jp), source_card_ids=descendants(jp), selection_decision_ids=['selection'], final_selection_decision_id='selection')]
    t['backend_selection_decisions'] = [dict(backend_selection_decision_id='selection', backend_selection_scope_id='backend-scope', decision_sequence_index=0, requested_target='SYNTHETIC', selected_backend='SYNTHETIC', selected_backend_version='1', selected_backend_implementation_identity='sha256:' + 'a'*64, decision_status='FINAL_EXECUTABLE', machinery_authorization_record_ids=[])]
    for i, (c, path, ce) in enumerate(cards):
        subject = dict(ref(path), subject_kind='CARD', subject_id=c['id'], execution_id=ce['card_execution_id'])
        class_ids = []
        if c['semantic_class'] != 'UNCLASSIFIED':
            class_ids = [f'class-{i}']
            t['epistemic_class_bindings'].append(dict(ref(path), epistemic_class_binding_id=class_ids[0], subject_kind='CARD', subject_id=c['id'], semantic_class=c['semantic_class']))
        for effect in c['effect_requirements']:
            t['effect_requirements'].append(dict(ref(path), declared_effect_id=effect['effect_id'], card_id=c['id'], effect_kind=effect['effect_kind'], required_capabilities=effect['required_capabilities']))
        for bi, binding in enumerate(c['result_bindings']):
            out = dict(output_id=f'output-{i}-{bi}', result_binding_ref=dict(ref(path), binding_id=binding['result_binding_id']), artifact_hash='sha256:' + 'b'*64, semantic_class=binding['semantic_class'], epistemic_class_binding_ids=class_ids, status='COMPLETE', producer_execution_refs=[subject], producer_card_ids=[c['id']], producer_card_execution_ids=[ce['card_execution_id']], input_ids=[], effect_attempt_ids=[], external_tool_ids=[], backend_selection_scope_ids=['backend-scope'], machinery_use_record_ids=[], generated_artifact_ids=[], cache_reuse_record_ids=[], publication_sequence_index=ce['execution_order_index']+70+bi)
            for ledger,(idfield,outfield) in trace.FAMILIES.items():
                out[outfield] = [r[idfield] for r in t[ledger] if path[:len(r['governed_scope_ref']['owner_scope_path'])] == r['governed_scope_ref']['owner_scope_path']]
            t['outputs'].append(out)
    return t


def fail(t, card_index=0):
    """Record one synthetic fail-stop event and block subsequent CARDs."""
    t = copy.deepcopy(t); c = t['card_executions'][card_index]
    t.update(execution_status='FAILED', job_status='FAILED', primary_failure_record_id='failed')
    f = dict(failure_record_id='failed', failing_scope_kind='CARD_EXECUTION', failing_scope_id=c['card_execution_id'], failure_card_id=c['card_id'], failure_card_execution_id=c['card_execution_id'], deck_execution_id=c['deck_execution_id'], failure_class='SYNTHETIC_FAILURE', failure_stage='CARD', sequence_index=c['execution_order_index']+80, effect_accounting_failure_record_ids=[])
    output = next(o for o in t['outputs'] if o['producer_card_execution_ids'] == [c['card_execution_id']])
    for _,(_,field) in trace.FAMILIES.items(): f[field] = output[field]
    t['failure_records'] = [f]
    c.update(card_status='FAILED', failure_record_id='failed')
    for later in t['card_executions'][card_index+1:]:
        later.update(card_status='BLOCKED', governing_failure_record_id='failed'); later.pop('execution_order_index')
    for d in t['deck_executions']:
        members = [x for x in t['card_executions'] if x['deck_execution_id'] == d['deck_execution_id']]
        if any(x['card_status']=='FAILED' for x in members): d.update(deck_status='FAILED', failure_record_id='failed')
        elif all(x['card_status']=='BLOCKED' for x in members):
            d.update(deck_status='BLOCKED', governing_failure_record_id='failed'); d.pop('execution_order_index')
    valid = {x['card_execution_id'] for x in t['card_executions'] if x['card_status']=='SUCCESS'}
    t['outputs'] = [o for o in t['outputs'] if set(o['producer_card_execution_ids']) <= valid]
    return t


def protected(state='COMPLETED', accounting=False):
    t = build(model(repeated=True, protected=True))
    if state != 'COMPLETED' or accounting:
        t = fail(t)
    t.update(capability_policy_id='synthetic-policy', capability_policy_version='1')
    decision = t['backend_selection_decisions'][0]
    decision.update(requested_target='GPU', selected_backend='GPU', machinery_authorization_record_ids=['machine-grant'])
    mr = {k:v for k,v in t['machinery_requirements'][0].items() if k in ('representation_kind','representation_identity','owner_scope_path','machinery_requirement_id')}
    t['machinery_authorization_records'] = [dict(machinery_authorization_record_id='machine-grant', backend_selection_scope_id='backend-scope', backend_selection_decision_id='selection', source_card_ids=['value'], machinery_requirement_refs=[mr], required_capabilities=['DEVICE','GPU'], granted_capabilities=['DEVICE','GPU'], denied_capabilities=[], capability_policy_id='synthetic-policy', capability_policy_version='1', authorization_status='GRANTED', authorization_sequence_index=1)]
    for i, c in enumerate(t['card_executions']):
        declaration = t['effect_requirements'][i]
        er = {k:v for k,v in declaration.items() if k in ('representation_kind','representation_identity','owner_scope_path','declared_effect_id')}
        subject = {k:v for k,v in er.items() if k != 'declared_effect_id'}
        subject.update(subject_kind='CARD',subject_id=c['card_id'],execution_id=c['card_execution_id'])
        base = dict(effect_requirement_ref=er,execution_subject_ref=subject,card_id=c['card_id'],card_execution_id=c['card_execution_id'])
        if c['card_status']=='BLOCKED':
            t['effect_non_attempt_records'].append(dict(base,effect_non_attempt_record_id=f'non-{i}',effect_kind='READ_FILE',non_attempt_reason='PRIOR_FAIL_STOP',governing_failure_record_id='failed'))
            continue
        start = c['execution_order_index']
        outids = [o['output_id'] for o in t['outputs'] if o['producer_card_execution_ids']==[c['card_execution_id']]]
        t['machinery_use_records'].append(dict(machinery_use_record_id=f'use-{i}',backend_selection_scope_id='backend-scope',backend_selection_decision_id='selection',generated_artifact_ids=[],execution_subject_refs=[subject],source_card_ids=[c['card_id']],card_execution_ids=[c['card_execution_id']],machinery_authorization_record_ids=['machine-grant'],output_ids=outids,protected_use_start_sequence_index=start+1,protected_use_stop_sequence_index=start+60))
        for o in t['outputs']:
            if o['output_id'] in outids: o['machinery_use_record_ids']=[f'use-{i}']
        if accounting:
            t['effect_accounting_failure_records'].append(dict(effect_accounting_failure_record_id='accounting',failure_record_id='failed',effect_requirement_ref=er,execution_subject_ref=subject,accounting_failure_kind='ACCOUNTING_INCOMPLETE',detected_sequence_index=start+40))
            t['failure_records'][0]['effect_accounting_failure_record_ids']=['accounting']
            continue
        denied = state=='NOT_STARTED'
        t['effect_authorization_records'].append(dict(base,effect_authorization_record_id=f'auth-{i}',effect_attempt_id=f'attempt-{i}',required_capabilities=['AUDIT','FILESYSTEM_READ'],granted_capabilities=[] if denied else ['AUDIT','FILESYSTEM_READ'],denied_capabilities=['AUDIT','FILESYSTEM_READ'] if denied else [],capability_policy_id='synthetic-policy',capability_policy_version='1',authorization_status='DENIED' if denied else 'GRANTED',authorization_sequence_index=start+2))
        attempt = dict(base,effect_attempt_id=f'attempt-{i}',effect_kind='READ_FILE',required_capabilities=['AUDIT','FILESYSTEM_READ'],effect_authorization_record_id=f'auth-{i}',sequence_index=start+3,completion_state=state,acquired_input_ids=[],observable_output_ids=[],external_tool_ids=[])
        if state!='NOT_STARTED':
            attempt['effect_begin_sequence_index']=start+4
            if state=='UNKNOWN': attempt['termination_known']=False
            else: attempt['effect_end_sequence_index']=start+5
        t['effect_attempts'].append(attempt)
    return t


def attributed():
    """Synthetic input, cold-cache and material-tool reciprocal participation."""
    t = protected()
    c=t['card_executions'][0]; o=t['outputs'][0]; a=t['effect_attempts'][0]
    ref=copy.deepcopy(a['execution_subject_ref'])
    value={'type':'TEXT','unit':'1','value':'synthetic public fixture'}
    t['inputs']=[dict(input_id='input',input_kind='SYNTHETIC_VALUE',canonical_value=value,content_hash=trace.content_hash(value),consumer_execution_refs=[ref],consumer_card_execution_ids=[c['card_execution_id']],source_card_ids=[c['card_id']],effect_attempt_ids=[a['effect_attempt_id']])]
    c['input_ids']=['input'];o['input_ids']=['input'];a['acquired_input_ids']=['input']
    t['cache_reuse_records']=[dict(cache_reuse_record_id='cold',classification='COLD_EXECUTION',execution_subject_refs=[ref],source_card_ids=[c['card_id']],card_execution_ids=[c['card_execution_id']],material_cache_identity_hash=trace.content_hash('synthetic cache identity'))]
    c['cache_reuse_record_ids']=['cold'];o['cache_reuse_record_ids']=['cold']
    t['external_tool_versions']=[dict(external_tool_id='tool',tool_kind='SYNTHETIC',tool_name_or_service='fixture-tool',material_identity_status='IDENTIFIED',material_identity_kind='CONTENT_HASH',material_identity_value=trace.content_hash('synthetic tool identity'),effect_attempt_ids=[a['effect_attempt_id']],output_ids=[o['output_id']],source_card_ids=[c['card_id']])]
    a['external_tool_ids']=['tool'];o['external_tool_ids']=['tool']
    return t


def retained_partial():
    t=protected('PARTIAL')
    o=copy.deepcopy(protected()['outputs'][0])
    o['status']='PARTIAL';o['effect_attempt_ids']=['attempt-0']
    t['outputs']=[o]
    t['effect_attempts'][0]['observable_output_ids']=[o['output_id']]
    t['machinery_use_records'][0]['output_ids']=[o['output_id']]
    return t


def multiple_bindings():
    m=model();c=m['jobs'][0]['decks'][0]['cards'][0]
    b=copy.deepcopy(c['result_bindings'][0]);b['result_binding_id']='mass2';c['result_bindings'].append(b)
    return build(m)
