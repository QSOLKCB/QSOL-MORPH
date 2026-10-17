#!/usr/bin/env python3
"""Read-only source-bound synthetic receipt checks, NOT an execution gate.

No program, effect, tool, rule, verifier supplied by a receipt is executed.
See docs/EXECUTION-TRACE-FOUNDATION.md for the intentionally provisional boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator
try:
    from . import check_model, serialization
except ImportError:
    import check_model
    import serialization

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'spec/execution-trace.schema.json'
HASH = re.compile(r'sha256:[0-9a-f]{64}\Z')
FAIL_STOP = 'QSOL-MORPH:FAIL_STOP:1.0.0'
FAMILIES = {
    'result_determinism_scopes': ('result_determinism_scope_id', 'result_determinism_scope_ids'),
    'numeric_execution_scopes': ('numeric_scope_id', 'numeric_scope_ids'),
    'randomness_execution_scopes': ('randomness_scope_id', 'randomness_scope_ids'),
    'failure_behavior_bindings': ('failure_behavior_binding_id', 'failure_behavior_binding_ids'),
}
LEDGER_IDS = {
    'deck_executions': 'deck_execution_id', 'card_executions': 'card_execution_id',
    'operation_executions': 'operation_execution_id', 'control_decisions': 'control_decision_id',
    'failure_records': 'failure_record_id', 'epistemic_class_bindings': 'epistemic_class_binding_id',
    'backend_selection_scopes': 'backend_selection_scope_id',
    'backend_selection_decisions': 'backend_selection_decision_id',
    'machinery_authorization_records': 'machinery_authorization_record_id',
    'machinery_use_records': 'machinery_use_record_id',
    'effect_authorization_records': 'effect_authorization_record_id',
    'effect_attempts': 'effect_attempt_id', 'effect_non_attempt_records': 'effect_non_attempt_record_id',
    'effect_accounting_failure_records': 'effect_accounting_failure_record_id',
    'inputs': 'input_id', 'outputs': 'output_id', 'external_tool_versions': 'external_tool_id',
    'cache_reuse_records': 'cache_reuse_record_id', 'rule_records': 'rule_id',
    'validation_evidence': 'validation_evidence_id', 'generated_artifacts': 'generated_artifact_id',
    'toolchain_invocations': 'toolchain_invocation_id',
    'toolchain_environment_configs': 'environment_config_hash',
    'optimization_provenance': 'optimization_record_id', 'resolved_extensions': 'resolved_extension_id',
    **{key: value[0] for key, value in FAMILIES.items()},
}
UNSUPPORTED = (
    'operation_executions', 'control_decisions', 'rule_records', 'validation_evidence',
    'generated_artifacts', 'toolchain_invocations', 'toolchain_environment_configs',
    'optimization_provenance', 'resolved_extensions', 'runtime_compiler_versions',
)


class Invalid(ValueError):
    """Receipt is inconsistent, malformed, or outside the supported profile."""


class Unsupported(Invalid):
    """A later frozen operational contract/verifier is required."""


def require(condition, message):
    if not condition:
        raise Invalid(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('ascii')


def content_hash(value):
    """Receipt-content identity; not a PR4 program fingerprint or trust proof."""
    return 'sha256:' + hashlib.sha256(canonical(value)).hexdigest()


def key(value):
    return canonical(value)


def same_set(actual, expected, name):
    a, e = [key(x) for x in actual], [key(x) for x in expected]
    require(len(a) == len(set(a)) and set(a) == set(e), f'{name}: exact set mismatch')


def path_key(path):
    return tuple((p['scope_kind'], p['scope_id']) for p in path)


def prefix(ancestor, descendant):
    return descendant[:len(ancestor)] == ancestor


def strict_load(path):
    """Read exact integer JSON, sharing PR4's bounded token conversion.

    Receipt fractions use typed decimal strings. This is ordinary receipt JSON,
    not a new canonical wire transport. _parse is the existing exact JSON
    primitive; unlike read_model it does not require a top-level program.
    """
    try:
        return serialization._parse(Path(path).read_bytes())
    except (OSError, serialization.Invalid) as exc:
        raise Invalid(str(exc)) from exc


class Receipt:
    def __init__(self, trace):
        self.t = trace
        self.ledgers = {}
        for ledger, field in LEDGER_IDS.items():
            rows = trace.get(ledger, [])
            ids = [r[field] for r in rows]
            require(len(ids) == len(set(ids)), f'{ledger}: duplicate stable identity')
            self.ledgers[ledger] = dict(zip(ids, rows))
        self.scopes = {}
        self.cards = {}
        self.card_paths = {}
        self.deck_paths = {}
        self.effects = {}
        self.machinery = {}
        self.events = {}

    def rows(self, name):
        return self.t.get(name, [])

    def lookup(self, ledger, identity):
        require(identity in self.ledgers[ledger], f'{ledger}: unresolved {identity}')
        return self.ledgers[ledger][identity]

    def event(self, record, field, owner, required=True):
        if field not in record:
            require(not required, f'{owner}: missing {field}')
            return None
        n = record[field]
        require(type(n) is int and n >= 0, f'{owner}: invalid {field}')
        # A shared index is permitted only for projections of one named event.
        require(n not in self.events or self.events[n] == owner,
                f'{owner}: event index reused by {self.events.get(n)}')
        self.events[n] = owner
        return n

    def ref(self, path):
        return {'representation_kind': 'SEMANTIC_IR',
                'representation_identity': self.identity, 'owner_scope_path': path}

    def scope(self, reference):
        require(reference['representation_kind'] == 'SEMANTIC_IR' and
                reference['representation_identity'] == self.identity,
                'wrong representation identity')
        p = path_key(reference['owner_scope_path'])
        require(p in self.scopes, 'unresolved complete scope path')
        return p

    def subject(self, reference):
        p = self.scope(reference)
        require(reference['subject_kind'] == 'CARD' and p in self.cards and
                reference['subject_id'] == p[-1][1], 'invalid CARD subject')
        c = self.lookup('card_executions', reference['execution_id'])
        require(self.card_paths[c['card_execution_id']] == p, 'wrong concrete CARD invocation')
        return c, p

    def projection(self, record, references, canonical_field, execution_field):
        subjects = [self.subject(r)[0] for r in references]
        same_set(record.get(canonical_field, []), [c['card_id'] for c in subjects], canonical_field)
        same_set(record.get(execution_field, []), [c['card_execution_id'] for c in subjects], execution_field)
        require(canonical_field in record and execution_field in record, 'missing Semantic projection')

    def descendants(self, p):
        return sorted({q[-1][1] for q in self.cards if prefix(p, q)})

    def source(self):
        t = self.t
        require(t['input_representation'] == 'SEMANTIC_IR', 'unsupported entry representation')
        require(len(t['representation_records']) == 1, 'exactly one Semantic model is supported')
        representation = t['representation_records'][0]
        require(representation['representation_kind'] == 'SEMANTIC_IR' and
                representation['format'] == 'QSOL-MORPH-MODEL-1.0.0', 'unsupported representation format')
        model = representation['content']
        try:
            self.identity = serialization.fingerprint(model)
        except (check_model.Invalid, serialization.Invalid) as exc:
            raise Invalid(f'invalid canonical source: {exc}') from exc
        require(self.identity == t['input_representation_identity'] == representation['representation_identity'],
                'canonical source fingerprint mismatch')
        jobs = [j for j in model['jobs'] if j['id'] == t.get('job_id')]
        require(len(jobs) == 1, 'selected JOB must resolve')
        self.job = jobs[0]
        self.jobpath = ({'scope_kind': 'JOB', 'scope_id': self.job['id']},)
        def add(node, path):
            p = path_key(path)
            self.scopes[p] = (node, list(path))
            if node['extension_requirements'] or (len(p) == 3 and node['qualifiers']):
                raise Unsupported('extension and qualifier operational interpretation is deferred')
            for declaration in node['machinery_requirements']:
                self.machinery[(p, declaration['machinery_requirement_id'])] = declaration
            if len(p) == 3:
                self.cards[p] = node
                for declaration in node['effect_requirements']:
                    self.effects[(p, declaration['effect_id'])] = declaration
        add(self.job, self.jobpath)
        for d in self.job['decks']:
            dp = self.jobpath + ({'scope_kind': 'DECK', 'scope_id': d['id']},)
            add(d, dp)
            for c in d['cards']:
                add(c, dp + ({'scope_kind': 'CARD', 'scope_id': c['id']},))
        expected_effects = []
        for (p, effect), d in self.effects.items():
            expected_effects.append({**self.ref(self.scopes[p][1]), 'declared_effect_id': effect,
                                    'card_id': p[-1][1], 'effect_kind': d['effect_kind'],
                                    'required_capabilities': d['required_capabilities']})
        same_set(t['effect_requirements'], expected_effects, 'effect_requirements source coverage')
        expected_machinery = []
        for (p, requirement), d in self.machinery.items():
            expected_machinery.append({**self.ref(self.scopes[p][1]), **d,
                                      'source_card_ids': self.descendants(p)})
        same_set(t['machinery_requirements'], expected_machinery, 'machinery_requirements source coverage')

    def contracts(self):
        self.family_paths = {}
        for ledger, (idfield, _) in FAMILIES.items():
            expected = {}
            for p, (node, path) in self.scopes.items():
                data = None
                if ledger == 'result_determinism_scopes' and 'result_determinism' in node:
                    data = dict(requested_result_determinism=node['result_determinism'],
                                effective_result_determinism=node['result_determinism'])
                if ledger == 'numeric_execution_scopes' and 'numeric_contract' in node:
                    n = node['numeric_contract']
                    data = dict(numeric_contract_id=n['contract_id'], numeric_contract_hash=n['definition_hash'],
                                material_numeric_mode=n)
                if ledger == 'randomness_execution_scopes' and 'randomness_contract' in node:
                    n = node['randomness_contract']
                    if n['mode'] == 'EXTERNAL-ENTROPY':
                        raise Unsupported('entropy acquisition semantics require a frozen operation contract')
                    data = dict(requested_randomness_mode=n['mode'], effective_randomness_mode=n['mode'])
                    data.update({k: v for k, v in n.items() if k != 'mode'})
                if ledger == 'failure_behavior_bindings' and (len(p) == 1 or 'failure_behavior' in node):
                    data = dict(requested_failure_behavior_id=FAIL_STOP, effective_failure_behavior_id=FAIL_STOP)
                if data is not None:
                    expected[p] = {**data, 'governed_scope_ref': self.ref(path),
                                   'source_card_ids': self.descendants(p)}
            actual = {}
            for row in self.rows(ledger):
                p = self.scope(row['governed_scope_ref'])
                require(p not in actual, f'{ledger}: duplicate governed scope')
                actual[p] = {k: v for k, v in row.items() if k != idfield}
            require(actual == expected, f'{ledger}: source-derived contract coverage/value mismatch')
            self.family_paths[ledger] = {
                path_key(r['governed_scope_ref']['owner_scope_path']): r[idfield] for r in self.rows(ledger)}
        classes = {}
        for row in self.rows('epistemic_class_bindings'):
            p = self.scope(row)
            require(p in self.cards and p not in classes, 'invalid/duplicate class owner')
            expected = {**self.ref(self.scopes[p][1]), 'subject_kind': 'CARD', 'subject_id': p[-1][1],
                        'semantic_class': self.cards[p]['semantic_class']}
            require({k: v for k, v in row.items() if k != 'epistemic_class_binding_id'} == expected,
                    'class binding differs from canonical source')
            require(expected['semantic_class'] != 'UNCLASSIFIED', 'UNCLASSIFIED has no claim binding')
            classes[p] = row['epistemic_class_binding_id']
        require(set(classes) == {p for p, c in self.cards.items() if c['semantic_class'] != 'UNCLASSIFIED'},
                'source-derived class coverage mismatch')
        self.classes = classes

    def attribution(self, record, paths):
        for ledger, (_, outputfield) in FAMILIES.items():
            expected = [identity for p, identity in self.family_paths[ledger].items()
                        if any(prefix(p, q) for q in paths)]
            same_set(record[outputfield], expected, outputfield)

    def executions(self):
        t = self.t
        require('deck_executions' in t and 'card_executions' in t, 'Semantic execution ledgers required')
        require(len(t['deck_executions']) == len(self.job['decks']), 'selected DECK coverage mismatch')
        ordered_cards = []
        for d, execution in zip(self.job['decks'], t['deck_executions']):
            require(execution['deck_id'] == d['id'], 'DECK order/identity mismatch')
            dp = path_key(self.jobpath) + (('DECK', d['id']),)
            self.deck_paths[execution['deck_execution_id']] = dp
            members = execution['card_execution_ids']
            require(len(members) == len(d['cards']), 'CARD membership coverage mismatch')
            for card, cid in zip(d['cards'], members):
                c = self.lookup('card_executions', cid)
                require(c['deck_execution_id'] == execution['deck_execution_id'] and c['card_id'] == card['id'],
                        'CARD membership/owner mismatch')
                require(cid not in self.card_paths, 'CARD invocation appears in multiple DECKs')
                self.card_paths[cid] = dp + (('CARD', card['id']),)
                ordered_cards.append(c)
        require(set(self.card_paths) == set(self.ledgers['card_executions']), 'orphan CARD execution')
        self.ordered_cards = ordered_cards
        self.failure_paths = {}
        for f in self.rows('failure_records'):
            kind, identity = f['failing_scope_kind'], f['failing_scope_id']
            if kind == 'JOB':
                require(identity == self.job['id'], 'wrong failing JOB')
                require(f['failure_stage'] == 'JOB_PREFLIGHT', 'JOB failure must have JOB_PREFLIGHT stage')
                p = path_key(self.jobpath)
                require(not any(k in f for k in ('failure_card_id', 'failure_card_execution_id',
                                                 'operation_execution_id', 'deck_execution_id')), 'fabricated failure lineage')
            elif kind == 'CARD_EXECUTION':
                require(f['failure_stage'] == 'CARD', 'CARD failure must have CARD stage')
                c = self.lookup('card_executions', identity)
                p = self.card_paths[identity]
                require(f.get('failure_card_execution_id') == identity and f.get('failure_card_id') == c['card_id'] and
                        f.get('deck_execution_id') == c['deck_execution_id'] and 'operation_execution_id' not in f,
                        'CARD failure lineage mismatch')
                require(c.get('failure_record_id') == f['failure_record_id'] and c['card_status'] == 'FAILED',
                        'failure not caused by referenced CARD')
            else:
                raise Unsupported('only JOB preflight and CARD-caused failures supported')
            self.attribution(f, [p])
            self.failure_paths[f['failure_record_id']] = p
            self.event(f, 'sequence_index', ('failure', f['failure_record_id']))
        require(len(self.rows('failure_records')) <= 1, 'single fail-stop failure profile')
        failure = self.rows('failure_records')[0] if self.rows('failure_records') else None
        blocked = failure if failure and failure['failing_scope_kind'] == 'JOB' else None
        previous = -1
        for c in ordered_cards:
            cid, status = c['card_execution_id'], c['card_status']
            require(status in ('SUCCESS', 'FAILED', 'BLOCKED'), 'unsupported CARD path status')
            for field in ('governing_control_decision_id', 'governing_skip_rule_id', 'skip_verification_evidence_id'):
                require(field not in c, 'unsupported control/skip cause')
            if blocked:
                require(status == 'BLOCKED' and c.get('governing_failure_record_id') == blocked['failure_record_id'],
                        'fail-stop must block every later CARD')
                require('failure_record_id' not in c and 'execution_order_index' not in c and not c['input_ids'],
                        'blocked CARD cannot execute, fail, or consume input')
            else:
                require(status != 'BLOCKED' and 'governing_failure_record_id' not in c, 'unsupported/cause-free block')
                order = self.event(c, 'execution_order_index', ('card', cid))
                require(order > previous, 'CARD order violates canonical fail-stop sequence')
                previous = order
                if status == 'FAILED':
                    require(failure is not None and failure['failing_scope_id'] == cid and
                            c.get('failure_record_id') == failure['failure_record_id'], 'failed CARD missing exact failure')
                    require(failure['sequence_index'] > order, 'failure precedes CARD execution')
                    blocked = failure
                else:
                    require('failure_record_id' not in c, 'successful CARD claims failure')
        for d in self.rows('deck_executions'):
            members = [self.lookup('card_executions', x) for x in d['card_execution_ids']]
            expected = 'FAILED' if any(c['card_status'] == 'FAILED' for c in members) else (
                'BLOCKED' if all(c['card_status'] == 'BLOCKED' for c in members) else 'SUCCESS')
            require(d['deck_status'] == expected, 'DECK outcome contradicts CARD outcomes')
            if expected == 'FAILED':
                require(d.get('failure_record_id') == failure['failure_record_id'] and
                        'governing_failure_record_id' not in d, 'DECK failure propagation mismatch')
            elif expected == 'BLOCKED':
                require(d.get('governing_failure_record_id') == failure['failure_record_id'] and
                        'failure_record_id' not in d and 'execution_order_index' not in d, 'blocked DECK cause mismatch')
            else:
                require('failure_record_id' not in d and 'governing_failure_record_id' not in d, 'successful DECK cause')
            if expected != 'BLOCKED':
                start = self.event(d, 'execution_order_index', ('deck', d['deck_execution_id']))
                require(start < members[0]['execution_order_index'], 'DECK starts after CARD')
                prior = [c['execution_order_index'] for c in ordered_cards
                         if c['card_status'] != 'BLOCKED' and
                         c['execution_order_index'] < members[0]['execution_order_index']]
                require(not prior or start > max(prior), 'DECK start violates sequential source order')
        expected = 'FAILED' if failure else 'SUCCESS'
        require(t['execution_status'] == expected and t['job_status'] == expected, 'run/JOB outcome mismatch')
        if failure:
            require(t.get('primary_failure_record_id') == failure['failure_record_id'], 'primary failure missing/wrong')
        else:
            require('primary_failure_record_id' not in t, 'successful run claims primary failure')

    def capability_sets(self, record, required):
        require(record['required_capabilities'] == required, 'canonical complete capabilities mismatch')
        granted, denied = record['granted_capabilities'], record['denied_capabilities']
        require(granted == sorted(set(granted)) and denied == sorted(set(denied)), 'capabilities not canonical sets')
        require(set(granted).isdisjoint(denied) and set(granted + denied) <= set(required), 'invalid capability partition')
        status = record['authorization_status']
        require(status in ('GRANTED', 'DENIED'), 'unsupported authorization status')
        if status == 'GRANTED':
            require(granted == required and not denied, 'grant does not cover entire declaration')
        else:
            require(denied and sorted(granted + denied) == required, 'denial must account for complete capability set')
        require(record['capability_policy_id'] == self.t['capability_policy_id'] and
                record['capability_policy_version'] == self.t['capability_policy_version'], 'policy identity mismatch')

    def selection(self):
        self.selection_paths = {}
        covered_decisions = set()
        for s in self.rows('backend_selection_scopes'):
            sid = s['backend_selection_scope_id']
            p = self.scope(s['governed_scope_ref'])
            require(sid != p[-1][1], 'selection scope identity must differ from governed computation')
            require(p not in self.selection_paths.values(), 'duplicate backend selection governed scope')
            same_set(s['source_card_ids'], self.descendants(p), 'selection source CARD projection')
            require('backend_unit_id' not in s, 'generated backend units unsupported')
            require(len(s['selection_decision_ids']) == 1, 'fallback/replacement needs deferred accepted rule')
            d = self.lookup('backend_selection_decisions', s['selection_decision_ids'][0])
            did = d['backend_selection_decision_id']
            require(did not in covered_decisions and d['backend_selection_scope_id'] == sid,
                    'selection decision scope mismatch')
            covered_decisions.add(did)
            require(not any(k in d for k in ('predecessor_selection_decision_id', 'fallback_rule_id',
                    'fallback_evidence_id', 'selection_policy_id', 'selection_policy_version',
                    'selection_tuning_id', 'selection_tuning_hash', 'target_architecture', 'device')),
                    'automatic/fallback/device-specific selection semantics deferred')
            require(d['requested_target'] == d['selected_backend'], 'unvalidated target substitution')
            self.event(d, 'decision_sequence_index', ('selection', did))
            require(d['decision_status'] in ('FINAL_EXECUTABLE', 'DENIED'), 'unsupported selection status')
            if d['decision_status'] == 'FINAL_EXECUTABLE':
                require(s.get('final_selection_decision_id') == did, 'final selection mismatch')
                require(HASH.fullmatch(d.get('selected_backend_implementation_identity', '')) is not None,
                        'final backend requires immutable content identity')
            else:
                require('final_selection_decision_id' not in s, 'denied selection cannot be final')
                require(self.t['execution_status'] == 'FAILED', 'denied-only selection cannot yield success')
            self.selection_paths[sid] = p
        require(covered_decisions == set(self.ledgers['backend_selection_decisions']), 'orphan selection decision')
        for c in self.ordered_cards:
            if c['card_status'] == 'BLOCKED':
                continue
            p = self.card_paths[c['card_execution_id']]
            scopes = [s for s in self.rows('backend_selection_scopes')
                      if prefix(self.selection_paths[s['backend_selection_scope_id']], p)]
            require(scopes, 'executed CARD has no backend selection')
            for s in scopes:
                require('final_selection_decision_id' in s, 'CARD executed under denied selection')
                d = self.lookup('backend_selection_decisions', s['final_selection_decision_id'])
                require(d['decision_sequence_index'] < c['execution_order_index'], 'selection after execution')

    def machinery_ref(self, ref):
        p = self.scope(ref)
        k = p, ref['machinery_requirement_id']
        require(k in self.machinery, 'unresolved owner-qualified machinery requirement')
        return k

    def machinery_checks(self):
        for a in self.rows('machinery_authorization_records'):
            aid = a['machinery_authorization_record_id']
            s = self.lookup('backend_selection_scopes', a['backend_selection_scope_id'])
            d = self.lookup('backend_selection_decisions', a['backend_selection_decision_id'])
            require(d['backend_selection_scope_id'] == s['backend_selection_scope_id'] and
                    d['backend_selection_decision_id'] in s['selection_decision_ids'], 'machinery authorization selection mismatch')
            refs = [self.machinery_ref(r) for r in a['machinery_requirement_refs']]
            require(refs and len(refs) == len(set(refs)), 'empty/duplicate machinery requirement refs')
            sp = self.selection_paths[s['backend_selection_scope_id']]
            for p, rid in refs:
                require(prefix(p, sp) or prefix(sp, p), 'unrelated machinery requirement')
                require(self.machinery[p, rid]['target_selector_or_class'] == d['requested_target'],
                        'unsupported target selector applicability')
            caps = sorted({cap for r in refs for cap in self.machinery[r]['required_capabilities']})
            self.capability_sets(a, caps)
            if 'source_card_ids' in a:
                same_set(a['source_card_ids'], self.descendants(sp), 'machinery authorization source projection')
            self.event(a, 'authorization_sequence_index', ('machinery-authorization', aid))
            require(aid in d.get('machinery_authorization_record_ids', []), 'missing reciprocal decision authorization')
        for d in self.rows('backend_selection_decisions'):
            same_set(d.get('machinery_authorization_record_ids', []),
                     [a['machinery_authorization_record_id'] for a in self.rows('machinery_authorization_records')
                      if a['backend_selection_decision_id'] == d['backend_selection_decision_id']],
                     'decision machinery authorizations')
        used_subjects = set()
        for u in self.rows('machinery_use_records'):
            uid = u['machinery_use_record_id']
            s = self.lookup('backend_selection_scopes', u['backend_selection_scope_id'])
            require(s.get('final_selection_decision_id') == u['backend_selection_decision_id'],
                    'machinery use is not final executable decision')
            d = self.lookup('backend_selection_decisions', u['backend_selection_decision_id'])
            require(d['decision_status'] == 'FINAL_EXECUTABLE', 'nonexecutable machinery used')
            require(not u['generated_artifact_ids'] and 'backend_unit_id' not in u, 'generated machinery deferred')
            refs = u['execution_subject_refs']
            if not refs:
                raise Unsupported('pre-execution protected setup requires a frozen setup applicability contract')
            require('initiating_scope_ref' not in u, 'runtime machinery cannot masquerade as setup')
            subjects = [self.subject(r) for r in refs]
            self.projection(u, refs, 'source_card_ids', 'card_execution_ids')
            require(all(c['card_status'] != 'BLOCKED' for c, _ in subjects), 'blocked subject used machinery')
            sp = self.selection_paths[s['backend_selection_scope_id']]
            require(all(prefix(sp, p) for _, p in subjects), 'machinery subject outside governed selection')
            expected = {r for r in self.machinery if any(prefix(r[0], p) for _, p in subjects)}
            require(expected, 'protected use without applicable protected requirement')
            for r in expected:
                require(self.machinery[r]['target_selector_or_class'] == d['requested_target'],
                        'target applicability cannot discard an inherited requirement')
            covered = []
            start = self.event(u, 'protected_use_start_sequence_index', ('machinery-start', uid))
            stop = self.event(u, 'protected_use_stop_sequence_index', ('machinery-stop', uid))
            require(start < stop, 'machinery stop must follow start')
            for aid in u['machinery_authorization_record_ids']:
                a = self.lookup('machinery_authorization_records', aid)
                require(a['backend_selection_scope_id'] == s['backend_selection_scope_id'] and
                        a['backend_selection_decision_id'] == d['backend_selection_decision_id'] and
                        a['authorization_status'] == 'GRANTED', 'wrong-context/denied machinery authorization')
                require(a['authorization_sequence_index'] < start, 'machinery authorization after use')
                covered.extend(self.machinery_ref(r) for r in a['machinery_requirement_refs'])
            require(set(covered) == expected, 'incomplete/unrelated canonical machinery coverage')
            for c, _ in subjects:
                used_subjects.add(c['card_execution_id'])
                self.within_card(c, start, stop)
        for c in self.ordered_cards:
            p = self.card_paths[c['card_execution_id']]
            if c['card_status'] == 'SUCCESS' and any(prefix(r[0], p) for r in self.machinery):
                require(c['card_execution_id'] in used_subjects, 'successful protected CARD omitted machinery use')

    def within_card(self, card, begin, end=None):
        require(card['card_status'] != 'BLOCKED', 'blocked CARD cannot have an event')
        lower = card['execution_order_index']
        require(begin > lower, 'event precedes owning CARD execution')
        following = [c['execution_order_index'] for c in self.ordered_cards
                     if c['card_status'] != 'BLOCKED' and c['execution_order_index'] > lower]
        next_decks = [d['execution_order_index'] for d in self.rows('deck_executions')
                      if d['deck_status'] != 'BLOCKED' and d['execution_order_index'] > lower]
        following.extend(next_decks)
        if following:
            upper = min(following)
            require(begin < upper and (end is None or end < upper), 'event crosses later CARD boundary')
        if card['card_status'] == 'FAILED':
            f = self.lookup('failure_records', card['failure_record_id'])
            require(begin < f['sequence_index'] and (end is None or end < f['sequence_index']),
                    'event follows owning CARD failure')

    def effect_pair(self, row, projection=True):
        p = self.scope(row['effect_requirement_ref'])
        k = p, row['effect_requirement_ref']['declared_effect_id']
        require(k in self.effects, 'unresolved canonical effect declaration')
        c, cp = self.subject(row['execution_subject_ref'])
        require(cp == p, 'effect declaration belongs to another execution subject')
        if projection:
            require(row.get('card_id') == c['card_id'] and row.get('card_execution_id') == c['card_execution_id'],
                    'effect Semantic lineage projection mismatch')
        return k, c

    def effects_checks(self):
        outcomes = {}
        for a in self.rows('effect_authorization_records'):
            k, c = self.effect_pair(a)
            aid = a['effect_authorization_record_id']
            attempt = self.lookup('effect_attempts', a['effect_attempt_id'])
            require(attempt['effect_authorization_record_id'] == aid and
                    attempt['effect_requirement_ref'] == a['effect_requirement_ref'] and
                    attempt['execution_subject_ref'] == a['execution_subject_ref'], 'authorization/attempt context mismatch')
            self.capability_sets(a, self.effects[k]['required_capabilities'])
            self.event(a, 'authorization_sequence_index', ('effect-authorization', aid))
        for a in self.rows('effect_attempts'):
            k, c = self.effect_pair(a)
            require(c['card_status'] != 'BLOCKED', 'blocked CARD has attempted effect')
            pair = k, c['card_execution_id']
            outcomes.setdefault(pair, []).append(('attempt', a))
            d = self.effects[k]
            require(a['effect_kind'] == d['effect_kind'] and a['required_capabilities'] == d['required_capabilities'],
                    'attempt differs from canonical effect')
            auth = self.lookup('effect_authorization_records', a['effect_authorization_record_id'])
            require(auth['effect_attempt_id'] == a['effect_attempt_id'], 'authorization reused across attempts')
            aid = a['effect_attempt_id']
            event = self.event(a, 'sequence_index', ('attempt', aid))
            state = a['completion_state']
            if state == 'NOT_STARTED':
                require(auth['authorization_sequence_index'] < event, 'never-started decision precedes authorization')
                require(not any(f in a for f in ('effect_begin_sequence_index', 'effect_end_sequence_index', 'termination_known')),
                        'NOT_STARTED has boundary events')
                require(not any(a[f] for f in ('acquired_input_ids', 'observable_output_ids', 'external_tool_ids')),
                        'NOT_STARTED claims material participation')
                require(c['card_status'] == 'FAILED', 'required never-started effect cannot satisfy successful CARD')
                self.within_card(c, event)
            else:
                require(auth['authorization_status'] == 'GRANTED', 'begun effect lacks grant')
                begin = self.event(a, 'effect_begin_sequence_index', ('effect-begin', aid))
                require(auth['authorization_sequence_index'] < begin and event <= begin, 'effect authorization/order violation')
                if state == 'UNKNOWN':
                    require(type(a.get('termination_known')) is bool, 'UNKNOWN requires explicit termination knowledge')
                    end = self.event(a, 'effect_end_sequence_index', ('effect-end', aid), a['termination_known'])
                    require(a['termination_known'] == (end is not None), 'UNKNOWN termination boundary contradiction')
                else:
                    require(state in ('COMPLETED', 'ABORTED_CLEAN', 'PARTIAL'), 'invalid completion state')
                    require('termination_known' not in a, 'termination discriminator only for UNKNOWN')
                    end = self.event(a, 'effect_end_sequence_index', ('effect-end', aid))
                require(end is None or begin < end, 'effect termination before begin')
                require(state == 'COMPLETED' or c['card_status'] == 'FAILED', 'incomplete effect cannot satisfy successful CARD')
                if state == 'ABORTED_CLEAN':
                    require(not a['observable_output_ids'], 'clean abort claims observable output')
                self.within_card(c, event, end)
                self.within_card(c, begin, end)
        for n in self.rows('effect_non_attempt_records'):
            k, c = self.effect_pair(n)
            pair = k, c['card_execution_id']
            outcomes.setdefault(pair, []).append(('non-attempt', n))
            require(n['effect_kind'] == self.effects[k]['effect_kind'], 'non-attempt effect kind mismatch')
            require(n['non_attempt_reason'] == 'PRIOR_FAIL_STOP' and c['card_status'] == 'BLOCKED' and
                    n.get('governing_failure_record_id') == c.get('governing_failure_record_id'),
                    'non-attempt needs exact validated fail-stop cause')
            require(not any(f in n for f in ('governing_control_decision_id', 'governing_skip_rule_id',
                                             'skip_verification_evidence_id')), 'unsupported skip/nonreach cause')
        for n in self.rows('effect_accounting_failure_records'):
            k, c = self.effect_pair(n, False)
            pair = k, c['card_execution_id']
            outcomes.setdefault(pair, []).append(('accounting-failure', n))
            require(n['accounting_failure_kind'] in ('BACKEND_OMISSION_DETECTED', 'ACCOUNTING_INCOMPLETE'),
                    'unknown accounting failure kind')
            require(c['card_status'] == 'FAILED' and n['failure_record_id'] == c.get('failure_record_id'),
                    'accounting failure cannot account for successful/unrelated subject')
            f = self.lookup('failure_records', n['failure_record_id'])
            detected = self.event(n, 'detected_sequence_index', ('accounting-detected', n['effect_accounting_failure_record_id']))
            require(c['execution_order_index'] < detected < f['sequence_index'], 'accounting failure detection order')
        expected = {(k, cid) for cid, p in self.card_paths.items() for k in self.effects if k[0] == p}
        require(set(outcomes) == expected, 'unconditional declared-effect accounting incomplete')
        for records in outcomes.values():
            # Multiple retries require later frozen retry semantics, not guessed behavior.
            require(len(records) == 1, 'duplicate/conflicting effect outcomes; retries deferred')
        for f in self.rows('failure_records'):
            expected_ids = [r['effect_accounting_failure_record_id'] for r in self.rows('effect_accounting_failure_records')
                            if r['failure_record_id'] == f['failure_record_id']]
            same_set(f.get('effect_accounting_failure_record_ids', []), expected_ids, 'failure accounting reciprocal closure')

    def inputs_checks(self):
        for i in self.rows('inputs'):
            iid = i['input_id']
            require('artifact_id_or_version' not in i, 'opaque immutable input identity needs a frozen resolver')
            require('canonical_value' in i or HASH.fullmatch(i.get('content_hash', '')) is not None,
                    'input lacks canonical value/content hash')
            if 'content_hash' in i:
                require(HASH.fullmatch(i['content_hash']) is not None, 'invalid input content hash')
                if 'canonical_value' in i:
                    require(content_hash(i['canonical_value']) == i['content_hash'], 'input value/hash mismatch')
            require(i['consumer_execution_refs'] and not i.get('consumer_scope_refs'),
                    'setup/build-only input provenance deferred')
            consumers = [self.subject(r)[0] for r in i['consumer_execution_refs']]
            same_set(i.get('consumer_card_execution_ids', []), [c['card_execution_id'] for c in consumers],
                     'input Semantic consumer projection')
            if 'source_card_ids' in i:
                same_set(i['source_card_ids'], [c['card_id'] for c in consumers], 'input source projection')
            for c in consumers:
                require(c['card_status'] != 'BLOCKED' and iid in c['input_ids'], 'unstarted/nonreciprocal input consumer')
            for aid in i['effect_attempt_ids']:
                a = self.lookup('effect_attempts', aid)
                require(iid in a['acquired_input_ids'] and a['completion_state'] == 'COMPLETED',
                        'input acquisition must be reciprocal and completed in this profile')
                _, owner = self.effect_pair(a)
                for c in consumers:
                    if owner['card_execution_id'] != c['card_execution_id']:
                        require(a['effect_end_sequence_index'] < c['execution_order_index'], 'input acquired after consumer began')
            # Material operands/result-dependency interpretation is a later operation contract.
        for c in self.ordered_cards:
            expected = [i['input_id'] for i in self.rows('inputs')
                        if any(r['execution_id'] == c['card_execution_id'] for r in i['consumer_execution_refs'])]
            same_set(c['input_ids'], expected, 'CARD input reciprocity')
        for a in self.rows('effect_attempts'):
            expected = [i['input_id'] for i in self.rows('inputs') if a['effect_attempt_id'] in i['effect_attempt_ids']]
            same_set(a['acquired_input_ids'], expected, 'effect acquisition reciprocity')

    def caches(self):
        seen = set()
        for r in self.rows('cache_reuse_records'):
            if r['classification'] != 'COLD_EXECUTION':
                raise Unsupported('cache reuse and diagnostic transitions require accepted rules')
            allowed = {'cache_reuse_record_id', 'classification', 'execution_subject_refs', 'source_card_ids',
                       'card_execution_ids', 'material_cache_identity_hash'}
            require(set(r) <= allowed, 'cold execution must not claim reuse authority')
            require(HASH.fullmatch(r['material_cache_identity_hash']) is not None, 'cache identity must be content-bound')
            self.projection(r, r['execution_subject_refs'], 'source_card_ids', 'card_execution_ids')
            require(r['execution_subject_refs'], 'runtime cache has no subjects')
            for ref in r['execution_subject_refs']:
                c, _ = self.subject(ref)
                cid = c['card_execution_id']
                require(cid not in seen and c['card_status'] != 'BLOCKED', 'contradictory/unstarted cache subject')
                seen.add(cid)
                require(r['cache_reuse_record_id'] in c.get('cache_reuse_record_ids', []), 'missing reciprocal cache link')
        for c in self.ordered_cards:
            same_set(c.get('cache_reuse_record_ids', []),
                     [r['cache_reuse_record_id'] for r in self.rows('cache_reuse_records')
                      if any(s['execution_id'] == c['card_execution_id'] for s in r['execution_subject_refs'])],
                     'CARD cache reciprocity')

    def outputs_checks(self):
        produced_bindings = set()
        for o in self.rows('outputs'):
            oid = o['output_id']
            refs = o['producer_execution_refs']
            subjects = [self.subject(r) for r in refs]
            require(len(subjects) == 1, 'multiple-producer composition requires a frozen operation rule')
            c, p = subjects[0]
            require(c['card_status'] != 'BLOCKED', 'blocked CARD produced output')
            self.projection(o, refs, 'producer_card_ids', 'producer_card_execution_ids')
            expected_classes = [self.classes[p]] if p in self.classes else []
            same_set(o['epistemic_class_binding_ids'], expected_classes, 'output source-derived class set')
            require(o['semantic_class'] == self.cards[p]['semantic_class'], 'output class differs from source binding')
            if o['semantic_class'] in ('TEST', 'VALIDATION', 'PROOF') or 'evidence_status' in o:
                raise Unsupported('research evidence requires an independently accepted substantive verifier')
            require(HASH.fullmatch(o['artifact_hash']) is not None, 'output content identity malformed')
            bindings = {b['result_binding_id'] for b in self.cards[p]['result_bindings']}
            if bindings:
                require('result_binding_ref' in o, 'named output binding omitted')
                ref = o['result_binding_ref']
                require(self.scope(ref) == p and ref['binding_id'] in bindings, 'output binding wrong owner/name')
                binding_key = c['card_execution_id'], ref['binding_id']
                require(binding_key not in produced_bindings, 'result binding produced more than once')
                produced_bindings.add(binding_key)
            else:
                require('result_binding_ref' not in o, 'output invents a source binding')
            self.attribution(o, [p])
            expected_backend = [sid for sid, q in self.selection_paths.items() if prefix(q, p)]
            same_set(o['backend_selection_scope_ids'], expected_backend, 'output producer-derived backend scopes')
            # A deliberately conservative synthetic materiality profile: all recorded
            # direct inputs contribute. Actual verb-specific pruning is not inferred.
            same_set(o['input_ids'], c['input_ids'], 'output material-input synthetic profile')
            require(not o.get('generated_artifact_ids'), 'generated output provenance deferred')
            pub = self.event(o, 'publication_sequence_index', ('publication', oid))
            self.within_card(c, pub)
            for iid in o['input_ids']:
                for aid in self.lookup('inputs', iid)['effect_attempt_ids']:
                    acquisition = self.lookup('effect_attempts', aid)
                    require(acquisition['effect_end_sequence_index'] < pub,
                            'output published before material input acquisition completed')
            if c['card_status'] == 'FAILED':
                require(o['status'] == 'PARTIAL' and o.get('effect_attempt_ids'),
                        'failed pure CARD cannot commit output; retained effect artifact must be PARTIAL')
            else:
                require(o['status'] == 'COMPLETE', 'successful CARD output must be COMPLETE')
            for aid in o.get('effect_attempt_ids', []):
                a = self.lookup('effect_attempts', aid)
                require(a['execution_subject_ref'] in refs and oid in a['observable_output_ids'],
                        'output effect producer/reciprocal mismatch')
                require(a['completion_state'] in ('COMPLETED', 'PARTIAL'), 'effect cannot expose this output')
                require(a['effect_end_sequence_index'] < pub, 'effect output published before termination')
            for uid in o['machinery_use_record_ids']:
                u = self.lookup('machinery_use_records', uid)
                require(oid in u['output_ids'] and all(r in refs for r in u['execution_subject_refs']),
                        'output protected-use producer/reciprocal mismatch')
                require(u['protected_use_stop_sequence_index'] < pub, 'output precedes protected-use stop')
            if any(prefix(r[0], p) for r in self.machinery):
                require(o['machinery_use_record_ids'], 'protected producer output omits concrete machinery use')
            for cid in o.get('cache_reuse_record_ids', []):
                r = self.lookup('cache_reuse_records', cid)
                require(all(s in refs for s in r['execution_subject_refs']), 'cache output has unrelated current invocation')
            same_set(o.get('cache_reuse_record_ids', []), c.get('cache_reuse_record_ids', []), 'output cache relation')
        expected_bindings = {(c['card_execution_id'], b['result_binding_id']) for c in self.ordered_cards
                             if c['card_status'] == 'SUCCESS'
                             for b in self.cards[self.card_paths[c['card_execution_id']]]['result_bindings']}
        successful_produced = {b for b in produced_bindings if self.lookup('card_executions', b[0])['card_status'] == 'SUCCESS'}
        require(successful_produced == expected_bindings, 'successful named result coverage incomplete')
        for a in self.rows('effect_attempts'):
            same_set(a['observable_output_ids'], [o['output_id'] for o in self.rows('outputs')
                     if a['effect_attempt_id'] in o.get('effect_attempt_ids', [])], 'effect output reciprocity')
        for u in self.rows('machinery_use_records'):
            same_set(u['output_ids'], [o['output_id'] for o in self.rows('outputs')
                     if u['machinery_use_record_id'] in o['machinery_use_record_ids']], 'machinery output reciprocity')
        if 'observable_output_ids' in self.t:
            same_set(self.t['observable_output_ids'], [o['output_id'] for o in self.rows('outputs')], 'observable output closure')

    def tools_checks(self):
        for tool in self.rows('external_tool_versions'):
            tid = tool['external_tool_id']
            require(tool['effect_attempt_ids'] or tool['output_ids'], 'material tool has no concrete subjects')
            if tool['material_identity_status'] == 'IDENTIFIED':
                require(tool.get('material_identity_kind') == 'CONTENT_HASH' and
                        HASH.fullmatch(tool.get('material_identity_value', '')) is not None, 'tool identity not content-bound')
            else:
                require(tool['material_identity_status'] == 'UNAVAILABLE' and
                        'material_identity_kind' not in tool and 'material_identity_value' not in tool,
                        'contradictory tool identity unavailability')
            cards = []
            for aid in tool['effect_attempt_ids']:
                a = self.lookup('effect_attempts', aid)
                require(tid in a['external_tool_ids'] and a['completion_state'] != 'NOT_STARTED', 'tool/attempt reciprocity')
                cards.append(self.subject(a['execution_subject_ref'])[0]['card_id'])
            for oid in tool['output_ids']:
                o = self.lookup('outputs', oid)
                require(tid in o['external_tool_ids'], 'tool/output reciprocity')
                cards.extend(self.subject(r)[0]['card_id'] for r in o['producer_execution_refs'])
            if 'source_card_ids' in tool:
                same_set(tool['source_card_ids'], cards, 'tool Semantic projection')
        for ledger, identity in (('effect_attempts', 'effect_attempt_id'), ('outputs', 'output_id')):
            reverse = 'effect_attempt_ids' if ledger == 'effect_attempts' else 'output_ids'
            for row in self.rows(ledger):
                same_set(row['external_tool_ids'], [tool['external_tool_id'] for tool in self.rows('external_tool_versions')
                         if row[identity] in tool[reverse]], 'material external tool reciprocal attribution')

    def summaries(self):
        required = sorted({cap for d in list(self.effects.values()) + list(self.machinery.values())
                           for cap in d['required_capabilities']})
        auths = self.rows('effect_authorization_records') + self.rows('machinery_authorization_records')
        for field, expected in (
            ('required_capabilities', required),
            ('granted_capabilities', sorted({c for a in auths for c in a['granted_capabilities']})),
            ('denied_capabilities', sorted({c for a in auths for c in a['denied_capabilities']})),
        ):
            if field in self.t:
                require(self.t[field] == expected, f'{field}: summary mismatch')
        used = {c for a in self.rows('effect_attempts') if a['completion_state'] != 'NOT_STARTED'
                for c in a['required_capabilities']}
        for u in self.rows('machinery_use_records'):
            for aid in u['machinery_authorization_record_ids']:
                used.update(self.lookup('machinery_authorization_records', aid)['required_capabilities'])
        if 'capabilities_used' in self.t:
            require(self.t['capabilities_used'] == sorted(used), 'capabilities_used summary mismatch')
        for field, expected in (('job_ids', [self.job['id']]),
                                ('deck_ids', [d['id'] for d in self.job['decks']]),
                                ('card_ids', sorted({p[-1][1] for p in self.cards}))):
            if field in self.t:
                same_set(self.t[field], expected, field)


def json_tree(value):
    """Accept only finite JSON data, even at the Python API's opaque payloads."""
    active = set()
    stack = [(value, False)]
    while stack:
        node, leaving = stack.pop()
        if leaving:
            active.remove(id(node))
            continue
        if type(node) in (dict, list):
            require(id(node) not in active, 'cyclic JSON content')
            active.add(id(node))
            stack.append((node, True))
            if type(node) is dict:
                require(all(type(k) is str for k in node), 'JSON object key must be a string')
                stack.extend((v, False) for v in node.values())
            else:
                stack.extend((v, False) for v in node)
        elif type(node) is float:
            raise Invalid('binary float payload unsupported; use exact integers or typed decimal strings')
        else:
            require(node is None or type(node) in (str, int, bool), 'non-JSON payload type')


