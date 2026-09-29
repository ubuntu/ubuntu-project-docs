(Calendar-test-plan)=
# GNOME Calendar test plan

Below are the test cases that should be run when `gnome-calendar` is updated to new major releases in the development version of Ubuntu. These should also be run for all `gnome-calendar` Stable Release Updates.


## Test case

1. Install the update
2. Open the Calendar app.
3. Open the ☰ menu and choose Online Accounts. The Settings app should open to the Online Accounts page. Click _Add an account_, choose Google and log in with your existing credentials for that service.
4. Close the Settings app. Any calendar events you have in your online account should show in the Calendar app
5. Click the time in the top bar of the screen in GNOME Shell. Events should also show below the calendar in this drop-down menu if you have any events today or if you click a day in the calendar that has an event.
6. Back in the Calendar app, check that editing calendar events works correctly.


## What could go wrong

GNOME Calendar is included by default in Ubuntu Desktop, Edubuntu, and Ubuntu Cinnamon.

If there are bugs in GNOME Calendar, Evolution (not installed by default) could be used instead.

GNOME Calendar can sync with Google or Microsoft Exchange online calendars. Therefore, bugs in editing calendar events can by synced to those services.

GNOME Calendar is part of GNOME Core and is included in the {ref}`GNOME micro release exception <reference-exception-GNOMEUpdates>`

Test plan approved by ChrisHalseRogers for the SRU team 2024-08-07
