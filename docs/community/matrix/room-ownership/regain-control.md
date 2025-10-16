(matrix-regain-control)=
# How to regain control of a room

There are several possible scenarios where a room loses its administrator.
To ensure a good experience, we provided a fallback mechanism to all {ref}`public official rooms <matrix-rooms-spaces>` on the Ubuntu homeserver.


## Prerequisites

This guide applies to official rooms on the Ubuntu homeserver that have the Moderator bot invited and properly configured.

## You are a room admin and lost access to your account

Access to the Ubuntu Matrix homeserver happens via Single Sign On and is tied to Launchpad groups.
If you cannot login, make sure you recover access to your Launchpad account.
This can be done by accessing the [Launchpad help webpage](https://help.launchpad.net/YourAccount).


## The administrators of your room are no longer active

If you are a room user or moderator, and your room administrator has been inactive for a long period of time:

**Attempt to reach the room administrator**
: * [Log into Launchpad](https://launchpad.net).
: * In the search bar on the top of the main Launchpad page, type the nickname of the user you are looking for. Launchpad ID is the same as Matrix ID, so if a Matrix user is `@myuser:ubuntu.com`, the Launchpad ID is `myuser`.
: * Check if the user has a separate contact method, and reach out.
: * Note the dates and contacts in case you need to move to the next stage.

**Reach out to the Matrix Council and ask for help**
: If the room administrator is still not reachable on any alternative platforms after 30 days, or if the room admin has no alternative contacts:
: * Provide the dates when you tried to make contact.
: * Save the matrix ID and Launchpad ID of the administrator you are trying to reach.
: * Draft a message to the Ubuntu Matrix Council with your issue and desired outcome.
: * Send it to the {ref}`Ubuntu Matrix Council <contact-matrix-council>`.


## Other cases

If you have a specific case, and you need help:
* For general advice, reach out to the {matrix}`Ubuntu Matrix Ops room <matrix-ops>`.
* If you need to escalate an issue, contact the {ref}`Ubuntu Matrix Council <contact-matrix-council>`.


## Further reading

* {ref}`matrix-room-moderation`
* {ref}`matrix-moderation-and-defense`
* {ref}`matrix-moderator-bot`
* {ref}`matrix-management`

