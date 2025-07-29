.. _package-archive:

Package archive
===============

:term:`Linux` :term:`distributions <Distribution>` like :term:`Ubuntu` use :ref:`repositories <Repositories>` to hold :term:`packages <Package>` for installing on target machines. Ubuntu has several repositories that anyone can access. The **Ubuntu package archive** hosts :term:`Debian` :term:`binary packages <Binary Package>` (``.deb`` files) and :term:`source packages <Source Package>` (``.dsc`` files).

On Ubuntu installations, the Ubuntu package archive is configured as the default source for the :term:`APT` package manager to download and install packages from. This Archive splits into many layers, each with its own terminology.

The general flow is that the archive splits into :ref:`Ubuntu series <archive-series>`. Each series is split up into :ref:`pockets <archive-pockets>`, and then each pocket contains four :ref:`components <archive-components>`. This diagram shows a look through a single path:

.. mermaid::

    flowchart TD;
      A[Ubuntu package archive] --> B([Splits into Ubuntu **series**]);

      B --> C[e.g., mantic];
      B --> D[noble];
      B --> E[oracular, etc.];

      D --> H([Series split into **pockets**]);

      H --> I[-release];
      H --> J[-proposed];
      H --> K[-updates];
      H --> L[-security];
      H --> M[-backports];

      K --> N([Splits into **components**]);

      N --> O[main];
      N --> P[universe];
      N --> Q[restricted];
      N --> R[multiverse];

      style C fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style D fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style E fill:#fff,stroke:#cfcfcf,stroke-width:2px;

      style I fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style J fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style K fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style L fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style M fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style O fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style P fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style Q fill:#fff,stroke:#cfcfcf,stroke-width:2px;
      style R fill:#fff,stroke:#cfcfcf,stroke-width:2px;

.. note::

    Some of the terminology is only loosely or informally defined. Be aware that the terminology surrounding the Ubuntu package archive gets mixed up in day-to-day communications. This can be confusing, but the meaning is usually evident from the surrounding context once you are familiar with the following terms.


.. _archive-repositories:

Repositories
------------

In the context of package management, **repositories** are servers containing sets of packages that a :term:`package manager` can download and install.

This term can refer to the Ubuntu package archive as a whole or just:

- :ref:`suites <archive-suite>`
- :ref:`pockets <archive-pockets>`
- :ref:`components <archive-components>`.


.. _archive-series:

Series
------

A **series** refers to the packages that target a specific Ubuntu version. A series is usually referred to by its :term:`code name`.

Examples of series are: ``mantic``, ``lunar``, ``jammy``, ``focal``, ``bionic``, ``xenial``, ``trusty``.

.. note::

    In practice, the terms "Ubuntu series" and "Ubuntu release" are often used interchangeably or are mistaken for each other. There is technically a difference; for example, an LTS version usually has an initial release (e.g. 22.04 LTS) and multiple point releases (e.g. 22.04.1 LTS, 22.04.2 LTS), which are all part of the same *series* (e.g. ``jammy``).


.. _archive-pockets:

Pockets
-------

**Pockets** are package sub-repositories within the Ubuntu package archive. Every Ubuntu series has the following pockets:


.. _archive-pockets-release:

release
~~~~~~~

This pocket contains the packages that an Ubuntu series was initially released with. After the initial release of an Ubuntu series, the packages in this pocket are not updated (not even for security-related fixes).


.. _archive-pockets-security:

security
~~~~~~~~

This pocket contains security-related updates to packages in the :ref:`archive-pockets-release` pocket.


.. _archive-pockets-updates:

updates
~~~~~~~

This pocket contains non-security-related updates to packages in the :ref:`archive-pockets-release` pocket.


.. _archive-pockets-proposed:

proposed
~~~~~~~~

This pocket is a :term:`staging environment` the Ubuntu community can opt into, to verify the stability of any updates before they get deployed to a broader range of consumers.

* Before the initial release of an Ubuntu series, this pocket contains non-security-related updates to packages in the :ref:`archive-pockets-release` pocket before they get uploaded to the :ref:`archive-pockets-release` pocket.

* After the initial release of an Ubuntu series, this pocket contains non-security-related updates to packages in the :ref:`archive-pockets-release` pocket before they get uploaded to the :ref:`archive-pockets-updates` pocket.


.. _archive-pockets-backports:

backports
~~~~~~~~~

This pocket contains packages the Ubuntu series was initially **NOT** released with.

The :ref:`backports` provides more information on backporting software.

.. important::

    The **backports pocket** does not come with any security support guarantee. The Ubuntu Security Team does not update packages in the backports pocket. The Ubuntu community is responsible for maintaining packages in backports with later patches for bug fixes and security updates.


.. _archive-suite:

Suite
-----

A combination of a series and a pocket. For example:

