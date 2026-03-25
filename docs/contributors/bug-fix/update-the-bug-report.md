(update-the-bug-report)=
## Update the bug report

For regular bug fixes and merges, adding a comment about your progress is
typically all you'll need. You might provide some links to your PPA if you'd
like to get people to test your fix, or if you want to provide the fix to the
user-base swiftly.


### SRU paperwork

For stable release updates (SRUs), on the other hand, you need to add a bit
more detail.

Go back to the
[example bug report](https://bugs.launchpad.net/ubuntu/+source/postfix/+bug/1753470).

Modify the bug description (yellow pencil icon) and update it to conform with
[the SRU bug template](https://documentation.ubuntu.com/sru/en/latest/reference/bug-template/).
These are normally the "Impact", "Test Case" and "Where problems could occur"
sections.

It is good practice to make the "Test Case" section itemized with explicit
steps, "paint-by-numbers" style. It is also best practice to include both a
"Development Fix" and "Stable Fix"; the former explains the situation with the
fix in the current development release, while the latter explains your
strategy for addressing (or skipping) it in LTS and other stable releases.

```{note}

Keep the original description as-is, in a section called
"Original Description" at the bottom.
```

```{note}
You'll see your branch and merge proposal in the `Related branches` because of
the (`LP: #NNNNNN`) in the changelog entry.
```


### SRU exceptions

There is a particular kind of
[special case SRU](https://documentation.ubuntu.com/sru/en/latest/reference/package-specific/)
which is called either a Minor Release Exception (MRE) or an SRU exception. In
the former we assume upstream is so stable and similar to our needs, process
and philosophy that fewer checks need to be done, in the latter we admit that
there is more to check - but both do more than the isolated individual bug
fixing that a normal SRU would do.

The work to get these exceptions granted gives us confidence that the minor
releases created by upstream take sufficient care over testing, ABI & API
stability, smooth upgradability, and other things important for an SRU.

Each case is slightly different, which is why each of them gets their own
discussion and their own accepted process listed in
[SRU special cases](https://documentation.ubuntu.com/sru/en/latest/reference/package-specific/)
of how that particular minor release will be served.

When we (in the server team) prepare special SRU updates they follow all the
normal SRU rules as outlined here, but in addition will follow all steps and
requirements outlined in the particular SRU exception. That usually includes
additional checks and validations.

There is one more thing that we (the server team) can do in addition for any
SRU exception upload that we work on. That is, to double check upstream
release notes and changelogs to ensure that there was really nothing that
would unexpectedly break the "stable" in SRU.

That is worthwhile for MREs where we expect nothing should<sup>(TM)</sup>
happen and even more so for general SRU exceptions. 

After having passed an SRU exception process, there is always a small chance
that the upstream project might have a slightly different stance/decision
policy with regard to stable releases. This check by our team will help to
serve those updates in the stable and reliable fashion our users expect them
to be.

To be clear, the expectation is that we should not find anything in this
check, but this is a classic case of "better safe than sorry".


## SRU review process

There is a distinction between sponsorship and the SRU process. They are
possibly a little confused in the SRU wiki page (especially section 6 “Fixing
several bugs in one upload").

Consider the process from the point of view of your sponsor and the SRU team.
On review, they will start from the diff and expect to see:

* **The diff fully explained by the changelog entry**.
  This means that if there is something in the diff that isn't explained by
  the changelog, then there is a problem.
* **A bug for everything mentioned in the changelog entry**.
  Reviewers are pragmatic: there is no strict rule that "every bullet point
  must refer to a bug", but rather that logically everything mentioned should
  correspond to a bug so the reviewer can go to a bug to find more info on
  any part of the changelog.
  
  For an SRU, even added functionality must refer to a bug. If some part of a
  changelog entry does not obviously refer to a bug, then there is a problem.
* **Every issue mentioned in an SRU changelog must have a bug task filed
  against the package**. The same bug # can be mentioned in different SRUs,
  since a bug may have multiple bug tasks. The Ubuntu Bug Control Team, or
  other members of the server team can assist if you need help creating bug
  tasks.
* **The issue should be resolved for the Ubuntu development release**. This is
  tracked by having a bug task set to "Fix Released" for the devel series.
  The goal is to avoid regression from a user’s perspective when they upgrade
  to the newer Ubuntu release. If the status is not "Fix Released" but you
  still want to proceed with the SRU, explain what is going on in a
  "Development Fix" section.
* **Every LP bug # mentioned in an SRU changelog must have "SRU paperwork"
  filled out**. As described in the previous section.

After you or your sponsor have uploaded your package:
* Set the bug task status to "In Progress".
* The upload will appear in the "unapproved queue", for example 
  `https://launchpad.net/ubuntu/focal/+queue?queue_state=1`. It may take a
  week or two before it gets processed.
* If you find a problem while it's still unapproved, ask in the Libera Chat
  `#ubuntu-release` channel for the package to be rejected from the queue.
  This is a trivial task for archive admins. If rejected at this stage, then
  the same version number can be re-used in a subsequent upload.
* The SRU team will review incoming SRU uploads from the unapproved queue and
  expect to see the review items completed correctly as above. They will
  either accept or reject (with a reason) from the unapproved queue. If they
  reject, then you will need to handle the rejection reason and then start
  again from the beginning. If they accept, then the bug task will change to
  "Fix Committed", the package will enter the `-proposed` pocket and then the
  package binaries will be built.
