(request-a-freeze-exception)=
# Request a Freeze exception

Requests for {ref}`freeze-exceptions` are filed as bugs in Launchpad
against the relevant package (or just "Ubuntu" if the package is not available
yet).

```{admonition} **Freezes** series

**Process overview:**
: {ref}`freezes`

**Reference:**
: {ref}`freeze-exceptions`

**Practical guidance:**
: {ref}`request-a-freeze-exception` (this page)
```


When you make your request, set the bug status to *New* to ensure the Release
Team sees the request. Once all the required information is included, file your
bug and subscribe [`ubuntu-release`](https://launchpad.net/~ubuntu-release) to
it. You can refer to
[open requests](https://bugs.launchpad.net/~ubuntu-release/+subscribedbugs) to
view bugs the Release Team is already subscribed to.


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

* Also include the output from the command `seeded-in-ubuntu <package-name>` for
  the package you are seeking the exception for, so the Release Team can see
  where the package is seeded so the impact of the change can be assessed

The request for an exception to {ref}`feature-freeze` should **demonstrate**
that the benefit of new functionality, or the total benefit of a new upstream
release that includes it, outweighs the risk of regressions and other potential
disruption of the release process.

Specific **additional** requirements for different scenarios are outlined below.


### Feature Freeze for new upstream versions

If you want to introduce a new upstream version with new features and/or
ABI/API changes, you should first create a new bug under your package (or, if
there is already a bug related to the exception, you can reuse the bug), e.g.
`https://bugs.launchpad.net/ubuntu/+source/<PACKAGE>/+filebug`

Your bug contents need to include the following:

* Add `[FFE]` to the bug summary (large title).

* Add an FFE stanza to the description starting with `## FFE ##`.

* **State the reason why you feel it is necessary** (e.g. other bugs it fixes).

* Attach (as files):

  * A diff of the **Upstream** changelog (not `debian/changelog`):

    ```none
    diff -u <package>-{old-version,new-version}/ChangeLog > changelog.diff
    ```

    Note that the changelog is sometimes called `CHANGES`, is missing or the
    tarball merely has a `NEWS` file.

  * The `NEWS` file, if you think that this information will help reviewing your
    request (true for most GNOME packages).

  * A link to the PPA where the requested changes have been uploaded. The
    Release Team can review the artifacts (build logs etc) from there.

  * Install log, e.g. a copy and paste of the install messages from console when
    installing.

  * Mention what testing you've done to see that it works.

  * Regression potential; for guidance, refer to the
    [SRU template](https://documentation.ubuntu.com/sru/en/latest/reference/bug-template/).

  * (Optional) A screenshot showing the main features would also be nice.

* Subscribe (do not assign!) the `ubuntu-release` team.


```{important}
We expect anyone making a request to have an updated package already prepared
and tested! You will need this anyway to provide proper build logs.
```

Once the Feature Freeze exception has been approved by a member of the
[Release Team](https://launchpad.net/~ubuntu-release), the status will be
changed to *TRIAGED*. You can then either upload the package (if you're in
[`motu`](https://launchpad.net/~motu) or
[`ubuntu-core-dev`](https://launchpad.net/~ubuntu-core-dev)), or follow the
{ref}`sponsorship process <sponsorship>`. Please close the bug from the upload,
where possible.


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

After that, subscribe (do not assign) the `ubuntu-release` team to the bug as
usual.

Refer to {ref}`ui-freeze-exceptions` for more details.


(request-final-freeze-exception)=
### Request Final Freeze exception

Exception requests for {ref}`final-freeze-exceptions` must include the following
additional details:

* It must fix a bug earmarked by the Release Team for that particular milestone.

* A complete `debdiff` or a merge proposal of the proposed upload must be
  provided (preferably as a bug attachment).

After that, subscribe (do not assign) the `ubuntu-release` team to the bug as
usual.

