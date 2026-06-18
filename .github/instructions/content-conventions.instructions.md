---
applyTo: "docs/**"
---

# Content conventions

> **Keep this file in sync with `docs/contributors/contribute-docs.md`** — whenever the contribution guide changes, update this file accordingly.


## Directory structure

All source files live under `docs/`. Content is organized by [Diátaxis](https://diataxis.fr/) type and audience:

| Directory | Purpose |
|---|---|
| `how-ubuntu-is-made/` | Concepts, governance, mission, process overviews (for all audiences) |
| `contributors/` | How-to guides for people contributing to Ubuntu |
| `maintainers/` | Guides for maintainers with elevated upload permissions |
| `who-makes-ubuntu/` | Roles, groups, membership information |
| `community/` | Community organization: teams, councils, governance, membership |
| `release-team/` | Release team procedures, freeze handling, release cycle docs |
| `MIR/` | Main Inclusion Review (MIR) process documentation |
| `staging/` | Work-in-progress / preview content (not linked from main nav) |
| `reuse/` | Shared content: `links.txt` (named URL references), substitutions |
| `images/` | Shared image assets |

Every section has an `index.md` that controls the toctree for that section.


## File naming

- Lowercase with hyphens: `contribute-docs.md`
- File name matches the article title (omit "how to" prefix): an article called *How to fix a bug* → `fix-a-bug.md`


## Headings and anchors

- Two blank lines before each heading
- Anchors use lowercase-with-hyphens matching the heading text:

  ```md
  (organization-principles)=
  ### Organization principles
  ```


## Markup format

MyST Markdown is preferred for all new content. reStructuredText is supported but use MyST unless you have a specific reason not to.

References:
- [MyST syntax reference](https://canonical-starter-pack.readthedocs-hosted.com/latest/reference/myst-syntax-reference/)
- [reStructuredText syntax reference](https://canonical-starter-pack.readthedocs-hosted.com/latest/reference/rst-syntax-reference/)


## Semantic roles

Use semantic roles instead of bare backtick formatting where applicable:

| Role | Use for |
|---|---|
| `{command}` | CLI commands |
| `{code}` | Inline source code snippets |
| `{file}` | File and directory names (including paths) |
| `{guilabel}` | GUI elements (buttons, labels, widgets) |
| `{kbd}` | Keyboard keys/shortcuts, e.g. `{kbd}\`Ctrl+C\`` |
| `{manpage}` | Ubuntu manual pages (auto-links to manpages.ubuntu.com) |
| `{pkg}` | Linux package names (custom role for this project) |
| `{term}` | Glossary terms (renders as a hover tooltip) |


## Special link roles

Use these instead of raw URLs:

| Role | Expands to |
|---|---|
| `` {manpage}`bash(1)` `` | manpages.ubuntu.com link for `bash(1)` |
| `` {lpbug}`123456` `` | bugs.launchpad.net link, renders as `LP: #123456` |
| `` {lpsrc}`bash` `` | launchpad.net/ubuntu/+source/bash |
| `` {matrix}`devel` `` | matrix.to link for `#devel:ubuntu.com` |

Named URL references in `docs/reuse/links.txt` are available on every page — use them instead of inline URLs where a reference already exists.


## Substitutions

These substitutions are defined in `conf.py` and available in all pages:

| Substitution | Value |
|---|---|
| `{{ stable_distro }}` | Current stable Ubuntu release codename |
| `{{ release_schedule }}` | URL to the current release schedule |


## Command-line examples and terminal output

**Command examples** — use a `none` code block (no syntax highlighting):
- `<angle_brackets>` for mandatory substitutions
- `[square_brackets]` for optional arguments
- `$` prompt for normal user, `#` for root
- Split long commands across lines with `\`

```none
$ command --option=<mandatory_value> [optional_parameter] && \
  another-command
```

**Terminal output** — use separate blocks for the invocation and its output; shorten output to only the relevant parts using `[...]`.

**Prompt + output together** — use the `{terminal}` directive:

````md
```{terminal}
:user: root
:host: ubuntu
:dir: /tmp

command --option

output here
```
````


## Code blocks

Use the appropriate language identifier for syntax highlighting. Use `none` to suppress highlighting.


## Soft-wrapped monospace blocks

For sample emails, comment messages, or other text that should not interpret markup:

````md
```{code}
:class: codeblock-wrap

Text here...
```
````


## Inline roles for prose

- `:woke-ignore:` — suppress an inclusive-language Vale warning for a specific term
- `:vale-ignore:` — suppress a Vale style warning for a specific passage
- `:center:` — center table cell content
- `:h2:` — style content for PDF generation
