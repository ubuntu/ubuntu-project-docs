(dmb-manage-packagesets)=
# DMB Manage Packagesets

```{note}
This page is about how to create and modify a Packageset.

Related information about how to become an uploader of a Packageset can
be found at {ref}`dmb-joining-packageset`.
```

(dmb-packagesets)=
## What is a Packageset

Packagesets are a method to provide fine grained upload permissions without
always managing everything individually per user. They allow to define a
list of packages per set and per Ubuntu release, to then allow developers
upload permissions to such a set.

Being per release allows them to evolve over time as Ubuntu changes, without
such changes affecting the maintenance of existing releases. For example a
package name might stay but contain something different in a late release.
Or a definition by either of the {ref}`dmb-types-of-packagesets` will imply
that it covers a different set of packages in different releases.

In regard to their definition they exist are defined in the
Launchpad database accessible by API (using the `edit-acl` command).
Think of it as a relation between launchpad personas and a list of packages.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
flowchart TD
    %% Entities
    Developers["Developer"]
    LPPersona["Launchpad team controlled by the DMB"]
    PackageSet["Packageset in Launchpad database"]
    Packages["Source packages per release"]

    %% Transitions
    Developers -->|"<i>member of</i>"| LPPersona
    LPPersona -->|"<i>associated to</i>"| PackageSet
    Packages -->|"<i>in package list</i>"| PackageSet
