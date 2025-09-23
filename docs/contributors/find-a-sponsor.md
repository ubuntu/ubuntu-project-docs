(find-a-sponsor)=
# How to find a sponsor

The ability to upload directly to the Archive is carefully managed to ensure the stability and security of Ubuntu. New contributors don't have upload rights immediately -- they must request {ref}`sponsorship` from someone who *does* have upload rights to:

- Make changes to existing packages or incremental updates.
- Submit security updates or bug fixes.
- Introduce new packages to Ubuntu.


## Preparation

Follow the general {ref}`guidance for contributors <how-to-contribute>` to have your changes properly prepared for sponsorship. Remember that someone else needs to understand what you've done.

For any non-trivial change, it's good practice to discuss your plans with a potential sponsor (ask in {matrix}`devel`) *after* you think you know what needs done, but *before* you've actually done it. Often, an experienced developer can offer alternative approaches that may save you time or provide better results.


## Seeking sponsorship

Submit a {ref}`Merge Proposal (MP) <merge-proposals>` with your changes. Ensure to:

* Include the Launchpad bug that is to be fixed by this upload in the {file}`changelog` file in the form `LP: #123456` (see {ref}`write-an-effective-changelog`).
* Select the `ubuntu-sponsors` team as the reviewer for the MP.
* Link the Launchpad bug to the MP (using the {guilabel}`Link a bug report` link).
