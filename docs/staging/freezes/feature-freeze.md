(feature-freeze)=
# Feature Freeze

```{note}
This page will be moved to:
* how-ubuntu-is-made > concepts
```

During Feature Freeze we stop introducing new features, packages, and APIs, and
concentrate on fixing bugs in the development release. Note that the upload
queue is not actually frozen -- uploads will enter the Archive, so be careful.

The #ubuntu-devel and #ubuntu-release channels on Matrix are generally updated
to indicate the current Freeze status.

(user-interface-freeze)=
## User Interface Freeze

The {term}`user interface <UI>` must be stabilized at some point, so that
documentation writers and translators can work on a fixed target that doesn't
make screenshots or documentation obsolete.

After the User Interface Freeze (UIF), the following things must not change
further without approval of the release team and notification (usually via
email, with a link to the mail in your exception bug) to the
[documentation](https://lists.ubuntu.com/mailman/listinfo/ubuntu-doc) and
[translation](https://lists.ubuntu.com/mailman/listinfo/ubuntu-translators)
teams:

* The user interface of individual applications that are installed by default

* The appearance of the desktop

* The distribution-specific artwork

* All user-visible strings in the desktop and applications that are installed
  by default


## Freeze exceptions

As with most rules, there are occasional exceptions to the restrictions imposed
by the various stages of the Ubuntu release process. These exceptions are
granted by the release team based on information provided by the developer who
proposes the change.

Find out more {ref}`about exceptions <freeze-exceptions>` or
{ref}`request-a-freeze-exception`.

## Additional notes

* Upstream microreleases of applications are usually fine after this point if
  they only fix bugs. This should be verified by reading the detailed upstream
  changelog and (cursorily) reading the diff between the version in the Ubuntu
  development release and the new upstream version. If in doubt, ask the release
  team for advice.

* ABI/API compatibility is a special case of a feature. If a library breaks
  backward compatibility (i.e. changes existing API/ABI and introduces a new
  [SONAME](http://www.netfort.gr.jp/~dancer/column/libpkg-guide/libpkg-guide.html#sonameapiabi),
  then this **always** needs approval from the release team, since all reverse
  dependencies need to be adjusted and rebuilt.

* New packages need to be {ref}`checked by Archive Administrators <aa-new-review>`
  before they find their way into the archive. This process can take several
  days up to a few weeks. For the purpose of the Feature Freeze, the upload date
  matters, i.e. all packages in the
  [NEW queue](https://launchpad.net/ubuntu/saucy/+queue?queue_state=0)
  by that time will be processed without the need for an exception.

