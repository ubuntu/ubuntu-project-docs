(aa-how-to)=
# Archive Admin tasks

Archive Administration is done client side using the Launchpad API through
various tools. To
[get hold of these tools](https://code.launchpad.net/~ubuntu-archive/ubuntu-archive-tools/trunk):

```none
$ git clone lp:ubuntu-archive-tools
```

(aa-tasks)=
## Tasks and responsibilities

The main tasks the Archive Admin team is responsible for are:

* {ref}`aa-new-review`
* {ref}`aa-package-removal`
* {ref}`aa-package-overrides`

Less commonly, they are asked to do the following tasks:

* {ref}`aa-priority-mismatches`
* {ref}`aa-signing-bootloaders`
* {ref}`aa-phasing-sru-updates`
* {ref}`aa-i386-allowlist-updates`
* {ref}`aa-triage-contributions`

The following list of Archive-related services needs to be updated with details
of the charmed hosted services as they are migrated.

- {ref}`aa-archive-related-services` 


```{toctree}
:titlesonly:
:hidden:

AA/aa-new-review
AA/aa-package-removal
AA/aa-package-overrides
AA/aa-priority-mismatches
AA/aa-signing-bootloaders
AA/aa-phasing-sru-updates
AA/aa-i386
AA/aa-archive-related-services
AA/triage-aa-contributions.md
```
