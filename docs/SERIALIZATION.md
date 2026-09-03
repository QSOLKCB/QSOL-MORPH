# Serialization

QSOL-MORPH should support one semantic model with multiple representations.

The representation may change. The meaning must not.

## Candidate representations

Possible forms include:

```text
.qsl      human-oriented QSOL source, deferred until grammar freeze
.qdeck    canonical deck representation
.jsonl    streaming record interchange
.json     structured interchange
.xml      schema-oriented interchange
.qbin     compiled/binary representation
```

A MIDI 2.0 representation, if added, belongs to an explicit extension profile rather than the core serialization model.

File extensions are provisional until frozen by specification.

The initial canonical-serialization implementation phase must **not** invent the `.qsl` grammar. Human-oriented QSOL source requires a separate normative grammar/profile plus a frozen source-to-Semantic-IR mapping before a parser or lossless text serializer is implemented. Until then, `.qsl` examples in this repository are illustrative architecture sketches only.

## Canonical semantic object

All supported **lossless** serialization formats must map to the same complete canonical semantic objects.

The shared serialized object model must be able to carry, where applicable:

```text
JOB
  JOB_ID
DECK
  DECK_ID
CARD
  CARD_ID
VERB
NOUN
OPERANDS
RESULT_BINDING
VALUES
TYPES
UNITS
QUALIFIERS
SEMANTIC_CLASS
EFFECT_REQUIREMENTS[]
  EFFECT_ID
  EFFECT_KIND
  REQUIRED_CAPABILITIES[]
RESULT_DETERMINISM_CONTRACT
NUMERIC_CONTRACT
RANDOMNESS_CONTRACT
DEPENDENCIES
EFFECT_ORDER_CONSTRAINTS
FAILURE_ORDER_CONSTRAINTS
FAILURE_BEHAVIOR
EXTENSION_REQUIREMENTS[]
  PROFILE_NAME
  REQUIRED_VERSION_OR_RANGE
  CONTRACT_ID_OR_HASH?
SOURCE_IDENTITY / LOCATIONS
SCHEMA / SPECIFICATION VERSION
```

`JOB_ID`, `DECK_ID`, and `CARD_ID` are stable canonical identities, not presentation labels. Dependencies, producer references, failure records, effect attempts, lowering maps, and provenance edges may refer to these identities, so a lossless serializer must preserve them exactly according to the frozen canonical model.

`RESULT_BINDING` is the canonical `Card.result?` identity naming the value produced by a CARD when that field is present. It is distinct from the produced value itself: a lossless serializer must preserve both the data and the identity that dependent CARDs reference.

`QUALIFIERS` includes canonical CARD modifiers that affect execution or lowering, such as explicit target-selection, adapter, tuning, or extension-control qualifiers. Lossless formats must retain them exactly according to the frozen canonical model.

`EFFECT_REQUIREMENTS[]` preserves the canonical association between each protected effect and the complete capability set required for that effect. A serializer must not flatten several effect-specific capability sets into one ambiguous CARD-level union.

`EXTENSION_REQUIREMENTS[]` preserves each required profile together with the exact version/range and contract identity needed to interpret that profile's syntax, qualifiers, effects, or lowering hooks. Separate parallel lists of extension names and version requirements are not lossless because they can lose which requirement belongs to which profile.

`FAILURE_BEHAVIOR` preserves any explicit CARD/DECK/JOB recovery, continuation, fail-stop, compensation, or other frozen failure policy present in the semantic model. It must not disappear and silently revert to a default during transport.

A serializer must not invent meaning that does not exist in the semantic model, and a lossless serializer must not discard enforcement fields that determine whether or how a program may execute.

In particular, round-tripping a JOB/DECK must not silently lose stable JOB/DECK/CARD identities, result bindings, qualifiers, effect-to-capability bindings, failure behavior, permissions, determinism requirements, numeric tolerances, randomness requirements, extension-profile/version/contract associations, target/control modifiers, or sequencing constraints.

## Human form

Illustrative source:

```text
OBSERVE TEMPERATURE 294.3 K
ASSUME VACUUM TRUE
SEED RNG 18437
RUN PROJECTILE
TRACE ALL
LOCK RESULT
```

The human form should optimize readability and semantic regularity.

This syntax is **not** an implementation target for the initial canonical-serialization phase. A future normative QSOL text-profile specification must freeze lexical/grammar rules, shorthand/default reconstruction, source-to-Semantic-IR mapping, diagnostics, and canonical text rendering before `.qsl` parsing/serialization is implemented.

Human-readable shorthand may omit fields only when the parser can reconstruct them unambiguously from that active frozen text-profile specification. Canonical serialization must retain the resolved semantic values, stable object identities, and result bindings.

