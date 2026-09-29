(Malcontent-test-plan)=
# Malcontent test plan

If a step fails, only mark the SRU as verification-failed if it is a regression, i.e., the current version (in normal updates pocket) is not affected.


## Parental controls

* Open the settings from the top right indicator
* Select "System" from the list of panels on the left, at the bottom
* Navigate to the "Users" page
* Add a new non-admin user with `gnome-control-center`
* Selecting "Parental Controls" in the UI after creating the new account should open the `malcontent-control` dialog
* Click unlock and enter your password to allow updating the app filter
* The dialog should only show two entries under "Application Usage Restrictions", "Restrict Web Browsers" and "Restrict Applications"
* Select "Restrict Applications" should open a dialog showing all apps
* Toggle the switch for an app and close the dialog
* Login to a user session with the restricted user account and confirm the application icon isn't show in the GNOME app grid
