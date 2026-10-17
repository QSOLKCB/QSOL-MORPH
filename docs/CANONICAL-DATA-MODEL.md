# Canonical Data Model 1.0.0

## Authority and deliberately bounded scope

PR #3 freezes the logical data model in this document and
[`spec/canonical-model.schema.json`](../spec/canonical-model.schema.json).
Both its closed structural schema and the cross-record rules below are required.
[`tools/check_model.py`](../tools/check_model.py) is the reference validator.
The [core invariants](CORE-INVARIANTS.md) continue to apply unchanged.
A disagreement between schema, prose, and implementation is a defect, not permission
to select the weaker interpretation. Changes to accepted meanings require an explicit
reviewed version/migration; unknown schema versions and fields fail closed.

This phase implements data validation only. It does not implement an instruction
set, evaluator, scheduler, optimizer, capability grant, external effect, backend,
lowering, execution ledger, evidence verifier, extension loader, or numeric-contract
interpreter. Success means **canonical-model conformance**, not that a program can
execute or that a research claim is true. Declaration completeness is relative to
this model: determining whether a verb actually performs undeclared effects requires
its later frozen operational contract and is not proved by this validator.

JSON files are inspectable validation fixtures for this logical model. The separately frozen [PR #4 serialization profile](CANONICAL-SERIALIZATION.md) owns
canonical bytes, key ordering, escaping, content fingerprints, JSONL/XML transport,
and lossless round trips. No serialization API or executable semantic-equivalence
hash is defined by this logical-model document. Human
`.qsl` grammar and source parsing remain deferred. Existing illustrative syntax and
candidate operational documents are not promoted wholesale into normative contracts.

## Representation and identity

A program is `{schema_version: "1.0.0", jobs: [...]}`. The program has one or more
JOBs; each JOB has one or more DECKs; each DECK has one or more CARDs. Arrays preserve
source containment and order. Empty programs/scopes are outside this initial profile.
JOBs are independently described workflows; this version does not define aggregate
execution or cross-JOB scheduling. Cross-JOB dependencies and sequencing are rejected.
The order of JOB records is retained, without claiming an inter-JOB runtime policy.

Each JOB, DECK, and CARD has an immutable-within-that-program local `id`. It is unique
among siblings, not globally unique. IDs are nonempty ASCII tokens starting with a
letter or underscore, followed by letters, digits, underscore, period, colon, or
hyphen, up to 256 characters. Case is significant. Validation does not generate,
renumber, trim, normalize, or sort identities. Changing a path changes the qualified
identity, even if the local ID is unchanged.

A CARD reference has exactly:

- `owner_scope_path`: the complete ordered three-element JOB / DECK / CARD path,
  each element `{scope_kind, scope_id}`;
- `producer_card_id`: exactly the terminal CARD ID.

It resolves in the current program only, using every path segment. No first-match,
relative, positional, missing-ancestor, or bare-ID lookup is permitted. A dependency
producer may additionally name `result_binding_id`; a value operand must do so.
Repeated local CARD IDs in different DECKs or JOBs remain distinct.

Declared effect identity is `(complete CARD path, effect_id)`. Machinery requirement
identity is `(complete owning JOB/DECK/CARD path, machinery_requirement_id)`. Local
requirement IDs can repeat at different owners; a child declaration never overwrites
an inherited declaration with the same local ID. Containment supplies declaration
ownership without redundant self-reported paths. Later external/cross-representation
references must also carry their representation identity; this self-contained model
never substitutes local IDs for that later content-bound identity.

## Field inventory

Every JOB, DECK, and CARD requires `id`, `machinery_requirements[]`, and
`extension_requirements[]`. Empty requirement arrays are explicit. They may contain
`source_location`, `result_determinism`, `numeric_contract`, `randomness_contract`,
and `failure_behavior` at their actual owning scope. JOB requires explicit
`result_determinism` and `randomness_contract`; children may inherit them.

JOB adds `decks[]`. DECK adds `cards[]`. CARD requires:

- `verb`, `noun`: case-sensitive declaration tokens, not a frozen instruction set;
- `operands[]`: ordered typed inputs, each with unique local `operand_id`;
- `result_bindings[]`: named produced values, possibly empty;
- `qualifiers[]`: named typed declaration values, possibly empty;
- `semantic_class`: an explicit class, including `UNCLASSIFIED`;
- `effect_requirements[]`: each external effect's own capability association;
- `dependencies[]`: explicit qualified producer references;
- `sequencing_constraints[]`: tagged predecessor constraints.

A CARD may also have a standalone typed `value`. This literal is independent of
operands and named results: preserving a result name/type/unit without the actual
literal value is not preservation. The validator neither computes results from
literals nor interprets the VERB/NOUN/qualifier vocabulary. Unknown structural fields
are rejected, rather than silently discarded. Future extension payload layouts,
compound/vector types, control structures, and additional sequencing tags require a
versioned model extension; arbitrary private backend fields are not an escape hatch.

## Source locations

An optional source location has nonempty `source_id` and inclusive `start` / exclusive
`end` positions, each with one-based integer `line` and `column`. End cannot precede
start; an empty span is allowed. Columns count Unicode scalar values in the identified
source, not bytes or display cells. `source_id` is an opaque source identity/locator;
this validator does not access it or verify source content. Source spans are metadata,
not a substitute for canonical identities, containment, or source order. Generated
records can omit locations rather than inventing source positions.

## Typed scalar values, operands, units, and results

A scalar value is exactly `{type, unit, value}`. Initial logical types are:

| Type | Value representation |
| --- | --- |
| `BOOLEAN` | JSON boolean |
| `INTEGER` | Exact base-ten integer string: `0` or optional minus and nonzero leading digit |
| `DECIMAL` | Exact finite base-ten decimal string, no exponent, plus sign, leading zeros, fractional trailing zeros, or negative zero; integer-shaped strings such as `"1"` are legal |
| `TEXT` | String, including empty string |

Numbers are strings to preserve exact logical values without imposing binary float
precision, overflow, or rounding semantics. `INTEGER "1"` and `DECIMAL "1"` retain
distinct declared types. NaN and infinity are not values in this profile. There is
no implicit numeric or text coercion. Byte encodings and machine types are deferred.

Units are case-sensitive symbolic IDs matching the schema's ASCII unit-token grammar.
`1` denotes dimensionless. BOOLEAN and TEXT must use `1`; numeric types may carry
another unit. Unit IDs are compared exactly; this phase does not infer dimensional
equivalence or convert aliases such as `K` and `kelvin`. User declarations remain
intact. A later frozen unit/type contract is required to interpret operations.

A literal operand is `{operand_id, value: <scalar value>}`. A bound operand is
`{operand_id, type, unit, producer_ref}` with a value-specific producer reference.
Its type and unit must exactly match the resolved result binding. Each bound operand
must have an explicit dependency on that same full producer path and binding ID;
a CARD-only dependency cannot stand in for it. Several operands may deliberately
consume the same binding; operand order and duplicate uses are preserved.

Each result binding is `{result_binding_id, type, unit, semantic_class}`. Binding IDs
are unique within their owning CARD. The class must match the CARD's class in this
initial profile; class transitions are unsupported. The class vocabulary is
`OBSERVATION`, `ASSUMPTION`, `PARAMETER`, `MODEL`, `SIMULATION`, `DERIVATION`, `TEST`,
`VALIDATION`, `PROOF`, `RESULT`, and `UNCLASSIFIED`. These are declarations, never
proof that a result exists, succeeded, or attained evidence status. Per-concrete-output
evidence and class-compatible status validation belongs to PR #5 and later execution
contracts. Merely labeling a CARD `PROOF` does not establish a theorem.

`qualifiers[]` and numeric `parameters[]` contain `{name, value: <scalar value>}`.
Names are unique and sorted. They preserve typed values without interpreting an
operational vocabulary. A later consumer must reject unsupported semantics; schema
acceptance does not authorize silently ignoring a qualifier.

## Scoped contract composition

The following rules are frozen conservatively for this version. They describe
compatibility of declarations, not execution or proof of realizability.

1. Result determinism is `STRICT`, `NUMERIC`, or `DECLARED-NONDETERMINISTIC`.
   Randomness is an independent facet, never another result-determinism enum value.
2. A JOB explicitly supplies both facets. An absent child facet inherits its nearest
   ancestor declaration for validation. Canonical data is not rewritten or flattened.
3. For result determinism, numeric contract, randomness contract, and failure behavior,
   a child declaration may repeat an inherited declaration **exactly**, or introduce
   a numeric contract where no ancestor declares one. Any different inherited facet
   is rejected, including an apparently stronger refinement. No implication lattice,
   tolerance comparison, RNG equivalence, or transition authority is invented here.
4. Every scope declaring or inheriting `NUMERIC` must already have a numeric contract
   at that scope or an ancestor. A JOB cannot defer that requirement to one child.
   A numeric contract includes `contract_id`, exact semantic `version`,
   `definition_hash` (`sha256:` plus 64 lowercase hex digits), and typed `parameters[]`.
   Equality includes the complete parameter set. Hashes identify externally defined
   contracts; this validator does not retrieve definitions or prove their meaning.
5. Randomness is `{mode}` for `NONE`, `EXTERNAL-ENTROPY`, or
   `DECLARED-NONDETERMINISTIC`. `SEEDED` additionally requires `rng_algorithm`,
   `rng_version`, nonnegative exact integer-string `seed`, `stream_id`, and explicit
   `parallel_partitioning` contract identity/version/hash. Even a sequential/no-split
   partitioning choice is explicit, preventing hidden partition defaults. No RNG or
   partition algorithm is implemented. A child cannot replace an inherited seed,
   stream, algorithm, partition contract, or mode.
6. The only failure policy is `{policy: "FAIL_STOP"}`. Omission has that same default
   identity at every scope; explicit declarations stay at their owners. Continue,
   retry, compensation, fallback, parallelism, and recovery are rejected until their
   own frozen contracts exist. No source transform may eliminate a potential failure.
7. Extension requirements accumulate through ancestors. Each record is
   `{profile_name, required_version, contract_id, definition_hash}`. Versions are
   exact three-component nonnegative semantic versions without ranges/prerelease/build
   suffixes in this profile. A descendant can add another profile or redeclare the
   identical complete record; changing any inherited profile requirement rejects.
   This freezes declaration composition, not the operational extension profiles.
8. Machinery requirements accumulate through ancestors **with their original owner
   paths**. All applicable requirements survive; a child never subtracts capabilities
   or replaces a parent's target requirement by reusing its local ID. Repeated local
   IDs at different scopes identify different declarations. Target interpretation,
   applicability, selection, and authorization remain future execution contracts.

An inherited requirement does not move to a child. A later effective-scope view must
retain every declaration owner and comply with these rules. Numeric/RNG identifiers,
versions, or hashes without available accepted definitions cannot establish executable
conformance. This validator verifies their shape and exact composition only.

## Effects and protected machinery

An effect requirement is `{effect_id, effect_kind, required_capabilities[]}`. A
machinery requirement is `{machinery_requirement_id, target_selector_or_class,
required_capabilities[]}`. Each capability set is nonempty, unique, and sorted.
These fields describe protected requirements only. A broad CARD/JOB capability union
is not accepted in their place. Effects are CARD-owned; machinery may be JOB-, DECK-,
or CARD-owned. Machinery selection is not synthesized as an external effect.

Effect kinds, target IDs, and capability IDs are declaration tokens whose operational
vocabularies are deferred. The validator does not infer a complete capability set
from a name, look up environmental grants, authorize a target, acquire entropy, or
execute an effect. Later operational validation must enforce the true complete set,
including RANDOM authorization for actual external-entropy acquisition. A randomness
mode merely records a contract; it never grants an effect or machinery capability.
Installing an extension likewise never grants a capability.

## Dependencies and conservative sequencing

A dependency is `{dependency_id, producer_ref}`. The producer reference resolves to
a CARD, optionally a named result of that CARD. Its producer must occur earlier in
the same JOB's source order (DECK order, then CARD order). Self, future, cyclic, and
cross-JOB references reject. Duplicate target references reject even under different
local dependency IDs. CARD-only and value-specific dependencies are distinct.

Each CARD's `sequencing_constraints[]` contains entries
`{constraint_id, kind, predecessor_ref}`. The predecessor is a full CARD reference
without a result binding. Every edge points from an earlier CARD in the same JOB to
the containing CARD. Kinds are `SOURCE_ORDER`, `EFFECT_ORDER`, and `FAILURE_ORDER`.
Duplicate `(kind, predecessor)` edges reject even under different constraint IDs.

The required minimum is deterministic:

- Every CARD after the first in a JOB carries `SOURCE_ORDER` and `FAILURE_ORDER`
  entries naming the immediately preceding CARD, including across DECK boundaries.
- Every effect-declaring CARD after the first effect-declaring CARD in a JOB carries
  `EFFECT_ORDER` naming that preceding effect-declaring CARD. Both endpoints must
  declare at least one effect.
- Additional well-formed backward edges with these tags may be retained. They cannot
  relax the mandatory chain. Constraint IDs are supplied stable identities, not
  synthesized or renumbered by validation.

This initial profile conservatively treats every CARD as potentially failing. It
has no purity/totality proof input and grants no reordering or deletion permission.
Thus `WRITE A; pure-but-failing DIV; WRITE B` remains ordered even across DECKs.
A claim of purity alone cannot omit failure-order edges. Future relaxation requires
its own frozen proof/ordering construct. No scheduler or optimizer is implemented.
Canonical tagged constraints are retained in full; derived effect/failure views are
not replacements. New tags require a model version that defines them.

## Deterministic logical ordering and validation

JOB/DECK/CARD arrays and operands retain their supplied source/argument order.
Other declaration arrays must be sorted by their stable local key: result bindings
by `result_binding_id`, qualifiers/parameters by `name`, effects by `effect_id`,
machinery by `machinery_requirement_id`, extensions by `profile_name`, dependencies
by `dependency_id`, constraints by `constraint_id`. Capability arrays sort by their
ASCII tokens. Keys are unique within each array. Object member order has no logical
meaning; deterministic byte/key order is reserved for PR #4. Validation never repairs,
reorders, defaults fields into, or otherwise mutates the supplied program.

Run with Python 3.11 or newer:

```sh
python -m pip install -r requirements-model.txt
python tools/check_invariants.py --base-ref <accepted-main-commit>
python tools/check_model.py tests/fixtures/model/positive/*.json
python -m unittest discover -s tests -v
```

Structural schema validation alone is insufficient. The reference validator also
checks uniqueness/order, exact containment references, type/unit and class bindings,
contract composition, backward dependencies, and the full required sequencing chain.
Fixture loading rejects duplicate JSON object keys and non-JSON numeric constants.
CLI errors return a nonzero status. Source/profile/contract locators are never fetched.
The schema is frozen byte-for-byte in `spec/history/canonical-model-1.0.0.schema.json`.
The validator checks its fixed digest and equality with the current 1.0.0 schema.
Future changes require an explicit reviewed version/migration rather than replacing
that history; the accepted-base invariant gate also preserves every accepted
`spec/history/` file. These checks do not prove prose or future code semantically
equivalent; normative changes still require review. The original invariant registry
and historical fixtures remain unchanged.
