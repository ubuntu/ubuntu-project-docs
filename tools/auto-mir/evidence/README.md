# Evidence Subsystem

This subsystem collects structured evidence for checks, combining host-side data
sources with in-VM analysis.

## Responsibilities

- discover required/optional adapters from catalog check definitions,
- execute adapters in dependency-safe order,
- collect results under `ctx.evidence["adapters"]`,
- propagate dependency failures explicitly,
- distinguish required failures from optional best-effort failures.

## Key files

- `evidence/__init__.py`: collection orchestration, dependency ordering, and the
  `ADAPTER_REGISTRY` id->collector mapping.
- Adapter payloads are plain dicts; their shapes are documented in
  CATALOG.md ("Evidence adapter data contracts").
- `evidence/host_adapters.py`: host-executed adapters (APIs, web/data feeds).
- `evidence/guest_adapters.py`: in-guest adapters (packaging, build, lint, scans).
- `evidence/team_mapping_adapter.py`: SUM-4 team-mapping integration.
- `evidence/lto_disabled_adapter.py`: PRF-10 LTO-disabled list integration.

## Adapter model

Adapters are plain collector functions mapped by id in `ADAPTER_REGISTRY`:

- required adapters can fail the evidence stage,
- optional adapters are collected best-effort and do not fail the run.

The registry mapping is currently authoritative for
runtime ordering. `catalog.yaml` documents adapter interfaces, and
`catalog-mir-review.yaml`/`catalog-mir-report.yaml` reference them from checks
and items, but this adapter metadata is not used to order execution. Keep both
representations aligned until the planned catalog consolidation removes this
temporary duplication.

`collect_from_catalog(ctx)` returns:

- `0` when all required adapters succeeded,
- `1` when one or more required adapters failed.

## Dependency and failure behavior

- Ordering uses topological sorting.
- If adapter A depends on B and B fails, A is marked failed with an upstream
  dependency message and is not executed.
- Unknown adapter ids become `pending` entries with explicit messages.

## Contracts

- Input context contract is the RunContext (auto_mir.py); see `collect_from_catalog`.
- Output payload schemas are described in `evidence/types.py` and consumed by checks.

## Validation

Run from `tools/auto-mir`:

```bash
make test
```

Focused orchestration coverage is in `tests/test_evidence.py`.
