# Evidence Module - Data Collection Adapters

This module implements evidence collection adapters that gather data from various sources (APIs, tools, files) to support MIR check evaluation.

## Architecture

Adapters are organized by execution context:

```
evidence/__init__.py           # Orchestrator and adapter registry
evidence/types.py              # TypedDict definitions for adapter outputs
evidence/host_adapters.py      # Host-side adapters (APIs, web queries)
evidence/container_adapters.py # In-container adapters (build tools, analysis)
```

## Adapter Execution Contexts

### Host-Side Adapters
Run on the host machine, no LXD container required:
- **Launchpad API**: Bug metadata, package info, team membership
- **CVE Trackers**: Ubuntu CVE database, cve.org queries
- **Autopkgtest**: Test result database queries

### In-Container Adapters
Run inside the LXD container via `lxd_runner.exec_in()`:
- **Packaging Source**: Fetch and analyze debian/ files
- **Dependency Analysis**: Extract runtime dependencies, check components
- **Component Mismatches**: Identify packages needing promotion
- **Sbuild**: Run lintian, detect static linking

## Adapter Interface

Each adapter is a function that returns a TypedDict:

```python
def _collect_adapter_name(ctx: RunContext) -> AdapterResultType:
    """Collect evidence for a specific aspect"""
    # Gather data from source (API, tool, file)
    data = _fetch_data(ctx)

    # Return structured result
    return {
        "status": "ok",  # or "error", "pending"
        "field1": value1,
        "field2": value2,
    }
```

**Status values**:
- `"ok"`: Collection succeeded, data is valid
- `"error"`: Collection failed, includes error message
- `"pending"`: Adapter not yet implemented

## Adapter Registry

The orchestrator maintains a registry mapping adapter IDs to collector functions:

```python
# evidence/__init__.py
ADAPTER_REGISTRY = {
    # Host-side
    "lp-bug-api": host_adapters.collect_lp_bug_api,
    "lp-package-api": host_adapters.collect_lp_package_api,
    "ubuntu-cve-tracker": host_adapters.collect_ubuntu_cve_tracker,

    # In-container
    "packaging-source": container_adapters.collect_packaging_source,
    "dep-analysis": container_adapters.collect_dep_analysis,
    "component-mismatches": container_adapters.collect_component_mismatches,
}
```

## Collection Orchestration

`collect_from_catalog()` orchestrates adapter execution:

```python
def collect_from_catalog(ctx: RunContext) -> None:
    """Collect evidence for all adapters referenced by catalog checks"""

    # 1. Scan catalog.yaml for required adapters
    required_adapters = _scan_catalog_for_adapters(ctx.catalog)

    # 2. Order adapters by dependencies
    ordered = _order_adapters(required_adapters)

    # 3. Execute each adapter
    for adapter_id in ordered:
        collector = ADAPTER_REGISTRY.get(adapter_id)
        if not collector:
            ctx.evidence["adapters"][adapter_id] = {
                "status": "pending",
                "message": "Adapter not implemented"
            }
            continue

        try:
            result = collector(ctx)
            ctx.evidence["adapters"][adapter_id] = result
        except Exception as e:
            ctx.evidence["adapters"][adapter_id] = {
                "status": "error",
                "message": str(e)
            }
```

## Adapter Dependencies

Some adapters depend on outputs from others:

```python
# evidence/__init__.py
ADAPTER_DEPS = {
    "dep-analysis": ["packaging-source"],      # Needs source dir
    "sbuild": ["packaging-source"],            # Needs source dir
    "component-mismatches": ["dep-analysis"],  # Needs binary list
}
```

The orchestrator uses topological sorting to execute adapters in dependency order.

## Type Safety with TypedDict

Each adapter defines its output structure using TypedDict:

```python
# evidence/types.py
class DepAnalysisResult(TypedDict):
    status: str
    binary_packages: list[str]
    runtime_deps: list[RuntimeDep]
    runtime_dep_packages: list[str]
    dep_components: list[DepComponent]
    deps_not_in_main: list[str]
```

**Benefits**:
- IDE autocomplete and type checking
- Self-documenting contracts
- Catches typos at development time

## Host-Side Adapters

