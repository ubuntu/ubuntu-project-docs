(UbuntuProDesktop-test-plan)=
# Ubuntu Pro Desktop test plan

Since the Ubuntu Pro package isn't easy to integrate to `autopkgtest`, we have a manual test plan.

## On Ubuntu 26.04 LTS and later

Open the Ubuntu Pro settings in the Security Center.

## Before Ubuntu 26.04 LTS

Open the Ubuntu Pro settings in the Software & Updates (`software-properties-gtk`) app.

Note that Ubuntu Pro was called Ubuntu Advantage before Ubuntu 22.04 LTS, and its command-line tool was called `ua`.

## Test the subscription attachment

Verify that the behavior is consistent between all the interfaces.

1. Check the current status of your Ubuntu Pro subscription.

    * In the graphical interface.

    * On the command line:

        ```{terminal}
        :user:
        :host:
        :dir:
        :copy:
        pro status
        ```

    * Using DBus:

        ```{terminal}
        :user:
        :host:
        :dir:
        :copy:
        gdbus call --system --dest com.canonical.UbuntuAdvantage --object-path /com/canonical/UbuntuAdvantage/Manager --method org.freedesktop.DBus.Properties.Get com.canonical.UbuntuAdvantage.Manager

        Attached
        ```

1. If it's not attached, attach it. You can find your subscription key at <https://ubuntu.com/pro>.

    * In the graphical interface.

    * On the command line:

        ```{terminal}
        :user:
        :host:
        :dir:
        :copy:
        pro attach <key>
        ```

    * Using DBus:

        ```{terminal}
        :user:
        :host:
        :dir:
        :copy:
        gdbus call --system --dest com.canonical.UbuntuAdvantage --object-path /com/canonical/UbuntuAdvantage/Manager --method com.canonical.UbuntuAdvantage.Manager.Attach <key>
        ```

1. Detach your subscription.

    * In the graphical interface.

    * On the command line:

        ```{terminal}
        :user:
        :host:
        :dir:
        :copy:
        pro detach
        ```

    * Using DBus:

        ```{terminal}
        :user:
        :host:
        :dir:
        :copy:
        gdbus call --system --dest com.canonical.UbuntuAdvantage --object-path /com/canonical/UbuntuAdvantage/Manager --method com.canonical.UbuntuAdvantage.Manager.Detach
        ```
