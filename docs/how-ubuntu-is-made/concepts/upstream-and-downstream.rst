.. _upstream-and-downstream:

Upstream and downstream
=======================

An :term:`Ubuntu` installation consists of :term:`packages <Package>` - copied and unpacked onto the target machine. The Ubuntu project packages, distributes, and maintains software of thousands of :term:`open source <Open Source Software>` projects for users, ready to install. The collection of Ubuntu packages is derived from the collection of packages maintained by the community-driven :term:`Debian` project.

An important duty of an Ubuntu package :term:`maintainer` is to collaborate with the open source projects the Ubuntu packages are derived from -- especially with Debian. We do this by keeping the Ubuntu copies of packages up-to-date and by sharing improvements made in Ubuntu back up to Debian.


Terminology
-----------

In the context of open source software development, the analogy of a stream that carries modifications, improvements, and code is used. It describes the relationship and direction of changes made between projects. This stream originates (upwards) from the original project (and related entities like :term:`source code`, authors, and maintainers) and flows downwards to projects (and associated entities) that depend on it.


Ubuntu delta
~~~~~~~~~~~~

Ubuntu delta (noun):
    A modification to an Ubuntu package that is derived from a Debian package.


.. _upstream:

Upstream
~~~~~~~~

.. _upstream-noun:

Upstream (noun):
    A software project (and associated entities) that another software project depends on either directly or indirectly.

    *Examples*:
        - Debian is the upstream of Ubuntu.
        - Upstream is not interested in the patch.

    *Usage note*:
        - There can be many layers. For example, **Kubuntu** is a :term:`flavor <Ubuntu flavours>` of Ubuntu, therefore Ubuntu and Debian are both upstreams of Kubuntu.
        - The adjective/adverb form is much more commonly used.

.. _upstream-adjective-adverb:

Upstream (adjective, adverb):
    Something (usually a code modification like a :term:`patch`) that flows in the direction or is relative to a software project closer to the original software project.

    *Examples*:
        - Debian is the upstream project of Ubuntu.
        - There is a new upstream release.
        - A pull request was created upstream.
        - A bug was patched upstream.

.. _upstream-verb:

upstream (verb):
    Sending something (usually a patch) upstream that originated from a :term:`fork` or project that depended on the upstream project.

    *Examples*:
        - We upstreamed the patch.
        - Can you upstream the bug fix?


.. _downstream:

Downstream
~~~~~~~~~~

Downstream (noun):
    Similar to :ref:`upstream-noun`. A software project(s) (and associated entities) that depend on another software project either directly or indirectly.

    *Example*:
        - Ubuntu is a downstream of Debian and there are many downstreams of Ubuntu.

    *Usage note*:
        - The :ref:`adjective/adverb form <downstream-adjective-adverb>` is much more commonly used.
        - There can be many layers. For example, **Kubuntu** is a flavor of Ubuntu, therefore Kubuntu and Ubuntu are both downstreams of Debian.

.. _downstream-adjective-adverb:

Downstream (adjective, adverb):
    Similar to :ref:`upstream-adjective-adverb` Something (usually a code modification like a patch) that flows in the direction or is relative to a software project farther away from the original software project.

    *Examples*:
        - Ubuntu is a downstream project of Debian.
        - The bug is already patched downstream.
        - The bug was reported by a downstream user.
        - Downstream maintainers have submitted a bug fix.
        - The change may affect downstream users.

Downstream (verb):
    Similar to :ref:`upstream-verb` Sending something (usually a patch) downstream that originated from an upstream project.

    *Example*:
        - We downstreamed the patch.


Why do we upstream changes?
---------------------------

.. note::
    The following list does not aim for completeness. There are plenty of other good arguments for why changes should be upstreamed.

- **Decreased maintenance complexity**: Think of any Ubuntu package derived from a Debian package that carries a :term:`delta <Ubuntu Delta>`. Every time the Debian package gets updated, the Ubuntu package may be subject to a :term:`merge conflict` when the changes to the Debian package get applied to the Ubuntu package. By upstreaming changes we reduce the maintenance cost to resolve merge conflicts when they occur.

- **Quality assurance and security**: Any changes that get upstreamed are also subject to the quality assurance of the upstream project and the testing coverage that the user base of the upstream project provides. This increases the likelihood of discovering regressions/bugs/unwanted behavior (especially security-related bugs). Also, be aware that an unpatched :term:`security vulnerability <Common Vulnerabilities and Exposures>` in any system can lead to the indirect exposure of other systems.

- **Mutual benefit**: By syncing the Debian packages into the Ubuntu package collection, Ubuntu benefits from the upstream maintenance work. In exchange, Ubuntu Maintainers upstream changes to Debian. This results in a win-win situation where both parties benefit from working together.
