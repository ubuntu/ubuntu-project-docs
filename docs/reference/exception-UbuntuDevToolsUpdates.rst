This document describes the policy for updating the ubuntu-dev-tools
package in a stable release.

\`ubuntu-dev-tools\` is a package providing a collection of tools
defining the standard experience for developers *of* Ubuntu. While
Ubuntu developers are encouraged to run ("dogfood") the unreleased devel
series on their systems, not all Ubuntu developers do so, and in any
case may have need for access to the tooling from diverse systems. It is
therefore important that we provide the same developer experience across
all Ubuntu releases. Having out-of-date tooling in stable Ubuntu
releases means inconsistency with Ubuntu developer documentation; or, if
the documentation is held back, it prevents updating documentation to
take advantage of \`ubuntu-dev-tools\` improvements. The
ubuntu-dev-tools package has stagnated for many years prior to this as a
result, as Ubuntu developers find (poor) alternative methods for
distributing new tools.

Because the purpose of the \`ubuntu-dev-tools\` package is to support
developers of Ubuntu, the risk of an SRU regression that impacts
production use by users is small and therefore the threshold for SRUs
should also be lower. The greatest risk of user-affecting regression is
to the tools \`mk-sbuild\` and \`pull-\*\` which are useful outside of
an Ubuntu development context.

.. _qa_process:

QA Process
----------

The \`ubuntu-dev-tools\` package has an autopkgtest covering the
\`ubuntutools\` python library included and used by those tools in the
package which are implemented in python. This provides some, but by no
means complete, CI coverage.

The SRUs will be backports of the versions of the package in the devel
series. Since many Ubuntu developers run the devel series, we should get
organic feedback about regressions there, before an SRU process
completes. The SRU verification process must include checking for new
bug reports at
https://bugs.launchpad.net/ubuntu/+source/ubuntu-dev-tools/+bugs?orderby=-id&start=0.

The primary risk of regression in SRU will come from changes to
interfaces to other packages, whose versions will differ across Ubuntu
series. Changes to how \`ubuntu-dev-tools\` interfaces with other
packages (commandline arguments, etc) must be called out in the SRU bug
and test cases provided; see the template below.

While the SRU process normally tries to preserve compatibility, SRUs of
\`ubuntu-dev-tools\` \```may``\` break interfaces, up to and including
the removal of commands no longer considered appropriate for Ubuntu
development. Care should be taken when deprecating interfaces, but this
should be considered out of scope of the SRU process for this package.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. The one bug should have the
following:

-  

   -  The SRU should be requested per the StableReleaseUpdates
      documented process
   -  The template at the end of this document should be used and all
      ‘TODO’ filled out
   -  Any packaging changes (e.g. a dependency changes) need to be
      stated
   -  If any manual testing occurs it should also be documented.

.. _sru_template:

SRU Template
------------

::

   == Begin SRU Template ==
   [Impact]
   This release sports both bug-fixes and new features and we would like to
   make sure all of our Ubuntu developers have access to these improvements.

   [Test Case]
   The following development and SRU process was followed:
   https://wiki.ubuntu.com/UbuntuDevToolsUpdates

   autopkgtests will be run for ubuntu-dev-tools as part of the SRU.

   The following changes affect how ubuntu-dev-tools interfaces with other packages:
   <TODO fill out list of changes, including test cases to ensure compatibility with stable releases>

   [Where problems could occur]
   <TODO document any risks, as with any SRU>

   == End SRU Template ==

   <TODO: Paste in change log entry>
