# Canonical Serialization 1.0.0

## Authority and scope

This document and `spec/serialization-profile.json` freeze roadmap PR #4's
canonical JSON, record-streaming JSONL, and XML interchange encodings of the
complete [Canonical Data Model 1.0.0](CANONICAL-DATA-MODEL.md). The reference
implementation is `tools/serialization.py`. Model schema, cross-record validation,
core invariants, and accepted historical fixtures remain unchanged. A disagreement
between this contract, the profile, fixtures, and implementation is a defect.

The transport version is distinct from the model's `schema_version`. Unknown
versions and fields fail closed. The profile has an immutable history copy in
`spec/history/serialization-profile-1.0.0.json`. Changing canonical bytes requires
an explicit reviewed transport version/migration; it must not rewrite history.

This is data transport only: no human `.qsl` grammar, runtime, lowering, evaluator,
backend, authorization, profile retrieval, or semantic-equivalence proof. The
broader examples in `SERIALIZATION.md` remain candidate material except for its
controlled invariant statements. This profile serializes only the frozen model,
not candidate operational fields that the model does not yet admit.

## Losslessness and equality

A serializer MUST validate the complete model before emitting a successful
transport. A reader MUST reconstruct and validate the complete model before
returning it. All explicit fields, absences, types, values, stable identities,
ordered nesting, metadata, and declaration ownership survive. Object key order
has no model meaning; every array retains its exact order and multiplicity.
There is no sorting or repair of invalid declaration arrays, default insertion,
contract flattening, ID renaming, capability union, Unicode normalization, unit
conversion, or weakening of tagged source/effect/failure constraints. Missing
versus explicit default declarations remain different content identities.

The round-trip relation compares complete logical trees: objects by key/value,
arrays by ordered elements, strings by their exact code-point sequences, booleans
by boolean value, and source-position numbers by exact mathematical integer value.
JSON Schema permits integer-valued JSON numbers such as `1.0` or `1e0` for source
positions; they have the same logical integer value as `1`. Canonical output uses
integer notation. An ordinary model JSON importer parses these exactly, never
through binary floating-point rounding. Typed INTEGER/DECIMAL values and RNG seeds
are strings and are never numerically rewritten. The Python API accepts finite
integral floats according to their actual stored value, not their original token;
callers requiring decimal-token fidelity must use the exact JSON importer.

## Wire-model string encoding

The frozen model validator accepts every Python string code point, including lone
surrogates and literal surrogate pairs. A standard JSON escaped surrogate pair
normally decodes to one supplementary Unicode scalar; XML cannot directly carry
all these strings (or NUL). Narrowing that accepted domain would break the model.

Before transport, recursively encode a model string containing ANY code point
in U+D800..U+DFFF as exactly `{"$qsol_string":[N,...]}`. The array is the complete
ordered string, each N the integer code point (0..1114111). At least one surrogate
is mandatory; ordinary strings MUST NOT use this tag. Booleans are not integers
here. All other strings stay strings. A tag has exactly one key; malformed,
empty, extra-field, out-of-range, or ordinary-only tags reject. Literal text that
looks like a tag stays literal text, without recursive reparsing.

This tag cannot collide with valid model objects: the closed frozen schema admits
no object with `$qsol_string`. Restore tags before model validation. Direct
surrogates outside tags reject. Ordinary supplementary scalar characters and
explicit two-code-point surrogate strings therefore have distinct encodings.
Model object keys are the fixed ASCII schema keys; these are not transformed.

Consumers MUST use this profile decoder. An ordinary JSON parser sees the
transport envelope and exceptional-string tags, not necessarily a raw model.
The separate ordinary-model importer follows JSON's escaped-pair interpretation;
it does not claim to reconstruct a pre-JSON language object's surrogate sequence.

## Canonical JSON

The envelope has exactly `format: "QSOL-MORPH-JSON"`,
`serialization_version: "1.0.0"`, and `model: <wire model>`.

Canonical bytes are ASCII (also UTF-8), no BOM, no trailing LF, and no whitespace
outside strings. Object keys sort lexicographically by Unicode code point (all
profile keys are ASCII). Arrays retain their supplied order. Separators are `,`
and `:`. Boolean tokens are `true`/`false`. Integer numbers use shortest decimal
notation, no plus, leading zero, fraction, or exponent. Null is not in the model.

Strings use double quotes. Quote and backslash escape as `\"` and `\\`; backspace,
form feed, LF, CR, and tab use `\b`, `\f`, `\n`, `\r`, `\t`. Other U+0000..U+001F
and every code point at or above U+007F use lowercase hexadecimal `\uXXXX`, with
supplementary scalars represented by a high/low surrogate escape pair. U+0020..U+007E
otherwise emit literally, including `/`. Exceptional model surrogates have already
become integer tags, so they cannot be confused with escaped supplementary scalars.
This is this project's canonical profile, not a claim of RFC 8785 conformance.

Strict readers reject duplicate keys, invalid UTF-8, non-JSON numbers, trailing
content, unknown envelope/model fields, and any byte sequence differing from the
canonical reserialization. Pretty JSON and alternative escapes belong to ordinary
model import, not to the strict canonical transport reader.

## Content fingerprint

