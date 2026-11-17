"""Unit tests for the review-coverage script."""

import argparse
import email.message
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import script as rc


class TestParse:
    def test_parses_sets_in_order(self):
        sets = rc.parse_codeowners("* @s-makin @rkratky\nMIR/ @setharnold @joalif\n")
        assert [(s.pattern, s.members) for s in sets] == [
            ("*", ["s-makin", "rkratky"]),
            ("MIR/", ["setharnold", "joalif"]),
        ]

    def test_normalizes_case_and_at(self):
        assert rc.parse_codeowners("MIR/ @SetHarnold\n")[0].members == ["setharnold"]

    def test_skips_comments_blanks(self):
        sets = rc.parse_codeowners("# c\n\nMIR/ @a\n  # ind\nSRU/ @b\n")
        assert [s.pattern for s in sets] == ["MIR/", "SRU/"]

    def test_memberless_line_clears_requirement(self):
        sets = rc.parse_codeowners("MIR/\n")
        assert sets[0].pattern == "MIR/" and sets[0].members == []

    def test_bracket_is_literal(self):
        p = rc.pattern_to_regex("x[1].md")
        assert p.match("x[1].md")
        assert not p.match("x1.md")

    def test_inline_comment_stripped(self):
        sets = rc.parse_codeowners("MIR/ @a @b #This is an inline comment.\n")
        assert sets[0].members == ["a", "b"]
        assert sets[0].unresolvable == []

    def test_team_and_email_owners_are_unresolvable(self):
        sets = rc.parse_codeowners("X/ @org/team docs@example.com @alice\n")
        s = sets[0]
        assert s.members == ["alice"]
        assert s.unresolvable == ["@org/team", "docs@example.com"]

    def test_quotes_are_literal(self):
        # N11: CODEOWNERS has no quoting; `'` and `"` are ordinary path chars.
        sets = rc.parse_codeowners("docs/user's-guide/ @bob\n")
        assert sets[0].pattern == "docs/user's-guide/"
        assert sets[0].members == ["bob"]
        sets = rc.parse_codeowners('docs/say-"hi".md @bob\n')
        assert sets[0].pattern == 'docs/say-"hi".md'
        assert sets[0].members == ["bob"]

    def test_escaped_space_pattern(self):
        sets = rc.parse_codeowners("path\\ with\\ spaces/x.md @a\n")
        assert sets[0].pattern == "path with spaces/x.md"
        assert rc.pattern_to_regex(sets[0].pattern).match("path with spaces/x.md")


class TestMatch:
    def test_root_anchored_dir(self):
        p = rc.pattern_to_regex("tools/auto-mir/")
        assert p.match("tools/auto-mir/x.md")
        assert not p.match("docs/tools/auto-mir/x.md")

    def test_trailing_slash_any_depth(self):
        p = rc.pattern_to_regex("SRU/")
        assert p.match("SRU/x.md")
        assert p.match("docs/who-makes-ubuntu/roles/SRU/x.md")
        assert not p.match("docs/SRUs/x.md")

    def test_leading_slash(self):
        p = rc.pattern_to_regex("/.github/CODEOWNERS")
        assert p.match(".github/CODEOWNERS")
        assert not p.match("docs/.github/CODEOWNERS")

    def test_doublestar_leading(self):
        p = rc.pattern_to_regex("**/dmb-*.md")
        assert p.match("dmb-c.md")
        assert p.match("docs/gov/dmb-c.md")
        assert not p.match("docs/gov/dmb-c.rst")

    def test_basename_any_depth(self):
        p = rc.pattern_to_regex("rocks-team.md")
        assert p.match("rocks-team.md")
        assert p.match("docs/deep/rocks-team.md")

    def test_last_match_wins(self):
        sets = rc.parse_codeowners("* @ta\nSRU/ @sru\n")
        assert rc.match_file("SRU/x.md", sets).pattern == "SRU/"
        assert rc.match_file("o.md", sets).pattern == "*"

    def test_no_match_none(self):
        assert rc.match_file("docs/o.md", rc.parse_codeowners("MIR/ @m\n")) is None

    def test_ownerless_last_match_skipped(self):
        # last matching entry has no owners -> no requirement for that file
        sets = rc.parse_codeowners("MIR/ @m\nMIR/\n")
        assert rc.reduce_pr_sets(["MIR/x.md"], sets) == []


class TestMatchSemantics:
    """R7/R8: gitignore-equivalent pattern semantics for CODEOWNERS."""

    def test_bare_pattern_covers_directory_contents(self):
        p = rc.pattern_to_regex("docs")
        assert p.match("docs")
        assert p.match("docs/x.md")
        assert p.match("a/docs/x.md")
        assert p.match("a/docs")
        assert not p.match("docs2/x.md")

    def test_trailing_slash_is_contents_only(self):
        p = rc.pattern_to_regex("docs/")
        assert p.match("docs/x.md")
        assert p.match("docs/a/b.md")
        assert not p.match("docs2/x.md")
        assert not p.match("docs")

    def test_anchored_no_trailing_slash_covers_contents(self):
        p = rc.pattern_to_regex("/apps/github")
        assert p.match("apps/github/x.md")
        assert p.match("apps/github")
        assert not p.match("x/apps/github")

    def test_anchored_trailing_slash_contents_only(self):
        p = rc.pattern_to_regex("/apps/github/")
        assert p.match("apps/github/x.md")
        assert not p.match("apps/github")

    def test_star_matches_any_depth(self):
        p = rc.pattern_to_regex("*")
        assert p.match("a.md")
        assert p.match("a/b.md")

    def test_mid_doublestar_zero_or_more_dirs(self):
        p = rc.pattern_to_regex("a/**/b")
        assert p.match("a/b")
        assert p.match("a/x/b")
        assert p.match("a/x/y/b")
        assert not p.match("a/xb")

    def test_trailing_doublestar_everything_inside(self):
        p = rc.pattern_to_regex("a/**")
        assert p.match("a/x")
        assert p.match("a/x/y")
        assert not p.match("a")

    def test_non_special_doublestar_does_not_cross_slash(self):
        # A non-special "**" behaves like a single "*": it cannot cross a
        # "/". "foo**" reduces to "foo*"; a wildcard final segment does not
        # extend to directory contents (N1), so "foo/bar" is not matched.
        p1 = rc.pattern_to_regex("foo**")
        assert p1.match("foobar")
        assert not p1.match("foo/bar")
        p2 = rc.pattern_to_regex("a**b")
        assert p2.match("axb")
        assert not p2.match("a/x/b")
        assert not p2.match("a/xb")

    def test_wildcard_last_segment_does_not_cover_nested(self):
        # N1, GitHub docs example: "The `docs/*` pattern will match files like
        # `docs/getting-started.md` but not further nested files like
        # `docs/build-app/troubleshooting.md`."
        p = rc.pattern_to_regex("docs/*")
        assert p.match("docs/getting-started.md")
        assert not p.match("docs/build-app/troubleshooting.md")
        p2 = rc.pattern_to_regex("/apps/*")
        assert p2.match("apps/x.md")
        assert not p2.match("apps/github/x.md")
        # A basename glob still matches at any depth.
        assert rc.pattern_to_regex("*.md").match("a/b/c.md")

    def test_plus_one_glob(self):
        p = rc.pattern_to_regex("plus-one-*.md")
        assert p.match("plus-one-1.md")
        assert p.match("x/plus-one-2.md")


class TestReduce:
    def test_distinct_first_seen(self):
        sets = rc.parse_codeowners("* @ta\nMIR/ @m\nSRU/ @s\n")
        got = rc.reduce_pr_sets(["b.md", "MIR/x", "SRU/y", "MIR/z"], sets)
        assert [s.pattern for s in got] == ["*", "MIR/", "SRU/"]


class TestNames:
    def test_loads_flat_subset(self):
        text = '# c\n"*": "Technical authors"\n"MIR/": MIR\n'
        assert rc.load_team_names(text) == {"*": "Technical authors", "MIR/": "MIR"}

    def test_display_fallback(self):
        assert rc.team_display_name("nope/", {}) == "nope/"
        assert rc.team_display_name("MIR/", {"MIR/": "MIR"}) == "MIR"


class TestCoverage:
    SETS_TXT = "MIR/ @setharnold @cpaelzer\n**/aa-*.md @cpaelzer @paride\n"

    def _cov(self, reviews, author=None):
        return rc.compute_coverage(
            ["MIR/x.md", "docs/aa-c.md"],
            rc.parse_codeowners(self.SETS_TXT),
            reviews,
            author=author,
        )

    def test_multi_set_approver_satisfies_all(self):
        cov = self._cov([{"user": {"login": "cpaelzer"}, "state": "APPROVED"}])
        assert [s.pattern for s in cov.satisfied] == ["MIR/", "**/aa-*.md"]
        assert cov.pending == [] and cov.approvers == ["cpaelzer"]

    def test_pending_keeps_members(self):
        cov = self._cov([{"user": {"login": "setharnold"}, "state": "APPROVED"}])
        assert [s.pattern for s in cov.satisfied] == ["MIR/"]
        assert [s.pattern for s in cov.pending] == ["**/aa-*.md"]

    def test_latest_state_wins(self):
        cov = self._cov(
            [
                {"user": {"login": "cpaelzer"}, "state": "APPROVED"},
                {"user": {"login": "cpaelzer"}, "state": "CHANGES_REQUESTED"},
            ]
        )
        assert cov.satisfied == [] and cov.approvers == []

    def test_dismissed_reverts(self):
        cov = self._cov(
            [
                {"user": {"login": "cpaelzer"}, "state": "APPROVED"},
                {"user": {"login": "cpaelzer"}, "state": "DISMISSED"},
            ]
        )
        assert cov.satisfied == []

    def test_author_self_approval_ignored(self):
        cov = self._cov(
            [{"user": {"login": "setharnold"}, "state": "APPROVED"}],
            author="setharnold",
        )
        assert cov.satisfied == []

    def test_comment_after_approval_does_not_revert(self):
        # R6: a COMMENTED review must never undo a prior approval.
        cov = self._cov(
            [
                {"user": {"login": "cpaelzer"}, "state": "APPROVED"},
                {"user": {"login": "cpaelzer"}, "state": "COMMENTED"},
            ]
        )
        assert cov.approvers == ["cpaelzer"]
        assert [s.pattern for s in cov.satisfied] == ["MIR/", "**/aa-*.md"]

    def test_pending_review_never_counts(self):
        cov = self._cov([{"user": {"login": "cpaelzer"}, "state": "PENDING"}])
        assert cov.approvers == [] and cov.satisfied == []

    def test_team_only_set_cannot_block(self):
        # G2: nobody the bot can verify may approve it, so it cannot block.
        sets = rc.parse_codeowners("MIR/ @org/team\n")
        cov = rc.compute_coverage(
            ["MIR/x.md"], sets, [{"user": {"login": "a"}, "state": "APPROVED"}]
        )
        assert cov.satisfied == [] and cov.pending == []
        assert [s.pattern for s in cov.unapprovable] == ["MIR/"]
        assert cov.unapprovable[0].unresolvable == ["@org/team"]

    def test_mixed_team_set_satisfied_by_individual_owner(self):
        # N7: GitHub accepts an approval from ANY listed owner, so an
        # individual owner's approval satisfies a set that also lists a team.
        sets = rc.parse_codeowners("MIR/ @org/team @a\n")
        cov = rc.compute_coverage(
            ["MIR/x.md"], sets, [{"user": {"login": "a"}, "state": "APPROVED"}]
        )
        assert [s.pattern for s in cov.satisfied] == ["MIR/"]
        assert cov.pending == []

    def test_mixed_team_set_without_approval_is_pending(self):
        sets = rc.parse_codeowners("MIR/ @org/team @a\n")
        cov = rc.compute_coverage(["MIR/x.md"], sets, [])
        assert [s.pattern for s in cov.pending] == ["MIR/"]


