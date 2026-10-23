(java-packaging)=
# {pkg}`java` packaging

How to create and update Java ecosystem packages in Ubuntu.

Java library and application packages in Ubuntu are largely shared with Debian and maintained by the [Debian Java Team](https://wiki.debian.org/Teams/JavaPackaging) on [Salsa](https://salsa.debian.org/java-team). Because package builds in the archive run without network access, Java build tools cannot download artifacts from remote repositories such as Maven Central or the Gradle Plugin Portal at build time. Instead, all build and runtime dependencies must be satisfied from packages already in the archive (installed under `/usr/share/java` and `/usr/share/maven-repo`).

```{toctree}
:maxdepth: 1

new-java-package
new-ant-package
new-maven-package
new-gradle-package
```
