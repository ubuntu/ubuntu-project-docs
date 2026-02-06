## Setting up the Repository Locally

This only needs to be done once when setting up a machine for Rust toolchain maintenance for the first time.

### Project directory structure

Since the Debian build tools generate files in the parent directory of your package source directory, it's recommended to keep things organized by placing the cloned repository inside of a fresh directory of its own.

Clone the repository inside an existing `rustc` directory so your file structure looks like the following:

```none
rustc
├── rustc
│   ├── [...]
│   ├── Cargo.lock
│   ├── Cargo.toml
│   ├── debian
│   └── [...]
└── rustc-<...>.orig.tar.xz
```

Naturally, your higher-level `rustc` directory won't have any {term}`.orig.tar.xz <orig tarball>` files yet, but they will be stored there once you start working on the package.

### Cloning the Git repository

The main repository for _all_ versioned Rust toolchain packages is the Foundations [Launchpad Git repository](https://git.launchpad.net/~canonical-foundations/ubuntu/+source/rustc). A branch exists for every single upstream release and {term}`backport` and serves as a central place to store _all_ Rust toolchain code, regardless of which versioned package a particular branch belongs to.

Clone the Foundations Git repository within your existing parent directory:

```none
$ git clone git+ssh://<lpuser>@git.launchpad.net/~canonical-foundations/ubuntu/+source/rustc
```

Then, create your own personal Git repository on Launchpad:

```none
$ git remote add <lpuser> git+ssh://<lpuser>@git.launchpad.net/~<lpuser>/ubuntu/+source/rustc
```

Generally, it's recommended to use your personal Git repository as a remote backup throughout the process — the update procedure involves multiple rebases, so it's best to wait pushing to the Foundations repository until you're done.

---
