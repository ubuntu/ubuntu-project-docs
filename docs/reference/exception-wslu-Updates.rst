.. _reference-exception-wslu-Updates:

wslu Updates
============

This document describes the policy for updating the wslu package to new
upstream versions in a stable, supported distro (including LTS
releases).

The wslu package is a set of settings and utilities to integrate Ubuntu
running in `WSL <https://wiki.ubuntu.com/WSL>`__ to the host Windows 10 system. The wslu package
is shipped in the Ubuntu Microsoft Store apps and in the downloadable
`WSL <https://wiki.ubuntu.com/WSL>`__ tarballs for supported Ubuntu releases (see
`installation <https://wiki.ubuntu.com/WSL#Installing_Ubuntu>`__).

The wslu package is shipped with the intent of providing uniformly
complete integration across all supported Ubuntu releases and the way of
ensuring consistent behavior is back-porting full upstream releases with
minimal changes.

New versions of wslu can be SRU'd in to older releases provided the
following process is followed.

.. _qa_process:

wslu QA Process
---------------

When a new version of wslu is uploaded to -proposed, the following will
be done:

-  The wslu package is tested if it can be upgraded from the previous
   version
-  The fixes upstream claimed to have been fixed are verified preferably
   by extending the package's autopkgtests
-  The wslu package's autopkgtest is run inside `WSL <https://wiki.ubuntu.com/WSL>`__ on a
   Windows 10 system manually or in an automated way that also captures
   the screen.
-  (optional) A new Ubuntu app is built with the updated wslu package
   preinstalled.
-  (optional) The autopkgtest is run in the installed new Ubuntu app
   with the preinstalled wslu package.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug for this stable release
exception, instead of individual bug reports for individual bug fixes.
However, individual bugs may be referenced in the changelog and each of
those bugs will need to be independently verified and commented on for
the SRU to be considered complete.
