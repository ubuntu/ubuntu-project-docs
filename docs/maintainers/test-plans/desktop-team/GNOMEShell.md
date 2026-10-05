(GNOMEShell-test-plan)=
# GNOME Shell test plan

Below are the test cases that should be run when `gnome-shell` is updated to new major releases in the development version of Ubuntu. These should also be run for all `gnome-shell` Stable Release Updates.


## Test case 1

1. `sudo apt install gnome-session gnome-shell-extensions`
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


## Test case 2

Because a GNOME Shell update years ago broke some GNOME Shell extensions, it's also requested that we do a basic test of all the extensions included in the Ubuntu repositories.

[This discourse post lists the currently available extensions](https://discourse.ubuntu.com/t/removal-of-gnome-shell-extension-from-universe-and-stop-auto-syncs/18437/9). `apt-file -l search /usr/share/gnome-shell/extensions` will list all the packages providing extensions in a given release.

1. Install all the extensions.
2. Log out and then log back in.
3. Enable all the extensions. This is a way to do it:
   ```none
   apt install gnome-shell-extension-manager
   extension-manager
   ```
4. Verify that they can all be enabled without showing an error.
5. Verify that the basic functionality of each extension works as expected.


## Test case 3 (optional)

This test case is optional, if you don't have easy access to a captive portal

1. Install the update
2. Log out and then log back in
3. Connect to a ["captive portal"](https://en.wikipedia.org/wiki/Captive_portal)
4. You should see a popup window showing the webpage to get full access to the network by logging in or accepting the user agreement.


## What could go wrong

GNOME Shell is the heart of the Ubuntu desktop experience.

A severe enough bug could mean that people are unable to use their desktop version of Ubuntu.

Smaller bugs could interrupt people's workflows.

While GNOME Shell **used** to be under the GNOME MRE, {ref}`this is no longer the case <reference-exception-GNOMEUpdates>`.

Although Shell is no longer under an MRE, this test plan is still a good smoke test in addition to tests for the specific bug fixes in any GNOME Shell SRU uploads.


## Other info

`gnome-shell` provides the GNOME version number for the Settings app About page, as of Ubuntu 22.10 (in earlier Ubuntu releases, this was provided by `gnome-desktop`/`gnome-desktop3`)

Test plan approved by RAOF on behalf of the SRU team on 2023-06-30
