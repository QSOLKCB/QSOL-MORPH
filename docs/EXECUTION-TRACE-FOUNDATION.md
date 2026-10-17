# Execution Trace Foundation

## Status and authority

This is a **bounded PR #5 foundation**, not completion of the executable PR #5
provenance gate. It provides a closed structural candidate trace schema,
[`spec/execution-trace.schema.json`](../spec/execution-trace.schema.json), and
[`tools/check_trace.py`](../tools/check_trace.py) for source-bound synthetic receipt
consistency. No QSOL program is executed, no external effect is performed, and no
capability is granted by validation.

The existing [core invariants](CORE-INVARIANTS.md), [Canonical Data Model
1.0.0](CANONICAL-DATA-MODEL.md), and [Canonical Serialization
1.0.0](CANONICAL-SERIALIZATION.md) remain unchanged. The broader record contracts in
[Trace and Provenance](TRACE-AND-PROVENANCE.md), [Failure and Partial
Effects](FAILURE-AND-PARTIAL-EFFECTS.md), and [Determinism and
Reproducibility](DETERMINISM-AND-REPRODUCIBILITY.md) remain the architectural targets
outside their already frozen controlled invariants. Adding structural definitions
does not freeze their operational interpretation.

There are three distinct questions:

1. **Structural validity:** does a candidate document have the closed shapes and
   field types represented by the schema?
2. **Synthetic consistency:** do supported receipt records agree with the
   independently validated, content-bound Semantic model and with one another?
3. **Execution conformance:** did an accepted implementation actually perform the
   frozen operations, effects, authorization checks, and evidence verification?

This foundation implements the first question and a bounded subset of the second.
It does not establish the third. A schema-valid document can be rejected by the
reference validator. A passing synthetic receipt does not establish that its
claimed events happened or that its output bytes are a correct research result.

## Accepted receipt boundary

The reference validator accepts only
`receipt_kind = SYNTHETIC_CONFORMANCE_RECEIPT`, with a hash-bound source conforming
to the frozen Semantic data model. `EXECUTION_TRACE` fails closed. A producer cannot
turn a synthetic receipt into an execution certificate by changing a label, adding
an implementation name, or reporting `SUCCESS` or `PASS`.

The source fingerprint is the PR #4 canonical serialization fingerprint, including
its versioned envelope, rather than a hash of arbitrary pretty-printed JSON. It
binds the entire validated source model, including explicit fields, absence versus
explicit defaults, source order, and owner identities. It is not a signature or
an independent attestation. Source content must be available for validation;
matching self-reported trace copies are insufficient.

The supported ledger describes one selected JOB, with every DECK and CARD in that
JOB represented exactly once in canonical order. It is a synthetic, sequential
fail-stop profile. Loops, calls, branches, retries, recovery, explicit verified
skips, and repeated invocation scheduling are not implemented. Local source IDs
remain local; full JOB/DECK/CARD paths distinguish siblings reusing an ID.

The validator does not interpret VERB/NOUN tokens as instructions, compute typed
operand values, establish numeric correctness, draw random numbers, load extension
profiles, or infer an operational capability vocabulary. Unsupported operational
claims fail closed rather than being silently ignored or treated as successful
execution. Preservation of a declaration or contract identity is not proof that
its operational meaning was satisfied.

### Envelope and supported source profile

The envelope uses `trace_version = 1.0.0`, the synthetic receipt kind above, and
`event_order_domain = RUN_SEQUENCE`. Its entered representation is `SEMANTIC_IR`,
with the PR #4 fingerprint in both `input_representation_identity` and the
corroborating `semantic_ir_hash`. Exactly one
`representation_records[]` entry retains `representation_kind`,
`representation_identity`, `format = QSOL-MORPH-MODEL-1.0.0`, and the complete PR #3
model in `content`. `job_id` selects an actual JOB in that model. A bound full model
may contain other JOBs; this receipt does not execute or schedule them.

