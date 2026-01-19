(dmb-manage-package-sets)=
# DMB Manage Package Sets

```{note}
This page is about how to create and modify a package set.

Related information about how to become an uploader of a package set can
be found at {ref}`dmb-joining-package-set`.
```

(dmb-package-sets)=
## What is a Package set

Package sets are a method to provide fine grained upload permissions without
always managing everything individually per user. They allow to define a
list of packages per set and per Ubuntu release, to then allow developers
upload permissions to such a set.

Being per release allows them to evolve over time as Ubuntu changes, without
such changes affecting the maintenance of existing releases.

In regard to their definition they exist are defined in the
Launchpad database accessible by API (using the `edit-acl` command).
Think of it as a relation between launchpad personas and a list of packages.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
flowchart TD
    %% Entities
    Developers["Developer"]
    LPPersona["Launchpad team controlled by the DMB"]
    PackageSet["Package Set in Launchpad database"]
    Packages["Source packages per release"]

    %% Transitions
    Developers -->|"<i>member of</i>"| LPPersona
    LPPersona -->|"<i>associated to</i>"| PackageSet
    Packages -->|"<i>in package list</i>"| PackageSet
```

For easy viewing, there are simple text files representing the current
state of the package sets. That includes the name of the sets, their
description, the list of packages included as well as the developers allowed
to upload to it. These files can be found at
[~ubuntu-archive/packagesets](https://ubuntu-archive-team.ubuntu.com/packagesets/).

Consider creating a package set once we have:

* Two or more PPU uploaders with the same set.

* Two or more related packages that always belong together.

* The grouping of those packages needs to make logical sense.

The application process to {ref}`dmb-become-package-set-uploader` is similar
to all other developer upload right applications. In this case applying to a
particular package set instead of for example {ref}`dmb-joining-motu`.

## Two types of package sets

Historically there are two kinds of package sets, those that mostly reflect
seeds and those that are logically defined by their description.

* A logical package set needs a *detailed description*. This is so that
  developers can mail `devel-permissions` after the set is created in order to
  have packages added.
  A DMB member then needs to judge the description against the requested change
  and may apply the change if they decide it is warranted.

* A {ref}`seeds` based package set is instead *mostly* defined by what is seeded
  for a particular Ubuntu variant. That is not strictly only and exactly the
  content of an ISO or image, but might also include related supported seeds
  that represent common use cases that are not default installed.

### Why are seed based package sets not generated?

The text above says "Mostly" as there are often are a few packages that
make sense to be added or removed when compared to the pure list that would
come out of the seeds to make it more practical.

Such could cases could be:

* Consider to remove a package from a set if is is in the related seed, but so
  central and impactful, that adding it would effectively make the package set to
  require core-developer permission level. This not only reduces impact, it also
  avoids that all package sets are very hard to join as they need core-dev
  like requirements to join as an uploader.

* Consider to remove a package from a set if it is also claimed by other seeds.
  In that case it often, but not always, is only updated by Ubuntu core-developers.

* Consider to add a package to a set if it is not in the seeds, but such a
  common use case for the package set that the same set of people that care
  about the rest is likely to also maintain these packages.

If in doubt it is worthwhile to compare a few sets of data to make decisions
what might need to be added or dropped from a package set. Here an example
for the ubuntu-server team:

* Fetch the current package set like `./edit-acl query --series resolute --packageset ubuntu-server`
* Look at the seeds
  * To do so fetch [ubuntu seeds](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/ubuntu/tree/)
    and [platform seeds](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/platform/tree/),
    to then check for anything related to server.
  * Or check the [germinated output](https://ubuntu-archive-team.ubuntu.com/germinate-output/ubuntu.resolute/)
    for an artifact you are interested in.
  * Yet one has to admit that seeds are hard to read, because they are expanded by
    dependencies and evaluated for various slightly different artifacts.
    Gladly what you need to compare, is often nicely approximated by checking what
    a team with the a related responsibility is subscribed to. And if they are
    not subscribed despite being in the germinated seed it would often be a case
    of overlapping responsibilities that suggest core-developer rights anyway.
    Therefore consider `curl --silent http://reports.qa.ubuntu.com/m-r-package-team-mapping.json | jq -r '."ubuntu-server"[]'`
    to be the most simple solution.
