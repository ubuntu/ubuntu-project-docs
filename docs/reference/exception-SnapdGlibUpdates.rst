This document describes the policy for updating the `snapd-glib
package <https://launchpad.net/ubuntu/+source/snapd-glib>`__ in stable
Ubuntu releases.

`snapd-glib <https://github.com/snapcore/snapd-glib/>`__ is a library to
help client applications to communicate with snapd. It provides
appropriate bindings for applications that use GLib, Qt or GObject
bindings. As the snapd project is continuously updated, snapd-glib is
also continuously updated to enable new features. snapd-glib is designed
to be both API and ABI compatible with older releases so these updates
can be rolled out.

.. _sru_process:

SRU Process
-----------

-  

   -  A new feature is added to snapd and this is updated into Ubuntu
      (`process <https://wiki.ubuntu.com/SnapdUpdates>`__).
   -  Changes are made to snapd-glib with automated unit tests.
   -  Changes are tested on landing using a continuous integration
      system (Travis).
   -  A tagged release of snapd-glib is made - this is manually
      confirmed to be working at release time.
   -  The current development Ubuntu release is updated.
   -  snapd-glib is updated in the Ubuntu development release.
   -  A bug is opened for each release and contains instructions on what
      to smoke test (i.e. the reverse dependencies of snapd-glib).
   -  Bugs are opened for specific features/bugfixes that have been
      backported to stable Ubuntu releases. These bugs contain testing
      instructions as per the `usual SRU <StableReleaseUpdates>`__
      process.
   -  Bugs are confirmed as per standard SRU process.
