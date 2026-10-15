# Core Invariants

This is the human-readable view of the first normative cross-cutting contract.
The authoritative statements and stable IDs are in
[`spec/core-invariants.json`](../spec/core-invariants.json), registry version 1.0.0.
This version is independent of the repository's immutable v1.0.0 documentation-foundation
release. This PR does not retag or reinterpret that historical release.

## Authority and requirement language

Only the statements inside the controlled blocks below and their identical domain-document
copies freeze the semantic invariants in this phase. This document's authority,
requirement-language, and change-control sections govern interpretation and maintenance
of that registry. The registry is authoritative if a copy disagrees; disagreement is a
validation failure that must be corrected, never permission to select a weaker statement.

MUST and MUST NOT express absolute requirements and prohibitions. SHOULD and SHOULD NOT
express recommendations whose deviation requires a documented justification and assessment
of consequences. MAY expresses permission, never a waiver of another requirement.
These meanings apply to uppercase terms in this normative contract. Ordinary prose,
examples, candidate layouts, and later roadmap descriptions are not additional frozen rules.

The contract constrains future conforming implementations. It does not claim that any
runtime, parser, data model, trace verifier, backend, or operational conformance suite
exists. Detailed field layouts and semantics deferred to later phases remain candidates;
a link to such a document does not normatively incorporate its whole contents.

## Compatibility and change control

IDs are permanent identities, independent of section order, file paths, and release tags.
Never renumber, recycle, or silently remove an ID. The checked-in initial snapshot at
`spec/history/core-invariants-1.0.0.json` is immutable history, not an editable expected-output
file. Historical releases and fixtures remain unchanged.

Every invariant change proposal must identify affected IDs, rationale, compatibility
classification, affected documents and tests, and migration consequences. Review must
explicitly assess scientific meaning, contracts, effects, authorization, failure,
epistemic class, and provenance. Passing textual checks is not semantic approval.

- Patch: editorial material outside frozen titles/statements, document placement, or tooling
  changes with unchanged normative meaning; update affected blocks and tests together.
- Minor: append new IDs without weakening, redefining, or removing an existing requirement.
  Additive obligations require an explicit opt-in to that newer registry version; do not
  retroactively claim that consumers of an older registry implement the additions.
- Major: any removal, weakening, strengthening of an existing requirement, or changed
  meaning requires an explicit new-major migration proposal retaining the old snapshot
  and ID history. A changed meaning receives a new ID with an explicit replacement mapping;
  old consumers remain bound to the version they adopted. This first validator deliberately
  rejects such changes until reviewed migration tooling and tests are supplied.

Normative wording/title edits, even intended as clarification, are rejected by the baseline
check. Explain and review them through the migration process rather than rewriting history
or bumping a version to evade the check. Registry versions do not freeze a language grammar,
Core instruction set, serialized data model, or an entire roadmap phase by implication.

## Validation coverage and limits

Run from the repository root with Python 3.11 or newer (standard library only):

```sh
python tools/check_invariants.py
python -m unittest discover -s tests -v
```

The validator checks strict registry fields and duplicate JSON keys; stable, unique, ordered
IDs; nonempty statements and document coverage; initial baseline compatibility; required
file existence; exactly one controlled block in each registered document; byte-equivalent
block text after universal newline decoding; and dangling `QM-INV-` three-digit references
in root and `docs/` Markdown files. Every registered domain copy contains the complete
statements assigned to it, not a manually abbreviated summary. The core view contains all IDs.

It deliberately parses no general Markdown: marker lines delimit plain generated text.
An accidental edit, missing/duplicate ID or block, orphan reference, or mismatched registered
statement fails. Files outside root Markdown and `docs/**/*.md`, arbitrary link anchors,
ordinary unmarked prose, examples, and semantic contradictions outside blocks are not
validated. Semantic review must check those areas. This is documentation agreement testing,
not execution-conformance testing, proof of security, or an implementation of the trace model.

To refresh blocks after a reviewed registry edit, use the `render_block` function in
`tools/check_invariants.py`; validation is read-only and never silently repairs drift.
Do not edit a generated block alone. The domain documents explain motivation and future
schemas; the controlled copy supplies their exact frozen cross-cutting requirements.

## Normative registry view

<!-- BEGIN QSOL CORE INVARIANTS -->

Registry version: 1.0.0

### QM-INV-001: Meaning before machinery

Transformations and backend selection MUST preserve the active semantic contract. Unsupported semantics MUST fail explicitly; a backend MUST NOT silently redefine, discard, or invent meaning.