class TestCull:
    def test_formula(self):
        sets = rc.parse_codeowners(
            "MIR/ @setharnold @cpaelzer @joalif\n**/aa-*.md @cpaelzer @paride\n"
        )
        cov = rc.compute_coverage(
            ["MIR/x.md", "docs/aa-c.md"],
            sets,
            [{"user": {"login": "setharnold"}, "state": "APPROVED"}],
        )
        assert rc.compute_cull(["cpaelzer", "joalif", "paride", "outsider"], cov) == [
            "joalif"
        ]

    def test_no_pending_culls_all_satisfied_members(self):
        cov = rc.compute_coverage(
            ["MIR/x.md"],
            rc.parse_codeowners("MIR/ @a @b\n"),
            [{"user": {"login": "a"}, "state": "APPROVED"}],
        )
        assert rc.compute_cull(["a", "b"], cov) == ["b"]

    def test_team_owned_pending_set_members_never_culled(self):
        sets = rc.parse_codeowners("MIR/ @org/team @a @b\n")
        cov = rc.compute_coverage(["MIR/x.md"], sets, [])
        assert rc.compute_cull(["a", "b"], cov) == []

    def test_mixed_team_set_satisfied_culls_other_members(self):
        sets = rc.parse_codeowners("MIR/ @org/team @a @b\n")
        cov = rc.compute_coverage(
            ["MIR/x.md"], sets, [{"user": {"login": "a"}, "state": "APPROVED"}]
        )
        assert rc.compute_cull(["a", "b"], cov) == ["b"]


class FakeClient:
    def __init__(self):
        self.repo = "ubuntu/ubuntu-project-docs"
        self.comments = {}
        self.removed = []
        self.requested_adds = []
        self.next_id = 1
        self.pr_files, self.pr_reviews, self.pr_requested = {}, {}, {}
        self.base_codeowners = ""
        self.base_yaml = ""
        self.codeowners_errors = []
        self.statuses = []
        self.status_urls = []
        self.dispatches = []
        self.open_pr_numbers = []
        self._pr = {
            "number": 7,
            "user": {"login": "s-makin"},
            "state": "open",
            "head": {
                "sha": "abc",
                "ref": "feat",
                "repo": {"fork": False, "full_name": "ubuntu/ubuntu-project-docs"},
            },
            "base": {"ref": "main"},
        }

    def get_pr(self, n):
        return dict(self._pr, number=n)

    def get_pr_files(self, n):
        return self.pr_files.get(n, [])

    def get_pr_reviews(self, n):
        return self.pr_reviews.get(n, [])

    def get_requested_reviewers(self, n):
        return self.pr_requested.get(n, [])

    def get_base_codeowners(self):
        return self.base_codeowners

    def get_base_text(self, path):
        return self.base_yaml if path.endswith(".yaml") else None

    def get_ref_codeowners(self, repo_full, ref):
        return None

    def _default_branch(self):
        return "main"

    def get_sticky_comment(self, n, marker=rc.STICKY_MARKER):
        c = self.comments.get(n)
        return c if c and c[1].lstrip().startswith(marker) else None

    def get_codeowners_errors(self):
        return self.codeowners_errors

    def set_status(self, sha, state, description, target_url):
        self.statuses.append((sha, state, description))
        self.status_urls.append(target_url)

    def dispatch_workflow(self, workflow, ref, inputs):
        self.dispatches.append((workflow, ref, dict(inputs)))

    def list_open_prs(self):
        return list(self.open_pr_numbers)

    def delete_comment(self, cid):
        for n, (i, _b) in list(self.comments.items()):
            if i == cid:
                del self.comments[n]

    def post_comment(self, n, body):
        cid = self.next_id
        self.next_id += 1
        self.comments[n] = (cid, body)
        return cid

    def patch_comment(self, cid, body):
        for n, (i, b) in list(self.comments.items()):
            if i == cid:
                self.comments[n] = (cid, body)

    def remove_requested_reviewers(self, n, logins):
        # Like the real API: answer with the updated pull request.
        self.removed.extend(logins)
        self.pr_requested[n] = [
            u for u in self.pr_requested.get(n, []) if u not in logins
        ]
        return {
            "number": n,
            "requested_reviewers": [{"login": u} for u in self.pr_requested[n]],
        }

    def request_reviewers(self, n, logins):
        self.requested_adds.extend(logins)
        self.pr_requested[n] = self.pr_requested.get(n, []) + list(logins)


def _mk_cov():
    sets = rc.parse_codeowners("MIR/ @setharnold @joalif @didrocks\n")
    return rc.compute_coverage(
        ["MIR/a.md", "MIR/b.md"],
        sets,
        [{"user": {"login": "setharnold"}, "state": "APPROVED"}],
    )


class TestRender:
    def test_marker_first_and_status(self):
        cov = _mk_cov()
        body = rc.render_comment(
            cov,
            {"MIR/": "MIR"},
            7,
            {"MIR/": ["MIR/a.md"]},
            "https://github.com/o/r",
            cull=[],
        )
        assert body.startswith(rc.STICKY_MARKER)
        assert "0 of 1" in body and "approved by @setharnold" in body

    def test_pending_status_and_fallback_name(self):
        sets = rc.parse_codeowners("MIR/ @a @b\n")
        cov = rc.compute_coverage(["MIR/a.md"], sets, [])
        body = rc.render_comment(
            cov, {}, 7, {"MIR/": ["MIR/a.md"]}, "https://github.com/o/r", cull=[]
        )
        assert "1 of 1" in body and "pending" in body and "MIR/" in body

    def test_file_links_diff_anchor_and_cap(self):
        files = [f"MIR/f{i}.md" for i in range(7)]
        sets = rc.parse_codeowners("MIR/ @a @b\n")
        cov = rc.compute_coverage(files, sets, [])
        fb = {s.pattern: files for s in cov.matched_sets}
        body = rc.render_comment(cov, {}, 7, fb, "https://github.com/o/r", cull=[])
        import hashlib as _h

        assert "pull/7/files#diff-" + _h.sha256(b"MIR/f0.md").hexdigest() in body
        assert "+2 more" in body and "MIR/f5.md" not in body

    def test_removed_note_persists_from_state(self):
        # R24: the note is derived from the persistent culled state, so it
        # survives later runs (and the body stays byte-stable: no churn).
        cov = _mk_cov()
        url = "https://github.com/o/r"
        first = rc.render_comment(
            cov,
            {},
            7,
            {},
            url,
            cull=["joalif", "didrocks"],
            culled=["joalif", "didrocks"],
        )
        later = rc.render_comment(
            cov, {}, 7, {}, url, cull=[], culled=["joalif", "didrocks"]
        )
        assert "removed from queue" in later and "@joalif" in later
        assert rc.comment_body_hash(first) == rc.comment_body_hash(later)
        gone = rc.render_comment(cov, {}, 7, {}, url, cull=[], culled=[])
        assert "removed from queue" not in gone

    def test_unresolvable_owner_warning(self):
        sets = rc.parse_codeowners("MIR/ @org/team @a\n")
        cov = rc.compute_coverage(["MIR/a.md"], sets, [])
        body = rc.render_comment(cov, {}, 7, {}, "https://github.com/o/r", cull=[])
        assert "Unverifiable owners" in body and "@org/team" in body

    def test_mixed_team_set_header_matches_row(self):
        # N7: the header count and the row status must agree.
        sets = rc.parse_codeowners("MIR/ @org/team @a\n")
        cov = rc.compute_coverage(
            ["MIR/a.md"], sets, [{"user": {"login": "a"}, "state": "APPROVED"}]
        )
        body = rc.render_comment(cov, {}, 7, {}, "https://github.com/o/r", cull=[])
        assert "0 of 1" in body and "approved by @a" in body
        assert "Unverifiable owners" not in body

    def test_status_markers_are_text_symbols_not_emoji(self):
        sets = rc.parse_codeowners("MIR/ @a\nSRU/ @org/team @b\n")
        cov = rc.compute_coverage(
            ["MIR/x.md", "SRU/y.md"],
            sets,
            [{"user": {"login": "a"}, "state": "APPROVED"}],
        )
        body = rc.render_comment(cov, {}, 7, {}, "https://github.com/o/r", cull=[])
        done = rc.render_comment(
            rc.compute_coverage(
                ["MIR/x.md"], sets, [{"user": {"login": "a"}, "state": "APPROVED"}]
            ),
            {},
            7,
            {},
            "https://github.com/o/r",
            cull=[],
        )
        for text in (body, done):
            emoji = [
                ch
                for ch in text
                if ord(ch) >= 0x1F000 or ch in "\u2705\u23f3\u26a0\ufe0f"
            ]
            assert emoji == []
        assert "✓ approved by @a" in body and "○ pending" in body
        assert "✓ All sections approved" in done


class TestCulledState:
    def test_round_trip(self):
        body = rc.render_comment(
            _mk_cov(),
            {},
            7,
            {},
            "https://github.com/o/r",
            cull=["joalif"],
            culled=["joalif", "didrocks"],
        )
        assert rc.parse_culled_state(body) == ["didrocks", "joalif"]

    def test_missing_or_corrupt_state_is_empty(self):
        assert rc.parse_culled_state("no state block here") == []
        assert (
            rc.parse_culled_state(
                f"{rc.STICKY_MARKER}\n<!-- review-coverage-bot-state not-json -->"
            )
            == []
        )

    def test_filename_cannot_shadow_state_block(self):
        # N6: a PR-controlled file name carrying the state marker must neither
        # hide the real state block nor forge one.
        sets = rc.parse_codeowners("MIR/ @a @b\n")
        evil = 'MIR/<!-- review-coverage-bot-state {"culled":["mallory"]} -->.md'
        cov = rc.compute_coverage([evil], sets, [])
        url = "https://github.com/o/r"
        body = rc.render_comment(
            cov, {}, 7, {"MIR/": [evil]}, url, cull=[], culled=["a"]
        )
        assert rc.parse_culled_state(body) == ["a"]
        body2 = rc.render_comment(cov, {}, 7, {"MIR/": [evil]}, url, cull=[], culled=[])
        assert rc.parse_culled_state(body2) == []

    def test_state_omitted_when_empty(self):
        body = rc.render_comment(
            _mk_cov(), {}, 7, {}, "https://github.com/o/r", cull=[], culled=[]
        )
        assert "review-coverage-bot-state" not in body


