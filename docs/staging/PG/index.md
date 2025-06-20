# Packaging guide move

The content in this staging area (`staging/PG/`) is an initial dump of the Packaging guide (with many tweaks and fixes). It intentionally uses the directory structure (i.e info architecture) proposed in [PR #58](https://github.com/ubuntu/ubuntu-project-docs/pull/58/).


```{toctree}
:maxdepth: 1

contributors/index
how-ubuntu-is-made/index
```

```
├── contributors
│   ├── bug-fix
│   │   ├── build-packages
│   │   ├── download-new-upstream-version
│   │   ├── extract-packages
│   │   ├── fix-bug
│   │   ├── install-built-packages
│   │   ├── propose-changes
│   │   └── run-tests
│   ├── new-package
│   │   ├── create-new-package
│   │   └── upload-packages-to-ppa
│   ├── patching
│   │   ├── configure.bash
│   │   ├── make-changes-to-package
│   │   └── patch-management
│   └── setup
│       ├── get-package-source
│       ├── getting-set-up
│       └── use-schroots
└── how-ubuntu-is-made
    ├── concepts
    │   ├── architectures
    │   ├── archive
    │   ├── debian-dir-overview
    │   ├── debian-policy
    │   ├── filesystem-hierarchy-standard
    │   ├── launchpad
    │   ├── package-model
    │   ├── package-version-format
    │   ├── patches
    │   ├── patchfile-headers
    │   ├── releases
    │   └── upstream-and-downstream
    └── processes
        ├── backports
        ├── debian-merges-and-syncs
        ├── development-process
        ├── main-inclusion-review
        ├── merge-a-package
        ├── proposed-migrations
        ├── request-freeze-exception
        ├── sponsorship
        └── transitions
```
