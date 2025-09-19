(request-a-sync)=
# Request a sync

When an Ubuntu package carries a delta, but it is no longer needed (because it has been merged in Debian or upstream), request a manual sync. See {ref}`merges-syncs` for context.


(asking-for-a-sync)=
## Asking for a sync

The automatic syncing of packages from Debian is active for only some of the
Ubuntu release cycle - see {ref}`debian-import-freeze` for more information.

Let us consider a test case where we have an empty Ubuntu delta before
Debian Import Freeze. You can check the
[Release Schedule](https://wiki.ubuntu.com/ReleaseSchedule)
for current releases in development. The Debian package is on
[`testing`](https://www.debian.org/releases/), so doing an
[explicit sync](https://wiki.ubuntu.com/SyncRequestProcess#Content_of_a_sync_request)
is unnecessary. 


### Simple Case

In simple cases, opening a bug with the required information is sufficient.
`sass-spec` bug for 25.04 is
[a good example](https://bugs.launchpad.net/ubuntu/+source/sass-spec/+bug/2098389).

* Ensure the patch or upstream information is included

* Provide the patch which has been adopted upstream

Cases like this may be:

* Debian adopts the same patch as Ubuntu, possibly with a different name

* Upstream has accepted the change, Debian takes upstream, and Ubuntu can drop its delta

  * Simple here being a single patch; for many patches see below


### Complex Case

When multiple changes are adopted, and many patches can be dropped, an MP may be
helpful for reviewers to understand the change. Also ensure there is an
accompanying bug, either a merge bug from the Server team automation, changing
it to a sync, or a new sync bug.

* Specify that the MP is for a sync request.

* Write down how you discovered it is a sync: changelog entries, step in where
  the empty commit message appeared, point to upstream git repository, etc.

* Change the changelog using `dch -i` to get a new version with the `ubuntu1`
  suffix and check the Ubuntu series for which the package is to be built. The
  text in that new changelog entry should say "build debian version to verify
  before a sync".
  
* {ref}`Build the source package <build-with-dpkg-buildpackage>` and upload to the
  PPA you're using in this MP.

An example of this case is
[presented here](https://code.launchpad.net/~mirespace/ubuntu/+source/freeipmi/+git/freeipmi/+merge/407014).

For other sync situations, see the
[Ubuntu wiki page](https://wiki.ubuntu.com/SyncRequestProcess).
Outside of the server team process, the common way is to request an explicit
sync via either
[filing a Launchpad Bug](https://wiki.ubuntu.com/SyncRequestProcess#For_people_requiring_sponsorship),
or using the {manpage}`requestsync tool <requestsync(1)>`.


(how-to-perform-a-sync)=
## How to perform a sync

If you have the permissions to upload the package to Ubuntu, you can issue a
sync request using the {manpage}`syncpackage tool <syncpackage(1)>`.
The process is described more fully in the
[Ubuntu Wiki page](https://wiki.ubuntu.com/SyncRequestProcess#For_people_with_permission_to_upload_the_package_to_Ubuntu).
To be able to use `syncpackage`, the package needs to be known to Launchpad
and there is a slight delay between a Debian upload and the availability in
Launchpad. You can check the Debian publishing history of a package in
`https://launchpad.net/debian/+source/<name_of_the_package>/+publishinghistory`
like in this example for
[`freeipmi`](https://launchpad.net/debian/+source/freeipmi/+publishinghistory).

For our example case of `freeipmi`, the sync was done in this way:

```shell
syncpackage -r impish-proposed -d unstable -v freeipmi --force
```


## What's next?

You can check the status of the build as with any other upload, from its
"Overview" page (in the format
`https://launchpad.net/ubuntu/+source/<name_of_the_package>`).
Checking the build log:

* In the main part of that page you can see the list of built packages for
  every Ubuntu series. You can click on a package's "version" to get to the
  builds for a specific architecture and see the build log -- e.g. the
  [`freeipmi` amd64 build log](https://launchpad.net/ubuntu/+source/freeipmi/1.6.6-4/+build/21971101/+files/buildlog_ubuntu-impish-amd64.freeipmi_1.6.6-4_BUILDING.txt.gz).

* Visiting the publishing history of the package (in the format 
  `https://launchpad.net/ubuntu/+source/<name_of_the_package>/+publishinghistory`):
  a link at the top right of the "Overview page" -- e.g.
  [for `freeipmi`](https://launchpad.net/ubuntu/+source/freeipmi/+publishinghistory).


## Further reading

* {ref}`merges-syncs`
