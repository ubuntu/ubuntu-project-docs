(EvolutionEWS-test-plan)=
# Evolution EWS test plan

Below are the test cases that should be run when `evolution-ews` is updated to new major releases in the development version of Ubuntu. These should also be run for all `evolution` Stable Release Updates.


## Pre-requisites

1. Have a Microsoft 365 account
2. Remove the `evolution-ews` package if installed, keeping only `evolution-ews-core`
3. Install the update
4. Log out and log back in (or restart)


## Add online account

1. Open the Settings app (`gnome-control-center`)
2. Navigate to "Online Accounts"
3. Click "Microsoft 365" under "Connect an Account"
4. Click "Sign In..."
5. Follow the steps in your web browser to log in
6. Return to Settings
7. Click "Microsoft 365" under "Your Accounts"
8. Ensure that the "Mail", "Calendar" and "Contacts" toggles are enabled


## Test case (Calendar)

1. In your web browser, navigate to <https://outlook.live.com/calendar/0/>
2. Create a new event for today
3. Open the Calendar app (`gnome-calendar`)
4. Hit {kbd}`F5` to synchronize the remote calendars
5. Verify that event you created is visible
6. Select the event
7. Modify the event title and schedule
8. Verify that the event was updated in the Calendar app
9. Verify that the event was updated in <https://outlook.live.com/calendar/0/>
10. Select the event again
11. Delete the event
12. Verify that the event is no longer visible in the Calendar app
13. Verify that the event is no longer visible in <https://outlook.live.com/calendar/0/>


## Optional test case (Contacts)

1. In your web browser, navigate to <https://outlook.live.com/people/0/>
2. Create a new contact
3. Open the Contacts app (`gnome-contacts`)
4. Verify that the contact you created is visible
5. Select the contact
6. Modify the contact information
7. Verify that the contact information was updated in the Contacts app
8. Verify that the contact information was updated in <https://outlook.live.com/people/0/>
9. Select the contact again
10. Delete the contact
11. Verify that the contact is no longer visible in the Contacts app
12. Verify that the contact is no longer visible in <https://outlook.live.com/people/0/>


## Optional test case (Email)

1. Send an email to your Microsoft 365 address
2. Open the Evolution app
3. Select the "Mail" view, from the bottom-right menu
4. Verify that you can see the email in your inbox
5. Click "New" From the top-left corner
6. Write an email to another email address of yours
7. Verify that you received the email
