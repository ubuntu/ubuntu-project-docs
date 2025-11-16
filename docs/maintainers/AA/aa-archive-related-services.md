(aa-archive-related-services)=
# Archive-related services 

```{note}
This page is a seed which will document which services are where, and how they
work. The previous list is being replaced as services are migrated to become
charmed hosted services.
```

This page documents the services used by the
{ref}`Archive Administrators <archive-administration>` and how they work.

## List of services on `ubuntu-archive-toolbox`


### Seeds/germinate


### Debian auto-import

When the next version of Ubuntu is in full development, we will automatically
pull some packages from Debian `unstable` into the new series' `-proposed`
pocket. Importantly, we're only importing the sources, and rebuild the binaries
from scratch.

The service is set up on the `ubuntu-archive-toolbox` machine, as a cronjob
running every 6 hours. The script itself is `auto-sync` in the
[`ubuntu-archive-tool`
repo](https://code.launchpad.net/~ubuntu-archive/ubuntu-archive-tools/+git/ubuntu-archive-tools/).

Packages eligible for the sync are any package that doesn't have
Ubuntu-specific changes. The heuristic is based on version number: if it
contains `ubuntu`, it is considered to have a delta.

In addition to delta-containing packages, some packages are entirely excluded from
the sync through the [sync-blocklist](https://code.launchpad.net/~ubuntu-archive/+git/sync-blocklist).

#### Disabling auto-import

To disable auto-import, the usual procedure is to edit the
`ubuntu-archive-toolbox` crontab to add a `--dry-run` parameter to the
appropriate line, e.g.

```
# Before
0 5,11,17,23 * * *      PYTHONPATH=/home/ubuntu-archive/python auto-sync --log-directory ~/public_html/auto-sync --batch
# After
0 5,11,17,23 * * *      PYTHONPATH=/home/ubuntu-archive/python auto-sync --dry-run --log-directory ~/public_html/auto-sync --batch
```

This allows for the continuing generation of logs, potentially useful for
monitoring.

### `phased-updater`


### Bugpatterns (related to Error tracker)


### Team-to-package mapping


### Component-mismatches


### OEM meta packageset sync


### Cleaning `buildd` builders


### Permission report


### Packageset report


### Auto-accept


### Transition tracker (`ben`)


## Debugging broken jobs on `ubuntu-archive-toolbox`