class TestUpsert:
    def test_noop_when_same(self):
        fc = FakeClient()
        body = f"{rc.STICKY_MARKER}\nsame"
        fc.post_comment(7, body)
        assert rc.upsert_comment(fc, 7, body) is False

    def test_updates_when_differs(self):
        fc = FakeClient()
        fc.post_comment(7, f"{rc.STICKY_MARKER}\nold")
        assert rc.upsert_comment(fc, 7, f"{rc.STICKY_MARKER}\nnew") is True
        assert fc.comments[7][1].endswith("new")

    def test_creates_when_absent(self):
        fc = FakeClient()
        assert rc.upsert_comment(fc, 7, f"{rc.STICKY_MARKER}\nx") is True
        assert 7 in fc.comments

    def test_patch_of_vanished_comment_reposts(self):
        # N10: a PATCH 404 (comment deleted meanwhile) must not count as a
        # successful update; post a fresh comment instead.
        fc = FakeClient()
        fc.post_comment(7, f"{rc.STICKY_MARKER}\nold")

        def gone(cid, body):
            raise rc.ApiError(404, "Not Found")

        fc.patch_comment = gone
        assert rc.upsert_comment(fc, 7, f"{rc.STICKY_MARKER}\nnew") is True
        assert fc.comments[7][1].endswith("new")


class TestStickyAuthor:
    def test_non_bot_marker_ignored(self):
        comments = [
            {"id": 1, "user": {"login": "evil"}, "body": f"{rc.STICKY_MARKER}\nhijack"},
            {
                "id": 2,
                "user": {"login": "github-actions[bot]"},
                "body": f"{rc.STICKY_MARKER}\nreal",
            },
        ]
        got = rc._bot_sticky(comments, rc.STICKY_MARKER)
        assert got == [(2, f"{rc.STICKY_MARKER}\nreal")]

    def test_duplicates_newest_wins_and_extras_deleted(self):
        class C:
            repo = "o/r"

            def __init__(self):
                self.deleted = []

            def get_all_pages(self, path, params=None):
                return [
                    {
                        "id": 1,
                        "user": {"login": "github-actions[bot]"},
                        "body": rc.STICKY_MARKER + "\nold",
                    },
                    {
                        "id": 2,
                        "user": {"login": "evil"},
                        "body": rc.STICKY_MARKER + "\nfake",
                    },
                    {
                        "id": 3,
                        "user": {"login": "github-actions[bot]"},
                        "body": rc.STICKY_MARKER + "\nnew",
                    },
                ]

            def delete(self, path, **kw):
                self.deleted.append(path)
                return {}

        c = C()
        got = rc.GitHubClient.get_sticky_comment(c, 7)
        assert got == (3, rc.STICKY_MARKER + "\nnew")
        assert any(p.endswith("issues/comments/1") for p in c.deleted)


class TestRunCoverage:
    def test_full_chain(self):
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @setharnold @joalif\n"
        fc.pr_files[7] = [{"filename": "MIR/a.md"}]
        fc.pr_reviews[7] = [{"user": {"login": "setharnold"}, "state": "APPROVED"}]
        fc.pr_requested[7] = ["setharnold", "joalif", "cpaelzer"]
        out = rc.run_coverage(fc, 7, dry_run=False)
        assert out.changed is True
        assert fc.removed == ["joalif"]
        assert "review-coverage-bot-state" in fc.comments[7][1]

    def test_dry_run_writes_nothing(self):
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @setharnold @joalif\n"
        fc.pr_files[7] = [{"filename": "MIR/a.md"}]
        fc.pr_reviews[7] = [{"user": {"login": "setharnold"}, "state": "APPROVED"}]
        fc.pr_requested[7] = ["setharnold", "joalif"]
        rc.run_coverage(fc, 7, dry_run=True)
        assert fc.comments == {} and fc.removed == [] and fc.requested_adds == []

    def test_cull_then_rerequest_on_dismissal(self):
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @setharnold @joalif\n"
        fc.pr_files[7] = [{"filename": "MIR/a.md"}]
        fc.pr_reviews[7] = [{"user": {"login": "setharnold"}, "state": "APPROVED"}]
        fc.pr_requested[7] = ["joalif"]
        rc.run_coverage(fc, 7)
        assert fc.removed == ["joalif"]
        assert "joalif" in rc.parse_culled_state(fc.comments[7][1])

        # The approval is dismissed: MIR/ is pending again, so joalif (whom
        # the bot itself culled) must be re-requested and dropped from state.
        fc.pr_reviews[7] = [{"user": {"login": "setharnold"}, "state": "DISMISSED"}]
        rc.run_coverage(fc, 7)
        assert fc.requested_adds == ["joalif"]
        assert rc.parse_culled_state(fc.comments[7][1]) == []

    def test_missing_pr_raises(self):
        class C(FakeClient):
            def get_pr(self, n):
                return None

        with pytest.raises(RuntimeError):
            rc.run_coverage(C(), 7)

    @staticmethod
    def _culled_fc(culled):
        """MIR/ pending, `culled` recorded in the existing sticky comment."""
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @setharnold @joalif @didrocks\n"
        fc.pr_files[7] = [{"filename": "MIR/a.md"}]
        state = json.dumps({"culled": culled}, separators=(",", ":"))
        fc.post_comment(
            7, f"{rc.STICKY_MARKER}\nold\n\n<!-- {rc.STATE_MARKER} {state} -->"
        )
        return fc

    def test_rejected_rerequest_is_dropped_and_comment_written(self):
        # N3: a permanently rejected re-request (422) must not brick the PR.
        fc = self._culled_fc(["joalif"])

        def reject(n, logins):
            raise rc.ApiError(422, "not a collaborator")

        fc.request_reviewers = reject
        rc.run_coverage(fc, 7)
        body = fc.comments[7][1]
        assert "\nold\n" not in body
        assert rc.parse_culled_state(body) == []
        assert "@joalif" in body and "could not be re-requested" in body

    def test_transient_rerequest_failure_kept_and_surfaced(self):
        fc = self._culled_fc(["joalif"])

        def flaky(n, logins):
            raise rc.ApiError(502, "bad gateway")

        fc.request_reviewers = flaky
        with pytest.raises(RuntimeError):
            rc.run_coverage(fc, 7)
        body = fc.comments[7][1]
        assert "\nold\n" not in body
        assert rc.parse_culled_state(body) == ["joalif"]
        assert "will retry" in body

    def test_partial_rerequest_failure_isolated_per_login(self):
        fc = self._culled_fc(["joalif", "didrocks"])
        adds = []

        def partial(n, logins):
            if "didrocks" in logins:
                raise rc.ApiError(422, "nope")
            adds.extend(logins)

        fc.request_reviewers = partial
        rc.run_coverage(fc, 7)
        assert adds == ["joalif"]
        assert rc.parse_culled_state(fc.comments[7][1]) == []

    def _approved_fc(self):
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @setharnold @joalif\n"
        fc.pr_files[7] = [{"filename": "MIR/a.md"}]
        fc.pr_reviews[7] = [{"user": {"login": "setharnold"}, "state": "APPROVED"}]
        fc.pr_requested[7] = ["joalif"]
        return fc

    def test_unconfirmed_removal_not_recorded(self):
        # R24: a DELETE that did not actually remove the reviewer must not be
        # recorded as a cull.
        fc = self._approved_fc()
        fc.remove_requested_reviewers = lambda n, logins: None
        rc.run_coverage(fc, 7)
        body = fc.comments[7][1]
        assert rc.parse_culled_state(body) == []
        assert "removed from queue" not in body

    def test_failed_removal_still_writes_comment(self):
        fc = self._approved_fc()

        def fail(n, logins):
            raise rc.ApiError(422, "boom")

        fc.remove_requested_reviewers = fail
        with pytest.raises(RuntimeError):
            rc.run_coverage(fc, 7)
        assert 7 in fc.comments
        assert rc.parse_culled_state(fc.comments[7][1]) == []

    def test_removed_note_survives_next_run(self):
        fc = self._approved_fc()
        rc.run_coverage(fc, 7)
        assert "removed from queue" in fc.comments[7][1]
        out = rc.run_coverage(fc, 7)
        assert "removed from queue" in fc.comments[7][1]
        assert out.changed is False


