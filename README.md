# QSOL-MORPH

**Deterministic code morphing for human–AI research computing.**

QSOL-MORPH is the proposed translation, optimization, and execution layer for the QSOL research-language architecture.

> **QSOL describes intent. QSOL-CORE defines meaning. QSOL-MORPH chooses machinery.**

The project aims to let humans and AI reason about one stable semantic program while allowing the implementation beneath it to change across CPUs, GPUs, compiler backends, operating environments, and future accelerators.

## Status

**Experimental / pre-alpha.**

The repository is specification-first and documentation-first. The language grammar, Semantic IR, QSOL-CORE instruction set, lowering contracts, extension profiles, and backend contracts remain provisional until later normative phases freeze them.

PR #1 establishes the architectural foundation. PR #2 is reserved for locking the first core invariants before executable implementation begins.

## Core architecture

```text
QSOL source / human-AI semantic layer
        ↓
Canonical Semantic IR
        ↓  Semantic-to-Core lowering
QSOL-CORE
        ↓  Core-to-Vector/Dataflow lowering
Full Vector/Dataflow IR
        ↓
QSOL-MORPH
        ↓
C / LLVM / Fortran / CUDA / HIP / VM / ...
```

Both lowering arrows are explicit contracts and independently provenance-bearing transformations. Backends consume the established lower pipeline rather than inventing private source semantics.

POSIX is intentionally **not** a mutually exclusive compiler backend. Process, stream, filesystem, environment, and signal behavior belongs in the composable `QX-POSIX` execution profile.

MIDI 2.0 and formal-tool mappings are also extension/adapter concerns, not machinery backends. They belong behind versioned contracts such as `QX-MIDI` and `QX-PROVE`.

## Canonical semantic model

The proposed structural hierarchy is:

```text
JOB [JOB ID]
 ├── SCOPED DETERMINISM / NUMERIC / RANDOMNESS CONTRACTS
 ├── MACHINERY REQUIREMENTS[]
 ├── EXTENSION REQUIREMENTS[]
 ├── FAILURE BEHAVIOR?
 └── DECK [DECK ID]
      ├── SCOPED DETERMINISM / NUMERIC / RANDOMNESS CONTRACTS
      ├── MACHINERY REQUIREMENTS[]
      ├── EXTENSION REQUIREMENTS[]
      ├── FAILURE BEHAVIOR?
      └── CARD [CARD ID]
           ├── VERB
           ├── NOUN
           ├── OPERANDS
           ├── VALUE
           ├── RESULT BINDING
           ├── TYPE / UNIT
           ├── QUALIFIERS
           ├── SEMANTIC CLASS
           ├── EFFECT REQUIREMENTS[]
           │    ├── DECLARED EFFECT ID
           │    ├── EFFECT KIND
           │    └── REQUIRED CAPABILITIES[]
           ├── MACHINERY REQUIREMENTS[]
           │    ├── MACHINERY REQUIREMENT ID
           │    ├── TARGET SELECTOR / CLASS
           │    └── REQUIRED CAPABILITIES[]
           ├── RESULT-DETERMINISM CONTRACT
           ├── RANDOMNESS CONTRACT
           ├── NUMERIC CONTRACT
           ├── EXTENSION REQUIREMENTS[]
           ├── FAILURE BEHAVIOR
           └── DEPENDENCIES / TAGGED SEQUENCING CONSTRAINTS[]
```

Stable JOB/DECK/CARD IDs are canonical semantic identities. They survive lossless serialization, both lowering stages, and trace production without renumbering.

`VALUE` carries an immediate or literal value when present. `RESULT BINDING` separately names a value produced for dependent CARDs.

Result-determinism, numeric, randomness, extension, and failure contracts remain attached to the JOB, DECK, CARD, or other frozen scope that owns them. A representation may not flatten a DECK/JOB requirement into arbitrary children and silently change its meaning.

Each protected external effect owns its stable declared effect ID, effect kind, and **complete capability set**. A derived CARD-wide capability union may help preflight, but it does not replace the per-effect association.

Protected machinery access is a different boundary. `machinery_requirements[]` can require capabilities such as `GPU` without pretending GPU selection is an external effect.

## Human–AI semantic anchors

Candidate research verbs include:

```text
AIM
OBSERVE
ASSUME
MODEL
DERIVE
RUN
TEST
PROVE
TRACE
LOCK
```

Epistemic distinctions are intentional:

```text
OBSERVATION
    !=
ASSUMPTION
    !=
SIMULATION
    !=
DERIVATION
    !=
VALIDATION
    !=
PROOF
```

