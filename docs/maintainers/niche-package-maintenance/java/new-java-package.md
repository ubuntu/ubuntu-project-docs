(new-java-package)=
# New Java package

Java-based projects use a number of build systems: Maven, Gradle, Ant, Mill, etc.
The universal way to start a Java-based package is to use `dh_make`; see {ref}`how-to-create-a-new-package`.

[Debian policy for Java](https://www.debian.org/doc/packaging-manuals/java-policy/) outlines the filesystem structure of
the Java package: Java libraries are installed into `/usr/share/java`; Maven artifacts (POMs and symbolic links to jars) are installed into `/usr/share/maven-repo`.

Debian provides additional helpers and build system support for the most common Java build systems:
- Maven: {pkg}`maven-debian-helper`, see {ref}`new-maven-package`.
- Gradle: {pkg}`gradle-debian-helper`, see {ref}`new-gradle-package`
- Ant: debhelper's built-in Ant build system, usually combined with {pkg}`javahelper`, see {ref}`new-ant-package`

## {pkg}`javahelper`

{pkg}`javahelper` provides a simple interface to package Java classes into jar file. It is primarily used to build projects that do not provide a build system.

The snippet below provides a minimal set of commands to build a jar file with `javahelper`:

```none
JAVA_HOME=/usr/lib/jvm/default-java
CLASSPATH=/usr/share/java/esd.jar:/usr/share/java/jsch.jar

%:
        dh $@ --with javahelper

override_auto_dh_build:
    jh_build weirdx.jar src

```

{pkg}`javahelper` [tutorial](file:///usr/share/doc/javahelper/tutorial.html) provides
a comprehensive overview of the options and configuration files.

## Other build systems

Build systems without helper support in the archive  or projects with no build system at all - for example the source-only artifacts published on Maven Central - can be built with {pkg}`javahelper` alone:
- Declare the jars to build and their source directories in `debian/javabuild` (one `<jar-file> <source-directory>` pair per line), or call `jh_build` in `debian/rules`; options such as `--javacopts='-encoding UTF-8'` adjust the compilation.
- Install the jars with a `debian/jlibs` file or `jh_installlibs`.
- Generate the runtime dependencies with `jh_depends` and the `${java:Depends}` substvar.

See the [no build system examples](https://wiki.debian.org/Java/Packaging/NoBuildSystem) on the Debian wiki.

## Forcing the build system

Upstream projects often ship several build definitions (for example both `pom.xml` and `build.gradle`).
Pass `--buildsystem=maven` (or `--buildsystem=gradle`) to `dh` to select the correct build system.

## Publish Maven artifacts from non-Maven build

{pkg}`maven-repo-helper` provides utilities `mh_installpoms`, `mh_install_jar` to install Maven artifacts in `/usr/share/maven-repo`, see {ref}`new-maven-package`.

## Further Reading

[Debian Java packaging](https://wiki.debian.org/Java/Packaging) provides instructions
on contributing changes to Debian.