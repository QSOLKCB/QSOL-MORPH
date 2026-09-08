# Extensions and Capabilities

QSOL-MORPH should keep the core deliberately small and move optional syntax, adapters, effects, vendor controls, and extension-owned lowering hooks behind explicit extension profiles. **Machinery selection itself remains a MORPH/backend concern and does not require an extension profile merely because the selected target is optional or accelerated.**

## Extension profiles

Candidate profiles include:

```text
QX-VEC      vector operations
QX-MATH     scientific numerics
QX-POSIX    POSIX processes and streams
QX-GPU      optional generic accelerator controls/syntax
QX-CUDA     CUDA-specific controls
QX-AI       model interaction
QX-PROVE    formal-verification adapters
QX-MIDI     MIDI 2.0 integration
QX-NET      network-related syntax/adapters
```

These names are provisional until frozen by a future specification.

`QX-GPU` and `QX-CUDA`, where retained by a future specification, describe optional language/control surfaces. They are not aliases for GPU/CUDA machinery selection and are not prerequisites for ordinary backend selection unless the program actually uses extension-owned syntax or controls.

## Core rule

An extension may add versioned syntax, adapters, effects, lowering hooks, or capability **requirements**. Activating or installing an extension never grants a runtime capability by itself, and an extension must not silently redefine frozen core meaning.

If a feature is vendor-specific syntax, an optional adapter, an extension-owned effect, or an optional language/control surface, the default assumption is that it belongs in an extension rather than QSOL-CORE. A machinery target such as C, LLVM, GPU, or CUDA remains machinery even when no extension profile is active.

## Declaring extensions

Extension availability and runtime authorization are separate concerns.

Illustrative source:

```text
USE QX-VEC
USE QX-MATH
USE QX-GPU
USE QX-NET

DENY NETWORK
```

`USE QX-NET` means that the deck expects the network extension/profile to exist. `DENY NETWORK` means that execution is not authorized to perform the network capability. A validator can therefore distinguish unsupported syntax/profile requirements from prohibited runtime effects.

## Capabilities

A capability is runtime permission to perform a class of protected effect **or to use a class of protected machinery**.

Candidate capability families include:

```text
FILESYSTEM_READ
FILESYSTEM_WRITE
NETWORK
PROCESS
CLOCK
RANDOM
GPU
AI_MODEL
EXTERNAL_TOOL
```

The final naming scheme is not frozen.

## Effects versus machinery versus capabilities

An **effect** describes an externally/statefully observable operation.

A **machinery selection** describes where/how a computation is executed, such as host, SIMD, GPU, CUDA, or another accelerator/backend target.

A **capability** describes what the execution environment allows, either for a protected effect or for protected machinery access.

An **extension profile** describes optional language/adapter/control functionality that must be available only when the program uses that profile's contract.

These are four different boundaries and must not be collapsed.

Example:

```text
FETCH DATASET
```

may require a network effect and therefore the `NETWORK` capability. If it uses syntax supplied by QX-NET, the deck may additionally declare:

```text
USE QX-NET
```

If the deck or execution policy declares:

```text
DENY NETWORK
```

then a network-requiring effect must not begin. Capability authorization is unconditional and must succeed before the protected effect starts, even when QX-NET is installed and available.

Conversely, allowing `NETWORK` does not make QX-NET syntax available if that extension is absent.

## Multiple capability requirements

A single protected effect may require more than one capability.

For example, a QX-AI operation that invokes a remote model may require both:

```text
AI_MODEL
NETWORK
```

Every capability required by that specific effect attempt must be granted before the attempt begins. Trace/provenance therefore records the complete per-attempt required-capability set rather than one optional capability label.

A protected machinery requirement may likewise require one or more capabilities. For example, a computation whose selected target class is GPU may require:

```text
GPU
```

through a distinct `machinery_requirements[]` record. That requirement does not turn GPU selection into an external effect and does not require `USE QX-GPU` unless extension-owned GPU controls are actually used.

## Protected machinery authorization

Machinery selection and machinery authorization are separate operations.

Canonical semantic state may carry a machinery requirement such as:

```text
machinery_requirement_id = gpu_access_1
target_selector_or_class = GPU
required_capabilities = [GPU]
```

For automatic selection such as `ON BEST`, the actual target may need to be resolved before the applicable machinery requirement is known. The execution rule is:

```text
resolve target
    ↓
resolve applicable machinery requirement(s)
    ↓
authorize every required machinery capability
    ↓
begin protected machinery use
```

Target resolution for planning/provenance is not permission to execute on that target. If machinery authorization fails, the protected machinery execution must not begin.

A backend or selection policy may not silently evade a denial by switching to another target unless a frozen pre-execution fallback rule permits that transition and records it. Likewise, no synthetic effect attempt should be created solely to represent machinery permission.