class TestCli:
    def _fake(self, monkeypatch):
        monkeypatch.setattr(rc, "make_client", lambda **kw: FakeClient())

    def test_missing_token_exit_1(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
        assert rc.main(["coverage", "--pr", "1"]) == 1

    def test_coverage_requires_selector(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "t")
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        self._fake(monkeypatch)
        assert rc.main(["coverage"]) != 0

    def test_drift_check_missing_token_exit_1(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        assert rc.main(["drift-check"]) == 1

    def test_coverage_happy_path(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "t")
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        self._fake(monkeypatch)
        assert rc.main(["coverage", "--pr", "7"]) == 0

    def test_sync_requires_selector(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "t")
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        self._fake(monkeypatch)
        assert rc.main(["sync-yaml"]) != 0

    def test_pr_zero_rejected(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "t")
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        self._fake(monkeypatch)
        assert rc.main(["coverage", "--pr", "0"]) != 0
        assert rc.main(["sync-yaml", "--pr", "0"]) != 0

    def test_help_exits_zero(self, capsys):
        # N13: `--help` is a successful exit, not an error.
        assert rc.main(["--help"]) == 0

    def test_dry_run_before_subcommand(self):
        ns = argparse.Namespace(dry_run=False)
        args = rc.build_parser().parse_args(
            ["--dry-run", "coverage", "--pr", "1"], namespace=ns
        )
        assert args.dry_run is True

    def test_dry_run_after_subcommand(self):
        ns = argparse.Namespace(dry_run=False)
        args = rc.build_parser().parse_args(
            ["coverage", "--dry-run", "--pr", "1"], namespace=ns
        )
        assert args.dry_run is True

    def test_dry_run_absent_defaults_false(self):
        ns = argparse.Namespace(dry_run=False)
        args = rc.build_parser().parse_args(["coverage", "--pr", "1"], namespace=ns)
        assert args.dry_run is False

    def test_dry_run_before_subcommand_reaches_runner(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "t")
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        self._fake(monkeypatch)
        seen = {}
        monkeypatch.setattr(
            rc,
            "run_coverage",
            lambda c, n, dry_run=False: seen.setdefault("dry_run", dry_run),
        )
        assert rc.main(["--dry-run", "coverage", "--pr", "7"]) == 0
        assert seen["dry_run"] is True

    def test_all_open_isolates_failures(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "t")
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        fc = FakeClient()
        fc.list_open_prs = lambda: [7, 8]
        monkeypatch.setattr(rc, "make_client", lambda **kw: fc)
        seen = []

        def fake_run(client, n, dry_run=False):
            seen.append(n)
            if n == 8:
                raise RuntimeError("boom")

        monkeypatch.setattr(rc, "run_coverage", fake_run)
        assert rc.main(["coverage", "--all-open"]) == 1
        assert seen == [7, 8]


class TestDefaults:
    def test_star(self):
        assert rc.default_team_name("*") == "Technical authors"

    def test_dir(self):
        assert rc.default_team_name("MIR/") == "MIR"

    def test_glob_prefix(self):
        assert rc.default_team_name("**/dmb-*.md") == "DMB"

    def test_stem(self):
        assert rc.default_team_name("rocks-team.md") == "rocks-team"


class TestRegen:
    def test_merge_forward_and_new(self):
        sets = rc.parse_codeowners("* @t\nMIR/ @m\nDMBNEW/ @d\n")
        text, changed = rc.regenerate_yaml(
            [("*", "Technical authors"), ("MIR/", "MIR")], sets
        )
        assert '"MIR/": "MIR"' in text and '"*": "Technical authors"' in text
        assert '"DMBNEW/": "DMBNEW"' in text and changed is True

    def test_unchanged_flag_false(self):
        sets = rc.parse_codeowners("MIR/ @m\n")
        text1, _ = rc.regenerate_yaml([], sets)
        text2, changed = rc.regenerate_yaml(rc.parse_teams_yaml_ordered(text1), sets)
        assert changed is False


class TestYamlRoundTrip:
    def test_colon_pattern_round_trips(self):
        sets = rc.parse_codeowners("docs/a:b.md @m\n")
        text, _ = rc.regenerate_yaml([], sets)
        entries = rc.parse_teams_yaml_ordered(text)
        text2, changed = rc.regenerate_yaml(entries, sets)
        assert changed is False and text2 == text
        assert rc.load_team_names(text)["docs/a:b.md"] == "a:b"

    def test_quote_in_pattern_round_trips(self):
        sets = rc.parse_codeowners('we\\"ird.md @m\n')
        text, _ = rc.regenerate_yaml([], sets)
        entries = rc.parse_teams_yaml_ordered(text)
        text2, changed = rc.regenerate_yaml(entries, sets)
        assert changed is False and text2 == text


class FakeSyncClient(FakeClient):
    def __init__(self):
        super().__init__()
        self.calls = []
        self.open_prs = []
        self.yaml_on_head = ""
        self.base_yaml = ""


class TestSyncForPr:
    def test_noop_without_codeowners_change(self, monkeypatch):
        fc = FakeSyncClient()
        monkeypatch.setattr(
            rc,
            "git_data_commit",
            lambda c, b, p, t, **kw: fc.calls.append(("COMMIT", p)) or True,
        )
        fc.pr_files[7] = [{"filename": "docs/x.md"}]
        fc.base_codeowners = "MIR/ @m\n"
        monkeypatch.setattr(
            fc, "get_ref_codeowners", lambda repo, ref: "MIR/ @m\n", raising=False
        )
        # head yaml identical to base yaml
        monkeypatch.setattr(
            fc,
            "get_head_yaml",
            lambda n: rc.regenerate_yaml([], rc.parse_codeowners("MIR/ @m\n"))[0],
            raising=False,
        )
        assert rc.sync_yaml_for_pr(fc, 7) == "noop"
        assert ("COMMIT", rc.TEAMS_YAML_PATH) not in fc.calls

    def test_same_repo_commits(self, monkeypatch):
        fc = FakeSyncClient()
        monkeypatch.setattr(
            rc,
            "git_data_commit",
            lambda c, b, p, t, **kw: fc.calls.append(("COMMIT", p)) or True,
        )
        fc.base_codeowners = "MIR/ @m\n"
        fc.pr_files[7] = [{"filename": ".github/CODEOWNERS"}]
        monkeypatch.setattr(
            fc,
            "get_ref_codeowners",
            lambda repo, ref: "MIR/ @m\nSRU/ @s\n",
            raising=False,
        )
        monkeypatch.setattr(fc, "get_head_yaml", lambda n: "", raising=False)
        assert rc.sync_yaml_for_pr(fc, 7) == "committed"
        assert ("COMMIT", rc.TEAMS_YAML_PATH) in fc.calls

    def test_same_repo_pr_in_a_forked_repo_commits(self, monkeypatch):
        # Found by end-to-end testing on a fork: `head.repo.fork` is true
        # whenever the repository itself is a fork, even for a PR between
        # two of its own branches. Only the exact full_name match decides.
        fc = FakeSyncClient()
        fc._pr = dict(
            fc._pr,
            head={
                "sha": "abc",
                "ref": "feat",
                "repo": {"fork": True, "full_name": fc.repo},
            },
        )
        monkeypatch.setattr(
            rc,
            "git_data_commit",
            lambda c, b, p, t, **kw: fc.calls.append(("COMMIT", p)) or True,
        )
        fc.pr_files[7] = [{"filename": ".github/CODEOWNERS"}]
        monkeypatch.setattr(
            fc,
            "get_ref_codeowners",
            lambda repo, ref: "MIR/ @m\nSRU/ @s\n",
            raising=False,
        )
        monkeypatch.setattr(fc, "get_head_yaml", lambda n: "", raising=False)
        assert rc.sync_yaml_for_pr(fc, 7) == "committed"

    def test_null_head_repo_is_treated_as_fork(self, monkeypatch):
        # R12: a missing/null head.repo must never be treated as same-repo.
        fc = FakeSyncClient()
        fc._pr = dict(fc._pr, head={"sha": "abc", "ref": "feat"})
        fc.pr_files[7] = [{"filename": ".github/CODEOWNERS"}]
        fc.base_codeowners = "MIR/ @m\n"
        monkeypatch.setattr(
            fc, "get_ref_codeowners", lambda repo, ref: None, raising=False
        )
        # get_ref_codeowners(head_repo="") returning None -> "noop", not a
        # commit: the guard must prevent reaching git_data_commit at all.
        assert rc.sync_yaml_for_pr(fc, 7) in ("noop",)

    def test_refuses_to_commit_to_default_branch(self, monkeypatch):
        fc = FakeSyncClient()
        fc._pr = dict(
            fc._pr,
            head={
                "sha": "abc",
                "ref": "main",
                "repo": {"fork": False, "full_name": fc.repo},
            },
        )
        fc.pr_files[7] = [{"filename": ".github/CODEOWNERS"}]
        fc.base_codeowners = "MIR/ @m\n"
        monkeypatch.setattr(
            fc,
            "get_ref_codeowners",
            lambda repo, ref: "MIR/ @m\nSRU/ @s\n",
            raising=False,
        )
        monkeypatch.setattr(fc, "get_head_yaml", lambda n: "", raising=False)
        assert rc.sync_yaml_for_pr(fc, 7) == "failed"


class TestDriftCheck:
    def test_up_to_date_zero(self, monkeypatch):
        fc = FakeSyncClient()
        sets = rc.parse_codeowners("MIR/ @m\n")
        text, _ = rc.regenerate_yaml([], sets)
        monkeypatch.setattr(
            fc, "get_base_codeowners", lambda: "MIR/ @m\n", raising=False
        )
        monkeypatch.setattr(fc, "get_base_text", lambda p: text, raising=False)
        assert rc.drift_check(fc) == 0

    def test_drift_one(self, monkeypatch):
        fc = FakeSyncClient()
        monkeypatch.setattr(
            fc, "get_base_codeowners", lambda: "MIR/ @m\nSRU/ @s\n", raising=False
        )
        monkeypatch.setattr(fc, "get_base_text", lambda p: "", raising=False)
        assert rc.drift_check(fc) == 1


class TestDriftCheckLocal:
    def test_local_up_to_date(self, tmp_path, monkeypatch):
        (tmp_path / ".github").mkdir()
        co = "# c\nMIR/ @m\n"
        yaml_text, _ = rc.regenerate_yaml([], rc.parse_codeowners(co))
        (tmp_path / rc.CODEOWNERS_PATH).write_text(co)
        (tmp_path / rc.TEAMS_YAML_PATH).write_text(yaml_text)
        monkeypatch.chdir(tmp_path)
        assert rc.drift_check(None, local=True) == 0

    def test_local_drift(self, tmp_path, monkeypatch):
        (tmp_path / ".github").mkdir()
        (tmp_path / rc.CODEOWNERS_PATH).write_text("MIR/ @m\nSRU/ @s\n")
        (tmp_path / rc.TEAMS_YAML_PATH).write_text('# x\n"MIR/": "MIR"\n')
        monkeypatch.chdir(tmp_path)
        assert rc.drift_check(None, local=True) == 1

    def test_local_missing_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert rc.drift_check(None, local=True) == 1


class TestRegression:
    REAL_CODEOWNERS = """\
# TAs
* @s-makin @rkratky @msuchane
# MIR team (ownerless line clears TA requirement, owned line re-adds it)
MIR/
tools/auto-mir/
MIR/ @setharnold @joalif @didrocks @cpaelzer @freyes @pushkarnk
tools/auto-mir/ @setharnold @joalif @didrocks @cpaelzer @freyes @pushkarnk
SRU/
SRU/ @basak @enr0n @tjaalton @panlinux @julian-klode @raof @awhitcroft @matthewruffell
tech-board/
tech-board/ @basak @mwhudson @seb128 @teward
release-team/ @utkarsh2102 @ginggs @paride @Hyask
community/ @aaronprisk @ilvipero
**/aa-*.md @panlinux @cpaelzer @paride @ginggs @mwhudson @utkarsh2102 @tjaalton @seb128 @raof
**/dmb-*.md @cpaelzer @lvoytek @rbasak @utkarsh2102 @athos-ribeiro @bdrung @uraltun
/.github/CODEOWNERS @s-makin @rkratky @setharnold
plus-one-*.md @s-makin @rkratky
rocks-team.md @asanvaq @cjdcordeiro
"""

    def test_drift_converges_on_real_codeowners(self):
        # BUG-03 regression: duplicated/ownerless patterns must dedupe so the
        # committed yaml converges (12 unique entries, no duplicate keys).
        co_sets = rc.parse_codeowners(self.REAL_CODEOWNERS)
        text1, _ = rc.regenerate_yaml([], co_sets)
        entries1 = rc.parse_teams_yaml_ordered(text1)
        assert len(entries1) == 12
        assert len({p for p, _ in entries1}) == 12
        text2, changed = rc.regenerate_yaml(entries1, co_sets)
        assert changed is False and text2 == text1

    def test_path_sanitized_in_render(self):
        # BUG-05 regression: markdown injection via PR-controlled paths.
        # The evil path must actually be rendered (a previous version of
        # this test matched zero files and passed vacuously).
        sets = rc.parse_codeowners("MIR/ @a @b\n")
        evil = "MIR/evil` [click](mailto:x@y.z) `.md"
        cov = rc.compute_coverage([evil], sets, [])
        assert cov.matched_sets, "the evil path must match a CODEOWNERS set"
        body = rc.render_comment(
            cov, {}, 7, {"MIR/": [evil]}, "https://github.com/o/r", cull=[]
        )
        # The whole path is ONE code span inside the link text. CommonMark
        # code spans bind tighter than link brackets, so the inner
        # "[click](...)" can never form a link. Backslash escapes are not
        # processed inside code spans, so none are emitted (N8).
        import hashlib as _h

        url = (
            "https://github.com/o/r/pull/7/files#diff-"
            + _h.sha256(evil.encode()).hexdigest()
        )
        assert f"[`MIR/evil' [click](mailto:x@y.z) '.md`]({url})" in body
        assert "``" not in body
        assert "\\[" not in body and "\\(" not in body

    def test_brackets_in_path_render_verbatim(self):
        sets = rc.parse_codeowners("MIR/ @a @b\n")
        cov = rc.compute_coverage(["MIR/a[b].md"], sets, [])
        body = rc.render_comment(
            cov, {}, 7, {"MIR/": ["MIR/a[b].md"]}, "https://github.com/o/r", cull=[]
        )
        assert "[`MIR/a[b].md`](" in body

    def test_hash_stable_across_footer_timestamps(self):
        # BUG-06 regression: the footer timestamp must not defeat the no-op.
        base = f"{rc.STICKY_MARKER}\n| MIR | x | pending |\n"
        body1 = base + "\n---\n*review-coverage bot · updated 2026-09-23 10:00 UTC*"
        body2 = base + "\n---\n*review-coverage bot · updated 2026-09-23 11:00 UTC*"
        assert rc.comment_body_hash(body1) == rc.comment_body_hash(body2)

    def test_fork_sync_reports_commented(self, monkeypatch):
        # BUG-08 regression: fork CODEOWNERS sync must be visible, not silent.
        fc = FakeSyncClient()
        fc._pr = dict(
            fc._pr,
            head={
                "sha": "abc",
                "ref": "feat",
                "repo": {"fork": True, "full_name": "other/repo"},
            },
        )
        fc.pr_files[7] = [{"filename": ".github/CODEOWNERS"}]
        fc.base_codeowners = "MIR/ @m\n"
        monkeypatch.setattr(
            fc,
            "get_ref_codeowners",
            lambda repo, ref: "MIR/ @m\nSRU/ @s\n",
            raising=False,
        )
        monkeypatch.setattr(fc, "get_head_yaml", lambda n: "", raising=False)
        assert rc.sync_yaml_for_pr(fc, 7) == "commented"
        body = fc.comments[7][1]
        assert ".github/.github/" not in body
        assert rc.TEAMS_YAML_PATH in body


def _http_error(code, headers=None, body=b'{"message":"err"}'):
    msg = email.message.Message()
    for k, v in (headers or {}).items():
        msg[k] = str(v)
    return urllib.error.HTTPError(
        "https://api.github.com/x", code, "err", msg, io.BytesIO(body)
    )


class _FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class TestHttpRequest:
    def test_404_returns_none(self, monkeypatch):
        def boom(*a, **k):
            raise _http_error(404)

        monkeypatch.setattr(urllib.request, "urlopen", boom)
        assert rc.GitHubClient("t", "o/r").get("/x") is None

    def test_404_on_write_raises(self, monkeypatch):
        # N10: only reads may treat 404 as "absent"; a write that 404s failed.
        def boom(*a, **k):
            raise _http_error(404)

        monkeypatch.setattr(urllib.request, "urlopen", boom)
        c = rc.GitHubClient("t", "o/r")
        for call in (
            lambda: c.patch("/x", body={}),
            lambda: c.delete("/x", body={}),
            lambda: c.post("/x", body={}),
        ):
            with pytest.raises(rc.ApiError) as ei:
                call()
            assert ei.value.status == 404

    def test_post_urlerror_not_retried(self, monkeypatch):
        # N9: a connection error on POST may have reached GitHub; never replay.
        sleeps, calls = [], []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))

        def boom(*a, **k):
            calls.append(1)
            raise urllib.error.URLError("connection reset")

        monkeypatch.setattr(urllib.request, "urlopen", boom)
        with pytest.raises(rc.ApiError):
            rc.GitHubClient("t", "o/r").post("/x", body={})
        assert len(calls) == 1 and sleeps == []

    def test_get_urlerror_retried(self, monkeypatch):
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
        responses = [urllib.error.URLError("reset"), _FakeResponse({"ok": 1})]

        def fake(*a, **k):
            r = responses.pop(0)
            if isinstance(r, BaseException):
                raise r
            return r

        monkeypatch.setattr(urllib.request, "urlopen", fake)
        assert rc.GitHubClient("t", "o/r").get("/x") == {"ok": 1}
        assert len(sleeps) == 1

    def test_403_secondary_rate_limit_retry_after(self, monkeypatch):
        # N12: secondary rate limits send retry-after without remaining=0.
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
        responses = [_http_error(403, {"retry-after": "3"}), _FakeResponse({"ok": 1})]

        def fake(*a, **k):
            r = responses.pop(0)
            if isinstance(r, BaseException):
                raise r
            return r

        monkeypatch.setattr(urllib.request, "urlopen", fake)
        assert rc.GitHubClient("t", "o/r").get("/x") == {"ok": 1}
        assert sleeps == [3.0]

    def test_422_raises_api_error(self, monkeypatch):
        def boom(*a, **k):
            raise _http_error(422)

        monkeypatch.setattr(urllib.request, "urlopen", boom)
        with pytest.raises(rc.ApiError):
            rc.GitHubClient("t", "o/r").post("/x", body={})

    def test_post_5xx_raises_without_retry(self, monkeypatch):
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))

        def boom(*a, **k):
            raise _http_error(502)

        monkeypatch.setattr(urllib.request, "urlopen", boom)
        with pytest.raises(rc.ApiError):
            rc.GitHubClient("t", "o/r").post("/x", body={})
        assert sleeps == []

    def test_patch_5xx_retries_then_succeeds(self, monkeypatch):
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
        responses = [_http_error(502), _FakeResponse({"ok": 1})]

        def fake(*a, **k):
            r = responses.pop(0)
            if isinstance(r, BaseException):
                raise r
            return r

        monkeypatch.setattr(urllib.request, "urlopen", fake)
        result = rc.GitHubClient("t", "o/r").patch("/x", body={})
        assert result == {"ok": 1}
        assert len(sleeps) == 1

    def test_429_retry_after_then_succeeds(self, monkeypatch):
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
        responses = [_http_error(429, {"retry-after": "7"}), _FakeResponse({"ok": 1})]

        def fake(*a, **k):
            r = responses.pop(0)
            if isinstance(r, BaseException):
                raise r
            return r

        monkeypatch.setattr(urllib.request, "urlopen", fake)
        result = rc.GitHubClient("t", "o/r").get("/x")
        assert result == {"ok": 1}
        assert sleeps == [7.0]

    def test_403_ratelimit_reset_capped(self, monkeypatch):
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))
        far_future = time.time() + 10_000
        responses = [
            _http_error(
                403,
                {"x-ratelimit-remaining": "0", "x-ratelimit-reset": str(far_future)},
            ),
            _FakeResponse({"ok": 1}),
        ]

        def fake(*a, **k):
            r = responses.pop(0)
            if isinstance(r, BaseException):
                raise r
            return r

        monkeypatch.setattr(urllib.request, "urlopen", fake)
        result = rc.GitHubClient("t", "o/r").get("/x")
        assert result == {"ok": 1}
        assert 0 <= sleeps[0] <= rc.MAX_SLEEP_SECONDS

    def test_plain_403_raises(self, monkeypatch):
        def boom(*a, **k):
            raise _http_error(403)

        monkeypatch.setattr(urllib.request, "urlopen", boom)
        with pytest.raises(rc.ApiError):
            rc.GitHubClient("t", "o/r").get("/x")

    def test_pagination_aborts_on_failure(self, monkeypatch):
        c = rc.GitHubClient("t", "o/r")
        monkeypatch.setattr(c, "get", lambda *a, **k: None)
        with pytest.raises(RuntimeError):
            c.get_all_pages("/x")


