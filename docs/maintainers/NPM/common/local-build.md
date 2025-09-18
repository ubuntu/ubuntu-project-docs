### Local Build and Bugfixing

You're now ready to try to build `rustc` using {manpage}`sbuild(1)`.

First, make sure that all previous build artifacts have been cleaned from your upper-level directory:

(updating-rust-clean-build)=

```none
$ rm -vf ../*.{debian.tar.xz,dsc,buildinfo,changes,ppa.upload}
$ rm -vf debian/files
$ rm -rf .pc
```

Then, run the build! Depending on your computer, a full build tends to take about 1-3 hours.

```none
$ sbuild -Ad <release>
```

#### Using another PPA to bootstrap

Not all `rustc` releases are necessarily in the archive. Perhaps you're waiting on a previous version to be upload, or you're creating a backport which isn't needed by the subsequent Ubuntu release.

If this applies to you, you must add your PPA as an extra repository to your `sbuild` command:

```none
$ sbuild -Ad <release> \
    --extra-repository="deb [trusted=yes] http://ppa.launchpadcontent.net/<lpuser>/<ppa_name>/ubuntu/ <release> main"
```

#### Fixing bugs

If the build fails, it's up to you to figure out why. This will require problem-solving skills and attention to detail.

First, try to find any upstream issues related to the problem on the [Rust GitHub page](https://github.com/rust-lang/rust/issues?q=is%3Aissue). It's quite common for non-packaging-related problems to be already known upstream, and you can often find a patch from there.

#### Searching for failing tests within the build log

`sbuild` saves the build logs to your computer. You can easily jump to the standard output of each failing test by searching for the following within the log:

```none
stdout ----
```

#### Running individual tests

If the build fails, then `sbuild` will place you in an interactive shell for debugging. This is extremely useful, as you can change the source code and retry tests without rebuilding the whole thing.

For example, here's how to re-run all the bootstrap tests:

```none
$ debian/rules override_dh_auto_test-arch RUSTBUILD_TEST_FLAGS="src/bootstrap/"
```

Here's how to re-run _just_ the `alias_and_path_for_library` bootstrap test:

```none
$ debian/rules override_dh_auto_test-arch RUSTBUILD_TEST_FLAGS="src/bootstrap/ --test-args alias_and_path_for_library"
```

#### Proper patch header format

In order to fix certain bugs, it's likely you'll need to create your own patch at some point. It's important that this patch contains enough information for other people to understand _what_ it's doing and _why_ it's doing it.

First, ensure that [Debian](https://salsa.debian.org/rust-team/rust/-/tree/debian/experimental?ref_type=heads) has not already created an equivalent patch. If so, you can simply use their patch directly. If you need to modify the patch in any way, make sure to add `Origin: backport, <Debian VCS patch URL>` to the patch header.

Otherwise, you must create your own patch. A template {term}`DEP-3 <DEP 3>` header can be generated using the following command:

```none
$ quilt header -e --dep3 <path/to/patch>
```

For the most part, you can follow the [Debian DEP-3 patch guidelines](https://dep-team.pages.debian.net/deps/dep3/). However, there are a few extra things you must do:

- Debian developers typically don't use the `This patch header follows DEP-3 [...]` line added by `quilt`. Delete this line.
- If this patch isn't something needed to get the new Rust version to build, and you're instead updating an existing source package, add a `Bug-Ubuntu:` line linking to the Launchpad bug.
