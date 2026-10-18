(new-gradle-package)=
# New Gradle package

The {pkg}`gradle-debian-helper` package provides:

- a Gradle plugin that resolves the dependencies against the system Maven repository (`/usr/share/maven-repo`), using the same `debian/maven.rules` and `debian/maven.ignoreRules` files as the Maven helpers, and
- a debhelper build system class that detects `build.gradle`, initializes the plugin and runs Gradle in offline mode.

General reference: [Debian Java packaging with Gradle](https://wiki.debian.org/Java/Packaging/Gradle).

## Set up the package

1. Add the helper and the packaged dependencies to `debian/control`:

   ```none
   Build-Depends: debhelper-compat (= 13), default-jdk, gradle, gradle-debian-helper, ...
   ```

2. Select the Gradle build system in `debian/rules`:

   ```makefile
   #!/usr/bin/make -f

   %:
   	dh $@ --buildsystem=gradle
   ```

3. Create `debian/maven.rules` and `debian/maven.ignoreRules` with the dependency rules, exactly as for a {ref}`Maven package <new-maven-package>`.

4. To build only some subprojects and ignore the others, pass the Gradle tasks to `dh_auto_build`:

   ```makefile
   override_dh_auto_build:
   	dh_auto_build -- :project1:jar :project2:jar
   ```

   Starting from debhelper compatibility level 13, the tests are run automatically.
   To run them explicitly, override `dh_auto_test` and call `dh_auto_build`:

   ```makefile
   override_dh_auto_test:
   	dh_auto_build -- check
   ```

## Caveats

- Gradle is run with `--offline`: every plugin and dependency must come from the archive.
  Dependencies declared with a version range (for example `org.foo:bar:1.0+`) are not handled.
- Transitive dependencies whose resolved version is neither `debian` nor a generic `*.x` version must be pinned in `debian/maven.rules` to preserve the version, with a rule like `org.foo bar * * * *`.
- The Gradle version in the archive (4.4.x) is much older than what most upstream projects require, so patching `build.gradle` and `settings.gradle` — to remove unsupported plugins and newer DSL features — is often the largest part of the work.
- `gradle-debian-helper` is at an early stage: it mostly helps with the substitution of Maven coordinates, so that Gradle uses the local repository instead of downloading build-dependencies from the internet.

For more details, see the package README (`/usr/share/doc/gradle-debian-helper/README.txt`).
