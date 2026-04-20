(how-to-contribute)=
# Contributing to Ubuntu Development

Contributing to Ubuntu can mean many things, from {ref}`developing new applications <contribute-to-app-development>` to {ref}`reporting <how-to-report-a-bug>`, {ref}`triaging <triaging-bugs>`, and {ref}`fixing bugs <fixing-bugs>`, and many more development tasks. 

## Getting Started with Ubuntu Development

A great place to start working on Ubuntu is through {ref}`reporting a bug <how-to-report-a-bug>`. Being active on the bug discussion after posting is important as developers and other community members may ask follow up questions or ask for additional log information.

{ref}`Triaging <triaging-bugs>` and bug verification are good next steps. Bug verification is when another user reads the bug, follows steps outlined, and can "verify" the bug affects their system or a representative system, such as a virtual machine of the same Ubuntu version in the bug. Helping to triage bugs, ensuring all information required is present, and the correct package identified helps developers address the issue more quickly. Being able to help report these confirmed bugs upstream to Debian and original source (such as GitHub) are valuable contributions to Ubuntu.

{ref}`Fixing bugs <fixing-bugs>` is a more advanced task that requires greater knowledge of `git` and {ref}`patching workflows <patching>`. If you're feeling more comfortable in your skills as a software developer then finding upstream fixes, applying them to existing packages, and contributing to upstream projects to fix issues is of great help to Ubuntu.

# Guides for contributors

These guides help you with the specific tasks and processes that build Ubuntu.


## Setting up for distro work

This section includes all the relevant tooling you'll need to work on Ubuntu.

```{toctree}
:maxdepth: 1

setup/index
```

## Bug triaging

How to ensure bugs are targeting the appropriate packages, contain the required information, and verify that the bug, as specified, is reproducible.

```{toctree}
:maxdepth: 1

bug-triage/index
```


## QA and testing

How to test packages, ISOs, and other images. Also covers more specialized testing, such as upgrade testing (upgrading from one version of Ubuntu to another) and specific hardware testing.

```{toctree}
:maxdepth: 1

qa-and-testing/index
```


## Debugging

Introduction to debugging, including understanding `apport` and crash reports.

```{toctree}
:maxdepth: 1

debugging/index
```


## Bug fixing

Pages on finding fixes upstream, building locally or in a PPA, and running package tests.

```{toctree}
:maxdepth: 1

bug-fix/index
```


## Updating

Specific pages on working with Debian patches.

```{toctree}
:maxdepth: 1

updating/index
```


## Building

```{toctree}
:maxdepth: 1

/contributors/building/index
```




## Merging

The {ref}`merging` article series provides instructions on how to perform package merges (i.e. how to import a new version of a Debian package into Ubuntu if the Ubuntu package carries a {term}`delta`).

```{toctree}
:maxdepth: 1

merging/index
```


## Uploading and sponsorship

All aspects of seeking sponsorship for uploads to the Archive are covered in the {ref}`sponsorship` article series.

```{toctree}
:maxdepth: 1

Uploading <uploading/index>
```


## New packages

Contributing a new package to Ubuntu.

```{toctree}
:maxdepth: 1

new-package/index
```


## Stable Release Updates

Guidance for contributors on how to submit requests for SRU. See

```{toctree}
:maxdepth: 1

/SRU/howto/index
```

## Language-specific features

When we develop our build pipelines, we will sometimes add new features. See

```{toctree}
:maxdepth: 2

language-specific/index
```

## Accessibility

Basic workflow for checking accessibility, such as contrast and themes, text sizes, keyboard navigation, and screen reader usability.

```{toctree}
:maxdepth: 1

Check accessibility <check-accessibility>
```


## Contribute documentation

*Ubuntu Project documentation* is a collaborative effort. We welcome community contributions. For guidance on how to contribute to this documentation set, see:

```{toctree}
:maxdepth: 1

Contribute docs <contribute-docs>
```


## Setting up and using Matrix

Matrix is the instant messaging platform the Ubuntu Community uses.
This section will help you get set up with a Matrix client and show you how to use it to stay in contact with the community.

```{toctree}
:maxdepth: 1

/community/contributors/matrix/index
```


## Advanced tasks

Although you do not need any elevated permissions to work on the tasks in this
section, they are not suitable for beginners and require you to already have
some working familiarity with Ubuntu development. 

```{toctree}
:maxdepth: 1

Advanced tasks <advanced/index>
```


## Mirrors

Information on setting up an archive mirror.

```{toctree}
:maxdepth: 1

Set up a mirror </release-team/mirrors>
```