### lp-bug-api
Fetches Launchpad bug metadata:
```python
{
    "status": "ok",
    "bug_id": "1234567",
    "bug_title": "MIR for package-name",
    "bug_description": "...",
    "bug_comments": [...],
    "target_source_package": "package-name",
    "target_series": "noble",
    "bug_tags": ["mir"],
    "bug_subscribers": ["ubuntu-mir", "..."]
}
```

### lp-package-api
Fetches package publishing history:
```python
{
    "status": "ok",
    "ubuntu_publish_history": [...],
    "debian_publish_history": [...],
    "current_version": "1.2.3-1ubuntu1",
    "upload_history": [...],
    "uploaders": ["uploader@ubuntu.com"]
}
```

### ubuntu-cve-tracker
Queries Ubuntu CVE database:
```python
{
    "status": "ok",
    "cves": [...],
    "active_cves": ["CVE-2024-1234"],
    "fixed_cves": ["CVE-2023-5678"]
}
```

## In-Container Adapters

### packaging-source
Fetches and analyzes debian/ files:
```python
{
    "status": "ok",
    "source_dir": "/tmp/auto-mir-1234567/package-1.2.3",
    "debian_control": "Source: package-name\n...",
    "debian_rules": "#!/usr/bin/make -f\n...",
    "cargo_lock_present": false,
    "go_sum_present": false,
    "vendored_dirs": ["vendor/", "third_party/"]
}
```

### dep-analysis
Extracts runtime dependencies:
```python
{
    "status": "ok",
    "binary_packages": ["package-name", "package-name-dev"],
    "runtime_deps": [
        {"binary": "package-name", "depends": "libc6, libssl3"}
    ],
    "runtime_dep_packages": ["libc6", "libssl3"],
    "dep_components": [
        {"package": "libc6", "component": "main"},
        {"package": "libssl3", "component": "main"}
    ],
    "deps_not_in_main": []
}
```

### component-mismatches
Identifies packages needing promotion:
```python
{
    "status": "ok",
    "series": "noble",
    "raw_output": "...",
    "promotion_candidates": ["package-name"]
}
```

## Error Handling

Adapters should handle errors gracefully:

```python
def collect_adapter(ctx: RunContext) -> AdapterResult:
    try:
        # Attempt collection
        data = _fetch_data(ctx)
        return {"status": "ok", **data}
    except NetworkError as e:
        return {
            "status": "error",
            "message": f"Network error: {e}",
            "retryable": True
        }
    except ParseError as e:
        return {
            "status": "error",
            "message": f"Parse error: {e}",
            "retryable": False
        }
```

**Retryable errors**: Network timeouts, transient API failures
**Non-retryable errors**: Parse errors, missing files, invalid data

## Testing

Unit tests in `tests/test_evidence.py` cover:
- Adapter output structure validation
- Error handling paths
- Dependency ordering logic

Integration tests verify:
- End-to-end collection flow
- LXD container execution
- Real API interactions (mocked in CI)

Run tests:
```bash
cd tools/auto-mir
python3 -m pytest tests/test_evidence.py -v
```

## Adding New Adapters

1. **Define TypedDict** in `evidence/types.py`:
   ```python
   class NewAdapterResult(TypedDict):
       status: str
       field1: str
       field2: list[str]
   ```

2. **Implement collector** in appropriate module:
   ```python
   # evidence/host_adapters.py or container_adapters.py
   def collect_new_adapter(ctx: RunContext) -> NewAdapterResult:
       data = _fetch_data(ctx)
       return {
           "status": "ok",
           "field1": data["value1"],
           "field2": data["values2"]
       }
   ```

3. **Register in orchestrator**:
   ```python
   # evidence/__init__.py
   ADAPTER_REGISTRY = {
       "new-adapter": host_adapters.collect_new_adapter,
   }
   ```

4. **Declare dependencies** (if any):
   ```python
   ADAPTER_DEPS = {
       "new-adapter": ["packaging-source"],
   }
   ```

5. **Reference in catalog.yaml**:
   ```yaml
   - id: NEW-1
     adapters_required:
       - new-adapter
   ```

6. **Add tests** in `tests/test_evidence.py`

## Key Files

- `evidence/__init__.py`: Orchestrator, adapter registry, dependency ordering
- `evidence/types.py`: TypedDict definitions for all adapter outputs
- `evidence/host_adapters.py`: Host-side adapters (APIs, web queries)
- `evidence/container_adapters.py`: In-container adapters (build tools)
- `lxd_runner.py`: Container execution utilities
