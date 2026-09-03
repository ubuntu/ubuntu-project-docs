"""Unit tests for check evaluators in checks.py."""

import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import checks.deterministic
import checks.language_gates
import checks.llm_eval
import llm
from models import Finding

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REAL_REVIEW_CATALOG: dict | None = None


def _real_review_catalog() -> dict:
    """Load the composed review catalog once and hand out the same object.

    Tests exercise the real catalog data instead of a hand-copied message
    table, so wording drift between catalog.yaml and these tests is
    impossible by construction.
    """
    global _REAL_REVIEW_CATALOG
    if _REAL_REVIEW_CATALOG is None:
        import catalog as catalog_module

        _REAL_REVIEW_CATALOG = catalog_module.load_catalog_for_role(
            Path(__file__).resolve().parent.parent,
            Path(__file__).resolve().parent.parent.parent.parent,
            "review",
        )
    return _REAL_REVIEW_CATALOG


def _make_finding(check_id="TST-1", title="Test check", mode="deterministic"):
    return Finding(
        id=check_id,
        section="Test",
        title=title,
        mode=mode,
    )


class _Ctx:
    """Minimal RunContext stub for check evaluator tests."""

    def __init__(
        self, *, source_package="testpkg", reporter_content="content", review_type="fresh"
    ):
        self.bug_id = "123456"
        self.series = "devel"
        self.source_package = source_package
        self.reporter_mir_content = reporter_content
        self.requested_binaries = []
        self.review_type = review_type
        self.bug = {"subscribers": []}
        self.findings = []
        self.tool_root = Path(__file__).resolve().parent.parent
        self.catalog = _real_review_catalog()
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
        "dep_source_map": [],
        "in_scope_deps_not_in_main": [],
        "out_of_scope_deps_not_in_main": [],
        "same_source_deps": [],
        "auto_included_binaries": [],
        "auto_included_dep_components": [],
        "auto_included_deps_not_in_main_or_unknown": [],
        "auto_included_offending_deps_by_binary": [],
        "auto_included_deps_same_source": [],
        "auto_included_same_source_deps_by_binary": [],
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# SUM-4: team subscriber in package-team-mapping
# ---------------------------------------------------------------------------


def test_sum_1_ok():
    ctx = _Ctx(source_package="libfoo")
    finding = checks.deterministic._check_sum_1(ctx, _make_finding("SUM-1"))
    assert finding.status == "ok"
    assert finding.confidence == "high"
    assert "libfoo" in finding.message


def test_sum_1_missing_package():
    ctx = _Ctx(source_package="")
    finding = checks.deterministic._check_sum_1(ctx, _make_finding("SUM-1"))
    assert finding.status == "not-ok"
    assert finding.severity == "required"


# ---------------------------------------------------------------------------
# SUM-2: Reporter MIR content present
# ---------------------------------------------------------------------------


def test_sum_2_ok():
    ctx = _Ctx(reporter_content="has content")
    finding = checks.deterministic._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding.status == "ok"


def test_sum_2_missing():
    ctx = _Ctx(reporter_content="")
    finding = checks.deterministic._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding.status == "not-ok"
    assert finding.severity == "nack"


def test_sum_2_rereview_ok_without_reporter_content():
    ctx = _Ctx(reporter_content="", review_type="rereview")
    finding = checks.deterministic._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding.status == "ok"


def test_sum_2_reorg_ok_without_reporter_content():
    ctx = _Ctx(reporter_content="", review_type="reorg")
    finding = checks.deterministic._check_sum_2(ctx, _make_finding("SUM-2"))
    assert finding.status == "ok"


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# DEP-3: No -dev/-debug/-doc packages needing exclusion
# ---------------------------------------------------------------------------


def test_dep_3_no_auto_included_binaries():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg1"],
        auto_included_binaries=[],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "ok"
    assert finding.confidence == "high"
    assert "no -dev/-debug/-doc packages" in finding.message


def test_dep_3_auto_included_binaries_safe():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg-dev"],
        auto_included_binaries=["libmypkg-dev"],
        auto_included_deps_not_in_main_or_unknown=[],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "ok"
    assert finding.confidence == "high"
    assert "will be auto-included" in finding.message


def test_dep_3_auto_included_binaries_with_offending_deps():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg-dev"],
        auto_included_binaries=["libmypkg-dev"],
        auto_included_deps_not_in_main_or_unknown=["libuniverse1", "libunknown1"],
        auto_included_offending_deps_by_binary=[
            {"binary": "libmypkg-dev", "dependencies": ["libunknown1", "libuniverse1"]}
        ],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "not-ok"
    assert finding.severity == "recommended"
    assert finding.confidence == "high"
    assert "libuniverse1" in finding.message
    assert "libunknown1" in finding.todo
    assert "libmypkg-dev" in finding.todo


def test_dep_3_auto_included_dep_from_same_source_is_ok():
    # libebur128-dev auto-includes libebur128-1, which is built by the same
    # source and being promoted by this very MIR request. It must not be flagged
    # as an offending dependency; instead DEP-3 succeeds with an explanatory note.
    ctx = _Ctx(source_package="libebur128")
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["libebur128-1", "libebur128-dev"],
        auto_included_binaries=["libebur128-dev"],
        auto_included_deps_not_in_main_or_unknown=[],
        auto_included_offending_deps_by_binary=[{"binary": "libebur128-dev", "dependencies": []}],
        auto_included_deps_same_source=["libebur128-1"],
        auto_included_same_source_deps_by_binary=[
            {"binary": "libebur128-dev", "dependencies": ["libebur128-1"]}
        ],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "ok"
    assert finding.confidence == "high"
    assert "part of this very request" in finding.message
    assert "libebur128-1" in finding.message
    assert not finding.todo


def test_dep_3_ignores_global_non_main_for_non_auto_included_binaries():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {"status": "ok"}
    ctx.evidence["adapters"]["dep-analysis"] = _dep_analysis_ok(
        binary_packages=["mypkg", "libmypkg-dev"],
        deps_not_in_main=["libuniverse-from-mainpkg"],
        auto_included_binaries=["libmypkg-dev"],
        auto_included_deps_not_in_main_or_unknown=[],
    )

    finding = checks.deterministic._check_dep_3(ctx, _make_finding("DEP-3"))

    assert finding.status == "ok"
    assert "have no dependencies outside main" in finding.message


# ---------------------------------------------------------------------------
# SEC-3: Does not use webkit
# ---------------------------------------------------------------------------
# SUM-4: team subscriber in package-team-mapping
# ---------------------------------------------------------------------------


def test_sum_4_subscribed():
    ctx = _Ctx(source_package="bash")
    ctx.evidence["adapters"]["team-mapping"] = {
        "status": "ok",
        "team_mapping": {
            "ubuntu-foundations": ["bash", "coreutils"],
            "ubuntu-server": ["nginx", "apache2"],
        },
        "subscribed_teams": ["ubuntu-foundations"],
        "source_package": "bash",
    }
    finding = checks.deterministic._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding.status == "ok"
    assert "ubuntu-foundations" in finding.message


def test_sum_4_not_subscribed():
    ctx = _Ctx(source_package="some-package")
    ctx.evidence["adapters"]["team-mapping"] = {
        "status": "ok",
        "team_mapping": {},
        "subscribed_teams": [],
        "source_package": "some-package",
    }
    finding = checks.deterministic._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding.status == "not-ok"
    assert finding.severity == "recommended"


def test_sum_4_adapter_failed():
    ctx = _Ctx(source_package="bash")
    ctx.evidence["adapters"]["team-mapping"] = {
        "status": "error",
        "error": "Launchpad API error",
    }
    finding = checks.deterministic._check_sum_4(ctx, _make_finding("SUM-4"))
    assert finding.status == "unknown"
    assert finding.confidence == "low"


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
    assert checks.language_gates._language_gate_active("go", ctx) is False


def test_language_gate_go_active_via_flag():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@ --with golang",
        "go_sum_present": False,
    }
    assert checks.language_gates._language_gate_active("go", ctx) is True


def test_language_gate_go_active_via_go_sum():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": True,
    }
    assert checks.language_gates._language_gate_active("go", ctx) is True


def test_language_gate_go_active_via_source_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "file_listing": [{"path": "./cmd/tool/main.go", "size": 321}],
    }
    assert checks.language_gates._language_gate_active("go", ctx) is True


def test_language_gate_go_ignores_vendor_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "file_listing": [{"path": "./vendor/example/lib.go", "size": 321}],
    }
    assert checks.language_gates._language_gate_active("go", ctx) is False


def test_language_gate_rust_inactive():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
    }
    assert checks.language_gates._language_gate_active("rust", ctx) is False


def test_language_gate_rust_active_via_source_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
        "file_listing": [{"path": "./src/main.rs", "size": 456}],
    }
    assert checks.language_gates._language_gate_active("rust", ctx) is True


def test_language_gate_rust_ignores_vendor_tree_files():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "cargo_lock_present": False,
        "file_listing": [{"path": "./third_party/rust/lib.rs", "size": 456}],
    }
    assert checks.language_gates._language_gate_active("rust", ctx) is False


def test_language_gate_unknown_defaults_active():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
    }
    # Unknown gate type should conservatively return True
    assert checks.language_gates._language_gate_active("cobol", ctx) is True


def test_language_gate_python_uses_is_python_package_detector():
    """The 'python' gate dispatches to _is_python_package, not a looser duplicate."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@ --with python3\noverride_dh_auto_build:\n\tdh_python3",
        "debian_control": "Package: myapp\n",
        "file_listing": [],
    }
    assert checks.language_gates._language_gate_active("python", ctx) is True


def test_language_gate_python_inactive_without_python_signals():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "debian_control": "Package: myapp\n",
        "file_listing": [],
    }
    assert checks.language_gates._language_gate_active("python", ctx) is False


def test_language_gate_adapter_missing_defaults_active():
    ctx = _Ctx()
    # No packaging-source adapter — conservative fallback
    assert checks.language_gates._language_gate_active("go", ctx) is True


def test_language_gate_combined_go_rust_active_with_go():
    """Test combined gate 'go|rust' returns True when go package detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh-golang",
        "go_sum_present": False,
        "cargo_lock_present": False,
    }
    assert checks.language_gates._language_gate_active("go|rust", ctx) is True


def test_language_gate_combined_go_rust_active_with_rust():
    """Test combined gate 'go|rust' returns True when rust package detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "cargo_lock_present": True,
    }
    assert checks.language_gates._language_gate_active("go|rust", ctx) is True


def test_language_gate_combined_go_rust_inactive():
    """Test combined gate 'go|rust' returns False when neither go nor rust present."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh $@",
        "go_sum_present": False,
        "cargo_lock_present": False,
    }
    assert checks.language_gates._language_gate_active("go|rust", ctx) is False


