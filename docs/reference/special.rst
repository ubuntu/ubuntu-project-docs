.. _reference-special-types-of-sru:

Special types of SRU
--------------------

`What is acceptable to SRU <#what-is-acceptable-to-sru>`__, together
with other considerations, give rise to the following special types of
permitted SRU, some of which overlap:

* **Package-specific non-standard process:** for routine non-standard
  cases, we create :ref:`package-specific notes
  <reference-package-specific-notes>` for consistency. These may
  incorporate any of the other special types below and may include any
  exceptions to our :ref:`usual criteria
  <reference-what-is-acceptable-to-sru>` that have been approved by the
  Technical Board.

* **Hardware enablement:** for Long Term Support releases we regularly
  want to enable new hardware [:ref:`criteria
  <reference-criteria-hardware>`].

* **Environmental change:** updates that need to be applied to Ubuntu
  packages to adjust to changes in the environment, server protocols,
  web services, and similar [:ref:`criteria
  <reference-criteria-environment>`].

* **Autopkgtest fix:** autopkgtest fixes may be included in SRUs. An
  update that fixes only autopkgtests is also acceptable, but should
  normally be :ref:`staged <explanation-staged-uploads>` [:ref:`criteria
  <reference-criteria-autopkgtest>`].

* **Extended Security Maintenance:** there are special procedures for
  uploads to stable releases in their `Extended Security Maintenance
  (ESM) <https://ubuntu.com/esm>`__ period. Please prepare the SRU bug
  and then contact `the ESM team
  <https://launchpad.net/~ubuntu-esm-team>`__.

* **Staged upload** [:ref:`explanation <explanation-staged-uploads>`]
  [:ref:`how-to: stage upload <howto-stage-upload>`] [:ref:`how-to: land staged
  upload <howto-unblock-staging>`].

* **Upload to the new queue of an active release** [:ref:`explanation <explanation-new-queue>`]
  [:ref:`how-to: new source or binary <howto-new-queue>`].

* **Bundled upload:** an SRU performed "on top" of an existing
  package already in -proposed. [TBC]

* **New upstream release:**

  * **New bugfix-only upstream release**

    Bugfix-only releases are acceptable if all changes are appropriate
    for an SRU under our normal :ref:`criteria
    <reference-what-is-acceptable-to-sru>`, by one of two paths:

    1. The upload may use the new upstream orig tarball, but with
       individual Launchpad bugs to track verification of each fix
       individually.

    2. Instead, if upstreams meet, in the opinion of the SRU team, our
       :ref:`more specific QA criteria for upstream microreleases
       <reference-criteria-microreleases>` then it is acceptable to
       process them with a single tracking bug instead of individual
       Launchpad bugs for each fix. If relying on this path, the
       upstream QA process that meets this criteria must be
       documented/demonstrated and linked from the SRU tracking bug.

  * **New upstream release that adds features without breaking existing
    behaviour**

    For Long Term Support releases we sometimes consider it appropriate
    to introduce new features. We may choose to do so we can do this
    safely. However, to meet expectations of release stability, we will
    consider these on a case-by-case basis [:ref:`criteria
    <reference-criteria-features>`].

  * **New upstream release that changes existing behaviour**

    Deliberately changing existing behaviour is to be avoided due to our
    :ref:`minimise regression principle
    <explanation-minimise-regression>`, so such SRUs are generally not
    permitted. Exceptions may be granted by the Technical Board, but
    require exceptional justification. Standing exceptions are documented
    in :ref:`Package-specific notes <reference-package-specific-notes>`.

* **Removals:** in rare cases, a package is or has become actively
  harmful to users, and is replaced by an empty package
  [:ref:`explanation <explanation-removals>`].

* **Security updates:** these usually follow a different process and
  are out of scope of the SRU team and processes documented here. See
  `SecurityTeam/UpdateProcedures
  <https://wiki.ubuntu.com/SecurityTeam/UpdateProcedures>`__ for details
  [:ref:`explanation <explanation-security>`].
