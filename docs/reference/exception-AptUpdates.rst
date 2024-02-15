The APT developers maintain upstream stable branches for LTS releases of
Ubuntu. These will be uploaded to LTS releases using upstream version
numbers and no ubuntu downstream version components.

Each upstream release undergoes a dedicated CI pipeline that runs the
test suite as both root and a normal user whereas the autopkgtests only
cover the root portion.

These branches are not just used by Ubuntu themselves, they also provide
a clean base for delivering stable APT branches with important bug fixes
to other downstreams such as OpenEmbedded.