def test_is_python_package_ignores_stray_py_file():
    """A stray .py helper/test script must not classify a C/C++ package as Python."""
    packaging = {
        "status": "ok",
        "debian_control": "Source: libgav1\n\nPackage: libgav1-2\nBuild-Depends: cmake",
        "debian_rules": "%:\n\tdh $@",
        "file_listing": [{"path": "tests/helper.py", "size": 80}],
    }
    assert checks.language_gates._is_python_package(packaging) is False


def test_is_python_package_detects_real_signals():
    """Genuine Python packaging signals are still detected."""
    dh_python = {
        "debian_control": "Package: python3-x\nBuild-Depends: dh-python, python3-all",
        "debian_rules": "%:\n\tdh $@ --with python3 --buildsystem=pybuild",
        "file_listing": [],
    }
    assert checks.language_gates._is_python_package(dh_python) is True

    metadata = {
        "debian_control": "Package: python3-y",
        "debian_rules": "dh $@",
        "file_listing": [{"path": "pyproject.toml", "size": 40}],
    }
    assert checks.language_gates._is_python_package(metadata) is True


def test_extract_build_hints_no_vendor_references():
    """Test _extract_build_hints returns empty results when no vendor paths present."""
    build_log = """
    gcc -Wall -O2 -c main.c
    gcc -o myapp main.o
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert hints["static_flags"] == []
    assert hints["vendor_compile_invocations"] == []
    assert hints["vendor_archive_ops"] == []


def test_extract_build_hints_static_linking():
    """Test _extract_build_hints detects static linking flags."""
    build_log = """
    gcc -static -Wall -c main.c
    gcc -Wl,--whole-archive -o myapp main.o
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert any("-static" in line for line in hints["static_flags"])
    assert any("--whole-archive" in line for line in hints["static_flags"])


def test_extract_build_hints_vendor_compile():
    """Test _extract_build_hints detects vendor paths in compiler invocations."""
    build_log = """
    gcc -I./vendor/zlib -c main.c
    clang -L./third_party/libs -lmylib main.o
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert any("vendor" in line and "gcc" in line for line in hints["vendor_compile_invocations"])
    assert any(
        "third_party" in line and "clang" in line for line in hints["vendor_compile_invocations"]
    )


def test_extract_build_hints_vendor_archive():
    """Test _extract_build_hints detects archive operations on vendor libraries."""
    build_log = """
    ar rcs ./vendor/libmylib.a obj1.o obj2.o
    ranlib ./third_party/libs/libfoo.a
    """
    hints = checks.llm_eval._extract_build_hints(build_log)
    assert any("ar" in line and "vendor" in line for line in hints["vendor_archive_ops"])
    assert any("ranlib" in line and "third_party" in line for line in hints["vendor_archive_ops"])


def test_parse_built_using_entries_empty():
    """Test _parse_built_using_entries with empty input."""
    import evidence.guest_adapters as adapters

    assert adapters._parse_built_using_entries("") == []
    assert adapters._parse_built_using_entries(None) == []


def test_parse_built_using_entries_single_line():
    """Test _parse_built_using_entries with single-line field."""
    import evidence.guest_adapters as adapters

    field = "golang-1.20 (>= 1.20~), golang-1.20 (<< 1.21~)"
    result = adapters._parse_built_using_entries(field)
    assert "golang-1.20 (>= 1.20~)" in result
    assert "golang-1.20 (<< 1.21~)" in result


def test_parse_built_using_entries_multi_line():
    """Test _parse_built_using_entries with multi-line field (continuation lines)."""
    import evidence.guest_adapters as adapters

    field = """golang-1.20 (>= 1.20~),
 golang-1.20 (<< 1.21~)"""
    result = adapters._parse_built_using_entries(field)
    assert "golang-1.20 (>= 1.20~)" in result
    assert "golang-1.20 (<< 1.21~)" in result


def test_esl_3_no_built_using():
    """Test ESL-3 with no Built-Using entries."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {
        "status": "ok",
        "message": "OK",
        "deb_packages": [
            {"package": "mypkg", "version": "1.0", "built_using": [], "static_built_using": []},
        ],
    }
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "ok"
    assert "Built-Using" not in result.message.lower() or "not" in result.message.lower()


def test_esl_3_toolchain_built_using():
    """Test ESL-3 with toolchain-only Built-Using entries."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {
        "status": "ok",
        "message": "OK",
        "deb_packages": [
            {
                "package": "mypkg",
                "version": "1.0",
                "built_using": ["golang-1.20 (>= 1.20~)"],
                "static_built_using": [],
            },
        ],
    }
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "ok"
    assert "toolchain" in result.message.lower()


def test_select_ev_to_ai_model_tier_small_for_short_prompt_and_payload():
    tier = checks.llm_eval._select_ev_to_ai_model_tier(
        "short prompt",
        {"adapter": "small"},
    )
    assert tier == "small"


def test_select_ev_to_ai_model_tier_large_for_long_prompt():
    prompt = "x" * (checks.llm_eval._PROMPT_LARGE_THRESHOLD_CHARS + 1)
    tier = checks.llm_eval._select_ev_to_ai_model_tier(
        prompt,
        {"adapter": "small"},
    )
    assert tier == "large"


def test_render_ev_to_ai_prompt_raises_when_tool_root_missing():
    """A missing/invalid tool_root means the checkout itself is damaged; this
    must raise loudly rather than silently substitute alternate wording."""
    ctx = _Ctx()
    ctx.tool_root = None
    check = {
        "id": "URF-2",
        "title": "Memory safety",
        "section": "Upstream red flags",
        "todo_refs": ["TODO: - check"],
    }

    with pytest.raises(TypeError):
        checks.llm_eval._render_ev_to_ai_prompt(check, {"adapter": "x"}, "policy text", ctx)


def test_render_ev_to_ai_prompt_carries_reviewer_wording_guardrail():
    """The rendered prompt must instruct the model to avoid internal field names."""
    ctx = _Ctx()
    check = {
        "id": "ESL-11",
        "title": "Vendored code refresh documented",
        "section": "Embedded sources and static linking",
        "todo_refs": ["TODO-B: - Does not include vendored code"],
    }

    prompt = checks.llm_eval._render_ev_to_ai_prompt(check, {"adapter": "x"}, "policy text", ctx)

    # Guardrail wording present from the on-disk prompts/ev_to_ai.md template.
    assert "reviewer-facing language" in prompt
    assert "vendored_dirs" in prompt  # named as an example of what NOT to quote


def test_eval_ai_graceful_on_large_tier_llm_error():
    ctx = _Ctx()
    check = {
        "id": "SUM-5",
        "title": "Summary verdict",
        "section": "Summary",
        "todo_refs": [],
        "messages": {"llm_unavailable_message": "LLM unavailable: {error}"},
    }
    finding = _make_finding("SUM-5", mode="ai")

    with mock.patch("llm.call_llm", side_effect=llm.LLMError("large model unavailable")):
        result = checks.llm_eval._eval_ai(check, ctx, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"


def test_eval_ev_to_ai_graceful_on_small_tier_llm_error():
    ctx = _Ctx()
    check = {
        "id": "SEC-1",
        "title": "Security synthesis",
        "section": "Security",
        "todo_refs": ["TODO: - Manual security review"],
        "adapters_required": [],
        "adapters_optional": [],
        "messages": {"llm_unavailable_message": "LLM unavailable: {error}"},
    }
    finding = _make_finding("SEC-1", mode="ev_to_ai")

    with mock.patch("checks.llm_eval._select_ev_to_ai_model_tier", return_value="small"):
        with mock.patch("llm.call_llm", side_effect=llm.LLMError("small model transient issue")):
            result = checks.llm_eval._eval_ev_to_ai(check, ctx, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"


def test_eval_ev_to_ai_graceful_on_large_tier_llm_error():
    ctx = _Ctx()
    check = {
        "id": "SEC-1",
        "title": "Security synthesis",
        "section": "Security",
        "todo_refs": ["TODO: - Manual security review"],
        "adapters_required": [],
        "adapters_optional": [],
        "messages": {"llm_unavailable_message": "LLM unavailable: {error}"},
    }
    finding = _make_finding("SEC-1", mode="ev_to_ai")

    with mock.patch("checks.llm_eval._select_ev_to_ai_model_tier", return_value="large"):
        with mock.patch("llm.call_llm", side_effect=llm.LLMError("large model unavailable")):
            result = checks.llm_eval._eval_ev_to_ai(check, ctx, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"


def test_eval_ev_to_ai_performs_followup_when_model_requests_more_evidence():
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "\n".join([f"line {i}" for i in range(1, 501)]),
    }
    check = {
        "id": "SEC-6",
        "title": "Endpoint exposure",
        "section": "Security",
        "todo_refs": ["TODO: - Manual review"],
        "adapters_required": ["fetch-build"],
        "adapters_optional": [],
    }
    finding = _make_finding("SEC-6", mode="ev_to_ai")

    first_response = {
        "status": "unknown",
        "severity": "required",
        "confidence": "low",
        "message": "Need more context",
        "todo": "TODO: - request details",
        "rationale": "Insufficient context",
        "human_confirmation_required": True,
        "evidence_refs": [],
        "risk_flags": [],
        "additional_evidence_requests": [{"type": "line_range", "start": 300, "end": 320}],
    }
    second_response = {
        "status": "ok",
        "severity": "ok",
        "confidence": "medium",
        "message": "No endpoint exposure detected",
        "todo": "",
        "rationale": "Reviewed requested lines",
        "human_confirmation_required": True,
        "evidence_refs": ["fetch-build:build_log"],
        "risk_flags": [],
    }

    with mock.patch("checks.llm_eval._select_ev_to_ai_model_tier", return_value="small"):
        with mock.patch("llm.call_llm", side_effect=[first_response, second_response]) as mocked:
            result = checks.llm_eval._eval_ev_to_ai(check, ctx, finding)

    assert mocked.call_count == 2
    second_prompt = mocked.call_args_list[1].args[0]
    assert "additional_evidence_requested" in second_prompt
    assert '"line": 300' in second_prompt
    assert result.status == "ok"


def test_cb_1_ok_when_lp_builds_pass():
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-build-api"] = {
        "status": "ok",
        "builds": [
            {"arch_tag": "amd64", "build_state": "Successfully built"},
            {"arch_tag": "arm64", "build_state": "Successfully built"},
        ],
    }

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "Launchpad build records pass" in result.message


def test_cb_1_not_ok_when_lp_build_state_fails():
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-build-api"] = {
        "status": "ok",
        "builds": [
            {"arch_tag": "amd64", "build_state": "Successfully built"},
            {"arch_tag": "arm64", "build_state": "Failed to build"},
        ],
    }

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "arm64" in result.message


def test_cb_1_unknown_when_no_lp_builds_found():
    """When Launchpad has no build records at all, the state stays unknown."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-build-api"] = {"status": "ok", "builds": []}

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "unknown"
    assert "No Launchpad build records" in result.message