`sha256:` followed by lowercase hexadecimal SHA-256 of the entire canonical JSON
envelope is the profile's content fingerprint. No self-hash is embedded in that
envelope. JSONL/XML readers reconstruct this same model and fingerprint. It binds
transport version, model version, metadata, all explicit fields, and order.

It is NOT an executable semantic-equivalence hash, signature, authorization,
provenance receipt, or proof of a research claim. Distinct explicit default fields
or source locations produce distinct identities. Later provenance schemas must
identify this profile when consuming its fingerprints; this PR does not implement
those schemas or fill candidate IR/provenance fields opportunistically.

## JSONL record stream

Each line is exactly one canonical JSON object using the byte rules above, followed
by one LF. No blank lines, CRLF, BOM, extra whitespace, or unterminated last line.
The stream has exactly:

1. Header: `format: "QSOL-MORPH-JSONL"`, `serialization_version: "1.0.0"`,
   `schema_version: "1.0.0"`, `job_count: N`, where N is a positive integer.
2. N JOB records: `index: I`, `job: <complete wire-model JOB>`, in consecutive
   zero-based index order 0..N-1.
3. End: `end: true`, `job_count: N`, `model_sha256: <content fingerprint>`.

Each record has exactly the stated fields. The index explicitly defines JOB
source order; duplicate, missing, swapped, or out-of-order indexes reject.
Nested DECK/CARD arrays retain exact ownership and sibling order. All qualified
references retain their complete typed paths. Nothing relies on bare local IDs,
implicit flat-record adjacency, positional pairing of associations, or ID sorting.
This profile explicitly freezes the indexed JOB ordering and nested array ordering.

Header count, end count, digest, end presence, and EOF are mandatory. The reader
returns no partial model before checking all of them and full model conformance.
Truncated streams, duplicate records, trailing records/bytes, malformed tags, or
digest mismatches reject. The end digest detects accidental corruption; an attacker
who can rewrite both content and digest has not authenticated anything.

`iter_jsonl` emits one JOB per line after validating the supplied model.
`load_jsonl` consumes an iterable of byte lines, retaining reconstructed JOBs for
full validation. This is record streaming, not constant-memory validation, runtime
execution, append-only event traces, or independently executable partial JOBs.

## XML interchange

Canonical XML is ASCII, without declaration, BOM, or final LF. Root:
`<qsol-morph serialization-version="1.0.0">VALUE</qsol-morph>`.
VALUE is the wire-model tree using these exact forms:

- Object: `<object><member name="KEY">VALUE</member>...</object>`, keys sorted as
  in canonical JSON. Model/profile keys contain no XML metacharacters.
- Array: `<array>VALUE...</array>`, preserving order.
- String: `<string>QUOTED_JSON_STRING</string>`, using the canonical ASCII JSON
  string token above, then XML text-escaping `&`, `<`, `>` as `&amp;`, `&lt;`, `&gt;`.
- Integer: `<integer>N</integer>`, using canonical integer notation.
- Boolean: `<boolean>true</boolean>` or `<boolean>false</boolean>`.

Empty objects/arrays use explicit paired tags. Empty strings contain `""`.
Exceptional string tags are ordinary typed object/array/integer nodes in this
wire tree. JSON-quoted ASCII payloads retain NUL, CR/LF/tab, supplementary scalars,
and all XML-forbidden characters without XML normalization or double interpretation.

No namespaces, DTDs, entity definitions, external entities/resources, XInclude,
comments, processing instructions, extra attributes, mixed text, tails, duplicate
members, scalar children, or unknown nodes. Strict readers reconstruct the wire
model and require byte-for-byte canonical reserialization. XML entity aliases,
CDATA, self-closing variants, formatting whitespace, or alternate number spellings
are noncanonical and reject. The reader never retrieves a source or contract URI.

## API, CLI, and conformance

Python 3.11+, pinned dependencies in `requirements-model.txt`:

```sh
python tools/serialization.py tests/fixtures/model/positive/minimal.json --to json
python tools/serialization.py input.json --from json --to xml
python tools/serialization.py input.xml --from xml --to jsonl
python tools/serialization.py input.jsonl --from jsonl --hash
python -m unittest discover -s tests -v
```

Output is binary stdout; use shell redirection to a new destination. Errors use
stderr and nonzero exit; invalid input produces no successful output. `-` reads
stdin. `--from model` (default) imports ordinary model JSON, distinctly from the
strict profile formats. The CLI does not mutate the input file or retrieve URLs.

`dumps(model, format)` returns bytes; `loads(bytes, format)` returns the validated
model; `fingerprint(model)` returns the content identity; `read_model(bytes)`
imports ordinary model JSON. Repeated serialization is byte-identical. Inputs are
not modified. Normal host resource failures are not proof of model invalidity;
this reference implementation makes no unbounded-memory or unbounded-input claim.
The host Python integer-string digit bound also applies before expanding decimal
exponent tokens; a resource-limit rejection is not a change to logical integer
semantics. The same bound applies to Python integer source positions before
serialization; the API reports `ResourceLimit` (a distinct `Invalid` subclass)
rather than claiming those models violate the schema. Typed numeric strings are
unaffected. The library never changes global interpreter limits.

Golden fixtures cover every existing positive model, multiple JOBs, exceptional
text/codepoints, large integers, control characters, and exact field preservation.
Negative tests cover all model rejection fixtures and malformed/corrupt transports.
No registry, model schema, or historical model/invariant fixture is replaced.
