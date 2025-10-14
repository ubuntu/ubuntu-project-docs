---
orphan: true
---

(dmb-vote-function)=
# DMB vote funtion

The text on {ref}`dmb-rules` should be easier to consume, but if in doubt
here a different way to express it.

These rules were proposed in
* this [mailing list thread](https://lists.ubuntu.com/archives/devel-permissions/2021-August/001728.html)
* then [extended to a poll](https://lists.ubuntu.com/archives/devel-permissions/2021-October/001756.html)
* with the [results](https://lists.ubuntu.com/archives/devel-permissions/2021-November/001782.html)
* then [clarified again](https://lists.ubuntu.com/archives/devel-permissions/2021-October/001763.html)
* and [finalized](https://lists.ubuntu.com/archives/devel-permissions/2021-October/001764.html)
* Also earlier [Quorum was publicly discussed](https://discourse.ubuntu.com/t/open-discussion-meetings-quorum/5966) on the community forum.

All that is summarized in this Python-like function:

```python
def do_vote(votes):
    """
    This function returns the outcome of a DMB vote as a string.

    :param votes: list of integers (-1, 0, +1) representing votes cast by members present
    """
    quorum = 4
    total_members=7

    dmb_members_voting = len(votes)
    missing_votes = total_members - dmb_members_voting

    sum_of_votes = sum(votes)
    non_abstain_votes = [v for v in votes if v != 0]

    if dmb_members_voting < quorum:
        return "Not quorate - require follow up, next time majority of present members votes will suffice"

    if non_abstain_votes and all(v == 1 for v in non_abstain_votes):
        return "quorum and unanimous - passed and final"
    if non_abstain_votes and all(v == -1 for v in non_abstain_votes):
        return "quorum and unanimous - failed and final"

    if sum_of_votes > 0:
        if sum_of_votes > missing_votes:
            return "quorum, missing votes could not overturn it - passed and final"
        else
            return "quorum and passed, but missing votes could be overturn it - absent members are asked to vote by mail until or at next meeting"

    if sum_of_votes < 0:
        if abs(sum_of_votes) > missing_votes:
            return "quorum, missing votes could not overturn it - failed and final"
        else:
            return "quorum and failed, but missing votes could be overturn it - absent members are asked to vote by mail until or at next meeting"

    return "hung, absent members are asked to vote by mail until or at next meeting"
```
