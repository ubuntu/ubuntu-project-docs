(contribute)=

# How to contribute

This guide provides information necessary to contribute to this documentation.
If you're contributing for the first time, you might find the Canonical Open
Documentation Academy has helpful resources to
[get you started](https://documentationacademy.org/docs/howto/get-started/).

## Report an issue

To report a mistake on any page, or highlight some missing documentation,
[file an issue](https://github.com/ubuntu/ubuntu-project-docs/issues) in our
issues list on GitHub.

You can do this using the {guilabel}`Give feedback` button on any page, which will open a
new issue.

Make sure to provide enough information in the issue for us to understand what
is needed.

## Edit documentation online

Each documentation page has a **Contribute to this page** link in the top-right
corner (the pencil icon). Clicking this button opens the GitHub web editor
where you can propose changes to that page. The first time you click this
button, you will be prompted to create a **fork** of the documentation before
you can start editing.

Remember to first check the
[latest version](https://canonical-ubuntu-project.readthedocs-hosted.com/) of
our documentation and make your proposal based on that revision.

## Contribute on GitHub

If you are familiar with a Git development workflow, `fork` the
[Ubuntu Project docs repository](https://github.com/ubuntu/ubuntu-project-docs)
and contribute your change as a
[pull request](https://github.com/ubuntu/ubuntu-project-docs/pulls).

While this project is under construction, there will be a lot of movement in
many different areas. To ensure that your efforts don't get wasted due to
overlaps, please either **claim an open issue** or, if there is no issue for
what you want to work on, create a new issue first **before** working on your
pull request.

### Directory structure

All the documentation files are located in the `docs/` directory. The `docs/`
directory contains sub-directories corresponding to different
[Diátaxis](https://diataxis.fr/) sections:

* `explanation/`
* `howto/`
* `reference/`
* `tutorial/`

Add new articles in the appropriate directory. You can read about
[how Ubuntu implements Diátaxis for documentation](https://ubuntu.com/blog/diataxis-a-new-foundation-for-canonical-documentation).

## Build the documentation locally

Follow these steps to build the documentation on your local machine.


### Prerequisites

* Git
* The `make` tool

    :::{note}
    The `make` command is compatible with Unix systems. On Windows,
    [install Ubuntu with WSL](https://documentationacademy.org/docs/howto/get-started/using_wsl/).
    :::


### Procedure

1. Fork the [Ubuntu Project docs repository](https://github.com/ubuntu/ubuntu-project-docs). Visit [Fork a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) for instructions.

2. Clone the repository to your machine:
    ```none
    git clone git@github.com:<your_user_name>/ubuntu-project-docs.git
    ```

3. Create a new branch:
    ```none
    git checkout -b <your_branch_name>
    ```

4. Change to the `docs/` directory and make your contribution:
    ```
    cd docs
    ```

5. Build a live preview of the documentation from within the `docs/` directory:
    ```
    make run
    ```
    You can find all the HTML files in the `.build/` directory.

    `make run` uses the Sphinx `autobuild` module, so that any edits you make (and save) as you work are applied, and the built HTML files refresh immediately.

6. Review your contribution in a web browser by navigating to [127.0.0.1:8000](http://127.0.0.1:8000/).

7. Push your contribution to GitHub and create a pull request against the original repository.


## Documentation format

The Ubuntu Project documentation is built with Sphinx using a combination of the MyST flavor of the Markdown and reStructuredText mark-up languages. MyST is preferred for new content. If you're new to this, see our guides:

* [MyST style guide](https://canonical-starter-pack.readthedocs-hosted.com/latest/reference/style-guide-myst/)
* [reStructuredText style guide](https://canonical-starter-pack.readthedocs-hosted.com/latest/reference/style-guide/)


### Semantic mark-up

We encourage (though not mandate) the use of semantic mark-up where possible. See [Roles](https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html) in Sphinx documentation for an overview of inline semantic roles available by default. The syntax is:

| MyST | reStructuredText |
| --- | --- |
| `` {role}`term` `` | `` :role:`term` `` |

The following roles are especially useful:

`code`
: Source-code snippets.

`command`
: Command-line interface (CLI) commands.

`file`
: Names of files and directories (including path).

`guilabel`
: Graphical user interface (GUI) elements: button, widgets, labels, ...

`kbd`
: Keyboard keys and shortcuts. Example:`` {kbd}`Shift+F1` `` (rendered as {kbd}`Shift+F1`).

`manpage`
: Link to an Ubuntu manual page. Example:`` {manpage}`man(1)` `` (rendered as a live link: {manpage}`man(1)`).

`pkg`
: Linux package name (this role is custom to this documentation project).


## Testing the documentation

Test your changes before submitting a pull request. Run the following commands from within the `docs/` directory to test the documentation locally:

| command  | use |
|---------|-----|
| `make spelling` | Check for spelling errors; this command checks the HTML files in the `_build` directory. Fix any errors in the corresponding Markdown file |
| `make linkcheck` | Check for broken links |
| `make woke` | Check for non-inclusive language |
| `make pa11y` | Check for accessibility issues |

:::{note}
For the `make spelling` command to work, you must have the `aspell` spellchecker installed. You can install it with `sudo apt install aspell`.
:::


## Open Documentation Academy

If you've never contributed to an open source project before, the [Open Documentation Academy](https://documentationacademy.org/) (ODA) is a great way to begin.

The Open Documentation Academy (ODA) is an initiative led by the documentation team at Canonical to encourage open source contributions from the community, and to provide help, advice and mentorship within a friendly and welcoming environment.

A key aim is to lower the barrier of entry to successful open-source software contributions by making documentation into the gateway, and it’s a great way to make your first open source contributions to projects like ours. Contributors gain real experience, structured support and recognition, while we benefit from improvements to our documentation and community feedback.

The best way to get started is to take a look at our [project-related documentation tasks](https://github.com/canonical/open-documentation-academy/issues) and read our [Getting started](https://discourse.ubuntu.com/t/getting-started/42769) guide. Tasks typically include testing and fixing tutorials, updating outdated pages, restructuring large documents and anything else you may want to suggest. We'll help you see those tasks through to completion.

Stay in touch either through the task list, or through one of the following locations:

* [Discussion forum](https://discourse.ubuntu.com/c/community/open-documentation-academy/166) on the Ubuntu Community Hub.
* [Matrix](https://matrix.to/#/#documentation:ubuntu.com) for interactive chat.
* [Fosstodon](https://fosstodon.org/@CanonicalDocumentation) for the latest updates and events.

In addition to the above, we have a weekly [Open Documentation Hour](https://discourse.ubuntu.com/t/open-documentation-hour-schedule/45291) at 16:00 UTC each Friday. Everyone is welcome.
