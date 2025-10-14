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
def do_vote(votes, total_members=7):
    """
    This function prints exactly one of: "passed", "failed", "hung", "require follow up".

    :param votes: list of integers (-1, 0, +1) representing votes cast by members present
    :param total_members: int, number of active board members (default 7)
    """
    quorum = 4
    dmb_members_present = len(votes)
    sum_of_votes = sum(votes)
    non_abstain_votes = [v for v in votes if v != 0]
    if dmb_members_present >= quorum:
        # unanimous among dmb_members_present non-abstain voters
        if non_abstain_votes and all(v == 1 for v in non_abstain):
            print("passed and final")
        if non_abstain_votes and all(v == -1 for v in non_abstain):
            print("failed and final")
        if sum_of_votes > 0:
            print("passed, but can be overturn by absent members voting by mail until or at next meeting")
        if sum_of_votes < 0:
            print("failed, but can be overturn by absent members voting by mail until or at next meeting")
        # tie or zero sum
        print("hung, absent members are asked to vote by mail until or at next meeting")
    else:
        print("Not quorate - require follow up, next time majority of present members votes will suffice")
```