class TestGitDataCommit:
    class _Client:
        repo = "o/r"

        def __init__(self, fail_patch=False, missing_ref=False):
            self.calls = []
            self.fail_patch = fail_patch
            self.missing_ref = missing_ref

        def get(self, path, **kw):
            self.calls.append(("GET", path))
            if self.missing_ref and path.endswith("/git/ref/heads/feat"):
                return None
            if path.endswith("/git/ref/heads/feat"):
                return {"object": {"sha": "headsha"}}
            if path.endswith("/git/commits/headsha"):
                return {"tree": {"sha": "treesha"}}
            return {}

        def post(self, path, **kw):
            self.calls.append(("POST", path))
            if path.endswith("/git/blobs"):
                return {"sha": "blobsha"}
            if path.endswith("/git/trees"):
                return {"sha": "newtree"}
            if path.endswith("/git/commits"):
                return {"sha": "newcommit"}
            return {}

        def patch(self, path, **kw):
            self.calls.append(("PATCH", path))
            return None if self.fail_patch else {"object": {"sha": "newsha"}}

    def test_commit_updates_ref(self):
        c = self._Client()
        assert rc.git_data_commit(c, "feat", ".github/x.yaml", "data") is True
        assert ("PATCH", "/repos/o/r/git/refs/heads/feat") in c.calls

    def test_missing_ref_returns_false(self):
        c = self._Client(missing_ref=True)
        assert rc.git_data_commit(c, "feat", ".github/x.yaml", "data") is False

    def test_failed_ref_update_returns_false(self):
        c = self._Client(fail_patch=True)
        assert rc.git_data_commit(c, "feat", ".github/x.yaml", "data") is False


SYNC_HEAD_FILTER = "ubuntu:review-coverage-bot/update-teams-yaml"


