.. _how-to-propose-changes:

How to propose changes
======================

This guide walks through the process for proposing changes to Ubuntu. When you find a problem, obtain the code, work on a solution, test the fix, push your changes to :term:`Launchpad`, and request a review and merge.

.. attention::

    There is information placed within angle brackets in this guide. Ensure you replace them with the appropriate values. For example, replace ``<package-name>`` with the name of the package you are working on.

Find a bug to fix
-----------------

Start by identifying an issue to work on. This can be a bug you encountered while using an application, a problem described in a bug report, or a known issue in the Ubuntu community.

You can also explore known bugs using these resources:

- `Bite-size bugs on Launchpad <https://bugs.launchpad.net/ubuntu/+bugs?field.tag=bitesize>`_: Small, well-scoped bugs that are great for new contributors.
- `One hundred paper cuts <https://launchpad.net/hundredpapercuts>`_: Minor bugs that negatively affect the user experience.
- `Launchpad bug tracker <https://bugs.launchpad.net/ubuntu>`_ and `Debian's bug trackers <https://www.debian.org/Bugs/>`_: Issue reports for Ubuntu and Debian packages.


Evaluate the bug report
-----------------------

Once you find a bug report on Launchpad that you want to work on, evaluate the bug.

Read the bug description carefully and look for:

.. TODO link UMH

- steps to reproduce the problem
- crash logs or terminal output
- details about the affected version and package
- attached ``.crash`` files or `Apport crash files <https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/PackageFixing.md#evaluate-the-bug>`_

For example, the `Postconf segfaults every 5 minutes <https://bugs.launchpad.net/ubuntu/+source/postfix/+bug/1753470>`_ bug report shows a segmentation fault in ``postconf`` on Ubuntu 18.04. It includes logs from ``/var/log/kern.log``, shell commands that reproduce the issue, and metadata about the system environment. This information helps confirm whether the bug still affects current versions and if the report is complete.

If the bug includes a ``.crash`` file, extract and inspect the stack trace. Use the information to better understand where the failure occurred in the code.

.. TODO link UMH

For more details, see `Evaluate the bug <https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/PackageFixing.md#evaluate-the-bug>`_.

Identify the source package
---------------------------

After selecting a bug to fix, identify the source package that contains the code related to the issue.

Start by identifying the name of the binary package. If you know the path or part of the filename of the affected program, run:

.. code-block:: none

    apt-file find <filename-or-path>

.. note::

    Replace ``<filename-or-path>`` with either the full path or part of the filename.

    For example, both of the following work:

    .. code-block:: none

        apt-file find /usr/games/bumprace
        apt-file find bumprace

Running the command returns an output similar to:

.. code-block:: none

    bumprace: /usr/games/bumprace

In the preceding output, the part before the colon is the name of the binary package.

After identifying the name of the binary package, the next step is to find the source package. Use the following command:

.. code-block:: none

    apt show <binary-package-name>

For example:

.. code-block:: none

    apt show bumprace

Check the output for the ``Source`` field. This field indicates the name of the source package.

It's possible for the name of a binary package to be the same as its source package. If this is the case, the ``apt show <binary-package-name>`` command doesn't display the ``Source`` field in its output. In such cases, assume the source package name is the same as the binary package name.

Check if the bug has been fixed
-------------------------------

Once you identify the source package, make sure the issue still exists. A fix may already exist in a newer Ubuntu release, in Debian, or upstream. Checking first saves time and avoids duplicate work.

Follow the steps in the following subsections to check whether the problem has already been addressed.

Check if the bug is fixed in a newer Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``rmadison`` to review the versions of the package available across Ubuntu releases.

.. code-block:: none

    rmadison <package-name>

This shows which versions are available in different Ubuntu series. Look for a newer version than the one you are using. If a fix was introduced in a later version, check the changelog or commit history to verify.

To review changes, clone the package with :command:`gitubuntu`:

.. code-block:: none

    git-ubuntu clone postfix postfix
    cd postfix
    git log -b pkg/ubuntu/<ubuntu-series>

Look through the commit messages and patch files to identify if the issue has been resolved.

