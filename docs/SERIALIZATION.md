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

All supported **lossless** serialization formats must map to the same complete canonical semantic objects, including their containment and canonical source/order relationships.

The shared serialized object model must be able to carry, where applicable:

```text
PROGRAM
  JOBS[]
    JOB
      JOB_ID
      RESULT_DETERMINISM_CONTRACT?
      NUMERIC_CONTRACT?
      RANDOMNESS_CONTRACT?
      MACHINERY_REQUIREMENTS[]
      EXTENSION_REQUIREMENTS[]
      FAILURE_BEHAVIOR?
      DECKS[]
        DECK
          DECK_ID
          RESULT_DETERMINISM_CONTRACT?
          NUMERIC_CONTRACT?
          RANDOMNESS_CONTRACT?
          MACHINERY_REQUIREMENTS[]
          EXTENSION_REQUIREMENTS[]
          FAILURE_BEHAVIOR?
          CARDS[]
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
              MACHINERY_REQUIREMENTS[]
                MACHINERY_REQUIREMENT_ID
                TARGET_SELECTOR_OR_CLASS
                REQUIRED_CAPABILITIES[]
              RESULT_DETERMINISM_CONTRACT
              NUMERIC_CONTRACT
              RANDOMNESS_CONTRACT
              DEPENDENCIES
              SEQUENCING_CONSTRAINTS[]
                CONSTRAINT_ID?
                CONSTRAINT_KIND
                PREDECESSOR_ID_OR_SCOPE
                SUCCESSOR_ID_OR_SCOPE
                RULE_ID?
                METADATA?
              FAILURE_BEHAVIOR
              EXTENSION_REQUIREMENTS[]
                PROFILE_NAME
                REQUIRED_VERSION_OR_RANGE
                CONTRACT_ID_OR_HASH?
              SOURCE_IDENTITY / LOCATION
SCHEMA / SPECIFICATION VERSION
```

`JOBS[]`, `DECKS[]`, and `CARDS[]` are not decorative nesting. They preserve the canonical containment relation and, where the frozen semantic model makes order observable or canonical, the deterministic order of children within their parent. Stable IDs alone do not establish which DECK belongs to which JOB, which CARD belongs to which DECK, or the canonical order of siblings.

A lossless flattened or streaming representation may encode the same relation without physical nesting only if it carries an explicit frozen equivalent, for example:

```text
JOB_ID
DECK_ID + PARENT_JOB_ID + DECK_ORDER_INDEX
CARD_ID + PARENT_DECK_ID + CARD_ORDER_INDEX
```

or another normative representation that permits unique deterministic reconstruction of the same containment and order. Record adjacency, parse order, filename, or coincidental ID sorting is not a valid implicit parent/order rule unless a future frozen serialization profile explicitly defines it as canonical.

`JOB_ID`, `DECK_ID`, and `CARD_ID` are stable canonical identities, not presentation labels. Dependencies, producer references, failure records, effect attempts, lowering maps, and provenance edges may refer to these identities, so a lossless serializer must preserve them exactly according to the frozen canonical model.

Scoped `RESULT_DETERMINISM_CONTRACT`, `NUMERIC_CONTRACT`, and `RANDOMNESS_CONTRACT` fields remain attached to the canonical JOB, DECK, or CARD that owns them. A serializer must not flatten a DECK-wide requirement into arbitrary CARD records or silently discard a JOB-wide requirement merely because every child happens to be serializable without it.

Scoped `EXTENSION_REQUIREMENTS[]` likewise remain attached to the JOB, DECK, or CARD that declares them. A serializer must not relocate a JOB- or DECK-wide profile requirement to an arbitrary child CARD merely to fit a representation. The owning scope is part of the lossless semantic association.

`RESULT_BINDING` is the canonical `Card.result?` identity naming the value produced by a CARD when that field is present. It is distinct from the produced value itself: a lossless serializer must preserve both the data and the identity that dependent CARDs reference.

`QUALIFIERS` includes canonical CARD modifiers that affect execution or lowering, such as explicit target-selection, adapter, tuning, or extension-control qualifiers. Lossless formats must retain them exactly according to the frozen canonical model.

`EFFECT_REQUIREMENTS[]` preserves the canonical association between each protected external effect and the complete capability set required for that effect. A serializer must not flatten several effect-specific capability sets into one ambiguous CARD-level union.

`MACHINERY_REQUIREMENTS[]` preserves the separate association between protected machinery access and the complete capability set required before that machinery may be used. Each requirement keeps its stable `MACHINERY_REQUIREMENT_ID`, target selector/class, and capability set. Machinery requirements must not be serialized as synthetic external effects merely to reuse the effect schema.

`SEQUENCING_CONSTRAINTS[]` is the canonical lossless ordering field corresponding to Semantic-IR `sequencing_constraints[]`. Each entry carries a frozen/tagged `CONSTRAINT_KIND` sufficient to distinguish source-order, effect-order, failure-order, or any later normative sequencing class without replacing the canonical field with parallel arrays. `EFFECT_ORDER_CONSTRAINTS` and `FAILURE_ORDER_CONSTRAINTS`, if exposed by tooling, are deterministic projections/views of tagged canonical sequencing records rather than alternative serialized state. A lossless representation must preserve every sequencing entry, including kinds that are neither effect-order nor failure-order.

`EXTENSION_REQUIREMENTS[]` preserves each required profile together with the exact version/range and contract identity needed to interpret that profile's syntax, qualifiers, effects, or lowering hooks. Separate parallel lists of extension names and version requirements are not lossless because they can lose which requirement belongs to which profile. JOB-, DECK-, and CARD-scoped requirements use the same structured tuple while retaining the canonical scope that owns each entry.