class TestSyncBase:
    def _client(self, drift=True):
        fc = FakeSyncClient()
        if drift:
            fc.base_codeowners = "MIR/ @m\nSRU/ @s\n"
            fc.base_yaml = rc.regenerate_yaml([], rc.parse_codeowners("MIR/ @m\n"))[0]
        else:
            fc.base_codeowners = "MIR/ @m\n"
            fc.base_yaml = rc.regenerate_yaml([], rc.parse_codeowners("MIR/ @m\n"))[0]
        return fc

    def _wire(
        self, monkeypatch, fc, existing_sync_ref=None, open_prs=None, pr_result="ok"
    ):
        state = {"sync_ref": existing_sync_ref, "calls": [], "pulls_params": []}

        def fake_get(path, **kw):
            state["calls"].append(("GET", path))
            if path.endswith("/git/ref/heads/review-coverage-bot/update-teams-yaml"):
                return state["sync_ref"]
            if path.endswith("/git/ref/heads/main"):
                return {"object": {"sha": "basesha"}}
            return {}

        def fake_post(path, **kw):
            state["calls"].append(("POST", path))
            if path.endswith("/git/refs"):
                state["sync_ref"] = {"object": {"sha": "basesha"}}
                return {"ref": "refs/heads/x"}
            if path.endswith("/pulls"):
                return (
                    None
                    if pr_result == "fail"
                    else {"number": 9, "html_url": "https://x/pull/9"}
                )
            return {}

        def fake_patch(path, **kw):
            state["calls"].append(("PATCH", path))
            return {"object": {"sha": "newsha"}}

        def fake_get_all_pages(path, params=None):
            state["pulls_params"].append(dict(params or {}))
            # Emulate the real API (N2): `head` must be `owner:branch`; the
            # `owner/repo:branch` form silently matches nothing.
            if (params or {}).get("head") == SYNC_HEAD_FILTER:
                return open_prs or []
            return []

        monkeypatch.setattr(fc, "get", fake_get, raising=False)
        monkeypatch.setattr(fc, "post", fake_post, raising=False)
        monkeypatch.setattr(fc, "patch", fake_patch, raising=False)
        monkeypatch.setattr(fc, "get_all_pages", fake_get_all_pages, raising=False)
        monkeypatch.setattr(rc, "git_data_commit", lambda c, b, p, t, **kw: True)
        return state

    def test_creates_branch_and_opens_pr(self, monkeypatch):
        fc = self._client()
        state = self._wire(monkeypatch, fc)
        assert rc.sync_yaml_base(fc) is True
        assert ("POST", "/repos/ubuntu/ubuntu-project-docs/git/refs") in state["calls"]
        assert ("POST", "/repos/ubuntu/ubuntu-project-docs/pulls") in state["calls"]

    def test_stale_branch_without_pr_is_reset(self, monkeypatch):
        fc = self._client()
        state = self._wire(
            monkeypatch, fc, existing_sync_ref={"object": {"sha": "stale"}}, open_prs=[]
        )
        assert rc.sync_yaml_base(fc) is True
        assert (
            "PATCH",
            "/repos/ubuntu/ubuntu-project-docs/git/refs/heads/review-coverage-bot/update-teams-yaml",
        ) in state["calls"]

    def test_open_pr_is_noop(self, monkeypatch):
        fc = self._client()
        state = self._wire(
            monkeypatch,
            fc,
            existing_sync_ref={"object": {"sha": "stale"}},
            open_prs=[{"number": 5}],
        )
        assert rc.sync_yaml_base(fc) is False
        assert not any(call[0] == "PATCH" for call in state["calls"])
        assert not any(call[0] == "POST" for call in state["calls"])
        assert state["pulls_params"][0]["head"] == SYNC_HEAD_FILTER

    def test_no_drift_is_noop(self, monkeypatch):
        fc = self._client(drift=False)
        self._wire(monkeypatch, fc)
        assert rc.sync_yaml_base(fc) is False

    def test_pr_creation_failure_raises(self, monkeypatch):
        fc = self._client()
        self._wire(monkeypatch, fc, pr_result="fail")
        with pytest.raises(RuntimeError):
            rc.sync_yaml_base(fc)

    def test_commit_failure_raises(self, monkeypatch):
        fc = self._client()
        self._wire(monkeypatch, fc)
        monkeypatch.setattr(rc, "git_data_commit", lambda c, b, p, t, **kw: False)
        with pytest.raises(RuntimeError):
            rc.sync_yaml_base(fc)

    def test_main_reports_failure_as_exit_1(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "t")
        monkeypatch.setenv("GITHUB_REPOSITORY", "ubuntu/ubuntu-project-docs")
        fc = self._client()
        self._wire(monkeypatch, fc, pr_result="fail")
        monkeypatch.setattr(rc, "make_client", lambda **kw: fc)
        assert rc.main(["sync-yaml", "--base"]) == 1


# --- Final review round (F1-F14, C1, C2) -----------------------------------

# Shape of GET /repos/{repo}/codeowners/errors (trimmed from the live API).
SAMPLE_CO_ERRORS = [
    {
        "kind": "Unknown owner",
        "line": 2,
        "column": 12,
        "source": "SRU/ @good @Bad\n",
        "suggestion": "make sure @Bad exists and has write access to the repository",
        "message": "Unknown owner on line 2: make sure @Bad exists and has "
        "write access to the repository",
        "path": ".github/CODEOWNERS",
    }
]


def _approved_fake():
    fc = FakeClient()
    fc.base_codeowners = "MIR/ @setharnold @joalif\n"
    fc.pr_files[7] = [{"filename": "MIR/a.md"}]
    fc.pr_reviews[7] = [{"user": {"login": "setharnold"}, "state": "APPROVED"}]
    fc.pr_requested[7] = ["joalif"]
    return fc


class TestUnknownOwners:
    """F1: owners GitHub flags as unknown never count as approvers."""

    CO = "* @ta\nSRU/ @good @Bad\n"

    def test_errors_map_to_line_and_owner(self):
        assert rc.unknown_owners_by_line(SAMPLE_CO_ERRORS) == {2: {"@bad"}}

    def test_other_kinds_and_malformed_entries_ignored(self):
        errs = [
            {"kind": "Invalid pattern", "line": 1, "suggestion": "fix it"},
            {"kind": "Unknown owner"},
            {"kind": "Unknown owner", "line": 3, "suggestion": "no owner here"},
        ]
        assert rc.unknown_owners_by_line(errs) == {}
        assert rc.unknown_owners_by_line(None) == {}

    def test_parse_moves_unknown_owner_out_of_members(self):
        sets = rc.parse_codeowners(self.CO, unknown={2: {"@bad"}})
        assert sets[1].members == ["good"]
        assert sets[1].invalid == ["@Bad"]
        assert sets[0].invalid == []

    def test_unknown_email_owner_is_invalid(self):
        sets = rc.parse_codeowners(
            "X/ docs@example.com @a\n", unknown={1: {"docs@example.com"}}
        )
        assert sets[0].invalid == ["docs@example.com"]
        assert sets[0].unresolvable == []

    def test_unknown_owner_approval_neither_satisfies_nor_culls(self):
        sets = rc.parse_codeowners(self.CO, unknown={2: {"@bad"}})
        cov = rc.compute_coverage(
            ["SRU/x.md"], sets, [{"user": {"login": "bad"}, "state": "APPROVED"}]
        )
        assert cov.satisfied == []
        assert [s.pattern for s in cov.pending] == ["SRU/"]
        assert rc.compute_cull(["good"], cov) == []

    def test_run_coverage_consults_codeowners_errors(self):
        fc = FakeClient()
        fc.base_codeowners = self.CO
        fc.codeowners_errors = SAMPLE_CO_ERRORS
        fc.pr_files[7] = [{"filename": "SRU/x.md"}]
        fc.pr_reviews[7] = [{"user": {"login": "bad"}, "state": "APPROVED"}]
        fc.pr_requested[7] = ["good"]
        rc.run_coverage(fc, 7)
        body = fc.comments[7][1]
        assert fc.removed == []
        assert "1 of 1" in body and "approved by" not in body
        assert "@Bad" in body and "write access" in body


class _BadReadResponse(_FakeResponse):
    def __init__(self, exc):
        self._exc = exc

    def read(self):
        raise self._exc


class _RawResponse(_FakeResponse):
    def __init__(self, raw):
        self._payload = raw


class TestTransportErrors:
    """F2, F7, C2: transport failures and rate-limit backoff."""

    @staticmethod
    def _seq(monkeypatch, responses):
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))

        def fake(*a, **k):
            r = responses.pop(0)
            if isinstance(r, BaseException):
                raise r
            return r

        monkeypatch.setattr(urllib.request, "urlopen", fake)
        return sleeps

    def test_read_timeout_on_get_is_retried(self, monkeypatch):
        sleeps = self._seq(
            monkeypatch, [_BadReadResponse(TimeoutError("t")), _FakeResponse({"ok": 1})]
        )
        assert rc.GitHubClient("t", "o/r").get("/x") == {"ok": 1}
        assert len(sleeps) == 1

    def test_incomplete_read_on_post_raises_api_error(self, monkeypatch):
        import http.client

        sleeps = self._seq(
            monkeypatch, [_BadReadResponse(http.client.IncompleteRead(b""))]
        )
        with pytest.raises(rc.ApiError) as ei:
            rc.GitHubClient("t", "o/r").post("/x", body={})
        assert ei.value.status == 0 and sleeps == []

    def test_undecodable_body_on_post_raises_api_error(self, monkeypatch):
        self._seq(monkeypatch, [_RawResponse(b"<html>oops</html>")])
        with pytest.raises(rc.ApiError):
            rc.GitHubClient("t", "o/r").post("/x", body={})

    def test_403_secondary_rate_limit_message_backs_off(self, monkeypatch):
        sleeps = self._seq(
            monkeypatch,
            [
                _http_error(
                    403,
                    body=b'{"message":"You have exceeded a secondary rate limit."}',
                ),
                _FakeResponse({"ok": 1}),
            ],
        )
        assert rc.GitHubClient("t", "o/r").get("/x") == {"ok": 1}
        assert sleeps == [60.0]

    def test_headerless_429_waits_at_least_a_minute(self, monkeypatch):
        sleeps = self._seq(monkeypatch, [_http_error(429), _FakeResponse({"ok": 1})])
        assert rc.GitHubClient("t", "o/r").get("/x") == {"ok": 1}
        assert sleeps == [60.0]

    def test_plain_403_permission_error_still_raises(self, monkeypatch):
        self._seq(
            monkeypatch,
            [_http_error(403, body=b'{"message":"Resource not accessible"}')],
        )
        with pytest.raises(rc.ApiError):
            rc.GitHubClient("t", "o/r").get("/x")


class TestQueueBookkeeping:
    """F2 (lost DELETE response), F9 (DELETE response parsing), stale state."""

    def test_removal_with_lost_response_is_confirmed_from_queue(self):
        fc = _approved_fake()

        def lost(n, logins):
            FakeClient.remove_requested_reviewers(fc, n, logins)
            raise rc.ApiError(0, "read timed out")

        fc.remove_requested_reviewers = lost
        rc.run_coverage(fc, 7)  # must not raise: the queue confirms removal
        assert rc.parse_culled_state(fc.comments[7][1]) == ["joalif"]

    def test_delete_response_still_listing_reviewer_not_recorded(self):
        fc = _approved_fake()
        fc.remove_requested_reviewers = lambda n, logins: {
            "requested_reviewers": [{"login": "joalif"}]
        }
        rc.run_coverage(fc, 7)
        assert rc.parse_culled_state(fc.comments[7][1]) == []

    def test_culled_reviewer_back_in_queue_leaves_state(self):
        # Someone re-requested a culled reviewer: stop tracking them.
        fc = TestRunCoverage._culled_fc(["joalif"])
        fc.pr_requested[7] = ["joalif"]
        rc.run_coverage(fc, 7)
        assert rc.parse_culled_state(fc.comments[7][1]) == []


class _RefClient:
    repo = "o/r"

    def __init__(self, ref_name=None, head="headsha", patch_exc=None):
        self.calls = []
        self.ref_name = ref_name
        self.head = head
        self.patch_exc = patch_exc

    def get(self, path, **kw):
        self.calls.append(("GET", path))
        if "/git/ref/heads/" in path:
            raw = path.split("/git/ref/heads/", 1)[1]
            name = self.ref_name or "refs/heads/" + urllib.parse.unquote(raw)
            return {"ref": name, "object": {"sha": self.head}}
        if path.endswith("/git/commits/" + self.head):
            return {"tree": {"sha": "tree"}}
        return {}

    def post(self, path, **kw):
        self.calls.append(("POST", path))
        return {"sha": "new"}

    def patch(self, path, **kw):
        self.calls.append(("PATCH", path))
        if self.patch_exc:
            raise self.patch_exc
        return {"object": {"sha": "new"}}


