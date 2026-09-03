# Contributing to QSOL-MORPH

QSOL-MORPH is currently specification-first and pre-alpha.

Contributions are welcome, but early changes should strengthen semantic clarity rather than race ahead into implementation.

## Current priority

The current sequence is intentionally specification-first:

1. document the architecture;
2. freeze cross-cutting core invariants;
3. define the canonical semantic data model and lossless serialization;
4. define the execution-contract, trace, failure, authorization, and provenance foundation;
5. freeze QSOL-CORE operational semantics;
6. implement the QSOL-CORE reference machine against those frozen semantics;
7. freeze the Semantic IR → QSOL-CORE lowering contract;
8. implement and validate the reference Semantic-to-Core lowering;
9. define the full semantics-preserving Vector/Dataflow IR used by backend lowering;
10. implement reference MORPH backends only after the preceding contracts exist;
11. optimize only after reference correctness and failure/effect boundaries are testable.

See [ROADMAP.md](ROADMAP.md) for the authoritative staged plan. A contributor-facing summary must not be used to skip a normative phase.

## Design expectations

A proposed change should explain:

- what semantic problem it solves;
- whether it belongs in core or an extension;
- what effects/capabilities it introduces;
- what determinism, randomness, or numeric assumptions it requires;
- how failure, totality, and ordering are affected;
- how it affects provenance;
- which lowering boundary owns the transformation;
- how a human and AI will interpret it;
- whether an existing primitive already expresses the same concept.

## Prefer small semantic changes

Avoid adding multiple synonyms, overlapping abstractions, or backend-specific concepts to the core.

A small orthogonal system is preferred over convenience-driven feature accumulation.

## Optimization changes

An optimization proposal must identify its reference semantics.

Performance alone is not sufficient. A faster result that violates the required semantic, numeric, determinism, randomness, failure-order, authorization, provenance, or evidence contract is not considered an optimization.

An optimization must not erase an observable failure merely because the failed operation's result is unused. In particular, dead-result elimination is legal only for operations proven pure and total under the active contract, unless the original failure is preserved at the same observable point.

## Backend changes

Backend-specific code should remain behind a clear lowering/profile boundary.

A backend must not silently redefine core operations or invent Semantic IR → QSOL-CORE meaning that belongs to an earlier frozen lowering specification.

The mandatory Vector/Dataflow IR stage must preserve the complete supported QSOL-CORE surface, including control, calls, effects, capabilities, sequencing, failure behavior, and execution contracts. A backend must not bypass that stage for non-vector operations merely because they are not optimization candidates.

## Research semantics

Do not collapse distinctions such as:

```text
OBSERVATION
ASSUMPTION
SIMULATION
DERIVATION
VALIDATION
PROOF
```

If a change upgrades epistemic status, the transition must be explicit and justified by the specification.

## Documentation

During the documentation-foundation phase, mark illustrative syntax clearly. Do not present planned functionality as implemented functionality.

Normative requirements will be introduced in their roadmap phases. Documentation summaries must remain consistent with those phases and must not imply that reference machinery precedes its governing specifications.

## Tests

Once executable code exists, changes should include the smallest tests that demonstrate:

- reference correctness;
- Semantic IR → QSOL-CORE lowering conformance where relevant;
- failure behavior and per-effect-attempt provenance;
- deterministic behavior where required;
- serialization/canonicalization stability where relevant;
- full-IR preservation of control/effect contracts where relevant;
- backend equivalence under the active contract.

## Pull requests

Prefer focused PRs with one architectural objective.

A PR description should state:

- intent;
- scope;
- non-goals;
- semantic impact;
- validation performed;
- follow-up work.

## License

By contributing, you agree that your contribution may be distributed under the repository's Apache License 2.0 terms.
