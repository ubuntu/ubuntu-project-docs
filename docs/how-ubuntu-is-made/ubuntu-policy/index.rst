.. _ubuntu-policy:

Ubuntu Policy Manual
====================

:Authors: The Debian Policy Mailing List; The Ubuntu Developers Mailing List
:Version: 4.7.3

----


.. _ubuntu-policy-abstract:

Abstract
--------

This manual describes the policy requirements for the Ubuntu distribution.
This includes the structure and contents of the Ubuntu archive and several
design issues of the operating system, as well as technical requirements that
each package must satisfy to be included in the distribution. It is derived
from the `Debian Policy Manual <https://www.debian.org/doc/debian-policy/>`_
and if not stated otherwise, the requirements of that apply to Ubuntu as well.

----

Copyright notice
----------------


Copyright © 1996,1997,1998 Ian Jackson and Christian Schwarz.

This file has been modified by Simon Johnsson on Feb 26, 2026.

:**Modifications**:

    - Change distribution method from the :pkg:`ubuntu-policy` package to
      Ubuntu docs website.
    - Omit section content equal to the Debian Policy Manual, and refer to the
      Debian Policy Manual instead, noted as "(*Shared with Debian, see:*
      `Debian Policy Manual`) and update :ref:`ubuntu-policy-abstract` to
      reflect this change.
    - Mark chapters and sections different to the Debian Policy Manual with
      "(*Modifies*: Debian Policy Manual, ``chapter/section``)".
    - Add "**Editor's note:**" to areas that are outdated, need
      clarification, and/or re-review.
    - Update number of packages in :ref:`chapter-2-ubuntu-archive`.
    - Update format version in :ref:`Section 5.6.16 Format
      <ubuntu-policy-format-field>`.

This manual is free software; you may redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2, or (at your option) any later version.

This is distributed in the hope that it will be useful, but *without any
warranty*; without even the implied warranty of merchantability or fitness for a
particular purpose. See the GNU General Public License for more details.

A copy of the GNU General Public License is available as
:file:`/usr/share/common-licenses/GPL` in the Debian GNU/Linux distribution or on the
World Wide Web at `the GNU General Public Licence
<http://www.gnu.org/copyleft/gpl.html>`_.

----

Contents
--------

.. admonition:: Chapters

   .. toctree::
      :maxdepth: 3

      1. About this manual <1-about-this-manual>
      2. The Ubuntu Archive <2-ubuntu-archive>
      3. Binary Packages <3-binary-packages>
      4. Source Packages <4-source-packages>
      5. Control files and their fields <5-control-files>
      6. Package maintainer scripts and installation procedure <6-package-maintainer-scripts>
      7. Declaring relationships between packages <7-declaring-relationships>
      8. Shared libraries <8-shared-libraries>
      9. The Operating System <9-the-operating-system>
      10. Files <10-files>
      11. Customized programs <11-customized-programs>
      12. Documentation <12-documentation>

.. admonition:: Appendices

   .. toctree::
      :maxdepth: 3

      A. Introduction and scope of these appendices <appendix-a>
      B. Binary packages <appendix-b>
      C. Source packages <appendix-c>
      D. Control files and their fields <appendix-d>
      E. Configuration file handling <appendix-e>
      F. Alternative versions of an interface - ``update-alternatives`` <appendix-f>
      G. Diversions - overriding a package's version of a file <appendix-g>


:ref:`← (Appendix G) Back <appendix-g>` | :ref:`Next (Chapter 1 - About this manual) → <chapter-1-about-this-manual>`
