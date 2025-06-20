(aa-secondary-tasks)=
# AA team's less common tasks


(aa-priority-mismatches)=
## Priority mismatches

Like `component-mismatches`,
[`priority-mismatches`](https://ubuntu-archive-team.ubuntu.com/priority-mismatches.txt)
tracks priority mismatches in the Archive. These are generally less important
than `component-mismatches` because wrong priorities have relatively little
impact: they affect the behavior of `debootstrap` so packages with a too-high
priority will be pulled into default installs necessarily, but these days
`debootstrap` will resolve dependencies on its own so too-low priorities don't
really impact users.

However, starting at Feature Freeze we should review these and try to drive the
list to zero because packages showing on this list as needing their priority
raised have this because they've been added as *Recommends* or *Depends* to
existing central packages, and we should make sure these additions are actually
desired in Ubuntu (sometimes they only make sense in Debian) to avoid bloating
the base system. This should be done at Feature Freeze to allow developers time
to drop dependencies that aren't wanted.

As with `component-overrides`, these are managed with `change-override`.

The overrides for a given binary name are the same for all architectures, so
attention should be given to per-arch `priority-mismatches` and decisions made
that make sense (e.g. don't raise the priority of `powerpc-specific` libraries),
and we should not expect the `priority-mismatch` report to be zeroed on ALL
arches.


(aa-signing-bootloaders)=
## Signing bootloaders

Responsibility for signing bootloaders and kernels no longer sits with the
Archive Admins as a team. The keys being on the main archive caused problems,
so the current production keys are all now attached to PPAs instead. So signing
is still done with the authority of the Archive Admins, but in practice it's
currently `apw`, `tjaalton`, and `vorlon` doing that via a separate restricted
Launchpad team.

```{admonition} Question
Do we have a link to this Launchpad team that we can put here ^^ to avoid having
to maintain a list of names that might change in this doc?
```

The one exception to this currently is s390x bootloaders (source: `s390-tools`),
which get signed in the Archive for their IBM-specific signing scheme (not UEFI
Secure Boot). These land in the *Unapproved* queue in the Archive and must be
accepted by an Archive Admin. In practice, provided the package was uploaded by
someone we expect to be uploading it, this is a rubber stamp operation; we don't
need to do Upstream code review, and the s390x signing model doesn't have
provisions for key rotation in production so in practice, kernel downgrade
attacks are possible all the way back to the first kernel we signed, limiting
the security value of these signatures.

Any other signing requests that come into the queue should be rejected.
Accepting them will result in a signing operation and publication of the signed
artifacts; however, since the key used for UEFI signing in the Archive has been
revoked long ago, this is harmless. The kernel signing machinery should
auto-reject those for us so that we don't have to worry about them in practice.


(aa-raw-uefi-uploads)=
### Raw UEFI uploads

Launchpad supports auto-signing of EFI binaries using the Secure Boot signature
format. This is implemented using a "raw UEFI" format upload within a binary
package build (see the `efilinux` package in Quantal or later for an example).

To provide additional assurance that only trusted EFI bootloaders are signed
using this method, packages that include raw UEFI binary uploads land in the
unapproved queue and require Archive Admin approval before they are signed.
Archive Admins should review the corresponding source upload for correctness
prior to approving these uploads.



(aa-phasing-on-delivering-sru-updates)=
## Phasing on delivering SRU updates

[Why we do phasing](https://documentation.ubuntu.com/sru/en/latest/explanation/standard-processes/#explanation-phasing),
how to [check the current state](https://documentation.ubuntu.com/sru/en/latest/howto/phasing/#investigate-halted-phased-update)
and much more is well explained in
[the SRU docs](https://documentation.ubuntu.com/sru/en/latest/) and doesn't
need outlining again here. There also is a way to
[override auto-halting the phasing](https://documentation.ubuntu.com/sru/en/latest/internal/#internal-override-phasing),
needed when a package is detected as crashing more frequently or has a new crash
but that this is actually a false positive. The override action can be performed
by Archive Admins or SRU team members.


### Why?

The delivery of an SRU is phased to allow detecting and holding back the
delivery of regressions that have made it to the `-updates` pocket in spite of
verification in `-proposed` prior to release to `-updates`.

It can be triggered in two ways: **automated** and **manual**.

* **Automated phasing stops** are triggered by `errors.ubuntu.com`. If it
  detects a spike of crash reports with a new version, or an altogether new
  crash with the new package version, phasing is auto-halted. The tooling sets
  the phasing to zero which can be seen in
  [phased updates](https://ubuntu-archive-team.ubuntu.com/phased-updates.html),
  and notifies the sponsor of the upload.

* **Manual phasing stops** are due to humans, usually either the developer that
  tracks their upload or a severe and urgent case of a `regression-update` bug.
  In this case an SRU team member or Archive Admin would set the phasing to
  zero, to stop delivering the potentially bad update.

In both cases it now needs to be investigated urgently to come to a conclusion,
choosing between one of the following paths:

1. **replace/remove:**

   If a fix is needed, the improved new version is likely not immediately ready
   and verified enough to be pushed to `-updates` (superseding the former). In
   that case the bad version should be
   {ref}`removed from -updates and the former version restored <revert-a-package-to-a-previous-version>`.

1. **continue phasing**:

   If instead it turns out to be a false alarm, phasing can be continued.


### How?

Once certain that it is the right step, phasing can be changed via
`change-override`. The relevant arguments are similar to other actions with
`change-override`. In addition use `--percentage` to set the new phasing ratio.

We only deliver (and thereby phase) binaries, but we usually want to set this
consistently for all binaries at once for a given source package, so we'd
usually use `--source-and-binary`.

For example, to hold the phasing of `containerd-app` in `noble-updates` and set
it back to zero (to no longer provide this update), you'd run:

```bash
./change-override --percentage 0 --suite noble-updates --source-and-binary containerd-app
```

```{important}
From the wiki page, import the i386 whitelist updates content
```

(aa-i386-whitelist-updates)=
## i386 whitelist updates

The i386 [is a partial archive now](https://wiki.ubuntu.com/i386).

To add packages to the whitelist:

* Update the `update-i386-whitelist` script from `u-a-t` (typically adding a
  `newSet.update(['$package'])` entry

* Run the script

* Trigger the i386 build either by doing an upload or by copying the package
  over itself (`copy-package -b --force-same-destination -e $version $pkg`)

Note that if the binary package was built for an earlier release, e.g. Oracular
for the current Plucky, you'll need to adjust the `copy-package` invocation to:

```bash
./copy-package -b --from-suite=oracular --to-suite=plucky -e $version $pkg`.
```

The copy should trigger a build on i386, once it's published:

* Remove the entry from the `update-i386-whitelist script`

* If the new item isn't pulled in as a build-/dependencies, manually add it to:
  [`https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/i386/`](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/i386/)

  * If a source package builds multiple binary packages, and a binary package
    other than the one pulled into the seed has dependencies that are not
    otherwise included, then this binary package will also need to be seeded in
    order to ensure dependency availability.