+---------------------+----------------------+----------------------------------+
| Suite               | Series               | Pocket                           |
+---------------------+----------------------+----------------------------------+
| ``jammy``           | ``jammy``            | :ref:`archive-pockets-release`   |
+---------------------+----------------------+----------------------------------+
| ``jammy-security``  | ``jammy``            | :ref:`archive-pockets-security`  |
+---------------------+----------------------+----------------------------------+
| ``jammy-updates``   | ``jammy``            | :ref:`archive-pockets-updates`   |
+---------------------+----------------------+----------------------------------+
| ``jammy-proposed``  | ``jammy``            | :ref:`archive-pockets-proposed`  |
+---------------------+----------------------+----------------------------------+
| ``jammy-backports`` | ``jammy``            | :ref:`archive-pockets-backports` |
+---------------------+----------------------+----------------------------------+

See `all active suites <http://archive.ubuntu.com/ubuntu/dists/>`_ in the archive.

.. note::

    The ``devel`` series always mirrors the series with the code name of the :term:`current release in development <Current Release in Development>`.


.. _archive-components:

Components
----------

**Components** are logical subdivisions or :term:`namespaces <Namespace>` of the packages in a suite. The APT package manager can subscribe to the individual components of a suite.

The packages of an Ubuntu series are categorized according to whether they are :term:`open source software` or :term:`closed source software`, and whether or not they are part of the :term:`base packages <Ubuntu Base Packages>` for a given series. On this basis, they are sorted into the components **main**, **restricted**, **universe**, or **multiverse**, as shown in the following table:

+----------------------------+------------------------------------+--------------------------------------+
|                            | Open source software               | Closed source software               |
+----------------------------+------------------------------------+--------------------------------------+
| **Ubuntu base packages**   | :ref:`archive-components-main`     | :ref:`archive-components-restricted` |
+----------------------------+------------------------------------+--------------------------------------+
| **Community packages**     | :ref:`archive-components-universe` | :ref:`archive-components-multiverse` |
+----------------------------+------------------------------------+--------------------------------------+

:term:`Canonical` maintains the base packages and provides security updates. See :ref:`release-lifespan` for more information about the official support provided by Canonical.

For example, if you look into any of the :ref:`archive-pockets` of the ``devel`` series (|devel-release|_, |devel-updates|_, |devel-security|_, |devel-proposed|_, |devel-backports|_) you see the four components (main, restricted, universe, multiverse) as directories.


.. _archive-components-main:

main
~~~~

This component contains open source software packages for a given series that are supported and maintained by Canonical.


.. _archive-components-restricted:

restricted
~~~~~~~~~~

This component contains closed source software packages for a given series that are supported and maintained by Canonical. Packages in this component are mostly proprietary drivers for devices and similar.


.. _archive-components-universe:

universe
~~~~~~~~

This component contains open source software packages for a given series that are supported and maintained by the Ubuntu community.


.. _archive-components-multiverse:

multiverse
~~~~~~~~~~

This component contains packages (for a given series) of closed source software, or open source software restricted by copyright or legal issues. These packages are maintained and supported by the Ubuntu community, but because of the restrictions, patching bugs or updates may not be possible.


.. _archive-mirrors:

Mirrors
-------

Every day, hundreds of thousands of people want to download and install packages from the Ubuntu package archive. To provide a good :term:`user experience`, the content of ``http://archive.ubuntu.com/ubuntu`` is mirrored (replicated and kept in sync) by other servers to distribute network traffic, reduce latency, and provide redundancy, which ensures high availability and fault tolerance.

A complete list of officially recognized `Ubuntu package archive mirrors <https://launchpad.net/ubuntu/+archivemirrors>`_.

.. note::

    There are also mirrors for the Ubuntu :term:`ISO` images (also called "CD images", because ISO images can be downloaded and burned to a CD to make installation disks.)

    A complete list of officially recognized `Ubuntu CD mirrors <https://launchpad.net/ubuntu/+cdmirrors>`_.


Country mirrors
~~~~~~~~~~~~~~~

Ubuntu package archive mirrors that provide a very reliable service in a country can request to be the official **country mirror** for that country. Ubuntu installations are configured by default to use the country mirror for their selected country.

Country mirrors are accessible via the domain name format:

.. code:: text

    <country-code>.archive.ubuntu.com

To see which mirror is the country mirror, do a :term:`DNS` lookup. For example:

