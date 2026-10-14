(ubuntu-image-builds)=
# Ubuntu image builds

This page explains how Ubuntu ISO and preinstalled image builds work, from trigger to publication.

## Overview

Ubuntu produces several image types:

- **Classic installer ISOs** (Desktop, Server) — e.g. `ubuntu/daily-live/current/`
- **Classic preinstalled images** — e.g. `ubuntu-server/daily-preinstalled/current/`
- **Core preinstalled images** (ubuntu-core) — e.g. `ubuntu-core/18/stable/current/`

## Build pipeline

1. **Trigger** — An image build is triggered automatically via cron or manually using the web UI.

1. **ubuntu-cdimage** — The central orchestrator. It starts `livefs` builds on Launchpad, downloads results, runs `debian-cd`, and publishes images.

1. **Setup** — `ubuntu-cdimage` performs basic project setup for the requested build configuration.

1. **`livefs` builds** — `ubuntu-cdimage` starts `livefs` builds on Launchpad for each requested architecture, using `live-build` to create the `rootfs`.

1. **livecd-`rootfs`** — An Ubuntu config overlay for `live-build` that customizes the `rootfs` build. Key customization hooks:

   - `auto/config` — initial configuration (project, arch, sub-architecture)
   - `.chroot` hooks — modify the `rootfs` contents
   - `auto/build` — finalise the `rootfs` build
   - `.binary` hooks — final customization

1. **Mirror sync** — A local mirror is synchronised in parallel to ensure no packages are stale.

1. **Intermediate steps** — `ubuntu-cdimage` runs `germinate` and other preparation steps.

1. **Wait for `livefs`** — `ubuntu-cdimage` waits for all `livefs` builds to complete and downloads them. Failed builds are reported by email to `ubuntu-cdimage` members.

1. **debian-cd** — `ubuntu-cdimage` calls `debian-cd` to create installer images:

   - Prepares the installer package pool
   - Configures boot (Grub, kernel selection)
   - Makes images bootable
   - Generates ISOs via `xorriso`
   - Generates file manifests

1. **Publishing** — `ubuntu-cdimage` copies images to the relevant build-stamp directory and performs a mirror sync to publish.

## Useful resources

- Build logs: `https://ubuntu-archive-team.ubuntu.com/cd-build-logs/`
- Crontab: `https://git.launchpad.net/ubuntu-cdimage/tree/etc/crontab`
- `livefs` build testing: [Testing a change to livecd-`rootfs` on Launchpad](https://discourse.canonical.com/t/testing-a-change-to-livecd-`rootfs`-on-launchpad/1518)
