(matrix-defenders)=
# Matrix Defenders


Defenders help the Ubuntu community by fighting spam and other obvious forms of abuse within Matrix.
They are global moderators who help combat spam waves and obvious trolls across every official room of our homeserver.
This group has access to the Moderation bot in order to fulfill their duties.

You can find the authoritative list of current Defenders in the [`matrix-defenders`](https://launchpad.net/~matrix-defenders) team on Launchpad.

A Defender is not a Moderator, and will never get involved in moderation decisions beyond the cases described above.


## Expectations

* Handling abusers of the service in a dispassionate and professional way
* Deferring all situations that aren't certain
* Being a high-trust individual for the level of privileges being granted


### Scope

* Defenders may only act on newly interacting accounts on the Ubuntu Homeserver (by rough estimate of the Defender)
* If any situation is uncertain it should be passed to the room Moderators ({ref}`how-to-find-a-moderator`)
* Interpretation of events by a room owner or Moderator always take priority over a Defender


### Examples of abuse

* Spamming
* Advertisement
* Extremely disruptive behavior


## How to contact a Defender

Defenders can be contacted in the {matrix}`Matrix Ops <matrix-ops>` room.
To draw Defenders' attention you can add `!defenders` in your message.


(how-to-become-a-defender)=
## How to become a Defender

Defenders have very high privileges in the Matrix homeserver, and their actions have important consequences.
Because of that, they are hand-selected and appointed directly by the Matrix Council. 

Room owners can make recommendations to the Matrix Council, but only Ubuntu Members and Canonical employees are currently eligible.

When our tooling improves so that Defenders need fewer permissions, we can open the role up to more people.


## Defender client configuration

In order to receive urgent requests of help, Defenders need to set up a special filter in their Element client.
This will trigger room notifications in red, as if someone sent a private message.

1. Open the Element client

1. Hover over your user avatar, at the top left of the Element client

1. Select {guilabel}`All Settings`

1. Select the {guilabel}`Notifications` menu

1. In the {guilabel}`Mentions & keywords` section, make sure that the {guilabel}`Messages containing keywords` is set to "On".

1. In the text field marked with "Keyword" in the {guilabel}`Mentions & keywords` section, type `!defenders`

1. Click on the {guilabel}`Add` icon to add the keyword

1. Confirm you can see the keyword `!defenders` below the text field marked with "Keyword".


## Further reading

If you want to become a Defender, or you are already one, refer to the documentation below for general direction and help:

* {ref}`matrix-moderation-and-defense`
* {ref}`matrix-moderator-bot`
* {ref}`matrix-mjolnir-commands`

