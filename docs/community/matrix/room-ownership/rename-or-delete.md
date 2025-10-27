(matrix-rename-or-delete)=
# Rename or delete a Matrix room

If you are thinking about deleting and re-creating a room, in most cases you can adjust settings in a way that you'll get the same end result without recreating the room.


## How to rename a room

Renaming a room will not actually require users to do anything.
The room addresses are simply labels that are applied to the physical room.

1. Go to {guilabel}`Settings` -- if the room is published, un-publish it from the room directory.

1. In the {guilabel}`Local Addresses` section, add the new local alias and mark it as "primary".
   Then you can remove all aliases that you'd like to get rid of.

   ```{note}
   This is a per-homeserver setting, so if you have an `:ubuntu.com` account, you can only add/remove `:ubuntu.com` aliases.
   If you'd like to add/remove an alias on a different homeserver like `matrix.org`, get a room admin with an account on that server to do it.
   ```

1. If you've changed the main address, promote the new main address for the room.

1. If the room was previously published, you can publish it again.
   Note that if you change the homeserver suffix in the main address, it will be published to that homeserver instead.


## How to delete a room

1. Go to {guilabel}`Settings`

1. Un-publish the room from the room directory.
   An admin with an account on the homeserver of the main room address needs to do this.

1. Remove all local aliases for the room, across all homeservers

1. In {guilabel}`Room settings` -> {guilabel}`Security & Privacy` -> {guilabel}`Access`, select {guilabel}`Private (invite only)`

1. Kick everyone out that you can.
   You can't kick out people at the same permissions level as you; these folks will have to leave or demote themselves.

1. Take a final look to see if everything is clean and close the door behind you.


### How to redirect people to another room

1. The simple version is to invite them to the new room and then shut down the old room using the steps above.

1. The hard version involves sending a so-called "tombstone event".
   This requires a command-line client or using CURL requests with your token.
   While this event is usually meant for room upgrades, it can also be used to determine a new room where the conversation continues.
   There are guides on how to do this on the internet.
   Be careful, you don't want to lose everyone in the room!