def test_cb_1_unknown_when_lp_build_api_unavailable():
    """When lp-build-api itself failed to collect, the state stays unknown."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-build-api"] = {"status": "error"}

    finding = _make_finding("CB-1", mode="deterministic")
    result = checks.deterministic._check_cb_1(ctx, finding)

    assert result.status == "unknown"
    assert "Could not confirm Launchpad build state" in result.message


def test_esl_3_unexpected_built_using():
    """Test ESL-3 with unexpected Built-Using entries."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {
        "status": "ok",
        "message": "OK",
        "deb_packages": [
            {
                "package": "mypkg",
                "version": "1.0",
                "built_using": ["libfoo (>= 1.0)"],
                "static_built_using": [],
            },
        ],
    }
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "not-ok"
    assert result.severity == "required"


def test_esl_3_missing_adapter():
    """Test ESL-3 when deb-metadata adapter is missing."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["deb-metadata"] = {"status": "error"}
    finding = _make_finding("ESL-3", mode="deterministic")
    result = checks.deterministic._check_esl_3(ctx, finding)
    assert result.status == "unknown"


def test_urf_1_clean_build_log():
    """Test URF-1 with clean build log."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "dh_auto_configure\ndh_auto_build\ndh_auto_test\ndh_auto_install",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "Errors/warnings" in result.message


def test_urf_1_build_warnings():
    """Genuine build warnings are routed to reviewer judgement (Left to decide)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:5: warning: unused variable 'x'",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "unknown"
    assert result.severity == "recommended"
    assert "warning" in result.message.lower()


def test_urf_1_ignores_dpkg_noise():
    """dpkg-source/dpkg-buildflags noise must not be reported as build warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": (
            "dpkg-source: warning: cannot verify inline signature for ./foo.dsc: "
            "no acceptable signature found\n"
            "dpkg-buildflags: warning: debian/changelog not found. Not setting "
            "ELF package metadata parameter.\n"
            "gcc -O2 -c foo.c\n"
        ),
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "Errors/warnings" in result.message


def test_urf_1_build_errors():
    """Test URF-1 with build errors detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:3: error: undefined reference to 'foo'",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "error" in result.message.lower()


def test_urf_1_security_warning():
    """Test URF-1 with security warning detected (reviewer judgement)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "gcc -Wall test.c\ntest.c:10: warning: format string vulnerability",
        "build_success": True,
    }

    finding = _make_finding("URF-1", mode="deterministic")
    result = checks.deterministic._check_urf_1(ctx, finding)

    assert result.status == "unknown"
    assert result.severity == "recommended"
    assert "warning" in result.message.lower()


def test_prf_10_not_on_list():
    """Test PRF-10 when package is not on lto-disabled list."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["lto-disabled-list"] = {
        "status": "ok",
        "on_list": False,
        "disabled_arches": [],
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "lto-disabled list" in result.message.lower()


def test_prf_10_on_list():
    """Test PRF-10 when package is on lto-disabled list (any architecture)."""
    ctx = _Ctx(source_package="llvm")
    ctx.evidence["adapters"]["lto-disabled-list"] = {
        "status": "ok",
        "on_list": True,
        "disabled_arches": ["arm64", "s390x"],
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "lto-disabled list" in result.message.lower()
    # Affected architectures are surfaced to the reviewer.
    assert "arm64" in result.message
    assert "s390x" in result.message


def test_prf_10_adapter_error_degrades_to_unknown():
    """Test PRF-10 degrades to unknown (left for reviewer) when fetch fails."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["lto-disabled-list"] = {
        "status": "error",
        "error": "network unreachable",
    }

    finding = _make_finding("PRF-10", mode="deterministic")
    result = checks.deterministic._check_prf_10(ctx, finding)

    assert result.status == "unknown"
    assert result.severity == "recommended"
    assert result.confidence == "low"
    assert result.todo.startswith("TODO:")
    assert "lto-disabled" in result.message.lower()


def test_prf_11_ok_when_no_delta():
    """PRF-11 is ok when Ubuntu carries no delta, regardless of Maintainer."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "delta_kind": "sync",
        "source_maintainer": "Debian Person <p@debian.org>",
        "analyzed_version": "1.0-1",
    }

    finding = _make_finding("PRF-11", mode="deterministic")
    result = checks.deterministic._check_prf_11(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "correct Maintainer field" in result.message


def test_prf_11_ok_when_delta_and_updated_maintainer():
    """PRF-11 is ok when the delta is present and Maintainer was updated."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "delta_kind": "ubuntu_delta",
        "source_maintainer": "Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>",
        "analyzed_version": "1.0-1ubuntu1",
    }

    finding = _make_finding("PRF-11", mode="deterministic")
    result = checks.deterministic._check_prf_11(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_prf_11_not_ok_when_delta_and_stale_maintainer():
    """PRF-11 flags a delta present without a Maintainer update."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "delta_kind": "ubuntu_delta",
        "source_maintainer": "Eric Berry <eric.berry@canonical.com>",
        "analyzed_version": "1.0-1ubuntu2",
    }

    finding = _make_finding("PRF-11", mode="deterministic")
    result = checks.deterministic._check_prf_11(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "1.0-1ubuntu2" in result.message
    assert "Eric Berry" in result.message
    assert result.todo.startswith("TODO:")


def test_prf_11_unknown_when_delta_kind_unavailable():
    """PRF-11 degrades to unknown when delta_kind cannot be classified."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "delta_kind": "unknown",
        "source_maintainer": "",
        "analyzed_version": "",
    }

    finding = _make_finding("PRF-11", mode="deterministic")
    result = checks.deterministic._check_prf_11(ctx, finding)

    assert result.status == "unknown"
    assert result.severity == "recommended"


def test_prf_11_adapter_error_degrades_to_unknown():
    """PRF-11 degrades to unknown (left for reviewer) when packaging-source fails."""
    ctx = _Ctx(source_package="testpkg")
    ctx.evidence["adapters"]["packaging-source"] = {"status": "error"}

    finding = _make_finding("PRF-11", mode="deterministic")
    result = checks.deterministic._check_prf_11(ctx, finding)

    assert result.status == "unknown"
    assert result.todo.startswith("TODO:")


def test_cb_8_not_python():
    """Test CB-8 when package is not Python."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("CB-8", mode="deterministic")
    result = checks.deterministic._check_cb_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not a Python package" in result.message


def test_cb_8_python_with_dh_python():
    """Test CB-8 when Python package uses dh_python."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_python3 build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("CB-8", mode="deterministic")
    result = checks.deterministic._check_cb_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "using dh_python" in result.message


def test_cb_8_python_without_dh_python():
    """Test CB-8 when Python package does not use dh_python."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("CB-8", mode="deterministic")
    result = checks.deterministic._check_cb_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "dh_python" in result.message.lower()


def test_cb_8_python_with_dh_sequence_python3_in_control():
    """Modern packaging declares dh-sequence-python3 in debian/control instead
    of an explicit dh_python3 override in debian/rules; the sequence add-on
    auto-invokes dh_python3, so debian/rules never contains that substring.
    Regression for bug 2161382 (prompt-toolkit)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "%:\n\tdh $@ --buildsystem=pybuild\n",
        "debian_control": (
            "Source: prompt-toolkit\n"
            "Build-Depends: debhelper-compat (= 13), dh-sequence-python3, pybuild-plugin-pyproject\n"
            "\n"
            "Package: python3-prompt-toolkit\n"
        ),
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("CB-8", mode="deterministic")
    result = checks.deterministic._check_cb_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "using dh_python" in result.message


