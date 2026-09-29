(GnomeSettingsDaemon-test-plan)=
# GNOME Settings Daemon test plan

Below are the test cases that should be run when `gnome-settings-daemon` is updated to new major releases in the development version of Ubuntu. These should also be run for all `gnome-settings-daemon` Stable Release Updates.

The GNOME Settings Daemon is responsible for setting various parameters of a
GNOME Session and the applications that run under it.

All tests are meant to be executed from a GNOME Wayland desktop session (the default Ubuntu Desktop session).


## Test A11y

1. Enable the Screen Reader
2. Verify that the AT-SPI bus was enabled:
   ```none
   gdbus call --session -d org.a11y.Bus -o /org/a11y/bus -m org.freedesktop.DBus.Properties.Get org.a11y.Status IsEnabled
   ```


## Test color

1. Open `gnome-control-center` (Settings app)
2. Enable Night Light
3. Configure start and end times so that it should enable now
4. Verify that Night Light is active:
   ```none
   gdbus call --session -d org.gnome.SettingsDaemon.Color -o /org/gnome/SettingsDaemon/Color -m org.freedesktop.DBus.Properties.Get org.gnome.SettingsDaemon.Color NightLightActive
   ```

Whether the screen actually changed color depends on other components; in case it did not, that should not count as a failure of this test case.


## Test housekeeping - thumbnails

1. Set the thumbnails cache age to zero:
   ```none
   gsettings set org.gnome.desktop.thumbnail-cache maximum-age 0
   ```
2. Log-out and log-in (or reboot and log-in)
3. Wait at least 2 minutes
4. Verify that the thumbnails cache is empty:
   ```none
   find ~/.cache/thumbnails -type f
   ```
5. Restore the default cache age
   ```none
   gsettings reset org.gnome.desktop.thumbnail-cache maximum-age
   ```


## Test housekeeping - trash

1. Move some files to the trash bin
2. Run:
   ```none
   gdbus call --session -d org.gnome.SettingsDaemon.Housekeeping -o /org/gnome/SettingsDaemon/Housekeeping -m org.gnome.SettingsDaemon.Housekeeping.EmptyTrash
   ```
3. Verify that the trash bin is empty


## Test media keys

This test requires a keyboard with media control keys

1. Verify that the Volume Up/Down and Mute keys modify the volume
2. Start a media player, for example YouTube within Firefox
3. Verify that the Play/Pause/Next/etc... keys work as expected.


## Test power - idle suspend

This test requires a machine with suspend support.

1. Enable Automatic Suspend
2. Configure a low sleep timeout for the test:
   ```none
   gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 30
   ```
3. Wait 30 seconds
4. Verify that you saw a notification: "Suspending soon because of inactivity."
5. Verify that the machine went to sleep
6. Reset the default sleep timeout
   ```none
   gsettings reset org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout
   ```


## Test power - lid

This test requires a laptop with a sensor detecting when the lid is closed.

1. Inhibit suspend:
   ```none
   systemd-inhibit --what=handle-lid-switch gnome-session-inhibit --inhibit suspend sleep 60
   ```
2. Close the laptop lid
3. Verify that the session was locked.


## Test power - backlight

This test requires a laptop with supported screen backlight controls.

1. Open the Quick Settings menu at the top-right of GNOME
2. Verify that there is a brightness slider
3. Verify that moving the slider adjusts the screen brightness


## Teset rfkill

1. Open the Quick Settings menu at the top-right of GNOME
2. Enable Airplane Mode
3. Verify that Wifi and Bluetooth got turned off


## Test screensaver proxy

1. Run:
   ```none
   gdbus call --session -d org.freedesktop.ScreenSaver -o /org/freedesktop/ScreenSaver -m org.freedesktop.ScreenSaver.Inhibit "foo" "bar"
   ```
2. Verify that the command returned a number

   The session will be automatically uninhibited as soon as the `gdbus` command exits.


## Test sharing

This test requires that the `rygel` package is installed

1. Connect to a secure network
2. Run:
   ```none
   gdbus call --session -d org.gnome.SettingsDaemon.Sharing -o /org/gnome/SettingsDaemon/Sharing -m org.freedesktop.DBus.Properties.Get org.gnome.SettingsDaemon.Sharing CurrentNetwork
   ```
3. Verify that the command returned a non-empty identifier
4. Run:
   ```none
   gdbus call --session -d org.gnome.SettingsDaemon.Sharing -o /org/gnome/SettingsDaemon/Sharing -m org.freedesktop.DBus.Properties.Get org.gnome.SettingsDaemon.Sharing SharingStatus
   ```
5. Verify that the command returned the number "3", meaning "sharing is available"
6. Disconnect from the network
7. Verify that the same command now returns "0"


## Smartcard

This test would require a smartcard and a system configured for log-in with the smartcard.
Instead, we're just going to verify that the service is running and can perform a basic query.

1. Log-in without a smartcard.
2. Run:
   ```none
   gdbus call --session -d org.gnome.SettingsDaemon.Smartcard -o /org/gnome/SettingsDaemon/Smartcard/Manager -m org.gnome.SettingsDaemon.Smartcard.Manager.GetLoginToken
   ```
3. Verify that the command returned:
   ```none
   Error: GDBus.Error:org.gnome.SettingsDaemon.Smartcard.Manager.Error.FindingSmartcard: User was not logged in with smartcard.
   ```


## Test XSettings

1. Verify that the a11y bus is available to X11 apps:
   ```none
   xprop -root AT_SPI_BUS
   ```
