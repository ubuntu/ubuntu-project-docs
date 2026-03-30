# Cargo-Auditable

[`cargo-auditable`](https://github.com/rust-secure-code/cargo-auditable) is a tool by the Rustsec Working Group that augments the Rust binary build process by embedding metadata showing the dependency tree into a the binary.
Specifically, it puts a JSON-encoded, Zlib-compressed payload into the `.dep-v0` header.

If you develop a Rust binary package for Ubuntu versions 26.04 and later and {manpage}`rustc(1)` versions 1.93 and later, you can easily opt-in to adding cargo-auditable metadata to your binaries.

```{admonition} Some caveats
`cargo-auditable` support is still **experimental**, which is why it is opt-in for now.
We hope to make it on-by-default in a later version of Ubuntu, but we would like to have the community test it first.
If you do not follow the steps below, at time of writing, nothing about your package will change.

Also, please note that this *only* works on Ubuntu 26.04 and later (that's Resolute Raccoon), and on `rustc-1.93` and later.

If you would like to know more technical details about `cargo-auditable`, see its Github repo above.
```

## Creating auditable binaries

To enable building with `cargo-auditable`, it takes two steps:

1. Export `UBUNTU_ENABLE_CARGO_AUDITABLE=1` in your `debian/rules` file.
2. Put a `Build-Depends` on `cargo-auditable` in your `debian/control` file.

Below is an example patch demonstrating these changes on {manpage}`rust-alacritty <alacritty(1)>`.
[The patch was made live in this commit.](https://git.launchpad.net/~petrakat/ubuntu/+source/rust-alacritty/commit/?h=petrakat/cargo-auditable&id=62b87bff4a7fb5e41bb2a6f770175c274b2f7918)

```diff
diff --git a/debian/control b/debian/control
index 118e3f9..f105861 100644
--- a/debian/control
+++ b/debian/control
@@ -6,7 +6,8 @@ Build-Depends: debhelper-compat (= 13),
  dh-sequence-bash-completion,
  fish-common,
  pkgconf,
- scdoc
+ scdoc,
+ cargo-auditable
 Build-Depends-Arch: cargo:native,
  rustc:native (>= 1.85.0),
  libstd-rust-dev,
diff --git a/debian/rules b/debian/rules
index 7460220..0ecb9df 100755
--- a/debian/rules
+++ b/debian/rules
@@ -1,4 +1,6 @@
 #!/usr/bin/make -f
+export UBUNTU_ENABLE_CARGO_AUDITABLE=1
+
 %:
        dh $@ --buildsystem cargo
```

## Reading auditable metadata

There are a number of tools that can read the metadata out of a binary.
The upstream publishers of `cargo-auditable` also publish the tool [`cargo-audit`](https://github.com/rustsec/rustsec/tree/main/cargo-audit#cargo-audit-bin-subcommand), the recommended way to read the metadata out of a binary.
It reads the dependency graph, and then checks it against a known database of vulnerabilities.

If you would like to just see the raw data, you can use the tool [`rust-audit-info`](https://github.com/rust-secure-code/cargo-auditable/blob/master/rust-audit-info/README.md).
It simply finds the metadata section in the binary, decompresses it, and dumps it to `stdout`.

You can install both tools with `cargo install`.

```{terminal}
:user: ubuntu
:host: resolute
:dir: ~

cargo audit bin /usr/bin/batcat
    Fetching advisory database from `https://github.com/RustSec/advisory-db.git`
      Loaded 1017 security advisories (from /root/.cargo/advisory-db)
    Updating crates.io index
       Found 'cargo auditable' data in /usr/bin/batcat (133 dependencies)
Crate:     adler
Version:   1.0.2
Warning:   unmaintained
Title:     adler crate is unmaintained, use adler2 instead
Date:      2025-09-05
ID:        RUSTSEC-2025-0056
URL:       https://rustsec.org/advisories/RUSTSEC-2025-0056
Dependency tree:
adler 1.0.2
└── miniz_oxide 0.7.1
    └── flate2 1.1.4
        ├── syntect 5.2.0
        │   └── bat 0.25.0
        └── bat 0.25.0

Crate:     bincode
Version:   1.3.3
Warning:   unmaintained
Title:     Bincode is unmaintained
Date:      2025-12-16
ID:        RUSTSEC-2025-0141
URL:       https://rustsec.org/advisories/RUSTSEC-2025-0141
Dependency tree:
bincode 1.3.3
├── syntect 5.2.0
│   └── bat 0.25.0
└── bat 0.25.0

Crate:     git2
Version:   0.20.1
Warning:   unsound
Title:     Potential undefined behavior when dereferencing Buf struct
Date:      2026-02-02
ID:        RUSTSEC-2026-0008
URL:       https://rustsec.org/advisories/RUSTSEC-2026-0008
Dependency tree:
git2 0.20.1
└── bat 0.25.0

warning: 3 allowed warnings found in /usr/bin/batcat
```

```{terminal}
:user: ubuntu
:host: resolute
:dir: ~

rust-audit-info /usr/bin/batcat

{"packages":[{"name":"adler","version":"1.0.2","source":"crates.io"},{"name":"aho-corasick","version":"1.1.4","source":"crates.io","dependencies":[65]},{"name":"ansi_colours","version":"1.2.3","source":"crates.io","dependencies":[86]},{"name":"anstream","version":"0.6.21","source":"crates.io","dependencies":[4,5,6,26,54,128]},{"name":"anstyle","version":"1.0.13","source":"crates.io"},{"name":"anstyle-parse","version":"0.2.7","source":"crates.io","dependencies":[128]},{"name":"anstyle-query","version":"1.1.4","source":"crates.io"},{"name":"anyhow","version":"1.0.101","source":"crates.io","kind":"build"},

# ... and many more dependencies
```

