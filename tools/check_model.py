#!/usr/bin/env python3
"""Validate canonical model 1.0.0 data; never execute or normalize a program."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / 'spec/canonical-model.schema.json'
HISTORY = SCHEMA.parent / 'history/canonical-model-1.0.0.schema.json'
HISTORY_SHA256 = 'b162907d3180208626cc96e4e260cc0a155db9c9066f129b84180e173da0670e'
FACETS = ('result_determinism', 'numeric_contract', 'randomness_contract', 'failure_behavior')


class Invalid(ValueError):
    """A structural or cross-record canonical-model violation."""


def require(condition, message):
    if not condition:
        raise Invalid(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f'duplicate object key: {key}')
        result[key] = value
    return result


def load(path):
    """Read a validation fixture; this is not a canonical transport profile."""
    def reject_constant(value):
        raise Invalid(f'non-JSON number: {value}')
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'),
                          object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Invalid(str(exc)) from exc


def ordered_unique(records, key, context):
    values = [record[key] for record in records]
    require(values == sorted(set(values)), f'{context}: {key} must be unique and sorted')


def sibling_ids(records, context):
    ids = [record['id'] for record in records]
    require(len(ids) == len(set(ids)), f'{context}: duplicate sibling id')


def path_key(path):
    return tuple(segment['scope_id'] for segment in path)


def ref_key(reference):
    return path_key(reference['owner_scope_path']), reference.get('result_binding_id')


def validate(program):
    """Raise Invalid on rejection; return None without modifying the input.

    Success establishes data-model conformance, not executable-language,
    capability, numeric-contract, extension, or research-evidence conformance.
    """
    historical = HISTORY.read_bytes()
    require(hashlib.sha256(historical).hexdigest() == HISTORY_SHA256,
            'historical model schema changed; explicit migration required')
    require(SCHEMA.read_bytes() == historical,
            'model 1.0.0 schema differs from frozen history; explicit migration required')
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    error = next(Draft202012Validator(schema).iter_errors(program), None)
    if error is not None:
        location = '/'.join(map(str, error.absolute_path)) or '<program>'
        raise Invalid(f'{location}: schema: {error.message}')

    def values(node):
        # Walk only after the closed schema has established shapes. Reject
        # noncanonical decimal zero and meaningless boolean/text dimensions.
        if isinstance(node, dict):
            if set(node) == {'type', 'unit', 'value'}:
                if node['type'] in ('BOOLEAN', 'TEXT'):
                    require(node['unit'] == '1', 'BOOLEAN/TEXT values must be dimensionless')
                if node['type'] == 'DECIMAL':
                    require(node['value'] != '-0', 'negative decimal zero is not canonical')
            for child in node.values():
                values(child)
        elif isinstance(node, list):
            for child in node:
                values(child)
    values(program)

    cards = {}
    job_orders = {}
    sibling_ids(program['jobs'], 'program')

    def scope(node, path, inherited, extensions):
        context = '/'.join(path)
        if 'source_location' in node:
            location = node['source_location']
            start, end = location['start'], location['end']
            require((start['line'], start['column']) <= (end['line'], end['column']),
                    f'{context}: reversed source span')
        effective = dict(inherited)
        for facet in FACETS:
            if facet in node:
                require(facet not in inherited or node[facet] == inherited[facet],
                        f'{context}: unsupported {facet} refinement; inherited contract must be identical')
                effective[facet] = node[facet]
        if effective.get('result_determinism') == 'NUMERIC':
            require('numeric_contract' in effective, f'{context}: NUMERIC requires numeric_contract at this scope or ancestor')
        if 'numeric_contract' in node:
            ordered_unique(node['numeric_contract']['parameters'], 'name', context)
        ordered_unique(node['extension_requirements'], 'profile_name', context)
        active = dict(extensions)
        for extension in node['extension_requirements']:
            name = extension['profile_name']
            require(name not in active or active[name] == extension,
                    f'{context}: conflicting inherited extension requirement {name}')
            active[name] = extension
        ordered_unique(node['machinery_requirements'], 'machinery_requirement_id', context)
        for requirement in node['machinery_requirements']:
            capabilities = requirement['required_capabilities']
            require(capabilities == sorted(capabilities), f'{context}: machinery capabilities must be sorted')
        return effective, active

    for job in program['jobs']:
        jid = job['id']
        job_contract, job_extensions = scope(job, (jid,), {}, {})
        sibling_ids(job['decks'], jid)
        ordered = []
        for deck in job['decks']:
            did = deck['id']
            deck_contract, deck_extensions = scope(deck, (jid, did), job_contract, job_extensions)
            sibling_ids(deck['cards'], f'{jid}/{did}')
            for card in deck['cards']:
                key = (jid, did, card['id'])
                context = '/'.join(key)
                scope(card, key, deck_contract, deck_extensions)
                cards[key] = card
                ordered.append(key)
                for field, ident in (('result_bindings', 'result_binding_id'), ('qualifiers', 'name'),
                                     ('effect_requirements', 'effect_id'), ('dependencies', 'dependency_id'),
                                     ('sequencing_constraints', 'constraint_id')):
                    ordered_unique(card[field], ident, context)
                operand_ids = [operand['operand_id'] for operand in card['operands']]
                require(len(operand_ids) == len(set(operand_ids)), f'{context}: duplicate operand_id')
                for binding in card['result_bindings']:
                    require(binding['semantic_class'] == card['semantic_class'],
                            f'{context}: result semantic class must match CARD class; class transitions are deferred')
                    if binding['type'] in ('BOOLEAN', 'TEXT'):
                        require(binding['unit'] == '1', f'{context}: BOOLEAN/TEXT binding must be dimensionless')
                for effect in card['effect_requirements']:
                    caps = effect['required_capabilities']
                    require(caps == sorted(caps), f'{context}: effect capabilities must be sorted')
        job_orders[jid] = ordered

    def resolve(reference, consumer):
        path = path_key(reference['owner_scope_path'])
        require(path[-1] == reference['producer_card_id'], 'terminal CARD and producer_card_id disagree')
        require(path in cards, f'{consumer}: unknown owner-qualified producer {path}')
        require(path[0] == consumer[0], 'cross-JOB dependencies/sequencing are not supported in model 1.0.0')
        binding = None
        if 'result_binding_id' in reference:
            binding = next((item for item in cards[path]['result_bindings']
                            if item['result_binding_id'] == reference['result_binding_id']), None)
            require(binding is not None, f'{consumer}: unknown result_binding_id at exact producer {path}')
        return path, binding

    for order in job_orders.values():
        positions = {key: index for index, key in enumerate(order)}
        previous_effect = None
        for index, key in enumerate(order):
            card = cards[key]
            dependencies = set()
            for dependency in card['dependencies']:
                producer, _ = resolve(dependency['producer_ref'], key)
                require(positions[producer] < index, f'{key}: dependency must precede consumer in JOB source order')
                reference = ref_key(dependency['producer_ref'])
                require(reference not in dependencies, f'{key}: duplicate dependency target')
                dependencies.add(reference)
            for operand in card['operands']:
                if 'producer_ref' in operand:
                    _, binding = resolve(operand['producer_ref'], key)
                    require(ref_key(operand['producer_ref']) in dependencies,
                            f'{key}: operand requires an exact value-specific dependency')
                    require(all(operand[field] == binding[field] for field in ('type', 'unit')),
                            f'{key}: operand type/unit differs from producer binding; conversions are not implicit')
            edges = set()
            for constraint in card['sequencing_constraints']:
                predecessor, _ = resolve(constraint['predecessor_ref'], key)
                require(positions[predecessor] < index, f'{key}: sequencing predecessor must precede CARD')
                edge = (constraint['kind'], predecessor)
                require(edge not in edges, f'{key}: duplicate sequencing edge')
                if constraint['kind'] == 'EFFECT_ORDER':
                    require(card['effect_requirements'] and cards[predecessor]['effect_requirements'],
                            f'{key}: EFFECT_ORDER endpoints must both declare effects')
                edges.add(edge)
            if index:
                for kind in ('SOURCE_ORDER', 'FAILURE_ORDER'):
                    require((kind, order[index - 1]) in edges, f'{key}: missing adjacent {kind} predecessor')
            if card['effect_requirements']:
                if previous_effect is not None:
                    require(('EFFECT_ORDER', previous_effect) in edges, f'{key}: missing previous EFFECT_ORDER predecessor')
                previous_effect = key


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args(argv)
    try:
        for path in args.files:
            validate(load(path))
            print(f'{path}: canonical model 1.0.0 valid (no execution or transport claim)')
    except (Invalid, OSError, UnicodeError, RecursionError) as exc:
        print(f'canonical model check failed: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
