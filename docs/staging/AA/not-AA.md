(not-AA)=
# Content that doesn't belong to AA

```{important}
This page should not be moved out of the staging area in its current state.
If you move content to another section, please delete it from this page.
```


All this content is saved from
[the Wiki Archive Admin page](https://wiki.ubuntu.com/ArchiveAdministration)


## DMB content

This content is used by DMB-members
 
### Adjusting Launchpad ACLs

```{note}
Due to [bug #562451](https://bugs.launchpad.net/launchpad/+bug/562451), Archive
Administrators cannot currently adjust Launchpad ACLs.
```

The new [Archive Reorganization](https://wiki.ubuntu.com/ArchiveReorganisation)
brings finer grained access controls than what components can provide.
Launchpad ACLs allow individuals and teams to have upload or admin rights on
certain packages, referred to as **sets**. In general, an Archive Administrator
can process requests to create and delete package sets, as well as add or remove
packages from package sets. Archive administrators should not add individuals
or teams to package sets without explicit
[Technical Board](https://wiki.ubuntu.com/TechnicalBoard) approval.

#### Package sets

Packages can be added to or removed from package sets using the `edit-acl` tool
from `ubuntu-archive-tools`.

To list the packages currently in the package set `mozilla`:

```none
$ ./edit-acl query -P mozilla -S zesty

adblock-plus
all-in-one-sidebar
bindwood
...
```

```{admonition} Update needed
:class: important
This section refers to zesty, but also says "currently"
```

To add a package to the `mozilla` package set:

```none
$ ./edit-acl -P mozilla -S zesty -s foo -s bar -s baz add
```

To remove a package from the `mozilla` package set:

```none
$ ./edit-acl -P mozilla -S zesty -s foo delete
```

For more information, please see `edit-acl --help`.


## The SRU team

### Useful tools

#### Diffs for unapproved uploads

The "unapproved" queue holds packages while a release is frozen, i.e. while a
milestone or final freeze is in progress, or for post-release updates (like
`hardy-proposed`). Packages in these queues need to be scrutinized before they
get accepted.

This can be done with the `queuediff` tool in `ubuntu-archive-tools`, which
generates a debdiff between the current version in the archive, and the
package sitting in the unapproved queue:

```none
$ ./queuediff -s hardy-updates hal
$ ./queuediff -b human-icon-theme | view -
```

`-s` specifies the release pocket to compare against and defaults to the
current development release. Please note that the pocket of the unapproved
queue is not checked or regarded; i.e. if there is a `hal` package waiting in
`hardy-proposed/unapproved`, but the previous version already migrated to
`hardy-updates`, then you need to compare against `hardy-updates`, not
`-proposed`.

Check `--help` for more options, such as specifying a different mirror, or use
`-b` to open the referred Launchpad bugs in your web browser.

This tool works very fast if the new package does not change the
`orig.tar.gz` -- then it only downloads the `diff.gz`. For native packages or
new upstream versions it needs to download both tarballs and run `debdiff` on
them. Thus for large packages you might want to do this manually in the data
center.


### Stable Release Updates

SRU packages in `-proposed` must be approved by `~ubuntu-sru` before accepting.

Please see: [SRU / Reviewing procedure and tools](https://documentation.ubuntu.com/sru/en/latest/internal/#reviewing-procedure-and-tools)


#### Langpack SRUs

Language packs are a special case; these packages are normally uploaded as a
batch and will not normally reference specific bugs. The
[status page](https://ubuntu-archive-team.ubuntu.com/pending-sru.html) will
only show `language-pack-en`. Please see
[the documentation](https://git.launchpad.net/langpack-o-matic/tree/doc/operator-guide.txt)
on how to copy packages between PPA, `-proposed`, and `-updates`.


## Release team

User of this content: Ubuntu Developers 
May be a duplicate of what's in the packaging guide

### Archive Administration and Freezes

Archive Admins should be familiar with the
[Freeze Exception Process](https://wiki.ubuntu.com/FreezeExceptionProcess),
however it is the bug submitter's and sponsor's responsibility to make sure
that the process is being followed. Some things to keep in mind for common tasks:

* When the Archive is frozen (i.e. the week before a Milestone, or from one
  week before RC until the final release), you need an ACK from `ubuntu-release`
  for all `main`/`restricted` uploads

* During the week before final release, you need an ACK from `ubuntu-release`
  for any uploads to `universe`/`multiverse`

* When the Archive is not frozen, `bugfix-only` sync requests can be processed
  if filed by a `core-dev`, `ubuntu-dev` or `motu` (`universe`/`multiverse`
  only) or have an ACK by a sponsor or someone from `ubuntu-sponsors`.

* After [Feature Freeze](https://wiki.ubuntu.com/FeatureFreeze), all (new or
  otherwise) packages in the Archive (i.e. `main`, `restricted`, `universe` and
  `multiverse`) require an ACK from `ubuntu-release` for any
  Freeze Exception (e.g. [Feature Freeze](https://wiki.ubuntu.com/FeatureFreeze),
  [User Interface Freeze](https://wiki.ubuntu.com/UserInterfaceFreeze), and
  [Milestone](https://wiki.ubuntu.com/MilestoneProcess)). Packages that do not
  require a Freeze Exception can be processed normally.

See [Freeze Exception Process](https://wiki.ubuntu.com/FreezeExceptionProcess) for complete details.


## MIR team

User of this documentation: OEM teams in Canonical
Owner: MIR + AA teams

### OEM metapackages

The Archive team runs a script, maintained by the
[Developer Membership Board](https://wiki.ubuntu.com/DeveloperMembershipBoard),
to automatically grant upload rights to `oem-*-meta` packages -- including
packages that aren't yet in Ubuntu (uploaders can upload to NEW for these
packages) -- to some members of Canonical's OEM delivery team via a packageset called "canonical-oem-metapackages".

The DMB handle applications to the packageset and maintain the code. Our responsibility in the archive team is to run the script reasonably frequently, pull any changes when the DMB ask us to, and arrange for its output to be emailed at least to the `devel-permissions` list.

See [the DMB knowledge base](https://wiki.ubuntu.com/DeveloperMembershipBoard/KnowledgeBase#Canonical_OEM_metapackage_packageset)
and [the script itself](https://git.launchpad.net/~developer-membership-board/+git/oem-meta-packageset-sync/tree/oem-meta-packageset-sync)
for some further information and links.



