(aa-package-overrides)=
# Package overrides

There are two main kinds of overrides that we need to keep tabs on, in order to
zero out the discrepancies before the end of the release cycle:
**component mismatches**, and **priority mismatches**.

Handling of component mismatches is already described in detail in
{ref}`component-mismatches-and-changing-overrides`.


## Target pocket for the override 

When overriding the component of a package, that component will "stick" to the
package when migrating from one pocket to the other. That means that if you
demote a package in the `-release` pocket but it has a version in `-proposed`,
you'll need to also demote that version or have to come back later on. Or you
can use that to your advantage so it takes this attribute with it just when it
migrates by only setting the component in `-proposed`.


## Special case -- demoting to universe 

Start at
[`component-mismatches`](https://ubuntu-archive-team.ubuntu.com/component-mismatches.html)
Or for more churn at: [`component-mismatches-proposed`](https://ubuntu-archive-team.ubuntu.com/component-mismatches-proposed.html).

* We will need to understand each individual case, so it is hard/not feasible
  to automate.

  * Study the case, related bugs and the changelogs.

  * If in doubt, ping the owning team to see if the fact that something demotes
    is an accident or intentional.

* Each case will thereby fall into one of two categories:

  * We know the background details, act accordingly.

  * We do not know, let us ping the owning team.

* We'd need to not repeat that so we'd want to keep state/info of what we found:

  * **Now**: try to leave comments on an MIR bug.

    * Helper to find them:
      [`get-mir-bug`](https://git.launchpad.net/~ubuntu-server/+git/ubuntu-helpers/tree/cpaelzer/get-mir-bug)

    * Not yet covering source renames or such, but be creative with your queries

    * If None exists due to the dark past, consider filing them a stub according
      to {ref}`mir-rereview`.

  * **Future**: We'd like to have a linked bug as with MIRs and in MoM would be
    a desire for the evolution of this page.


## Special case -- promoting in stable releases

A special case are promotions in stable Ubuntu releases. Most of the time
promotions there work just as normal for packages in `-updates` and `-security`,
like:

```bash
./change-override --component main --suite focal-updates [...] pkg-with-update
```

But if there was no update and it is only in the `-release` pocket like `focal`
it is immutable. Then we would get:

```bash
./change-override --component main --suite focal [...] pkg-without-update
triggering:
lazr.restfulclient.errors.BadRequest: HTTP Error 400: Bad Request
b"Cannot change overrides in suite 'focal'"
```

Instead in this special case it is recommended to handle this as a pocket copy
of the package from the `-release` pocket to the `-updates` pocket with
binaries and no rebuild and change the component only in `-updates`, e.g. as
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

```bash
./copy-package --version 6.9.4-1 --from-suite focal --to-suite focal-updates --include-binaries --auto-approve libonig
# wait until it is there
./change-override --component main --suite focal-updates --source-and-binary libonig
```

It is also possible to do this as a no-change rebuild of the package in the
`-release` pocket into the `-updates` pocket; however this then requires more
SRU process overhead because of the additional binaries and it is recommended
not to do this.


## Watch out -- sometimes changes are not instant all the way through

[See MM discussion here](https://chat.canonical.com/canonical/pl/47hr8y3xp3bu9fno5a87x7w1ma).

Launchpad does well in changing most attributes right away when acting with
`ubuntu-archive-tools`. But some aspects need a publisher run or similar. Some
other elements like `rdeps` are even a stage later as they are created from the
archive state -- so it could be publish + regenerate. This is well known and
accepted for `-proposed` migration where you'd wait for the next run, and also
well known for acceptance from NEW. But it can also affect promotions/demotions.
Therefore here is an example of such a case to illustrate, hint at what to
check if in doubt:

In promoting
[`tinysparql`](https://bugs.launchpad.net/ubuntu/+source/tinysparql/+bug/2099086/comments/7)
the interim situation was seen that we could see the tool reporting the same
content in `main` and in `universe` at once.

That was such a case of a pending change, the
[Launchpad view to the package](https://launchpad.net/ubuntu/plucky/amd64/tinysparql)
stated it as pending at the time and explained what was going on. Once that
state resolved there, it also was in the right state in all other tools.

```{admonition} Question
:class: important
Unsure: should we explain more deeply how this is also true in `rdeps` and
`-proposed` migration in the same place or refer to it?
```

```{admonition} Question
:class: important
Unsure: was this actually a bug and should we write it at all?

**TODO**: Contact Launchpad about that.
```
