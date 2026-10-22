(new-ant-package)=
# New Ant package

`debhelper` automatically detects a `build.xml` file and runs Ant, so an Ant-based package often needs nothing more than `ant` in `Build-Depends`.

Combine it with {pkg}`javahelper` to install the jars, manipulate `MANIFEST` files and generate the runtime dependencies.

Add the `${java:Depends}` substvar to the binary package's `Depends:` field, so that `jh_depends` (part of javahelper) can insert the runtime dependencies it derives from the build-dependencies.
A typical `debian/rules` looks like this:

```makefile
#!/usr/bin/make -f

export CLASSPATH=/usr/share/java/bsh.jar:/usr/share/java/slf4j-api.jar

%:
	dh $@ --with javahelper
```

## Caveats

- Ant has no formal conventions, and upstreams frequently include prebuilt jar and class files in their source releases.
  All prebuilt binaries must be removed before upload — repack the upstream tarball if necessary — so that everything is compiled from source.
- Point the compiler at the system libraries: patch the `<javac>` task in `build.xml` to use `<pathelement>` entries under `/usr/share/java`, or export `CLASSPATH` in `debian/rules` as shown above.
  An exported `CLASSPATH` is also recorded by javahelper, which inserts a matching `Class-Path` entry into the `MANIFEST` of the resulting jar, so that the runtime dependencies are found.
- To override only the file encoding, export `JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF8` in `debian/rules` instead of patching `build.xml`.
- Use `jh_installibs` to install the resulting jars into `/usr/share/java` with a `debian/<binary-package>.jlibs` file, and set `Class-Path` and `Main-Class` entries with a `debian/<binary-package>.classpath` or `debian/<binary-package>.manifest` file.
- If the build expects its dependencies as local files, a `debian/linkjars` file symlinks the system jars into the source tree and avoids patching `build.xml` altogether.
- To start an application, either ship a wrapper script using {pkg}`java-wrappers` (`find_java_runtime`, `find_jars`, `run_java`), or make the jar executable and let {pkg}`jarwrapper` run it through `binfmt`; `jh_depends` adds the `jarwrapper` dependency automatically for executable jars.

## Further Reading

General reference: [Debian Java packaging with Ant](https://wiki.debian.org/Java/Packaging/Ant).