```

For easy viewing, there are simple text files representing the current
state of the Packagesets. That includes the name of the sets, their
description, the list of packages included as well as the developers allowed
to upload to it. These files can be found at
[~ubuntu-archive/packagesets](https://ubuntu-archive-team.ubuntu.com/packagesets/).

Consider creating a Packageset once we have:

* Two or more PPU uploaders with the same set.

* Two or more related packages that always belong together.

* The grouping of those packages needs to make logical sense.

The application process to {ref}`dmb-become-packageset-uploader` is similar
to all other developer upload permission applications. In this case applying to
a particular Packageset instead of for example {ref}`dmb-joining-motu`.

(dmb-types-of-packagesets)=
## Types of Packagesets

Historically there a few different kinds of Packagesets.
There are two common variants, one mostly reflect seeds and the other
is logically defined by the description.
Further variants that have been established to cover special cases
like Personal packagesets and OEM metapackage packagesets.

* **Logical Packagesets** needs a *detailed description*. This is so that
  developers can mail `devel-permissions` after the set is created in order to
  have packages added.
  A DMB member then needs to judge the description against the requested change
  and may apply the change if they decide it is warranted.

* **{ref}`seeds` based Packagesets** are instead defined by what is
  generally seeded and supported for a particular Ubuntu variant or has a
  direct relation to a seed named in the description.
  One has to be careful as there are exceptions that force a seed based
  packageset seeds to not be just equal to the seed.
  defies the purpose (See below about details on these cases).
  * These packagesets used to be fully generated based on
    [this code](https://code.launchpad.net/~developer-membership-board/+git/packageset)
    and the logic tries to detect how sources are shared between flavours to
    remove those. But that has proven to cause to cause too many exceptions.
    Therefore they have - for now - become defined by the seeds, but modified
    manually on request.
  * While currently not automated, the DMB still aims for *eventual
    consistency*. A seed based packageset should converge to be based on the
    seed, plus exceptions (previously maintained in the script in git).
    Just like packagesets based on a logical definition converge on the text
    of their definition.
  * Common reasons for exceptions to a pure seed = packageset approach are:
    * Consider to remove a package from a set if is is in the related seed, but
      so central and impactful, that adding it would effectively make the
      Packageset to require core-developer permission level. That would defy
      the purpose of being a stepping stone for upload permissions as on one
      could join until the could get core-developer rights anyway.
      Examples of that would be: `grub2`, `systemd`, or `cloud-init`.
    * Consider to remove a package from a set if it is also claimed by other
      seeds or common use case. In that case it often, but not always, is only
      updated by Ubuntu core-developers.
      Examples of that would be: `vim`, `dhcpcd` or `tzdata`
    * Consider to add a package to a set if it is not in the seeds, but such a
      common use case for the Packageset that the same set of people that care
      about the rest is likely to also maintain these packages.
      Examples of that would be: `docker.io` or `valkey`

* **Personal Packagesets** are used where an individual has a special reason for
  upload rights to a large number of packages that the DMB expects to need to
  manage frequently. For such a case a "personal packageset" for this person,
  named "`personal-<lpid>`" can be created.
  * When the associated developers are granted Core Dev those packagesets can
    be removed.
  * See the thread starting at [May 2016](https://lists.ubuntu.com/archives/devel-permissions/2016-May/000924.html),
    and subsequent months for an example.

* The **canonical-oem-metapackages Packageset** is glob based. The exact glob is
  defined in the packageset description and is expanded according to the list of
  source packages in the Ubuntu Archive for a given series. Any DMB member may
  update the packageset according to the glob expansion at any time without
  needing further consultation. However, this is now done automatically with
  [this script](https://git.launchpad.net/~developer-membership-board/+git/oem-meta-packageset-sync/tree/oem-meta-packageset-sync).
  The script is "owned" by the DMB, who is the gatekeeper for changes to the
  script, but run and managed on behalf of the DMB by the
  [Archive Admin team](https://launchpad.net/~ubuntu-archive/+members). To make
  this work, this packageset is owned by the Archive Admin team.
  * The expected nature of the packageset, to which the DMB grants upload access,
    relies on the MIR team's requirements for these packages, defined at
    {ref}`mir-exceptions-oem`.
  * [Background thread](https://lists.ubuntu.com/archives/devel-permissions/2020-July/001542.html)
  * Decided at the [DMB meeting of 2020-08-11](https://irclogs.ubuntu.com/2020/08/10/%23ubuntu-meeting.html#t19:01)
  * Documented at [OEM Archive](https://wiki.ubuntu.com/OEMArchive)

### Why are seed based Packagesets not generated?

(dmb-modify-packagesets)=
## How to modify a Packageset

One can modify the definition, the members or the associated package list.

This is the more common task compared to {ref}`creating a set <dmb-create-packagesets>`.

### How to modify a Packageset definition

* If necessary, we can modify the description later on following a full DMB vote.
  Such requests would usually be driven by members of a Packageset that want to
  expand the set or better define it - often to match how Ubuntu has evolved
  since the set was created.
  In such a case the DMB should consider if, due to the update of the
  definition, it would need to reconsider:
  * the set of packages in the packageset, and if they should be adjusted
  * the set of uploaders to the packageset, and if they should be adjusted.

### How to modify members of a Packageset

* Modification of the membership list for an existing Packageset team can
  be done directly by the DMB. A DMB member should go to the Packageset
  uploader team page, and add (or if needed remove) the applicant to the team.

  * If not already a member, add the applicant to either
   [`~ubuntu-dev`](https://launchpad.net/~ubuntu-dev/+members) or
   [`~ubuntu-uploaders`](https://launchpad.net/~ubuntu-uploaders/+members).
   See {ref}`dmb-teams-to-add-uploaders-to`.

### How to modify a new Packageset list of covered packages

* Modification of the package list for an existing Packageset can also be done
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

(dmb-create-packagesets)=
## How to create a new Packageset

This step is comprised of creating the Packageset team managed by the DMB
as well as creation of the Packageset associated with it.

More often than creating one would {ref}`modify an existing package
set<dmb-modify-packagesets>`.

### Create the associated launchpad team

We create initially Packagesets with just one uploader, which is a launchpad
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
   (In rare cases the DMB may require membership of Packageset uploaders, in that
    case add it to [`~ubuntu-dev` member page](https://launchpad.net/~ubuntu-dev/+members) instead)

### Create the actual Packageset

   * If the action requires creation of a new Packageset or PPU, or (rarely)
     changes to the uploader for a Packageset or PPU, it must be done by the TB,
     so the DMB member must:

     1. For a new Packageset, create a new uploader team (see {ref}`dmb-packagesets` section)

        * For a new PPU, the uploader is the applicant

     2. Open a bug against the [ubuntu-community project](https://launchpad.net/ubuntu-community), and the bug description should include the exact [`edit-acl`](https://git.launchpad.net/ubuntu-archive-tools/tree/edit-acl) command to run.

        * For PPU creation, [file a bug with this subject](https://bugs.launchpad.net/ubuntu-community/+filebug?field.title=[TB/DMB]%20PPU%20for%20)
          and include the PPU member name

        * For Packageset creation (or uploader team change),
          [file a bug with this subject](https://bugs.launchpad.net/ubuntu-community/+filebug?field.title=[TB/DMB]%20Packageset%20%20for%20)
          and include the Packageset name

        * In the bug, if creating a new Packageset, request the TB create the
          Packageset, setting the DMB as owner:

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
