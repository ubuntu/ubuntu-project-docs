"""Unit tests for check evaluators in checks.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import checks as checks_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_finding(check_id="TST-1", title="Test check", mode="deterministic"):
    return {
        "id": check_id,
        "section": "Test",
        "title": title,
        "mode": mode,
        "status": "not-evaluated",
        "severity": None,
        "confidence": "low",
        "message": "",
        "todo": "",
        "evidence_refs": [],
        "blocker_class": "none",
    }


class _Ctx:
    """Minimal RunContext stub for check evaluator tests."""

    def __init__(self, *, source_package="testpkg", reporter_content="content"):
        self.source_package = source_package
        self.reporter_mir_content = reporter_content
        self.bug = {"subscribers": []}
        self.evidence = {"adapters": {}}


def _dep_analysis_ok(**kwargs):
    base = {
        "status": "ok",
        "runtime_deps": [],
        "deps_not_in_main": [],
        "dep_components": [],
        "runtime_dep_packages": [],
        "binary_packages": [],
        "dev_debug_doc_packages": [],
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# SUM-1: Source package identified
# ---------------------------------------------------------------------------


def test_sum_1_ok():
    ctx = _Ctx(source_package="libfoo")
    finding = checks_module._check_sum_1(ctx, _make_finding("SUM-1"))
    assert finding["status"] == "ok"
    assert finding["confidence"] == "high"
    assert "libfoo" in finding["message"]


def test_sum_1_missing_package():
    ctx = _Ctx(source_package="")
    finding = checks_module._check_sum_1(ctx, _make_finding("SUM-1"))
    assert finding["status"] == "not-ok"
    assert finding["severity"] == "required"


# ---------------------------------------------------------------------------
# SUM-2: Reporter MIR content present
# ---------------------------------------------------------------------------


def test_sum_2_ok():
    ctx = _Ctx(reporter_content="has content")
    finding = checks_module._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding["status"] == "ok"


def test_sum_2_missing():
    ctx = _Ctx(reporter_content="")
    finding = checks_module._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding["status"] == "not-ok"
    assert finding["severity"] == "nack"


# ---------------------------------------------------------------------------
# DEP-1: No unresolved runtime dependencies
# ---------------------------------------------------------------------------


def test_dep_1_all_in_main():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        dep_components=[{"package": "libz", "component": "main"}],
    )
    finding = checks_module._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding["status"] == "ok"
    assert finding["confidence"] == "high"


def test_dep_1_deps_outside_main():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        deps_not_in_main=["libfancyuniverse"],
        dep_components=[{"package": "libfancyuniverse", "component": "universe"}],
    )
    finding = checks_module._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding["status"] == "not-ok"
    assert finding["severity"] == "required"
    assert "libfancyuniverse" in finding["message"]


def test_dep_1_adapter_missing():
    ctx = _Ctx()
    # No dep-analysis adapter at all
    finding = checks_module._check_dep_1(ctx, _make_finding("DEP-1"))
    assert finding["status"] == "unknown"
    assert finding["confidence"] == "low"


# ---------------------------------------------------------------------------
# SEC-3: Does not use webkit
# ---------------------------------------------------------------------------


def test_sec_3_clean():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "libfoo", "depends": "libc6"}],
    )
    finding = checks_module._check_sec_3(ctx, _make_finding("SEC-3"))
    assert finding["status"] == "ok"


def test_sec_3_webkit_found():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "libwebkit2gtk-4.0"}],
    )
    finding = checks_module._check_sec_3(ctx, _make_finding("SEC-3"))
    assert finding["status"] == "not-ok"
    assert finding["severity"] == "required"
    assert finding["confidence"] == "high"


# ---------------------------------------------------------------------------
# SEC-4: Does not use lib*v8
# ---------------------------------------------------------------------------


def test_sec_4_clean():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "libssl3"}],
    )
    finding = checks_module._check_sec_4(ctx, _make_finding("SEC-4"))
    assert finding["status"] == "ok"


def test_sec_4_libv8_found():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "libv8-dev"}],
    )
    finding = checks_module._check_sec_4(ctx, _make_finding("SEC-4"))
    assert finding["status"] == "not-ok"
    assert finding["severity"] == "required"


# ---------------------------------------------------------------------------
# CB-7: No Python2 dependency
# ---------------------------------------------------------------------------


def test_cb_7_clean():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "python3"}],
    )
    finding = checks_module._check_cb_7(ctx, _make_finding("CB-7"))
    assert finding["status"] == "ok"


def test_cb_7_python2_found():
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        runtime_deps=[{"binary": "myapp", "depends": "python2.7"}],
    )
    finding = checks_module._check_cb_7(ctx, _make_finding("CB-7"))
    assert finding["status"] == "not-ok"
    assert finding["severity"] == "required"


# ---------------------------------------------------------------------------
# SUM-4: ubuntu-mir subscribed
# ---------------------------------------------------------------------------


def test_sum_4_subscribed():
    ctx = _Ctx()
    ctx.bug["subscribers"] = ["ubuntu-mir", "ubuntu-main-sponsors"]
    finding = checks_module._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding["status"] == "ok"


def test_sum_4_not_subscribed():
    ctx = _Ctx()
    ctx.bug["subscribers"] = []
    finding = checks_module._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding["status"] == "not-ok"
    assert finding["severity"] == "recommended"


# ---------------------------------------------------------------------------
# Language gate helpers
# ---------------------------------------------------------------------------


def test_language_gate_go_inactive():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
    }
    assert checks_module._language_gate_active("go", ctx) is False


def test_language_gate_go_active_via_flag():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@ --with golang",
        "go_sum_present": False,
    }
    assert checks_module._language_gate_active("go", ctx) is True


def test_language_gate_go_active_via_go_sum():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": True,
    }
    assert checks_module._language_gate_active("go", ctx) is True


def test_language_gate_rust_inactive():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
    }
    assert checks_module._language_gate_active("rust", ctx) is False


def test_language_gate_unknown_defaults_active():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
    }
    # Unknown gate type should conservatively return True
    assert checks_module._language_gate_active("cobol", ctx) is True


def test_language_gate_adapter_missing_defaults_active():
    ctx = _Ctx()
    # No packaging-source adapter — conservative fallback
    assert checks_module._language_gate_active("go", ctx) is True
