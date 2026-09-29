(PipewireMediaSession-test-plan)=
# PipeWire Media Session test plan

Since `pipewire-media-session` doesn't include a testsuite nor autopkgtests we will follow a manual testplan to verify updates.

Currently we are not using `pipewire` as a sound server so its use is limited to screen recording and sharing.


## Setup

* Ensure a GNOME session, `gnome-remote-desktop` and `pipewire-media-session` are installed.
* Log into the GNOME session


## Testing screen recording

* Hit {kbd}`Ctrl` + {kbd}`Shift` + {kbd}`Alt` + {kbd}`R`
  * a red circle icon should be displayed in the top panel indicating recording has started

* Hit {kbd}`Ctrl` + {kbd}`Shift` + {kbd}`Alt` + {kbd}`R` again
  * the circle should be removed

The recording should be available in the standard xdg Video directory (`~/Video` in english)


## Testing screen sharing

* Go to settings -> Sharing
* Enable sharing in the headbar if needed
* Click on Screen Sharing to enable it, check that remote login is enabled

On another machine

* Install a VNC client on another machine
* Try to connect to your linux desktop
  * The desktop should prompt to allow access, one accepted the VNC client should be able to see the session
