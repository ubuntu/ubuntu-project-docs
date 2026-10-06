(freeze-exceptions)=
# Freeze exceptions

This page outlines some of the common scenarios where freeze exceptions
might be wanted. You should read this page before you
{ref}`request-a-freeze-exception`.

```{admonition} **Freezes** series

**Process overview:**
: {ref}`freezes`

**Reference:**
: {ref}`freeze-exceptions` (this page)

**Practical guidance:**
: {ref}`request-a-freeze-exception`
```


(feature-freeze-exceptions)=
## Feature Freeze exceptions

Exceptions to the {ref}`feature-freeze` process must be approved by the Release
Team for all packages in the Archive (i.e. `main`, `restricted`, `universe`
and `multiverse`).

Exceptions should be granted if the upload:

* Contributes to high-priority feature goals for the release

* Is warranted due to other exceptional circumstances, as judged by the release managers.


### ABI/API compatibility

ABI/API compatibility is a special case of a feature. If a library breaks
backward compatibility (i.e. changes existing API/ABI and introduces a new
[SONAME](https://www.netfort.gr.jp/~dancer/column/libpkg-guide/libpkg-guide.html#sonameapiabi),
then this **always** needs approval from the Release Team, since all reverse
dependencies need to be adjusted and rebuilt.


(openstack-feature-freeze-exceptions)=
### OpenStack release alignment

OpenStack has a standing arrangement with the Release Team to continue
updating to the OpenStack release targeted for an Ubuntu development release
after Feature Freeze. This accommodates upstream milestones, release
candidates, and final releases that fall after Ubuntu's Feature Freeze.

The OpenStack team can track these updates in a single Feature Freeze
exception bug for the Ubuntu release. The bug records the scope, release
schedule, and Release Team approval, and provides a common reference for
package changelogs. See {ref}`request-an-openstack-feature-freeze-exception`.

The historical scope covers core OpenStack packages and direct dependencies
maintained within the upstream OpenStack project. A dependency on an external
project does not automatically bring that project within the exception;
changes outside the agreed scope need separate Release Team consideration.

The arrangement is recorded in the
[Mitaka/Xenial release coordination email (2016)](https://lists.ubuntu.com/archives/ubuntu-release/2016-February/003572.html)
and the
[Dalmatian/Oracular release coordination email (2024)](https://lists.ubuntu.com/archives/ubuntu-release/2024-September/006246.html).
The Release Team clarified the dependency boundary in the
[6 April 2016 IRC discussion](https://irclogs.ubuntu.com/2016/04/06/%23ubuntu-release.html#t21:00).
For Flamingo/Questing, the Release Team explicitly acknowledged the standing
arrangement and the use of a single tracking bug in
[bug 2121258, comment 1](https://bugs.launchpad.net/ubuntu/+source/openstack/+bug/2121258/comments/1),
and recorded approval and release timing requirements in
[comment 2](https://bugs.launchpad.net/ubuntu/+source/openstack/+bug/2121258/comments/2).


(ui-freeze-exceptions)=
## User Interface Freeze exceptions

{ref}`user-interface-freeze` exception request bugs need a justification for
why the User Interface (UI) needs to be changed at that point, and give a
rationale as to why the benefits of it are worth breaking existing documentation
and translations.

Refer to the {ref}`request-ui-freeze-exception` section for additional
instructions for your request bug.


(final-freeze-exceptions)=
## Final Freeze exceptions

During the Final Freeze period, extreme caution is exercised when considering
exceptions, as a regression could cause a deadline to be missed, or a build to
receive less testing than desired. A request for an exception must demonstrate
strong rationale and minimal risk for the update to be considered.

Refer to the {ref}`request-final-freeze-exception` section for additional
instructions for your request bug.


(universe-multiverse-freeze-exceptions)=
### Exceptions for universe/multiverse

The Freeze Exception process is the same for `universe`/`multiverse` as for
`main`/`restricted`, except during the last week of development before the
release. During that time, all uploads need to get approved by the Release Team. 

The instructions for request bugs for `universe` and `multiverse` are the same
as those for Final Freeze exceptions. Refer to the
{ref}`request-final-freeze-exception` section for details.


