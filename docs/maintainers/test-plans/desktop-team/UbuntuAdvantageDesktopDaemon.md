(UbuntuAdvantageDesktopDaemon-test-plan)=
# Ubuntu Advantage Desktop Daemon test plan

Since the package isn't really easy to integrate to autopkgtest we have a manual testplan


## Use dbus calls to control the service

**Get the current `ua` status**

```none
$ gdbus call --system --dest com.canonical.UbuntuAdvantage --object-path /com/canonical/UbuntuAdvantage/Manager --method org.freedesktop.DBus.Properties.Get com.canonical.UbuntuAdvantage.Manager Attached
```

check that it matches what '`ua status`' reports

**If it's not attached to a subscription you can do it**

```none
$ gdbus call --system --dest com.canonical.UbuntuAdvantage --object-path /com/canonical/UbuntuAdvantage/Manager --method com.canonical.UbuntuAdvantage.Manager.Attach "TOKEN"
```

where TOKEN is your subscription key which you can find on <https://ubuntu.com/advantage>

**If it's attached you can detach it**

```none
$ gdbus call --system --dest com.canonical.UbuntuAdvantage --object-path /com/canonical/UbuntuAdvantage/Manager --method com.canonical.UbuntuAdvantage.Manager.Detach
```


## Using Software Properties

:::{warning}
Not available yet but should be before the LTS
:::

Use the `software-properties-gtk` controls to connect to the service
