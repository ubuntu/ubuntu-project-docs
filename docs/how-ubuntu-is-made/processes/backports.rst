.. _backports:

Backports
=========

Backporting allows for making new functionality (that is not connected to a critical bug fix) available in a stable release. For these scenarios, there are two options:

* :ref:`Uploading to a PPA <upload-packages-to-a-ppa>`.
* Preparing a backport.


Official Ubuntu Backports
-------------------------

.. TODO: Add link to 'Security Update'

The Backports Project is a means to provide new features to users. Because of the inherent stability risks in backporting packages, users do not get backported packages without some explicit action on their part. This generally makes backports an inappropriate avenue for fixing bugs. If a package in an Ubuntu release has a bug, it should be fixed either through the Security Update or the :ref:`stable-release-updates` process, as appropriate.

All packages that are to be backported to a stable release must be built and tested on the given stable release. Use the :command:`pbuilder-dist` tool (from the :pkg:`ubuntu-dev-tools` package) for this.

To report the backport request and get it processed by the Backporters team, use the :command:`requestbackport` tool (also in the :pkg:`ubuntu-dev-tools` package). The tool serves to:

* Determine the intermediate releases that the package needs to be backported to.
* List all reverse-dependencies.
* File the backporting request (Launchpad bug). It also includes a testing checklist in the request.
