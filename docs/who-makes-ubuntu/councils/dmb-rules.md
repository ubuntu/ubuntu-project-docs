(dmb-rules)=
# DMB rules

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

The following details [are agreed on](http://irclogs.ubuntu.com/2009/10/13/%23ubuntu-meeting.html):

* [`devel-permissions@lists.ubuntu.com`](https://lists.ubuntu.com/mailman/listinfo/devel-permissions) list will be used.

* Invitations/applications go there as well as to relevant team lists.

* All approvals go to `ubuntu-devel@` (meeting minutes) and `devel-permissions@` (individual outcomes) (maybe also to the team list).

