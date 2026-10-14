(plus-one-report-template)=

# +1 Maintenance report template

Here is a template one can use to file a {ref}`+1 maintenance <plus-one-maintenance>` report.
The report is to be posted [on the Ubuntu Discourse](https://discourse.ubuntu.com/c/pre-release-discussion/plusone-maintenance/415).

```md
# +1 Maintenance report from $start to $end

Small paragraph to give some context for the report, e.g. if you were asked to
work on specific things, what you focused on, what event shaped your shift.

## Work-needed items

You don't need to be too specific about the problems themselves (do that, but do mention the kind of work remaining). For instance:

* [Some package](https://bugs.launchpad.net/ubuntu/+source/hello/+bug/1234567): some more investigation needed.
* [Some other package](https://bugs.launchpad.net/ubuntu/+source/hello/+bug/1234567): Tentative fix uploaded, still building.
* [Package removal](https://bugs.launchpad.net/ubuntu/+source/hello/+bug/1234567): Paperwork filled, waiting on AA.
* The libfoo1->libfoo2 transition just started in Debian.

### Sponsorship needed

If you're not an uploader, please group all your sponsorship needs here in a
dedicated subsection. Who knows, a roaming patch pilot might just pick them all
up in their shift!

## Full logs

This is likely the longest section, as it should in principle contain most
work-needed items, along with a description of what you actually did. How much
you get into details is up to you.

For instance:
[PM: hello](https://bugs.launchpad.net/ubuntu/+source/hello/+bug/1234567): src:hello is stuck in -proposed, its new autopkgtests are failing due to the proxy. I uploaded a fix, and also forwarded it to Debian.

```