Optimization and lowering must not silently promote one class into another.

Illustrative source examples are architectural sketches only. Human `.qsl` parsing and canonical text serialization remain deferred until a normative text profile freezes grammar and source-to-Semantic-IR mapping.

## QSOL-CORE direction

QSOL-CORE is intended to remain deliberately small.

Candidate instruction families include:

```text
DATA       LOAD STORE MOVE
ARITH      ADD SUB MUL DIV MOD
LOGIC      AND OR XOR NOT
COMPARE    EQ NE LT LE GT GE
CONTROL    JUMP BRANCH CALL RET STOP
EFFECT     explicit stateful/external operations
```

The final instruction inventory and operational meaning will be defined by the normative QSOL-CORE specification, not by this README.

## Semantic-to-Core lowering

Canonical Semantic IR carries richer research semantics than QSOL-CORE. The first lowering stage therefore has its own normative specification, reference implementation, conformance fixtures, and provenance identity.

The lowering must preserve or explicitly validate before erasure:

- stable JOB/DECK/CARD identity;
- literal values and result bindings;
- epistemic classes and evidence boundaries;
- types and units;
- execution-relevant qualifiers;
- declared effect IDs and complete per-effect capability sets;
- protected machinery requirements where still material;
- explicit `failure_behavior`;
- result-determinism, numeric, and randomness contracts at their governing scopes;
- extension requirements at their governing scopes;
- the canonical tagged `sequencing_constraints[]` relation, including source/effect/failure ordering.

Its provenance records lowering-spec and implementation identities plus `extension_requirement_lowering_decisions[]`, qualifier, result-determinism, numeric, randomness, machinery/failure, and result-binding decisions where material. Resolved extension identity alone does not replace the source-to-Core scope mapping that preserves profile ownership.

`machinery_requirement_lowering_decisions[]` additionally uses identified cardinality-aware mapping groups with typed `source_scope_refs[]` / `core_scope_refs[]` plus mandatory owner-qualified `source_machinery_requirement_refs[]` / `lower_machinery_requirement_refs[]`. Each requirement reference pairs its local `machinery_requirement_id` with the complete representation-relative `owner_scope_path[]`; the scope arrays remain correspondence context and are never a positional join for requirement identity. The qualified references resolve in the hash-bound Semantic IR and resulting Core IR. A frozen rule defines every split/fusion relation and the exact target selector/capability set reaching each lower requirement. A reconstruction exception must recover every owner-qualified requirement association as well as scope ownership.

### Result-binding maps

Both mandatory lowering boundaries record `result_binding_map[]` whenever result identities are **preserved or transformed**.

Omission is allowed only when a frozen rule permits deterministic reconstruction of the identity mapping.

That means an unchanged binding does not automatically excuse the map. IR hashes alone do not establish which lower name corresponds to which source result.

## Full Vector/Dataflow IR

The mandatory Vector/Dataflow IR is not merely a vector optimizer input. It preserves the complete supported QSOL-CORE surface while exposing dataflow and vectorization opportunities.

It carries or represents:

- scalar and vector operations;
- result/data identities and dependencies;
- representation-qualified epistemic class bindings plus their source-binding/mapping lineage;
- control flow and calls;
- explicit effects with declared effect IDs and complete capability sets;
- protected machinery requirements/metadata where still material;
- qualifiers and failure behavior where still material;
- dependency/effect/failure ordering;
- result-determinism, numeric, randomness, and extension contracts including extension ownership;
- provenance links back to QSOL-CORE and originating semantic CARDs.

A non-vectorizable operation is not permission to bypass this IR.

Core→Vector/Dataflow provenance records not only result-binding correspondence and epistemic-class binding lineage but also contract-scope mappings for extension requirements, result determinism, numeric behavior, randomness, machinery requirements, and failure behavior whenever Core scopes or bound subjects are split, fused, renamed, relocated, or otherwise remapped into lower execution regions/units.

For machinery mappings, typed scope correspondence alone is insufficient when one Core scope owns several requirements. Provenance therefore carries owner-qualified `source_machinery_requirement_refs[]` and `lower_machinery_requirement_refs[]`, with every local `machinery_requirement_id` paired to its complete representation-relative `owner_scope_path[]`. The Core/Vector scope arrays remain mapping context only, so split/fusion groups cannot pair repeated local IDs by position or shared source CARD summaries; the qualified references preserve which exact target selector and capability set reached each lower region.

## Determinism, numerics, and randomness

