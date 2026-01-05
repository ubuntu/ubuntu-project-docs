(dmb-manage-packagesets)=
# DMB Manage Package Sets

``{note}
This page is about how to create and modify a package set.
The related info about how to become a developers that is an uploaders
of a package set can be found at {ref}`dmb-joining-packageset`.
```

(dmb-packagesets)=
## What is a Package set

Packagesets are a method to provide fine grained upload permissions without
always managing everything individually per user. They allow to define a
lists of packages per set and per Ubuntu release, to then allow developers
upload permissions to such a set.

Being per release allows them to evolve over time as Ubuntu changes, without
such changes affecting the maintenance of existing releases.

In regard to their definition they exist are defined in the
Launchpad database accessible by API (using the `edit-acl` command).

For easy viewing, see there are simple text files pre rendering the current
state of the package sets, the list of packages included as well as the
developers allowed to upload to it at
[~ubuntu-archive/packagesets](https://ubuntu-archive-team.ubuntu.com/packagesets/).

Consider creating a packageset once we have:

* Two or more PPU uploaders with the same set.

* Two or more related packages that always belong together.

* The grouping of those packages needs to make logical sense.

The application process is more-or-less the same as for developer upload rights.
The differences are:

## Two types of package sets

Historically there are two kinds of package sets, those that mostly reflect
seeds and those that are just logically defined.

* A logical packageset needs a *description*. This is so that developers can mail
  `devel-permissions` after the set is created in order to have packages added.
  One DMB member then needs to judge the description against the requested change
  and may make it if they decide it is warranted.

* A {ref}`seeds` based packageset is instead mostly defined by what is seeded
  for a particular Ubuntu variant. That is not strictly only the content of an
  iso or image, but also the supported seeds that represent common use cases
  that are not default installed.

### Seed based packageset - why not just generated?

The text above says "Mostly" as there are often are a few packages that
make sense to be added or removed when compared to the pure list that would
come out of the seeds to make it more practical.

Such could cases could be:

* Consider to remove a package from a set if is is in the related seed, but so
  central and impactful, that adding it would effectively make the packageset to
  require core-developer permission level making it too hard to join as an
  uploader to that set.

* Consider to add a package to a set if it is not in the seeds, but such a
  common use case for the package set that the same set of people that care
  about the rest is likely to also maintain these packages.


If necessary, we can modify the description later on following a full vote,
either by email or in a meeting.

Quick set of steps for creating packageset team:

1. Start at [new team registration page](https://launchpad.net/people/+newteam).

2. Make sure {guilabel}`Membership Policy` is *Restricted Team*.

3. Set both the {guilabel}`Subscription Period` and {guilabel}`Self Renewal Period`
   to 720 (or 180 for 'flavor' teams).

4. Change renewal option to *invite them to renew their own membership*.

5. Create the team.

6. On the new team page:

   1. Click {guilabel}`Change Details` and then {guilabel}`Change Owner`.

   2. Change the team owner to `developer-membership-board`.

7. On the new team member page:

   1. Add `ubuntu-core-dev`.

   2. Edit `ubuntu-core-dev` membership expiration to *Subscription Expires: Never*.

   3. Remove (deactivate) yourself.

   4. Remove (deactivate) `developer-membership-board`.

8. Go to [`~ubuntu-uploaders` member page](https://launchpad.net/~ubuntu-uploaders/+members)
   (or, if appropriate, [`~ubuntu-dev` member page](https://launchpad.net/~ubuntu-dev/+members))
   and add the new team as a member.



## TODO

TODO
  # document seed based = seed based minus very core-dev'y
  # also seeded by a related supported-*
  # If claimed by multiple seeds, then it is more likely core-dev
  # mention how to generate pkgset vs seeds

TODO old content from KB

TODO MODIFY MEMBERS

   * Modification of the membership list for an existing packageset team can
     be done directly by the DMB. A DMB member should go to the packageset's
     uploader team page, and add the applicant to the team.

3. If not already a member, add the applicant to either
   [`~ubuntu-dev`](https://launchpad.net/~ubuntu-dev/+members) or
   [`~ubuntu-uploaders`](https://launchpad.net/~ubuntu-uploaders/+members).

   See {ref}`dmb-teams-to-add-uploaders-to`.

   * If applying for {ref}`dmb-joining-contributing` membership, the
     applicant should only be added to the
     [`~ubuntu-developer-members`](https://launchpad.net/~ubuntu-developer-members)
     team and nothing more.


TODO MODIFY PACKAGE LIST in a set

   * Modification of the package list for an existing packageset can also be done
     directly by the DMB. This requires using the [`edit-acl` tool](https://git.launchpad.net/ubuntu-archive-tools/tree/edit-acl)

     * Example: (replace `add` with `delete` to remove a package instead of adding):

       ```none
       edit-acl -S $RELEASE -P $PACKAGESET -s $PACKAGE add
       ```

     * Usually the command should be repeated for all supported releases:

       ```none
       for RELEASE in $(distro-info --supported); do edit-acl ...; done
       ```

TODO CREATE NEW PACKAGE SET

   * If the action requires creation of a new packageset or PPU, or (rarely)
     changes to the uploader for a packageset or PPU, it must be done by the TB,
     so the DMB member must:

     1. For a new packageset, create a new uploader team (see {ref}`dmb-packagesets` section)

        * For a new PPU, the uploader is the applicant

     2. Open a bug against the [ubuntu-community project](https://launchpad.net/ubuntu-community), and the bug description should include the exact [`edit-acl`](https://git.launchpad.net/ubuntu-archive-tools/tree/edit-acl) command to run.

        * For PPU creation, [file a bug with this subject](https://bugs.launchpad.net/ubuntu-community/+filebug?field.title=[TB/DMB]%20PPU%20for%20)
          and include the PPU member name

        * For packageset creation (or uploader team change),
          [file a bug with this subject](https://bugs.launchpad.net/ubuntu-community/+filebug?field.title=[TB/DMB]%20Packageset%20%20for%20)
          and include the packageset name

        * In the bug, if creating a new packageset, request the TB create the
          packageset, setting the DMB as owner:

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
