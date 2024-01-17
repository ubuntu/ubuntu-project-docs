Background
==========

Open-vmware-tools is a guest package for virtual machines hosted on
VMware. It is a suite of virtualization utilities and drivers to improve
the functionality, user experience and administration of VMware virtual
machines.

As such it is an odd case of being userspace software, even one that is
not tied to real hardware - but it is bound to support virtual hardware.

As such it is often required to have get an updated version of it to
provide platform enablement while being in the lifecycle of a Ubuntu LTS
release.

Process
=======

No less than **<QUESTION: what is the correct time here>** after each
Ubuntu release (to allow widespread testing) the version of
open-vm-tools can be backported from the current Ubuntu release to the
most recent LTS' -updates pocket and any non-LTS stable release in
support.

There should be a single SRU bug tracking the backport. Other bugs may
included in the changelog; they must have test cases and be verified as
normal. It is expected that no packaging changes from the current
release will be required for this backport - any necessary changes
should be highlighted in the SRU bug. Similarly, any packaging changes
from the previous stable version should be called out in the SRU bug.

Verification
~~~~~~~~~~~~

On one hand we want to keep these upload longer in -proposed to give the
few that run canary with -proposed a better chance to speak up. And we
need that time anyway to allow for the following.

Once pre-checks at build have been done, reviews passed and builds are
accepted in proposed the server team reaches out to VMware to coordinate
testing and verification of the uploads.

You'll see updates and confirmation usually by the `QA
team <https://launchpad.net/~vmware-gos-qa>`__ or `their
lead <https://launchpad.net/~yhzou>`__. Those are also the people one
can reach out to if in doubt.

Sometimes we had discussions, other issues found or not all releases
tested, but the server team communicates with VMware until all we need
is in place.

.. _sru_bug_template:

SRU Bug Template
~~~~~~~~~~~~~~~~

::

   Title: Backport open-vm-tools version $version to $release, $release

   [ Impact ]

   * Without SRUing the never version users get issues running on more
      recent hypervisors.

   * This is not backporting a single fix, nor an MRE, but backporting the
      version of a latter Ubuntu release for platform enablement.

   * See https://wiki.ubuntu.com/OpenVMToolsUpdates for more details

   [ Test Plan ]

   * VMWare QA Team does the qualification of these uploads as we don't have
      a matrix of Host versions for that around. Once made available in -proposed
      and passing build time tests the Server team will reach out to VMware to to
      run their verification harness against the new build and confirming that
      with a statement on the bug.

   * As an additional safety net we want to keep this in -proposed longer
      than usual, suggesting >=14 days.

   [ Where problems could occur ]

   * It is a full new version which might contain new issues, but also
      new fixes and we've had cases where this brought CVE coverage before
      we needed backports for those. Still, worst you'd expect all that you
      expect on a release-upgrade like deprecated features gone, handling
      configuration differently or in general behaving differently by adding
      (even wanted) new features.
      Gladly the toolset has proven to be very stable at all that.

   [ Other Info ]

   * Mostly regressions seen on those backports would be the same as seen on
      an upgrade to a new Ubuntu version with the new version of open-vm-tools.
      Hence, unless other reasons like a former delay or an urgent need
      cause a change, we try to do this early in the Ubuntu cycle backporting
      the version released just recently.
      For example the version that will go out with 24.10 is expected to be
      proposed for 24.04 shortly, but after 24.10 is released so that we'd have
      a chance to pick those regression reports up.

.. _past_context:

Past Context
============

Ambiguity
---------

The server team does many MREs and therefore sometimes it happened that
these uploads were called an MRE, it is not. This is a platform
enablement SRU upload under the condition of `"other safe cases" sub
section
2 <https://wiki.ubuntu.com/StableReleaseUpdates#Other_safe_cases>`__:

| ``"... is also applicable as they have a low potential for regressing existing``
| ``installations but a high potential for improving the user experience,``
| ``particularly for Long Term Support releases ... For Long Term Support releases``
| ``we regularly want to enable new hardware. Such changes are appropriate provided``
| ``that we can ensure not to affect upgrades on existing hardware."``

History
-------

Before 2018 we released with the open-vm-tools version that we had in
-release at the time and that was it. But users every now and then
complained in chat or in bugs that they'd need a newer one without a
good path to resolve.

The reason for that was that while we understood the need we didn't have
the insight or capacity to verify this across a variety of VMware
versions nor to use any of the advanced features.

But then in 2018 we went the extra mile sorting out how we could adress
the problem outlined for the better of our users.

The bug that changed this from "we can't" to, "let us help our users"
was
`1741390 <https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1741390>`__
back in 2018. There we had a concrete example of the lack of such an
update breaking users.

Resolution
----------

After discussion of the risks and if this would even qualify as an SRU
Steve was so kind to share his
`expertise <https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1741390/comments/6>`__:

| ``"With my SRU team hat on, I will say that open-vm-tools clearly falls into``
| ``the class of packages that have a "platform enablement" (new "hardware``
| ``enablement") exception to the usual bugfix-only rule.``

| ``Care must of course still be taken to test the updates and avoid``
| ``regressions, but in cases where the package must be updated from upstream to``
| ``maintain compatibility with the moving target of the OS's substrate (whether``
| ``that's hardware, or a cloud platform, or a VM platform), the requirement to``
| ``selectively cherry-pick bugfixes is waived."``

So it would be a valid SRU, but what was left to resolve, was how to
ensure to avoid regressions. Back then we reached out to VMware and cam
to an agreement that VMware would have the set of different hypervisor
versions and the ability to run tests using all kind of VMware features.
This coordination was negotiated back then under Dean H > David B >
Christian E, wow how time has passed.

OTOH we agreed to not do this too often (roughly once per cycle) to be
able to allow each party to do proper deep testing. Furthermore we
limited (unless there are very special reasons) to limit this to LTS-1.
Hence you see the updates in 2018 covering Xenial, but those in 2019
only gone to Bionic. The users should have an LTS available that allows
them to use the latest VMware based virtualization. The effort to do
more was left open once there is a reasonable need for that.

Bonus: Furthermore, not required for this process, but related: the
engineers related to the open-vm-tools package at VMware help us by
monitoring (or reporting) bug on launchpad - they have kept this active
even with responsible people changing from Oliver Kurth to John Wolfe.

.. _track_record:

Track Record
------------

Since the agreement above we have done this on a regular pace, but
lacked the more formal documentation and agreement (= this page) until
now. But to raise confidence, let us refer to all the backports created
and verified in the same style that have so far been done and not cause
a reported regression.

-  2018, 10.2.0 to X,A:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1741390
-  2018, 10.3.0 to B:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1784638
-  2019, 10.3.5 to B,C:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1813944
-  2019: 10.3.10 to B,C:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1822204
-  2019: 11.0.0 to B,D,E:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1844834
-  2020: 11.0.5 to B,E:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1868012
-  2020: 11.1.0 to F:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1877672
-  2020: 11.1.5 to F:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1892266
-  2021: 11.2.5 to F,G:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1911831
-  2021: 11.3.0 to F,H:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1933143
-  2022: 12.1.0 to J:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1975767
-  2022: 12.1.5 to J,K,L:
   https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/1998558
-  2023 was stalled on misunderstanding which led to this very document
   to clarify
   (https://bugs.launchpad.net/ubuntu/+source/open-vm-tools/+bug/2028420)
