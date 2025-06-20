(aa-phasing-sru-updates)=
# Phasing on delivering SRU updates

[Why we do phasing](https://documentation.ubuntu.com/sru/en/latest/explanation/standard-processes/#explanation-phasing),
how to [check the current state](https://documentation.ubuntu.com/sru/en/latest/howto/phasing/#investigate-halted-phased-update)
and much more is well explained in
[the SRU docs](https://documentation.ubuntu.com/sru/en/latest/) and doesn't
need outlining again here. There also is a way to
[override auto-halting the phasing](https://documentation.ubuntu.com/sru/en/latest/internal/#internal-override-phasing),
needed when a package is detected as crashing more frequently or has a new crash
but that this is actually a false positive. The override action can be performed
by Archive Admins or SRU team members.


## Why?

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


## How?

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

