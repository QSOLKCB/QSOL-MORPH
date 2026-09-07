from pathlib import Path
import re


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected 1 occurrence, found {count}: {old[:140]!r}")
    p.write_text(text.replace(old, new, 1))
    print(f"patched {path}: {old.splitlines()[0]}")


# 1. Agent-facing failure-policy transitions require subject-bound evidence.
replace_once(
    "AGENTS.md",
    """    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
```

Outputs and failure records reference applicable `failure_behavior_binding_ids[]`. The frozen default fail-stop behavior has a stable identity when it materially governs execution; it must not be inferred only from skipped CARDs or DECKs.
""",
    """    requested_failure_behavior_id
    effective_failure_behavior_id
    mapping_or_transition_rule_id?
    transition_evidence_id?
```

Outputs and failure records reference applicable `failure_behavior_binding_ids[]`. The frozen default fail-stop behavior has a stable identity when it materially governs execution; it must not be inferred only from skipped CARDs or DECKs.

For a representation-only failure-policy mapping, `mapping_or_transition_rule_id` resolves to an accepted content-bound `FAILURE_BEHAVIOR_MAPPING` rule proving semantic preservation. Whenever requested and effective failure semantics differ, both `mapping_or_transition_rule_id` and `transition_evidence_id` are mandatory: the rule is an accepted `CONTRACT_TRANSITION`, and the evidence is passing, subject-bound `validation_evidence[]` for this exact `FAILURE_BEHAVIOR_BINDING`, requested/effective pair, owning governed scope, and active context. Validation must precede application in the shared event-order domain. A rule assertion without passing pre-application evidence cannot authorize fail-stop becoming continue, retry, compensation, or another semantic change.
""",
)

# 2. Remove stale bare-scope guidance in AGENTS and backend docs.
replace_once(
    "AGENTS.md",
    """`backend_selection_scope_id` is the stable identity of the selection-scope record. `scope_kind` + `scope_id` identify the computation governed by that record. They are not aliases. Decisions, machinery authorization/use records, generated artifacts, and outputs reference `backend_selection_scope_id`.
""",
    """`backend_selection_scope_id` is the stable identity of the selection-scope record. The full `governed_scope_ref = { representation_kind, representation_identity, owner_scope_path[] }` identifies the canonical computation governed by that record; the terminal path element is the governed scope and every disambiguating ancestor participates in identity. The governed computation and selection-scope record are not aliases. Decisions, machinery authorization/use records, generated artifacts, and outputs reference `backend_selection_scope_id`, while validation resolves its complete `governed_scope_ref`.
""",
)
replace_once(
    "docs/BACKENDS-AND-MORPHING.md",
    """`scope_id` identifies the computation governed by target selection; `backend_selection_scope_id` identifies the selection-scope record that governs it; `backend_selection_decision_id` identifies one concrete decision in the selection/fallback history. Decision IDs are unique and ordered. The scope's `final_selection_decision_id`, when execution proceeds, identifies the decision whose machinery was actually used.
""",
    """The complete `governed_scope_ref = { representation_kind, representation_identity, owner_scope_path[] }` identifies the computation governed by target selection; `backend_selection_scope_id` identifies the selection-scope record that governs it; `backend_selection_decision_id` identifies one concrete decision in the selection/fallback history. Local `scope_kind`/`scope_id` pairs and source CARD summaries are not canonical governed-computation identity. Decision IDs are unique and ordered. The scope's `final_selection_decision_id`, when execution proceeds, identifies the decision whose machinery was actually used.
""",
)