class TestGitDataCommitHardening:
    """F3 (ref path encoding), F5 (expected parent), C1 (error contract)."""

    def test_branch_name_is_percent_encoded(self):
        c = _RefClient()
        assert rc.git_data_commit(c, "main#x", ".github/x.yaml", "d") is True
        assert ("GET", "/repos/o/r/git/ref/heads/main%23x") in c.calls
        assert ("PATCH", "/repos/o/r/git/refs/heads/main%23x") in c.calls
        c2 = _RefClient()
        rc.git_data_commit(c2, "feat%2Fx", ".github/x.yaml", "d")
        assert ("GET", "/repos/o/r/git/ref/heads/feat%252Fx") in c2.calls

    def test_slash_branches_keep_path_segments(self):
        c = _RefClient()
        rc.git_data_commit(c, "review-coverage-bot/sync", ".github/x.yaml", "d")
        assert ("GET", "/repos/o/r/git/ref/heads/review-coverage-bot/sync") in c.calls

    def test_mismatched_ref_name_refuses_to_write(self):
        c = _RefClient(ref_name="refs/heads/main")
        assert rc.git_data_commit(c, "feat", ".github/x.yaml", "d") is False
        assert not any(call[0] in ("POST", "PATCH") for call in c.calls)

    def test_api_error_returns_false(self):
        c = _RefClient(patch_exc=rc.ApiError(422, "not a fast forward"))
        assert rc.git_data_commit(c, "feat", ".github/x.yaml", "d") is False

    def test_moved_branch_raises_ref_moved(self):
        c = _RefClient(head="newer")
        with pytest.raises(rc.RefMoved):
            rc.git_data_commit(c, "feat", ".github/x.yaml", "d", expected_sha="headsha")
        assert not any(call[0] == "POST" for call in c.calls)


class TestSyncForPrHardening:
    """F5 (read at head sha), F6 (stale fork suggestion cleanup)."""

    def _fc(self, monkeypatch, head_codeowners="MIR/ @m\nSRU/ @s\n", head_yaml=""):
        fc = FakeSyncClient()
        fc.pr_files[7] = [{"filename": ".github/CODEOWNERS"}]
        seen = {}

        def ref_co(repo, ref):
            seen["ref"] = ref
            return head_codeowners

        monkeypatch.setattr(fc, "get_ref_codeowners", ref_co, raising=False)
        monkeypatch.setattr(fc, "get_head_yaml", lambda n: head_yaml, raising=False)
        return fc, seen

    def test_reads_codeowners_at_head_sha_and_pins_parent(self, monkeypatch):
        fc, seen = self._fc(monkeypatch)
        got = {}

        def commit(c, b, p, t, **kw):
            got.update(kw)
            return True

        monkeypatch.setattr(rc, "git_data_commit", commit)
        assert rc.sync_yaml_for_pr(fc, 7) == "committed"
        assert seen["ref"] == "abc"
        assert got["expected_sha"] == "abc"

    def test_moved_branch_is_noop(self, monkeypatch):
        fc, _ = self._fc(monkeypatch)

        def moved(c, b, p, t, **kw):
            raise rc.RefMoved("feat moved")

        monkeypatch.setattr(rc, "git_data_commit", moved)
        assert rc.sync_yaml_for_pr(fc, 7) == "noop"

    def test_noop_removes_stale_fork_suggestion(self, monkeypatch):
        co = "MIR/ @m\n"
        fc, _ = self._fc(
            monkeypatch,
            head_codeowners=co,
            head_yaml=rc.regenerate_yaml([], rc.parse_codeowners(co))[0],
        )
        fc.post_comment(7, rc.YAML_SYNC_MARKER + "\nold suggestion")
        assert rc.sync_yaml_for_pr(fc, 7) == "noop"
        assert 7 not in fc.comments

    def test_codeowners_no_longer_changed_removes_suggestion(self):
        fc = FakeSyncClient()
        fc.pr_files[7] = [{"filename": "docs/x.md"}]
        fc.post_comment(7, rc.YAML_SYNC_MARKER + "\nold suggestion")
        assert rc.sync_yaml_for_pr(fc, 7) == "noop"
        assert 7 not in fc.comments

    def test_noop_leaves_coverage_comment_alone(self):
        fc = FakeSyncClient()
        fc.pr_files[7] = [{"filename": "docs/x.md"}]
        fc.post_comment(7, rc.STICKY_MARKER + "\ncoverage")
        assert rc.sync_yaml_for_pr(fc, 7) == "noop"
        assert 7 in fc.comments

    def test_dry_run_noop_deletes_nothing(self):
        fc = FakeSyncClient()
        fc.pr_files[7] = [{"filename": "docs/x.md"}]
        fc.post_comment(7, rc.YAML_SYNC_MARKER + "\nold suggestion")
        rc.sync_yaml_for_pr(fc, 7, dry_run=True)
        assert 7 in fc.comments

    def test_real_client_reads_head_yaml_at_sha(self, monkeypatch):
        c = rc.GitHubClient("t", "o/r")
        monkeypatch.setattr(
            c,
            "get_pr",
            lambda n: {
                "head": {"sha": "s1", "ref": "feat", "repo": {"full_name": "f/r"}}
            },
        )
        seen = {}

        def contents(repo, path, ref):
            seen.update(repo=repo, ref=ref)
            return "x"

        monkeypatch.setattr(c, "_contents", contents)
        assert c.get_head_yaml(7) == "x"
        assert seen == {"repo": "f/r", "ref": "s1"}


class TestPatternEdgeCases:
    def test_bare_globstar_matches_everything(self):
        # F11: gitignore `**` / `/**` match everything, recursively.
        for pat in ("**", "/**"):
            p = rc.pattern_to_regex(pat)
            assert p.match("a.md") and p.match("a/b/c.md")


class TestApiEconomy:
    """F13: no redundant calls."""

    def test_default_branch_cached(self, monkeypatch):
        c = rc.GitHubClient("t", "o/r")
        calls = []
        monkeypatch.setattr(
            c,
            "get",
            lambda path, **kw: calls.append(path) or {"default_branch": "main"},
        )
        assert c._default_branch() == "main"
        assert c._default_branch() == "main"
        assert len(calls) == 1

    def test_upsert_reuses_supplied_comment(self):
        fc = FakeClient()
        fc.post_comment(7, f"{rc.STICKY_MARKER}\nold")
        existing = fc.get_sticky_comment(7)

        def refetch(*a, **k):
            raise AssertionError("sticky comment listed twice")

        fc.get_sticky_comment = refetch
        assert rc.upsert_comment(fc, 7, f"{rc.STICKY_MARKER}\nnew", existing=existing)
        assert fc.comments[7][1].endswith("new")

    def test_upsert_existing_none_posts(self):
        fc = FakeClient()
        fc.get_sticky_comment = lambda *a, **k: pytest.fail("listed")
        assert rc.upsert_comment(fc, 7, f"{rc.STICKY_MARKER}\nx", existing=None)
        assert 7 in fc.comments

    def test_run_coverage_lists_comments_once(self):
        fc = _approved_fake()
        calls = []
        orig = fc.get_sticky_comment

        def counting(*a, **k):
            calls.append(1)
            return orig(*a, **k)

        fc.get_sticky_comment = counting
        rc.run_coverage(fc, 7)
        assert len(calls) == 1


# --- Read-only dry-run, CODEOWNERS all-groups rule, commit status ----------


class TestReadOnlyClient:
    def test_writes_are_blocked_before_any_request(self, monkeypatch):
        def never(*a, **k):
            raise AssertionError("urlopen must not be called")

        monkeypatch.setattr(urllib.request, "urlopen", never)
        c = rc.GitHubClient("t", "o/r", read_only=True)
        for call in (
            lambda: c.post("/x", body={}),
            lambda: c.patch("/x", body={}),
            lambda: c.delete("/x"),
        ):
            with pytest.raises(rc.ReadOnlyError):
                call()

    def test_reads_still_work(self, monkeypatch):
        monkeypatch.setattr(
            urllib.request, "urlopen", lambda *a, **k: _FakeResponse({"ok": 1})
        )
        assert rc.GitHubClient("t", "o/r", read_only=True).get("/x") == {"ok": 1}

    def test_duplicate_cleanup_skipped_when_read_only(self):
        class C:
            repo = "o/r"
            read_only = True

            def __init__(self):
                self.deleted = []

            def get_all_pages(self, path, params=None):
                return [
                    {
                        "id": i,
                        "user": {"login": "github-actions[bot]"},
                        "body": rc.STICKY_MARKER + f"\n{i}",
                    }
                    for i in (1, 2)
                ]

            def delete(self, path, **kw):
                self.deleted.append(path)

        c = C()
        assert rc.GitHubClient.get_sticky_comment(c, 7)[0] == 2
        assert c.deleted == []

    def test_main_dry_run_builds_read_only_client(self, monkeypatch):
        seen = []

        def mk(read_only=False):
            seen.append(read_only)
            return FakeClient()

        monkeypatch.setattr(rc, "make_client", mk)
        monkeypatch.setattr(rc, "run_coverage", lambda c, n, dry_run=False: None)
        rc.main(["--dry-run", "coverage", "--pr", "7"])
        rc.main(["coverage", "--pr", "7"])
        assert seen == [True, False]


CO_RULE = (
    "* @ta\nMIR/\nMIR/ @m1 @m2\nSRU/ @s\ngone/ @g\ngone/\n/.github/CODEOWNERS @ta @m1\n"
)


def _approve(*logins):
    return [{"user": {"login": u}, "state": "APPROVED"} for u in logins]


class TestAllGroupsRule:
    def test_all_owned_groups_last_line_wins(self):
        groups = rc.all_owned_groups(rc.parse_codeowners(CO_RULE))
        assert [g.pattern for g in groups] == [
            "*",
            "MIR/",
            "SRU/",
            "/.github/CODEOWNERS",
        ]
        assert groups[1].members == ["m1", "m2"]

    def test_codeowners_change_requires_every_group(self):
        sets = rc.parse_codeowners(CO_RULE)
        cov = rc.compute_coverage(
            [".github/CODEOWNERS"],
            sets,
            _approve("ta"),
            extra=rc.all_owned_groups(sets),
        )
        assert [s.pattern for s in cov.satisfied] == ["/.github/CODEOWNERS", "*"]
        assert [s.pattern for s in cov.pending] == ["MIR/", "SRU/"]

    def test_one_approver_covers_several_groups(self):
        sets = rc.parse_codeowners(CO_RULE)
        cov = rc.compute_coverage(
            [".github/CODEOWNERS"],
            sets,
            _approve("m1", "s"),
            extra=rc.all_owned_groups(sets),
        )
        assert [s.pattern for s in cov.pending] == ["*"]

    def test_author_sole_owner_group_cannot_block(self):
        # G3: SRU/'s only valid owner is the author, so nobody can approve it.
        sets = rc.parse_codeowners(CO_RULE)
        cov = rc.compute_coverage(
            [".github/CODEOWNERS"],
            sets,
            _approve("ta", "m1", "s"),
            author="s",
            extra=rc.all_owned_groups(sets),
        )
        assert cov.pending == []
        assert [s.pattern for s in cov.unapprovable] == ["SRU/"]

    def _fc(self, files, reviews=()):
        fc = FakeClient()
        fc.base_codeowners = CO_RULE
        fc.pr_files[7] = [{"filename": f} for f in files]
        fc.pr_reviews[7] = list(reviews)
        return fc

    def test_run_coverage_applies_rule_and_links_codeowners(self):
        fc = self._fc([".github/CODEOWNERS"], _approve("ta"))
        rc.run_coverage(fc, 7)
        body = fc.comments[7][1]
        assert (
            "This PR changes `.github/CODEOWNERS`: every owner-group must approve."
            in body
        )
        assert "2 of 4 section(s) still pending" in body
        mir = next(l for l in body.splitlines() if l.startswith("| MIR/ |"))
        assert "[`.github/CODEOWNERS`](" in mir

    def test_other_prs_unaffected(self):
        fc = self._fc(["MIR/a.md"], _approve("m1"))
        rc.run_coverage(fc, 7)
        body = fc.comments[7][1]
        assert "every owner-group" not in body
        assert "All sections approved (0 of 1 pending)" in body


