.. _chapter-12-documentation:

Chapter 12 - Documentation
--------------------------

12.1 Manual pages
~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 12.1
<https://www.debian.org/doc/debian-policy/ch-documentation.html#manual-pages>`_)

----

12.2 Info documents
~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 12.2
<https://www.debian.org/doc/debian-policy/ch-documentation.html#info-documents>`_)

----

12.3 Additional documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 12.3
<https://www.debian.org/doc/debian-policy/ch-documentation.html#additional-documentation>`_)

----

12.4 Preferred documentation formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 12.4
<https://www.debian.org/doc/debian-policy/ch-documentation.html#preferred-documentation-formats>`_)

----

.. _ubuntu-policy-copyright-information:

12.5 Copyright information
~~~~~~~~~~~~~~~~~~~~~~~~~~

(*Modifies*: `Debian Policy Manual, Section 12.5
<https://www.debian.org/doc/debian-policy/ch-documentation.html#copyright-information>`_)

Every package must be accompanied by a verbatim copy of its copyright and
distribution license in the file :file:`/usr/share/doc/package/copyright`. This file
must neither be compressed nor be a symbolic link.

In addition, the copyright file must say where the upstream sources (if any)
were obtained. It should name the original authors of the package and the
Ubuntu maintainer(s) who were involved with its creation.

A copy of the file which will be installed in
:file:`/usr/share/doc/package/copyright` should be in debian/copyright in the
source package.

:file:`/usr/share/doc/package` may be a symbolic link to another directory in
:file:`/usr/share/doc` only if the two packages both come from the same source
and the first package Depends on the second. These rules are important because
copyrights must be extractable by mechanical means.

Packages distributed under the UCB BSD license, the Apache license (version
2.0), the Artistic license, the GNU GPL (version 2 or 3), the GNU LGPL
(versions 2, 2.1, or 3), and the GNU FDL (versions 1.2 or 1.3) should refer to
the corresponding files under :file:`/usr/share/common-licenses`, [#f98]_
rather than quoting them in the copyright file.

You should not use the copyright file as a general README file. If your package
has such a file it should be installed in :file:`/usr/share/doc/package/README`
or README.Debian or some other appropriate place.

----

12.6 Examples
~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 12.6
<https://www.debian.org/doc/debian-policy/ch-documentation.html#examples>`_)

----

.. _ubuntu-policy-changelog-files:

12.7 Changelog files
~~~~~~~~~~~~~~~~~~~~

(*Shared with Debian, see:* `Debian Policy Manual, Section 12.7
<https://www.debian.org/doc/debian-policy/ch-documentation.html#changelog-files>`_)

----

:ref:`← (Chapter 11 - Customized programs) Back <chapter-11-customized-programs>` | :ref:`Next (Appendix A) → <appendix-a>`

----

.. [#f98]
   In particular, :file:`/usr/share/common-licenses/BSD`,
   :file:`/usr/share/common-licenses/Apache-2.0`, :file:`/usr/share/common-licenses/Artistic`,
   :file:`/usr/share/common-licenses/GPL-2`, :file:`/usr/share/common-licenses/GPL-3`,
   :file:`/usr/share/common-licenses/LGPL-2`, :file:`/usr/share/common-licenses/LGPL-2.1`,
   :file:`/usr/share/common-licenses/LGPL-3`, :file:`/usr/share/common-licenses/GFDL-1.2`, and
   :file:`/usr/share/common-licenses/GFDL-1.3 respectively`.

