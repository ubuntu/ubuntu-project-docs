(matrix-rooms-spaces-process)=
# Official rooms and spaces process

Users on the Ubuntu Matrix homeserver should be free to create rooms and spaces as they see fit.
This encourages interaction and keeps operations fast and smooth.
Having said that, we also want to make sure that all the official rooms and their owners follow our guidelines and are aware of rules, expectations, and processes.
For a user to promote a room or space to official, they need to contact the Matrix Ops team and ask to have it published in the server directory and listed under the Ubuntu Community space.

Users on the Ubuntu Matrix homeserver do not have permissions to publish their spaces or rooms in the server room directory.
They also do not have permissions to list their spaces or rooms under the main Ubuntu Community space.

This document describes a complete list of tasks that need to happen when new room or space owner reaches out to Matrix Ops asking to make their room or space official.


## Space/room owner contacts moderators

Users create spaces or rooms, then they contact the moderators in {matrix}`matrix-ops` as described in {ref}`matrix-rooms-spaces`.


## Awareness

Moderators in the {matrix}`matrix-ops` room, share documentation that every space/room owner should read.
The documents describe their responsibilities and requirements for an official Ubuntu room.


## Invite moderator bot

Room owners will invite the moderator bot, `@moderator:ubuntu.com` to their rooms, and assign admin privileges to the bot.
This is required so that the moderator bot can perform automated actions or other operations when invoked by moderators.
The room owner will inform the moderators when the actions are completed.

Moderators will then enable protection on the rooms, by sending these moderator bot commands in {matrix}`the management room <management>`:

* Check moderator bot status: `!mjolnir status`

* Check rooms protected by the moderator bot: `!mjolnir rooms`

* Add the room to the protected rooms list: `!mjolnir rooms add <insertyourroomname>`

* Check moderator bot status one more time to make sure everything looks good: `!mjolnir status`


## Ubuntu Code of Conduct banner

The moderator will ensure the room owner added a link to the Ubuntu Code of Conduct to the room description: 

```none
Please follow the CoC: https://ubuntu.com/community/ethos/code-of-conduct
```


## Room mod and room admin

The moderator will make sure that the room owner is aware of the following:

* Each room should have two admins.
  This helps with redundancy, as there are some actions only admins can take.

* Admin status cannot be removed by another admin, as they are on the same power level.
  Do not grant admin status lightly. Mod is enough for most needs.

* The room owner should identify suitable mods that can help protect the room from spam, abuse, and other unwanted behavior.
 
* Room owners are encouraged to keep an eye on great mods and refer them to the Matrix Council as server moderators.


## List and publish spaces/rooms

The moderator will list the spaces and/or rooms in the server directory by enabling the flag in the room configuration -> general settings. 

```none
Publish this room to the public in ubuntu.com's room directory?
```

The moderator will list the space/room in the main {matrix}`Ubuntu Community space <community>`.

