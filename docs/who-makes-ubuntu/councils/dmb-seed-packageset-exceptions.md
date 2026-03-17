(dmb-seed-packagesets-exceptions)=
# DMB seed packagesets exceptions

As outlined for {ref}`seeds based packagesets <dmb-types-of-packagesets>`
there can be cases that cause such a package set to not be absolutely
equivalent to the seed.

Historically those exceptions have been tracked in
[this code](https://code.launchpad.net/~developer-membership-board/+git/packageset),
but when generating them was stopped it became a case by case decision
and was hard to track.

This page provides the compromise (over fully maintaining it in code) of at
least allowing us to track those exceptions along the rules that define
the process.

## ubuntu-server

### Related Seed(s)

* https://ubuntu-archive-team.ubuntu.com/germinate-output/ubuntu.resolute/server
* Anything supported-*-server in platform seeds like https://ubuntu-archive-team.ubuntu.com/germinate-output/ubuntu.resolute/supported-hardware-server

### Additions

Packages added in addition to what would be derived from the seeds:

| Package           | Reason |
|-------------------|------------------------------------------------------------------------------|
| `valkey`          | Not in main, but a common server use case the ubuntu-server team looks after |

### Removals

Packages removed in relative to what would be derived from the seeds:

| Package | Reason |
|---------|--------|
| `docker-buildx`, `docker-compose-v2`, `docker.io`, `docker.io-app`, `containerd`, `containerd-stable`, `runc-app`, `runc-stable` | Impact to a vast variety of workloads would bump the requirements too much |
| `cloud-initramfs-tools`, `cloud-utils`  | Impact to system boot would bump the requirements too much |
| `cloud-init`, `grub2` | Impact to system boot would bump the requirements too much |
