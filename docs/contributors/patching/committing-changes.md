(committing-changes)=
# Committing your changes

Add all of your changed files to `git`. For example:

```none
$ git add debian/patches/my-changes.patch debian/patches/series
```


(the-commit-message)=
## The commit message

Structure your git commit message in changelog format to make later steps
easier, as follows:

```none
  * changed/or/added/files: [how it was fixed], [thanks to original author]
    (LP: #12345678)
```

Use "Thanks to" when you are not the author of the code being submitted. Note
that the maximum column width is 79.

Simple example:

```none
  * debian/patches/my-changes.diff: Reroute the inertial dampeners
    through the auxiliary power relay. Thanks to Miles O'Brien
    <miles.obrien@ds9.fed>. (LP: #19999999)
```

To add additional information to a commit message, or to format for readability,
use `--CL--`. `git-ubuntu` will ignore all lines prior to it. Here is the
previous example with this change:

```none
Reroute inertial dampeners through auxiliary power relay

Modify the energy distribution system to reroute the inertial dampeners through
the auxiliary power relay, ensuring consistent operation during peak load
scenarios or primary power fluctuations. Adjust the power management algorithm,
prioritizing stability under high-stress maneuvers.

UD-Forwarded: no, ubuntu-specific

--CL--
  * debian/patches/my-changes.diff: Reroute the inertial dampeners
    through the auxiliary power relay. Thanks to Miles O'Brien
    <miles.obrien@ds9.fed>. (LP: #19999999)
```

The `UD-Forwarded` tag is an optional addition that describes the status of this
change in Debian. The tag includes `yes` followed by the link to the forwarded
commit, or `no` followed by an explanation. `ubuntu-specific` is standard for
Ubuntu-only changes.

This style of commit message makes integration with the other tools you'll be
using easier because it's already in changelog format. The `(LP: #12345678)` at
the end will auto-close that bug once the package is published to updates.

For brevity, you'll often see well-known directories abbreviated to their
initial letter, such as `d/p/my-changes.diff` for the previous example. A
change affecting multiple files can list them as comma-separated paths, as
shown in the next example. Sub-bullets '`-`' and '`+`' can be used to organize
the information.

Here is a more complex example:

```none
  * Re-calibrate the long range sensors to detect quasi-particle anomalies.
    - d/p/important.patch: Reroute the inertial dampeners
      through the auxiliary power relay. Thanks to Miles O'Brien
      <miles.obrien@ds9.fed>. (LP: #19999999)
    - d/control, d/rules: Adjust long range sensor power levels
      + Increase power input draw from auxiliary power relay.
      + Set scan range to subatomic frequencies.
```


## Writing an effective changelog

For the changelog entry, you can often reuse (or even directly cut and paste)
text from the git commit or commits you've already made. However, there are
some specific changes required that are unique to the changelog. These are some
guidelines to help you when creating your changelog entries.

* For each thing you change, briefly explain **why** you're making the change as
  well as **what** you're changing. Remember that the "what" can always be
  determined by a future reader by digging into the diff, but the "why" may be
  unknowable except from your message. This can assist decision-making about
  whether your change is still relevant in future merges, or if it's important
  enough to backport to other Ubuntu releases.

* Use nested bullet points indented by two spaces with hanging indentation on
  wrapped lines. Bullet characters are `*`, `-` and `+` for levels 1, 2 and 3 
  (respectively).

* The contents of bullet points are free-form English text, so use normal
  grammar, punctuation, spaces, full stop at the end, etc.
  
  **Exception**: for technical specifics like filenames, matching technical
  case exactly, or otherwise breaking grammatical rules to avoid ambiguity is
  appropriate. Brevity in grammar is fine, but not at the cost of losing
  information. If in doubt, err on the side of verbosity -- although if you
  wish you can always summarize entries and put longer explanations in the
  relevant bugs.

