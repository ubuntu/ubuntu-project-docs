(how-to-request-an-upload)=
# How to request an upload

After fixing a bug in a package or when introducing a new package to the distribution, the updated package needs to be uploaded to the Ubuntu Archive. If you don't have upload rights to the Archive, find a sponsor who does to upload your changes. This article describes, how to request an upload.

:::{admonition} **Sponsorship** series
The article series provides guidance on requesting sponsorship and sponsoring.

Overview:
:   * {ref}`sponsorship`

For contributors:
:   * {ref}`how-to-find-a-sponsor`
    * {ref}`how-to-request-an-upload` (this article)
    * {ref}`how-to-request-a-sync`

For sponsors:
:   * {ref}`how-to-review-a-merge-proposal`
    * {ref}`how-to-sponsor-an-upload`
    * {ref}`how-to-sponsor-a-sync`
:::

Follow the general {ref}`guidance for contributors <how-to-contribute>` to have your changes properly prepared for sponsorship. Remember that someone else needs to understand what you've done.

For any non-trivial change, it's good practice to discuss your plans with a potential sponsor (ask in {matrix}`devel`) *after* you think you know what needs to be done, but *before* you've actually done it. Often, an experienced developer can offer alternative approaches that may save you time or provide better results.


## Seek upload sponsorship

Submit a {ref}`Merge Proposal (MP) <how-to-submit-a-merge-proposal>` with your changes. Ensure to:

* Include the Launchpad bug that is to be fixed by this upload in the {file}`changelog` file in the form `LP: #123456` (see {ref}`write-the-changelog-entry`).
* Select the `ubuntu-sponsors` team as the reviewer for the MP.
* Link the Launchpad bug to the MP (using the {guilabel}`Link a bug report` link).