.. tabs::

    .. tab:: Finland (``FI``)

        .. terminal::
           :input: dig fi.archive.ubuntu.com +noall +answer

            fi.archive.ubuntu.com.	332	IN	CNAME	mirrors.nic.funet.fi.
            mirrors.nic.funet.fi.	332	IN	A	193.166.3.5

        Therefore, ``mirrors.nic.funet.fi`` is Finland's country mirror.

    .. tab:: Tunisia (``TN``)

        Tunisia does not have any third-party mirrors in its country. Therefore the
        Tunisia country mirror is just the primary Ubuntu package archive server
        (``archive.ubuntu.com``).

        .. terminal::
           :input: dig tn.archive.ubuntu.com +noall +answer

            tn.archive.ubuntu.com.	60	IN	A	185.125.190.36
            tn.archive.ubuntu.com.	60	IN	A	91.189.91.83
            tn.archive.ubuntu.com.	60	IN	A	91.189.91.82
            tn.archive.ubuntu.com.	60	IN	A	185.125.190.39
            tn.archive.ubuntu.com.	60	IN	A	91.189.91.81

        which are just the ``archive.ubuntu.com`` IP addresses:

        .. terminal::
           :input: dig archive.ubuntu.com +noall +answer

            archive.ubuntu.com.	1	IN	A	185.125.190.39
            archive.ubuntu.com.	1	IN	A	185.125.190.36
            archive.ubuntu.com.	1	IN	A	91.189.91.83
            archive.ubuntu.com.	1	IN	A	91.189.91.81
            archive.ubuntu.com.	1	IN	A	91.189.91.82


Package uploads
---------------

Ubuntu encourages contributions from any person in the wider community. However, direct uploading to the Ubuntu package archive is restricted. These general contributions need to be reviewed and uploaded by a :term:`sponsor`.

See :ref:`sponsorship` that explains this process in more detail.


Security update propagation
---------------------------

Because security updates contain fixes for :term:`Common Vulnerabilities and Exposures` (CVE), it is critical to distribute them as fast as possible to end users. Mirrors are a technical burden in this case, because there is a delay between the synchronization of a mirror and the primary Ubuntu package archive server.

In the worst case a bad actor gets informed about a CVE and can use it before the update reaches a target machine.

Therefore the APT package manager (on Ubuntu) is configured by default to also check for updates from ``security.ubuntu.com``. Security updates get uploaded there first. If a mirror does not provide the update yet, a client downloads it from ``security.ubuntu.com`` instead from the mirror.

To see this yourself, look what the :manpage:`sources.list(5)` file contains on your Ubuntu machine:

.. code:: none

    cat /etc/apt/sources.list

At the end of the file, you find something similar to this:

.. code:: text

    deb http://security.ubuntu.com/ubuntu SERIES-security main restricted
    # deb-src http://security.ubuntu.com/ubuntu SERIES-security main restricted
    deb http://security.ubuntu.com/ubuntu SERIES-security universe
    # deb-src http://security.ubuntu.com/ubuntu SERIES-security universe
    deb http://security.ubuntu.com/ubuntu SERIES-security multiverse
    # deb-src http://security.ubuntu.com/ubuntu SERIES-security multiverse

Because the :manpage:`sources.list(5)` file is read from top to bottom, the APT package manager downloads updates from the mirror first and only downloads them from ``security.ubuntu.com`` if the mirror has an older version.

``security.ubuntu.com`` points to the same servers as ``archive.ubuntu.com``. It is used in the :manpage:`sources.list(5)` file for the security pocket to prevent a user or script from accidentally changing it to a mirror.


Further reading
---------------

- `Ubuntu release cycle <https://ubuntu.com/about/release-cycle>`_
- `Ubuntu blog -- Ubuntu updates, releases and repositories explained <https://ubuntu.com/blog/ubuntu-updates-releases-and-repositories-explained>`_
- `Ubuntu Server docs -- package management <https://ubuntu.com/server/docs/package-management>`_


Landscape repositories
~~~~~~~~~~~~~~~~~~~~~~

`Landscape <https://ubuntu.com/landscape>`_ is a management and administration tool for Ubuntu. Landscape allows to mirror :term:`APT` repositories like the Ubuntu package archive. Although it is not directly related to the Ubuntu package archive, it can be educational to understand how APT repositories work in general.

.. |main| replace:: :ref:`archive-components-main`
.. |restricted| replace:: :ref:`archive-components-restricted`
.. |universe| replace:: :ref:`archive-components-universe`
.. |multiverse| replace:: :ref:`archive-components-multiverse`

.. _devel-release: http://archive.ubuntu.com/ubuntu/dists/devel/
.. |devel-release| replace:: ``devel-release``
.. _devel-updates: http://archive.ubuntu.com/ubuntu/dists/devel-updates/
.. |devel-updates| replace:: ``devel-updates``
.. _devel-security: http://archive.ubuntu.com/ubuntu/dists/devel-security/
.. |devel-security| replace:: ``devel-security``
.. _devel-proposed: http://archive.ubuntu.com/ubuntu/dists/devel-proposed/
.. |devel-proposed| replace:: ``devel-proposed``
.. _devel-backports: http://archive.ubuntu.com/ubuntu/dists/devel-backports/
.. |devel-backports| replace:: ``devel-backports``
