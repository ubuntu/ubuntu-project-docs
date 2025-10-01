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

Summarized in this Python-like function:

```python

def do_vote(votes, total_members=7):
   """
   Print the outcome of the vote

   :param votes - a list of votes given being -1,0 or +1
   :param total_members - active members of the DMB
  """
  absent = total_members - len(votes)

  net_vote = sum(votes)

  min = net_vote - absent

  max = net_vote + absent

  if min > 0:

    print(f'Vote minimum {min} > 0, vote passes')

  elif max < 0:

    print(f'Vote maximum {max} < 0, vote fails')

  elif min == max == net_vote == 0:

    print(f'Vote is tied, vote fails')

  else:

    print(f'Vote is between {min} and {max}, outcome unknown as quorum was not reached')
```