* Out of such a three way comparison in an example of 2025 we generated and discussed [this list](https://lists.ubuntu.com/archives/devel-permissions/2025-September/002906.html)

(dmb-modify-package-sets)=
## How to modify a Package set

One can modify the definition, the members or the associated package list.

This is the more common task compared to {ref}`creating a set <dmb-create-package-sets>`.

### How to modify a Package set definition

* If necessary, we can modify the description later on following a full DMB vote.

### How to modify members of a Package set

* Modification of the membership list for an existing package set team can
  be done directly by the DMB. A DMB member should go to the package set's
  uploader team page, and add (or if needed remove) the applicant to the team.

  * If not already a member, add the applicant to either
   [`~ubuntu-dev`](https://launchpad.net/~ubuntu-dev/+members) or
   [`~ubuntu-uploaders`](https://launchpad.net/~ubuntu-uploaders/+members).
   See {ref}`dmb-teams-to-add-uploaders-to`.

### How to modify a new Package set list of covered packages

* Modification of the package list for an existing package set can also be done
  directly by the DMB. This requires using the tool
  [`edit-acl`](https://git.launchpad.net/ubuntu-archive-tools/tree/edit-acl).

  * Example: (replace `add` with `delete` to remove a package instead of adding):

    ```none
    edit-acl -S $RELEASE -P $PACKAGESET -s $PACKAGE add
    ```

  * Sometimes a package or use case is new, but sometimes it is valid for all
    releases, in that case the command should be repeated for all supported releases:

    ```none
    for RELEASE in $(distro-info --supported); do edit-acl ...; done
    ```

(dmb-create-package-sets)=
## How to create a new Package set

This step is comprised of creating the package set team managed by the DMB
as well as creation of the package set associated with it.

More often than creating one would {ref}`modify an existing package
set<dmb-modify-package-sets>`.

### Create the associated launchpad team

We create initially package sets with just one uploader, which is a launchpad
team that we then later add developers to.

1. Start at [new team registration page](https://launchpad.net/people/+newteam).

2. Make the description to match what was proposed and approved by the DMB

3. Make sure {guilabel}`Membership Policy` is *Restricted Team*.

4. Set both the {guilabel}`Subscription Period` and {guilabel}`Self Renewal Period`
   to 720 (or 180 for 'flavor' teams).

5. Change renewal option to *invite them to renew their own membership*.

6. Create the team.

7. On the new team page:

   1. Click {guilabel}`Change Details` and then {guilabel}`Change Owner`.

   2. Change the team owner to `developer-membership-board`.

8. On the new team member page:

   1. Add `ubuntu-core-dev`.

   2. Edit `ubuntu-core-dev` membership expiration to *Subscription Expires: Never*.

   3. Remove (deactivate) yourself.

   4. Remove (deactivate) `developer-membership-board` (membership, keep ownership).

9. Go to [`~ubuntu-uploaders` member page](https://launchpad.net/~ubuntu-uploaders/+members)
   and add the new team as a member.
   (In rare cases the DMB may require membership of package set uploaders, in that
    case add it to [`~ubuntu-dev` member page](https://launchpad.net/~ubuntu-dev/+members) instead)

### Create the actual package set

   * If the action requires creation of a new package set or PPU, or (rarely)
     changes to the uploader for a package set or PPU, it must be done by the TB,
     so the DMB member must:

     1. For a new package set, create a new uploader team (see {ref}`dmb-package-sets` section)

        * For a new PPU, the uploader is the applicant

     2. Open a bug against the [ubuntu-community project](https://launchpad.net/ubuntu-community), and the bug description should include the exact [`edit-acl`](https://git.launchpad.net/ubuntu-archive-tools/tree/edit-acl) command to run.

        * For PPU creation, [file a bug with this subject](https://bugs.launchpad.net/ubuntu-community/+filebug?field.title=[TB/DMB]%20PPU%20for%20)
          and include the PPU member name

        * For package set creation (or uploader team change),
          [file a bug with this subject](https://bugs.launchpad.net/ubuntu-community/+filebug?field.title=[TB/DMB]%20Packageset%20%20for%20)
          and include the package set name

        * In the bug, if creating a new package set, request the TB create the
          package set, setting the DMB as owner:

          ```none
          edit-acl -S $RELEASE -p developer-membership-board -P $PACKAGESET -t admin create
          ```

        * Also request the TB set or change the uploader:

          ```none
          edit-acl -S $RELEASE -p $UPLOADER -P $PACKAGESET -t upload modify
          ```

        * Usually the commands should be repeated for all supported releases:

          ```none
          for RELEASE in $(distro-info --supported); do edit-acl ...; done
          ```
