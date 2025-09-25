.. _how-to-make-changes-to-a-package:

How to make changes to a package
================================

This tutorial goes through the process of adding a patch to a package in Ubuntu. Specifically, we add a command-line option to the :command:`hello` command, which greets a user using their username. This covers topics like :command:`git-ubuntu`, :command:`quilt`, and changelogs.


Getting the tools
-----------------

We are using a :command:`git-ubuntu` workflow. Install it with :command:`snap`:

.. prompt:: none $ auto

    $ sudo snap install --classic git-ubuntu

Once we have :command:`git-ubuntu` installed, use it to fetch the source code for the :pkg:`hello` package in Ubuntu:

.. prompt:: none $ auto

    $ git-ubuntu clone hello
    $ cd hello/

We are using some tools from the :pkg:`ubuntu-dev-tools` package. Install it with:

.. prompt:: none $ auto

    $ sudo apt install -y ubuntu-dev-tools


Understanding the package
-------------------------

Initially, we have the ``ubuntu/devel`` branch checked out. At the time of writing this tutorial, the development series is ``plucky``, so the ``ubuntu/devel`` branch is in line with the ``plucky`` version.

Let's explore the packaging we are dealing with. In the :file:`debian` directory, there are files like :file:`changelog`, :file:`rules`, :file:`control`, and more. Everything outside of the :file:`debian` directory is from the original upstream source. In :file:`debian/source/format`, we see:

.. code-block:: text

    3.0 (quilt)

This means that, like most packages, this package uses the :command:`quilt` tool to manage patches to the upstream source code. So, even though we are using Git to track our changes to the *packaging*, we need to use a :command:`quilt` patch to maintain the changes required for our new command-line option.

In particular, instead of ending up with a Git commit that modifies the upstream source code directly, our commit adds a new file, :file:`debian/patches/add-username-command-line-option.patch`, which contains the patch to apply to the upstream source code.


.. _creating-a-patch-with-quilt:

Creating a patch with :command:`quilt`
--------------------------------------

First, create the new patch file using :command:`quilt`:

.. prompt:: none $ auto

    $ QUILT_PATCHES=debian/patches quilt new add-username-command-line-option.patch
    Patch add-username-command-line-option.patch is now on top

This should create a new, empty file: :file:`debian/patches/add-username-command-line-option.patch`. And it adds a corresponding entry to the :file:`debian/patches/series` file. Once that is done, start writing the patch. For each source file that is modified by our patch, we need to tell :command:`quilt` about it. In this case:

.. prompt:: none $ auto

    $ quilt add src/hello.c

After that, edit the source normally using our favorite text editor. To see our progress, use the usual Git tools to see the diff. So, after adding the new command line flag, the diff might look like:

