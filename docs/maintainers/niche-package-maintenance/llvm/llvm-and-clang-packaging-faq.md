(llvm-and-clang-packaging-faq)=
# LLVM and Clang Packaging FAQ

You may want to start by reading the {ref}`LLVM packaging guide <packaging-llvm>`.
The goal of this FAQ is to collect answers to common questions in a single place.

## Why does one source package build so many things?

LLVM upstream uses a monorepo: `clang`, `lld`, `lldb`, `flang`, `MLIR`, and the rest are all developed in the same repository and released together as a single tarball. The subprojects share the LLVM core libraries and are tightly coupled at the source level, which makes a monolithic source package a natural fit. The effect of that is that `llvm-toolchain-X` is one of the largest source packages in the archive and produces more than 50 binary packages from a single build.

## What is the LLVM release cadence, and how does it affect Ubuntu?

LLVM follows a time-based schedule with major releases roughly every 6 months, branching in January and July.

Ubuntu series each adopt one version as the default, which gets maintained for the lifetime of that series. Ubuntu LTS releases have support windows of up to 15 years, so the default LLVM version will continue to receive updates and security fixes long after newer major versions have shipped upstream. Newer major versions are kept available in the archive alongside it, mostly to support developers and packages that need newer features, but they do not replace the default.

## How do SONAMEs work for LLVM libraries, and why can multiple versions coexist?

LLVM only guarantees ABI stability within a major version: patch releases (19.1.0, 19.1.1, …) are ABI-compatible with each other, but LLVM 18 and LLVM 19 are not compatible. Rather than following the conventional Debian pattern of incrementing the number after `.so` on each ABI break, LLVM embeds the major version directly in the library name. So the shared library is `libLLVM-19.so.1`, and the `.1` suffix (`SONAME_EXT` in `debian/rules`) stays at `1` regardless of how many minor releases ship.

The practical consequence is that `libllvm18` and `libllvm19` are completely independent packages with no file conflicts, and installing both on the same system is straightforward. This is by design, as many tools are built against a specific LLVM major version and link against that specific `.so`.

The common packages like `libomp5` are the exception: they have a stable ABI across major LLVM versions, which is why they can be shipped without a version suffix.

## What is the difference between `libllvm`, `libclang1`, and `libclang-cpp`?

The LLVM project exposes several different shared libraries, which serve distinct audiences.

`libllvm19` is the core LLVM library, containing the optimizer, code generators, and analysis infrastructure. Most tools that work with LLVM IR directly link against this.

`libclang1-19` exposes a stable C API for working with Clang's AST and analysis. It is intentionally limited but has strong backwards compatibility guarantees, making it the preferred interface for editors, IDEs, and other tooling that needs to parse C/C++ without committing to LLVM's internal C++ APIs.

`libclang-cpp19` exposes the full Clang C++ API, which is much more powerful but carries no stability guarantees between releases.
It is used by tools that are developed in lockstep with LLVM, such as `clangd` and `clang-tidy`, which depend on `libclang-cpp19` at the same version they were built against.

## What is the relationship between `llvm-toolchain-X`, `llvm-defaults`, and the unversioned packages?

Historically, each LLVM source package would build versioned binary packages, e.g., `clang-18` and `libomp5-18`. Then `llvm-defaults` would define the unversioned packages like `clang` and `libomp5` and have those depend on whichever versioned ones were the default. More recently, this has changed so that some shared libraries are built directly by the most recent `llvm-toolchain-X` package, and so there are now two distinct types of unversioned packages:

The unversioned **tool packages** like `clang`, `lldb`, and `lld` come from the `llvm-defaults` source package.
These packages contain no code of their own, they simply depend on the appropriate versioned package for that Ubuntu release.
On Noble, for instance, installing `clang` gives you an `llvm-defaults`-generated stub that pulls in `clang-18`.
Updating the default LLVM version for a series is then just a matter of updating `llvm-defaults`.

