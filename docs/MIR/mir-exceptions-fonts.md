(mir-exceptions-fonts)=
# MIR exception - font packages

```{include} _mir-series.md
```





Given that fonts are just data, there's no way for them to trip any of the
problems that would cause us to not want to support them. Therefore not all of
the process have to be followed for these.

Unfortunately there were cases where `src:font-*` packages contained way
more than just a font -- due to that, either the MIR team (if an MIR bug was
filed) or the Ubuntu-Archive team (on promoting it) has to do a spot check that
neither the source nor the created binary packages violate these assumptions.

The only limitation is that the package needs a valid team subscriber before
being promoted by an Archive Admin -- just in case anything might come up later.
The MIR team should try to clarify that with the team that owns the depending
package to own the font as well (read: without the overhead of a full MIR process).