Check if the bug is fixed in Debian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Debian is a key source for Ubuntu packages. Search for bug reports or patches applied there.

First, check Debian’s bug tracker using the URL ``https://bugs.debian.org/src:<package-name>``.

To inspect changes in more detail, find the source repository used by Debian. You can do this in a few ways:

- Use ``debcheckout``:

    .. code-block:: none

        debcheckout <package-name>
        cd <package-name>
        git log

- Look for the ``Vcs-Git`` and ``Vcs-Browser`` fields from the ``apt showsrc`` command output. These point to the package's source code repository and its web interface:

    .. code-block:: none

        apt showsrc --only-source <package-name>

    Look for commit messages that describe fixes relevant to your issue. If a bug number is referenced, open the link and review the context.

Check if the bug is fixed upstream
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the problem originates from the software itself and not the package, investigate :term:`upstream`. Each project has its own bug tracker and code repository.

To find the upstream project:

- search the package homepage listed by running the command ``apt show <package>``
- look up the project through web search
- check the metadata in the package description or Debian tracker

Once you find the upstream repository:

1. look through open and closed issues
#. search the commit history for relevant fixes
#. clone the upstream Git repository if available and inspect the logs

If upstream has resolved the problem, consider if that version has reached Debian or Ubuntu. If not, you may propose packaging the new version or backporting the patch.

Offer to help
-------------

Once you confirm the issue still exists, a bug report is open, and no one is working on it, you can offer to help. This step signals your interest in resolving the issue and helps prevent duplicated efforts.

Start by commenting on the bug report in Launchpad. Let others know that you intend to work on the issue. Include any relevant details you have, such as:

- when and how the bug occurred
- how you plan to fix the issue, or what you've tried so far
- any testing you’ve done or plan to do

If the bug doesn't yet exist in Launchpad, create a new bug report. Provide a clear title and description. Explain how the issue can be reproduced, and add logs or screenshots if helpful.

Get the source code
-------------------

Once you're assigned to the bug, get the source code for the affected package. You can get the source code using any of these four methods:

- ``git-ubuntu``
- ``pull-pkg``
- ``apt-get source``
- ``dget``

For detailed instructions on using these methods to get the source code, see :ref:`get-package-source`.

Create a patch to fix the issue
-------------------------------

You may need to create a patch to make changes to a package. Start by checking where your changes are located. If your changes are only within the ``debian/`` directory, for example, in ``debian/control``, you don't need to create a patch. However, if you changed upstream source code, that is anything outside ``debian/``, then you must create a patch and include it in ``debian/patches``.

There are two main methods for creating patches for Ubuntu packages. The method to choose depends on the workflow that the package source uses:

.. TODO UMH dupl.?

- If the package uses :term:`quilt`, use the :manpage:`quilt(1)` tool to create and manage patches. To learn how to create a patch using ``quilt``, see :ref:`creating-a-patch-with-quilt`.
- If the package is maintained using ``git-ubuntu``, commit your changes directly in Git.

.. TODO how do i know?


Documenting the fix
-------------------

It’s important to document your changes, so future developers can understand your reasoning and assumptions without having to guess.

Explain your changes in the ``debian/changelog`` file. This file tracks every change uploaded to Ubuntu or Debian, and future developers rely on it to understand what changed, where it happened, and why.

See :ref:`updating-the-changelog` for details.


Testing the fix
---------------

Run package tests to check that your change doesn't introduce regressions. Ubuntu uses :term:`autopkgtest` to automate this process. You can run tests in several ways: 

- in a local virtual machine (VM)
- through a :term:`Personal Package Archive` (PPA) on Launchpad
- in a container

For local testing, use a VM or container. The `autopkgtest` tool builds test images and runs the tests in an isolated environment. Use this method when you want to debug failures or verify changes before uploading to a PPA. If your testbed needs to reboot or be isolated, use a VM or container as defined in the package’s ``debian/tests/control`` file.

