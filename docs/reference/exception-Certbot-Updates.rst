.. _reference-exception-CertbotUpdates:

Certbot Updates
===============

This document describes the policy for updating the Certbot-related
packages (currently the source packages python-acme, python-certbot,
python-certbot-apache and python-certbot-nginx) to new upstream versions
in a stable, supported distro (including LTS releases). This is an
exception to the standard SRU process and includes new features under
the SRU "new features for LTS" exception.

The primary purpose of certbot is to automatically obtain and configure
SSL certificates. Certificates are obtained using the `ACME
protocol <https://en.wikipedia.org/wiki/Automated_Certificate_Management_Environment>`__,
which involves a validation step to "prove" ownership of a configured
domain, for example by configuring a web server to respond with a
correct token when queried using the domain requested. Once obtained,
certbot then configures the web server with the issued certificate.

Certbot is under active development upstream. Feature work generally
involves better integration with the platform (eg. web server daemons).
For example, a recent update enhanced certbot to correctly configure web
server daemons in the case that multiple virtual domains are configured.
As Ubuntu Server LTS is one of the most commonly used platforms for
serving websites, and we want to promote the "HTTPS everywhere"
initiative, it makes sense for the LTS to be updated with these types of
enhancements.

.. _requesting_the_sru:

Requesting the SRU
------------------

The SRU should be done with a single process bug, instead of individual
bug reports for individual bug fixes. See `bug
1640978 <https://launchpad.net/bugs/1640978>`__ for an example. The one
bug should have the following:

-  The SRU should be requested per the
   `StableReleaseUpdates <https://wiki.ubuntu.com/StableReleaseUpdates>`__
   documented process.
-  The template at the end of this document should be used and all
   ‘TODO’ filled out.
-  Major changes should be called out in the SRU template, especially
   where changed behavior is not backwards compatible.

.. _reviewing_the_sru:

Reviewing the SRU
-----------------

In addition to normal SRU review checks, the SRU team should
additionally consider if any major changes are still appropriate to be
automatically updated by Ubuntu users.

.. _qa_process:

Certbot QA Process
------------------

Upstream carries out extensive testing:

-  Nosetest unit tests with coverage for each module between 97% and
   100%; \*test.py in the relevant tree.

-  Integration tests that run Certbot against the current copy of Let's
   Encrypt's serverside boulder codebase. These require docker and are a
   little more involved to run. See tests/boulder_integration.sh for
   instructions.

-  "Compatibility tests" that run the Apache and Nginx plugins against
   corpora of configuration files for those webservers; these live in
   certbot-compatibility-test/

-  Test farm tests, which upstream uses to check that our releases run
   correctly on a wide range of platforms. These spin up Amazon EC2
   instances for numerous OSes and run various tests on them. They live
   in tests/letstest

Packaging includes a dep8 smoke test.

.. _sru_verification_process:

SRU Verification Process
~~~~~~~~~~~~~~~~~~~~~~~~

The following must be verified before a proposed update is marked
verification-done-:

-  Integration tests (performed automatically or manually):

   -  Verify that certbot is correctly able to acquire a certificate
      using ACME.
   -  Verify that certbot is correctly able to configure the apache
      and nginx servers by querying them over HTTPS and verifying the
      certificate presented.
   -  /TestScript can help with these verifications.

-  Verify that dep8 has passed by checking
   http://people.canonical.com/~ubuntu-archive/pending-sru.html
-  Comment in the bug detailing that these checks have been performed
   and list the package versions verified.

.. _sru_template:

Certbot SRU Template
--------------------

::

   This bug tracks an update for the Certbot family of packages, version TODO.

   This update includes [TODO: remove one] bugfixes only/new features following the SRU policy exception defined at https://wiki.ubuntu.com/StableReleaseUpdates/Certbot.

   [Impact]

   Not directly applicable; see the exception policy document at https://wiki.ubuntu.com/StableReleaseUpdates/Certbot

   TODO: explain why we need this particular update

   [Major Changes]

   TODO: explain what changes users receiving the SRU will experience. In the case of a backport, this should summarize all changes from the version currently available in the stable releases to the uploads being proposed.

   [Test Plan]

   See https://wiki.ubuntu.com/StableReleaseUpdates/Certbot#SRU_Verification_Process

   [Regression Potential]

   Upstream performs extensive testing before release, giving us a high degree of confidence in the general case. There problems are most likely to manifest in Ubuntu-specific integrations, such as in relation to the versions of dependencies available and other packaging-specific matters.

   TODO: consider any other regression potential specific to the version being updated.
