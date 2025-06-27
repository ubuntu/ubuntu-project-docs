(aa-signing-bootloaders)=
# Signing bootloaders

```{note}
This page will be moved to:
* Maintainers -> Archive Admin tasks
```

Responsibility for signing bootloaders and kernels no longer sits with the
Archive Admins as a team. The keys being on the `main` Archive caused problems,
so the current production keys are all now attached to PPAs instead.

So, signing is still done with the authority of the Archive Admins, but in
practice it's currently `apw`, `tjaalton`, and `vorlon` doing that via a
**separate restricted Launchpad team**.

```{admonition} Question
:class: important

Do we have a link to this Launchpad team that we can put here ^^ to avoid having
to maintain a list of names that might change in this doc?
```


## s390x bootloaders

The one exception to this currently is s390x bootloaders (source: `s390-tools`),
which get signed in the Archive for their IBM-specific signing scheme (not UEFI
Secure Boot).

These land in the *Unapproved* queue in the Archive and must be accepted by an
Archive Admin. In practice, provided the package was uploaded by someone we
expect to be uploading it, this is a rubber stamp operation; we don't
need to do Upstream code review, and the s390x signing model doesn't have
provisions for key rotation in production so in practice, kernel downgrade
attacks are possible all the way back to the first kernel we signed, limiting
the security value of these signatures.

Any other signing requests that come into the queue should be rejected.
Accepting them will result in a signing operation and publication of the signed
artifacts; however, since the key used for UEFI signing in the Archive was
revoked long ago, this is harmless. The kernel signing machinery should
auto-reject those for us so that we don't have to worry about them in practice.


(aa-raw-uefi-uploads)=
## Raw UEFI uploads

Launchpad supports auto-signing of EFI binaries using the Secure Boot signature
format. This is implemented using a "raw UEFI" format upload within a binary
package build (see the `efilinux` package in Quantal or later for an example).

```{admonition} Question
:class: important

Do we have a more up to date example, with a link?
```

To provide additional assurance that only trusted EFI bootloaders are signed
using this method, packages that include raw UEFI binary uploads land in the
unapproved queue and require Archive Admin approval before they are signed.
Archive Admins should review the corresponding source upload for correctness
prior to approving these uploads.


