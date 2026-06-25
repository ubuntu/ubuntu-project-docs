(dmb-rules)=
# DMB rules

```{include} ../_dmb-series.md
```



This section contains rules and regulations for the {ref}`dmb` to use when conducting its business.
Changes to these rules should be proposed by a board member and voted on by the board.


## Board Member attendance

The final formal wording is from [this post](https://lists.ubuntu.com/archives/devel-permissions/2021-October/001750.html) and is reproduced here:

> Any DMB member who fails to attend 6 consecutive scheduled DMB meetings (during a period no shorter than 12 weeks) shall be considered inactive and removed from membership in the DMB.
> Since the number of members required for quorum is 1/2 the number of active DMB members, rounded up, the change in the number of active members will affect quorum.
> At such time as any DMB member is found to be inactive due to this rule, the current DMB chair will add an action item to schedule a public vote for a new DMB member.
> Previous DMB members, including those changed to inactive due to this rule, are eligible to run in the new election and any later elections.
> This proposal is not retroactive, and the attendance requirement shall start the first meeting after this proposal is adopted.

```{note}
This rule [was proposed](https://lists.ubuntu.com/archives/devel-permissions/2021-August/001726.html) on the mailing list, and [approved on 2021-11-05](https://lists.ubuntu.com/archives/devel-permissions/2021-November/001780.html).
```

(dmb-voting-and-quorum)=
## Voting and quorum

* The total number of active board members should be 7, with a quorum of 4.

* We don't require quorum to hold meetings, we only require 'quorum' during voting.

* Members vote on applications or proposals by giving -1 (reject), 0 (abstain), or +1 (approve).

* The sum of all votes given must reach >0 (a majority) to pass a vote.

* The vote must be quorate for it to be valid.

  * However if quorum is not reached at first meeting, then at the next meeting a "majority of present votes" is sufficient to pass.

* If the meeting is quorate and all members present vote in the same way (+1 or -1), then the application will have passed or failed -- the remaining members cannot overturn the vote. However if the verdict was not unanimous, then the remaining members will be asked to vote by email or at the next meeting.

* If the vote is in doubt (for example, if 4 members are present and the vote is tied) then it is *hung* and the remaining members will be asked to vote by email or at the next meeting.

* In the case of a deferred email or next-meeting vote, those members are entitled to ask the applicant further questions if they still have any upon reviewing the meeting log (or recording).


```{note}
These rules are complex, a different approach to make it less misunderstandable
is by expressing it as a {ref}`dmb-vote-function`.
```

(dmb-application-communication)=
## Application-related communication

The following details [are agreed on](https://irclogs.ubuntu.com/2009/10/13/#ubuntu-meeting.html):

* [`devel-permissions@lists.ubuntu.com`](https://lists.ubuntu.com/mailman/listinfo/devel-permissions) list will be used.

* Invitations/applications go there as well as to relevant team lists.

* All approvals go to `ubuntu-devel@` (meeting minutes) and `devel-permissions@` (individual outcomes) (maybe also to the team list).

## Actions after an application

### Successful application

1. Assign two meeting actions: one to make ACL changes, and one to announce
   the successful applicant. This is to make sure that the announcement does not
   get forgotten.

2. If applying for {ref}`dmb-joining-contributing` membership, the
   applicant should only be added to the
   [`~ubuntu-developer-members`](https://launchpad.net/~ubuntu-developer-members)
   team, no other ACL changes are needed.

3. {ref}`Adjust ACLs <dmb-manage-packagesets>`

4. Consider more {ref}`teams to add uploaders to <dmb-teams-to-also-add-uploaders-to>`
   if granting PPU or packageset permissions.

5. Announce successful applicants (this can be done in a single email or multiple
   emails as appropriate), as the Community Council
   [would like to see these announced](https://irclogs.ubuntu.com/2016/07/21/%23ubuntu-meeting.html#t17:17)
   and [we agreed in a subsequent meeting](https://irclogs.ubuntu.com/2016/08/01/%23ubuntu-meeting.html#t16:02).

   Send emails to:

   * A reply to the original `devel-permissions@lists.ubuntu.com` thread (useful
      for future reference)

   * An email to `ubuntu-devel@lists.ubuntu.com`

   * An email to `ubuntu-news-team@lists.ubuntu.com`

### Unsuccessful application

* Reply with regrets to the `devel-permissions@lists.ubuntu.com` thread
  to make it clear that voting is complete.

(dmb-teams-to-also-add-uploaders-to)=
### Teams to also add uploaders to

In almost all cases uploaders are also Ubuntu members and we need to represent
that correctly. In applications to high permission groups that is implied and
happens implicit due to [`~motu`](https://launchpad.net/~motu) and
[`~ubuntu-core-dev`](https://launchpad.net/~ubuntu-core-dev) itself being a
member of [`~ubuntu-dev`](https://launchpad.net/~ubuntu-dev).

But uploaders to packagesets and per-package uploaders should also be
granted "Ubuntu Development Team" membership, since those do not happen
implicitly we need to add them to the respective group. The DMB team therefore
needs to evaluate if a PPU or packagesets contributor also shall become a
Ubuntu Member, in which cases they must be added to the
[~ubuntu-dev](https://launchpad.net/~ubuntu-dev) team.

Occasionally the DMB may want to grant people upload rights even if they do
not meet the usual {ref}`"significant and sustained contributions to Ubuntu
Development" requirement <dmb-joining-contributing>`. In that case instead of
`~ubuntu-dev` they would be added to [~ubuntu-uploaders](https://launchpad.net/~ubuntu-uploaders).

An exception to the above is that some packagesets *require* membership. You can
identify these because the uploading teams are a member of `~ubuntu-dev` instead
of `~ubuntu-uploaders`. In these cases applicants must satisfy the membership
criteria: granting upload rights without membership is not possible.

This is, of course, only the case when adding **uploaders**. Memberships such
as for {ref}`dmb-joining-contributing`, which do not grant any upload
rights to the Ubuntu Archive, do not require adding the new members to any of
the above teams. Those should only be added to
[`~ubuntu-developer-members`](https://launchpad.net/~ubuntu-developer-members).

## Accidental expiry

Since we usually require uploaders to self-renew after some period, sometimes
this is missed by an uploader, and they request that we reinstate them shortly
after expiry.

The DMB have long established that if it's relatively soon after expiry in the
judgement of an individual DMB member, then the uploader can have their
membership reinstated without any further consideration.

If it has been some considerable time since the uploader's team membership
expired, then a full DMB vote is required as usual, but the DMB has in the past
opted not to require a full application (just an agenda item and a quick
discussion at the next meeting).

For the "relatively soon" case, the DMB member should use the following process:

1. Make sure the request is available in the archives of `devel-permissions@`

2. Go to the "Members" page on Launchpad for the team in question (e.g.
   [`~ubuntu-core-dev` members](https://launchpad.net/~ubuntu-core-dev/+members))

3. Page to the end to locate the "Former members" section and locate the uploader.

4. Check the "Expired on" date in the "Status" column is relatively recent. If
   it is not, then stop this process here and ask that the applicant attends a
   DMB meeting to request reinstatement as discussed above.

5. Using the {guilabel}`Edit` button on the right of the former team member
   entry, change "Expiration" to "On" using the default date provided, write a
   suitable comment, and click the {guilabel}`Renew` button.

6. Reply to the `devel-permissions@` thread confirming renewal so there is a
   record in the Archive.


