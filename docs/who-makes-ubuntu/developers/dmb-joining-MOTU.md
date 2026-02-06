(dmb-joining-motu)=
# MOTU

MOTU, or "Masters of the Universe", maintain the collection of packages in the `universe` and `multiverse` components (i.e. packages not in `main`).
They are [members of the MOTU team](https://launchpad.net/~motu) in Launchpad.

In terms of the {ref}`uploaders-journey`, MOTU are {ref}`experts <upload-path-expert>` in Ubuntu Development, answering questions of other developers to expand their understanding of packaging work, and providing guidance for prospective Ubuntu developers regarding technical issues.

They understand packaging concepts, having substantial experience of uploading packages through a sponsor.
They then apply this knowledge by uploading new packages to, and updating existing packages in, the `universe` component.
MOTU may also contribute to the `main` component in cooperation with a {ref}`dmb-joining-core-dev`.


(motu-training-and-preparation)=
## Training and preparation

Whether MOTU upload rights should be granted is a question of both skill and trust, with the latter often seen as the more imperative.
Trust, in the context of Ubuntu packaging, means:

* Doing it the right way, even when not required

* Picking the more difficult solution when it will give better results

* Welcoming constructive criticism, without getting defensive

* Asking for help or advice if you're uncertain

* "Measuring twice, cutting once"

* Highlighting, not hiding, the thing you broke

* Following through on tasks you commit to do

* Helping someone succeed, even though you don't agree


### Trust

Demonstration of trust is more important than mastery of skills, because a lack of skill can be solved by more training and practice.
If someone demonstrates a lack of trustworthiness, that is not so easily fixed! 

Everyone makes mistakes, and an error caused by lack of experience can itself be a learning opportunity, and a chance to demonstrate trustworthiness.
So watch for opportunities to work on challenging problems outside your comfort zone.
Keep track of both experiences that went well, and disasters that you used as valuable learning experiences.


### Skill

At a minimum, you must have mastery of the same skills as a {ref}`Package Set Uploader <dmb-joining-packageset>` would have.
Work through all the items on that page's {ref}`training and preparation <packageset-training-and-preparation>` section, focusing on anything you're uncomfortable with.

The main difference with MOTU is *breadth*.
Make sure you have direct experience in these skills across a broader range of packages throughout the Archive, including types of software you've never worked on before.

More advanced packaging topics you should be comfortable with as a MOTU applicant include:

* Package merges from upstream, to go ahead of Debian's version

* {ref}`Ubuntu's release process <release-cycle>`, including the {ref}`Freeze Exception process <freeze-exceptions>`

* Understand the `main`/`universe` split, and how that affects dependencies

* {ref}`Seed management <seed-management>`

* The {ref}`Main Inclusion Review (MIR) <main-inclusion-review>`process

* [Component mismatches](https://ubuntu-archive-team.ubuntu.com/component-mismatches-proposed.html)

* Binary packages [not built from source (NBS)](https://ubuntu-archive-team.ubuntu.com/nbs.html)

* [Multi-arch issues](https://wiki.ubuntu.com/MultiarchCross)

* {ref}`Autopkgtest <how-to-run-package-tests>` writing, fixing, and understanding [of the spec](https://salsa.debian.org/ci-team/autopkgtest/-/blob/master/doc/README.package-tests.rst)

* {ref}`Proposed migration <proposed-migration>` basics, and the process in general

* {ref}`Transition basics <transitions>`, and the [library transitions process](https://ubuntu-archive-team.ubuntu.com/transitions/) more generally

You don't need to have completed tasks in all of the above topics, but should have direct and deep experience in at least some, and a solid understanding of most.
Be prepared to answer technical questions about these topics at the application meeting, as you'll likely be asked one or two.

Finally, an important element of MOTU is working with the wider Ubuntu development community.
Find a way to engage yourself with current community discussions and look for opportunities to contribute.


### Become a MOTU

First check the general requirements for {ref}`ubuntu-membership`.
You can then apply to the {ref}`dmb` using the {ref}`dmb-application`.


## Next steps

Common paths MOTU members follow are:

* {ref}`Core Dev <dmb-joining-core-dev>`

* [Other Ubuntu interest groups](https://wiki.ubuntu.com/Teams)

