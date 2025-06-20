.. _main-inclusion-review-mir:

Main Inclusion Review (MIR)
===========================

.. important::

    Do not confuse the abbreviation :term:`MIR` with the `display server <https://mir-server.io/>`_ Mir.

:term:`Packages <Package>` in :term:`Main` and :term:`Restricted` are officially
maintained, supported and recommended by the :term:`Ubuntu` project.
:term:`Canonical's <Canonical>` support services applies to these packages, 
which include security updates and certain :term:`SLA` guarantees when bugs are reported
and technical support is requested.

Therefore, special consideration is necessary before adding new packages
to Main or Restricted. The Ubuntu :term:`MIR Team` reviews packages for promotion:

- from :term:`Universe` to :term:`Main`, or
- from :term:`Multiverse` to :term:`Restricted`.

This review process is called **Main Inclusion Review (MIR)**.

Submit a package for Main Inclusion Review
------------------------------------------

The `Main Inclusion Review documentation <MainInclusionReviewDocumentation_>`_
by the MIR team provides instructions on how to apply for
:term:`Main Inclusion Review` for a package. The documentation even contains
details of how the application gets reviewed by the MIR team.

.. note::

    The guidelines and review process is constantly evolving. Therefore you
    should re-read the MIR documentation even if you have submitted a package
    for Main Inclusion Review in the past.

    The MIR documentation is also a living document. External contributions,
    suggestions, discussions or questions about the process are always welcome.

MIR team weekly meeting
-----------------------

The MIR team holds weekly meetings every Tuesday at 16:30 CET on the
:term:`IRC` server ``irc.libera.chat`` in the ``#ubuntu-meeting`` channel.
You can follow these `instructions <https://libera.chat/guides/connect>`_ on
how to connect to ``irc.libera.chat``.

The purpose of the meeting is:

- to distribute the workload fairly between the members of the MIR team
- to provide a timely response to reporters of MIR applications
- detection and discussion of any current or complex cases

You should attend these meetings if you submit an MIR request until it is approved or rejected.

Usually, the amount of MIR requests increases during the six-month development
period of a new Ubuntu release. Especially right before the various feature freezes 
(see :ref:`ubuntu-development-process`), Ubuntu developers submit MIR requests
they have been working on before they have to submit an exception request. As a result,
the meetings tend to be quieter, and response times to MIR requests are, on average,
faster after the release of a new Ubuntu version.

Resources
---------

- `Main Inclusion Review documentation <MainInclusionReviewDocumentation_>`_ by the MIR team
    - `MIR process overview <https://github.com/canonical/ubuntu-mir#process-states>`_
    - `MIR application template <https://github.com/canonical/ubuntu-mir#main-inclusion-requirements>`_
    - `Helper tools <https://github.com/canonical/ubuntu-mir#tools>`_
    - `Bug lists <https://github.com/canonical/ubuntu-mir#bug-lists>`_
    - `Pull requests <https://github.com/canonical/ubuntu-mir/pulls>`_
    - `Issues <https://github.com/canonical/ubuntu-mir/issues>`_
- MIR team on :term:`Launchpad`: |MainInclusionReviewTeamLaunchpadGroup|_

.. _MainInclusionReviewDocumentation: https://github.com/canonical/ubuntu-mir
.. _MainInclusionReviewTeamLaunchpadGroup: https://launchpad.net/~ubuntu-mir
.. |MainInclusionReviewTeamLaunchpadGroup| replace:: ``~ubuntu-mir`` 
