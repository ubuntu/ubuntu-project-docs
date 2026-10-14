(UpdateManager-test-plan)=
# Update Manager test plan


1. If `apt list --upgradable` returns nothing, downgrade a package in the system.

   :::{tip}
   Of course it's better to do so with a cosmetic package that has no chance to impact the system, e.g. [`cowsay`](https://launchpad.net/ubuntu/+source/cowsay/+publishinghistory).
   :::

2. Start `update-manager`.

3. Verify that `update-manager` suggests packages matching the output of `apt list --upgradable`.

   :::{note}
   If the list is too long, just scanning over the output is OK, as Apt will list package names and Update Manager their short descriptions and that makes a one-by-one comparison very slow.
   :::

4. Install one or more updates via Update Manager, verify that the corresponding packages are gone from

   * `apt list --upgrade`; and
   * `update-manager`'s recalculated view.