Result determinism and randomness are separate facets.

```text
RESULT DETERMINISM
    STRICT
    NUMERIC
    DECLARED-NONDETERMINISTIC

RANDOMNESS
    NONE
    SEEDED
    EXTERNAL-ENTROPY
    DECLARED-NONDETERMINISTIC
```

`SEEDED` does not replace a result-determinism contract.

A `NUMERIC` result contract is incomplete without the numeric contract defining legal variation.

Provenance is scoped because different JOBs, DECKs, CARDs, regions, kernels, or generated units may use different legal contracts or machinery:

```text
backend_selection_scopes[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
failure_behavior_bindings[]
```

Each execution-scope record has its own stable type-specific record key distinct from the generic computation `scope_id` it governs. `failure_behavior_bindings[]` uses stable `failure_behavior_binding_id`; output reference arrays point to those record keys directly.

A single execution-wide scope is valid only when a frozen rule proves one entry genuinely governs every relevant source computation.

Whenever requested and effective result-determinism or randomness contracts differ, require `transition_authorized_by` resolving to a versioned `CONTRACT_TRANSITION` rule and `transition_evidence_id` resolving to passing evidence for the exact execution-scope record and requested/effective pair. Accepted source/policy authority, applicable conditions, and evidence must be verified before effective-contract activation or use. Missing, stale, unknown, mismatched, unverifiable, or late authority/evidence fails closed. Optional notation allows omission only when no transition occurs, not an undocumented downgrade.

A semantics-changing numeric contract at either mandatory lowering boundary is governed by the same transition discipline. `numeric_contract_lowering_decisions[]` and `core_to_vector_numeric_contract_mapping_decisions[]` identify the exact requested/source and effective numeric contract IDs/hashes and require stable `transition_decision_id`, accepted `CONTRACT_TRANSITION` authority, and passing subject-bound `transition_evidence_id` validated before the changed contract is applied. Changing strict IEEE behavior into tolerance/fast-math, newly allowing reassociation/FMA, changing effective precision, rounding, or denormal behavior, or otherwise changing the legal arithmetic/value set is a semantic transition—not a generic mapping or backend flag. Representation-only relocation/rename of an identical content-bound numeric contract remains a mapping.