Trace/provenance binds each machinery authorization record to both the stable `backend_selection_scope_id` **and the concrete `backend_selection_decision_id` it governs**, plus the applicable `machinery_requirement_refs[]`, complete required/granted/denied capability sets, and responsible policy identity/version. Each machinery requirement reference is representation-qualified: `representation_kind` identifies the retained representation family, `representation_identity` is the content-bound identity/hash of the exact retained representation snapshot, and the complete ordered `owner_scope_path[]` is interpreted relative to that representation. For Semantic lineage the path begins at the owning JOB and continues through DECK/CARD as applicable; for direct `QSOL_CORE` entry it uses the actual Core-relative owner hierarchy and must not fabricate Semantic ancestry. The local `machinery_requirement_id` is resolved only within that qualified representation-relative owner. Identical owner paths and local IDs in different retained IR snapshots remain distinct because `representation_identity` participates in the reference. The selection scope alone is not enough when several candidate decisions share that scope.

Conceptually:

```text
machinery_authorization_records[]:
    machinery_authorization_record_id
    backend_selection_scope_id
    backend_selection_decision_id
    machinery_requirement_refs[]:
        representation_kind
        representation_identity
        owner_scope_path[]:
            scope_kind
            scope_id
        machinery_requirement_id
    required_capabilities[]
    granted_capabilities[]
    denied_capabilities[]
    capability_policy_id
    capability_policy_version
    authorization_status
    authorization_sequence_index?
```

A machinery requirement reference is invalid if its representation identity is missing, stale, mismatched to the retained trace snapshot, or if its owner path cannot resolve the local requirement unambiguously within that representation. A direct-Core authorization therefore resolves against the retained Core IR identity and Core-relative path; a Semantic authorization resolves against the retained Semantic IR identity and Semantic owner path. Cross-representation guessing, first-match lookup, or invented JOB/DECK/CARD ancestry fails closed.

For example, if `ON BEST` first chooses GPU and that concrete decision is denied, then a frozen fallback rule chooses CPU and that second decision is authorized, the two authorization outcomes remain separate records keyed to their two different `backend_selection_decision_id` values. A later fallback must never overwrite or detach the denial that governed the earlier candidate.

## Fail closed

Capability checking should reject rather than silently escalate.

A program denied network access must not have a backend quietly substitute a network-backed helper because that helper is convenient.

A program denied protected GPU access must not launch GPU work merely because target selection already chose CUDA or another accelerator.

Likewise, an unavailable extension must not be treated as equivalent to a denied capability. The diagnostic should say which boundary failed: extension availability, effect authorization, machinery authorization, or another frozen contract.

## Extension versioning

Extensions should be independently versionable.

A frozen deck should be able to identify the extension contract it expects, for example conceptually:

```text
USE QX-VEC VERSION 1
```

The exact syntax is not yet defined.

## Backend-specific controls

Vendor controls belong behind explicit profiles.

Generic source:

```text
RUN MODEL ON GPU
```

Target-specific source:

```text
USE QX-CUDA
RUN MODEL ON CUDA WITH:
    threads 128
```

A generic backend should not be required to understand CUDA-specific launch syntax.

GPU/CUDA access may require a machinery capability, but selecting GPU/CUDA machinery is not itself an externally observable Semantic-IR effect and does not by itself activate `QX-GPU` or `QX-CUDA`. Device selection belongs in MORPH/execution trace metadata; protected device use is authorized through the machinery-authorization boundary. Extension availability is checked separately only for extension-owned syntax or controls.

## POSIX profile

QX-POSIX is a composable execution profile rather than a compiler backend.

Its operational semantics must be frozen by a normative QX-POSIX contract before a reference implementation or backend adapter is allowed to choose process, stream, file, environment, signal, encoding, buffering, failure, or effect-completion behavior.

A program emitted through C, LLVM, or another backend may still use POSIX process, file, signal, environment, and stream semantics when QX-POSIX is explicitly active and every capability required by the specific protected effect is authorized.

## AI capability boundary

AI model interaction is an external effect, not ordinary arithmetic.

A future QX-AI profile should expose material properties such as:

- model/provider identity;
- sampling or deterministic settings;
- input/output boundaries;
- external network requirements;
- complete capability requirements;
- caching;
- provenance;
- replay limitations.

An AI result must not silently acquire a stronger epistemic class merely because the call succeeded.

## MIDI profile

MIDI 2.0 should be an adapter/extension rather than part of the core language.

A QSOL card can retain stable semantics while QX-MIDI maps relevant events or properties into an external MIDI representation.

## Principle

> Keep the core small. Effects describe external actions. Machinery describes execution placement. Capabilities authorize protected boundaries. Extensions define optional language, adapter, and control functionality. Never let one masquerade as another.
