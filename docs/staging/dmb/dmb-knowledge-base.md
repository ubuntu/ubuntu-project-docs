# DMB knowledge base

```{note}
[Page source](https://wiki.ubuntu.com/DeveloperMembershipBoard/KnowledgeBase)
```

```{admonition} Sally's note
This page should not go into the docs in its current format. Any knowledge that
should be kept should find appropriate pages to live on (can be new pages).

I have only changed the formatting, corrected some minor spelling errors and
updated links to point to internal references where the original wiki link points
to a wiki page that has been moved already. The wording of the content is the
same as the wiki page.
```

This page is intended to list all of the miscellaneous pieces of DMB knowledge
that have accumulated over the years.

This page is authoritative. If you think you've found a mistake, please
[email the DMB](mailto:developer-membership-board@lists.ubuntu.com).

# Delegating packageset uploader permissions

The DMB can decide to delegate the granting of upload rights to a packageset to
a different group of developers. An example is that the Ubuntu Desktop team is
self-managed. This means that applicants to that packageset do not come to the
DMB, but they come to the team itself instead. The procedure is the same as for
most other applications: somebody approaches the DMB with the proposal and it is
voted on at the meeting. If approved, the body delegated should be added as an
administrator of the team. It is very important that the teams come with a
policy that says how applications will be managed. That is the document which
you approve. You can see some examples on {ref}`dmb`, and it is important that
this list is kept current.

## SRU Developers

Based on [this thread](https://lists.ubuntu.com/archives/ubuntu-devel/2017-February/039652.html),
[the DMB agreed](https://irclogs.ubuntu.com/2017/02/27/%23ubuntu-meeting.html#t19:32)
to create [a new team for SRU developers](https://launchpad.net/~ubuntu-sru-developers).
This was [announced to ubuntu-devel on 28 February 2017](https://lists.ubuntu.com/archives/ubuntu-devel/2017-February/039702.html).
See {ref}`dmb-joining-sru-dev` for details.

This team is for contributors who work mostly on SRUs but don't necessarily yet
have experience in wider Ubuntu development. Team membership allows the sponsors
to get out of the way for SRUs only.

This team grants Ubuntu Membership. In other words, the DMB must determine that
an applicant meets the requirements for Ubuntu Membership before granting an
applicant membership of this team.

Add successful applicants to the [`~ubuntu-sru-developers`](https://launchpad.net/~ubuntu-sru-developers)
team.

### Removals

There was some concern about potential bad uploads bothering the SRU team, so to
mitigate this the DMB also agreed that individual `~ubuntu-sru-developers`
membership will be removed if any of:

* `~ubuntu-sru` resolves to remove the member (how they do so is up to them); or
* The DMB resolves to remove the member by a quorate vote, and a vote will be
  held if any member of `~ubuntu-sru` requests it.
