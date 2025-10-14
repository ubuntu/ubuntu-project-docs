(matrix-room-configuration-announcements)=
# How to configure a room for announcements

You might want to have dedicated rooms in your space dedicated to announcements, news, feeds, or a mix of the three.
There are many bots that pull information from other platforms, such as social media, news sites, Launchpad, GitHub, GitLab, and many more.
However, a room admin usually wants to focus discussions in specific channels:

* To avoid chatter mixed with news and important announcements making everything hard to find
* To keep important announcements visible to your community for a longer period of time


## Configure your room

1. First, {ref}`create a public <matrix-room-creation-public>` or {ref}`a private room <matrix-room-creation-private>`

1. Select a suitable name and topic for your room, so the community knows what to expect

1. Right click on the room name, and select {guilabel]`Settings`

1. Select the {guilabel]`Roles & Permissions` menu

1. In the {guilabel]`Permissions` section, open the {guilabel]`Send Messages` drop-down menu

1. Change the setting from {guilabel]`Default` to {guilabel]`Custom level`, and type 10

1. Close the {guilabel]`Settings` menu


## Configure user power level

Users or bots need at least power level 10 to post messages in this room.
This gives room administrators good flexibility to let users or bots post messages, without having to promote them to mods or admins.

1. Right click on the room name, and select {guilabel]`People`

1. Select the user or bot you want to allow to send messages in this room

1. Check their power level; if it is {guilabel]`Default` and you do not want to grant mod or admin status, click the {guilabel]`Power level` drop-down menu and select {guilabel]`Custom level`

1. Enter 10 in the {guilabel]`Power level` drop-down


## Further reading

* {ref}`matrix-concepts`
* {ref}`matrix-moderation-and-defense`
* {ref}`matrix-governance`

