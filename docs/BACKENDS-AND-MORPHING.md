# Backends and Morphing

QSOL-MORPH separates source meaning from target machinery.

A backend is an implementation target. It does not own the semantics of the QSOL program it receives.

## Pipeline

```text
QSOL source
    ↓
canonical semantic model
    ↓
semantic-to-QSOL-CORE lowering
    ↓
QSOL-CORE
    ↓
Vector/Dataflow IR
    ↓
MORPH legality + optimization
    ↓
backend lowering
    ↓
target artifact + trace
```

The Semantic IR → QSOL-CORE boundary is specified and implemented independently before backend work. The roadmap then places Vector/Dataflow IR before the first MORPH code-generation backend so this remains the single documented lowering architecture.

A backend must not accept rich Semantic IR and invent its own private interpretation of CARDs that bypasses the frozen semantic-to-core lowering contract.

## MORPH responsibilities

QSOL-MORPH may:

- select a backend when policy permits;
- validate extension requirements at the machinery boundary;
- check determinism compatibility;
- choose legal target-lowering strategies from the already-defined lower IR;
- vectorize;
- fuse;
- schedule within effect/failure-order constraints;
- place data;
- specialize for a target;
- emit inspectable code or binaries;
- record material transformation and selection decisions.

It may not silently redefine scientific meaning or absorb the Semantic IR → QSOL-CORE language-lowering stage into backend-specific code generation.

## Reference C backend

The first code-generation backend should be deliberately conservative. Portable C provides a useful baseline because it is broadly supported, easy to inspect, easy to diff, and suitable as an independent reference against more aggressive backends.

The C path exists first for semantic clarity, not maximum performance.

Its end-to-end input originates as canonical Semantic IR, but the C backend itself consumes the established lower pipeline after the reference Semantic-to-Core and Vector/Dataflow stages.

## LLVM

LLVM can provide mature target support and optimization while QSOL-MORPH retains responsibility for QSOL-specific legality. A transformation being legal to LLVM is not automatically legal under a QSOL numeric, provenance, failure-order, authorization, or epistemic contract.

## POSIX

POSIX is a composable execution profile, not a compiler backend peer.

`QX-POSIX` may expose process and stream behavior explicitly:

```text
stdin
stdout
stderr
exit status
process execution
files
environment
signals
```

Typed QSOL records may cross into byte or text streams at explicit process boundaries. A C-, LLVM-, Fortran-, or other generated target may use the POSIX profile when enabled and authorized.

## Fortran

Fortran is a natural interoperability and code-generation target for scientific numerics. QSOL-MORPH should reuse established numerical ecosystems rather than attempting to replace them.

## Generic GPU model

The generic accelerator layer should sit above vendor-specific APIs.

Candidate concepts include:

```text
RUN ... ON GPU
AUTO/HOST/DEVICE residency
work decomposition
shared/local memory
synchronization
kernel boundaries
numeric contracts
determinism contracts
```

## CUDA backend

**CUDA is a backend/machinery selection.**

Selecting CUDA answers where/how the generic GPU computation is lowered. It does not by itself require vendor-specific source controls.

Desired simple form:

```text
RUN GRAVITY ON CUDA
```

QSOL-MORPH may generate normal CUDA plumbing such as allocation, transfers, launch configuration, synchronization, cleanup, and stable failure mapping. Generated CUDA should remain inspectable.

## QX-CUDA control profile

**`QX-CUDA` is an optional vendor-specific extension profile**, separate from selecting the CUDA backend.

The profile exists for explicit CUDA-only controls such as launch geometry, shared-memory configuration, or other vendor-specific tuning that generic QSOL source should not need.

Illustrative form:

```text
USE QX-CUDA
RUN GRAVITY ON CUDA WITH:
    blocks 256
    threads 128
    shared 48 KiB
```

A deck may select the CUDA backend without using QX-CUDA-specific syntax. Conversely, source that uses QX-CUDA controls declares that vendor-specific extension dependency explicitly.

This distinction keeps:

```text
CUDA      = machinery/backend
QX-CUDA   = optional source/control extension
```

from collapsing into one ambiguous concept.

## Automatic target selection

A source may eventually request:

```text
RUN MODEL ON HOST
RUN MODEL ON BEST
```