## JSONL form

A streaming representation may resemble:

```json
{"verb":"OBSERVE","noun":"TEMPERATURE","value":294.3,"unit":"K"}
{"verb":"ASSUME","noun":"VACUUM","value":true}
{"verb":"SEED","noun":"RNG","value":18437}
{"verb":"RUN","noun":"PROJECTILE"}
```

These examples are deliberately incomplete sketches, not the canonical JSONL schema.

JSONL is attractive for:

- streaming;
- logs;
- AI/tool interchange;
- line-addressable transformations;
- append-oriented traces.

If JSONL claims semantic losslessness, stable JOB/DECK/CARD identities, result bindings, contract metadata, and enforcement metadata must be represented either on the relevant records or through explicitly linked JOB/DECK metadata records whose scope and identity are deterministic.

## JSON form

Canonical JSON may represent full jobs/decks with explicit schema/specification identity and all canonical enforcement fields.

If used for hashing, canonical JSON requires strict rules for:

- field ordering;
- number formatting;
- Unicode handling;
- escaping;
- omitted versus null fields;
- stable JOB/DECK/CARD identifier representation;
- result-binding representation;
- map ordering;
- canonical qualifier maps;
- deterministic effect-requirement ordering;
- deterministic ordering of each `required_capabilities[]` set;
- canonical failure-behavior representation;
- canonical contract identifiers;
- deterministic representation and ordering of `extension_requirements[]`, including each profile's bound version/range and contract identity.

A normal pretty-printed JSON document should not be assumed canonical merely because it parses.

## XML form

XML may provide useful schema-oriented interchange for institutional/scientific systems.

Illustrative card:

```xml
<card verb="OBSERVE" noun="TEMPERATURE">
  <value>294.3</value>
  <unit>K</unit>
</card>
```

This is an illustrative fragment only. A lossless XML profile must also preserve every applicable canonical field, including stable JOB/DECK/CARD identities, result bindings, qualifiers, effect/capability bindings, failure behavior, enforcement fields, extension-profile/version/contract associations, and scoped JOB/DECK contracts.

XML is an interchange profile, not the preferred human authoring syntax.

## Binary form

A binary representation may eventually improve startup time, storage efficiency, or direct runtime loading.

A binary form should include enough schema, specification, stable JOB/DECK/CARD identity, extension requirement/profile/version/contract association, result-binding, qualifier, effect-binding, failure-behavior, and contract identity to avoid interpreting bytes under the wrong semantic, dependency, target-control, failure, authorization, or provenance model.

## Round-trip requirement

Where a representation claims semantic losslessness, conversion should satisfy conceptually:

```text
semantic object
    ↓ serialize
representation
    ↓ parse
semantic object'

semantic object == semantic object'
```

Equality here includes execution-relevant, dependency-relevant, and reference-relevant fields. Two representations are not semantically equal if one loses, changes, or defaults any stable JOB/DECK/CARD identity, result binding, qualifier, effect requirement, per-effect capability set, failure behavior, determinism, numeric, randomness, extension requirement/profile-version-contract association, dependency, effect-order, or failure-order contract.

Formatting metadata need not round-trip unless explicitly included in the representation contract.

## Canonical hashing

Hashes should be computed over a defined canonical representation or semantic canonicalization process.

Do not hash incidental whitespace and then call the digest a semantic identity unless source-text identity is specifically the object being bound.

Stable JOB/DECK/CARD identities, result bindings, qualifiers, effect requirements, per-effect capability sets, explicit failure behavior, contract identities, and extension requirement/profile-version-contract associations that affect execution, dependency, or provenance meaning must contribute to semantic identity according to the frozen canonicalization rules.

## Versioning

Serialized forms should identify the specification/schema version needed for interpretation.

A future reader must be able to determine whether a deck was written under:

- an older compatible version;
- a newer unsupported version;
- a version requiring migration;
- extension contracts whose required versions are unavailable or incompatible.

## Migration

Semantic migrations should be explicit and inspectable.

A migration tool should ideally report changed cards/fields and distinguish:

- pure representation updates;
- semantic changes requiring human review;
- JOB/DECK/CARD identity changes;
- result-binding/dependency changes;
- qualifier/target-control changes;
- effect/capability-binding changes;
- failure-behavior changes;
- permission/capability changes;
- determinism/numeric/randomness contract changes;
- extension requirement/version/contract changes.

A migration must not silently manufacture, discard, detach, or renumber a stable JOB/DECK/CARD identity, result binding, extension requirement, execution authorization, failure policy, target-control qualifier, or scientific contract merely to make an old deck parse.

## Principle

> One meaning, many transports. Freeze source grammar before implementing it, round-trip every semantic field, canonicalize before you hash, and version before you freeze.
