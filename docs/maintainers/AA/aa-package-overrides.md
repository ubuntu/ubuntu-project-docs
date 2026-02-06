(aa-package-overrides)=
# Package overrides

There are two main kinds of overrides the {ref}`Archive Admin <archive-administration>`
team needs to keep tabs on so we can zero out the discrepancies before the end
of the release cycle:
{ref}`aa-component-mismatches`, and {ref}`aa-priority-mismatches`.

Packages just don't stay where they're put. {ref}`seed-management` details how
packages get chosen for the `main` component, the various meta packages and
presence on the CD. What it doesn't point out is that packages
that fall out of the seeding process are destined for the `universe` component.

(aa-component-mismatches)=
## What are component mismatches
 
Every 30 minutes or so, the difference between what the seeds expect to be true
and what the Archive actually states is evaluated by the `component-mismatches`
tool, and the output placed at:

* [`component-mismatches.txt`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.txt)

* [`component-mismatches.svg`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.svg)
  ([dot source](https://ubuntu-archive-team.ubuntu.com/component-mismatches.dot))


### Promotions to `main`

Source and binary
: These are source packages currently in `universe` that appear to need promoting
  to `main`. The usual reasons are that they are seeded, or that a package they
  build has become a dependency or build-dependency of a package in `main`.

  New sources need to be processed through the Ubuntu
  {ref}`Main Inclusion Review <main-inclusion-review>`,
  and have been approved before they should be promoted. Ensure that all of
  their dependencies (which will be in this list) are approved as well.

Binary-only
: These are binary packages currently in `universe` that appear to need promoting
  to `main`, as above; except that their source package is already in `main`. An
  inclusion report isn't generally needed, though the package should be checked
  for correctness.

  Especially check that all of the package's dependencies are already in `main`
  or have been approved.

### Demotions to `universe`

Source and binary
: Sources and their binaries that are currently in `main` but are no longer
  seeded or depended on by another package. These either need to be seeded
  explicitly, or demoted.

Binary-only
: Binary packages in `main` that are no longer seeded or depended on, but the
  source is still to remain in `main` -- usually because another binary saves it.
  Often these tend to be `-dev` or `-dbg` packages and need to be seeded, rather
  than demoted; but not always.



## Resolving component mismatches

For both directions, (universe -> main or main -> universe), start with
[`component-mismatches`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.html).
Or for more churn at: [`component-mismatches-proposed`](https://ubuntu-archive-team.ubuntu.com/component-mismatches-proposed.html).

* We will need to understand each individual case, so it is hard/not feasible
  to automate.

  * Study the case, related bugs and the changelogs.

  * If in doubt, ping the owning team to see if the fact that something demotes
    is an accident or intentional.

* Each case will thereby fall into one of two categories:

  * We know the background details, act accordingly.

  * We do not know, let us ping the owning team.

* We'd want to keep state/info of the case:

  * **Any promotion needs an approve {ref}`Main Inclusion Request <main-inclusion-review>`**
  * If any of the archive `ref`<freezes> are going on, please do not promote a package that would then unblock something in -proposed that is seeded on ISOs or Images.
  * Any demotion should leave a trail on the related MIR
    * Helper to find them:
      [`get-mir-bug`](https://git.launchpad.net/~ubuntu-server/+git/ubuntu-helpers/tree/cpaelzer/get-mir-bug)

    * Not yet covering source renames or such, but be creative with your queries

    * If no bug exists due to the dark past, consider filing them a stub according
      to {ref}`mir-rereview`.


### change-override

Once you’ve determined what overrides need to be changed, use the
`change-override` client-side tool to do it.

To promote a binary package to `main`:

```none
$ ./change-override --component main git-email
```

To demote a source package and all of its binaries to `universe`:

```none
# in -release
$ ./change-override --component universe --suite questing tspc
# in -proposed
$ ./change-override --component universe --suite questing-proposed tspc
```

### Less common options to change-override

Less frequently used are the options to just move a source, and leave its
binaries where they are (usually just to repair a mistaken forgotten `-S`) or
binary and source of the same name (but not its other binaries):

```none
# only this src and same named binary
$ ./change-override --component universe ---binary-and-source tspc
# ...oops, forgot the source...
$ ./change-override --component universe --source-only tspc
```

### Component attributes are sticky

When overriding the component of a package, that component will “stick” to the
package when migrating from one pocket to the other. That means that if you
demote a package in the `-release` pocket but it has a version in `-proposed`,
you’ll need to also demote that version or have to come back later on. Or you
can use that to your advantage so it takes this attribute with it just when it
migrates by only setting the component in `-proposed`.



### Special case -- promoting in stable releases

A special case are promotions in stable Ubuntu releases. Most of the time
promotions there work just as normal for packages in `-updates` and `-security`,
like:

```none
./change-override --component main --suite focal-updates [...] pkg-with-update
```

But if there was no update and it is only in the `-release` pocket like `focal`
it is immutable. Then we would get:

```none
./change-override --component main --suite focal [...] pkg-without-update
triggering:
lazr.restfulclient.errors.BadRequest: HTTP Error 400: Bad Request
b"Cannot change overrides in suite 'focal'"
```

Instead in this special case it is recommended to handle this as a pocket copy
of the package from the `-release` pocket to the `-updates` pocket with
binaries and no rebuild, and change the component only in `-updates`, e.g. as
done [in this case](https://bugs.launchpad.net/ubuntu/+source/mdevctl/+bug/1889248)
using the following arguments to `copy-package`: 

1. **`--version <version>`**: optional, but being explicit avoids hitting the
   wrong entry

1. **`--from-suite <from>`**: to select where it comes from

1. **`--to-suite <to>`**: to select where it should go to

1. **`--include-binaries`**: to not build

1. **`--auto-approve`**: to skip review queue

Afterwards it can then be promoted in `-updates`. So in the linked example it
was:

```none
./copy-package --version 6.9.4-1 --from-suite focal --to-suite focal-updates --include-binaries --auto-approve libonig
# wait until it is there
./change-override --component main --suite focal-updates --source-and-binary libonig
```

It is also possible to do this as a no-change rebuild of the package in the
`-release` pocket into the `-updates` pocket; however this then requires more
SRU process overhead because of the additional binaries and it is recommended
not to do this.


### Watch out -- sometimes changes are not instant all the way through

Launchpad does well in changing most attributes right away when acting with
`ubuntu-archive-tools`. But some aspects need a publisher run or similar. Some
other elements like `rdeps` are even a stage later as they are created from the
archive state -- so it could be publish + regenerate. This is well known and
accepted for `-proposed` migration where you'd wait for the next run, and also
well known for acceptance from NEW. But it can also affect promotions/demotions.
Therefore here is an example of such a case to illustrate, hint at what to
check if in doubt:

For example, while promoting
[`tinysparql`](https://bugs.launchpad.net/ubuntu/+source/tinysparql/+bug/2099086/comments/7)
the interim situation was seen that we could see the tool reporting the same
content in `main` and in `universe` at once. That was such a case of a pending change, the
[Launchpad view to the package](https://launchpad.net/ubuntu/plucky/amd64/tinysparql)
stated it as pending at the time and explained what was going on. Once that
state resolved there, it also was in the right state in all other tools.