def test_esl_2_no_static_linking():
    """Test ESL-2 with clean build log (no static linking)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "dh_auto_configure\ndh_auto_build\ndh_auto_test",
        "static_link_hints": [],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "static linking" in result.message


def test_esl_2_static_linking_detected():
    """Test ESL-2 when static linking is detected."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "gcc -static -o myapp main.c",
        "static_link_hints": ["myapp"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "static linking" in result.message.lower()


def test_esl_2_static_linking_justified():
    """Test ESL-2 when static linking is justified."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "gcc -static -o scanner security_scanner.c  # integrity checker",
        "static_link_hints": ["scanner"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "justified" in result.message.lower()


def test_esl_2_ignores_configure_static_probe():
    """A configure feature probe for -static must not be treated as static linking."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": (
            "checking if gcc static flag -static works... yes\n"
            "checking if g++ static flag -static works... yes\n"
            "libtool --mode=link gcc -Wl,-Bsymbolic-functions -o liblua.so lua.o\n"
        ),
        "static_link_hints": [],
        "static_binaries": [],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.message == "no static linking"


def test_esl_2_static_binary_in_built_deb_flagged():
    """A fully static ELF binary shipped in a built deb is flagged."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "dh_auto_build\n",
        "static_link_hints": [],
        "static_binaries": ["mytool/usr/bin/mytool"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "mytool" in result.message


def test_esl_2_ignores_static_libgcc_helper_flag():
    """A build log with only helper flags / no static binaries reports no static linking."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "build_log": "gcc -static-libgcc -static-libstdc++ -o app app.c\n",
        "static_link_hints": [],
        "static_binaries": [],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("ESL-2", mode="deterministic")
    result = checks.deterministic._check_esl_2(ctx, finding)

    assert result.status == "ok"
    assert result.message == "no static linking"


def test_prf_2_not_library():
    """Test PRF-2 when package is not a library."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp\nDescription: Command line tool",
        "debian_rules": "dh_auto_configure",
        "file_listing": [],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not applicable" in result.message.lower()


def test_prf_2_python_library():
    """A pure-Python library (no shared object) needs no symbols tracking."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: python3-mylib\nDescription: Python library",
        "debian_rules": "dh_auto_configure\ndh_python3 build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not applicable" in result.message.lower()


def test_prf_2_python_package_shipping_shared_lib_still_tracked():
    """A package that ships BOTH Python code and a .so is still responsible for
    symbols tracking of that shared library (language does not exempt it)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": (
            "Source: mymix\n\n"
            "Package: python3-mymix\nDepends: ${python3:Depends}\n\n"
            "Package: libmymix1\nDepends: ${shlibs:Depends}\n"
        ),
        "debian_rules": "dh_python3 build",
        "file_listing": [{"path": "setup.py", "size": 100}],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "libmymix1" in result.rationale


def test_prf_2_cpp_library_with_helper_py_and_symbols():
    """Feedback #8: a C++ library that ships a helper .py and a .symbols file is
    credited with tracking in place (not mis-gated as Python/not-applicable)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Source: libgav1\n\nPackage: libgav1-2\nDepends: ${shlibs:Depends}",
        "debian_rules": "%:\n\tdh $@",
        "file_listing": [
            {"path": "debian/libgav1-2.symbols", "size": 500},
            {"path": "tests/helper.py", "size": 80},
        ],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "symbols tracking is in place" in result.message
    assert "libgav1-2.symbols" in result.rationale


def test_prf_2_cpp_library_with_symbols():
    """Test PRF-2 when C++ library has symbols file."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: libmyapp1\nLibrary package with .so and .symbols",
        "debian_rules": "dh_makeshlibs",
        "file_listing": [{"path": "debian/libmyapp1.symbols", "size": 500}],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "symbols tracking is in place" in result.message


def test_prf_2_shared_library_with_symbols_file():
    """A C shared library that ships debian/<pkg>.symbols reports tracking in place."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": (
            "Source: lua5.5\n\n"
            "Package: liblua5.5-0\nArchitecture: any\n\n"
            "Package: liblua5.5-dev\nArchitecture: any\n"
        ),
        "debian_rules": "dh_makeshlibs",
        "file_listing": [
            {"path": "./debian/liblua5.5-0.symbols", "size": 500},
            {"path": "./debian/control", "size": 500},
        ],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.message == "symbols tracking is in place"


def test_prf_2_shared_library_without_symbols_file():
    """A shared library with no symbols file is flagged as a recommendation."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Source: foo\n\nPackage: libfoo1\nArchitecture: any\n",
        "debian_rules": "dh_auto_configure",
        "file_listing": [{"path": "./debian/control", "size": 500}],
    }
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "built_debs": ["/tmp/out/libfoo1_1.0-1_amd64.deb"],
    }

    finding = _make_finding("PRF-2", mode="deterministic")
    result = checks.deterministic._check_prf_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "symbols" in result.message.lower()


def test_prf_3_watch_present():
    """Test PRF-3 when debian/watch is present."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "file_listing": [
            {"path": "debian/watch", "size": 200},
            {"path": "debian/control", "size": 500},
        ],
    }

    finding = _make_finding("PRF-3", mode="deterministic")
    result = checks.deterministic._check_prf_3(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "debian/watch" in result.message


def test_prf_3_native_package():
    """Test PRF-3 when package is native (watch not needed)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "debian/source/format: 3.0 (native)",
        "file_listing": [{"path": "debian/control", "size": 500}],
    }

    finding = _make_finding("PRF-3", mode="deterministic")
    result = checks.deterministic._check_prf_3(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not needed" in result.message.lower()


def test_prf_3_non_native_no_watch():
    """Test PRF-3 when non-native package lacks debian/watch."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: upstream-tool\nVersion: 1.2.3-1",
        "file_listing": [
            {"path": "debian/control", "size": 500},
            {"path": "debian/changelog", "size": 300},
        ],
    }

    finding = _make_finding("PRF-3", mode="deterministic")
    result = checks.deterministic._check_prf_3(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "debian/watch" in result.message


def test_sec_2_non_root():
    """Test SEC-2 when daemon does not run as root."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "[Unit]\nUser=myuser\nDynamicUser=yes",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "root" in result.message.lower()


def test_sec_2_root_with_mitigations():
    """Test SEC-2 when daemon runs as root but has mitigations."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=root\nSeccomp=strict\nAppArmor=profile",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert "mitigations" in result.message.lower()


def test_sec_2_root_no_mitigations():
    """Test SEC-2 when daemon runs as root with no mitigations."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=root",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_sec_2_root_in_comment_no_trigger():
    """Test SEC-2 when 'User=root' appears only in a comment line."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "# Do not set User=root\nUser=daemon",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("SEC-2", mode="deterministic")
    result = checks.deterministic._check_sec_2(ctx, finding)

    # comment line must not trigger the root check; User=daemon satisfies non-root
    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_3_no_escalation():
    """Test URF-3 when no privilege escalation found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-3", mode="deterministic")
    result = checks.deterministic._check_urf_3(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_3_escalation_outside_tests():
    """Test URF-3 when privilege escalation found outside tests."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "sudo apt-get install foo",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-3", mode="deterministic")
    result = checks.deterministic._check_urf_3(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_3_test_marker_elsewhere_does_not_bypass():
    """Test URF-3 when escalation exists outside test-context lines."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "# tests run in autopkgtest\nsudo apt-get install foo",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-3", mode="deterministic")
    result = checks.deterministic._check_urf_3(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_4_no_nobody():
    """Test URF-4 when no 'nobody' user found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=myapp",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_4_nobody_found():
    """Test URF-4 when 'nobody' user found outside tests."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "User=nobody",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_4_test_marker_elsewhere_does_not_bypass():
    """Test URF-4 when nobody exists outside test-context lines."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "# tests use fake users\nUser=nobody",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_5_no_setuid():
    """Test URF-5 when no setuid/setgid found in rules or lintian."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_5_setuid_with_systemd():
    """Test URF-5 when setuid present but using systemd (mitigated)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "chmod 4755 myapp\n# Using systemd service permissions",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"


def test_urf_5_setuid_no_justification():
    """Test URF-5 when setuid present in rules without justification."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "chmod 4755 myapp",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_urf_5_lintian_setuid_tag():
    """Test URF-5 when lintian reports a setuid-binary tag on the built artifact."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": ["W: myapp: setuid-binary usr/bin/myapp 4755 root/root"],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "lintian" in result.message.lower()


def test_urf_4_nobody_found_in_source_tree():
    """URF-4 detects 'nobody' in the broader source tree, not just debian/."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": ['src/daemon.c:42:    setuser("nobody");'],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "nobody" in result.message.lower()


def test_urf_4_nobody_in_tests_is_ignored():
    """A 'nobody' hit under a test path does not trip URF-4."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": ['tests/test_user.c:5:    run_as("nobody");'],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "ok"


def test_urf_4_nobody_in_doc_text_file_is_ignored():
    """A 'nobody' mention inside a non-executable doc/text file is not a risk."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": [
            "./tools/execsnoop_example.txt:37:chown 9664 0 /bin/chown nobody:nobody ./main",
        ],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "ok"


def test_urf_4_nobody_pronoun_in_comment_is_ignored():
    """The English pronoun 'nobody' in a C/C++ comment is not a user reference."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": [
            "./vio/viosocket.cc:162:  /* Ensure nobody uses vio_read_buff simultaneously. */",
            "./storage/innobase/lock/lock0lock.cc:6170:  trx->mutex. In theory nobody else should use it.",
            "./sql/sql_show.cc:4085:    but nobody cares - it may be called only in case of failed plugin",
        ],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "ok"


def test_urf_4_nobody_quoted_string_is_flagged():
    """A quoted 'nobody' string literal in source code is a genuine reference."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": [
            './storage/innobase/sync/sync0arr.cc:367:          (owner == std::thread::id{} ? "nobody" : to_string(owner).c_str())',
        ],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert "nobody" in result.message.lower()


def test_urf_4_nobody_chown_style_is_flagged():
    """A chown-style 'nobody:group' reference in a script is a genuine reference."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": [
            "./scripts/setup.sh:5:chown nobody:nogroup /var/lib/myapp",
        ],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert "nobody" in result.message.lower()


def test_urf_4_nobody_pronoun_in_readme_debian_is_ignored():
    """A 'nobody' mention in *.README.Debian is filtered (doc + pronoun)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": [
            "./debian/mysql-server.README.Debian:71:(-rw------- username groupname .my.cnf) to ensure that nobody else can read",
        ],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "ok"


def test_urf_4_nobody_assignment_is_flagged():
    """A 'User=nobody' assignment in a config is a genuine reference."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": [
            "./configs/daemon.conf:3:User=nobody",
        ],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert "nobody" in result.message.lower()


def test_urf_4_nobody_cli_flag_is_flagged():
    """A '--user nobody' CLI flag in a script is a genuine reference."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "nobody_source_hits": [
            "./scripts/run.sh:10:exec /usr/bin/myapp --user nobody",
        ],
        "nobody_source_files": [],
    }

    finding = _make_finding("URF-4", mode="deterministic")
    result = checks.deterministic._check_urf_4(ctx, finding)

    assert result.status == "not-ok"
    assert "nobody" in result.message.lower()
    """URF-5 flags a setuid/setgid binary found in the built artifacts."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "setuid_setgid_source_hits": [],
        "setuid_setgid_source_files": [],
    }
    ctx.evidence["adapters"]["fetch-build"] = {
        "status": "ok",
        "setuid_setgid_binaries": ["myapp/usr/bin/myhelper"],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert result.confidence == "high"
    assert "myhelper" in result.message


def test_urf_5_setuid_in_doc_text_file_is_ignored():
    """A setuid/setgid keyword inside a doc/text file (sample output) is ignored."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "setuid_setgid_source_hits": [
            "./tools/execsnoop_example.txt:40:run 9660 -2 /usr/local/bin/setuidgid nobody",
        ],
        "setuid_setgid_source_files": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "ok"


def test_urf_5_setuid_in_script_still_flags():
    """Softening is by file type only: a real script hit still trips URF-5."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "setuid_setgid_source_hits": [
            "./scripts/install.sh:5:chmod u+s /usr/bin/myhelper  # setuid",
        ],
        "setuid_setgid_source_files": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
        "lintian_pedantic": [],
    }

    finding = _make_finding("URF-5", mode="deterministic")
    result = checks.deterministic._check_urf_5(ctx, finding)

    assert result.status == "not-ok"


def test_path_is_nonexecutable_doc_classification():
    doc = checks.deterministic._path_is_nonexecutable_doc
    # Plain-text / documentation files.
    assert doc("./tools/execsnoop_example.txt")
    assert doc("docs/guide.md")
    assert doc("README")
    assert doc("COPYING")
    assert doc("man/foo.1")
    assert doc("man/foo.3pm")
    # Debian conventional documentation basenames: *.README.Debian, README.source.
    assert doc("debian/mysql-server.README.Debian")
    assert doc("debian/README.Debian")
    assert doc("debian/README.source")
    assert doc("debian/libfoo.NEWS.Debian")
    # Code and scripts are never softened, even with "example" in the name.
    assert not doc("./tools/execsnoop_example.py")
    assert not doc("scripts/install.sh")
    assert not doc("src/daemon.c")
    assert not doc("license_check.py")
    assert not doc("readme_check.py")


