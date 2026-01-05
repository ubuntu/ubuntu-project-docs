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

* Each packageset needs a *description*. This is so that developers can mail
  `devel-permissions` after the set is created in order to have packages added.
  One DMB member then needs to judge the description against the requested change
  and may make it if they decide it is warranted.

* We create packagesets with just one uploader, which is a team that we then add
  developers to. The team should be configured like so:

  * Owned by the DMB (but without having the DMB as a member).

  * Self renewal.

  * 720 day expiry period.

    ```{note}
    For 'Ubuntu Flavor' packageset teams, [the TB requested](http://ubottu.com/meetingology/logs/ubuntu-meeting-2/2019/ubuntu-meeting-2.2019-06-04-19.04.moin.txt) a 180 day expiry period.
    ```

  * `~ubuntu-core-dev` as a member.

  * Member of `~ubuntu-uploaders` (in rare cases the DMB may require membership
    of packageset uploaders: in this case make the team a member of `~ubuntu-dev`
    instead.)

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
