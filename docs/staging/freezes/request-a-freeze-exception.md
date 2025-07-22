(request-a-freeze-exception)=
# Request a Freeze exception

```{note}
This page will be moved to:
* contributors > advanced
```

Requests for {ref}`freeze-exceptions` are filed as bugs in Launchpad
against the relevant package (or just "Ubuntu" if the package is not available
yet).

When you make your request, set the bug status to *New* to ensure the Release
Team sees the request. Once all the required information is included, file your
bug and subscribe [`ubuntu-release`](https://launchpad.net/~ubuntu-release) to
it.


## What to include

All freeze exception request bugs **must** include the following information,
which provides the release team with enough information to weigh the risk of
regressions against the benefit of the changes:

* A description of the proposed changes, with enough detail to estimate
  their potential impact on the distribution

* A rationale for the exception, explaining the benefit of the change

* Any additional information which would be helpful in considering the decision

* An explanation of what testing has been performed on the new version in Ubuntu,
  including verification that the new package:

  * Builds

  * Installs

  * Upgrades

  * Does not break packages depending on it (or that corresponding updates have
    been prepared)

* If the upload is a new upstream micro-release, the relevant part of the
  upstream changelog and/or release notes also needs to be included

The request for an exception to {ref}`feature-freeze` should demonstrate that
the benefit of new functionality, or the total benefit of a new upstream release
that includes it, outweighs the risk of regressions and other potential
disruption of the release process.

Specific **additional** requirements for different scenarios are outlined below.

### Feature Freeze for new upstream versions

If you want to introduce a new upstream version with new features and/or
ABI/API changes, you should first create a new bug under your package (or, if
there is already a bug related to the exception, you can reuse the bug), e.g.
`https://bugs.launchpad.net/ubuntu/+source/<PACKAGE>/+filebug`

Your bug contents need to include the following:

* Add `[FFE]` to the bug summary (large title)

* Add an FFE stanza to the description starting with `## FFE ##`

* **State the reason why you feel it is necessary** (e.g. other bugs it fixes)

* Attach (as files):

  * A diff of the **Upstream** changelog (not `debian/changelog`):

    ```none
    diff -u <package>-{old-version,new-version}/ChangeLog > changelog.diff
    ```

    Note that the changelog is sometimes called `CHANGES`, is missing or the
    tarball merely has a `NEWS` file

  * The `NEWS` file, if you think that this information will help reviewing your
    request (true for most GNOME packages)

  * Build log (as a file)

    * `pbuilder` has the `--logfile` option

    * `pbuilder-dist` and `cowbuilder-dist` automatically save it as `last_operation.log`

  * Install log

   * For instance, a copy and paste of the install messages from console when
     installing

  * Mention what testing you've done to see that it works 

  * (Optional) A screenshot showing the main features would also be nice

* Subscribe (do not assign!) the '`ubuntu-release`' team


```{important}
We expect anyone making a request to have an updated package already prepared
and tested! You will need this anyway to provide proper build logs.
```

Once the Feature Freeze Exception has been approved by a member of the
[Release Team](https://launchpad.net/~ubuntu-release), the status will be
changed to *TRIAGED*. You can then either upload the package (if you're in
[`motu`](http://launchpad.net/~motu) or
[`ubuntu-core-dev`](http://launchpad.net/~ubuntu-core-dev)), or follow the
{ref}`sponsorship-process`. Please close the bug from the upload, where possible.


```{seealso}
* [Open requests](https://bugs.launchpad.net/~ubuntu-release/+subscribedbugs)

* [Original announcement](https://lists.ubuntu.com/archives/ubuntu-motu/2006-February/000545.html) of the change to the UVF exceptions process
```

(request-ui-freeze-exception)=
### Request UI Freeze exception

Every change of the UI (either a string or the layout) requires you to notify
the [documentation](https://lists.ubuntu.com/mailman/listinfo/ubuntu-doc) and
[translation](https://lists.ubuntu.com/mailman/listinfo/ubuntu-translators)
teams.

Please add links to your posts in the
[`ubuntu-doc@`](https://lists.ubuntu.com/archives/ubuntu-doc/) and
[`ubuntu-translators@`](https://lists.ubuntu.com/archives/ubuntu-translators/)
mailing list archives to the bug.

After that, subscribe the Release Team as usual.

Refer to {ref}`ui-freeze-exceptions` for more details.

(request-milestone-freeze-exception)=
### Request Milestone Freeze exception

Exception requests for Milestone Freeze exceptions must include the following
additional details:

* It must fix a bug earmarked for that particular milestone

* A complete `debdiff` of the proposed upload must be provided (preferably as
  a bug attachment)

Refer to {ref}`milestone-freeze-exceptions` for more details.

(request-universe-multiverse-exception)=
### Request universe/multiverse exception

For Freeze exception requests for `universe` or `multiverse`, the process is to
either:

* File a bug with the debdiff, assign it to `ubuntu-release`, and get approval
  for it

* Or ask a member of the [`ubuntu-release`](http://launchpad.net/~ubuntu-release)
  team for approval of the debdiff.

Refer to {ref}`universe-multiverse-freeze-exceptions` for more details.
