(XdgDesktopPortalGnome-test-plan)=
# XDG Desktop Portal GNOME test plan

Since `xdg-desktop-portal-gnome` doesn't include a testsuite nor autopkgtests we will follow a manual test plan to verify updates.

The `xdg-desktop-portal-gnome` package provides the desktop portals specifics to the GNOME desktop, those were moved out of the GTK variant to make that one desktop neutral.

The portals provide an API that confined software can use to access to the system resources, the GNOME ones currently include

* Applications Selector
* Screenshot
* Screencast
* RemoteDesktop
* Lockdown
* Background
* Settings
* Wallpaper
* {spellexception}`FileSelector`


## Setup

Ensure you are using a GNOME based session and that `xdg-desktop-portal-gnome` is installed


## `portal-tests`

* Install the `portal-test` snap from the edge channel
* Start '`portal-test`'
* Try the different actions

That's going to exercise portals from the GTK and GNOME backends.


## Applications selector

* `snap install thunderbird`
* configure an account
* try to open an attachment from an email


## Screenshot

* Log into a Wayland session
* `snap install gimp`
* Try to take a screenshot from `gimp`

It should trigger the portal prompt and if allowed take the screenshot


## Screencast

* Log into a Wayland session
* `snap install obs-studio`
* Try to do a screen recording

It should trigger the portal prompt and if allowed do the recording


## Wallpaper

* `snap install eog`
* open an image with `eog`
* try to set it as desktop background

It should prompt for permission and set the wallpaper if allowed


## File selector

* `snap install firefox`
* file -> open a file
* it should display a {spellexception}`fileselector` allowing access to any directory from the system