* Use exactly "`LP: #NNNNNNN`" or "`(LP: #NNNNNNN)`" (with a space to separate)
  to reference bugs being fixed by the upload. The version using parentheses is
  useful to neatly fit the bug references into sentences. Bug references *must*
  include a single space, as they are picked up by regular expressions in the
  tooling to ultimately auto-close the bugs.

* If you want to mention a bug but that wasn’t fixed by this change you can
  break the automation that would auto-close it by removing the colon
  "`(LP #NNNNNNN)`".

* For Debian, the same is “`Closes: #NNNNNN`”, and again, automation can be
  avoided by breaking the regular expression by removing the colon
  ("`Closes #NNNNNN`"). If an Ubuntu contribution also fixes a related Debian
  bug it is good practice to tag the closing of the Debian bug as well. That way
  if they pick our change it automatically closes their bug.

* For standard (non-merge) uploads, one bullet point per logical thing changed
  is appropriate. Use sub-items for more detail or if this otherwise helps
  with clarity. If the set of changes is large, consider categorizing the
  entries with top level bullet points.

* For merge uploads, the convention is:

  - One top level bullet point to introduce the merge, with sub-items
    documenting each logical item present in the previous Ubuntu delta which
    is still present in the new Ubuntu delta.

  - If items have been dropped from the previous Ubuntu delta, then use one top
    level bullet point with sub-items describing what was dropped.

  - Further top level bullet points for each new change made that is not a
    carry-over or drop from the previous delta.


### Version string format

Selecting the {manpage}`right version <deb-version(7)` for an upload sounds
trivial and it often is. In most cases it is as easy as
"_increment the right number_", but there are many of edge cases to be aware of.
See {ref}`version-strings` for details.


### Reconstruct the changelog with git-ubuntu

Optionally, you can use `git-ubuntu.reconstruct-changelog [base branch]` to
construct a changelog entry:

```none
$ git-ubuntu.reconstruct-changelog pkg/ubuntu/bionic-devel
```

This modifies `debian/changelog` like so:

```none
mypackage (3.3.0-1ubuntu1) UNRELEASED; urgency=medium

  * debian/patches/my-changes.diff: Reroute the inertial dampeners
    through the auxiliary power relay. Thanks to Miles O'Brien
    <miles.obrien@ds9.fed>. (LP: #19999999)

 -- Karl Stenerud <karl.stenerud@canonical.com>  Mon, 20 Aug 2018 07:58:52 -0700
```

You'll need to manually fix up anything that `reconstruct-changelog` got wrong:

* Version is wrong (should be `3.3.0-1ubuntu1.1`).

* Name and email may be wrong if you don't have `DEBFULLNAME` and `DEBEMAIL`
  set in your env.

* `UNRELEASED`: Change this to the release this change is for (e.g., `bionic`).

If a package was only just synced over from Debian to Ubuntu and hasn't yet
been "touched", such that you are modifying it for the first time (e.g. to
include a patch for an SRU) and your changes mean it is becoming
Ubuntu-specific, the `update-maintainer` script needs to be called after the
changelog entry is created. This will update the 'Maintainer' entries in the
`debian/control` file. In such cases, both the `debian/changelog` and the
modified `debian/control` need to be committed. 


### Reconstruct the changelog with DCH

Simply run `dch` from inside the repository and follow the instructions.

```{note}

Use either `git-ubuntu.reconstruct-changelog` or `dch`, but not both!
```


## Commit the changelog

```none
$ git commit -m "Update changelog" debian/changelog
```


## Update the maintainer field


```none
$ update-maintainer
$ git commit -m "Update maintainer" debian/control
```


## Push your changes

```none
git push [launchpad name] [branch name]
```

For example:

```none
$ git push kstenerud mypackage-fix-lp19999999-inertial-dampeners-bionic
```

To see the repository in Launchpad, go to your code page using this template:
`https://code.launchpad.net/~your-username/+git`