`FAILURE_BEHAVIOR` preserves any explicit CARD/DECK/JOB recovery, continuation, fail-stop, compensation, or other frozen failure policy present in the semantic model. It must not disappear and silently revert to a default during transport.

A serializer must not invent meaning that does not exist in the semantic model, and a lossless serializer must not discard enforcement fields that determine whether or how a program may execute.

In particular, round-tripping a JOB/DECK must not silently lose JOB→DECK→CARD containment/order, stable JOB/DECK/CARD identities, scoped determinism/numeric/randomness contracts, scoped extension requirements, result bindings, qualifiers, effect-to-capability bindings, machinery-to-capability bindings, failure behavior, permissions, extension-profile/version/contract associations, target/control modifiers, dependencies, or canonical sequencing constraints.

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

Human-readable shorthand may omit fields only when the parser can reconstruct them unambiguously from that active frozen text-profile specification. Canonical serialization must retain the resolved semantic values, stable object identities, containment/order, and result bindings.

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

If JSONL claims semantic losslessness, stable JOB/DECK/CARD identities, explicit parent containment, deterministic sibling/source-order identity, result bindings, scoped contract metadata, scoped JOB/DECK/CARD extension requirements, machinery requirements, canonical tagged sequencing constraints, and enforcement metadata must be represented either on the relevant records or through explicitly linked metadata records. A flat JSONL stream must not infer ownership solely from record adjacency.

## JSON form

Canonical JSON may represent full jobs/decks with explicit schema/specification identity and all canonical enforcement fields.

If used for hashing, canonical JSON requires strict rules for:

- field ordering;
- number formatting;
- Unicode handling;
- escaping;
- omitted versus null fields;
- stable JOB/DECK/CARD identifier representation;
- deterministic `JOBS[]` / `DECKS[]` / `CARDS[]` containment and ordering, or an explicitly frozen equivalent parent/order encoding;
- result-binding representation;
- map ordering;
- canonical qualifier maps;
- deterministic effect-requirement ordering;
- deterministic machinery-requirement ordering;
- deterministic ordering of each `required_capabilities[]` set;
- deterministic ordering and tagged representation of `sequencing_constraints[]`;
- canonical failure-behavior representation;
- canonical scoped contract identifiers;
- deterministic representation and ordering of scoped `extension_requirements[]`, including owning scope and each profile's bound version/range and contract identity.

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

This is an illustrative fragment only. A lossless XML profile must also preserve every applicable canonical field, including explicit JOB→DECK→CARD containment and sibling/source order, stable JOB/DECK/CARD identities, result bindings, qualifiers, effect/capability bindings, machinery/capability bindings, failure behavior, canonical tagged sequencing constraints, enforcement fields, scoped extension-profile/version/contract associations, and scoped JOB/DECK contracts.

XML is an interchange profile, not the preferred human authoring syntax.

## Binary form

A binary representation may eventually improve startup time, storage efficiency, or direct runtime loading.

A binary form should include enough schema, specification, explicit JOB→DECK→CARD containment/order, stable JOB/DECK/CARD identity, scoped extension requirement/profile/version/contract association, result-binding, qualifier, effect-binding, machinery-requirement, failure-behavior, canonical sequencing-constraint, and scoped contract identity to avoid interpreting bytes under the wrong semantic, dependency, target-control, failure, authorization, ordering, or provenance model.

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

Equality here includes hierarchy-, execution-, dependency-, and reference-relevant fields. Two representations are not semantically equal if one loses, changes, or defaults any JOB→DECK→CARD containment/order relation, stable JOB/DECK/CARD identity, result binding, qualifier, effect requirement, machinery requirement, per-requirement capability set, failure behavior, scoped determinism, scoped numeric, scoped randomness, scoped extension requirement/profile-version-contract association, dependency, or tagged sequencing constraint.

Formatting metadata need not round-trip unless explicitly included in the representation contract.

## Canonical hashing

Hashes should be computed over a defined canonical representation or semantic canonicalization process.

Do not hash incidental whitespace and then call the digest a semantic identity unless source-text identity is specifically the object being bound.

Canonical JOB→DECK→CARD containment/order, stable JOB/DECK/CARD identities, result bindings, qualifiers, effect requirements, machinery requirements, per-requirement capability sets, explicit failure behavior, canonical sequencing constraints, scoped contract identities, and scoped extension requirement/profile-version-contract associations that affect execution, dependency, authorization, ordering, or provenance meaning must contribute to semantic identity according to the frozen canonicalization rules.

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
- JOB/DECK/CARD containment or sibling/source-order changes;
- JOB/DECK/CARD identity changes;
- result-binding/dependency changes;
- qualifier/target-control changes;
- effect/capability-binding changes;
- machinery/capability-binding changes;
- sequencing-constraint changes;
- failure-behavior changes;
- permission/capability changes;
- JOB/DECK/CARD determinism/numeric/randomness contract changes;
- scoped extension requirement/version/contract changes.

A migration must not silently manufacture, discard, detach, relocate, reorder, or renumber a JOB→DECK→CARD hierarchy relation, stable JOB/DECK/CARD identity, result binding, extension requirement, execution authorization requirement, failure policy, sequencing constraint, target-control qualifier, machinery requirement, or scientific contract merely to make an old deck parse.

## Principle

> One meaning, many transports. Preserve hierarchy as well as identity, freeze source grammar before implementing it, round-trip every semantic field, canonicalize before you hash, and version before you freeze.