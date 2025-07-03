# Partner archive

The Canonical partner archive, though not part of Ubuntu proper, is managed
using the same tools and queues. As such, use the same procedures when
processing partner packages. E.g.:

```text
$ ./queue -s hardy info
Listing ubuntu/hardy (New) 2
---------|----|----------------------|----------------------|---------------
 1370980 | S- | arkeia               | 8.0.9-3              | 19 hours
	 | * arkeia/8.0.9-3 Component: partner Section: utils
 1370964 | S- | arkeia-amd64         | 8.0.9-3              | 19 hours
	 | * arkeia-amd64/8.0.9-3 Component: partner Section: utils
---------|----|----------------------|----------------------|---------------
                                                               2
```

Notice `'Component: partner'`. Use `-A ubuntu/partner` to remove a package:

```none
$ ./remove-package -m "request from First Last name" \
  -A ubuntu/partner -s precise adobe-flashplugin
```

The rules governing package inclusion in partner are not the same as those for
the main Ubuntu archive. See
[Extension Repository Policy](https://wiki.ubuntu.com/ExtensionRepositoryPolicy)
for the Technical Board's requirements regarding the contents of add-on
repositories made available through the `Software Sources` interface.

