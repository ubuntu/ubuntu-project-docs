(new-gradle-package)=
# New Gradle package

The {pkg}`gradle-debian-helper` package provides:

- a Gradle plugin that resolves the dependencies against the system Maven repository (`/usr/share/maven-repo`), using the same `debian/maven.rules` and `debian/maven.ignoreRules` files as the Maven helpers, and
- a debhelper build system class that detects `build.gradle`, initializes the plugin and runs Gradle in offline mode.

## Set up the package

1. Add the helper and the packaged dependencies to `debian/control`:

   ```none
   Build-Depends: debhelper-compat (= 13), default-jdk, gradle, gradle-debian-helper, ...
   ```

2. Select the Gradle build system in `debian/rules`:

   ```makefile
   #!/usr/bin/make -f

   %:
   	dh $@ --buildsystem=gradle --with maven-repo-helper
   ```

3. Create `debian/maven.rules` and `debian/maven.ignoreRules` with the dependency rules, exactly as for a {ref}`Maven package <new-maven-package>`.

4. Create `debian/gradle.ignoreRules` to exclude plugins and files from the build. The file has a
   two-column layout. The first one is a plugin, project (denoted by leading ':'), or a file path.
   The second is a comma-sepearated list of configuration blocks. The special case is '-' - it indicates that the configuration blocks are not declared by a particular plugin.
   Example:

   ```none
   com.gradle.plugin-publish    pluginBundle,gradlePlugin
   org.gradle.kotlin.ktlint-convention
   tests/build.gradle.kts
   :osgi-test
   -                            jmh
   ```
   This configuration will make the build ignore `com.gradle.plugin-publish` and
   its configuraiton blocks `pluginBundle{}` and `gradlePlugin{}`,
   remove `tests/build.gradle.kts` from the build and exclude `osgi-test` project.
   In addition `jmh` configuration block is disabled.


4. To build only some subprojects and ignore the others, pass the Gradle tasks to `dh_auto_build`:

   ```makefile
   override_dh_auto_build:
   	dh_auto_build -- :project1:jar :project2:jar
   ```
## Caveats

- Gradle is run with `--offline`: every plugin and dependency must come from the archive.
  Dependencies declared with a version range (for example `org.foo:bar:1.0+`) are not handled.
- Transitive dependencies whose resolved version is neither `debian` nor a generic `*.x` version must be pinned in `debian/maven.rules` to preserve the version, with a rule like `org.foo bar * * * *`.
- The Gradle version in the archive (4.x) is much older than what most upstream projects require, so patching `build.gradle` and `settings.gradle` — to remove unsupported plugins and newer DSL features — is often the largest part of the work.
- The major difference between Maven and Gradle build: `maven-debian-helper` populates Maven repository in `debian/maven-repo` and writes stub POM files (defined in `/etc/maven/fake-poms.conf` and `debian/fake-conf.poms`) and `gradle-debian-helper` uses Gradle plugin and `gradle` patch to rewrite or ignore Maven coordinates in runtime.

## Further Reading

General reference: [Debian Java packaging with Gradle](https://wiki.debian.org/Java/Packaging/Gradle).
