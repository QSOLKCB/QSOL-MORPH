#!/usr/bin/env python3
"""Generate the closed, structural PR5 trace envelope (no execution semantics).

Run with --check to detect schema drift. Cross-record/source-bound validation is
intentionally separate. Opaque JSON is confined to explicitly content-bound
payloads, not arbitrary extension or metadata fields.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / 'spec/execution-trace.schema.json'


def build_schema():
    defs = {}
    def ref(name): return {'$ref': '#/$defs/' + name}
    def enum(*values): return {'enum': list(values)}
    def array(item=None, minimum=0, unique=True):
        value = {'type': 'array', 'items': item or ref('identity'), 'minItems': minimum}
        if unique: value['uniqueItems'] = True
        return value
    def obj(properties, optional=()):
        return {'type': 'object', 'properties': properties,
                'required': [name for name in properties if name not in optional],
                'additionalProperties': False}
    def record(name, fields, overrides=None):
        properties = {}
        optional = []
        for token in fields.split():
            opt = token.endswith('?')
            token = token.rstrip('?')
            is_array = token.endswith('[]')
            key = token[:-2] if is_array else token
            if opt: optional.append(key)
            properties[key] = array() if is_array else ref('identity')
            if key.endswith('_index'): properties[key] = ref('event_index')
        properties.update(overrides or {})
        defs[name] = obj(properties, optional)
        return ref(name)
    def when(field, value, required=(), forbidden=(), properties=None):
        then = {}
        if required: then['required'] = list(required)
        if forbidden: then['not'] = {'anyOf': [{'required': [name]} for name in forbidden]}
        if properties: then['properties'] = properties
        return {'if': {'properties': {field: {'const': value}}, 'required': [field]}, 'then': then}
    def conditions(name, *rules): defs[name].setdefault('allOf', []).extend(rules)
    def co_present(name, fields):
        dependencies = defs[name].setdefault('dependentRequired', {})
        for field in fields:
            dependencies[field] = sorted(set(dependencies.get(field, ())) | (set(fields) - {field}))
    defs['identity'] = {'type': 'string', 'minLength': 1}
    defs['event_index'] = {'type': 'integer', 'minimum': 0}
    defs['payload'] = {'description': 'Opaque JSON content; its declared content identity must be verified separately.'}
    defs['representation_kind'] = enum('SEMANTIC_IR', 'QSOL_CORE', 'VECTOR_DATAFLOW_IR')
    defs['semantic_class'] = enum('OBSERVATION', 'ASSUMPTION', 'PARAMETER', 'MODEL', 'SIMULATION', 'DERIVATION', 'TEST', 'VALIDATION', 'PROOF', 'RESULT', 'UNCLASSIFIED')
    defs['randomness_mode'] = enum('NONE', 'SEEDED', 'EXTERNAL-ENTROPY', 'DECLARED-NONDETERMINISTIC')
    defs['authorization_status'] = enum('GRANTED', 'DENIED', 'INCOMPLETE')
    defs['execution_status'] = enum('SUCCESS', 'FAILED', 'NOT_STARTED', 'UNTAKEN', 'UNTAKEN_BRANCH', 'BLOCKED', 'FAIL_STOP_BLOCKED', 'NOT_REACHED', 'EXPLICIT_SKIP', 'SKIPPED')
    record('scope_segment', 'scope_kind scope_id')
    defs['scope_path'] = array(ref('scope_segment'), 1, unique=False)
    defs['binding_owner_path'] = array(ref('scope_segment'), unique=False)
    defs['binding_owner_path']['description'] = 'Empty only for an actual representation-root binding; contextual resolution must establish root ownership.'
    qualified = {'representation_kind': ref('representation_kind'), 'representation_identity': ref('identity'), 'owner_scope_path': ref('scope_path')}
    record('scope_ref', 'owner_scope_path', {'owner_scope_path': ref('scope_path')})
    record('governed_scope_ref', 'representation_kind representation_identity owner_scope_path', qualified)
    record('execution_subject_ref', 'representation_kind representation_identity owner_scope_path subject_kind subject_id execution_id', dict(qualified, subject_kind=enum('CARD', 'CORE_OPERATION', 'VECTOR_DATAFLOW_OPERATION')))
    for representation, subject in (('SEMANTIC_IR', 'CARD'), ('QSOL_CORE', 'CORE_OPERATION'), ('VECTOR_DATAFLOW_IR', 'VECTOR_DATAFLOW_OPERATION')):
        conditions('execution_subject_ref', when('representation_kind', representation, properties={'subject_kind': {'const': subject}}))
    record('effect_requirement_ref', 'representation_kind representation_identity owner_scope_path declared_effect_id', qualified)
    record('machinery_requirement_ref', 'representation_kind representation_identity owner_scope_path machinery_requirement_id', qualified)
    record('local_machinery_requirement_ref', 'owner_scope_path machinery_requirement_id', {'owner_scope_path': ref('scope_path')})
    record('result_binding_ref', 'representation_kind representation_identity owner_scope_path binding_id', dict(qualified, owner_scope_path=ref('binding_owner_path')))
    record('operation_ref', 'representation_kind representation_identity owner_scope_path operation_id', qualified)
    record('initiating_scope_ref', 'scope_kind scope_id', {'scope_kind': enum('RUN', 'DECK_EXECUTION')})
    record('source_binding_ref', 'owner_scope_path binding_id source_card_id?', {'owner_scope_path': ref('binding_owner_path')})
    record('lower_binding_ref', 'owner_scope_path binding_id', {'owner_scope_path': ref('binding_owner_path')})
    record('sequencing_endpoint', 'endpoint_kind owner_scope_path endpoint_id', {'owner_scope_path': ref('scope_path')})
    record('edge_ref', 'representation_kind representation_identity owner_scope_path constraint_kind predecessor_endpoint_ref successor_endpoint_ref edge_hash', dict(qualified, constraint_kind=enum('SOURCE_ORDER','EFFECT_ORDER','FAILURE_ORDER'), predecessor_endpoint_ref=ref('sequencing_endpoint'), successor_endpoint_ref=ref('sequencing_endpoint')))
    defs['sequencing_endpoint']['description'] = 'Typed endpoint shape only. Recognized kinds, exact ownership, permitted edges and applicability require a frozen representation-specific validator; no lower-representation namespace is frozen here.'
    defs['edge_ref']['description'] = 'Directed source/lower edge reference. The containing boundary supplies representation identities; hash agreement and edge preservation are cross-record checks.'
    # Reuse the frozen canonical shapes without remote schema resolution.
    canonical = json.loads((ROOT / 'spec/canonical-model.schema.json').read_text())['$defs']
    def canonical_ref(name):
        target = 'canonical_' + name
        if target not in defs:
            defs[target] = {}
            def rewrite(value):
                if isinstance(value, dict):
                    if '$ref' in value: return canonical_ref(value['$ref'].split('/')[-1])
                    return {key: rewrite(child) for key, child in value.items()}
                if isinstance(value, list): return [rewrite(child) for child in value]
                return value
            defs[target] = rewrite(copy.deepcopy(canonical[name]))
        return ref(target)
    numeric = canonical_ref('numericContract')
    partition = obj({'contract_id':ref('identity'), 'version':ref('identity'), 'definition_hash':ref('identity')})
    record('representation_record', 'representation_kind representation_identity format content', {'representation_kind':ref('representation_kind'), 'content':ref('payload')})
    record('deck_identity', 'deck_id owner_scope_path', {'owner_scope_path':ref('scope_path')})
    record('card_identity', 'card_id owner_scope_path', {'owner_scope_path':ref('scope_path')})
    record('source_trace', 'source_hash spec_version run_id? job_id deck_identities[] card_identities[] source_location?', {'deck_identities':array(ref('deck_identity')), 'card_identities':array(ref('card_identity')), 'source_location':canonical_ref('sourceLocation')})
    record('epistemic_class_binding', 'epistemic_class_binding_id representation_kind representation_identity owner_scope_path subject_kind subject_id semantic_class source_epistemic_class_binding_ids[]? mapping_rule_id?', dict(qualified,semantic_class=ref('semantic_class')))
    conditions('epistemic_class_binding', when('representation_kind', 'SEMANTIC_IR', properties={'subject_kind': {'const': 'CARD'}}))
    defs['epistemic_class_binding']['properties']['semantic_class'] = {'allOf': [ref('semantic_class'), {'not': {'const': 'UNCLASSIFIED'}}]}
    record('effect_requirement', 'representation_kind representation_identity owner_scope_path declared_effect_id card_id? operation_id? effect_kind required_capabilities[]', qualified)
    conditions('effect_requirement', when('representation_kind', 'SEMANTIC_IR', ('card_id',), forbidden=('operation_id',)))
    record('machinery_requirement', 'representation_kind representation_identity owner_scope_path machinery_requirement_id source_card_ids[]? source_operation_ids[]? target_selector_or_class required_capabilities[]', qualified)
    record('result_determinism_binding', 'owner_scope_path source_card_ids[] requested_result_determinism', {'owner_scope_path':ref('scope_path')})
    record('numeric_contract_binding', 'owner_scope_path source_card_ids[] numeric_contract_id numeric_contract_hash', {'owner_scope_path':ref('scope_path')})
    record('randomness_contract_binding', 'owner_scope_path source_card_ids[] requested_randomness_mode', {'owner_scope_path':ref('scope_path'), 'requested_randomness_mode':ref('randomness_mode')})
    record('failure_behavior_binding', 'failure_behavior_binding_id governed_scope_ref source_card_ids[] requested_failure_behavior_id effective_failure_behavior_id mapping_or_transition_rule_id? transition_evidence_id?', {'governed_scope_ref':ref('governed_scope_ref')})
    defs['failure_behavior_binding']['dependentRequired'] = {'transition_evidence_id': ['mapping_or_transition_rule_id']}
    record('extension_component', 'component_kind component_id component_version component_content_hash component_location?')
    record('extension_source_ref', 'representation_kind ir_hash owner_scope_path requirement_hash', {'representation_kind':ref('representation_kind'), 'owner_scope_path':ref('scope_path')})
    record('extension_scope_ref', 'representation_kind ir_hash owner_scope_path', {'representation_kind':ref('representation_kind'), 'owner_scope_path':ref('scope_path')})
    record('resolved_extension', 'resolved_extension_id profile_name resolved_version contract_id contract_hash implementation_components[] source_requirement_refs[] governing_scope_refs[] source_card_ids[]', {'implementation_components':array(ref('extension_component'),1), 'source_requirement_refs':array(ref('extension_source_ref'),1), 'governing_scope_refs':array(ref('extension_scope_ref'),1)})
    record('source_qualifier_ref', 'representation_kind representation_identity owner_scope_path qualifier_key_path[] qualifier_value_hash', dict(qualified, qualifier_key_path=array(ref('identity'),1,unique=False)))
    record('core_result_ref', 'owner_scope_path result_kind result_key_or_id result_value_hash?', {'owner_scope_path':ref('scope_path')})
    record('qualifier_lowering_decision', 'qualifier_lowering_decision_id source_qualifier_ref disposition core_scope_refs[] resulting_core_refs[] resolved_extension_ids[]? lowering_rule_id? validation_evidence_id?', {'source_qualifier_ref':ref('source_qualifier_ref'), 'disposition':enum('PRESERVED','CONSUMED'), 'core_scope_refs':array(ref('scope_ref'),1), 'resulting_core_refs':array(ref('core_result_ref'),1)})
    conditions('qualifier_lowering_decision',when('disposition','CONSUMED',('lowering_rule_id','validation_evidence_id')))
    record('source_fact_ref', 'representation_kind representation_identity owner_scope_path fact_kind fact_key_or_id fact_value_hash', qualified)
    record('core_fact_ref', 'owner_scope_path fact_kind fact_key_or_id fact_value_hash?', {'owner_scope_path':ref('scope_path')})
    record('type_unit_lowering_decision', 'type_unit_lowering_decision_id source_fact_refs[] core_fact_refs[] disposition lowering_rule_id? validation_evidence_id?', {'source_fact_refs':array(ref('source_fact_ref'),1), 'core_fact_refs':array(ref('core_fact_ref'),1), 'disposition':enum('PRESERVED','NORMALIZED','ERASED')})
    for disposition in ['NORMALIZED','ERASED']: conditions('type_unit_lowering_decision',when('disposition',disposition,('lowering_rule_id','validation_evidence_id')))
    record('sequencing_mapping', 'sequencing_mapping_id source_edge_refs[] lower_edge_refs[] mapping_rule_id? validation_evidence_id?', {'source_edge_refs':array(ref('edge_ref'),1), 'lower_edge_refs':array(ref('edge_ref'),1)})
    record('result_binding_map', 'mapping_group_id source_bindings[] lower_bindings[] mapping_rule_id?', {'source_bindings':array(ref('source_binding_ref'),1), 'lower_bindings':array(ref('lower_binding_ref'),1)})
    conditions('result_binding_map',{'if':{'properties':{'source_bindings':{'minItems':2}}},'then':{'required':['mapping_rule_id']}})
    record('numeric_contract_ref','numeric_contract_id numeric_contract_hash')
    transition = 'transition_decision_id? transition_authorized_by? transition_evidence_id?'
    record('first_scope_mapping', 'source_scope_ref core_scope_refs[] source_card_ids[] mapping_rule_id '+transition, {'source_scope_ref':ref('scope_ref'), 'core_scope_refs':array(ref('scope_ref'),1)})
    record('first_numeric_mapping', 'source_scope_ref core_scope_refs[] source_card_ids[] mapping_rule_id requested_numeric_contract_ref? effective_numeric_contract_ref? '+transition, {'source_scope_ref':ref('scope_ref'), 'core_scope_refs':array(ref('scope_ref'),1), 'requested_numeric_contract_ref':ref('numeric_contract_ref'), 'effective_numeric_contract_ref':ref('numeric_contract_ref')})
    record('first_extension_mapping', 'source_scope_ref core_scope_refs[] source_card_ids[] resolved_extension_ids[] profile_name resolved_version_or_content_identity contract_id_or_hash? mapping_rule_id', {'source_scope_ref':ref('scope_ref'), 'core_scope_refs':array(ref('scope_ref'),1), 'resolved_extension_ids':array(minimum=1)})
    record('first_machinery_mapping', 'mapping_group_id source_scope_refs[] core_scope_refs[] source_machinery_requirement_refs[] lower_machinery_requirement_refs[] source_card_ids[] mapping_rule_id', {'source_scope_refs':array(ref('scope_ref'),1), 'core_scope_refs':array(ref('scope_ref'),1), 'source_machinery_requirement_refs':array(ref('local_machinery_requirement_ref'),1), 'lower_machinery_requirement_refs':array(ref('local_machinery_requirement_ref'),1)})
    second_fields = 'core_scope_refs[] vector_dataflow_scope_refs[] source_card_ids[] mapping_rule_id backend_unit_ids[]? '
    second_types = {'core_scope_refs':array(ref('scope_ref'),1), 'vector_dataflow_scope_refs':array(ref('scope_ref'),1)}
    record('second_scope_mapping',second_fields+transition,second_types)
    record('second_numeric_mapping',second_fields+'requested_numeric_contract_ref? effective_numeric_contract_ref? '+transition,dict(second_types,requested_numeric_contract_ref=ref('numeric_contract_ref'),effective_numeric_contract_ref=ref('numeric_contract_ref')))
    record('second_extension_mapping',second_fields+'profile_name resolved_version_or_content_identity contract_id_or_hash? resolved_extension_ids[]',dict(second_types,resolved_extension_ids=array(minimum=1)))
    record('second_machinery_mapping',second_fields+'source_machinery_requirement_refs[] lower_machinery_requirement_refs[]',dict(second_types,source_machinery_requirement_refs=array(ref('local_machinery_requirement_ref'),1),lower_machinery_requirement_refs=array(ref('local_machinery_requirement_ref'),1)))
    for name in ('first_scope_mapping', 'first_numeric_mapping', 'second_scope_mapping', 'second_numeric_mapping'):
        co_present(name, ('transition_decision_id', 'transition_authorized_by', 'transition_evidence_id'))
    for name in ('first_numeric_mapping', 'second_numeric_mapping'):
        co_present(name, ('requested_numeric_contract_ref', 'effective_numeric_contract_ref'))
        conditions(name, {'if': {'required': ['transition_decision_id']},
                          'then': {'required': ['requested_numeric_contract_ref', 'effective_numeric_contract_ref']}})
    first_arrays = {'result_binding_map':'result_binding_map', 'sequencing_constraint_lowering_decisions':'sequencing_mapping','type_unit_lowering_decisions':'type_unit_lowering_decision','resolved_extensions':'resolved_extension','extension_requirement_lowering_decisions':'first_extension_mapping','qualifier_lowering_decisions':'qualifier_lowering_decision','machinery_requirement_lowering_decisions':'first_machinery_mapping','result_determinism_lowering_decisions':'first_scope_mapping','numeric_contract_lowering_decisions':'first_numeric_mapping','randomness_lowering_decisions':'first_scope_mapping','failure_behavior_lowering_decisions':'first_scope_mapping'}
    record('semantic_to_core','semantic_ir_hash semantic_to_core_spec_version semantic_to_core_implementation_version core_ir_hash '+' '.join(k+'[]' for k in first_arrays)+' lowering_diagnostics[]',{k:array(ref(v)) for k,v in first_arrays.items()})
    second_arrays = {'result_binding_map':'result_binding_map','sequencing_constraint_mapping_decisions':'sequencing_mapping','extension_requirement_mapping_decisions':'second_extension_mapping','machinery_requirement_mapping_decisions':'second_machinery_mapping','core_to_vector_result_determinism_mapping_decisions':'second_scope_mapping','core_to_vector_numeric_contract_mapping_decisions':'second_numeric_mapping','core_to_vector_randomness_mapping_decisions':'second_scope_mapping','failure_behavior_mapping_decisions':'second_scope_mapping'}
    record('core_to_vector','core_ir_hash vector_dataflow_spec_version vector_dataflow_implementation_version vector_dataflow_ir_hash '+' '.join(k+'[]' for k in second_arrays)+' vector_dataflow_lowering_diagnostics[]',{k:array(ref(v)) for k,v in second_arrays.items()})
    record('backend_selection_scope','backend_selection_scope_id governed_scope_ref source_card_ids[] backend_unit_id? selection_decision_ids[] final_selection_decision_id?',{'governed_scope_ref':ref('governed_scope_ref')})
    record('backend_selection_decision','backend_selection_decision_id backend_selection_scope_id decision_sequence_index requested_target selected_backend selected_backend_version? selected_backend_implementation_identity? target_architecture? device? selection_policy_id? selection_policy_version? selection_tuning_id? selection_tuning_hash? predecessor_selection_decision_id? fallback_rule_id? fallback_evidence_id? machinery_authorization_record_ids[]? decision_status')
    co_present('backend_selection_decision', ('predecessor_selection_decision_id', 'fallback_rule_id', 'fallback_evidence_id'))
    authorization = 'required_capabilities[] granted_capabilities[] denied_capabilities[] capability_policy_id capability_policy_version authorization_status authorization_sequence_index?'
    record('machinery_authorization_record','machinery_authorization_record_id backend_selection_scope_id backend_selection_decision_id source_card_ids[]? machinery_requirement_refs[] '+authorization,{'machinery_requirement_refs':array(ref('machinery_requirement_ref'),1),'authorization_status':ref('authorization_status')})
    record('machinery_use_record','machinery_use_record_id backend_selection_scope_id backend_selection_decision_id backend_unit_id? generated_artifact_ids[] execution_subject_refs[] source_card_ids[]? card_execution_ids[]? initiating_scope_ref? machinery_authorization_record_ids[] output_ids[] protected_use_start_sequence_index protected_use_stop_sequence_index?',{'execution_subject_refs':array(ref('execution_subject_ref')),'initiating_scope_ref':ref('initiating_scope_ref')})
    conditions('machinery_use_record',{'if':{'properties':{'execution_subject_refs':{'maxItems':0}}},'then':{'required':['initiating_scope_ref']},'else':{'not':{'required':['initiating_scope_ref']}}})
    record('generated_artifact','generated_artifact_id artifact_kind artifact_hash backend_unit_id backend_selection_scope_id backend_selection_decision_id source_card_ids[]? optimized_ir_hash? optimization_record_ids[]? direct_producer_toolchain_invocation_id toolchain_invocation_chain_ids[] artifact_location?',{'toolchain_invocation_chain_ids':array(minimum=1)})
    conditions('generated_artifact', {'if': {'required': ['optimized_ir_hash']},
        'then': {'required': ['optimization_record_ids'], 'properties': {'optimization_record_ids': {'minItems': 1}}}})
    co_present('generated_artifact', ('optimized_ir_hash', 'optimization_record_ids'))
    defs['generated_artifact']['properties']['optimization_record_ids']['minItems'] = 1
    record('argument','argument_index argument_kind argument_text input_id? generated_artifact_id? ir_hash? output_generated_artifact_id?',{'argument_text':{'type':'string'},'argument_kind':enum('LITERAL','INPUT','GENERATED_ARTIFACT_INPUT','IR_INPUT','OUTPUT_GENERATED_ARTIFACT','SEPARATOR','RESPONSE_FILE')})
    argument_refs = ('input_id', 'generated_artifact_id', 'ir_hash', 'output_generated_artifact_id')
    for kind, key in [('INPUT','input_id'),('GENERATED_ARTIFACT_INPUT','generated_artifact_id'),('IR_INPUT','ir_hash'),('OUTPUT_GENERATED_ARTIFACT','output_generated_artifact_id'),('RESPONSE_FILE','input_id'),('LITERAL',None),('SEPARATOR',None)]:
        conditions('argument', when('argument_kind', kind, (key,) if key else (),
                                   tuple(field for field in argument_refs if field != key)))
    record('toolchain_invocation','toolchain_invocation_id invocation_sequence_index invocation_kind tool_name material_tool_identity target_or_architecture? abi? flags[] argument_vector[] environment_config_hash? input_ir_hashes[] input_ids[] input_generated_artifact_ids[]? output_generated_artifact_ids[] backend_unit_id? backend_selection_scope_id?',{'argument_vector':array(ref('argument'),unique=False)})
    defs['toolchain_invocation']['properties']['argument_vector']['description'] = ('Exact ordered occurrences: argument_index must equal the zero-based array position. Unbounded cross-value equality is enforced by tools.check_trace.validate_structure, not raw JSON Schema. Structural success does not establish execution acceptance.')
    record('environment_entry','name value_identity')
    record('toolchain_environment_config','environment_config_hash canonical_environment_entries[] working_directory_identity? config_input_ids[] reproducibility_input_ids[] locale_or_timezone_identity? record_content? record_location?',{'canonical_environment_entries':array(ref('environment_entry')),'record_content':ref('payload')})
    record('legality_witness','legality_witness_id witness_kind validation_evidence_id')
    record('optimization_record','optimization_record_id source_card_ids[] backend_unit_id? reference_ir_hash optimized_ir_hash transformation_sequence[] legality_witnesses[] vectorization_decisions[]? fusion_decisions[]? memory_placement_decisions[]? target_context_measurements[]? resource_model_assumptions[]? generated_artifact_ids[]',{'legality_witnesses':array(ref('legality_witness')), 'transformation_sequence':array(unique=False)})
    record('rule_record','rule_id rule_kind authority_kind authority_id authority_version_or_hash rule_content_hash rule_content? rule_location?',{'rule_content':ref('payload')})
    record('validation_evidence','validation_evidence_id rule_id subject_kind subject_id evaluated_context_hash verifier_identity outcome validation_sequence_index application_sequence_index? related_evidence_ids[]? evidence_hash evidence_content? evidence_location?',{'evidence_content':ref('payload'),'outcome':enum('PASS','FAIL','UNAVAILABLE')})
    for outcome in ('FAIL', 'UNAVAILABLE'):
        conditions('validation_evidence', when('outcome', outcome, forbidden=('application_sequence_index',)))
    for name,payload,location in [('rule_record','rule_content','rule_location'),('validation_evidence','evidence_content','evidence_location'),('toolchain_environment_config','record_content','record_location')]:
        defs[name]['anyOf']=[{'required':[payload]},{'required':[location]}]
    record('result_determinism_scope','result_determinism_scope_id governed_scope_ref source_card_ids[] requested_result_determinism effective_result_determinism transition_authorized_by? transition_evidence_id? backend_unit_id?',{'governed_scope_ref':ref('governed_scope_ref')})
    record('numeric_execution_scope','numeric_scope_id governed_scope_ref source_card_ids[] numeric_contract_id numeric_contract_hash material_numeric_mode backend_unit_id?',{'governed_scope_ref':ref('governed_scope_ref'),'material_numeric_mode':numeric})
    record('randomness_execution_scope','randomness_scope_id governed_scope_ref source_card_ids[] requested_randomness_mode effective_randomness_mode transition_authorized_by? transition_evidence_id? rng_algorithm? rng_version? seed? stream_id? parallel_partitioning? entropy_effect_attempt_ids[]? entropy_input_ids[]? backend_unit_id?',{'governed_scope_ref':ref('governed_scope_ref'),'requested_randomness_mode':ref('randomness_mode'),'effective_randomness_mode':ref('randomness_mode'),'parallel_partitioning':partition})
    conditions('randomness_execution_scope',when('effective_randomness_mode','SEEDED',('rng_algorithm','rng_version','seed','stream_id')),when('effective_randomness_mode','EXTERNAL-ENTROPY',('entropy_effect_attempt_ids',),properties={'entropy_effect_attempt_ids':array(minimum=1)}))
    for name in ('result_determinism_scope', 'randomness_execution_scope'):
        co_present(name, ('transition_authorized_by', 'transition_evidence_id'))
    # The randomness discriminator is a finite closed set, so unequal modes
    # have an expressible local transition obligation without comparing hashes.
    for requested in defs['randomness_mode']['enum']:
        for effective in defs['randomness_mode']['enum']:
            if requested != effective:
                conditions('randomness_execution_scope', {
                    'if': {'properties': {'requested_randomness_mode': {'const': requested},
                                          'effective_randomness_mode': {'const': effective}},
                           'required': ['requested_randomness_mode', 'effective_randomness_mode']},
                    'then': {'required': ['transition_authorized_by', 'transition_evidence_id']}})
    causes = 'governing_control_decision_id? governing_failure_record_id? governing_skip_rule_id? skip_verification_evidence_id? failure_record_id?'
    record('deck_execution','deck_execution_id deck_id deck_status card_execution_ids[] execution_order_index? governing_failure_record_id? failure_record_id?',{'deck_status':ref('execution_status')})
    record('card_execution','card_execution_id deck_execution_id card_id card_status input_ids[] cache_reuse_record_ids[]? execution_order_index? '+causes,{'card_status':ref('execution_status')})
    record('operation_execution','operation_execution_id operation_ref operation_kind operation_status input_ids[] cache_reuse_record_ids[]? execution_order_index? '+causes+' source_card_ids[]? source_card_execution_ids[]?',{'operation_ref':ref('operation_ref'),'operation_status':ref('identity')})
    for name, status in (('deck_execution', 'deck_status'), ('card_execution', 'card_status'), ('operation_execution', 'operation_status')):
        conditions(name, when(status, 'FAILED', ('failure_record_id',)))
    for name, status in (('card_execution', 'card_status'), ('operation_execution', 'operation_status')):
        conditions(name, when(status, 'EXPLICIT_SKIP', ('governing_skip_rule_id', 'skip_verification_evidence_id')))
    record('control_decision','control_decision_id card_execution_id? operation_execution_id? control_kind decision sequence_index? backend_detail?')
    record('failure_record','failure_record_id failing_scope_kind failing_scope_id failure_behavior_binding_ids[] result_determinism_scope_ids[] numeric_scope_ids[] randomness_scope_ids[] effect_accounting_failure_record_ids[]? failure_class failure_stage failure_card_id? failure_card_execution_id? operation_execution_id? deck_execution_id? sequence_index? backend_detail?')
    record('input','input_id input_kind canonical_value? content_hash? artifact_id_or_version? location? media_or_schema_type? source_card_ids[]? consumer_execution_refs[] consumer_card_execution_ids[]? consumer_scope_refs[]? effect_attempt_ids[]',{'canonical_value':ref('payload'),'consumer_execution_refs':array(ref('execution_subject_ref')),'consumer_scope_refs':array(ref('initiating_scope_ref'))})
    defs['input']['anyOf']=[{'required':[key]} for key in ['canonical_value','content_hash','artifact_id_or_version']]
    effect_refs = {'effect_requirement_ref':ref('effect_requirement_ref'),'execution_subject_ref':ref('execution_subject_ref')}
    record('effect_authorization_record','effect_authorization_record_id effect_attempt_id effect_requirement_ref execution_subject_ref card_id? card_execution_id? '+authorization,dict(effect_refs,authorization_status=ref('authorization_status')))
    record('effect_attempt','effect_attempt_id effect_requirement_ref execution_subject_ref card_id? card_execution_id? effect_kind required_capabilities[] effect_authorization_record_id sequence_index effect_begin_sequence_index? effect_end_sequence_index? completion_state termination_known? backend_detail? acquired_input_ids[] observable_output_ids[] external_tool_ids[]',dict(effect_refs,completion_state=enum('NOT_STARTED','COMPLETED','ABORTED_CLEAN','PARTIAL','UNKNOWN'),termination_known={'type':'boolean'}))
    for state in ['COMPLETED','ABORTED_CLEAN','PARTIAL']: conditions('effect_attempt',when('completion_state',state,('effect_begin_sequence_index','effect_end_sequence_index'),forbidden=('termination_known',)))
    conditions('effect_attempt',when('completion_state','UNKNOWN',('effect_begin_sequence_index','termination_known')),when('completion_state','NOT_STARTED',forbidden=('effect_begin_sequence_index','effect_end_sequence_index','termination_known'),properties={key:{'maxItems':0} for key in ['acquired_input_ids','observable_output_ids','external_tool_ids']}))
    conditions('effect_attempt', when('termination_known', True, ('effect_end_sequence_index',)),
               when('termination_known', False, forbidden=('effect_end_sequence_index',)))
    conditions('effect_attempt', when('completion_state', 'ABORTED_CLEAN', properties={'observable_output_ids': {'maxItems': 0}}))
    record('effect_non_attempt_record','effect_non_attempt_record_id effect_requirement_ref execution_subject_ref card_id? card_execution_id? effect_kind non_attempt_reason governing_control_decision_id? governing_failure_record_id? governing_skip_rule_id? skip_verification_evidence_id? backend_detail?',effect_refs)
    record('effect_accounting_failure_record','effect_accounting_failure_record_id failure_record_id effect_requirement_ref execution_subject_ref accounting_failure_kind detected_sequence_index? backend_detail?',dict(effect_refs,accounting_failure_kind=enum('BACKEND_OMISSION_DETECTED','ACCOUNTING_INCOMPLETE')))
    record('external_tool','external_tool_id tool_kind tool_name_or_service material_identity_status material_identity_kind? material_identity_value? endpoint_or_location? source_card_ids[]? effect_attempt_ids[] output_ids[]',{'material_identity_status':enum('IDENTIFIED','UNAVAILABLE')})
    conditions('external_tool',when('material_identity_status','IDENTIFIED',('material_identity_kind','material_identity_value')))
    conditions('external_tool', when('material_identity_status', 'UNAVAILABLE', forbidden=('material_identity_kind', 'material_identity_value')))
    defs['external_tool']['anyOf']=[{'properties':{key:{'minItems':1}}} for key in ['effect_attempt_ids','output_ids']]
    record('cache_reuse_record','cache_reuse_record_id classification execution_subject_refs[] source_card_ids[]? card_execution_ids[]? reused_computation_id? cache_key_hash? cached_artifact_hash? cached_output_id? cache_producer_run_id? legality_rule_id? verification_evidence_id? material_cache_identity_hash',{'classification':enum('COLD_EXECUTION','VERIFIED_REUSE','UNVERIFIED_HIT'),'execution_subject_refs':array(ref('execution_subject_ref'),1)})
    conditions('cache_reuse_record',when('classification','VERIFIED_REUSE',('legality_rule_id','verification_evidence_id')))
    record('evidence_status','evidence_class status evidence_rule_id evidence_validation_id',{'evidence_class':enum('TEST','VALIDATION','PROOF')})
    record('output','output_id result_binding_ref? artifact_hash artifact_location? semantic_class epistemic_class_binding_ids[] status producer_execution_refs[] producer_card_ids[]? producer_card_execution_ids[]? input_ids[] effect_attempt_ids[]? external_tool_ids[] backend_selection_scope_ids[] machinery_use_record_ids[] generated_artifact_ids[]? result_determinism_scope_ids[] numeric_scope_ids[] randomness_scope_ids[] failure_behavior_binding_ids[] cache_reuse_record_ids[]? evidence_status? publication_sequence_index?',{'result_binding_ref':ref('result_binding_ref'),'semantic_class':ref('semantic_class'),'producer_execution_refs':array(ref('execution_subject_ref'),1),'evidence_status':ref('evidence_status')})
    conditions('output',when('semantic_class','UNCLASSIFIED',forbidden=('evidence_status',),properties={'epistemic_class_binding_ids':{'maxItems':0}}))
    for cls in ['TEST','VALIDATION','PROOF']: conditions('output',when('semantic_class',cls,('evidence_status',),properties={'evidence_status':{'properties':{'evidence_class':{'const':cls}}}}))
    conditions('output', {'if': {'properties': {'semantic_class': {'not': enum('TEST', 'VALIDATION', 'PROOF')}}, 'required': ['semantic_class']},
        'then': {'not': {'required': ['evidence_status']}}})
    for name in ('effect_authorization_record', 'machinery_authorization_record'):
        conditions(name, when('authorization_status', 'GRANTED', properties={'denied_capabilities': {'maxItems': 0}}))
    for name, status in (('card_execution', 'card_status'), ('operation_execution', 'operation_status'), ('effect_non_attempt_record', 'non_attempt_reason')):
        co_present(name, ('governing_skip_rule_id', 'skip_verification_evidence_id'))
        conditions(name, when(status, 'EXPLICIT_SKIP', ('governing_skip_rule_id', 'skip_verification_evidence_id')),
                   when(status, 'UNTAKEN_BRANCH', ('governing_control_decision_id',)))
        if name != 'effect_non_attempt_record':
            conditions(name, when(status, 'FAIL_STOP_BLOCKED', ('governing_failure_record_id',)))
    conditions('effect_non_attempt_record', when('non_attempt_reason', 'PRIOR_FAIL_STOP', ('governing_failure_record_id',)))
    conditions('deck_execution', when('deck_status', 'FAIL_STOP_BLOCKED', ('governing_failure_record_id',)))
    conditions('failure_record', when('failing_scope_kind', 'CARD_EXECUTION', ('failure_card_id', 'failure_card_execution_id')),
               when('failing_scope_kind', 'CORE_OPERATION_EXECUTION', ('operation_execution_id',)))
    # No frozen composition rule is admitted for multiple non-reach causes.
    exactly_one_cause = {'oneOf': [
        {'required': ['governing_control_decision_id']},
        {'required': ['governing_failure_record_id']},
        {'required': ['governing_skip_rule_id', 'skip_verification_evidence_id']}]}
    for name, status in (('card_execution', 'card_status'), ('operation_execution', 'operation_status'), ('effect_non_attempt_record', 'non_attempt_reason')):
        defs[name]['description'] = ('This bounded structural profile admits one typed non-reach cause only. Multiple-cause composition requires a future frozen composition contract and is not represented here; contextual resolution must still verify the cause.')
        for value in ('NOT_REACHED', 'SUBJECT_NOT_REACHED', 'CARD_NOT_REACHED', 'OPERATION_NOT_REACHED', 'UNTAKEN_BRANCH', 'FAIL_STOP_BLOCKED', 'EXPLICIT_SKIP', 'PRIOR_FAIL_STOP'):
            conditions(name, {'if': {'properties': {status: {'const': value}}, 'required': [status]}, 'then': exactly_one_cause})
        if name != 'effect_non_attempt_record':
            for value in ('UNTAKEN', 'SKIPPED', 'BLOCKED'):
                conditions(name, {'if': {'properties': {status: {'const': value}}, 'required': [status]}, 'then': exactly_one_cause})
            for value in ('NOT_REACHED', 'SUBJECT_NOT_REACHED', 'CARD_NOT_REACHED', 'OPERATION_NOT_REACHED', 'UNTAKEN_BRANCH', 'UNTAKEN', 'FAIL_STOP_BLOCKED', 'BLOCKED', 'EXPLICIT_SKIP', 'SKIPPED', 'NOT_STARTED'):
                conditions(name, when(status, value, forbidden=('failure_record_id',)))
    co_present('failure_record', ('failure_card_id', 'failure_card_execution_id'))
    for kind in ('JOB', 'RUN', 'BACKEND_SELECTION_SCOPE', 'LOWERING'):
        conditions('failure_record', when('failing_scope_kind', kind, forbidden=('failure_card_id', 'failure_card_execution_id')))
    defs['failure_record']['description'] = ('CARD culprit projections are paired and forbidden for known pre-execution JOB/RUN/selection/lowering failures. Lower-operation and DECK scopes may retain a paired CARD culprit only when contextual lineage and causation are independently verified; shape validity does not establish that relation.')
    for name in ('effect_authorization_record', 'effect_attempt', 'effect_non_attempt_record'):
        co_present(name, ('card_id', 'card_execution_id'))
    for name, fields in (('output', ('producer_card_ids', 'producer_card_execution_ids')),
                         ('machinery_use_record', ('source_card_ids', 'card_execution_ids')),
                         ('cache_reuse_record', ('source_card_ids', 'card_execution_ids'))):
        co_present(name, fields)
        # Output and machinery-use projections explicitly forbid empty lineage placeholders.
        if name in ('output', 'machinery_use_record'):
            for field in fields:
                defs[name]['properties'][field]['minItems'] = 1
    for name, rule in (('qualifier_lowering_decision', 'lowering_rule_id'), ('type_unit_lowering_decision', 'lowering_rule_id'), ('sequencing_mapping', 'mapping_rule_id')):
        defs[name].setdefault('dependentRequired', {})['validation_evidence_id'] = [rule]
    semantic_card_subject = {'properties': {'representation_kind': {'const': 'SEMANTIC_IR'}, 'subject_kind': {'const': 'CARD'}},
                             'required': ['representation_kind', 'subject_kind']}
    for name in ('effect_authorization_record', 'effect_attempt', 'effect_non_attempt_record'):
        conditions(name, {'if': {'properties': {'execution_subject_ref': semantic_card_subject}, 'required': ['execution_subject_ref']},
                          'then': {'required': ['card_id', 'card_execution_id']}})
    for name, refs, projections in (
            ('output', 'producer_execution_refs', ('producer_card_ids', 'producer_card_execution_ids')),
            ('machinery_use_record', 'execution_subject_refs', ('source_card_ids', 'card_execution_ids'))):
        conditions(name, {'if': {'properties': {refs: {'contains': semantic_card_subject}}, 'required': [refs]},
                          'then': {'required': list(projections), 'properties': {field: {'minItems': 1} for field in projections}}})
    conditions('output', {'if': {'properties': {'semantic_class': {'not': {'const': 'UNCLASSIFIED'}}}, 'required': ['semantic_class']},
                          'then': {'properties': {'epistemic_class_binding_ids': {'minItems': 1}}}})
    ledgers = {
        'operation_executions':'operation_execution','epistemic_class_bindings':'epistemic_class_binding','control_decisions':'control_decision','failure_records':'failure_record',
        'backend_selection_scopes':'backend_selection_scope','backend_selection_decisions':'backend_selection_decision','machinery_requirements':'machinery_requirement','machinery_authorization_records':'machinery_authorization_record','machinery_use_records':'machinery_use_record',
        'result_determinism_scopes':'result_determinism_scope','numeric_execution_scopes':'numeric_execution_scope','randomness_execution_scopes':'randomness_execution_scope','failure_behavior_bindings':'failure_behavior_binding','rule_records':'rule_record','validation_evidence':'validation_evidence','inputs':'input','resolved_extensions':'resolved_extension',
        'effect_requirements':'effect_requirement','effect_authorization_records':'effect_authorization_record','effect_attempts':'effect_attempt','effect_non_attempt_records':'effect_non_attempt_record','effect_accounting_failure_records':'effect_accounting_failure_record','cache_reuse_records':'cache_reuse_record','external_tool_versions':'external_tool','generated_artifacts':'generated_artifact','toolchain_environment_configs':'toolchain_environment_config','toolchain_invocations':'toolchain_invocation','optimization_provenance':'optimization_record','outputs':'output'}
    root = {'trace_version':{'const':'1.0.0'},'receipt_kind':enum('SYNTHETIC_CONFORMANCE_RECEIPT','EXECUTION_TRACE'),'run_id':ref('identity'),'input_representation':ref('representation_kind'),'input_representation_identity':ref('identity'),'execution_status':ref('execution_status'),'event_order_domain':{'const':'RUN_SEQUENCE'},'representation_records':array(ref('representation_record'),1)}
    root.update({key:array(ref(value)) for key,value in ledgers.items()})
    required = list(root)
    root.update({'job_id':ref('identity'),'job_status':ref('execution_status'),'deck_executions':array(ref('deck_execution')),'card_executions':array(ref('card_execution')),'source_trace':ref('source_trace'),'semantic_ir_hash':ref('identity'),'core_ir_hash':ref('identity'),'vector_dataflow_ir_hash':ref('identity'),'semantic_to_core':ref('semantic_to_core'),'core_to_vector':ref('core_to_vector'),'dependency_graph_hash':ref('identity'),'morph_version':ref('identity'),'optimization_profile':ref('identity'),'primary_failure_record_id':ref('identity'),'observable_output_ids':array(),'result_determinism_bindings':array(ref('result_determinism_binding')),'numeric_contract_bindings':array(ref('numeric_contract_binding')),'randomness_contract_bindings':array(ref('randomness_contract_binding')),'extension_requirements':array(canonical_ref('extension'))})
    for key in ['job_ids','deck_ids','card_ids','required_capabilities','granted_capabilities','denied_capabilities','capabilities_used','runtime_compiler_versions','vectorization_decisions','fusion_decisions','memory_placement_decisions']: root[key]=array()
    for key in ['capability_policy_id','capability_policy_version']: root[key]=ref('identity')
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://github.com/QSOLKCB/QSOL-MORPH/blob/main/spec/execution-trace.schema.json','title':'QSOL-MORPH PR5 structural trace envelope 1.0.0','description':'Closed structural provenance vocabulary. Schema validity does not authorize execution or prove operational, lowering, evidence, or research conformance. The reference validator accepts only its explicitly bounded synthetic receipt profile.','type':'object','properties':root,'required':required,'additionalProperties':False,'$defs':defs}
    schema['allOf']=[when('input_representation','SEMANTIC_IR',('job_id','job_status','semantic_ir_hash','deck_executions','card_executions'))]
    # array() marks ledger/reference inventories as sets. Containment/key paths,
    # argv, and the pass sequence are ordered occurrences and preserve repeats.
    # Reused canonical value/parameter shapes retain their own frozen semantics.
    return schema


def check_structural_smoke(schema):
    """Check multiplicity and typed endpoints without accepting future execution."""
    from jsonschema import Draft202012Validator
    Draft202012Validator.check_schema(schema)
    definitions = schema['$defs']

    def valid(fragment, value):
        checker = Draft202012Validator(dict(fragment, **{'$defs': definitions}))
        return checker.is_valid(value)

    repeated_scope = [{'scope_kind': 'REGION', 'scope_id': 'r'}] * 2
    checks = [
        (definitions['scope_path'], repeated_scope, True),
        (definitions['source_qualifier_ref']['properties']['qualifier_key_path'], ['x', 'x'], True),
        (definitions['optimization_record']['properties']['transformation_sequence'], ['pass:v1', 'pass:v1'], True),
        (definitions['toolchain_invocation']['properties']['argument_vector'],
         [{'argument_index': 0, 'argument_kind': 'LITERAL', 'argument_text': '-lfoo'},
          {'argument_index': 1, 'argument_kind': 'LITERAL', 'argument_text': '-lfoo'}], True),
        (definitions['output']['properties']['input_ids'], ['input-1', 'input-1'], False),
        (definitions['sequencing_endpoint'], {'endpoint_kind': 'DECLARED_EFFECT',
         'owner_scope_path': repeated_scope, 'endpoint_id': 'effect-1'}, True),
        (definitions['sequencing_endpoint'], {'endpoint_kind': 'DECLARED_EFFECT', 'owner_scope_path': [], 'endpoint_id': 'effect-1'}, False),
    ]
    for index, (fragment, value, expected) in enumerate(checks):
        if valid(fragment, value) != expected:
            raise RuntimeError(f'trace structural smoke case {index} failed')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    schema=build_schema()
    text=json.dumps(schema,indent=2,ensure_ascii=False)+'\n'
    if args.check:
        if not DESTINATION.exists() or DESTINATION.read_text()!=text:
            parser.exit(1,'execution-trace.schema.json differs from generator\n')
        check_structural_smoke(schema)
        print('Trace schema matches generator; ordered multiplicity and typed-endpoint smoke checks pass.')
    else:
        DESTINATION.write_text(text)
        print(DESTINATION)


if __name__=='__main__': main()
