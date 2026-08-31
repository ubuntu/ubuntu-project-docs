# Auto-MIR

Auto-MIR assists both Ubuntu Main Inclusion Review (MIR) reporters and
reviewers. Reviewer mode reads an existing Launchpad MIR bug. Reporter mode
starts from an Ubuntu source package and guides the reporter through preparing
an evidence-backed request in a terminal.

Auto-MIR does not post to Launchpad and does not make the final ACK or NACK
decision. A reviewer must verify, edit, and complete every generated draft.

## Quick start

Auto-MIR supports Ubuntu 24.04 LTS and newer. Install its Python dependencies
from the Ubuntu archive:

```text
sudo apt install python3-launchpadlib python3-yaml python3-pythonjsonlogger python3-tenacity
```

Install and initialize LXD if it is not already available:

```text
sudo snap install lxd
sudo lxd init --auto
```

A full review uses OpenRouter by default. Read an API key without putting it in
shell history, then export it to the current shell:

```text
read -rsp "OpenRouter API key: " OPENAI_API_KEY
echo
export OPENAI_API_KEY
```

`OPENAI_API_KEY` is optional: if it is unset, auto-mir warns and proceeds with
a placeholder credential, which is enough for a local/unauthenticated
OpenAI-compatible endpoint (set via `OPENAI_API_BASE`). Set `OPENAI_API_KEY`
for OpenRouter or any other endpoint that actually checks the token.

From this directory, review an existing Launchpad MIR bug:

```text
./auto_mir.py review <bug number>
```

To prepare a reporter draft from a source package, use an interactive terminal:

```text
./auto_mir.py report <source package>
```

Reporter mode targets the development release (`devel`) when `--series` is not
specified. Pass an explicit codename only when preparing a request for another
series. Reviewer mode continues to infer the series from Launchpad bug tasks.

During the window right after a new Ubuntu release opens, `--series devel` (or
an unspecified `--series`) can be unreliable for a short period: `distro-info`
itself may not yet know about the new series, and daily `devel` LXD guest
images may not exist yet either, so a real build/verify pass is not possible
regardless of series-resolution correctness. In that window, pass the
previous (stable) release's codename explicitly with `--series` instead, and
switch back to `devel` once daily devel images become available.

Reporter mode collects evidence before asking long-form questions. Finish a
multiline answer with a line containing only `.`; enter `\.` for a literal dot.
Answers are not saved for resume if the process is interrupted. Use `--no-llm`
to disable optional model-backed enrichment; the current user-test catalog is
deterministic plus human input and does not require an API key.

The completion banner prints the artifact directory and the path to
`review-draft.txt`. Open that file, resolve its remaining TODOs, verify its
conclusions, and thereby complete it before posting as review to the Launchpad
bug.

## Requirements

- Ubuntu 24.04 LTS or newer with Python 3.12 or newer
- Access to a working LXD service and Ubuntu image remotes
- Network access to Launchpad, The Ubuntu archive and services
- An OpenRouter API key for a full review
- Enough resources for the default LXD VM: 4 CPUs, 8 GiB memory, and a 20 GiB
  root disk

The tool checks all required Python modules before doing work. If one or more
are missing, it reports the corresponding Ubuntu packages in one installation
command. `./auto_mir.py --help` remains available on an unprepared host.

The OpenAI-compatible endpoint defaults to `https://openrouter.ai/api/v1`, with
`z-ai/glm-4.7` and `z-ai/glm-5.2` as the small and large models. To use another
compatible service, set `OPENAI_API_BASE` and select compatible models with the
model options shown by `./auto_mir.py --help`.

## What happens during a run

Auto-MIR:

1. reads the reporter's MIR data from Launchpad;
2. creates and provisions a fresh LXD guest for the target Ubuntu series;
3. builds the package and collects archive, dependency, test, security, and
   upstream evidence;
4. evaluates deterministic and AI-assisted checks; and
5. renders artifacts for reviewer inspection.

Some external evidence is deliberately best-effort. An unavailable optional
source produces explicit unknown findings or reviewer TODOs rather than making
up an answer. The complete collected adapter data remains available
in `evidence.json`.

Component overview:

```
┌──────────────────────────┐
│ auto-mir.py              │ defines┌───────────────────────┐
│ orchestrates order and   ◄────────┼ catalog*.yaml files   │
│ dependencies             │        └───────────────────────┘
└────────────────┬─────────┘
┌────────────────▼────────────────────────────┐  ┌────────────────────────────────┐
│ evidence/                                   │  │ orchestration / intake         │
│ abstracts the sources of factual data       │  │ reports progress and handles   │
│ (builds, CVEs, packages, tests, ...).       │  │ bounded operator interaction.  │
└────────────────┬──▲─────────────────────────┘  └────────────────────────────────┘
┌────────────────▼──┴─────────────────────────┐  ┌────────────────────────────────┐
│ checks/                                     ┼──► prompts/                       │
│ Use Data to decide about MIR rules          │  │ guide LLM calls and handling   │
│ Where interpretation is needed call to LLM. ◄──┼ of answers.                    │
└────────────────┬────────────────────────────┘  └────────────────────────────────┘
┌────────────────▼────────────────────────────┐
│ render/                                     │
│ converts all insight to full report.json    │
│ and review-draft.txt for human finalization.│
└─────────────────────────────────────────────┘
```


## Output

A normal run writes these files beneath the reported output directory:

| File | Purpose |
| --- | --- |
| `review-draft.txt` | Reviewer-template-aligned draft to verify and edit before posting. |
| `reporter-draft.txt` | Reporter-template-aligned draft, ready to review and post. |
| `report.json` | Structured findings, confidence, evidence references, and LLM usage. |
| `evidence.json` | Collected adapter evidence for auditing and diagnosis. |
| `auto-mir.log` | JSON-formatted execution log. |
| `build_log.txt` | Build output, written when the package build fails and a log is available. |

Resolved API credentials stay on the host and are not persisted in the LXD
guest. Auto-MIR redacts registered credential values from console logs and all
files in the output directory, including exception and subprocess output. The
directory is therefore safe to share for diagnosis with respect to credentials.
It is not anonymous: it still contains public Launchpad content, package
evidence, versions, guest names, and diagnostic paths.

Redaction cannot repair logs produced by older versions. If an older log
contains a credential, revoke or rotate that credential before sharing the log.

An exit status of zero means the pipeline completed. It does not mean the
package is ready for an ACK, that every adapter succeeded, or that the draft has
no findings. Confirmed deterministic problems and lower-confidence items are
rendered differently so the reviewer can apply the appropriate judgment.

The same distinction applies to reporter mode: a successful run can produce an
honest not-ready draft containing TODOs, blockers, or warnings. Resolve and
verify those items before posting the request. Auto-MIR never creates or edits a
Launchpad bug.

Reporter mode covers all 12 sections through 53 stable logical items, including
conditional choice groups and all A-H/X non-automated-testing alternatives.
Deterministic evidence, human declarations, accepted AI suggestions, selected
options, readiness issues, and final consistency results remain distinguishable
in the structured report.

## Development documentation

The end-user workflow intentionally stays small. Maintainers and contributors
can use the following references for implementation details:

- [Design and runtime architecture](design.md)
- [Decision history and trade-offs](decisions.md)
- [Testing guide](testing.md)
- [Check and evidence catalog](CATALOG.md)
- [Check evaluation](checks/README.md)
- [Evidence adapters](evidence/README.md)
- [Rendering](render/README.md)
- [LLM prompts](prompts/README.md)

Auto-MIR is licensed under GPLv3 see the [license file](LICENSE).
