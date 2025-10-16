(matrix-room-properties)=
# Room properties

**Room name**
: * Your room name should stand for itself and accurately describe its purpose.
: * It can use more than one word and does not need to be lowercase-in-one-word-with-dashes like on IRC, however keep it concise so people will understand at a glance.

**Room topic**
: * This is the topic at the top of the room, what people need to know who just arrived or are a part of the room.
: * While (currently) Markdown is not supported, you can use links which will automatically link in Element's clients and others.
: * Start with a short sentence on what is to be discussed, then link off to a page that describes your effort in more detail.

**Room addresses**
: * Matrix rooms don't *only* exist on the server you are on; thanks to federation, they are synchronized between all servers of everyone participating. So there is no concept of "A room on the :ubuntu.com server" aside from the fact that it might have been created there.
: * Each room has a "main address" where it is considered home. Additionally, rooms can have an alias on any number of other servers. Adding an alias needs to be done by an admin to your room with an account on the respective other server.
: * As a matter of convention, please use all lowercase for the room aliases. If you are organizing your rooms as part of a space, stay consistent. For example, in the Charmhub Space, the Identity team might have its own space, and there are a set of rooms including a general room. You'd have #charmhub-identity-general:ubuntu.com as your alias.
: * Even if your room is part of a space, please remember that a room can be joined by people that have not joined the space it is listed in. Therefore, please make sure that room alias gives enough context to people that look it up or join:
:   * Bad example: #general-chatter:ubuntu.com
:   * Good example: #kubuntu-general-chatter:ubuntu.com
: * If you are moving a room, you don't need to re-create it. You can simply remove and add the aliases accordingly, and the room will continue to exist in its new location with everyone in it.


## Security and privacy

**General hints**
: * "Block anyone not part of ubuntu.com from ever joining this room", or disabling federation, should generally not be used. It may make sense for a very limited set of rooms, e.g. a room only for Ubuntu Members. Note for Canonical, this is not a way to restrict communications to just Canonical staff.
: * If you create a room encrypted or with federation blocked, you will not be able to change this if you decide differently later. You can however migrate people to the new room, but it requires an interaction from them. Keep this in mind especially when creating private rooms you think might become public soon.

**Public rooms**
: * Public rooms should not be encrypted, as this complicates the setup for a room that is open for anyone to join anyway.
: * For public rooms please keep the default history setting of "Members only (since the point in time of selecting this option)". For select public rooms we may expand this to "Anyone", but please discuss with moderators beforehand.

**Space members**
: * This setting mainly makes sense for private spaces, so that people who have been invited to the space can join any room in the space.
: * For public spaces, please don't use this option.

**Private rooms**
: * Use these for truly private conversations where you don't expect community members to join.
: * The history setting "Members only (since they were invited)" will allow you to give people context between when you invite them and when they join.