The shared `rule_records[]` and `validation_evidence[]` schemas are defined in [Trace and Provenance](docs/TRACE-AND-PROVENANCE.md#referenced-rules-and-validation-evidence). They bind authority identity/version, verifiable rule/evidence content, exact typed subject, evaluated context, verifier identity, and same-domain validation-before-application ordering. A backend's success label is not evidence; these records neither grant capabilities nor promote research evidence classes.

Every `randomness_execution_scopes[]` record with `effective_randomness_mode = SEEDED` records the exact RNG algorithm, RNG version, seed, and stream identity. Parallel partitioning/stream mapping is additionally mandatory whenever it can change the generated or consumed sequence; it may be omitted only when the active frozen RNG/execution contract proves partitioning cannot affect the sequence. Implementation defaults or the `SEEDED` label alone are not replay identity.

`EXTERNAL-ENTROPY` permits fresh entropy but does not authorize hidden entropy access. Each concrete acquisition is a declared protected `RANDOM` effect with its own declared effect ID, complete capability set including `RANDOM` (or frozen equivalent), contextual authorization record, and runtime attempt provenance. The randomness scope also links to the exact acquisition attempt(s) and immutable entropy input identity where material.

## Failure and execution path

Failure is observable behavior.

The candidate default is fail-stop:

```text
SUCCESS(value?)
FAILURE(record)
```

An unhandled CARD failure stops its DECK. An unhandled DECK failure fails its JOB and prevents later DECKs from starting. Pure failure commits no semantic state.

A run therefore distinguishes canonical membership from actual execution. Semantic execution uses `deck_executions[]` / `card_executions[]`; a legitimate direct QSOL-CORE or other lower entry instead uses identified representation-qualified `operation_executions[]` and does not fabricate Semantic membership.

Every protected external effect attempt is individually identified and records:

```text
effect_attempt_id
effect_requirement_ref:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    declared_effect_id
execution_subject_ref:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    subject_kind
    subject_id
    execution_id
card_id?
card_execution_id?
effect_kind
required_capabilities[]
effect_authorization_record_id
sequence_index
effect_begin_sequence_index?
effect_end_sequence_index?
completion_state
acquired_input_ids[]
observable_output_ids[]
external_tool_ids[]
```

`effect_requirement_ref` and `execution_subject_ref` are canonical. Semantic CARD-backed attempts retain matching CARD fields as verified projections; direct Core attempts resolve the actual Core operation and `operation_execution_id` and omit CARD fields unless independently verified Semantic lineage exists.

`effect_authorization_record_id` links the concrete attempt to the contextual required/granted/denied capability decision and policy that governed it. Execution-wide capability summaries do not substitute for this per-attempt authorization record.

For every attempt marked `COMPLETED`, `ABORTED_CLEAN`, `PARTIAL`, or `UNKNOWN`, the effect is known to have begun. `effect_begin_sequence_index` is therefore mandatory, the linked authorization must be `GRANTED` with a concrete `authorization_sequence_index` in the same frozen monotonic event-order domain, and `authorization_sequence_index < effect_begin_sequence_index` must hold. For every `COMPLETED`, `ABORTED_CLEAN`, or `PARTIAL` attempt, `effect_end_sequence_index` is also mandatory, is in that same event-order domain, and must satisfy `effect_begin_sequence_index < effect_end_sequence_index`. `UNKNOWN` may omit the end index only when the attempt's termination/completion boundary genuinely cannot be established; if a definite termination event is known, the end index is recorded. `NOT_STARTED` has no begin/end event and empty `acquired_input_ids[]`, `observable_output_ids[]`, and `external_tool_ids[]`; no output may cite it through `effect_attempt_ids[]`. Generic `sequence_index` is neither authorization-order nor effect-boundary-order proof.

`observable_output_ids[]` is the reciprocal side of output `effect_attempt_ids[]`: it identifies the exact outputs this concrete attempt produced, exposed, published, or materially supplied. `external_tool_ids[]`, where material, identifies the exact tool/service/model/prover used by this attempt, so retries or multiple tools invoked by one execution subject do not collapse into broad CARD attribution.

A declared effect that has no runtime attempt for a concrete execution subject is accounted for by an identified `effect_non_attempt_records[]` entry carrying its own stable record ID, the same representation-qualified declaration and execution-subject refs, legitimate non-attempt reason, and typed control/failure cause where applicable. Conditional CARD fields are retained only when verified Semantic lineage exists.

An explicit frozen skip additionally requires `governing_skip_rule_id` resolving to an applicable `EFFECT_SKIP` rule and `skip_verification_evidence_id` resolving to passing evidence for this exact non-attempt record, declared effect, concrete execution subject, and active semantic/policy context before the skip is applied. A label or unverifiable rule is not a legitimate reason to omit a reachable effect. Explicit Semantic CARD skips require the same fields with evidence for their `CARD_EXECUTION` subject and cannot evade accounting for their effects.

Declared-effect accounting is unconditional. Every applicable declaration for every selected concrete execution subject resolves to attempt(s), exactly one legitimate identified non-attempt, or structured failure. No audit/profile/optimization/deployment switch may disable this rule.

`BACKEND_OMISSION_DETECTED` (or a frozen equivalent) is not an ordinary successful non-attempt reason. It means a reachable required effect was omitted and therefore **forces structured execution/conformance failure**; it cannot coexist with a successful enclosing execution.

Completion state is one of:

```text
NOT_STARTED
COMPLETED
ABORTED_CLEAN
PARTIAL
UNKNOWN
```

Known completion takes precedence over uncertainty about broader consequences. Completion belongs to the effect attempt, not the enclosing CARD/lower-operation outcome.

Failure records always carry typed `failing_scope_kind` plus `failing_scope_id`. `failure_card_id?` and `failure_card_execution_id?` are present only when a CARD execution actually caused the failure. JOB/DECK/setup/lowering/machinery or direct lower-operation failures that occur without a CARD culprit must not fabricate one.

Every failure record requires `failure_behavior_binding_ids[]` for the exact policy bindings active for that failure and its handling/propagation, including the applicable frozen default fail-stop binding. A rejected requested policy is not an effective handling policy, and the resulting path cannot substitute for the policy references. Each failure also preserves the complete applicable `result_determinism_scope_ids[]`, `numeric_scope_ids[]`, and `randomness_scope_ids[]`, including output-free failures.

Failure traces retain `failure_behavior_bindings[]`, `result_determinism_scopes[]`, `numeric_execution_scopes[]`, `randomness_execution_scopes[]`, `backend_selection_scopes[]`, and `backend_selection_decisions[]` alongside machinery authorization/use records, including denied candidates and fallback predecessors. A standalone failure manifest preserves the complete transitive reference closure inline or through retrievable content-bound records; dangling selection, policy, requirement, rule, evidence, contract-scope, or output IDs are incomplete provenance.

## Extensions, capabilities, and machinery authorization

Extension availability and runtime authorization are independent.

```text
USE QX-NET
DENY NETWORK
```

may mean that the profile is understood while runtime network access is forbidden.

Candidate profiles include:

```text
QX-VEC
QX-MATH
QX-POSIX
QX-GPU
QX-CUDA
QX-AI
QX-PROVE
QX-MIDI
QX-NET
```

Activating an extension never grants runtime permission by itself.

Machinery selection is also distinct from authorization. `RUN MODEL ON GPU` may select a GPU-backed scope, but protected GPU use begins only after the applicable machinery requirement's capabilities are granted.

`machinery_authorization_records[]` bind the selected backend-selection scope **and concrete backend-selection decision** to applicable representation-qualified `machinery_requirement_refs[]`, required/granted/denied machinery capabilities, and the capability policy responsible for the decision. Each requirement ref carries `representation_kind`, content-bound `representation_identity`, the complete representation-relative `owner_scope_path[]`, and local `machinery_requirement_id`. Semantic requirements resolve through their actual JOB/DECK/CARD containment; direct QSOL-CORE requirements resolve in `core_ir_hash` through the real Core-relative owner path without fabricating Semantic ancestors.

`machinery_use_records[]` identify protected-use start/stop and link back to the applicable authorization records in the same frozen event-order domain. Execution-governed use carries nonempty representation-qualified `execution_subject_refs[]`: Semantic subjects resolve through `card_executions[]`, while direct Core work resolves the actual `CORE_OPERATION` / `operation_execution_id`. `source_card_ids[]` / `card_execution_ids[]` are conditional verified Semantic projections only. Genuine RUN/DECK pre-execution setup may instead use `initiating_scope_ref`; this exception never stands in for an executing Core operation. Each protected use also retains the exact generated artifacts and reciprocal output IDs where applicable.

## CUDA without ordinary plumbing

A long-term target experience is:

```text
RUN GRAVITY ON CUDA
```

while QSOL-MORPH handles ordinary target mechanics.

The roadmap freezes a generic GPU execution contract before the CUDA backend. CUDA machinery and QX-CUDA controls remain separate: optional launch/memory/tuning controls require a separately frozen, versioned QX-CUDA contract.

## Trace and provenance

Executable research results should be bound to enough context to explain and reproduce the run.

Core trace material includes:

```text
source identity/hash when present
canonical Semantic-IR identity/hash when present
stable run/JOB/DECK/CARD IDs when Semantic lineage exists
identified deck_executions[] / card_executions[] when Semantic execution exists
identified operation_executions[] for direct lower-entry execution
representation-qualified epistemic_class_bindings[]
representation-qualified effect_requirements[]
representation-qualified machinery_requirements[]
semantic-to-core spec + implementation identity when traversed
semantic-to-core result_binding_map[] when traversed
semantic-to-core extension/contract decisions[] when traversed
QSOL-CORE IR hash
core-to-vector/dataflow spec + implementation identity when traversed
core-to-vector result_binding_map[] when traversed
core-to-vector epistemic_class_bindings[] with source-binding/mapping lineage when traversed
core-to-vector extension/contract-scope mapping decisions[] when traversed
Vector/Dataflow IR hash when traversed
MORPH/compiler identity
backend_selection_scopes[]
backend_selection_decisions[]
machinery_authorization_records[]
machinery_use_records[]
result_determinism_scopes[]
numeric_execution_scopes[]
randomness_execution_scopes[]
failure_behavior_bindings[]
rule_records[]
validation_evidence[]
identified inputs[]
identified outputs[]
resolved extension identities
external_tool_versions[]
capability authorization policy
effect_authorization_records[]
declared effect IDs + runtime effect attempts + explicit non-attempt reasons
cache_reuse_records[]
optimization_provenance[]
generated_artifacts[]
toolchain_invocations[]
failure records
```

Effect and machinery declarations/references are representation-qualified: the representation kind/content identity plus complete representation-relative `owner_scope_path[]` and local declaration ID identify the actual declaration. Semantic paths preserve JOB/DECK/CARD containment; a direct Core path begins at the Core representation root and never fabricates a Semantic hierarchy. First-lowering scope references likewise retain complete containment paths in their source/Core representations rather than only kind plus local ID.

`backend_selection_scopes[]` identify governed machinery-selection records through a fully qualified `governed_scope_ref` containing representation identity plus complete representation-relative `owner_scope_path[]`; stable selection-scope IDs do not replace canonical ownership. Execution-contract scope ledgers use the same qualified governed-scope rule. `backend_selection_decisions[]` preserve the ordered decision history within those scopes, including denied/superseded targets and frozen fallback transitions rather than overwriting them with the final backend.

`external_tool_versions[]` must carry immutable/versioned material identity when an external tool/service/model/prover/process materially affects result or evidence. A mutable name or endpoint alone is insufficient. If exact material identity is unavailable, that unavailability is explicit and the replay/evidence claim is weakened according to frozen policy.

Every generated artifact requires its exact production `backend_selection_decision_id`, resolving in the recorded selection scope and consistently identifying the target context. A rejected candidate's artifact must not be attributed to the scope's final fallback decision; artifact existence does not authorize protected use.

Generated artifacts identify one `direct_producer_toolchain_invocation_id` plus ordered `toolchain_invocation_chain_ids[]`. Invocation `input_generated_artifact_ids[]` and `output_generated_artifact_ids[]` are direct build-graph edges, so a transitive ancestor in the chain does not falsely claim it directly emitted the final artifact. For `compile → object → link → executable`, the compiler directly emits the object, the linker directly emits the executable, while the executable's ordered ancestry can retain both invocations. Run-wide compiler version lists remain summaries, not artifact-level build evidence.

Toolchain invocations carry explicit `input_ir_hashes[]`, nonempty whenever that invocation directly consumes IR, so ordinary non-optimized code generation remains bound to the exact IR snapshot that produced the artifact. They also carry `input_ids[]` resolving to immutable `inputs[]` records for material dependencies not generated in this run, including prebuilt objects, libraries, headers, startup files, sysroots, and implicit dependencies. The array is empty only when no such inputs were consumed; composite inputs must content-bind the complete material dependency set. Mutable paths, library names, flags, and tool versions alone are insufficient identity, and prebuilt dependencies must not be fabricated as this run's generated outputs. Missing material input identity invalidates complete/reproducible build provenance.

### Identified inputs

Material inputs bind stable `input_id` values to the exact canonical value, content hash, or immutable artifact/version identity actually consumed. Each concrete CARD or lower-operation consumer is identified by representation-qualified `consumer_execution_refs[]`; direct Core consumers resolve the actual `operation_execution_id`. `consumer_card_execution_ids[]`, when present, is only the verified Semantic projection of CARD-backed consumer refs. Effect-acquired values also retain `effect_attempt_ids[]`, with reciprocal attempt input IDs even when the consumer later fails or emits no output. Genuine RUN/DECK setup may use typed `consumer_scope_refs[]`; it does not replace a required concrete execution-subject ref for an actual operation/CARD consumer.

A mutable path, URL, dataset name, or model name is retrieval context, not content identity.

Applicable outputs reference the exact materially contributing input records through `input_ids[]`; execution-wide input availability is not itself proof that every input contributed to every output.

### Identified outputs

Outputs are **not** bare hashes.

Each `outputs[]` entry binds:

```text
output_id
result_binding_ref?:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    binding_id
artifact_hash
artifact_location?
semantic_class
epistemic_class_binding_ids[]
status
evidence_status?:
    evidence_class
    status
    evidence_rule_id
    evidence_validation_id
producer_execution_refs[]:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
    subject_kind
    subject_id
    execution_id
producer_card_ids[]?
producer_card_execution_ids[]?
input_ids[]
effect_attempt_ids[]?
external_tool_ids[]
backend_selection_scope_ids[]
machinery_use_record_ids[]
generated_artifact_ids[]?
result_determinism_scope_ids[]
numeric_scope_ids[]
randomness_scope_ids[]
failure_behavior_binding_ids[]
cache_reuse_record_ids[]?
```

`result_binding_ref?`, when present, is the qualified binding endpoint: representation kind/content identity, complete owner path, and local binding ID. It must resolve directly or through the applicable cardinality-aware lowering maps, so sibling `v0` bindings or a fused lower `v0` cannot be selected by text or producer position.

`producer_execution_refs[]` is the canonical nonempty concrete producer relation. Semantic CARD producers resolve through `card_executions[]`; a legitimate direct QSOL-CORE producer resolves through `operation_executions[]` to the actual `operation_execution_id`. `producer_card_ids[]` / `producer_card_execution_ids[]` are conditional verified Semantic-lineage projections only and are absent rather than fabricated when no Semantic ancestry exists.

`epistemic_class_binding_ids[]` is always explicit. Independently derive the complete applicable representation-qualified class-binding set from `producer_execution_refs[]`, the entered representation, and every traversed class-preservation mapping, then require duplicate-free exact-set equality. A classified output must have a nonempty applicable set that justifies its exact `semantic_class`. Legitimate lower-entry output with no applicable class binding uses `semantic_class = UNCLASSIFIED` (or frozen no-claim equivalent), an empty binding array, and no `evidence_status`; operational success cannot manufacture TEST/VALIDATION/PROOF provenance.

`evidence_status` is conditionally present by class, but its rule/evidence IDs are not optional once the output is evidence-bearing. Every TEST, VALIDATION, PROOF, or frozen evidence-bearing class requires `evidence_status`, `evidence_rule_id`, and `evidence_validation_id`, including class-preserving TEST→TEST, VALIDATION→VALIDATION, and PROOF→PROOF claims. For class preservation, the rule resolves to accepted content-bound `EVIDENCE_STATUS` authority and the validation ID resolves to passing output-bound substantive evidence for this exact artifact, class bindings, concrete producers, material inputs/tools/evidence identities, and claim-publication event before publication. For a non-class-preserving transition, the rule instead resolves to accepted `EPISTEMIC_TRANSITION` authority and the same output-bound validation additionally proves the exact source-class-to-target-class transition. Generic output `status` remains an execution/artifact state and cannot itself create or preserve an evidence claim.

`input_ids[]` identifies the exact immutable input records that materially contributed to the output under the frozen provenance-dependency rule. It is not a copy of all inputs available during the run.

`effect_attempt_ids[]`, when applicable, identifies the concrete authorized effect attempts that produced, exposed, or materially supplied the output. Each referenced attempt reciprocally names the output in `observable_output_ids[]` and must have begun; `NOT_STARTED` is never a valid output producer/exposer. `external_tool_ids[]` is always an explicit array, empty when no material tool contributed; material tools carry explicit attempt/output subject arrays and reciprocal links. `machinery_use_record_ids[]` likewise names the exact protected-use occurrences that produced or exposed the output and reciprocates `machinery_use_records[].output_ids[]`. These joins prevent retries, repeated protected launches, or multiple tools invoked by one execution subject from collapsing into ambiguous attribution.

`backend_selection_scope_ids[]` is a normative duplicate-free exact-set attribution. Independently derive every applicable backend-selection scope from the concrete `producer_execution_refs[]`, their representation-qualified governed scopes, final executable selection decisions, and any material interpreted/reference/backend execution relation used by those producers. Require the recorded IDs to equal that complete producer-derived set: an unrelated scope is invalid, and omitting a producer's actual scope is equally invalid. This rule applies even when there is no generated artifact or protected-machinery use record from which a consumer might otherwise infer the scope. `generated_artifact_ids[]`, when applicable, identifies the **exact executable/kernel/bytecode artifact that actually ran or supplied the result**; it complements rather than replaces backend-scope attribution.

`failure_behavior_binding_ids[]` resolves to the exact identified failure-policy records that governed whether the producer path continued, failed, recovered, or compensated. Generic source-scope IDs are not substitutes for the stable binding-record keys.

An optimized generated artifact records its applicable `optimized_ir_hash` and `optimization_record_ids[]`, while each optimization record reciprocally lists the `generated_artifact_ids[]` it produced. Each generated artifact also identifies its direct toolchain producer and ordered transitive toolchain ancestry. This makes the provenance path `output → generated artifact → optimization provenance / direct toolchain producer / toolchain ancestry` directly resolvable rather than inferred from `backend_unit_id` or a run-wide compiler list.

A simulation artifact and a separately validated artifact therefore cannot accidentally share one evidence status or machinery/RNG/generated-code provenance record.

### Cache reuse

Legal cache reuse is provenance-bearing.

`cache_reuse_records[]` distinguishes `COLD_EXECUTION`, `VERIFIED_REUSE`, and `UNVERIFIED_HIT` or frozen equivalents and binds material cache identity plus reused computation/artifact identity.

For `VERIFIED_REUSE`, both `legality_rule_id` and `verification_evidence_id` are mandatory. They resolve to an applicable `CACHE_SUBSTITUTION` rule and passing evidence for the exact reuse record, checked cache identity/artifact, and current inputs/contracts/context before substitution. A label, matching hash, unknown ID, or stale evidence is not verification. `UNVERIFIED_HIT` cannot satisfy a CARD or supply a verified-reuse output: verify successfully before reuse, execute cold, or fail closed.

A verified cache reuse does **not** prove that a cold reconstruction still succeeds.

Ordinary cached result substitution is conservative and effect-free by default. Effectful reuse requires the referenced rule to be the specifically applicable separately frozen replay/cache semantic preserving the declared effect, authorization, ordering, failure, output attribution, external state, and per-attempt provenance boundaries. A generic cache rule is insufficient. See the shared [cache validation contract](docs/TRACE-AND-PROVENANCE.md#cache-reuse-provenance).

## Optimization rule

> **A faster semantics-breaking change is not an optimization.**

Optimization is subordinate to:

- semantic preservation;
- epistemic boundaries;
- result-determinism and numeric contracts;
- randomness/replay requirements;
- effect/failure ordering;
- effect and machinery capability authorization;
- provenance.

Dead-result elimination may remove an operation solely because its result is unused only when the operation is proven pure and total, unless its original failure is explicitly preserved at the same observable point.

## Documentation

Start with [docs/README.md](docs/README.md).

Key documents:

- [Specification Status](docs/SPECIFICATION-STATUS.md)
- [Design Principles](docs/DESIGN-PRINCIPLES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Human–AI Language Model](docs/LANGUAGE-MODEL.md)
- [Candidate Semantic IR](docs/SEMANTIC-IR.md)
- [Semantic-to-QSOL-CORE Lowering](docs/SEMANTIC-TO-CORE-LOWERING.md)
- [Vector and Dataflow](docs/VECTOR-AND-DATAFLOW.md)
- [Backends and Morphing](docs/BACKENDS-AND-MORPHING.md)
- [Extensions and Capabilities](docs/EXTENSIONS-AND-CAPABILITIES.md)
- [Determinism and Reproducibility](docs/DETERMINISM-AND-REPRODUCIBILITY.md)
- [Failure and Partial Effects](docs/FAILURE-AND-PARTIAL-EFFECTS.md)
- [Trace and Provenance](docs/TRACE-AND-PROVENANCE.md)
- [Optimization and CI](docs/OPTIMIZATION-AND-CI.md)
- [Roadmap](ROADMAP.md)
- [AI / Agent Guidance](AGENTS.md)

## Development sequence

The authoritative details are in `ROADMAP.md`.

```text
PR #1   Documentation Foundation
PR #2   Lock in Core Invariants
PR #3   Canonical Data Model
PR #4   Canonical Machine-Readable Serialization
PR #5   Execution Contract, Trace, Failure, and Provenance Foundation
PR #6   Normative QSOL-CORE Operational Specification
PR #7   QSOL-CORE Reference Machine
PR #8   Normative Semantic-to-QSOL-CORE Lowering Specification
PR #9   Reference Semantic-to-QSOL-CORE Lowering
PR #10  Normative Full Vector/Dataflow IR Specification
PR #11  Reference QSOL-CORE-to-Vector/Dataflow Lowering
PR #12  Reference MORPH to C
PR #13  Morph Optimization Passes
PR #14  Normative QX-POSIX Contract
PR #15  QX-POSIX Reference Implementation
PR #16  LLVM Backend
PR #17  Normative Generic GPU Execution Contract
PR #18  CUDA Backend
PR #19  Normative QX-CUDA Control Contract
PR #20  QX-CUDA Reference Control Implementation
PR #21  Additional Backends
PR #22  Formalization
```

The human `.qsl` text profile remains a deferred normative workstream until its grammar and source mapping are frozen.

The repeated architectural rule is simple: **specify meaning before implementing machinery.**

## Design influences

QSOL-MORPH borrows architectural lessons rather than reproducing historical systems:

- **Transmeta:** stable semantics above replaceable machinery;
- **Cray:** vector-first data movement and chaining;
- **RISC:** small orthogonal cores;
- **Bell Labs / Unix:** composition and explicit streams;
- **Apollo:** compact memorable operational vocabulary;
- **mainframe record systems:** JOB / DECK / CARD discipline.

## Non-goals

QSOL-MORPH does not initially aim to:

- replace every compiler;
- replace CUDA, LLVM, Fortran, or POSIX;
- hide all machine characteristics;
- guarantee identical floating-point behavior across every target without an explicit contract;
- become a universal kitchen-sink language.

The project should reuse mature machinery whenever that machinery already solves the lower-level problem well.

## License

QSOL-MORPH is released under the **Apache License 2.0** unless otherwise noted. See [LICENSE](LICENSE).

---

**QSOL-IMC Research Architecture**