(units-policy)=
# Units policy

This policy defines how units (file sizes, memory sizes, data transfer rates) should be displayed in Ubuntu software.

## Rationale

There are two ways to represent large quantities:

* **Decimal (base-10):** multiples of 1000, using [SI prefixes](https://en.wikipedia.org/wiki/Metric_prefix) (KB, MB, GB, ...).
* **Binary (base-2):** multiples of 1024, using [IEC prefixes](https://en.wikipedia.org/wiki/Binary_prefix) (KiB, MiB, GiB, ...).

Historically, many applications used SI prefix names while dividing by 1024, creating ambiguity. A "KB" could mean 1000 bytes or 1024 bytes depending on the application. This policy resolves that ambiguity.

## Recommendation

* Use **IEC binary prefixes** (KiB, MiB, GiB, TiB, ...) for quantities that are naturally measured in powers of two (file sizes, memory sizes).
* Use **SI decimal prefixes** (KB, MB, GB, TB, ...) for quantities that are naturally measured in powers of ten (disk capacities, network speeds, clock rates).
* When in doubt, default to **base-2 with IEC prefixes** for file and memory sizes.

## Packaging

When packaging software, the maintainer must ensure the software reports units in accordance with this policy. If upstream software uses SI prefix names for binary quantities, it should be patched to use IEC prefixes instead.

## Exceptions

Command-line tools are exempt from this policy when they:

* Are command-line tools whose output is often parsed by machine (for example, in scripts).
* Display only the prefix without the unit (for example, `M` instead of `MB`).

## See also

* [SI prefixes (Wikipedia)](https://en.wikipedia.org/wiki/Metric_prefix)
* [Binary prefixes (Wikipedia)](https://en.wikipedia.org/wiki/Binary_prefix)
* [ISO/IEC 80000](https://en.wikipedia.org/wiki/ISO/IEC_80000)
