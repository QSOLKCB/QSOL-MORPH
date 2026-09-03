# Contributing to QSOL-MORPH

QSOL-MORPH is currently specification-first and pre-alpha.

Contributions are welcome, but early changes should strengthen semantic clarity rather than race ahead into implementation.

## Current priority

The current sequence is:

1. document the architecture;
2. freeze core invariants;
3. define canonical data structures;
4. implement reference machinery;
5. optimize only after correctness boundaries exist.

See [ROADMAP.md](ROADMAP.md).

## Design expectations

A proposed change should explain:

- what semantic problem it solves;
- whether it belongs in core or an extension;
- what effects/capabilities it introduces;
- what determinism or numeric assumptions it requires;
- how it affects provenance;
- how a human and AI will interpret it;
- whether an existing primitive already expresses the same concept.

## Prefer small semantic changes

Avoid adding multiple synonyms, overlapping abstractions, or backend-specific concepts to the core.

A small orthogonal system is preferred over convenience-driven feature accumulation.

## Optimization changes

An optimization proposal must identify its reference semantics.

Performance alone is not sufficient. A faster result that violates the required semantic, numeric, determinism, provenance, or evidence contract is not considered an optimization.

## Backend changes

Backend-specific code should remain behind a clear lowering/profile boundary.

A backend must not silently redefine core operations.

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

Normative requirements will be introduced in the invariant-lock phase.

## Tests

Once executable code exists, changes should include the smallest tests that demonstrate:

- reference correctness;
- failure behavior;
- deterministic behavior where required;
- serialization/canonicalization stability where relevant;
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
