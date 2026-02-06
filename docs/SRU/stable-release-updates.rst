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

.. toctree::
    :maxdepth: 1

    explanation/principles
    explanation/requirements


Who releases updates
----------------------

The SRU team and other stakeholders review and release updates. Community members outside of Canonical can contribute in the process.

.. toctree::
    :maxdepth: 1

    explanation/pipeline
    explanation/roles


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
