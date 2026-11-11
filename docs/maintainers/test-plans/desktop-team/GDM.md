(GDM-test-plan)=
# GDM test plan

Below are the test cases that should be run when GDM is updated to new major releases in the development version of Ubuntu.

These should also be run for all GDM Stable Release Updates.


## Test case 1

**Login**

1. `sudo apt install gnome-session gnome-classic`
2. Install the update.
3. Log out.
4. Select your name on the login screen.
5. Click the gear button to choose a session to log in to.
6. Finish logging in.
7. Verify that things continue to work well for all these sessions:
   * GNOME
   * GNOME Classic
   * Ubuntu
   * Ubuntu on Xorg
     (only for ubuntu 25.04 or older)


## Test case 2

**User switch and user lock**

1. From a logged-in session, select the _Switch user_ option
2. You need to be able to login as another user
3. You need to be able to unlock and go back to the the previous session


## Test case 3

**Smart card authentication**

In absence of a physical smart card, this test can be performed by simulating one in software. Follow {ref}`this guide <GDM-Smartcard-test-plan>`.

1. Configure setup with smart card authentication following [this tutorial](https://ubuntu.com/tutorials/how-to-use-smart-card-authentication-in-ubuntu-desktop)
2. Ensure smart cart authentication works, plugging in the card both before and after `gdm` has been started
3. Once logged in, unlocking the screen should work with smart card


## Test case 4

**Fingerprint authentication** - _If hardware supports it_

1. Configure user to enable fingerprint authentication from user session (Settings -> Users -> Fingerprint)
2. Ensure that after the user has been selected, it's possible to log-in with fingerprint
3. Once logged in, unlocking the screen should work with fingerprint


## Test case 5.a

**NVIDIA (Ubuntu 24.10 and 25.04)** - _For desktops or laptops with NVIDIA graphics_

This test verifies the default session type for NVIDIA systems running Ubuntu 24.10 or newer

1. Boot to the login screen
2. Select your name
3. Click the cogwheel at the bottom-right of the screen
4. Verify that all these options are listed:
   * Ubuntu
   * Ubuntu on Xorg
5. Verify that there does not exist:
   * Ubuntu on Wayland


## Test case 5.b

**NVIDIA (Ubuntu 24.04 or older)** - _For desktops or laptops with NVIDIA graphics_

This test verifies the default session type for NVIDIA systems running Ubuntu 24.04 or older

1. Boot to the login screen
2. Select your name
3. Click the cogwheel at the bottom-right of the screen
4. Verify that all these options are listed:
   * Ubuntu
   * Ubuntu on Wayland
5. Verify that there does not exist:
   * Ubuntu on Xorg


## Test case 5.c

**NVIDIA (Ubuntu 25.10 and newer)**

Skip. NVIDIA is no longer handled as a special case.


## Test case 6

**First boot**

On the first boot of a pre-installed images with no configured users, GDM will hand-off the desktop to a temporary session that runs `gnome-initial-setup` as a first-boot configuration wizard.

This test will simulate a first boot.

1. Reboot to the GRUB menu (hold {kbd}`Esc` at the BIOS splash screen)
2. With the up/down arrow keys, highlight "Ubuntu"
3. Press '{kbd}`e`'
4. With the up/down arrow keys, highlight the line beginning with "linux "
5. Press {kbd}`End`
6. Type "` gnome.initial-setup=1`"
7. Press {kbd}`Ctrl` + {kbd}`X`
8. Verify that you booted into the first-boot wizard.

Beware that navigating through the first-boot wizard will overwrite system configuration, so avoid doing that and immediately reboot instead.


## What could go wrong

GDM is the main login manager for Ubuntu desktop.

A severe enough bug could mean that people are unable to use their desktop version of Ubuntu or to log in to a specific session.

Smaller bugs could interrupt people's workflows.