### QM-INV-002: Canonical identity and ownership

Canonical JOB, DECK, and CARD identities, containment, source order, literal values, result bindings, types, units, qualifiers, semantic classes, and semantic/enforcement requirements MUST survive any boundary claiming semantic preservation, either directly or through an explicit frozen provenance-visible mapping. Local identifiers MUST be resolved with their complete owning context, not first-match lookup.

### QM-INV-003: Mandatory lowering boundaries

Semantic IR to QSOL-CORE and QSOL-CORE to Vector/Dataflow IR MUST be explicit independently specified and provenance-bearing boundaries. Backends MUST NOT bypass either applicable boundary or privately reinterpret source semantics. Vector/Dataflow IR MUST preserve the complete supported Core surface, including scalar operations, control, calls, effects, capabilities, machinery, epistemic bindings, failure behavior, and contracts.

### QM-INV-004: Lowering identity mappings

Each mandatory lowering MUST preserve or explicitly map result bindings with cardinality-aware, owner-qualified relations. Split/fusion and other non-identity mappings MUST use applicable frozen rules. Execution-relevant qualifiers, scoped contracts, extension requirements, machinery requirements, and epistemic bindings MUST remain attributable through preserved identity or explicit provenance-visible mappings; a copied label or IR hash alone MUST NOT substitute for required lineage.

### QM-INV-005: Scoped contract preservation

Result-determinism, numeric, randomness, failure-behavior, extension, and machinery requirements MUST retain their canonical owning scope. A representation MUST NOT silently flatten or relocate requirements or weaken a parent requirement. Composition and inheritance rules MUST be frozen before execution derives effective contracts.

### QM-INV-006: Nondeterminism disclosure

Result-determinism guarantees and randomness configuration MUST be distinct contract facets. Permitted nondeterministic behavior MUST be explicit in the source contract and trace. Reproducibility claims MUST identify the governed scope and material program, input, implementation, and execution-contract identities; portability MUST NOT be presented as universal byte identity.

### QM-INV-007: Numeric contracts

Numeric behavior MUST satisfy the explicit contract governing its scope. Tolerance, precision, rounding, denormals, reassociation, and other material numeric choices MUST NOT be silently changed by a backend or optimization. A tolerance-bounded result guarantee MUST identify the contract that defines permitted variation.

### QM-INV-008: Randomness and entropy

Reproducible seeded randomness MUST identify algorithm, version, seed, stream, and material partitioning or stream mapping. Fresh external entropy MUST be an explicit protected effect with contextual authorization and concrete acquisition provenance. A randomness mode MUST NOT itself grant permission.

### QM-INV-009: Epistemic non-promotion

Observation, assumption, simulation, derivation, test, validation, proof, and unclassified output MUST NOT be silently conflated or promoted. Each output MUST retain its applicable epistemic bindings and class-compatible evidence status. Evidence-bearing claims and class transitions MUST be justified by applicable frozen rules and passing evidence bound to the exact output and context before publication; operational success or AI output alone MUST NOT establish a stronger research claim.

### QM-INV-010: Explicit protected effects

External stateful interactions MUST be explicit effects. Each protected effect declaration MUST retain its stable owner-qualified identity and complete associated capability set. Every concrete protected attempt MUST have contextual authorization granting every required capability before the effect begins, with ordering evidence. Aggregate capability summaries MUST NOT replace the per-effect association or authorization.

### QM-INV-011: Separate machinery authorization

Protected machinery requirements MUST remain distinct from external effects and MUST NOT be encoded as synthetic effects merely for authorization. Every protected use MUST satisfy all applicable machinery capabilities before use begins and retain its concrete execution or genuine pre-execution scope, authorization ordering, and final executable selection decision. Denied or merely considered machinery MUST NOT be represented as executed.

### QM-INV-012: Small core and extension boundary

Backend-specific controls and optional operational profiles MUST remain behind explicit versioned backend or extension boundaries rather than silently expanding core semantics. Extension availability MUST NOT grant runtime capability authorization. Compiler backend selection, operating-environment profiles, and optional vendor controls MUST remain distinct concepts.

### QM-INV-013: Failure is semantic

Failure MUST be a structured outcome, not an implicit ordinary sentinel. A failed pure evaluation MUST NOT commit a partial result. Failure behavior and already observable effects MUST be preserved through execution, lowering, optimization, and tracing; target-language undefined behavior MUST NOT define QSOL semantics.

