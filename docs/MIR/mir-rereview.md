(mir-rereview)=
# MIR - re-reviews

Historically, if something was in main once, there was no re-evaluation done
later unless teams asked for it based on huge changes. Doing regular
re-evaluations on all packages would be nice, but also rather a huge effort.

We want to be pragmatic, therefore:

- All we identify shall be recommended tasks (not required to continue) unless
  we find something really intolerable.
- We'd appreciate it if the owning team could file a MIR-reporter bug for it,
  but would not insist on it if they can't. In that case we create a stub for it.

The benefit of this is that the stricter rules we have today (added for
good reasons usually triggered by painful lessons learned no one wants to
repeat), will be considered. Thereby we might create useful suggestions for
components that are central to Ubuntu, its quality, and its maintainability.

We would create an MIR bug if there was none. But if there was a bug already
we would want to keep the context together and avoid flooding Launchpad with
multiple MIR bugs for a single package. Therefore in this case, just
as we do when we retroactively promote in an SRU we would add per-series bug
tasks to show the state of each review independently.

If source renames are involved, those can be tracked the same way -- all
associated to one bug.


## Renamed or reorganized sources

We can use some regular events to start with re-reviews at a small scale,
and that is when things pop up on our radar anyway.

In the past, if a source was already in main, but then appeared in a different
form -- common cases that come to mind are renames or code being split out --
have gotten a fast-path approval based on being in main already.

But from now on, for packages old enough to not have any audit-trail via an MIR
bug, we want to do a re-evaluation when they show up as a component mismatch.


## Opt-in re-review

For special cases (read: do not dump hundreds of requests to the MIR team at
once) teams can also request a re-review. That might even be worthwhile if
there already is a former MIR bug -- for example, if the project was rewritten
in another language, all former assumptions might be invalid anyway.

For that a team should contact the MIR team directly in the
{ref}`MIR team meeting <mir-team-meeting>`.
