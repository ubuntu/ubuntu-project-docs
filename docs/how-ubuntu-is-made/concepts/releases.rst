.. _ubuntu-releases:

Ubuntu releases
===============

Release cadence
---------------

:term:`Ubuntu` follows a strict time-based release cycle. Every six months since 2004, :term:`Canonical` publishes a new Ubuntu version and its set of :term:`packages <Package>` are declared stable (production-quality). Simultaneously, a new version begins development; it is given its own :term:`Code name`, but also referred to as the ":term:`Current Release in Development`" or ":term:`Devel`".


.. _lts-releases:

LTS releases
~~~~~~~~~~~~

Since 2006, every fourth release, made every two years in April, receives :ref:`long-term-support-lts`. This is the origin of the term :term:`LTS` for stable, maintained releases.

An estimated 95% of all Ubuntu installations are LTS releases.

.. note::

    Because of the strict time-based six months release cycle, LTS releases only happen in even-numbered years (e.g. ``18``, ``20``, ``22``) in April (``04``). The only exception to this rule was Ubuntu 6.06 LTS (Dapper Drake).


.. _point-releases:

Point releases
~~~~~~~~~~~~~~

To ensure that a fresh install of an :ref:`lts-releases` works on newer hardware and does not require a big download of additional updates, Canonical publishes **point releases** that include all the updates made so far.

The first point release of an LTS is published three months after the initial release and repeated every six months at least until the next LTS is published. In practice, Canonical may publish even more point releases for an LTS series, depending on the popularity of that LTS series.

For example, the Ubuntu 16.04.7 LTS (Xenial Xerus) point release was published more than four years after the initial release of Ubuntu 16.04 LTS.


.. _interim-releases:

Interim releases
~~~~~~~~~~~~~~~~

In the years between LTS releases, Canonical also produces **interim releases**, sometimes also called "regular releases".

Many developers use interim releases because they provide newer compilers or access to newer :term:`kernels <Kernel>` and newer libraries, and they are often used inside rapid DevOps processes like :term:`CI`/:term:`CD` pipelines where the lifespan of an artifact is likely to be shorter than the support period of the interim release.


Why does Ubuntu use time-based releases?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ubuntu releases represent an aggregation of the work of thousands of independent software projects. The time-based release process provides users with the best balance of the latest software, tight integration, and excellent overall quality.


Ubuntu version format
---------------------

.. code:: text

    YY.MM[.POINT-RELEASE] [LTS]

Ubuntu version identifier as used for Ubuntu releases consist of four components, which are:

``YY``
    The 2-digit year number of the initial release.

``MM``
    The 2-digit month number of the initial release.

``POINT-RELEASE``
    The :ref:`point release <point-releases>` number starts at ``1`` and increments with every additional point release.

    This component is omitted for the initial release, in which case zero is
    assumed.

``LTS``
    Any Ubuntu release that receives long term support is marked with ``LTS`` (see the :ref:`release-lifespan` section for more information).

    Any Ubuntu release that does not receive long term support omits this component.


Examples
~~~~~~~~

.. list-table::
    :header-rows: 1

    * - Version Identifier
      - Release Date
      - Support
      - End of Standard Support
      - End of Life
    * - ``22.04 LTS``
      - 21 April 2022
      - Long term
      - April 2027
      - April 2032
    * - ``22.04.1 LTS``
      - 11 August 2022
      - Long term
      - April 2027
      - April 2032
    * - ``22.10``
      - 22 October 2022
      - Regular
      - July 2023
      - July 2023
    * - ``22.04.2 LTS``
      - 13 February 2023
      - Long term
      - April 2027
      - April 2032
    * - ``23.04``
      - 20 April 2022
      - Regular
      - January 2024 
      - January 2024 


.. _release-lifespan:

Release lifespan
----------------

Every Ubuntu :term:`series` receives the same production-grade support quality, but the length of time for which an Ubuntu series receives support varies.


.. _regular-support:

Regular support
~~~~~~~~~~~~~~~

:ref:`interim-releases` are production-quality releases and are supported for nine months, with sufficient time provided for users to update, but these releases do not receive the long-term commitment of LTS releases.


.. _long-term-support-lts:

Long Term Support (LTS)
~~~~~~~~~~~~~~~~~~~~~~~

LTS releases receive five years of standard security maintenance for all packages in the :term:`main` :term:`component`. With an :term:`Ubuntu Pro` subscription, you get access to :term:`Expanded Security Maintenance` (:term:`ESM`), covering security fixes for packages in the :term:`universe` :term:`component`. ESM also extends the lifetime of an LTS series from five years to ten years.


Editions
--------

Every Ubuntu release is provided as both a :term:`Server <Ubuntu Server>` and :term:`Desktop <Ubuntu Desktop>` edition.

Ubuntu Desktop provides a graphical :term:`user interface` (:term:`GUI`) for everyday computing tasks, making it suitable for personal computers and laptops. :term:`Ubuntu Server`, on the other hand, provides a text-based :term:`User Interface` (:term:`TUI`) instead of a :term:`GUI`, optimized for server environments, that allows machines on the server to be run headless, focusing on server-related services and applications, making it ideal for hosting web services, databases, and other server functions.

Additionally, each release of Ubuntu is available in minimal configurations, which have the fewest possible packages installed: available in the installer for Ubuntu Server, Ubuntu Desktop, and as separate cloud images.

Canonical publishes Ubuntu on all major public clouds, and the latest :term:`image` for each LTS version will always include any security update provided since the LTS release date, until two weeks prior to the image creation date.


Ubuntu flavors
--------------

Ubuntu flavors are :term:`distributions <Distribution>` of the default Ubuntu releases that choose their own default applications and settings. Ubuntu flavours are owned and developed by members of the Ubuntu community and backed by the full :term:`Ubuntu Archive` for packages and updates.

Officially recognized flavors are:

- `Edubuntu`_
- `Kubuntu`_
- `Lubuntu`_
- `Ubuntu Budgie`_
- `Ubuntu Cinnamon`_
- `Ubuntu Kylin`_
- `Ubuntu MATE`_
- `Ubuntu Studio`_
- `Ubuntu Unity`_
- `Xubuntu`_

In addition to the officially recognized flavors, dozens of other :term:`Linux` distributions take Ubuntu as a base for their own distinctive ideas and approaches.


Further reading
---------------

- `The Ubuntu life cycle and release cadence <https://ubuntu.com/about/release-cycle>`_
- `Ubuntu flavors <https://ubuntu.com/desktop/flavours>`_
- `Ubuntu releases <https://releases.ubuntu.com/>`_
- `Ask a bug supervisor <https://answers.launchpad.net/launchpad/+question/140509>`_