`BEST` requires a declared selection policy.

Backend choice may differ across CARDs, regions, kernels, or generated units. Provenance therefore separates the **governed selection scope** from the ordered **selection decisions** made for that scope.

A conceptual `backend_selection_scopes[]` entry may bind:

```text
backend_selection_scope_id
governed_scope_ref:
    representation_kind
    representation_identity
    owner_scope_path[]:
        scope_kind
        scope_id
source_card_ids[]
backend_unit_id?
selection_decision_ids[]
final_selection_decision_id?
```

`backend_selection_scope_id` is the stable identity of the selection-scope record itself. `governed_scope_ref` identifies the exact computation by representation identity plus its complete representation-relative owner path; the terminal path element is the governed scope. Local IDs and source CARD summaries cannot substitute. Decisions, machinery-authorization records, generated artifacts, and outputs reference the stable `backend_selection_scope_id`.

Each material selection attempt is an identified decision:

```text
backend_selection_decisions[]:
    backend_selection_decision_id
    backend_selection_scope_id
    decision_sequence_index
    requested_target
    selected_backend
    selected_backend_version?
    target_architecture?
    device?
    selection_policy_id?
    selection_policy_version?
    selection_tuning_id?
    selection_tuning_hash?
    predecessor_selection_decision_id?
    fallback_rule_id?
    fallback_evidence_id?
    machinery_authorization_record_ids[]?
    decision_status
```

The complete `governed_scope_ref = { representation_kind, representation_identity, owner_scope_path[] }` identifies the computation governed by target selection; `backend_selection_scope_id` identifies the selection-scope record that governs it; `backend_selection_decision_id` identifies one concrete decision in the selection/fallback history. Local `scope_kind`/`scope_id` pairs and source CARD summaries are not canonical governed-computation identity. Decision IDs are unique and ordered. The scope's `final_selection_decision_id`, when execution proceeds, identifies the decision whose machinery was actually used.

Policy/tuning fields are material when selection is automatic, such as `ON BEST`. An explicit target still needs enough scope and decision identity to establish which source computation and generated unit used that machinery.

A denied protected target followed by an authorized fallback must remain represented as **two decisions**, not as one record whose `selected_backend` is overwritten. The fallback decision references its predecessor, an accepted content-bound `BACKEND_FALLBACK` rule through `fallback_rule_id`, and passing subject-bound `fallback_evidence_id` establishing applicability to this exact predecessor/target/policy context before selection. The denied decision retains its machinery-authorization record and status; the later decision retains its own authorization record where required. Unknown, stale, mismatched, self-issued, or late fallback evidence fails closed.

A single execution-wide selection scope is valid only when one frozen machinery-selection process genuinely governs the whole run. Mixed-target JOBs keep distinct scope entries.

This allows replay/audit to explain **what was considered**, **what was denied or selected**, **why fallback was legal**, and **which final target actually ran**.

For a frozen replay, policy may require the previously final selected target rather than re-running an evolved selection/tuning process.

## Future backends

Candidate backend targets include:

```text
HIP
OpenCL
Vulkan Compute
WebAssembly
native QSOL VM
future accelerators
```

Adapter or integration mappings are **not** compiler backends merely because they exchange data or invoke an external system. MIDI 2.0 mapping belongs to the versioned `QX-MIDI` extension/adapter workstream, while formal-tool integration such as Lean belongs behind the appropriate proof/verification extension boundary such as `QX-PROVE`.

A target earns backend support because it is useful as machinery, not because an adapter exists for it.

## Backend equivalence

Backends need not produce identical machine code or performance. They must satisfy the semantic, failure, authorization, numeric, randomness, and determinism contracts required by the source and active specification.

For floating-point programs, equivalence may be exact or tolerance-bounded depending on the declared numeric contract.

## Inspectability

The toolchain should eventually support operations such as:

```text
qsol morph model.qsl --to=c
qsol morph model.qsl --to=cuda
qsol morph model.qsl --show-ir
qsol morph model.qsl --show-vector-ir
qsol morph model.qsl --explain
```

The exact CLI is not frozen.

## Principle

> QSOL programs describe meaning. Semantic lowering defines lower meaning. QSOL-MORPH chooses machinery and must be able to explain the choice.