You can also use PPA-based method whenever possible. It produces results closest to what Launchpad runs for archive packages. After uploading your package to a PPA and building it, trigger tests using the ``PPA`` tool from ``ppa-dev-tools``. You need special permissions to launch these tests. Ask for help in the ``#ubuntu-devel`` IRC channel if needed.

.. TODO UMH link

To learn how to set up and run these test methods, see `Running package tests <https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/PackageTests.md>`_.


Submitting the fix
------------------

Once you've documented and saved your changes in a new changelog entry, run ``debuild``:

.. code-block:: none

    debuild -S -d

.. TODO UMH link

The command signs the changes in the file. After that, submit your fix by opening a merge proposal. For details on how to do this, see the section on `Merge proposal <https://github.com/canonical/ubuntu-maintainers-handbook/blob/main/MergeProposal.md>`_ in the Ubuntu Maintainer's Handbook.

In many cases, Debian would benefit from the fix as well. Submitting to Debian is considered best practice because it ensures that a wider audience receives the fix. You can submit the fix to Debian by running:

.. code-block:: none

    submittodebian

Running the preceding command walks you through a series of steps to ensure the bug report ends up in the correct place. Be sure to review the :term:`diff` again to confirm it doesn’t include unrelated changes you made earlier.

Also, ensure you add a clear description of the fix to the inclusion request.

If everything goes well, you get an email from Debian's bug tracking system with more information. This may take a few minutes.

Sometimes it’s best to get your fix included in Debian first. It then flows downstream to Ubuntu automatically. In that case, skip the following steps.

For security updates or updates to stable releases, the fix might already be in Debian or intentionally ignored. In these cases, follow the process described here.

.. TODO link to the article on Security and stable release updates.

If you're doing a security or stable release update, read the article on Security and stable release updates.

You can also follow this process when dealing with Ubuntu-only packages that don’t build correctly, or with issues that affect Ubuntu specifically.

If you're submitting your fix to Ubuntu, generate a ``debdiff``. A ``debdiff`` shows the difference between two Debian source packages. The command comes from the ``devscripts`` package. For full details, see the manual page for :manpage:`debdiff(1)`.

To compare two source packages, use the ``.dsc`` files as arguments:

.. code-block:: none

    debdiff <package_name>_1.0-1.dsc <package_name>_1.0-1ubuntu1.dsc

Compare the original ``.dsc`` file with the one you generated after making your changes. This generates a patch that your sponsor can then apply locally by using ``patch -p1 < /path/to/debdiff``. In this case, redirect the output of the ``debdiff`` command to a file and attach it to the bug report:

.. code-block:: none

    debdiff <package_name>_1.0-1.dsc <package_name>_1.0-1ubuntu1.dsc > 1-1.0-1ubuntu1.debdiff

The format of the filename shown in ``1-1.0-1ubuntu1.debdiff`` has some meaning:

1. ``1-`` tells the sponsor that this is the first revision of your patch.
#. ``1.0-1ubuntu1`` shows the version you are working on.
#. ``.debdiff`` makes it clear that it’s a ``debdiff`` file.

While this format is optional, it works well and you're encouraged to use it.

Next, go to the bug report on Launchpad. Log in and click **Add attachment or patch** near the comment box. Attach the ``debdiff`` and leave a comment. Explain how the patch can be applied and what testing you've done.

Here’s an example:

.. code-block:: text

    This is a debdiff for Artful applicable to 1.0-1. I built this in pbuilder and it builds successfully, and I installed it, the patch works as intended.

Mark the attachment as a patch. This notifies the Ubuntu Sponsors team. Subscribe to the bug report to get updates.

You usually get a review within a few hours to a few weeks. If it takes too long, join ``#ubuntu-motu`` on IRC and ask for help. Stay in the channel until someone responds and guides you through your next steps.

After the review, the sponsor might upload your fix, request changes, or reject it. If changes are needed, follow the same steps and submit a new ``debdiff`` to the bug. If the fix is rejected because it's not a fit for Ubuntu, you might need to send it to Debian instead.

If you have questions, email ``ubuntu-motu@lists.ubuntu.com`` or join ``#ubuntu-motu`` on IRC. There you find people who share your passion for improving open source and making the world better.