# 3. Result-binding fusion requires an explicit frozen rule.
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """    lower_bindings[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        binding_id
    mapping_rule_id?
```
""",
    """    lower_bindings[]:
        owner_scope_path[]:
            scope_kind
            scope_id
        binding_id
    mapping_rule_id?   # REQUIRED for every many-to-one or many-to-many group
```
""",
)
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """This model supports:

- one-to-one preservation or rename;
- one-to-many split;
- many-to-one frozen legal fusion;
- many-to-many only when an explicit frozen rule permits it.

`source_bindings[]` and `lower_bindings[]` use deterministic canonical ordering by the complete qualified references, with no duplicate member in an array. Path segments retain containment order. Positional inference and sorting by `binding_id` alone are not sufficient. A map is required whenever result identities are preserved or transformed unless a frozen rule permits deterministic reconstruction of the complete mapping, including every owner path and both representation identities. Identity of local name text alone is not that reconstruction rule. Both mandatory lowerings and all manifest projections use this same qualified map.
""",
    """This model supports:

- one-to-one preservation or rename;
- one-to-many split;
- many-to-one frozen legal fusion;
- many-to-many only when an explicit frozen rule permits it.

For every many-to-one or many-to-many mapping group, `mapping_rule_id` is mandatory and resolves to the accepted frozen, content-bound rule that defines the value semantics of the fusion/reassociation and how dependent references are redirected. The rule must apply to this exact qualified source/lower binding set and lowering boundary. Missing, unknown, wrong-boundary, context-mismatched, or unverifiable rule identity rejects the mapping rather than silently choosing which source value a dependent consumes. One-to-one preservation/rename and one-to-many split may omit the field only where the frozen default/reconstruction semantics unambiguously define that non-fusing relation.

`source_bindings[]` and `lower_bindings[]` use deterministic canonical ordering by the complete qualified references, with no duplicate member in an array. Path segments retain containment order. Positional inference and sorting by `binding_id` alone are not sufficient. A map is required whenever result identities are preserved or transformed unless a frozen rule permits deterministic reconstruction of the complete mapping, including every owner path and both representation identities. Identity of local name text alone is not that reconstruction rule. Both mandatory lowerings and all manifest projections use this same qualified map.
""",
)
replace_once(
    "AGENTS.md",
    """Result-binding mapping must be cardinality-aware. One source result may legally split into several lower bindings, and several source bindings may legally fuse only under a frozen rule. Do not use scalar mapping fields or positional arrays that cannot represent those transformations unambiguously.
""",
    """Result-binding mapping must be cardinality-aware. One source result may legally split into several lower bindings, and several source bindings may legally fuse only under a frozen rule. Every many-to-one or many-to-many mapping group therefore requires `mapping_rule_id` resolving to the accepted frozen rule for that exact qualified source/lower binding set; never infer fusion legality from array position, equal local names, or producer success. Do not use scalar mapping fields or positional arrays that cannot represent those transformations unambiguously.
""",
)

# 4. Replace every output-schema scalar result_binding? projection with a qualified reference.
# Restrict this to the known documentation projections and require one output-schema occurrence per file.
output_files = [
    "docs/TRACE-AND-PROVENANCE.md",
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    "README.md",
    "ROADMAP.md",
    "AGENTS.md",
]
for path in output_files:
    p = Path(path)
    text = p.read_text()
    pattern = re.compile(r"(?m)^(?P<i>[ \t]*)output_id\n(?P=i)result_binding\?\n")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise SystemExit(f"{path}: expected exactly one output_id/result_binding? schema pair, found {len(matches)}")
    m = matches[0]
    i = m.group("i")
    replacement = (
        f"{i}output_id\n"
        f"{i}result_binding_ref?:\n"
        f"{i}    representation_kind\n"
        f"{i}    representation_identity\n"
        f"{i}    owner_scope_path[]:\n"
        f"{i}        scope_kind\n"
        f"{i}        scope_id\n"
        f"{i}    binding_id\n"
    )
    p.write_text(text[:m.start()] + replacement + text[m.end():])
    print(f"patched {path}: qualified output result binding")

# Canonical output-binding validation contract.
replace_once(
    "docs/TRACE-AND-PROVENANCE.md",
    """`producer_card_ids[]` records the canonical semantic producers. `producer_card_execution_ids[]` records the concrete runtime CARD execution(s) that actually produced, materially supplied, or published the output. Every concrete producer resolves through `card_executions[]` to its `deck_execution_id` and canonical `card_id`.
""",
    """`result_binding_ref?`, when present, identifies exactly one named result binding by `(representation_kind, representation_identity, owner_scope_path[], binding_id)`. `representation_identity` is the content-bound identity of the named Semantic/Core/Vector-Dataflow representation, normally its IR hash. The complete ordered owner path terminates at the binding-defining scope and includes every ancestor needed to distinguish reused local names. If the output is attributed to producers or bindings in another representation, the applicable `result_binding_map[]` chain must connect those qualified endpoints to this exact referenced binding. After a legal fusion, the output may name the fused lower binding; it must not choose one source `v0` by scalar text, producer-array position, or first match. Omit the field only when the output genuinely has no result-binding identity. Missing representation identity, truncated/ambiguous owner paths, unresolved bindings, or an absent required mapping chain fail provenance validation.

`producer_card_ids[]` records the canonical semantic producers. `producer_card_execution_ids[]` records the concrete runtime CARD execution(s) that actually produced, materially supplied, or published the output. Every concrete producer resolves through `card_executions[]` to its `deck_execution_id` and canonical `card_id`.
""",
)