Within the selected JOB, the source profile rejects nonempty qualifiers and
extension requirements, and rejects `EXTERNAL-ENTROPY`. Their operational meaning cannot be supplied by this
receipt. Numeric scope records preserve the complete source `numeric_contract` in
`material_numeric_mode`; SEEDED scope records preserve every source RNG and
partitioning field. Neither numeric behavior nor random-number generation is
executed or proved. Requested and effective supported contracts remain unchanged.
The stable default failure policy is `QSOL-MORPH:FAIL_STOP:1.0.0`, represented at
JOB scope plus explicit child policy declarations, retaining their source owners.

The public checker rejects nonempty `operation_executions`, `control_decisions`,
`rule_records`, `validation_evidence`, `generated_artifacts`,
`toolchain_invocations`, `toolchain_environment_configs`, `optimization_provenance`,
`resolved_extensions`, and `runtime_compiler_versions`. Unsupported optional
source-trace, lowering, and source-contract-summary projections also reject rather
than being accepted as opaque metadata. Structural presence of a candidate family
is not permission to populate it in an accepted synthetic receipt.

Receipt JSON numeric tokens must denote exact mathematical integers; the reader
uses PR #4's bounded exact token conversion, including integral fraction/exponent
spellings. Non-integral numbers reject; decimal material values use typed strings.
The Python API accepts only JSON tree types with integer numbers, string object
keys, and no cycles or binary floats. It never rounds source coordinates through
binary floating point before checking their fingerprint. Host integer/exponent
resource limits still apply. Receipt content hashes use sorted-key ASCII JSON
with compact separators after this integer normalization; they are separate from
the PR #4 program fingerprint and confer no authentication.

## Source-derived identity and contracts

Canonical declaration and subject references retain representation kind, content
identity, and complete ordered owner path. Concrete CARD execution IDs are distinct
from canonical CARD IDs. Each reference resolves against the bound source and the
appropriate execution ledger, never by first matching a local name.

Effect declarations preserve the exact source owner, declared effect ID, effect
kind, and complete required-capability set. Machinery declarations independently
preserve their exact owning scope, requirement ID, target selector, and complete
capability set. Matching truncated trace/attempt/authorization copies cannot satisfy
a larger source requirement. Machinery selection is never fabricated as an effect.

Contract records retain their original canonical owner. Applicable result-
determinism, numeric, randomness, failure-behavior, and backend-selection record
sets are derived from the concrete producer or failing scope and the supported
containment relation. Output and failure reference arrays must equal the complete
applicable sets; unrelated extras and missing parent scopes both reject. These
checks establish scoped receipt consistency, not numeric/RNG behavior or backend
correctness. Requested-to-effective semantic transitions require future frozen
authority/verifier support and are not authorized by a self-asserted rule record.

## Failure and sequential accounting

Synthetic success/failure records must agree across CARD, DECK, and JOB ledgers.
The initial profile admits at most one failure: a JOB preflight failure or a
CARD-caused failure. It does not admit independent DECK-setup or lower-operation
failures. CARD outcomes are `SUCCESS`, `FAILED`, or `BLOCKED`; a JOB preflight
failure blocks all selected CARDs and DECKs without fabricated CARD attribution.
This bounded profile requires `failure_stage: JOB_PREFLIGHT` for JOB failures and
`failure_stage: CARD` for CARD-caused failures; other stages remain unsupported.
An unhandled CARD failure fails its DECK and JOB; later CARDs and DECKs remain
present with the applicable blocking failure. A blocked subject references the
failure that prevented it, rather than claiming it caused a new failure. Typed
failure identity and exact applicable contract bindings remain mandatory even when
no output was produced.

For every selected concrete CARD subject and every applicable declared effect,
receipt accounting requires one mutually exclusive route:

- exactly one identified attempt (retries are deferred);
- exactly one legitimate non-attempt tied to its supported fail-stop cause; or
- exactly one declaration/subject-specific accounting-failure record linked to a
  structured failure, with reciprocal accounting-failure IDs on that failure.

A broad failure cannot discharge an unrelated missing effect. A reachable omitted
effect cannot become a successful non-attempt. Canonical membership cannot prove
an attempt occurred, and a blocked CARD cannot supply an invented begun attempt.

