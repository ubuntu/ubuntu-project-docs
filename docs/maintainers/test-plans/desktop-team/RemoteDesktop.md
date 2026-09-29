(RemoteDesktop-test-plan)=
# Remote Desktop test plan

Below are the test cases that should be run when `gnome-remote-desktop` is updated to new major releases in the development version of Ubuntu. These should also be run for any `gnome-remote-desktop` Stable Release Update.


## Basic RDP test case

1. Install all updates. Log out and log back in.
2. Open the Settings app to the Sharing page. Turn on Desktop Sharing and turn on Remote Control.
3. From a second computer, open Remmina.

   The Remote Desktop page on the first computer provides the username and password to use. It also shows the computer name. If you want to use your IP address instead, you can find it with `ip a` or in the Settings app > Wifi > gear button. If you are connected via Ethernet, use the Network page instead of the Wifi page.

4. Change the protocol to RDP in the address bar. Fill in the first computer's name or IP address and press {kbd}`Enter`. On many network's you need to add a `.local` suffix to the computer's name for it to work.
5. On the next screen, fill in your username and password. On the first computer you can click the Show Text button to see the password. (A password is automatically assigned but it can be changed.)
6. Ensure that the connection works.


## Basic remote login test case (for Ubuntu 24.04 LTS and later only)

1. Install all updates. Log out and log back in.
2. Open the Settings app to the System page. Click Remote Desktop. Click Remote Login.
3. Unlock the page.
4. Turn on Remote Login.
5. Create a username and password. This is not a real user but only authentication for remote clients to be able to access the login screen.
6. Log out.
7. From a second computer, open Remmina.
8. Change the protocol to RDP in the address bar. Fill in the first computer's name or IP address and press {kbd}`Enter`. On many network's you need to add a `.local` suffix to the computer's name for it to work.
9. On the next screen, fill in the username and password from the Remote Login screen.
10. You should now see the login screen.
11. Log in to one of the accounts. Login should complete successfully and you should be able to use the Ubuntu Desktop. On the first computer, the login screen should still be showing.

Note that Remote Login requires working Wayland.


## Basic VNC test case (for Ubuntu 22.04 LTS only)

1. Do the Basic RDP Test Case but this time also enable the Legacy VNC option on the Remote Desktop Sharing page.
2. In Remmina, change the protocol to VNC, fill in the first computer's name or IP address and press {kbd}`Enter`.
3. Ensure that the connection works.

Note: The VNC feature was removed from Ubuntu 22.10 so this test case is only for Ubuntu 22.04 LTS.


## Audio forwarding test case

1. Install all updates. Log out and log back in.
2. Open the Settings app to the Sharing page. Turn on Sharing and turn on Remote Desktop Sharing.
3. From a second computer, open the Remmina snap.
4. Create a new connection:
   1. Protocol: RDP
   2. Basic > Server: The first computer's name or IP address
   3. Basic > Username: The configured RDP username
   4. Basic > Password: The configured RDP password
   5. Advanced > Audio output mode: Local
5. Save and Connect
6. You may be prompted to accept the security certificate with a warning that the identify of the remote computer cannot be verified. Click Yes to proceed.
7. You should be able to view the remote desktop now.
8. Open an audio file. Play the file. You should hear the audio on the second computer.


## New hardware acceleration feature

As of Resolute, you should see logging similar to,

`Jul 13 17:51:21 framework gnome-remote-desktop-daemon[58439]: [HWAccel.Vulkan] Initialization of Vulkan was successful`

Indicating a hardware-accelerated context was successfully negotiated. If that doesn't show up and you have capable hardware, investigate.


## What could go wrong

RDP Sharing is a new feature for Ubuntu 22.04 LTS as part of GNOME 42. (Previously only VNC Sharing was offered.)

RDP Sharing can be used for providing remote support so it's important that this feature works well because it may be difficult for the remote admin to fix issues in person.

`gnome-remote-desktop` is part of GNOME Core and falls under the GNOME Stable Release Update microrelease exception.
