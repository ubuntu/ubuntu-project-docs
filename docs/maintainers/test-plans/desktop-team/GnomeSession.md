(GnomeSession-test-plan)=
# GNOME Session test plan

Below are the test cases that should be run when `gnome-session` is updated to new major releases in the development version of Ubuntu. These should also be run for all `gnome-session` Stable Release Updates.


## Test case 1

1. Install the update
2. Log-out or reboot
3. Log-in to Ubuntu Desktop
4. Verify that the desktop loads correctly, with no errors
5. Log-out
6. Verify that you returned to the log-in screen correctly


## Test case 2

1. Install the update
2. Log-out or reboot
3. Log-in to Ubuntu Desktop
4. Open a web browser
5. Playback some video
6. Verify that the screen doesn't lock, dim, nor blank


## What could go wrong

`gnome-session` is the session manager for the GNOME desktop, included by default in Ubuntu Desktop and Edubuntu.

If there are bugs in `gnome-session`, in the worst case the user may be unable to log-in graphically.

`gnome-session` is part of GNOME Core and is included in the GNOME micro release exception

<https://ubuntu.com/project/docs/SRU/reference/exception-GNOME-Updates/>
