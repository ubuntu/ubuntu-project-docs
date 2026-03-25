(once-the-bugfix-is-accepted)=
## Once the bugfix is accepted


### The acceptance email

You'll receive an email notification that the bugfix was accepted:

```none
Accepted postfix into bionic-proposed. The package will build now and be
available at
https://launchpad.net/ubuntu/+source/postfix/3.3.0-1ubuntu0.1 in a few
hours, and then in the -proposed repository.

Please help us by testing this new package.  See
https://wiki.ubuntu.com/Testing/EnableProposed for documentation on how
to enable and use -proposed.Your feedback will aid us getting this
update out to other Ubuntu users.

If this package fixes the bug for you, please add a comment to this bug,
mentioning the version of the package you tested and change the tag from
verification-needed-bionic to verification-done-bionic. If it does not
fix the bug for you, please add a comment stating that, and change the
tag to verification-failed-bionic. In either case, details of your
testing will help us make a better decision.

Further information regarding the verification process can be found at
https://wiki.ubuntu.com/QATeam/PerformingSRUVerification .  Thank you in
advance!

** Changed in: postfix (Ubuntu Bionic)
       Status: In Progress => Fix Committed

** Tags added: verification-needed verification-needed-bionic
```

Follow the
[build link](https://launchpad.net/ubuntu/+source/postfix/3.3.0-1ubuntu0.1)
and make sure it's publishing to the correct place (Bionic), and that the
builds completed (green check marks).


### The excuses page

Check the "excuses" or "migration" page,
[for Bionic](https://ubuntu-archive-team.ubuntu.com/proposed-migration/bionic/update_excuses.html)
in this case.

[General page](https://ubuntu-archive-team.ubuntu.com/proposed-migration/update_excuses.html)

Eventually, the package with your fixes will appear there (search for
`postfix` in this case). It will show the DEP-8 tests for `postfix` and
anything that depends on it. Any tests that fail will show in red.

```{note}
This page is generated every few minutes, and doesn't update in real-time.
```


### SRU verification

It's best to have the package independently verified (preferably by the person
who reported the bug), but if it sits idle too long (2 days or so), you can
verify it yourself. Follow the
[instructions provided](https://documentation.ubuntu.com/sru/en/latest/howto/common-issues/)
by the SRU team, which usually means changing the "verification-needed" tag
into "verification-done".

[Pending SRU](https://ubuntu-archive-team.ubuntu.com/pending-sru.html) shows which SRUs
are pending and what their status is. Note that this includes DEP-8 test
results; if these have failed then it's unlikely the SRU team will release
the update, so it's wise to follow-up if this happens.

Once all of the SRU's bugs have reached `verification-done` and a 7-day
waiting period has elapsed, the SRU team will move the source and binary
packages into the `-updates` pocket and mark the bug task(s) as "Fix Released".

