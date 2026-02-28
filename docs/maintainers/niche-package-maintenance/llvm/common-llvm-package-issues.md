(common-llvm-package-issues)=
# Common LLVM package issues

Unfortunately, the upstream Debian Salsa repository


## Circular dependencies or incorrect versions being referenced

First of all, LLVM has some actual circular dependencies by design, and so you may be encountering that. It also has some specific build dependency chains, as well as configuration options that might be set incorrectly which can all manifest this issue.


### Actually circular dependencies

You might actual being encountering a circular dependency issue, especially if you are backporting a new version of LLVM. LLVM builds support for SPIR-V, which is a kind of intermediate representation for GPUs. In order to build some of the libraries needed to target SPIR-V, it actually needs some tooling to convert LLVM IR to SPIR-V. While LLVM is starting to get internal support for that, currently the de facto standard tool is an external one packaged as `llvm-spirv-X`. So in order to build LLVM fully, we need that package installed. However, that package makes use of LLVM libraries, and so it depends on `libllvm`. Usually, when we are doing a patch update for LLVM, like X.Y.Z to X.Y.Z+1 then we can just use the existing packages in the archive to bootstrap the new ones. If you are doing something like backporting a brand new version of LLVM to an older LTS release, you may need to do this bootstrapping yourself depending on what packages are available.

For doing that, see the instructions in {ref}`bootstrapping-a-new-llvm-version`.


(llvm-common-packages)=
### LLVM common packages

Another possibility is that you encountering issues related to the "common packages". This will generally manifest as an error where a dependency on an LLVM package is unsatisfiable, and the missing package does not contain an LLVM version name. For example, the build or tests might tell you that you're missing `libomp5`. But your package should be configured to build and use `libomp5-19` instead. This means that you haven't fully reverted the upstream change to this.

For help on this, see {ref}`configuring-the-common-llvm-packages`.

Note that if you see an unversioned `libllvm` dependency resolution failure, that's because that package doesn't exist, and your settings are incorrect. Ensure you're setting `SKIP_COMMON_PACKAGES` to `no`.


(why-is-it-saying-i-need-wasi-libc-installed)=
## Why is it saying I need `wasi-libc` installed?

It's not clear exactly why it was designed this way, but the `debian/rules` file has a specific check for this. There's some conditional code that disables the WASM support for older distros (Jammy, for instance), but when WASI is supported (Noble onward), it expects that to be installed on the host-system and errors out if it isn't found. However, it's already configured as a build dependency, so this configure-time check is superfluous. You can either install `wasi-libc` on your host system, or you can delete the following lines from `debian/rules`:

```bash
else \
    if ! dpkg -l|grep -q wasi-libc; then \
       echo "Could not find wasi-libc on the system"; \
	   echo "Please check that the package is available on the system"; \
	   echo "it might be that the 'hello' package is installed by another constraint"; \
	   exit 1; \
	fi; \
fi
```


## The integration test suite isn't unpacked correctly

At the time of writing, the component tarball that `pristine-tar` creates for the integration test suite has a mismatching directory name. While the packaging files expect it to unpack to `integration-test-suite`, it's currently unpacking to `llvm-toolchain-integration-test-suite-main`. An easy workaround is to change a line in `debian/tests/integration-test-suite-test.in` that copies the test suite directory to an autopkgtest direcotry. Just change the source directory name.
