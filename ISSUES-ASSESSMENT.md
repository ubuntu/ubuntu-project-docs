# Issues Assessment

## Summary

| Issue | Title | Labels | Verdict | Complexity |
|-------|-------|--------|---------|------------|
| #694 | Mermaid diagrams unreadable in dark mode | DMB | In-repo | Medium |
| #661 | SRU requirements should link to reference/requirements | SRU | In-repo | Low |
| #645 | Missing Futures Release update in list of releases | Release team | In-repo | Low |
| #634 | Convert Ubuntu governance model to Mermaid | TB, community | In-repo (PR #687 exists) | Medium |
| #641 | snapshots missing | — | Out-of-repo | — |
| #640 | Upload a PPA page needs help | — | Out-of-repo | — |
| #607 | Apps installed from Edge/Chrome icon issue | — | Out-of-repo | — |
| #592 | SRU standard-process clean up | SRU | Skipped (SRU label, requires investigation) | — |
| #587 | Expand SRU examples | SRU | Skipped (SRU label, requires investigation) | — |
| #543 | Refresh Snapd special case documentation | SRU, TB | Skipped (SRU+TB labels, requires Launchpad MP investigation) | — |
| #540 | Improvements to Apport content | — | Skipped (requires investigation for replacement URLs) | — |
| #536 | Build packages locally: address prior revision comments | — | Skipped (requires technical investigation of PR comments) | — |
| #521 | Flavours? (seed management) | Release team | Skipped (Release team label, requires investigation) | — |
| #520 | Platform vs ubuntu repositories? | Release team | Skipped (Release team label, requires investigation) | — |
| #516 | Request to add rsync page | community | Out-of-repo | — |
| #509 | SRU broken link (ubuntu-image) | SRU | Skipped (SRU label, replacement URL not provided) | — |
| #507 | SRU broken link (postgres) | SRU | Skipped (SRU label, replacement URL not provided) | — |
| #506 | SRU broken link (postfix) | SRU | Skipped (SRU label, replacement URL not provided) | — |
| #490 | Outdated information in Ubuntu Bug Control | — | Skipped (requires investigation for replacement contact) | — |
| #479 | Request to add Boot-Info page | documentation | Out-of-repo | — |

## In-repo issues to fix

### #694 — Mermaid diagrams unreadable in dark mode

- **Task**: Remove hard-coded colors from all Mermaid diagrams so they use default theme (adapts to light/dark mode)
- **Files** (12 total):
  - `docs/how-ubuntu-is-made/processes/lifecycle-of-a-change.txt`
  - `docs/how-ubuntu-is-made/processes/lifecycle-1-report-triage.txt`
  - `docs/how-ubuntu-is-made/processes/lifecycle-2-prepare-test.txt`
  - `docs/how-ubuntu-is-made/processes/lifecycle-3-propose-review.txt`
  - `docs/how-ubuntu-is-made/processes/lifecycle-4-upload-sponsor.txt`
  - `docs/how-ubuntu-is-made/processes/lifecycle-5-proposed-migration.txt`
  - `docs/who-makes-ubuntu/developers/diagrams/overall-path.txt`
  - `docs/who-makes-ubuntu/developers/diagrams/basics.txt`
  - `docs/who-makes-ubuntu/developers/diagrams/intermediate.txt`
  - `docs/who-makes-ubuntu/developers/diagrams/advanced.txt`
  - `docs/who-makes-ubuntu/developers/diagrams/expert.txt`
  - `docs/MIR/mir-process-states.md`
- **Resolution**: Remove all `fill:#`, `stroke:#`, `background:#`, `classDef`, and `style` lines from mermaid diagrams

### #661 — SRU requirements should link to reference/requirements

- **Task**: Add cross-reference from explanation requirements page to reference requirements page
- **Files**: `docs/SRU/explanation/requirements.rst`
- **Resolution**: Add a `.. seealso::` directive or note linking to `docs/SRU/reference/requirements.rst`

### #645 — Missing Futures Release update in list of releases

- **Task**: Add Ubuntu 26.04.1 LTS to Future releases table
- **Files**: `docs/release-team/list-of-releases.md`
- **Resolution**: Add row for Ubuntu 26.04.1 LTS (Resolute Raccoon) with TBD for unknown fields, May 2031 for End of Standard Support

### #634 — Convert Ubuntu governance model to Mermaid

- **Task**: Convert governance map PNG to Mermaid diagram (PR #687 exists as draft, needs fixing — uses hard-coded colors)
- **Files**: `docs/community/governance/index.md`
- **Resolution**: Update PR #687 to remove hard-coded colors from the Mermaid diagram
