(GnomeControlCenter-test-plan)=
# GNOME Control Center test plan

If a step fails, only mark the SRU as verification-failed if it is a regression, i.e., the current version (in normal updates pocket) is not affected.


## Settings application

* Open the settings from the top right indicator, verify that it starts correctly
* Check that the list of panels listed as section bellow is displayed in the left side pane
* Start typing, verify that the search entry display on the top left and that results are filtered according to keywords
* Hit {kbd}`enter`, the panel corresponding to the item which was selected by the search should be displayed, the search UI should close
* Click on the 3-lines icons on the right of the side pane, verify that the 3 items (Keyboard shortcut, help, about) open the corresponding dialogs


## Wi-Fi

* Check that the 'Visible Networks' section includes the expected APs
* Try connecting and disconnecting to an AP
* Click on the options icon on the right on one of the network and verify that the details dialog opens and is showing the expected configuration
* Enable the hotspot and try connecting from another device
* Try turning WiFi off and verify that the connectivity indicator of the shell reflect the new status


## Network

* Click on the '+' next to the VPN section and configure a VPN


## Bluetooth

* Check that the devices known to the system (which have been paired before) at listed.
* Pair a new device
* Forgot a device


## Display

* Check that the screen configuration is correctly reflect
* Try changing the layout and resolution or your screens
* Try changing the scaling factor


## Sound

* Check that input/output device are correctly listed
* Do the output test, verify that the sound is working
* Change the volume and verify it has an impact
* Check that indicator bar on the right of the input section react to sounds
* Enable/disable over-amplification and verify that the output slide adapt as expected


## Power

* If you are on a device with a battery verify that the status displayed is correct
* Verify that the power mode section list the same profiles than `powerprofilesctl`
* Change the profile and verify with `powerprofilesctl` that it was correctly changed
* Change the Screen Blank timeout and wait for the delay to verify the configuration is working
* Toggle the show battery percentage control and check that the top panel correctly reflect the option


## Multitasking

* Toggle the Hot Corner setting and verify the shell behaves according to the configuration
* Toggle the Active Screen edges setting and verify the shell behaves according to the configuration

  :::{warning}
  This setting is currently overridden by enhanced tiling in **Ubuntu Desktop** section
  :::

* Switch between dynamic and fixed workspaces and verify that the layout adapts
* If you have a multi monitor setup check if the workspaces option correctly change the behaviour
* Change the app switching configuration and verify that the shell reflects the choice


## Appearance

* Switch between light and dark mode and verify that the wallpaper and colors adapt
* Try changing the default wallpaper, verify that the configuration is correctly adapted
* Select a different accent color, verify that the desktop interfaces (GTK) reflects


## Ubuntu Desktop

* Enable/Disable the desktop icons, change the size and position. Verify that the desktop view refreshes according to the settings
* Enable/Disable the Dock auto-hide and panel mode, change the position and icons size. Verify that the dock adapts to the settings
* Enable/Disable tiling, popup and groups and verify that the shell behavior is adapted to the configuration.


## Apps

* Go to the 'Default Apps' section, try to change the default for web/mail/photos and verify that the corresponding actions call the right application (`gio open` on an `http:` or `mailto:` URL, opening a photo from `nautilus`)

  :::{note}
  If you don't have at least two apps for each category, `apt install claws-mail qutebrowser neomutt` will suffice.
  :::

* Go back to the top level 'Apps' pane.
* Verify that applications are listed
* Select a snap and verify that the connections are correctly listed and reflecting the right status (so matching `snap connections $snapname`)


## Notifications

* Enable Do Not Disturb mode and do a `sleep 10; notify-send Msg`. Verify that the notification isn't displayed
* Disable lock screen notification, do a `sleep 10; notify-send Msg` and lock the screen. The notification shouldn't show on the lock screen.
* Turn off notification for one application in the list and verify that the setting is respected by using the application in a situation where it should send a notification.


## Search

* Disable App Search and verify that the shell stops proposing integration with the applications listed below (typing 1+2 for example, if the `gnome-calculator` provider is installed it should return 3 but not if App Search is disabled)
* Disable some search locations and try to find files from those in `nautilus`' **Search Everywhere** (magnifying lens on the top left corner of the window, **not** 'Search current folder'), it should not list them. Enable it back and verify that `nautilus` is able to find the content again
* Disable one of the providers of the list and verify in the shell that the corresponding integration is disable (using the previous calculator steps for example)


## Online accounts

* Enable an online account, you should be able to go through the steps and see the account listed under the 'Your accounts' section
* Verify that the integration to the desktop is working (by example a google account should make `gnome-calendar` see your calendar events)
* Remove the account, it shouldn't be listed in the 'Your accounts' section anymore


## Sharing

* Change the device name. Verify that `/etc/hostname` reflect the name change. Then go back to the initial name.
* Enable file sharing. Verify from another machine that you can connect to the URL indicated.

  :::{important}
  If `org.gnome.desktop.file-sharing` does not exist in `dconf`, the entry will be missing.
  :::

* Enable media sharing. Verify from another machine that you can see the corresponding multimedia content.

  :::{important}
  If you do not have a [UPnP or DLNA enabled device such as a phone, TV or game console](https://help.gnome.org/users/gnome-help/stable/sharing-media.html.en), this won't work.
  :::


## Mouse & touchpad

* Change the primary button and pointer speed, verify that the change are reflected on the behaviour


## Keyboard

* Add a new layout. Verify that it's listed in the shell panel and that selecting it change the input behavior.
* Remove a layout and verify it's not listed in the shell anymore.
* Go the keybinding section, change some configuration and verify the new keybinding is working.


## Color

* Select your screen in the list. Click Add Profile.
* Verify that the colors change according to the profile.

  :::{tip}
  Suggestion: 'test profile blue'.
  :::

* Remove the profile and verify the color are reset.


## Printers

* Verify that the configured printers are listed
* If you have access to a printer try adding it and print a test page.


## Accessiblity

* Enable large text, verify that the labels are getting bigger in the shell and the applications.
* Enable high contrast, verify that the theme is changing accordingly (some of the icons are become black&white for example)
* Enable the onscreen keyboard, verify that it's displayed when focusing a text field in a GTK application (e.g. `gnome-terminal`) and can be used


## Privacy & security

* Change the screen lock delay. Don't touch to the computer for the corresponding time and confirm that the screen get locked.


## System

* Change the language. Restart the session and verify that the new language is being used.
* Disable Automatic Date&Time and change the timezone and time manually. Verify that the system configuration is reflecting the change (clock on the panel, `timedatectl`)
* Enable back automatic time, verify that the clock is synchronized.
* Go the users section, add an user. Try to log using the new user and verify the account is working
* Go the About section and verify that the information displayed match the system.
