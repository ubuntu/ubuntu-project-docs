(matrix-defenders)=
# Matrix defenders

As described in {ref}`matrix-moderation-and-defense`, defenders help the Ubuntu community by fighting spam and other obvious forms of abuse within Matrix.
They have the ability to help every official room that is hosted on the Ubuntu homeserver, and has the Moderator bot properly configured.
A defender is not a moderator, and will never get involved in moderation decisions beyond the cases described above.


## How to become a defender

Defenders have very high privileges in the Matrix homeserver, and their actions have important consequences.
Because of that, they are selected by the Matrix Council. 
More information on how to become a defender can be found in {ref}`how-to-become-a-defender`.


## Configure your Element client

In order to receive urgent requests of help, defenders need to set up a special filter in their Element client.
This will trigger room notifications in red, as if someone sent a private message.

1. Open the Element client
1. Hover over your user avatar, at the top left of the Element client
1. Select {guilabel}`All Settings`
1. Select the {guilabel}`Notifications` menu
1. In the {guilabel}`Mentions & keywords` section, make sure that the {guilabel}`Messages containing keywords` is set to "On".
1. In the text field marked with "Keyword" in the {guilabel}`Mentions & keywords` section, type `!defenders`
1. Click on the {guilabel}`Add` icon to add the keyword
1. Confirm you can see the keyword `!defenders` below the text field marked with "Keyword".


## How to contact a defender

Defenders can be contacted in the {matrix}`Matrix Ops <matrix-ops>` Matrix room.
To draw defenders attention you can add `!defenders` in your message.


## Further reading

If you want to become a defender, or you are already one, refer to the documentation below for general direction and help:

* {ref}`matrix-moderation-and-defense`
* {ref}`matrix-governance`
* [ref}`matrix-moderator-bot`
* {ref}`matrix-mjolnir-commands`

