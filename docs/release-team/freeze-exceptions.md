(freeze-exceptions)=
# Freeze exceptions

This page outlines some of the common scenarios where {ref}`freezes` exceptions
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
[SONAME](http://www.netfort.gr.jp/~dancer/column/libpkg-guide/libpkg-guide.html#sonameapiabi),
then this **always** needs approval from the Release Team, since all reverse
dependencies need to be adjusted and rebuilt.


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


