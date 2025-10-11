(git-ubuntu)=
# Git-ubuntu

```{toctree}
:maxdepth: 1
:hidden:

Design goals and principles <git-ubuntu-design-goals-and-principles>
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

1. The git-ubuntu importer service runs the importer to maintain git
repositories of Ubuntu packages in Launchpad.

1. The {command}`git-ubuntu` CLI tool contains all its provided automation for developer
use.


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


### Git-ubuntu and Launchpad

Launchpad is the platform where Ubuntu development happens. But it is separate
from git-ubuntu:

* Launchpad provides the machinery that validates, builds and publishes
  packages.

* Launchpad also provides the hosting for the git-ubuntu repositories, and the
  mechanism for developers to collaborate on them through repository forks and
  merge proposals with comment and voting facilities.

* Git-ubuntu maintains the git-ubuntu repositories in Launchpad. The git-ubuntu
  importer service clones them, scans and downloads Launchpad source
  publications updates, converts these into repository updates and pushes the
  updated repositories back to Launchpad.

The importer itself is provided by the CLI as the `import` subcommand. It's
possible to run the tool locally if the importer service is unavailable or
inaccessible, and for development of the git-ubuntu importer itself. Similarly,
the components that schedule the imports are available as the
`importer-service-{broker,poller,worker}` subcommands.


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


## Further reading

* [git-ubuntu source](https://git.launchpad.net/git-ubuntu)
* [git-ubuntu bug tracker](https://bugs.launchpad.net/git-ubuntu/)
