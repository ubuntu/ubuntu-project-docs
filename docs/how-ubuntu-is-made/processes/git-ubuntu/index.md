(git-ubuntu)=
# git-ubuntu

```{toctree}
:maxdepth: 1
:hidden:

changes-file-headers
empty-directories
```

As Ubuntu's packaging architecture pre-dates git, different packages have
evolved to use different mechanisms to achieve the same thing. Developers had
to learn them all in order to be effective when working across a wide range of
packages. git-ubuntu's unification of these mechanisms allows for simpler, more
general tooling, which results in faster onboarding of new developers and
easier "drive-by" contributions.

git-ubuntu comprises two components:

1. The {command}`git-ubuntu` CLI tool contains all its provided automation for developer use.

1. The git-ubuntu importer service runs the importer to maintain git
repositories of Ubuntu packages in Launchpad.


## CLI

The {command}`git-ubuntu` CLI is installed with `sudo snap install --classic git-ubuntu`. It adds `ubuntu` subcommands to the `git` command. For example: `git ubuntu clone hello`.

Just like the `git` command itself, most git-ubuntu subcommands expect to be
running in the context of a git repository.


### When to use the CLI

Since the git-ubuntu importer service hosts its imported repositories in
Launchpad, there is a regular public URL to clone from for each source package,
and you can do this using plain git. So it's not strictly necessary to use the
git-ubuntu CLI at all.

However use of the git-ubuntu CLI gives you the following:

* Convenience. For example:

  * `git ubuntu clone <package>` clones a git-ubuntu repository without you
    having to look up the URL, and adds an additional remote that corresponds
    to your personal space on Launchpad, so you can later easily push to it to
    propose a merge.

  * `git ubuntu remote add <lpuser>` adds a peer's personal repository space
    for the same package, so you can easily fetch and review their merge
    proposals without typing long URLs.

* `git log` is automatically configured to display "changelog notes" if you
  used `git ubuntu clone`, so it's easier to see summaries of what changed
  in synthesized commits.

* Workaround hooks are automatically added by `git ubuntu clone` to help
  detect and deal with edge case issues, such as
  {ref}`empty-directories`.


## Importer service

The git-ubuntu importer service maintains a view of the entire packaging
version history of Ubuntu source packages using git repositories with a common
branching and tagging scheme. The git-ubuntu CLI provides tooling and
automation that understands these repositories to make the development of
Ubuntu itself easier.


### Sources only

The git-ubuntu importer consumes source packages only, and has no involvement
with binaries. Launchpad's source and binary publication pipelines are
independent of each other, except that of course binary publications are
dependent on their corresponding source publications. So whether or not a build
fails, or even if Launchpad hasn't processed a build or binary packages yet,
git-ubuntu catches up on source package updates as soon as Launchpad publishes
them.


### git-ubuntu and Launchpad

Launchpad is the platform where Ubuntu development happens. But it is separate
from git-ubuntu:

* Launchpad provides the machinery that validates, builds and publishes
  packages.

* Launchpad also provides the hosting for the git-ubuntu repositories, and the
  mechanism for developers to collaborate on them through repository forks and
  merge proposals with comment and voting facilities.

The importer itself is provided by the CLI as the `import` subcommand. It's
possible to run the tool locally if the importer service is unavailable or
inaccessible, and for development of the git-ubuntu importer itself. Similarly,
the components that schedule the imports are available as the
`importer-service-{broker,poller,worker}` subcommands.


(rich-history)=
## Rich history

git-ubuntu's rich history mechanism has some requirements:

1. The developer must provide rich history commits at the time of the dput-based (non-git) upload.

1. These commits must remain available to the git-ubuntu importer until after it has imported them.

1. The tree of the final rich history commit provided must precisely match the tree of the upload. There exist some edge cases necessary to maintain a lossless mapping from source package to git tree where git-ubuntu defines exactly what should happen to the tree; the rich history commit must do precisely the same to meet this requirement.

1. The specification defines some further requirements; the general idea is that the rich history commits must be based on a commit that corresponds to a previous import and your upload must preserve the old `debian/changelog` entries in the usual way.

If these requirements are met, then git-ubuntu will use your commits for its
import instead of synthesizing one.

See {ref}`how-to-upload-with-rich-history` for instructions on providing rich history to the
importer.


(keyring-integration)=
## Keyring integration

Some {command}`git-ubuntu` subcommands (e.g. `git-ubuntu submit`) require authenticated
access to the Launchpad API. The first time you do this, you will be prompted
to authenticate in a web browser. If successful, the authenticated API key will
then be saved in your local keyring. You may be prompted for a password. This
password is used to encrypt your local keyring. If you don't yet have a local
keyring, the password you provide will be used to encrypt it. If you already
have a local keyring, the password you provide is the one required to decrypt
it.

See {ref}`keyring-with-plaintext-storage` for instructions on configuring keyring to use
plaintext password storage instead, to avoid getting keyring password prompts.

git-ubuntu uses {external:std:ref}`launchpadlib <get-started-with-launchpadlib>` for Launchpad API access. This
library in turn uses the [Python keyring package](https://pypi.org/project/keyring/) for credential storage. If you see a password prompt, it is because the keyring package's defaults in your particular environment require encrypted password-based credential storage. Configure this to your needs by following the [keyring documentation](https://pypi.org/project/keyring/).


## Further reading

* [git-ubuntu source](https://git.launchpad.net/git-ubuntu)
* [git-ubuntu bug tracker](https://bugs.launchpad.net/git-ubuntu/)
