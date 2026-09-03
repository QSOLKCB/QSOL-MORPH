# Backends and Morphing

QSOL-MORPH separates source meaning from target machinery.

A backend is an implementation target. It does not own the semantics of the QSOL program it receives.

## Pipeline

```text
QSOL source
    ↓
canonical semantic model
    ↓
QSOL-CORE / lower IR
    ↓
vector/dataflow analysis
    ↓
MORPH legality + optimization
    ↓
backend lowering
    ↓
target artifact + trace
```

## MORPH responsibilities

QSOL-MORPH may:

- select a backend when policy permits;
- validate extension requirements;
- check determinism compatibility;
- choose legal lowering strategies;
- vectorize;
- fuse;
- schedule;
- place data;
- specialize for a target;
- emit inspectable code or binaries;
- record material transformation decisions.

It may not silently redefine scientific meaning.

## Reference C backend

The first executable backend should be deliberately conservative. Portable C provides a useful baseline because it is broadly supported, easy to inspect, easy to diff, and suitable as an independent reference against more aggressive backends.

The C path exists first for semantic clarity, not maximum performance.

## LLVM

LLVM can provide mature target support and optimization while QSOL-MORPH retains responsibility for QSOL-specific legality. A transformation being legal to LLVM is not automatically legal under a QSOL numeric, provenance, or epistemic contract.

## POSIX

A POSIX profile should expose process and stream behavior explicitly:

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

Typed QSOL records may cross into byte or text streams at explicit process boundaries.

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

## CUDA

CUDA should be an explicit backend/profile beneath the generic GPU model.

Desired simple form:

```text
RUN GRAVITY ON CUDA
```

QSOL-MORPH may generate normal CUDA plumbing such as allocation, transfers, launch configuration, synchronization, and cleanup. Generated CUDA should remain inspectable.

An expert escape hatch may expose explicit target controls through an extension profile.

Illustrative form:

```text
RUN GRAVITY ON CUDA WITH:
    blocks 256
    threads 128
    shared 48 KiB
```

## Automatic target selection

A source may eventually request:

```text
RUN MODEL ON HOST
RUN MODEL ON BEST
```

`BEST` requires a declared policy. The selected backend, device, policy version, and relevant tuning state should be recorded when material to reproducibility.

## Future backends

Candidate targets include:

```text
HIP
OpenCL
Vulkan Compute
WebAssembly
native QSOL VM
MIDI 2.0 adapters
Lean 4 adapters
future accelerators
```

A target earns support because it is useful, not because it exists.

## Backend equivalence

Backends need not produce identical machine code or performance. They must satisfy the semantic and determinism contract requested by the source and active specification.

For floating-point programs, equivalence may be exact or tolerance-bounded depending on the declared numeric profile.

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

> QSOL programs describe meaning. QSOL-MORPH chooses machinery, and must be able to explain the choice.