# Mirror the qualified-output rule into the principal projections.
replace_once(
    "docs/DETERMINISM-AND-REPRODUCIBILITY.md",
    """`producer_card_ids[]` records canonical semantic producers. `producer_card_execution_ids[]` records the concrete CARD execution(s) that actually produced, materially supplied, or published the output. Each concrete producer ID resolves to `card_executions[]`, which identifies its DECK execution and canonical CARD.
""",
    """`result_binding_ref?` is the representation- and owner-qualified result identity defined by the canonical trace contract: representation kind/content identity, complete binding-owner path, and local binding ID. It resolves through the applicable cardinality-aware result-binding maps when the producer and named output binding live in different representations; local binding text or producer-array position is never sufficient, including after fusion.

`producer_card_ids[]` records canonical semantic producers. `producer_card_execution_ids[]` records the concrete CARD execution(s) that actually produced, materially supplied, or published the output. Each concrete producer ID resolves to `card_executions[]`, which identifies its DECK execution and canonical CARD.
""",
)
replace_once(
    "README.md",
    """`producer_card_ids[]` identifies canonical semantic producers. `producer_card_execution_ids[]` identifies the concrete runtime CARD execution(s) that actually produced or materially supplied the output and resolves through `card_executions[]` to the DECK execution and canonical CARD.
""",
    """`result_binding_ref?`, when present, is the qualified binding endpoint: representation kind/content identity, complete owner path, and local binding ID. It must resolve directly or through the applicable cardinality-aware lowering maps, so sibling `v0` bindings or a fused lower `v0` cannot be selected by text or producer position.

`producer_card_ids[]` identifies canonical semantic producers. `producer_card_execution_ids[]` identifies the concrete runtime CARD execution(s) that actually produced or materially supplied the output and resolves through `card_executions[]` to the DECK execution and canonical CARD.
""",
)
replace_once(
    "ROADMAP.md",
    """`producer_card_ids[]` identifies canonical semantic producers. **`producer_card_execution_ids[]` identifies the concrete runtime producer executions and is required by the PR #5 gate.** A canonical CARD ID alone cannot distinguish outputs from separate loop iterations, retries, calls, or repeated DECK executions.
""",
    """`result_binding_ref?`, when present, is required to carry representation kind/content identity, complete owner path, and local binding ID and to resolve through the applicable cardinality-aware result-binding map chain. A bare binding name is not an acceptable PR #5 result identity, including for fused producers or sibling scopes that reuse the same local name.

`producer_card_ids[]` identifies canonical semantic producers. **`producer_card_execution_ids[]` identifies the concrete runtime producer executions and is required by the PR #5 gate.** A canonical CARD ID alone cannot distinguish outputs from separate loop iterations, retries, calls, or repeated DECK executions.
""",
)
replace_once(
    "AGENTS.md",
    """`producer_card_ids[]` identifies canonical semantic producers. `producer_card_execution_ids[]` identifies the concrete runtime producer executions and must resolve through `card_executions[]` to their canonical CARD and DECK execution. The canonical CARD ID alone is insufficient when a CARD may execute more than once.
""",
    """`result_binding_ref?`, when present, identifies the output's exact binding by representation kind/content identity, complete owner path, and local binding ID. Resolve it directly or through the applicable cardinality-aware result-binding maps; never infer a binding from scalar local text, producer-array order, or first-match lookup after a fusion.

`producer_card_ids[]` identifies canonical semantic producers. `producer_card_execution_ids[]` identifies the concrete runtime producer executions and must resolve through `card_executions[]` to their canonical CARD and DECK execution. The canonical CARD ID alone is insufficient when a CARD may execute more than once.
""",
)

# Sanity checks: no known output projection may retain the old scalar pair.
for path in output_files:
    text = Path(path).read_text()
    if re.search(r"(?m)^\s*output_id\n\s*result_binding\?\n", text):
        raise SystemExit(f"{path}: stale scalar output result_binding? remains")

print("all identity/authority review fixes staged")
