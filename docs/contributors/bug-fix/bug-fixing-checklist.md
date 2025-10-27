(bug-fixing-checklist)=
# Bug fixing checklist

## 1. Get code and tarball

For the tarball, you have to be inside the repository folder. You must checkout
to the version you need before getting the tarball.

- [ ]  `git-ubuntu clone <source_package_name> [destination_folder]`

  - [ ]  Tarball: `git-ubuntu export-orig`

- [ ]  If not there, from `ubuntu-dev-tools` package: `pull-lp-source <source_package_name> [release|version]`

- [ ]  If not there, from `ubuntu-dev-tools` package: `pull-debian-source <source_package_name> [release|version]`

- [ ]  Or, from `devscripts`: `debcheckout <source_package_name>`

  - [ ] Tarball: `origtargz`

- [ ] Or, from `devscripts`: `dget <url_dsc_file_of_the_package (tracker.debian.org/salsa.debian ... look on this webs for this)>`

- [ ] Or, from `git-buildpackage`: `gpb import-dsc --pristine-tar <url_dsc_file_of_the_package (tracker.debian.org/salsa.debian ... look on this webs for this)>`

  - [ ] Tarball: `gbp import-orig --uscan` or `uscan` or `origtargz`

## 2. Bug fix

- [ ]  Step-to-reproduce (for later copy-paste)

  ```none

  ```

- [ ]  Record bad case (for later copy-paste)

  ```none

  ```

- [ ] Code the fix:

  - [ ] Changes are under `debian/` folder or the package is Native
    (`debian/source/format` is Native 1.0)

  - [ ] Or patching: Changes are outside `debian/` folder or incorporating a
    patch-as-is and `debian/source/format` is Quilt 3.0:

    - [ ] Create the patch using `dquilt` -- **don't forget** to activate the
      new patch BEFORE doing the changes!)

      - [ ] Or using `git diff`

      - [ ] Or using Git Patch in VS Code

      - [ ] Or `edit-patch` (for incorporating/changing an existing one)

    - [ ] Check the patch header:

      - [ ] If it doesn't exist, create a new one: `quilt header -e --dep3 <patch_file>`

      - [ ] Check header style:

        - [ ] Not references to the functions after @@

        - [ ] Path of the files are with a and b

        - [ ] New lines are with a dot (.) in the Description (no empty lines)

- [ ]  Record good case (for later copy-paste)

  ```none

  ```

## 3. Build new package

- [ ] `debian/changelog` (use ```dch -i```)

  - [ ]  Version: for an SRU, it increments decimal. See {ref}`version-strings` for more.

  - [ ]  Change UNRELEASED to series name

  - [ ]  Respect the format:

    - [ ]  Check there are ≤ 70 chars per line

    - [ ]  Check no trailing spaces are present

    - [ ]  Indent has 2 spaces since last bullet point (or the beginning)

    - [ ]  Bullet points go from `*` (more general) then `-`, then `+`

    - [ ]  `(LP: #XXXXXXXX)` is present if a fix for a LP bug is being released

    - [ ]  `(LP: XXXXXXXX)` is present if a LP bug is referenced

    - [ ]  If Debian related bug is mentioned: `Closes: NNNNNNN`

    - [ ]  If Debian related bug is being fixed: `Closes: #NNNNNNN`

    - [ ]  Optional: A "Thanks to" is present if you are not the author of the
      code being submitted (normally when submitting patches)

- [ ]  `debian/control`: check Maintainers field is set to Ubuntu Developers (if
  not, use `update-maintainer` from `ubuntu-dev-tools` -- this is more frequent
  in merges)

- [ ] Optional: Get {command}`lintian` output

  ```none
    
  ```

- [ ] Optional: Autopkgtest output (DEP-8 tests)

  - [ ] Locally

  - [ ] Using the PPA's package (Recommended): `ppa tests ${ppa_address} --release ${codename}`


## 4. (optional) PPA :

```none
    
```

- [ ]  Change Build types

- [ ]  {command}`dput`-signed {file}`changes` file


## 5. (optional) SRU/MIR/FFe template

- [ ] [SRU](https://documentation.ubuntu.com/sru/en/latest/reference/bug-template/)

- [ ] {ref}`mir-reporters-template`

- [ ] {ref}`FFe <feature-freeze-exceptions>`:

  ```
  [[ Feature Freeze Exception ]]
  [Description]
     * A description of the proposed changes, with sufficient detail to estimate their potential impact on the distribution
  [Rationale]
     * A rationale for the exception, explaining the benefit of the change
  [Additional information]
     * Any additional information which would be helpful in considering the decision:
       -  If the upload is a new upstream microrelease, the relevant part of the upstream changelog and/or release notes.
       -  An explanation of the testing which has been performed on the new version in Ubuntu (main features screenshot), including verification that the new package:
         + builds (attach build.log)
         + installs and upgrades (attach install log)
  [Original Report]
  ----------------------------
  ```


## 6. MP

- [ ]  Target Branch: `ubuntu/<UbuntuSeries>-devel` for bug fixing or
  `debian/sid` for merges

- [ ]  Reviewers : `$(ubuntu-upload-permission --list-uploaders <package>)` and
  `canonical-<your-team>` (e.g. `canonical-server-reporter` for Server team
  members)

- [ ]  Description:

  - [ ]  PPA

  - [ ]  Optional: Tags for merge bugs

  - [ ]  G/B cases or refer to SRU template

  - [ ]  (optional) autopkgtest output

  - [ ]  (optional) Lintian output


## After submission and approval

- [ ] **7.** Upload the package (or {ref}`look for Sponsorship <sponsorship>`).

  - [ ] Check that it builds ok and it gets published in the archive (`https://launchpad.net/ubuntu/+source/<package_name>`) or check mail.

  - [ ] Change the MP status to "Merged"

- [ ]  **8.** Tracking migration: check `update_excuses`

- [ ]  **9.** If SRU: Verification: change the tags in LP bug for the done ones
  instead of the needed ones

- [ ]  **10.** (optional) When Fix Released: Remove `server-next`/`server-todo`
  tags in the LP bug

