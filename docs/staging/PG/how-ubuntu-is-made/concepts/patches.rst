.. _patches:

Patches
=======

Patches record modifications to :term:`source code`. Patches can come in many
forms, including but not limited to:

- :term:`Upstream` features or bug-fixes not present in the current release.
- :term:`Ubuntu` specific changes, such as custom defaults and theming.
- :term:`CVE` fixes and other security-related updates.

All changes to a :term:`source package` in the ``3.0 (quilt)`` format (see
:ref:`explanation <SourcePackageFormat_3.0quilt>`) to the source files
(all files inside the :term:`orig tarball` / outside the ``debian/``
directory) must be applied in the form of a patch.

Changes to a source package in the ``3.0 (native)`` format (see 
:ref:`explanation <SourcePackageFormat_3.0native>`) get applied directly
and will not be further discussed in this article. 

It is important to treat patches with care, and ensure the format and headers
follow best practices. This makes it easier to maintain a package long-term.
In Ubuntu, we try to follow the :term:`DEP 3` specification, which details a
standard format for patch headers.

The source package stores the patches in the :file:`debian/patches/` directory.
These patches get applied from top to bottom in the order they are listed in
:file:`debian/patches/series`, excluding empty lines and lines starting with ``#``.

Sending patches upstream
------------------------

Changes to the upstream source code which are not Ubuntu specific should be sent
to the upstream authors in whatever form they prefer. This allows the upstream
authors to include the patch in the upstream version of the package.

When you should (not) rewrite a patch header to follow DEP 3
------------------------------------------------------------

You **should** rewrite a patch header to follow DEP 3 if:

* You are introducing a new patch altogether.
* You are making substantive modifications to an existing patch.
* More information is known about the patch, and a DEP 3 header would contain
  updated information.

You **should not** rewrite a patch header to follow DEP 3 if:

* You are preparing a non-:term:`micro-release exception SRU <Micro-Release Exception>`
  and changing the patch header is not directly related to the bug being fixed.
* You intend on keeping only the modifications to the header as part of the
  :term:`Ubuntu delta` without making substantive changes to the diff contents,
  and have no plans to forward it to :term:`Debian`.
* The team claiming responsibility for this package in Ubuntu explicitly
  disagrees with the usage of DEP 3 headers. (This should be brought up on the
  ubuntu-devel mailing list.)

Resources
---------

- :ref:`patch-management`
- :ref:`dep-3-patch-file-headers`
- `Debian Policy Section 4.3. -- Changes to the upstream sources <https://www.debian.org/doc/debian-policy/ch-source.html#changes-to-the-upstream-sources>`_
- `Debian Policy Section 4.13. -- Embedded code copies <https://www.debian.org/doc/debian-policy/ch-source.html#embedded-code-copies>`_
- `Debian Policy Section 4.17. -- Vendor-specific patch series <https://www.debian.org/doc/debian-policy/ch-source.html#vendor-specific-patch-series>`_
- `Debian Policy Appendix 7. -- Diversions - overriding a package's version of a file (from old Packaging Manual) <https://www.debian.org/doc/debian-policy/ap-pkg-diversions.html>`_