def validate(trace):
    """Validate supported synthetic consistency only; never grant execution authority.

    This public entry has no caller-controlled adapter, verifier, network resolver,
    bypass flag, or production execution acceptance path.
    """
    json_tree(trace)
    schema = strict_load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    error = next(Draft202012Validator(schema).iter_errors(trace), None)
    if error is not None:
        location = '/'.join(map(str, error.absolute_path)) or '<receipt>'
        raise Invalid(f'{location}: {error.message}')
    if trace['receipt_kind'] != 'SYNTHETIC_CONFORMANCE_RECEIPT':
        raise Unsupported('EXECUTION_TRACE requires a frozen operational contract; gate remains closed')
    if trace['input_representation'] != 'SEMANTIC_IR':
        raise Unsupported('lower entry requires a frozen representation adapter; no production adapter installed')
    for field in UNSUPPORTED:
        if trace.get(field):
            raise Unsupported(f'{field}: later accepted contract/verifier required')
    forbidden = ('source_trace', 'core_ir_hash', 'vector_dataflow_ir_hash', 'semantic_to_core', 'core_to_vector',
                 'dependency_graph_hash', 'morph_version', 'optimization_profile', 'result_determinism_bindings',
                 'numeric_contract_bindings', 'randomness_contract_bindings', 'extension_requirements',
                 'vectorization_decisions', 'fusion_decisions', 'memory_placement_decisions')
    for field in forbidden:
        if field in trace:
            raise Unsupported(f'{field}: unsupported provenance projection')
    require(trace.get('semantic_ir_hash') == trace['input_representation_identity'], 'Semantic identity summary mismatch')
    require('capability_policy_id' in trace and 'capability_policy_version' in trace, 'synthetic policy identity required')
    receipt = Receipt(trace)
    receipt.source()
    receipt.contracts()
    receipt.executions()
    receipt.selection()
    receipt.machinery_checks()
    receipt.effects_checks()
    receipt.inputs_checks()
    receipt.caches()
    receipt.outputs_checks()
    receipt.tools_checks()
    receipt.summaries()
    if receipt.rows('failure_records'):
        failure = receipt.rows('failure_records')[0]
        require(all(index < failure['sequence_index'] or owner == ('failure', failure['failure_record_id'])
                    for index, owner in receipt.events.items()),
                'event occurs after fail-stop failure')
    return {'validation_kind': 'SYNTHETIC_RECEIPT_CONSISTENCY', 'execution_conformance': False,
            'run_id': trace['run_id'], 'input_representation_identity': receipt.identity}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipts', nargs='+', type=Path)
    args = parser.parse_args(argv)
    try:
        # All inputs validate before any success is printed.
        results = [validate(strict_load(path)) for path in args.receipts]
    except (Invalid, RecursionError, ValueError, TypeError, OverflowError) as exc:
        print(f'trace rejected: {exc}', file=sys.stderr)
        return 1
    for result in results:
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