class TestCommitStatus:
    def test_failure_while_pending(self):
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @a\n"
        fc.pr_files[7] = [{"filename": "MIR/x.md"}]
        rc.run_coverage(fc, 7)
        assert fc.statuses == [("abc", "failure", "1 of 1 section(s) pending approval")]

    def test_success_when_all_approved(self):
        fc = _approved_fake()
        rc.run_coverage(fc, 7)
        assert fc.statuses == [("abc", "success", "All 1 section(s) approved")]

    def test_status_set_before_collected_errors_raise(self):
        fc = _approved_fake()

        def fail(n, logins):
            raise rc.ApiError(422, "boom")

        fc.remove_requested_reviewers = fail
        with pytest.raises(RuntimeError):
            rc.run_coverage(fc, 7)
        assert fc.statuses and fc.statuses[-1][1] == "success"

    def test_no_changed_files_is_success(self):
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @a\n"
        rc.run_coverage(fc, 7)
        assert fc.statuses == [("abc", "success", "No changed files")]

    def test_dry_run_sets_no_status(self, capsys):
        fc = FakeClient()
        fc.base_codeowners = "MIR/ @a\n"
        fc.pr_files[7] = [{"filename": "MIR/x.md"}]
        rc.run_coverage(fc, 7, dry_run=True)
        assert fc.statuses == []
        assert "would set status failure" in capsys.readouterr().out

    def test_real_client_status_payload(self, monkeypatch):
        c = rc.GitHubClient("t", "o/r")
        seen = {}

        def post(path, **kw):
            seen.update(path=path, body=kw.get("body"))
            return {}

        monkeypatch.setattr(c, "post", post)
        c.set_status("abc", "failure", "1 of 2", "https://x/pull/7")
        assert seen["path"] == "/repos/o/r/statuses/abc"
        assert seen["body"] == {
            "state": "failure",
            "context": "review-coverage",
            "description": "1 of 2",
            "target_url": "https://x/pull/7",
        }


# --- Review round 4 (G1-G11, H1) ---------------------------------------------


class TestCodeownersLocations:
    """G1/H1: all GitHub CODEOWNERS locations, including renames."""

    def _fc(self, files):
        fc = FakeClient()
        fc.base_codeowners = CO_RULE
        fc.pr_files[7] = files
        fc.pr_reviews[7] = _approve("ta")
        return fc

    def test_rename_away_from_github_dir_triggers_rule(self):
        fc = self._fc(
            [
                {
                    "filename": "CODEOWNERS",
                    "previous_filename": ".github/CODEOWNERS",
                    "status": "renamed",
                }
            ]
        )
        rc.run_coverage(fc, 7)
        body = fc.comments[7][1]
        assert "This PR changes `CODEOWNERS`: every owner-group must approve." in body
        assert fc.statuses[-1][1] == "failure"

    def test_rename_into_github_dir_triggers_rule(self):
        fc = self._fc(
            [
                {
                    "filename": ".github/CODEOWNERS",
                    "previous_filename": "CODEOWNERS",
                    "status": "renamed",
                }
            ]
        )
        rc.run_coverage(fc, 7)
        assert "every owner-group must approve" in fc.comments[7][1]

    def test_root_and_docs_locations_trigger_rule(self):
        for loc in ("CODEOWNERS", "docs/CODEOWNERS"):
            fc = self._fc([{"filename": loc}])
            rc.run_coverage(fc, 7)
            assert "every owner-group must approve" in fc.comments[7][1], loc

    def test_base_codeowners_falls_back_in_github_order(self, monkeypatch):
        c = rc.GitHubClient("t", "o/r")
        c._default_branch_name = "main"
        seen = []

        def contents(repo, path, ref):
            seen.append(path)
            return "* @a\n" if path == "CODEOWNERS" else None

        monkeypatch.setattr(c, "_contents", contents)
        assert c.get_base_codeowners() == "* @a\n"
        assert seen == [".github/CODEOWNERS", "CODEOWNERS"]


class TestStatusEdgeCases:
    """G7, G8, G6, G10."""

    def test_unreadable_base_codeowners_sets_failure(self):
        fc = FakeClient()
        fc.base_codeowners = None
        fc.pr_files[7] = [{"filename": "a.md"}]
        rc.run_coverage(fc, 7)
        assert fc.statuses == [("abc", "failure", "cannot read base CODEOWNERS")]

    def test_truncated_file_list_sets_failure(self):
        fc = _approved_fake()
        fc._pr = dict(fc._pr, changed_files=3001)
        rc.run_coverage(fc, 7)
        assert fc.statuses[-1][1] == "failure"
        assert fc.statuses[-1][2].startswith("too many files to evaluate")
        assert "3001" in fc.comments[7][1]

    def test_complete_file_list_unaffected(self):
        fc = _approved_fake()
        fc._pr = dict(fc._pr, changed_files=1)
        rc.run_coverage(fc, 7)
        assert fc.statuses[-1][1] == "success"

    def test_status_post_is_retried(self, monkeypatch):
        sleeps = TestTransportErrors._seq(
            monkeypatch, [_http_error(502), _FakeResponse({})]
        )
        rc.GitHubClient("t", "o/r").set_status("abc", "success", "d", "u")
        assert len(sleeps) == 1

    def test_failed_status_write_is_reported(self):
        fc = _approved_fake()

        def boom(*a):
            raise rc.ApiError(502, "bad gateway")

        fc.set_status = boom
        with pytest.raises(RuntimeError, match="status"):
            rc.run_coverage(fc, 7)
        assert 7 in fc.comments

    def test_status_links_to_the_pr(self, monkeypatch):
        monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
        fc = _approved_fake()
        rc.run_coverage(fc, 7)
        assert fc.status_urls == ["https://github.com/o/r/pull/7"]


class TestCannotBlock:
    """G2/G3: groups nobody can approve are reported but never block."""

    def test_unknown_only_group_cannot_block(self):
        sets = rc.parse_codeowners("X/ @Bad\n", unknown={1: {"@bad"}})
        cov = rc.compute_coverage(["X/a.md"], sets, [])
        assert cov.pending == []
        assert [s.pattern for s in cov.unapprovable] == ["X/"]
        assert rc.coverage_status(cov)[0] == "success"

    def test_render_marks_and_explains(self):
        sets = rc.parse_codeowners("MIR/ @a\nX/ @org/team\n")
        cov = rc.compute_coverage(["MIR/a.md", "X/b.md"], sets, _approve("a"))
        body = rc.render_comment(cov, {}, 7, {}, "https://github.com/o/r", cull=[])
        row = next(line for line in body.splitlines() if line.startswith("| X/ |"))
        assert "△ cannot be approved (no valid individual owner)" in row
        assert "cannot block" in body
        assert "✓ No approvable section pending" in body
        assert rc.coverage_status(cov) == (
            "success",
            "All approvable sections approved (1 cannot be approved)",
        )

    def test_author_only_reason(self):
        sets = rc.parse_codeowners("X/ @s\n")
        cov = rc.compute_coverage(["X/a.md"], sets, [], author="s")
        body = rc.render_comment(cov, {}, 7, {}, "https://github.com/o/r", cull=[])
        assert "cannot be approved (only valid owner is the PR author)" in body

    def test_pending_still_blocks_alongside_unapprovable(self):
        sets = rc.parse_codeowners("MIR/ @a\nX/ @org/team\n")
        cov = rc.compute_coverage(["MIR/a.md", "X/b.md"], sets, [])
        assert rc.coverage_status(cov) == (
            "failure",
            "1 of 2 section(s) pending approval",
        )


class TestDispatchRescan:
    """G5: the rescan dispatches per-PR runs (serialized per PR)."""

    def test_dispatches_one_run_per_open_pr(self):
        fc = FakeClient()
        fc.open_pr_numbers = [7, 9]
        assert rc.dispatch_coverage_runs(fc) == 0
        assert fc.dispatches == [
            ("review-coverage.yml", "main", {"pr": "7"}),
            ("review-coverage.yml", "main", {"pr": "9"}),
        ]

    def test_dry_run_dispatches_nothing(self, capsys):
        fc = FakeClient()
        fc.open_pr_numbers = [7]
        assert rc.dispatch_coverage_runs(fc, dry_run=True) == 0
        assert fc.dispatches == []
        assert "would dispatch coverage for PR #7" in capsys.readouterr().out

    def test_failed_dispatch_isolated(self):
        fc = FakeClient()
        fc.open_pr_numbers = [7, 9]
        calls = []

        def disp(workflow, ref, inputs):
            calls.append(inputs["pr"])
            if inputs["pr"] == "7":
                raise rc.ApiError(422, "nope")

        fc.dispatch_workflow = disp
        assert rc.dispatch_coverage_runs(fc) == 1
        assert calls == ["7", "9"]

    def test_main_wires_dispatch_flag(self, monkeypatch):
        monkeypatch.setattr(rc, "make_client", lambda **kw: FakeClient())
        seen = []
        monkeypatch.setattr(
            rc,
            "dispatch_coverage_runs",
            lambda c, dry_run=False: seen.append(dry_run) or 0,
        )
        assert rc.main(["coverage", "--all-open", "--dispatch"]) == 0
        assert rc.main(["--dry-run", "coverage", "--all-open", "--dispatch"]) == 0
        assert seen == [False, True]
        assert rc.main(["coverage", "--pr", "7", "--dispatch"]) == 2

    def test_real_client_dispatch_payload(self, monkeypatch):
        c = rc.GitHubClient("t", "o/r")
        seen = {}
        monkeypatch.setattr(
            c, "post", lambda path, **kw: seen.update(path=path, body=kw.get("body"))
        )
        c.dispatch_workflow("review-coverage.yml", "main", {"pr": "7"})
        assert seen == {
            "path": "/repos/o/r/actions/workflows/review-coverage.yml/dispatches",
            "body": {"ref": "main", "inputs": {"pr": "7"}},
        }
