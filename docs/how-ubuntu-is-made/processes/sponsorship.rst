.. _sponsorship:

Sponsorship
===========

Sponsorship is a process that allows developers without upload rights to submit their patches or new packages for review. If approved, an authorized developer will upload the changes on their behalf.


When to request sponsorship
---------------------------

Since upload rights are carefully managed to ensure system stability and security, new contributors don't have them. So if you don't have upload rights, you can request sponsorship in the following situations:

- Making changes to existing packages or incremental updates.
- Submitting security updates or bug fixes.
- Introducing new packages to Ubuntu.


Requesting sponsorship
----------------------

To request sponsorship, follow these steps:

1. `File an Ubuntu bug in Launchpad <https://bugs.launchpad.net/ubuntu/+filebug>`_ or follow up on an existing one.
#. Add the necessary files, such as patches or ``.diff.gz`` files, according to the package's requirements. If the change is a patch, follow the patch tagging guidelines. For security updates, follow the security update packaging guidelines described in `Packaging <https://wiki.ubuntu.com/SecurityTeam/UpdatePreparation#Packaging>`_.
#. Link your changes to the bug. See `Seeking Sponsorship <https://wiki.ubuntu.com/DistributedDevelopment/Documentation/SeekingSponsorship>`_.
#. Subscribe ``ubuntu-sponsors`` or ``ubuntu-security-sponsors`` to the bug.


Sponsoring a patch
------------------

Members of the :term:`Ubuntu Sponsors` and :term:`Ubuntu Security Sponsors` teams have the right to sponsor patches or new packages. If you are interested in sponsoring, you can apply to join these teams.


Responding to feedback from sponsors
------------------------------------

If a sponsor reviews your changes and requests further modifications, make the modifications to the branch you were working on, then commit them by running:

.. code-block:: none

    $ bzr commit

Now, push your modifications to :term:`Launchpad`. Since ``bzr`` remembers the previous push location, you can run:

.. code-block:: none

    $ bzr push

After pushing your modifications, reply to the sponsor's request explaining the modifications you made and request a re-review. You can also respond directly on the merge proposal page in Launchpad.
