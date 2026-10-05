(Mutter-test-plan)=
# Mutter test plan

Below are the test cases that should be run when `mutter` is updated to new major releases in the development version of Ubuntu. These should also be run for all `mutter` Stable Release Updates.


## Test case

1. `sudo apt install budgie-desktop gnome-session gnome-shell-extensions`
2. Install the update.
3. Log out.
4. Select your name on the login screen.
5. Click the gear button to choose a session to log in to.
6. Finish logging in.
7. Verify that things continue to work well for all these sessions:
   * Budgie (you can ask the Ubuntu Budgie team for help verifying this session. Note that this step is only required for Ubuntu 23.04 and earlier. Starting with Ubuntu 23.10, Budgie no longer uses the Mutter library.)
   * GNOME
   * GNOME Classic
   * Ubuntu
   * Ubuntu on Xorg

TBC: plan to repeat recurrence of mouse input latency regression that has occurred in the past


## What could go wrong

Mutter is an essential component of the default Ubuntu desktop which is also used by Edubuntu.

A severe enough bug could mean that people are unable to use their desktop version of Ubuntu.

Smaller bugs could interrupt people's workflows.

Mutter micro releases have generally been accepted as SRUs in the past. The .1 release is a little more risky with higher chance of breaking changes, but later releases are more limited to regular bug fixes.
<https://discourse.ubuntu.com/t/mutter-gnome-shell-are-no-longer-covered-by-the-gnome-mre/45218>


## Record of regressions

* 2023-06-08: [Mouse input latency is one frame higher than it was earlier](https://bugs.launchpad.net/ubuntu/+source/mutter/+bug/2023363)
* 2023-12-14: [Heavy stuttering in Firefox with `mutter` 45.1/45.2](https://bugs.launchpad.net/ubuntu/+source/mutter/+bug/2046360)
