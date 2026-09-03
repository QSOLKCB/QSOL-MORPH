# Human–AI Language Model

QSOL-MORPH is designed around a specific collaboration goal:

> Humans and AI should reason about the same operational semantics rather than translating between unrelated human-friendly and machine-friendly programs.

The language should therefore minimize syntactic ambiguity while maximizing recognizable semantic structure.

## Semantic anchors

A **semantic anchor** is a reserved concept whose ordinary-language meaning, research meaning, and computational meaning are intentionally aligned.

Candidate anchors include:

```text
AIM
USE
LET
SET
OBSERVE
ASSUME
MODEL
DERIVE
RUN
TEST
PROVE
TRACE
SAVE
LOCK
ALLOW
DENY
WARN
FAIL
RETURN
```

The design preference is one canonical word per concept wherever practical.

For example, the language should avoid simultaneously introducing `import`, `include`, `require`, `attach`, and `using` when a single `USE` operation can carry the intended meaning.

## Research semantics

QSOL should retain explicit epistemic distinctions.

Candidate classes include:

```text
OBSERVATION
ASSUMPTION
PARAMETER
MODEL
SIMULATION
DERIVATION
TEST
VALIDATION
PROOF
RESULT
```

These labels are not interchangeable.

In particular:

```text
OBSERVATION ≠ ASSUMPTION
ASSUMPTION  ≠ DERIVATION
SIMULATION  ≠ OBSERVATION
TEST        ≠ PROOF
RESULT      ≠ THEOREM
```

A transformation may preserve or refine representation while retaining the epistemic class. It must not silently upgrade the class.

## JOB → DECK → CARD

The proposed mnemonic hierarchy is:

```text
JOB
 └── DECK
      └── CARD
```

### JOB

A research task, batch, or orchestration boundary.

A JOB may coordinate multiple decks, compare outputs, or define execution order.

Illustrative form:

```text
JOB ORBIT-STUDY
    RUN DECK BASELINE
    RUN DECK HIGH-ALTITUDE
    COMPARE RESULTS
END
```

### DECK

A reproducible semantic workflow.

Illustrative form:

```text
DECK PROJECTILE-001
    AIM TEST RANGE
    OBSERVE HEIGHT 100 m
    ASSUME VACUUM TRUE
    RUN PROJECTILE
    TEST RANGE
    TRACE ALL
    LOCK RESULT
END
```

### CARD

An atomic semantic instruction.

A conceptual card may contain:

```text
CARD = (
    identifier,
    verb,
    noun,
    operands,
    value,
    type,
    unit,
    qualifiers,
    semantic_class,
    effects,
    dependencies,
    source_location
)
```

Not every field is required for every card.

Examples:

```text
RUN MODEL
OBSERVE TEMPERATURE 294.3 K
SEED RNG 18437
XOR FLAGS MASK
TRACE RESULT
```

## VERB / NOUN grammar

The Apollo-style VERB/NOUN concept is useful because it reduces the number of grammatical roles a reader must infer.

Illustratively:

```text
OBSERVE TEMPERATURE 294.3 K
```

can be interpreted as:

```text
VERB  = OBSERVE
NOUN  = TEMPERATURE
VALUE = 294.3
UNIT  = K
```

The goal is not to force every possible program into exactly two tokens. The goal is to make the first semantic roles predictable.

## Memetic design without semantic gimmicks

QSOL uses memorable vocabulary only when that vocabulary accurately reflects behavior.

Good candidate terms are:

- common;
- semantically dense;
- easy to distinguish;
- already meaningful in research or computing;
- stable across human and AI contexts.

Invented jargon should be introduced only when existing vocabulary is materially ambiguous.

## Canonicality

Where practical, QSOL should provide one preferred representation for one semantic concept.

This reduces lexical entropy and helps:

- code review;
- model generation;
- static analysis;
- documentation;
- deterministic formatting;
- formalization.

Canonical formatting may eventually be mandatory for hashed/frozen representations.

## Mnemonic oppositions

Semantic pairs can make intent easier to recognize:

```text
ALLOW / DENY
PASS  / FAIL
LOCK  / UNLOCK
INPUT / OUTPUT
PURE  / IMPURE
LOCAL / EXTERNAL
```

A pair should only exist when both states are real language concepts. The language should not add synonyms merely for symmetry.

## Memorable diagnostics

Compiler diagnostics may pair stable error identifiers with memorable names.

Illustrative examples:

```text
KNOWLEDGE LEAP
simulation output was used as a proof-class value

HIDDEN DICE
randomness was used without an allowed/recorded source

GHOST INPUT
computation depends on undeclared external state

BROKEN LOCK
frozen state was mutated

LOST TRACE
required provenance cannot reconstruct the declared execution context
```

The memorable name improves human recall. A stable error code remains necessary for tooling.

## AI edit model

AI-assisted editing should prefer semantic transformations over unconstrained character rewriting when the canonical model permits it.

Examples:

```text
ADD CARD AFTER @018:
    SEED RNG 18437
```

```text
REPLACE CARD @020:
    TEST RANGE < 1020 m
```

```text
FUSE @042 @043
```

Such operations can be validated against the same schema and invariants used for human-written programs.

## 80-column profile

A future style profile may recommend that ordinary CARDs fit within 80 columns.

This is not a historical emulation requirement. It is a complexity budget: if one atomic semantic instruction requires excessive width, it may be expressing too many concerns.

Long strings, data literals, generated identifiers, or explicit structured blocks are obvious exceptions.

## Design test

For any proposed syntax, ask:

1. Can a researcher explain it without compiler jargon?
2. Can an AI identify its semantic role without guessing from surrounding punctuation?
3. Can it map deterministically to a canonical representation?
4. Does it preserve epistemic meaning?
5. Is there already a simpler semantic anchor for the same concept?

If the answer to the last question is yes, prefer the existing anchor.