def test_grep_hit_path_extracts_path():
    hit = checks.deterministic._grep_hit_path
    assert hit("./tools/execsnoop_example.txt:37:chown nobody:nobody") == (
        "./tools/execsnoop_example.txt"
    )
    assert hit("src/daemon.c:42:setuser") == "src/daemon.c"


def test_urf_7_no_old_webkit():
    """Test URF-7 when no old webkit dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libglib2.0", "libgtk-3-0"],
    }

    finding = _make_finding("URF-7", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_urf_7_webkit_found():
    """Test URF-7 when webkit dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libwebkit2gtk-4.0", "libgtk-3-0"],
    }

    finding = _make_finding("URF-7", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "webkit" in result.message.lower()


def test_sec_8_no_accounts():
    """Test SEC-8 when no centralized accounts found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libglib2.0", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-8", mode="deterministic")
    result = checks.deterministic._check_sec_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_sec_8_accounts_found():
    """Test SEC-8 when centralized accounts dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "gnome-online-accounts", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-8", mode="deterministic")
    result = checks.deterministic._check_sec_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "account" in result.message.lower()


def test_sec_10_no_pam():
    """Test SEC-10 when no PAM dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libglib2.0", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-10", mode="deterministic")
    result = checks.deterministic._check_sec_10(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_sec_10_pam_found():
    """Test SEC-10 when direct PAM runtime library found (libpam0g)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libpam0g", "libgtk-3-0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-10", mode="deterministic")
    result = checks.deterministic._check_sec_10(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "pam" in result.message.lower()


def test_sec_10_pam_dev_triggers():
    """Test SEC-10 when libpam-dev found (direct PAM development dep)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libpam-dev"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-10", mode="deterministic")
    result = checks.deterministic._check_sec_10(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert result.confidence == "high"


def test_sec_10_pam_runtime_meta_no_trigger():
    """Test SEC-10 when only system PAM meta-packages present (no direct auth usage)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libpam-runtime", "libpam-modules"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("SEC-10", mode="deterministic")
    result = checks.deterministic._check_sec_10(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_canonical_ok_statement_used_for_single_statement_ev_to_ai():
    """A single-statement ev_to_ai OK finding uses the template wording + rationale."""
    check = {
        "id": "SEC-1",
        "section": "Security",
        "mode": "ev_to_ai",
        "todo_refs": ["TODO: - history of CVEs does not look concerning"],
    }
    finding = _make_finding("SEC-1", mode="ev_to_ai")
    response = {
        "status": "ok",
        "message": "no CVEs anywhere",
        "rationale": "Both trackers report zero CVEs for the package.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.message.startswith("history of CVEs does not look concerning")
    assert "Both trackers report zero CVEs" in result.rationale
    assert result.todo == ""


def test_canonical_ok_statement_skipped_for_placeholder_todo():
    """A placeholder (TBD) template statement falls back to the model message."""
    check = {
        "id": "SUM-3",
        "section": "Summary",
        "mode": "ev_to_ai",
        "todo_refs": ["TODO: List of binary packages to be promoted: TBD"],
    }
    finding = _make_finding("SUM-3", mode="ev_to_ai")
    response = {
        "status": "ok",
        "message": "libgav1-2 is the sole promotion candidate",
        "rationale": "The reporter lists only libgav1-2.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    # Summary section is excluded from canonical substitution.
    assert result.message.startswith("libgav1-2 is the sole promotion candidate")


def test_selected_option_ok_sets_template_statement():
    """An ev_to_ai option with outcome ok renders its canonical statement, no TODO."""
    check = {
        "id": "PRF-1",
        "section": "Packaging red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "PRF-1-B",
                "todo_ref": "TODO-B",
                "render": "- Ubuntu does carry a delta, but it is reasonable and maintenance under control",
                "outcome": "ok",
            },
        ],
    }
    finding = _make_finding("PRF-1", mode="ev_to_ai")
    response = {
        "status": "ok",
        "selected_option": "PRF-1-B",
        "rationale": "The delta only adds autopkgtests (debian/tests).",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.message.startswith(
        "Ubuntu does carry a delta, but it is reasonable and maintenance under control"
    )
    assert "only adds autopkgtests" in result.rationale
    assert result.todo == ""


def test_selected_option_matches_by_todo_ref():
    """The model may name an option by its todo_ref instead of its id."""
    check = {
        "id": "ESL-11",
        "section": "Embedded sources and static linking",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "ESL-11-B",
                "todo_ref": "TODO-B",
                "render": "- Does not include vendored code",
                "outcome": "ok",
            },
        ],
    }
    finding = _make_finding("ESL-11", mode="ev_to_ai")
    response = {"status": "ok", "selected_option": "TODO-B", "rationale": "Only test-only dirs."}
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.message.startswith("Does not include vendored code")


def test_urf_8_option_not_ui_renders_template_statement():
    """URF-8 (ev_to_ai): selecting the not-UI option yields the template line."""
    check = {
        "id": "URF-8",
        "section": "Upstream red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "URF-8-A",
                "todo_ref": "TODO-A",
                "render": "- not part of the UI for extra checks",
                "outcome": "ok",
            },
            {
                "id": "URF-8-C",
                "todo_ref": "TODO-B",
                "render": "- part of the UI but no valid .desktop file is shipped",
                "outcome": "required",
            },
        ],
    }
    finding = _make_finding("URF-8", mode="ev_to_ai")
    response = {
        "status": "ok",
        "selected_option": "URF-8-A",
        "rationale": "libgav1 is a codec library with a CLI helper, not a desktop program.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.message.startswith("not part of the UI for extra checks")
    assert result.todo == ""


def test_urf_8_option_missing_desktop_is_required():
    """URF-8: a desktop program without a .desktop file is a required TODO."""
    check = {
        "id": "URF-8",
        "section": "Upstream red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "URF-8-B",
                "todo_ref": "TODO-B",
                "render": "- part of the UI, desktop file is ok",
                "outcome": "ok",
            },
            {
                "id": "URF-8-C",
                "todo_ref": "TODO-B",
                "render": "- part of the UI but no valid .desktop file is shipped",
                "outcome": "required",
            },
        ],
    }
    finding = _make_finding("URF-8", mode="ev_to_ai")
    response = {
        "status": "not-ok",
        "selected_option": "URF-8-C",
        "rationale": "GTK app but ships no .desktop file.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "GTK app" in result.rationale
    assert result.todo.startswith("TODO:")
    assert "no valid .desktop" in result.todo


def test_urf_9_option_not_user_visible_needs_no_translation():
    """URF-9 (ev_to_ai): not-user-visible option resolves ok without a TODO."""
    check = {
        "id": "URF-9",
        "section": "Upstream red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "URF-9-A",
                "todo_ref": "TODO-A",
                "render": "- no translation present, but none needed for this case (not user visible)",
                "outcome": "ok",
            },
            {
                "id": "URF-9-C",
                "todo_ref": "TODO-B",
                "render": "- user-visible but no translations are present",
                "outcome": "recommended",
            },
        ],
    }
    finding = _make_finding("URF-9", mode="ev_to_ai")
    response = {
        "status": "ok",
        "selected_option": "URF-9-A",
        "rationale": "A shared library exposes no user-facing strings.",
    }
    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not user visible" in result.message.lower()
    assert result.todo == ""


def test_selected_option_uses_todo_ref_when_render_is_empty():
    """Option mapping keeps TODO-ref prefixes intact when render text is missing."""
    check = {
        "id": "URF-8",
        "section": "Upstream red flags",
        "mode": "ev_to_ai",
        "options": [
            {
                "id": "URF-8-C",
                "todo_ref": "TODO-C: - no valid .desktop file",
                "render": "",
                "outcome": "required",
            }
        ],
    }
    finding = _make_finding("URF-8", mode="ev_to_ai")
    response = {
        "status": "not-ok",
        "selected_option": "URF-8-C",
        "rationale": "No desktop file found.",
    }

    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "not-ok"
    assert result.todo.startswith("TODO-C:")


def _cb5_ctx_with_cb4(cb4_status):
    """Build a ctx whose findings already contain a CB-4 result."""
    ctx = _Ctx()
    ctx.catalog["checks"].append(
        {
            "id": "CB-5",
            "section": "Common blockers",
            "title": "Special hardware compromise accepted",
            "mode": "deterministic",
            "messages": {
                "ok_message": "no special hardware needed, so there is no compromise to accept",
                "human_only_message": "Human review required",
                "human_only_todo": "TODO: - {title} - reviewer judgment needed",
            },
        }
    )
    ctx.findings = [
        Finding(
            id="CB-4",
            section="Common blockers",
            title="Special hardware: requirement and coverage plan",
            mode="ev_to_ai",
            status=cb4_status,
            severity="ok" if cb4_status == "ok" else "recommended",
            confidence="medium",
            message="",
        )
    ]
    return ctx