The ABI-stable **library packages**, like `libomp5` and `libc++1`, work differently.  These are built directly by the latest `llvm-toolchain-X` in the archive, and can be inspected via that package's `debian/packages.common` file. Any version of LLVM that is older, links against these. While that means that the code used to generate the shared libraries can change throughout the lifetime of an Ubuntu release, upstream guarantees that this is transparent by their ABI stability promise.  Configuring the package itself is done by the `SKIP_COMMON_PACKAGES` mechanism described below.

## What are the "common packages" and why do they matter?

Some LLVM libraries have a stable ABI and are intentionally shipped without a version suffix in the package name.
These are called the common packages, listed in `debian/packages.common`, and include things like `libomp5` and `libc++1`.

The `SKIP_COMMON_PACKAGES` variable in `debian/rules` is how maintainers control which version of LLVM builds them.  When set to `no`, the package builds the unversioned forms directly, which is what the default version for a given Ubuntu series should do.  When set to `yes`, the package skips building the common libraries and instead declares dependencies on the ones produced by `NEW_LLVM_VERSION`.

See {ref}`configuring-llvm-common-packages` for more detail.

## What components does the `llvm-toolchain-X` source package produce?

The `llvm-toolchain-X` source package is a monolithic build of the entire LLVM project and produces more than 50 binary packages.
Some notable ones include:

- `llvm-X` — the LLVM optimizer and code generator tools
- `clang-X` — the C/C++/Objective-C compiler front end
- `lld-X` — the LLVM linker
- `lldb-X` — the LLVM debugger
- `flang-X` — the Fortran compiler front end
- `libllvm-X-dev` / `libllvm-X` — LLVM libraries for development and runtime use
- `libclang-X-dev` / `libclang1-X` — Clang libraries (e.g. for `libclang` bindings)
- `libomp-X-dev` / `libomp5` — OpenMP runtime (`libomp5` is a common package built by the default version)
- `libc++-X-dev` / `libc++1` — LLVM's C++ standard library (also a common package)
- `libc++abi-X-dev` / `libc++abi1-X` — C++ ABI library used by `libc++`
- `libunwind-X-dev` / `libunwind-X` — LLVM's unwinder library
- `python3-lldb-X` — Python bindings for `lldb`

Because the source package builds so many binary packages, build times are substantial.
The `PROJECTS` and `RUNTIMES` variables in `debian/rules` control which subprojects are compiled, and trimming them down is a good way to speed up local test builds.

## What is the circular dependency involving SPIR-V?

LLVM can target SPIR-V, a GPU intermediate representation used by Vulkan and OpenCL.
Building the SPIR-V backend requires `llvm-spirv-X`, a separate tool for converting LLVM IR to SPIR-V, but `llvm-spirv-X` itself depends on LLVM libraries.

In practice this is only a problem when no version of `llvm-spirv-X` is yet available in the archive for the LLVM version you are building, which typically comes up when backporting a brand-new LLVM major version to an LTS release.
In that case you need to bootstrap: build a stripped-down LLVM first without SPIR-V support, use that to build `llvm-spirv-X`, and then do a full LLVM build.

See the {ref}`bootstrapping section of the packaging guide <bootstrapping-llvm>` for instructions.

## How do `clang/llvm` and `gcc` interact on an Ubuntu system?

There are interactions in both directions.

Clang depends on some GCC system headers, runtime libraries (`crtbegin.o`, `crtend.o`), and linker scripts. On Ubuntu, Clang finds these automatically by detecting the installed `gcc` version, which is why `clang` and `clang-X` both depend on `gcc`. This may change as LLVM projects like `libc++` and `lld` continue to mature.  See the [LLVM documentation](https://clang.llvm.org/docs/Toolchain.html) for some details.

GCC also depends on LLVM in some scenarios (but not `clang` directly). For instance, GCC can offload OpenMP and OpenACC code to AMD GCN GPUs via the `gcc-N-offload-amdgcn` package. That package depends on `amdgcn-tools-X`, which in turn depends on `llvm-X` and `lld-X`, because LLVM provides the assembler, linker, and related binary tools for the `amdgcn` target, while GCC has no native support for those.