Attempt completion is separate from enclosing success/failure. The represented
states preserve `NOT_STARTED`, `COMPLETED`, `ABORTED_CLEAN`, `PARTIAL`, and `UNKNOWN`.
A completed effect may remain recorded when its enclosing CARD fails; failure does
not erase prior effects or relabel known completion as uncertainty.

Every begun attempt requires a linked granted authorization with the full exact
capability set, and same-domain authorization-before-begin ordering. Definitively
terminated attempts require an end after begin. `NOT_STARTED` has no begin/end
and no acquired-input, observable-output, or external-tool participation, and no
output can cite it. A generic record sequence number cannot replace boundary
ordering. `UNKNOWN` attempts carry the explicit `termination_known` boolean:
a known termination requires an end event, while unknown termination cannot be
claimed as a definite end. Output `publication_sequence_index` is mandatory in
the same synthetic event-order domain. The initial sequential profile allows no
recorded event after its unique fail-stop failure, and a never-started attempt
follows its authorization decision. These are consistency checks on supplied
event facts; this validator
cannot observe an external completion boundary or prove that a reported abort
left the real world unchanged.

## Inputs, outputs, tools, and machinery

Inputs carry stable identities and canonical values or content hashes,
with concrete consumer joins. Effect-acquired inputs join reciprocally to their
attempts. Inputs must have concrete runtime consumers; setup/build-only consumers
and opaque artifact-version resolvers are deferred. This synthetic profile requires
completed acquisition attempts and records all direct producer inputs on each
output. Material input acquisition must complete strictly before every contributing
output publication, including acquisition within the same CARD. This does not
interpret operand consumption or establish hidden materiality.
Outputs have one producer; multi-producer composition requires a later frozen rule.
Output records identify concrete producer executions, represented material
input references, applicable scope sets, and named result-binding identity whenever
one exists. These joins do not compute the actual output or independently discover
hidden material inputs.

Class provenance is derived before interpreting an output's label. An output cannot
remove an inherited TEST, VALIDATION, or PROOF obligation by writing `UNCLASSIFIED`
or clearing the class-binding array. The source/result binding and exact applicable
class-binding set must agree. Evidence-bearing TEST/VALIDATION/PROOF outputs are
rejected because this foundation provides no accepted class-specific substantive
evidence verifier. Generic operational success, a copied class, or a producer's
`PASS` assertion cannot satisfy that missing verifier. The output is not silently
declassified to make it pass.

Concrete effect/output/tool and machinery/output relations must be reciprocal.
A broad source CARD association does not identify which attempt or protected-use
occurrence materially contributed. Final executable backend decisions retain a
content-bound implementation identity; a mutable name or version assertion alone
is insufficient. Protected machinery use must resolve its scope's final executable
decision and every applicable granted authorization, with authorization before
use. A denied, superseded, or merely considered decision cannot become the used
decision by sharing a selection scope. This profile permits one initial explicit
target decision per source scope, with the target token equal to the backend token.
It conservatively requires every inherited machinery declaration and an exact
target-selector token match. Automatic/device-specific selection, fallback, and
pre-execution setup applicability are deferred. Runtime protected uses record both
start and stop; multiple concrete uses may remain distinct. Cache records are
restricted to reciprocal `COLD_EXECUTION` classifications.

These checks validate represented identities and ordering only. They neither invoke
a backend nor attest that the identified implementation or external tool ran.

## Coverage matrix

“Structural” below means closed record shapes, not substantive verification.
“Synthetic” means supported source-bound ledger consistency only.

