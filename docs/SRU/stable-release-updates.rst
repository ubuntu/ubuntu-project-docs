.. _stable-release-updates-sru:

Stable Release Updates (SRU)
============================

.. A single sentence that says what the product is, succinctly and
   memorably.

**Stable release updates** (SRUs) are package updates to a currently supported Ubuntu release.

.. A paragraph of one to three short sentences, that describe what the
   product does.

Once an Ubuntu release has been completed and published, updates for it
are only **released under certain circumstances**, and must follow **a special
procedure** called SRU.

.. A third paragraph of similar length, this time explaining what need the
   product meets.

The SRU principles and processes ensure that stable Ubuntu releases **remain stable
and predictable** to the user.

.. Finally, a paragraph that describes whom the product is useful for.

This documentation is intended for **all Ubuntu users** if
they wish to understand what to expect from Ubuntu stable releases, and
also for **upstream and Ubuntu developers** if they wish to
understand what changes would or would not be acceptable to us. The rest
is intended for **Ubuntu developers and SRU team members** to achieve this
in practice.

.. important::
    Did you **notice a regression** in a package that went to the ``-updates`` pocket?
    Please report this by following :ref:`howto-report-regression`.

---------

Learn how Canonical determines which updates qualify for SRUs, who supervises the update process, who contributes and what responsibilities they have.


Which updates we release
------------------------

We follow strict rules to ensure that SRUs fix real-world problems and introduce no disruptions.

You can propose an SRU in the following cases:

- To fix high-impact bugs, including those that may directly cause security vulnerabilities, severe regressions from the previous release, or bugs that may directly cause loss of user data.
- To adjust to changes in the environment, server protocols, or web services. This ensures that Ubuntu remains compatible with evolving technologies.
- For safe cases with low regression potential but high user experience improvement.
- To introduce new features in :term:`LTS releases <LTS>`, usually under strict conditions.
- To update commercial software in the :ref:`partner-archive`.
- To fix :term:`Failed to build from Source` issues.
- To fix :term:`autopkgtest` failures, usually in conjunction with other high-priority fixes.

For the authoritative criteria, see :ref:`Reference → Requirements → What is acceptable to SRU <reference-what-is-acceptable-to-sru>`.

.. toctree::
    :maxdepth: 1

    explanation/principles
    explanation/requirements


Who releases updates
----------------------

The :ref:`SRU team and other stakeholders <explanation-role-expectations>` review and release updates. Community members outside of Canonical can contribute in the process.

.. toctree::
    :maxdepth: 1

    explanation/pipeline


Processes
---------

You must follow these rules when you upload a package update. Processes such as automatic tests, phasing and user reports prevent regressions in updates. Certain exceptions to standard processes are possible.

.. toctree::
    :maxdepth: 1

    explanation/standard-processes
    explanation/non-standard-processes
    explanation/further-requirements


Getting started
---------------

The basic SRU process consists of the following steps:

.. include:: explanation/pipeline.rst
   :start-line: 4
   :end-before: See also

For next steps, see :ref:`How-to → Perform a standard SRU <howto-perform-standard-sru>`.


.. toctree::
   :hidden:
   :maxdepth: 2

   reference/index
   internal