def test_cb_5_ok_when_cb4_needs_no_special_hw():
    """CB-5 resolves ok (no TODO) when CB-4 concluded no special hardware is needed."""
    ctx = _cb5_ctx_with_cb4("ok")
    finding = _make_finding("CB-5", mode="deterministic")
    result = checks.deterministic._check_cb_5(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.todo == ""


def test_cb_5_needs_judgment_when_cb4_not_ok():
    """CB-5 asks for reviewer judgment only when CB-4 did not clear special HW."""
    ctx = _cb5_ctx_with_cb4("not-ok")
    finding = _make_finding("CB-5", mode="deterministic")
    result = checks.deterministic._check_cb_5(ctx, finding)

    assert result.status == "unknown"
    assert result.todo.startswith("TODO:")
    assert "reviewer judgment needed" in result.todo


def _urf9_ctx_with_urf8(*, selected_option, status="ok", has_translation_files=False):
    """Build a ctx whose findings already contain a URF-8 result."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "has_translation_files": has_translation_files,
    }
    ctx.findings = [
        Finding(
            id="URF-8",
            section="Upstream red flags",
            title="UI/desktop file check",
            mode="ev_to_ai",
            status=status,
            severity="ok" if status == "ok" else "required",
            confidence="medium",
            message="",
            selected_option=selected_option,
        )
    ]
    return ctx


def test_urf_9_not_needed_when_urf_8_says_not_ui():
    """URF-9 resolves ok without a TODO when URF-8 judged the package not UI."""
    ctx = _urf9_ctx_with_urf8(selected_option="URF-8-A")
    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.todo == ""
    assert "not user-visible" in result.message.lower()


def test_urf_9_ok_when_ui_and_translations_present():
    """URF-9 resolves ok when URF-8 judged the package UI and translations ship."""
    ctx = _urf9_ctx_with_urf8(selected_option="URF-8-B", has_translation_files=True)
    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert result.todo == ""


def test_urf_9_recommended_when_ui_and_no_translations():
    """URF-9 flags a recommended TODO when URF-8 judged the package UI but no translations ship."""
    ctx = _urf9_ctx_with_urf8(selected_option="URF-8-C", has_translation_files=False)
    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"
    assert result.todo.startswith("TODO:")


def test_urf_9_unknown_when_urf_8_unresolved():
    """URF-9 reports unknown rather than guessing when URF-8 itself is unresolved."""
    ctx = _urf9_ctx_with_urf8(selected_option="", status="unknown")
    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "unknown"
    assert "URF-8" in result.message


def test_urf_9_unknown_when_urf_8_finding_missing():
    """URF-9 reports unknown when URF-8's finding is absent from ctx.findings entirely."""
    ctx = _Ctx()
    ctx.findings = []
    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "unknown"


def test_urf_9_unknown_when_packaging_source_failed():
    """URF-9 falls back to unknown when packaging-source itself failed, even though URF-8 resolved."""
    ctx = _urf9_ctx_with_urf8(selected_option="URF-8-B")
    ctx.evidence["adapters"]["packaging-source"] = {"status": "error"}
    finding = _make_finding("URF-9", mode="deterministic")
    result = checks.deterministic._check_urf_9(ctx, finding)

    assert result.status == "unknown"


def test_cb_7_no_py2():
    """Test CB-7 when no Python 2 dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["python3", "libc6", "libglib2.0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("CB-7", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_cb_7_py2_found():
    """Test CB-7 when Python 2 dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["python2", "libc6", "libglib2.0"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("CB-7", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "python2" in result.message.lower()


def test_sec_3_no_webkit():
    """Test SEC-3 when no webkit dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libgtk-3-0", "libglib2.0"],
    }

    finding = _make_finding("SEC-3", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_sec_3_webkit_found():
    """Test SEC-3 when webkit dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libwebkit2gtk-4.0", "libgtk-3-0"],
    }

    finding = _make_finding("SEC-3", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"
    assert "webkit" in result.message.lower()


def test_sec_4_no_v8():
    """Test SEC-4 when no V8 dependencies found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libnode", "libglib2.0"],
    }

    finding = _make_finding("SEC-4", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    # libnode matches v8_patterns, so should fail
    assert result.status == "not-ok"
    assert result.severity == "required"


def test_sec_4_v8_not_found():
    """Test SEC-4 when V8 not in dependencies."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "runtime_dep_packages": ["libc6", "libgtk-3-0", "libglib2.0"],
    }

    finding = _make_finding("SEC-4", mode="deterministic")
    result = checks.deterministic._eval_dep_scan(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_esl_4_not_go():
    """Test ESL-4 when package is not Go (gate N/A; check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-4", mode="deterministic")
    result = checks.deterministic._check_esl_4(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not" in result.message.lower() and "go" in result.message.lower()


def test_esl_4_is_go():
    """Test ESL-4 when package is Go (gate active; check still passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure --buildsystem golang",
        "debian_control": "Package: myapp\nBuild-Depends: golang-go",
        "file_listing": [{"path": "main.go", "size": 100}],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-4", mode="deterministic")
    result = checks.deterministic._check_esl_4(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "go" in result.message.lower()


def test_esl_8_not_rust():
    """Test ESL-8 when package is not Rust (gate N/A; check passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-8", mode="deterministic")
    result = checks.deterministic._check_esl_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "not" in result.message.lower() and "rust" in result.message.lower()


def test_esl_8_is_rust():
    """Test ESL-8 when package is Rust (gate active; check still passes)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure --buildsystem cargo",
        "debian_control": "Package: myapp\nBuild-Depends: cargo, rustc",
        "file_listing": [{"path": "src/main.rs", "size": 100}],
        "go_sum_present": False,
        "cargo_lock_present": False,
    }

    finding = _make_finding("ESL-8", mode="deterministic")
    result = checks.deterministic._check_esl_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "rust" in result.message.lower()


def test_dep_1_no_unresolved():
    """Test DEP-1 when no unresolved runtime dependencies."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "in_scope_deps_not_in_main": [],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("DEP-1", mode="deterministic")
    result = checks.deterministic._check_dep_1(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_dep_1_unresolved_dep():
    """Test DEP-1 when unresolved dependency found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["dep-analysis"] = {
        "status": "ok",
        "in_scope_deps_not_in_main": ["myuniversepkg"],
    }
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_control": "Package: myapp",
        "debian_rules": "dh_auto_build",
        "file_listing": [],
    }

    finding = _make_finding("DEP-1", mode="deterministic")
    result = checks.deterministic._check_dep_1(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_esl_9_not_rust():
    """Test ESL-9 when package is not Rust."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp",
        "file_listing": [],
    }

    finding = _make_finding("ESL-9", mode="deterministic")
    result = checks.deterministic._check_esl_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_esl_9_rust_with_dh_cargo():
    """Test ESL-9 when Rust package uses dh_cargo."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure --buildsystem cargo\ndh_auto_build",
        "debian_control": "Package: myapp\nBuild-Depends: cargo, rustc",
        "file_listing": [{"path": "src/main.rs", "size": 100}],
    }

    finding = _make_finding("ESL-9", mode="deterministic")
    result = checks.deterministic._check_esl_9(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_esl_9_rust_without_dh_cargo():
    """Test ESL-9 when Rust package doesn't use dh_cargo."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh_auto_configure\ndh_auto_build",
        "debian_control": "Package: myapp\nBuild-Depends: cargo, rustc",
        "file_listing": [{"path": "src/main.rs", "size": 100}],
    }

    finding = _make_finding("ESL-9", mode="deterministic")
    result = checks.deterministic._check_esl_9(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_prf_8_no_warnings():
    """Test PRF-8 when no lintian warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": [],
        "lintian_errors": [],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"


def test_prf_8_few_warnings():
    """Test PRF-8 when few lintian warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": ["W1", "W2"],
        "lintian_errors": [],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "ok"


def test_prf_8_excessive_warnings():
    """Test PRF-8 when excessive lintian warnings."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": ["W1", "W2", "W3", "W4", "W5", "W6"],
        "lintian_errors": [],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"


def test_prf_8_errors():
    """Test PRF-8 when lintian errors found."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_warnings": [],
        "lintian_errors": ["E1", "E2"],
    }

    finding = _make_finding("PRF-8", mode="deterministic")
    result = checks.deterministic._check_prf_8(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


# ---------------------------------------------------------------------------
# PRF-6: Current release packaged
# ---------------------------------------------------------------------------


def test_prf_6_current_version():
    """Test PRF-6 when archive version is current with upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "1.2.3-0ubuntu1",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "1.2.3",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "ok"
    assert result.severity == "ok"
    assert "current" in result.message.lower() or "packaged" in result.message.lower()


def test_prf_6_behind_upstream():
    """Test PRF-6 when archive version is somewhat behind upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "1.1.0-2ubuntu1",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "1.3.0",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "recommended"


def test_prf_6_very_old_version():
    """Test PRF-6 when archive version is very old compared to upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "1:0.9.0-0ubuntu1",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "2.0.0",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "not-ok"
    assert result.severity == "required"


def test_prf_6_adapter_missing():
    """Test PRF-6 when lp-package-api adapter is missing."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "error",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "unknown"


def test_prf_6_current_version_with_epoch_and_ubuntu_revision():
    """PRF-6 should ignore epoch and Ubuntu revision when matching upstream."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["lp-package-api"] = {
        "status": "ok",
        "current_version": "2:3.4.5-1ubuntu2",
    }
    ctx.evidence["adapters"]["upstream-tracker"] = {
        "status": "ok",
        "latest_version": "3.4.5",
    }

    finding = _make_finding("PRF-6", mode="deterministic")
    result = checks.deterministic._check_prf_6(ctx, finding)

    assert result.status == "ok"


def test_versions_compatible_strips_debian_revision():
    """PRF-6 version comparison should use the upstream portion of package versions."""
    is_compatible, _ = checks.deterministic._versions_compatible(
        "1:2.3.4-0ubuntu1",
        "2.3.4",
    )

    assert is_compatible is True


def test_synthesis_checks_evaluated_last(monkeypatch):
    """Synthesis checks run after all others and see the accumulated findings.

    The returned list still preserves catalog order so rendering/Summary
    placement is unaffected.
    """
    from types import SimpleNamespace

    order = []
    synthesis_seen = {}

    def normal_eval(check, ctx, finding):
        order.append(check["id"])
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = f"msg {check['id']}"
        return finding

    def synth_eval(check, ctx, finding):
        order.append(check["id"])
        synthesis_seen[check["id"]] = [f.id for f in ctx.findings]
        finding.status = "ok"
        finding.severity = "ok"
        finding.confidence = "high"
        finding.message = "synthesis"
        return finding

    monkeypatch.setitem(checks.EVALUATORS, "tnorm", normal_eval)
    monkeypatch.setitem(checks.EVALUATORS, "tsyn", synth_eval)

    ctx = SimpleNamespace(
        catalog={
            "checks": [
                {"id": "A-1", "mode": "tnorm", "section": "Summary"},
                {"id": "SUM-X", "mode": "tsyn", "section": "Summary", "synthesis": True},
                {"id": "B-1", "mode": "tnorm", "section": "Dependencies"},
            ]
        },
        evidence={},
        findings=[],
    )

    result = checks.evaluate_checks(ctx)

    # Synthesis check evaluated last, after both non-synthesis checks.
    assert order == ["A-1", "B-1", "SUM-X"]
    # Returned list preserves catalog order.
    assert [f.id for f in result] == ["A-1", "SUM-X", "B-1"]
    # Synthesis check saw the accumulated non-synthesis findings via ctx.findings.
    assert synthesis_seen["SUM-X"] == ["A-1", "B-1"]


def test_summarise_findings_so_far_respects_message_cap():
    """The per-finding message cap is honoured and overridable for synthesis."""
    from types import SimpleNamespace

    ctx = SimpleNamespace(
        findings=[
            Finding(
                id="X-1",
                section="Summary",
                title="t",
                mode="deterministic",
                status="not-ok",
                severity="required",
                message="y" * 5000,
            )
        ]
    )

    default = checks.llm_eval._summarise_findings_so_far(ctx)
    assert len(default[0]["message"]) == checks.llm_eval._DEFAULT_FINDING_MESSAGE_CHARS

    synth = checks.llm_eval._summarise_findings_so_far(
        ctx, max_message_len=checks.llm_eval._SYNTHESIS_FINDING_MESSAGE_CHARS
    )
    assert len(synth[0]["message"]) == checks.llm_eval._SYNTHESIS_FINDING_MESSAGE_CHARS


def test_combined_language_gate_suppresses_umbrella_message():
    """A combined 'go|rust' gate must not emit a redundant umbrella OK line."""
    from types import SimpleNamespace

    import checks

    ctx = SimpleNamespace(
        evidence={"adapters": {"packaging-source": {"status": "ok"}}},
    )
    check = {
        "id": "ESL-1",
        "section": "Embedded sources and static linking",
        "title": "No embedded source present",
        "mode": "ev_to_ai",
        "language_gate": "go|rust",
    }

    finding = checks._evaluate_single_check(check, ctx)

    assert finding.status == "ok"
    assert finding.message == ""


def test_single_language_gate_still_emits_message():
    """A single-language gate keeps its specific 'not a <lang> package' line."""
    from types import SimpleNamespace

    import checks

    ctx = SimpleNamespace(
        evidence={"adapters": {"packaging-source": {"status": "ok"}}},
    )
    check = {
        "id": "ESL-4",
        "section": "Embedded sources and static linking",
        "title": "Go gate",
        "mode": "ev_to_ai",
        "language_gate": "go",
    }

    finding = checks._evaluate_single_check(check, ctx)

    assert finding.status == "ok"
    assert finding.message == "not a go package, no extra constraints to consider in that regard"


def test_evaluate_checks_maps_failed_adapters_to_low_confidence_findings(monkeypatch):
    """Low-confidence unresolved findings should expose causing adapter failures."""
    from types import SimpleNamespace

    import checks

    def low_conf_eval(check, ctx, finding):
        finding.status = "not-ok"
        finding.severity = "recommended"
        finding.confidence = "low"
        finding.message = "needs review"
        finding.todo = "TODO: - verify manually"
        return finding

    monkeypatch.setitem(checks.EVALUATORS, "tlow", low_conf_eval)

    ctx = SimpleNamespace(
        catalog={
            "checks": [
                {
                    "id": "RDO-X",
                    "mode": "tlow",
                    "section": "Rationale",
                    "adapters_required": ["dep-analysis", "packaging-source"],
                    "adapters_optional": ["git-ubuntu-delta"],
                }
            ]
        },
        evidence={
            "adapters": {
                "dep-analysis": {"status": "error"},
                "packaging-source": {"status": "ok"},
                "git-ubuntu-delta": {"status": "pending"},
            }
        },
        findings=[],
    )

    findings = checks.evaluate_checks(ctx)
    assert len(findings) == 1
    assert findings[0].adapter_error_cause == ["dep-analysis", "git-ubuntu-delta"]


def test_evaluate_single_check_unknown_mode_has_normalized_todo_prefix():
    """Unknown evaluator mode should degrade to unknown with TODO prefix preserved."""
    from types import SimpleNamespace

    import checks

    ctx = SimpleNamespace(evidence={"adapters": {}})
    check = {
        "id": "X-UNKNOWN",
        "section": "Summary",
        "title": "Unknown mode check",
        "mode": "does-not-exist",
    }

    finding = checks._evaluate_single_check(check, ctx)

    assert finding.status == "unknown"
    assert finding.todo.startswith("TODO:")


def test_apply_llm_response_invalid_payload_degrades_to_unknown_low_confidence():
    check = {
        "id": "RDO-X",
        "section": "Rationale",
        "title": "Malformed response check",
        "mode": "ev_to_ai",
    }
    finding = _make_finding("RDO-X", title="Malformed response check", mode="ev_to_ai")

    result = checks.llm_eval._apply_llm_response("not-a-dict", check, finding)

    assert result.status == "unknown"
    assert result.confidence == "low"
    assert result.todo.startswith("TODO:")


def test_extract_build_test_hints_detects_wiring():
    hints = checks.llm_eval._extract_build_test_hints(
        "override_dh_auto_test:\n\tmake check\n",
        "Running tests\n5 passed\n",
    )
    assert hints["rules_has_test_wiring"] is True
    assert "make check" in hints["rules_test_runners"]
    assert hints["build_log_runs_tests"] is True
    assert hints["build_log_has_pass_fail"] is True
    assert hints["failures_possibly_ignored"] is False


def test_extract_build_test_hints_no_tests():
    hints = checks.llm_eval._extract_build_test_hints(
        "%:\n\tdh $@\n",
        "dh_auto_build\n",
    )
    assert hints["rules_has_test_wiring"] is False
    assert hints["rules_test_runners"] == []


def test_extract_build_test_hints_failures_ignored():
    hints = checks.llm_eval._extract_build_test_hints(
        "override_dh_auto_test:\n\tmake check || true\n",
        "",
    )
    assert hints["failures_possibly_ignored"] is True


# ---------------------------------------------------------------------------
# CB-3 autopkgtest detection: both evidence sources reach the model (feedback #1)
# ---------------------------------------------------------------------------


class _EvCtx:
    """Minimal ctx for exercising _build_evidence_payload."""

    def __init__(self, adapters):
        self.source_package = "libgav1"
        self.bug_id = "2158712"
        self.series = "devel"
        self.bug = {"title": "[MIR] libgav1"}
        self.reporter_mir_content = ""
        self.findings = []
        self.untrusted_nonce = "NONCE"
        self.evidence = {"adapters": adapters}


def test_cb3_payload_includes_autopkgtest_and_tests_control():
    """CB-3 must receive the autopkgtest DB result AND the full debian/tests/control
    so the model can credit a passing autopkgtest even though it judges non-triviality."""
    control = "Tests: decode\nDepends: libgav1-bin\nRestrictions: allow-stderr\n"
    ctx = _EvCtx(
        {
            "packaging-source": {
                "status": "ok",
                "debian_tests_control": control,
                "debian_control": "Source: libgav1",
                "file_listing": [],
            },
            "autopkgtest-db": {
                "status": "ok",
                "has_autopkgtest": True,
                "passing_arches": ["amd64", "arm64", "armhf", "ppc64el", "s390x"],
                "failing_arches": [],
            },
        }
    )
    check = {
        "id": "CB-3",
        "section": "Common blockers",
        "mode": "ev_to_ai",
        "adapters_required": ["packaging-source", "autopkgtest-db"],
    }
    payload = checks.llm_eval._build_evidence_payload(check, ctx)

    # debian/tests/control is kept verbatim (declares the functional 'decode' test).
    assert payload["packaging-source"]["debian_tests_control"] == control
    # The authoritative pass/fail signal is present.
    assert payload["autopkgtest-db"]["has_autopkgtest"] is True
    assert "s390x" in payload["autopkgtest-db"]["passing_arches"]
    assert payload["autopkgtest-db"]["failing_arches"] == []


# ---------------------------------------------------------------------------
# CB-6 E2E-via-consumers: reverse-dep + consumer autopkgtest evidence reaches AI
# ---------------------------------------------------------------------------


def test_cb6_payload_includes_prioritised_consumer_summary():
    """CB-6 must receive a compact, prioritised reverse-dep consumer summary."""
    ctx = _EvCtx(
        {
            "dep-analysis": {"status": "ok"},
            "autopkgtest-db": {"status": "ok", "has_autopkgtest": False},
            "reverse-deps": {
                "status": "ok",
                "release": "plucky-proposed",
                "consumers": [
                    {"source": "pipewire", "kind": "runtime"},
                    {"source": "quietlib", "kind": "build"},
                ],
            },
            "consumer-autopkgtests": {
                "status": "ok",
                "consumers": [
                    {
                        "source": "pipewire",
                        "kind": "runtime",
                        "has_autopkgtest": True,
                        "passing_arches": ["amd64", "arm64"],
                        "failing_arches": [],
                    },
                    {
                        "source": "quietlib",
                        "kind": "build",
                        "has_autopkgtest": False,
                        "passing_arches": [],
                        "failing_arches": [],
                    },
                ],
            },
        }
    )
    check = {
        "id": "CB-6",
        "section": "Common blockers",
        "mode": "ev_to_ai",
        "adapters_required": [
            "dep-analysis",
            "autopkgtest-db",
            "reverse-deps",
            "consumer-autopkgtests",
        ],
    }
    payload = checks.llm_eval._build_evidence_payload(check, ctx)

    summary = payload["consumer_test_summary"]
    assert summary["reverse_deps_release"] == "plucky-proposed"
    assert summary["total_consumers"] == 2
    assert summary["consumers_with_tests_count"] == 1
    assert summary["consumers_with_tests"][0]["source"] == "pipewire"
    assert summary["consumers_with_tests"][0]["passing_arches"] == ["amd64", "arm64"]
    assert summary["consumers_without_tests_count"] == 1
    assert summary["consumers_without_tests"][0]["source"] == "quietlib"


# ---------------------------------------------------------------------------
# SUM-3 promotion status: grounded in lp-package-api's current_component
# rather than re-derived from a (possibly truncated) debian/control excerpt.
# ---------------------------------------------------------------------------


def test_sum3_payload_lists_binaries_needing_promotion():
    """Regression for bug 2161382 (prompt-toolkit): universe component must
    surface a concrete promotion list, not an unresolved TBD."""
    ctx = _EvCtx({"lp-package-api": {"status": "ok", "current_component": "universe"}})
    ctx.requested_binaries = ["python3-prompt-toolkit"]
    check = {
        "id": "SUM-3",
        "section": "Summary",
        "mode": "ev_to_ai",
        "adapters_required": ["lp-package-api"],
    }
    payload = checks.llm_eval._build_evidence_payload(check, ctx)

    status = payload["promotion_status"]
    assert status["current_component"] == "universe"
    assert status["already_in_main"] is False
    assert status["needs_promotion"] == ["python3-prompt-toolkit"]
    assert status["binaries"] == ["python3-prompt-toolkit"]


def test_sum3_payload_already_in_main_needs_no_promotion():
    ctx = _EvCtx({"lp-package-api": {"status": "ok", "current_component": "main"}})
    ctx.requested_binaries = ["libfoo1"]
    check = {
        "id": "SUM-3",
        "section": "Summary",
        "mode": "ev_to_ai",
        "adapters_required": ["lp-package-api"],
    }
    payload = checks.llm_eval._build_evidence_payload(check, ctx)

    status = payload["promotion_status"]
    assert status["already_in_main"] is True
    assert status["needs_promotion"] == []
    assert status["binaries"] == ["libfoo1"]


def test_sum3_payload_falls_back_to_dep_analysis_binaries():
    """When requested_binaries isn't set (e.g. bare test ctx), fall back to
    dep-analysis's binary_packages list rather than an empty list."""
    ctx = _EvCtx(
        {
            "lp-package-api": {"status": "ok", "current_component": "universe"},
            "dep-analysis": {"status": "ok", "binary_packages": ["libfoo1", "libfoo-dev"]},
        }
    )
    check = {
        "id": "SUM-3",
        "section": "Summary",
        "mode": "ev_to_ai",
        "adapters_required": ["lp-package-api"],
        "adapters_optional": ["dep-analysis"],
    }
    payload = checks.llm_eval._build_evidence_payload(check, ctx)

    status = payload["promotion_status"]
    assert status["binaries"] == ["libfoo1", "libfoo-dev"]
    assert status["needs_promotion"] == ["libfoo1", "libfoo-dev"]


def test_sum3_payload_unknown_component_does_not_claim_already_in_main():
    ctx = _EvCtx({"lp-package-api": {"status": "error"}})
    ctx.requested_binaries = ["libfoo1"]
    check = {
        "id": "SUM-3",
        "section": "Summary",
        "mode": "ev_to_ai",
        "adapters_required": ["lp-package-api"],
    }
    payload = checks.llm_eval._build_evidence_payload(check, ctx)

    status = payload["promotion_status"]
    assert status["current_component"] == "unknown"
    assert status["already_in_main"] is False
    assert status["needs_promotion"] == ["libfoo1"]


# ---------------------------------------------------------------------------
# Comment-aware source scanning: matches confined to commented-out code are
# "found, reported but ok" (user-test regression for the rust-sequoia-sq run,
# where rust doc comments like '/// let err = self.name.ok_or("nobody")...'
# were listed under Problems).
# ---------------------------------------------------------------------------


def test_comment_classifier_line_leading_markers():
    """Whole-line comments classify as inactive; mixed lines never do."""
    from checks.deterministic import _hit_is_comment, _line_comment_markers

    rust_hit = './debian/rust-vendor/writeable/src/try_writeable.rs:62:///         let err = self.name.ok_or("nobody").try_write_to_parts(sink)?.err();'
    rust_block = "./src/a.rs:7:/* setuid note */"
    py_hit = "./tools/harness.py:12:# setuid helper used in tests"
    c_hit = "./src/io.c:3:// nobody drops privileges here"
    sh_hit = "./scripts/setup.sh:4:# sudo is not needed"

    for hit in (rust_hit, rust_block, py_hit, c_hit, sh_hit):
        assert _hit_is_comment(hit), hit

    # Mixed lines stay active: real privilege setup can never hide behind a
    # trailing comment (exact shape from the existing chmod test).
    mixed = "./scripts/install.sh:5:chmod u+s /usr/bin/myhelper  # setuid"
    assert not _hit_is_comment(mixed)

    # Unknown extension -> conservative: active.
    assert not _hit_is_comment("./data/blob.bin:1:setuid inside")
    assert _line_comment_markers("./debian/rules") == ("#",)


def test_urf_4_rust_doc_comment_hits_are_found_but_ok():
    """Exact regression shape from the rust-sequoia-sq run: all URF-4 hits in
    /// doc comments -> the check succeeds while naming the matches, instead
    of listing them under Problems."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh",
        "debian_control": "Package: rust-sequoia-sq",
        "nobody_source_hits": [
            './debian/rust-vendor/writeable/src/try_writeable.rs:62:///         let err = self.name.ok_or("nobody").try_write_to_parts(sink)?.err();',
            './debian/rust-vendor/writeable/src/try_writeable.rs:245:    /// #        let _ = self.name.ok_or("nobody").try_write_to_parts(sink)?;',
        ],
        "nobody_source_files": [],
    }
    ctx.evidence["adapters"]["fetch-build"] = {"status": "ok", "nobody_owned_binaries": []}

    result = checks.deterministic._check_urf_4(ctx, _make_finding("URF-4"))

    assert result.status == "ok"
    assert "commented-out code only" in result.message
    assert "try_writeable.rs" in result.message
    assert result.todo == ""


def test_urf_5_rust_doc_comment_hits_are_found_but_ok():
    """Same regression shape for setuid/setgid: tokio/rustix doc comments."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh",
        "debian_control": "Package: rust-sequoia-sq",
        "setuid_setgid_source_hits": [
            "./debian/rust-vendor/tokio/src/process/mod.rs:682:    /// `setuid` call in the child process. Failure in the `setuid`",
            "./debian/rust-vendor/rustix/src/thread/id.rs:21:/// `setuid(uid)`",
        ],
        "setuid_setgid_source_files": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
    }
    ctx.evidence["adapters"]["fetch-build"] = {"status": "ok", "setuid_setgid_binaries": []}

    result = checks.deterministic._check_urf_5(ctx, _make_finding("URF-5"))

    assert result.status == "ok"
    assert "commented-out code only" in result.message
    assert result.todo == ""


def test_urf_5_mixed_comment_hits_still_flag():
    """One doc-comment hit plus one active-code hit -> Problem lists the
    active occurrence (comment hits are kept out of the failure sample)."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "dh",
        "debian_control": "Package: myapp",
        "setuid_setgid_source_hits": [
            "./debian/rust-vendor/tokio/src/x.rs:682:    /// `setuid` call here",
            "./src/priv.c:9:int drop = setuid(0);",
        ],
        "setuid_setgid_source_files": [],
    }
    ctx.evidence["adapters"]["lintian"] = {
        "status": "ok",
        "lintian_errors": [],
        "lintian_warnings": [],
    }
    ctx.evidence["adapters"]["fetch-build"] = {"status": "ok", "setuid_setgid_binaries": []}

    result = checks.deterministic._check_urf_5(ctx, _make_finding("URF-5"))

    assert result.status == "not-ok"
    assert "priv.c" in result.message
    assert "x.rs" not in result.message


def test_urf_3_commented_rules_line_is_found_but_ok():
    """debian/rules hash-commented sudo mention -> ok with note."""
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "# sudo apt-get foo was considered, not used",
        "debian_control": "Package: myapp",
    }

    result = checks.deterministic._check_urf_3(ctx, _make_finding("URF-3"))

    assert result.status == "ok"
    assert "commented-out code only" in result.message
    assert result.todo == ""


def test_urf_3_active_rules_line_still_flags():
    ctx = _Ctx()
    ctx.evidence["adapters"]["packaging-source"] = {
        "status": "ok",
        "debian_rules": "\tsudo make install",
        "debian_control": "Package: myapp",
    }

    result = checks.deterministic._check_urf_3(ctx, _make_finding("URF-3"))

    assert result.status == "not-ok"


# ---------------------------------------------------------------------------
# human_verdict checks (SUM-5 overall verdict, SUM-6 security review): the
# final call is ALWAYS the human's - the AI synthesis stays an advisory NOTE
# and the full option TODO block is kept for the reviewer to prune.
# ---------------------------------------------------------------------------


def _sum5_check(human_verdict=True):
    return {
        "id": "SUM-5",
        "section": "Summary",
        "title": "Overall ACK/NACK/ACK-with-conditions",
        "mode": "ai",
        "human_verdict": human_verdict,
        "todo_refs": [
            "TODO-A: MIR team ACK",
            "TODO-B: MIR team NACK",
            "TODO-C: MIR team ACK under the constraint to resolve the below listed TODOs",
        ],
        "options": [
            {
                "id": "SUM-5-A",
                "todo_ref": "TODO-A: MIR team ACK",
                "outcome": "ok",
                "render": "- Suggesting ACK: everything looks fine",
            },
            {
                "id": "SUM-5-B",
                "todo_ref": "TODO-B: MIR team NACK",
                "outcome": "nack",
                "render": "- Suggesting NACK",
            },
            {
                "id": "SUM-5-C",
                "todo_ref": "TODO-C: MIR team ACK under the constraint",
                "outcome": "required",
                "render": "- Suggesting ACK with conditions",
            },
        ],
    }


def test_human_verdict_free_form_model_answer_is_never_pre_decided():
    """User-test regression: the model returned a free-form 'status: ok'
    answer with no option id, and the draft rendered a confident
    'Suggesting ACK' line. With human_verdict it stays Left to decide with
    all three template TODOs and the suggestion only as a note."""
    check = _sum5_check()
    finding = _make_finding("SUM-5", mode="ai")
    response = {
        "status": "ok",
        "confidence": "medium",
        "message": "Suggesting ACK: no required-severity findings or hard blockers.",
        "rationale": "No findings reached required severity; all open items are recommended.",
    }

    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "unknown"
    assert "TODO-A: MIR team ACK" in result.todo
    assert "TODO-B: MIR team NACK" in result.todo
    assert "TODO-C: MIR team ACK under the constraint" in result.todo
    assert result.message.startswith("AI suggestion")
    assert "Suggesting ACK" in result.message
    assert "No findings reached required severity" in result.rationale


def test_human_verdict_option_pick_still_keeps_all_todos():
    """Even a confident option pick only becomes the advisory note."""
    check = _sum5_check()
    finding = _make_finding("SUM-5", mode="ai")
    response = {
        "selected_option": "SUM-5-A",
        "confidence": "high",
        "message": "Suggesting ACK: no required findings.",
        "rationale": "Clean run.",
    }

    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "unknown"
    assert "TODO-A: MIR team ACK" in result.todo
    assert "TODO-B: MIR team NACK" in result.todo
    assert "TODO-C: MIR team ACK under the constraint" in result.todo
    assert "SUM-5-A" in result.message
    assert result.rationale == "Clean run."


def test_human_verdict_absent_keeps_the_old_option_flow():
    """The field is opt-in: without it, a free-form ok answer keeps the old
    semantics (this is exactly what the user report flagged for SUM-5)."""
    check = _sum5_check(human_verdict=False)
    finding = _make_finding("SUM-5", mode="ai")
    response = {
        "status": "ok",
        "confidence": "high",
        "message": "Suggesting ACK: no required findings.",
        "rationale": "Clean run.",
    }

    result = checks.llm_eval._apply_llm_response(response, check, finding)

    assert result.status == "ok"
    assert result.todo == ""


def test_sum6_security_review_is_a_human_verdict_check():
    """SUM-6 keeps the same always-decide shape as the SUM-5 contract."""
    from pathlib import Path

    import catalog as catalog_module

    tool_root = Path(__file__).resolve().parent.parent
    review = catalog_module.load_catalog_for_role(tool_root, tool_root.parent.parent, "review")
    by_id = {c["id"]: c for c in review["checks"]}

    assert by_id["SUM-5"].get("human_verdict") is True
    assert by_id["SUM-6"].get("human_verdict") is True
