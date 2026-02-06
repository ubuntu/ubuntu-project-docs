(how-to-find-a-sponsor)=
# How to find a sponsor

The ability to upload or sync directly to the Archive is carefully managed to ensure the stability and security of Ubuntu. New contributors don't have upload rights immediately -- they must request {ref}`sponsorship` from someone who *does* have upload rights to:

- Make changes to existing packages or incremental updates.
- Submit security updates or bug fixes.
- Introduce new packages to Ubuntu.
- Initiate syncs from Debian.

:::{admonition} **Sponsorship** series
The article series provides guidance on requesting sponsorship and sponsoring.

Overview:
:   * {ref}`sponsorship`

For contributors:
:   * {ref}`how-to-find-a-sponsor` (this article)
    * {ref}`how-to-request-an-upload`
    * {ref}`how-to-request-a-sync`

For sponsors:
:   * {ref}`how-to-review-a-merge-proposal`
    * {ref}`how-to-sponsor-an-upload`
    * {ref}`how-to-sponsor-a-sync`
:::


## Formal sponsorship request

To request sponsorship, file a bug or submit a merge proposal in Launchpad, subscribing the `ubuntu-sponsors` team. See the following articles for instructions on how to do this for uploads (merges) and syncs:

  * {ref}`how-to-sponsor-an-upload`
  * {ref}`how-to-sponsor-a-sync`


## Informal channels

In urgent cases or when you wish to discuss your potential request for sponsorship before filing a bug or submitting a merge proposal, ask in the {matrix}`devel` Matrix channel or in the [ubuntu-devel](https://lists.ubuntu.com/mailman/listinfo/ubuntu-devel) mailing list.


## After sponsorship request

Following a sponsorship request, continue to monitor the status of the upload or sync.

Check the build
: To check the status of the build, visit the {guilabel}`Overview` page for the package in question on Launchpad:

  `https://launchpad.net/ubuntu/+source/<name_of_the_package>`

  For example: {lpsrc}`hello`.

  The main part of the page contains a list of built packages for every Ubuntu series. Click the package version to see the builds for specific architectures and the build logs.

Package history
: Use {guilabel}`View full publishing history` of the package (link at the top right of the {guilabel}`Overview`):

  `https://launchpad.net/ubuntu/+source/<name_of_the_package>/+publishinghistory`

  For example: [Publishing history of hello package in Ubuntu](https://launchpad.net/ubuntu/+source/hello/+publishinghistory).


## Further reading

* {ref}`merges-syncs`
