(membership-in-motu)=
# Membership in MOTU

MOTU, or "Masters of the Universe", maintain the large collection of packages
in the `universe` and `multiverse` components (i.e. packages not in `main`).

## Application process

1. Keep an eye on the
   [Developer Membership Board (DMB) agenda](https://wiki.ubuntu.com/DeveloperMembershipBoard/Agenda),
   noting when the upcoming meetings are and if there is a queue of applicants;
   if so, make sure to add yourself to the "Ubuntu MOTU Developer Applications"
   bullet, since only 2 applications are considered per meeting.

1. {ref}`motu-training-and-preparation`, as needed.

1. [Prepare an application form](https://wiki.ubuntu.com/DeveloperMembershipBoard/ApplicationProcess)
   in the Ubuntu Wiki.

1. Collect **endorsements** from people who have reviewed or sponsored your
   packages, or worked with you on noteworthy packaging efforts. If you work
   for Canonical, seek out diversity in your endorsers by looking outside your
   immediate team. Since MOTU is more focused on community maintainers, their
   testimonials are of particular value. Even words from noteworthy Debian
   maintainers can carry weight for MOTU applications.


(motu-training-and-preparation)=
## Training and preparation

Whether MOTU upload rights should be granted is a question of both skill and
trust, with the latter often seen as the more imperative.

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

Demonstration of trust is more important than mastery of skills, because a lack
of skill can be solved by more training and practice. If someone demonstrates a
lack of trustworthiness, that is not so easily fixed! 

Everyone makes mistakes, and an error caused by lack of experience can itself
be a learning opportunity, and a chance to demonstrate trustworthiness. So
watch for opportunities to work on challenging problems outside your comfort
zone. Keep track of both experiences that went well, and disasters that you
used as valuable learning experiences.


### Skill

At a minimum, you must have mastery of the same skills as a
{ref}`Package Set Uploader <membership-in-packageset>` would have. Work through
all the items on that page's
{ref}`training and preparation <packageset-training-and-preparation>` section,
focusing on anything you're uncomfortable with.

The main difference with MOTU is *breadth*. Make sure you have direct experience
in these skills across a broader range of packages throughout the Archive,
including types of software you've never worked on before.

More advanced packaging topics you should master as a MOTU applicant include:

* Package merges from upstream, to go ahead of Debian's version

* [Ubuntu's release process](https://wiki.ubuntu.com/UbuntuDevelopment/ReleaseProcess),
  including the
  [freeze exception process](https://wiki.ubuntu.com/FreezeExceptionProcess)
* Understand the `main`/`universe` split, and how that affects dependencies

* {ref}`Seed management <seed-management>`

* The {ref}`Main Inclusion Review (MIR) <main-inclusion-review>`process

* [Component mismatches](https://ubuntu-archive-team.ubuntu.com/component-mismatches-proposed.html)

* Binary packages
  [not built from source (NBS)](https://ubuntu-archive-team.ubuntu.com/nbs.html)

* [Multi-arch issues](https://wiki.ubuntu.com/MultiarchCross)

* {ref}`Autopkgtest <package-tests>` writing and fixing, and understanding
  [of the spec](https://salsa.debian.org/ci-team/autopkgtest/-/blob/master/doc/README.package-tests.rst)

* {ref}`Proposed migration <proposed-migration>` basics, and the
  [process in general](https://wiki.ubuntu.com/ProposedMigration)

* {ref}`Transition basics <transitions>`, and the
  [library transitions process](https://ubuntu-archive-team.ubuntu.com/transitions/) 
  more generally

You don't need to have completed tasks in all of the above topics, but should
have direct and deep experience in at least some, and a solid understanding of
most. Be prepared to answer technical questions about these topics at the
application meeting, as you'll likely be asked one or two.

Finally, an important element of MOTU is working with the wider Ubuntu
development community. Find a way to engage yourself with current community
discussions and look for opportunities to contribute.


## Further reading

Common paths MOTU members follow are:

* {ref}`Core Dev <membership-in-core-dev>`

* [Ubuntu Flavors](https://wiki.ubuntu.com/UbuntuFlavors)

* [Ubuntu derivatives](https://wiki.ubuntu.com/DerivativeTeam/Derivatives)

* [Other Ubuntu interest groups](https://wiki.ubuntu.com/Teams)

