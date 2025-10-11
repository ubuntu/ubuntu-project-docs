.. _git-ubuntu-design-goals-and-principles:

Git-ubuntu design goals and principles
======================================


Consistency and tool unification
--------------------------------

One measure of success for git-ubuntu is to reduce or eliminate the occasions
where an experienced Ubuntu developer has to say "that package is special" when
a new developer or drive-by contributor is asking for help on performing a
routine task.

Another measure is the amount of setup required before a developer can perform
a task, such as test building a package from a source tree in a reproducible
way.

For example, in answer to the following questions, git-ubuntu already
eliminates the "this package is special" excuse for packages covered by
git-ubuntu repositories:

* "Where can I clone the git tree for package X"? Without git-ubuntu, "this
  package is special" is needed when a Vcs-Git header doesn't exist, or does
  exist but no git branch is maintained for the Ubuntu delta, or does exist but
  the header hasn't been updated to point to it.

The following are medium term goals:

* "How do I build package X"? Right now, the recommended :command:`sbuild` method
  involves setting up :term:`chroots <chroot>`, arranging :command:`sbuild` group membership, and :command:`sbuild`
  default configuration expects an MTA that also requires setting up.

* "How do I patch the version of package X that Ubuntu ships in release Y"?
  Right now, this usually involves knowledge of quilt and the "3.0 (quilt)"
  Debian source package format.

Because git-ubuntu uses a single scheme to represent package source trees in
git, and also a single schema for all branch and tag names, automation that
operates on package sources is easier to write, including automation that needs
visibility across multiple package versions at once. For example, it's easier
to write automation to help validate SRUs since such automation can easily
inspect the current state of different releases and pockets. Instead of using
the Launchpad API for this kind of inspection, the tooling can inspect this
state using the same mechanism it can use to inspect the existing published
source tree and the source trees in Launchpad's queues. git is the single tool
that can be used for all of this.

Single source of truth
----------------------

Uploads arrive into Ubuntu regardless of git-ubuntu, such as via syncs from
Debian or just direct uploads using ``dput`` without git-ubuntu. Launchpad is
the authority that publishes Ubuntu packages via apt. So Launchpad, not
git-ubuntu, is the authority and "single source of truth" of what the source
tree is for a particular package, and what they were historically.

git-ubuntu is designed to be able to guarantee that its git repositories do
actually represent this single source of truth. Therefore, its git repositories
are necessarily derived from and form a view onto Launchpad's single source of
truth, and cannot define it.

Integrity requirements
----------------------

Since git-ubuntu's git repositories are merely a view of Launchpad's single
source of truth, its refs (branches, tags, etc) must also be derived from that
truth and therefore must be read-only from the git perspective. Otherwise,
developers would be able to push a different truth to the git repositories that
do not reflect the truth in Launchpad, and that would defeat the purpose of
git-ubuntu in the first place.

Similarly, the commits that correspond to specific published source package
versions must match what was uploaded exactly, so that developers can trust
that what they see in the git repository corresponds to what was actually
published.

How uploads map to commits
--------------------------

In the common case, git-ubuntu achieves this by synthesizing a commit from what
was uploaded to Launchpad as a package upload. In this case, all the changes
from the previous upload are "squashed" into a single commit.

However, the integrity requirement is just that the specific commits that
correspond to package uploads match. Intermediate commits are permitted, and
these need not be restricted for integrity purposes.

Therefore, this schema allows for developers to provide a "richer" path that
describes how they arrived at their upload in more granular detail, in the
git usual way by providing intermediate commits. In git-ubuntu, since we aren't
the single source of truth, we must handle this specially to maintain our other
integrity requirements, and call this concept "rich history".


.. _rich-history:

Rich history
------------

git-ubuntu's rich history mechanism has some requirements:

#. The developer must provide rich history commits at the time of the dput-based (non-git) upload.

#. These commits must remain available to the git-ubuntu importer until after it has imported them.

#. The tree of the final rich history commit provided must precisely match the tree of the upload. There exist some edge cases necessary to maintain a lossless mapping from source package to git tree where git-ubuntu defines exactly what should happen to the tree; the rich history commit must do precisely the same to meet this requirement.

#. The specification defines some further requirements; the general idea is that the rich history commits must be based on a commit that corresponds to a previous import and your upload must preserve the old ``debian/changelog`` entries in the usual way.

If these requirements are met, then git-ubuntu will use your commits for its
import instead of synthesizing one.

See :ref:`how-to-upload-with-rich-history` for instructions on providing rich history to the
importer.


Determining the parent
----------------------

Trust the uploader to base it correctly by looking at :file:`debian/changelog`.
This leads to "force pushes".


.. _keyring-integration:

Keyring integration
-------------------

Some git-ubuntu subcommands (e.g. ``git-ubuntu submit``) require authenticated
access to the Launchpad API. The first time you do this, you will be prompted
to authenticate in a web browser. If successful, the authenticated API key will
then be saved in your local keyring. You may be prompted for a password. This
password is used to encrypt your local keyring. If you don't yet have a local
keyring, the password you provide will be used to encrypt it. If you already
have a local keyring, the password you provide is the one required to decrypt
it.

See :ref:`keyring-with-plaintext-storage` for instructions on configuring keyring to use
plaintext password storage instead, to avoid getting keyring password prompts.

git-ubuntu uses `launchpadlib <https://help.launchpad.net/API/launchpadlib>`_ for Launchpad API access. This
library in turn uses the `Python keyring package <https://pypi.org/project/keyring/>`_ for credential storage. If you see a password prompt, it is because the keyring package's defaults in your particular environment require encrypted password-based credential storage. Configure this to your needs by following the `keyring documentation <https://pypi.org/project/keyring/>`_.
