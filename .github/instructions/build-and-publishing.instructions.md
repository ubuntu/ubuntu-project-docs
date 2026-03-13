---
applyTo: "**"
---

# Build and publishing


## Commands

All commands run from the `docs/` directory. The first run auto-creates a Python venv at `docs/.sphinx/venv/`.

```bash
make run          # Build, watch, and serve locally at http://127.0.0.1:8000
make html         # Build only
make linkcheck    # Check all external links
make lint-md      # Check Markdown syntax (pymarkdownlnt)
make vale         # Full style guide check (Canonical rules, errors only)
make spelling     # Spelling check only
make woke         # Inclusive language check only
make pa11y        # Accessibility check (requires npm/Node)
make clean        # Full clean including venv
make clean-doc    # Clean built output only
```

Run a style check against a specific file or directory:

```bash
make vale TARGET=maintainers/some-file.md
make spelling TARGET=contributors/
```


## Architecture

- **Sphinx + MyST Markdown**: all content is `.md` using MyST extensions; `.rst` is also supported
- **`docs/conf.py`**: central Sphinx config — extensions, substitutions, intersphinx mappings, custom roles, linkcheck exceptions; update `stable_distro` here when a new Ubuntu release becomes stable
- **`docs/redirects.txt`**: old→new path mappings enforced by `sphinxext.rediraffe`; add an entry here whenever a page is moved or renamed
- **`docs/.sphinx/`**: tooling config (Vale, pa11y, pymarkdown, static assets) — not content
- **`docs/.custom_wordlist.txt`**: add project-specific terms here to suppress false Vale spelling errors
- **`docs/reuse/links.txt`**: RST link definitions appended to every page via `rst_epilog`; define shared URLs here and use the named references in content


## Intersphinx targets

Cross-references into external doc sets are available via these keys:

| Key | Doc set |
|---|---|
| `ubuntu-server` | Ubuntu Server documentation |
| `pkg-guide` | Canonical Ubuntu Packaging Guide |
| `starter-pack` | Canonical Starter Pack |
| `launchpad` | Launchpad documentation |


## Excluded content

- `maintainers/niche-package-maintenance/rustc/common` — excluded from build (`exclude_patterns` in `conf.py`)
- `SRU/**`, `tech-board/**`, `**/*.txt`, `**/*.html` — excluded from all Vale/style checks (`VALE_IGNORE` in Makefile)


## Publishing

Documentation is published automatically to [Read the Docs](https://documentation.ubuntu.com/project/) on every push to `main`. Configuration is in `.readthedocs.yaml` (Python 3.13, Ubuntu 24.04, PDF format). PR builds with no documentation changes are auto-cancelled.
