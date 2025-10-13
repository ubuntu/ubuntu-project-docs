:::{attention}
Some empty directories won't be included in the Git commit. This is a [known issue](https://pad.lv/1917877) not unique to `rustc`. Unfortunately, this means that you'll have to re-extract and overlay every time you clone the Git repo to a new place, run `git clean`, switch to a branch without that vendored dependency, etc.
:::