### QM-INV-014: Default fail-stop propagation

Unless an explicit frozen scoped policy handles the failure, an unhandled CARD failure MUST fail its DECK and stop later CARD execution, and an unhandled DECK failure MUST fail its JOB and prevent later DECKs from starting. Dependents MUST NOT consume failed, missing, or partial outputs as complete. Already committed effects and completed DECK history MUST remain recorded; retained partial artifacts MUST retain their status.

### QM-INV-015: Failure and effect ordering

Canonical sequencing MUST preserve source, effect, and failure ordering required by the active contract. Purity alone MUST NOT authorize reordering or dead-result elimination: a potentially failing operation remains observable under fail-stop. Dependency-only reordering or deletion solely because a result is unused MUST require purity and totality, unless a separately frozen rule preserves the original failure/effect observability and provenance.

### QM-INV-016: Concrete execution accounting

Canonical program membership MUST NOT be treated as concrete execution evidence. Every selected DECK and every CARD in a selected DECK execution MUST have an identified outcome/path record, including prevented, untaken, not-reached, and explicitly skipped paths. Legitimate lower-representation entry MUST instead retain actual representation-qualified operation executions and MUST NOT fabricate Semantic lineage. Non-reach and skips MUST retain validated typed causes and applicable rule/evidence.

### QM-INV-017: Unconditional effect accounting

For every selected concrete execution subject, each applicable declared effect MUST resolve to identified attempt(s), exactly one legitimate identified non-attempt, or structured failure. A detected omission of a reachable required effect MUST fail execution/conformance, never legitimize success. No profile, backend, optimization mode, or audit setting MAY disable this accounting.

### QM-INV-018: Per-attempt completion distinctions

Effect completion MUST be classified per concrete attempt independently of its enclosing outcome. Never begun, known completed, begun but cleanly aborted, observably partial, and genuinely unknown states MUST remain distinct. Known completion MUST take precedence over uncertainty about broader consequences. A begun attempt MUST NOT be classified as never started, and no attempt MUST NOT be confused with an identified never-started attempt.

### QM-INV-019: Inspectability and attributable provenance

Material inputs, outputs, effects, external tools, lowerings, scoped contracts, backend decisions, generated artifacts, and toolchain transformations MUST be inspectable and attributable to exact identities and concrete executions. Material content MUST be bound immutably or its unavailability and resulting claim limits explicitly disclosed. Required references MUST resolve with complete ownership and representation context, including in failure traces. Summaries and mutable locators MUST NOT replace required identity or lineage.

### QM-INV-020: Selection and fallback history

Backend-selection scopes and individual selection decisions MUST have distinct identities. Fallback MUST preserve the ordered predecessor, denial or rejection, applicable frozen fallback authority, passing context-bound evidence, and final decision rather than overwrite history. Selection provenance MUST identify the exact scope governed.

### QM-INV-021: Authorized semantic transitions

A requested-to-effective semantic contract change MUST require explicit accepted versioned or content-bound transition authority and passing evidence for the exact subject, requested/effective pair, owning scope, and active context before application. A generic mapping, recorded change, backend flag, or later success MUST NOT authorize the transition. Missing, inapplicable, unverifiable, or late authority/evidence MUST fail closed.

### QM-INV-022: Optimization and cache legality

An optimization or cache substitution MUST preserve the active semantic, numeric, determinism, randomness, failure, authorization, provenance, and evidence contracts. Verified reuse MUST have applicable frozen legality rules and passing current-context evidence before substitution. Effectful reuse MUST NOT skip effects or their boundaries without a separately frozen applicable replay/cache rule. An unverified hit MUST NOT supply a verified result.

### QM-INV-023: Lossless transport

A representation claiming semantic losslessness MUST round-trip all canonical identity, containment, source-order, value, dependency, result-binding, semantic, scoped-contract, and enforcement state. Canonical tagged sequencing MUST NOT be replaced by incomplete derived views. Human text parsing and lossless text serialization MUST await a frozen grammar and source mapping; architectural examples MUST NOT be treated as that grammar.

### QM-INV-024: Freeze before implementation

Operational Core, lowering, Vector/Dataflow, extension, and backend implementations MUST follow their applicable frozen specifications. The invariant registry MUST NOT be treated as an instruction set, data schema, grammar, execution engine, or authorization to implement later roadmap phases. Documentation MUST distinguish implemented behavior from design targets.

<!-- END QSOL CORE INVARIANTS -->
