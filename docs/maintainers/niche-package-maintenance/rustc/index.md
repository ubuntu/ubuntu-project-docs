(rustc-packaging)=
# `rustc` packaging

How to update, package, and maintain versions of {pkg}`rustc` in Ubuntu.

## Rust community

The Rust programming language has a vibrant and thriving community,
which is a valuable resource in addition to the guides on this website.

The Rust project maintains [an official webpage for community interaction](https://rust-lang.org/community/).

- Development of the Rust language happens on [the Rust project's Zulip instance](https://rust-lang.zulipchat.com/),[^oldrustdiscord] and of course on [Rust's Github repository](https://github.com/rust-lang/rust/).
- Discussion of Rust internals happens on the [Internals forum](https://internals.rust-lang.org/).
- You can get help with Rust as a programmer on the [User's forum](https://users.rust-lang.org/).
- [This Week In Rust](https://this-week-in-rust.org/) is a newsletter with handpicked updates about Rust and projects written in Rust, delivered to your inbox every Friday.

[^oldrustdiscord]: Rust used to have an official Discord server, but it is deprecated in favor of the Zulip.

There are also a great deal of unofficial resources and communities.

- The [Rust Programming Language Community Server](https://discord.com/servers/rust-programming-language-community-273534239310479360) (aka RPLCS) is a Discord server all about learning and sharing Rust knowledge, and helping others.
- [r/rust](https://reddit.com/r/rust), the Rust subreddit.

In general, Rust communities, whether official or unofficial, follow the [Rust code of conduct](https://rust-lang.org/policies/code-of-conduct/).

## Debian Rust community

Rust packaging has many quirks that it has inherited from Debian, and so the Debian documentation and community for packaging Rust will also be helpful.

- Debian's [wiki page on Rust packaging](https://wiki.debian.org/Teams/RustPackaging) documents the process of packaging things *written* in Rust. It also has many links to communication, like their mailing list and IRC.
- The [Debian Rust team book](https://rust-team.pages.debian.net/book/) documents how they package {pkg}`rustc` itself. Notably, this is where the documentation for {pkg}`debcargo` and {pkg}`dh-cargo` lives.

---

```{toctree}
:maxdepth: 1

Update Rust <update-rust>
Patch Rust <patch-rust>
Backport Rust <backport-rust>
rust-version-strings
Packaging FAQ <rust-packaging-faq>
rustc-debian-repository
Common Lintian issues <common-rustc-lintian-issues>

```
