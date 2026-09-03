# Serialization

QSOL-MORPH should support one semantic model with multiple representations.

The representation may change. The meaning must not.

## Candidate representations

Possible forms include:

```text
.qsl      human-oriented QSOL source
.qdeck    canonical deck representation
.jsonl    streaming record interchange
.json     structured interchange
.xml      schema-oriented interchange
.qbin     compiled/binary representation
```

A MIDI 2.0 representation, if added, belongs to an explicit extension profile rather than the core serialization model.

File extensions are provisional until frozen by specification.

## Canonical semantic object

All supported serialization formats should map to the same canonical semantic objects:

```text
JOB
DECK
CARD
VERB
NOUN
OPERANDS
TYPES
UNITS
EFFECTS
DEPENDENCIES
```

A serializer must not invent meaning that does not exist in the semantic model.

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

## JSONL form

A streaming representation may resemble:

```json
{"verb":"OBSERVE","noun":"TEMPERATURE","value":294.3,"unit":"K"}
{"verb":"ASSUME","noun":"VACUUM","value":true}
{"verb":"SEED","noun":"RNG","value":18437}
{"verb":"RUN","noun":"PROJECTILE"}
```

JSONL is attractive for:

- streaming;
- logs;
- AI/tool interchange;
- line-addressable transformations;
- append-oriented traces.

## JSON form

Canonical JSON may represent full jobs/decks with explicit schema/specification identity.

If used for hashing, canonical JSON requires strict rules for:

- field ordering;
- number formatting;
- Unicode handling;
- escaping;
- omitted versus null fields;
- map ordering.

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

XML is an interchange profile, not the preferred human authoring syntax.

## Binary form

A binary representation may eventually improve startup time, storage efficiency, or direct runtime loading.

A binary form should include enough versioning to avoid interpreting bytes under the wrong semantic contract.

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

Formatting metadata need not round-trip unless explicitly included in the representation contract.

## Canonical hashing

Hashes should be computed over a defined canonical representation or semantic canonicalization process.

Do not hash incidental whitespace and then call the digest a semantic identity unless source-text identity is specifically the object being bound.

## Versioning

Serialized forms should identify the specification/schema version needed for interpretation.

A future reader must be able to determine whether a deck was written under:

- an older compatible version;
- a newer unsupported version;
- a version requiring migration.

## Migration

Semantic migrations should be explicit and inspectable.

A migration tool should ideally report changed cards/fields and distinguish:

- pure representation updates;
- semantic changes requiring human review.

## Principle

> One meaning, many transports. Canonicalize before you hash. Version before you freeze.