.. code-block:: diff

    $ git diff -- src/hello.c
    diff --git a/src/hello.c b/src/hello.c
    index 453962f..f1ccf0a 100644
    --- a/src/hello.c
    +++ b/src/hello.c
    @@ -23,6 +23,10 @@
     #include "error.h"
     #include "progname.h"
     #include "xalloc.h"
    +#include "unistd.h"
    +#include "sys/types.h"
    +#include "pwd.h"
    +#include "limits.h"

     static const struct option longopts[] = {
       {"greeting", required_argument, NULL, 'g'},
    @@ -44,6 +48,8 @@ main (int argc, char *argv[])
       const char *greeting_msg;
       wchar_t *mb_greeting;
       size_t len;
    +  struct passwd *pwd = NULL;
    +  char user_greeting[sizeof("hello, !") + LOGIN_NAME_MAX] = {};

       set_program_name (argv[0]);

    @@ -65,7 +71,7 @@ main (int argc, char *argv[])
          This is implemented in the Gnulib module "closeout".  */
       atexit (close_stdout);

    -  while ((optc = getopt_long (argc, argv, "g:htv", longopts, NULL)) != -1)
    +  while ((optc = getopt_long (argc, argv, "g:htvu", longopts, NULL)) != -1)
         switch (optc)
           {
            /* --help and --version exit immediately, per GNU coding standards.  */
    @@ -83,6 +89,15 @@ main (int argc, char *argv[])
           case 't':
            greeting_msg = _("hello, world");
            break;
    +      case 'u':
    +        errno = 0;
    +        pwd = getpwuid(geteuid());
    +        if (!pwd)
    +          error (EXIT_FAILURE, errno, _("failed to get user name"));
    +
    +        snprintf(user_greeting, sizeof(user_greeting), "hello, %s!", pwd->pw_name);
    +        greeting_msg = _(user_greeting);
    +        break;
           default:
            lose = 1;
            break;

To save these changes in our quilt patch, we need to *refresh* the patch:

.. prompt:: none $ auto

    $ quilt refresh -p ab --no-timestamps --no-index

It is good practice to add :ref:`DEP-3 headers <dep-3-patch-file-headers>` to patches to add additional context, such as the origin, author, and related bugs. The :command:`quilt` tool has a helper for this:

.. prompt:: none $ auto

    $ quilt header -e --dep3

This opens a text editor with pre-populated text: ::

    Description: <short description, required>
     <long description that can span multiple lines, optional>
    Author: <name and email of author, optional>
    Origin: <upstream|backport|vendor|other>, <URL, required except if Author is present>
    Bug: <URL to the upstream bug report if any, implies patch has been forwarded, optional>
    Bug-<Vendor>: <URL to the vendor bug report if any, optional>
    Forwarded: <URL|no|not-needed, useless if you have a Bug field, optional>
    Applied-Upstream: <version|URL|commit, identifies patches merged upstream, optional>
    Reviewed-by: <name and email of a reviewer, optional>
    Last-Update: 2025-04-23 <YYYY-MM-DD, last update of the meta-information, optional>
    ---
    This patch header follows DEP-3: http://dep.debian.net/deps/dep3/

Not everything here needs to be filled in. In this case, our headers might look like: ::

    Description: Add -u command line option to hello
     This command line option adds a username-specific greeting. E.g.,
     $ hello -u
     hello, user123!
    Author: Nick Rosbrook <enr0n@ubuntu.com>
    Forwarded: no, Ubuntu only
    Last-Update: 2025-04-23 
    ---
    This patch header follows DEP-3: http://dep.debian.net/deps/dep3/

Our final patch should look something like:

.. code-block:: diff

    Description: Add -u command line option to hello
     This command line option adds a username-specific greeting. E.g.,
     $ hello -u
     hello, user123!
    Author: Nick Rosbrook <enr0n@ubuntu.com>
    Forwarded: no, Ubuntu only
    Last-Update: 2025-04-23
    ---
    This patch header follows DEP-3: http://dep.debian.net/deps/dep3/
    --- a/src/hello.c
    +++ b/src/hello.c
    @@ -23,6 +23,10 @@
     #include "error.h"
     #include "progname.h"
     #include "xalloc.h"
    +#include "unistd.h"
    +#include "sys/types.h"
    +#include "pwd.h"
    +#include "limits.h"

     static const struct option longopts[] = {
       {"greeting", required_argument, NULL, 'g'},
    @@ -44,6 +48,8 @@
       const char *greeting_msg;
       wchar_t *mb_greeting;
       size_t len;
    +  struct passwd *pwd = NULL;
    +  char user_greeting[sizeof("hello, !") + LOGIN_NAME_MAX] = {};

       set_program_name (argv[0]);

    @@ -65,7 +71,7 @@
          This is implemented in the Gnulib module "closeout".  */
       atexit (close_stdout);

    -  while ((optc = getopt_long (argc, argv, "g:htv", longopts, NULL)) != -1)
    +  while ((optc = getopt_long (argc, argv, "g:htvu", longopts, NULL)) != -1)
         switch (optc)
           {
      /* --help and --version exit immediately, per GNU coding standards.  */
    @@ -83,6 +89,15 @@
           case 't':
      greeting_msg = _("hello, world");
      break;
    +      case 'u':
    +       errno = 0;
    +       pwd = getpwuid(geteuid());
    +       if (!pwd)
    +         error (EXIT_FAILURE, errno, _("failed to get user name"));
    +
    +       snprintf(user_greeting, sizeof(user_greeting), "hello, %s!", pwd->pw_name);
    +       greeting_msg = _(user_greeting);
    +       break;
           default:
      lose = 1;
      break;

The patch is currently applied in the working directory.

* To un-apply: :command:`quilt pop -a`
* To apply again: :command:`quilt push -a`


.. _committing-the-changes:

Committing the changes
----------------------

Now that we have created our patch file, track the changes in Git (see also :ref:`how-to-commit-changes` for detailed guidance on commit message and changelog formatting). Add the new patch file (and in this case, the newly created :file:`debian/patches/series` file) to the Git index and commit the change:

.. prompt:: none $ auto

    $ git add debian/patches/
    $ git commit -m "debian/patches: add a new -u command line option to hello"

Next, some housekeeping changes:

#. Make sure that the ``Maintainer:`` field in :file:`debian/control` is set correctly.

#. Add a new entry to :file:`debian/changelog` explaining our changes and incrementing the package version number.

To update the maintainer field, use the :command:`update-maintainer` tool from the :pkg:`ubuntu-dev-tools` package. In this case, the field is already set correctly, so we should see:

.. prompt:: none $ auto

    $ update-maintainer
    The Maintainer email is set to an ubuntu.com address. Doing nothing.

If a change was made, commit that change with:

.. prompt:: none $ auto

    $ git commit -m "update maintainer" -- debian/control


.. _updating-the-changelog:

Updating the changelog
----------------------

Once you have either updated the maintainer, or confirmed that it is already correct, update the changelog. The :command:`dch` tool helps with this. If you run :command:`dch -i`, you see something like this in your text editor: ::

    hello (2.10-3ubuntu1) UNRELEASED; urgency=medium

      *

     -- Nick Rosbrook <enr0n@ubuntu.com>  Tue, 22 Apr 2025 17:03:03 -0400

    hello (2.10-3build2) oracular; urgency=medium

      * No-change rebuild to bump version in oracular.

     -- Marc Deslauriers <marc.deslauriers@ubuntu.com>  Mon, 27 May 2024 07:18:24 -0400

    hello (2.10-3build1) noble; urgency=high

      * No change rebuild for 64-bit time_t and frame pointers.

     -- Julian Andres Klode <juliank@ubuntu.com>  Mon, 08 Apr 2024 17:58:52 +0200

     [...SNIP...]

The :command:`dch` tool has done a few things:

1. Created a new empty changelog entry.
2. Set the author line using your name, email, and the current date and time.
3. Updated the package version number to ``2.10-3ubuntu1``.
4. Set the release name to ``UNRELEASED``.

Our job now is to fill in the entry and explain our changes. In this case, write something like: ::

    hello (2.10-3ubuntu1) plucky; urgency=medium

      * debian/patches: add a new -u command line option to hello

     -- Nick Rosbrook <enr0n@ubuntu.com>  Tue, 22 Apr 2025 17:03:03 -0400

Write a short and informative message between the top and bottom lines. This message should include:

- where you made the change, such as file or component
- what the change does
- why you made the change
- link to the Launchpad bug or mailing list discussion, if available

An example template of the changelog entry is as follows:

.. code-block:: text

    my-package <version> UNRELEASED; urgency=low

    * fix crash in system monitor when reading temperature sensors
        - updated <script.py> to handle missing sensor values
        - added error handling to prevent crashes

    -- name <name@example.com>  Tue, 13 May 2025 15:42:10 +0000

Reference Launchpad bugs like this:

.. code-block:: text

    LP: #<bug-number>

This ensures the bug is closed automatically when the fix is uploaded.

Once you are happy with the changelog entry, commit the updated file:

.. prompt:: none $ auto

    $ git commit -m "update changelog" -- debian/changelog

At this point, we should have two (or three if :command:`update-maintainer` was needed) commits: one adding our new patch, and another updating the changelog:

.. prompt:: none $ auto

    $ git log
    commit a62e1590cc6a12925c8fe9bce49d9b7f5834468e (HEAD -> ubuntu/devel)
    Author: Nick Rosbrook <enr0n@ubuntu.com>
    Date:   Wed Apr 23 10:04:32 2025 -0400

        update changelog

    commit d6ef1607ce6163e6a611c591e94f478c2c06a35a
    Author: Nick Rosbrook <enr0n@ubuntu.com>
    Date:   Tue Apr 22 16:24:39 2025 -0400

        debian/patches: add a new -u command line option to hello

    commit fd73db6d7406ee1fb8512a5b54c259f3b3368eab (tag: pkg/import/2.10-3build2, pkg/ubuntu/plucky-devel, pkg/ubuntu/plucky, pkg/ubuntu/oracular-proposed, pkg/ubuntu/oracular-devel, pkg/ubuntu/oracular, pkg/ubuntu/devel, pkg/HEAD)
    Author: Marc Deslauriers <marc.deslauriers@ubuntu.com>
    Date:   Mon May 27 07:18:24 2024 -0400

        2.10-3build2 (patches unapplied)

        Imported using git-ubuntu import.

    Notes (changelog):
          * No-change rebuild to bump version in oracular.

And that's it! We have successfully:

* Added a new patch to this package.
* Documented our change.
* Prepared the package for its next upload to the Ubuntu archive.


Next steps
----------

From here, there are many options for testing our patch before proposing the change in a merge proposal:

* Build and test the package locally using :command:`sbuild` and :command:`autopkgtest`.
* Upload to a PPA and test from there.

Once you feel confident that the patch is working correctly, open a merge proposal and request :ref:`sponsorship` for your change.


Further reading
---------------

* :ref:`how-to-commit-changes`
