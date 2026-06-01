(openjdk-version-strings)=
# OpenJDK version strings

OpenJDK versions are controlled by `is_upstream_release` variable in `debian/rules`

`is_upstream_release=yes` - upstream release, e.g. `25.0.2+10-1~24.04.1`. `<Upstream Version>+<build>-<debian-revision>~<backport version>`.
`is_upstream_release=` - development preview, e.g. `25~36ea-1`. `<Upstream Version>~<version>ea-<debian-revision>`.

The build will fail if the version string in `debian/changelog` does not match the expected format.