| Area | Structural schema | Implemented synthetic boundary | Deferred execution conformance |
| --- | --- | --- | --- |
| Entry identity | Representation-qualified references and receipt discriminator | Bound canonical Semantic model; one selected JOB | Actual `EXECUTION_TRACE`; direct Core or other lower entry |
| Execution ledgers | DECK/CARD and lower-operation candidate records | Complete once-only sequential Semantic ledger and fail-stop consistency | Core instruction execution, branches, loops, calls, retries, recovery |
| Source declarations | Owner-qualified effect and machinery records | Exact owners, identities, declaration fields, and capability sets | Operational effect/target applicability and actual permission enforcement |
| Effect accounting | Attempts, non-attempts, accounting failures | Per-subject accounting, typed failure joins, boundary consistency | Observing external completion, partial effects, rollback, replay |
| Failure records | Typed failures and contract references | Exact cause and applicable scope consistency | Arithmetic, runtime, setup, and lower-operation failure semantics |
| Outputs and classes | Identified output and class-binding records | Source-derived bindings/classes/scopes and reciprocal joins | Result computation; substantive TEST/VALIDATION/PROOF verification |
| Inputs and tools | Immutable identity and concrete participation fields | Reference/identity consistency and reciprocal joins | Independent observation of consumed bytes and external participation |
| Backend and machinery | Selection, authorization, and use ledgers | Final decision identity and authorization-before-use consistency | Selection algorithms, actual protected use, device/runtime semantics |
| Numeric and randomness contracts | Scoped declarations and provenance fields | Supported source-preserving contract attribution | Numeric interpretation, RNG generation/partition semantics, entropy execution |
| Rules and evidence | Candidate typed rule/evidence records | Unsupported evidence-dependent behavior rejects | Accepted rule registry, substantive verifiers, transitions, fallback, verified skips |
| Lowering and class maps | Candidate mapping and lineage records | Not an accepted execution/lowering path | Both frozen lowering specifications and reference implementations |
| Artifacts and toolchains | Candidate artifact, argv, environment, and ancestry records | No compiler/toolchain execution certification | Generated-byte reconstruction and operational build conformance |
| Cache and optimization | Candidate reuse and transformation records | No verified substitution or optimization authority | Frozen legality/replay semantics and accepted verification |
| Extension profiles | Candidate identity/provenance records | No extension interpretation or implied capability grant | Frozen profile contracts, loading, adapters, effects, lowerings |

Direct Core structural-schema and public-rejection tests do not freeze an
instruction set or make direct Core receipts acceptable to the public validator.
No production or payload-selected Core adapter is installed.

The schema retains deliberately generic closed shapes for deferred first/second
lowering mappings; their kinds and diagnostics are not a new Core instruction or
compiler contract. Ordered paths, qualifier key paths, pass sequences, and argv
preserve multiplicity; reference inventories are duplicate-free. The structural
schema alone cannot enforce identity resolution, cardinality, or semantic legality.

## Validation and review

Use Python 3.11+ and the pinned model dependencies. Run the complete suite:

```sh
python -m pip install -r requirements-model.txt
python tools/check_invariants.py
python tools/check_model.py tests/fixtures/model/positive/*.json
python tools/trace_schema.py --check
python tools/check_trace.py tests/fixtures/trace/positive/*.json
python -m unittest discover -s tests -v
```

The CLI accepts one or more receipt paths. The public `validate(trace)` API returns
a result dictionary with `validation_kind = SYNTHETIC_RECEIPT_CONSISTENCY` and
`execution_conformance = false` on acceptance. The trace CLI's acceptance is
synthetic consistency only. Rejection tests should
include schema-valid but source-inconsistent records, wrong full owner paths,
truncated capability sets copied into multiple ledgers, missing or extra governing
scope references, suppressed evidence classes, ambiguous result bindings, broken
reciprocal joins, invalid event order, missing effect accounting, and unsupported
execution/evidence claims. Schema rejection tests alone cannot cover these checks.

Preserve all accepted historical invariant/model/serialization files and fixtures.
Do not broaden this foundation by silently admitting unsupported receipt kinds or
operations. Expanding executable acceptance requires an explicit reviewed contract,
accepted source adapters and verifiers, conformance fixtures, and truthful status
updates. The full [PR #5 gate](../ROADMAP.md#pr-5--execution-contract-trace-failure-and-provenance-foundation)
remains open and continues to block PR #7 and later executable research paths.
