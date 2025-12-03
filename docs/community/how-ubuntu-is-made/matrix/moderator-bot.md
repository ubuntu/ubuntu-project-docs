(matrix-moderator-bot)=
# Moderator bot

This document explains what the moderator bot is, what it does, and why we need it.


## Who is the moderator I see in my room?

You may have noticed an account called "moderator", with the alias: `@moderator:ubuntu.com` in your room or space.
This is not a personal account, but a moderator bot we use to protect our Ubuntu Matrix homeserver from spam and abuse.
This is part of our process for {ref}`publicly listed rooms and spaces <matrix-rooms-spaces-process>`.


## What does the moderator bot do?

The moderator bot we currently used has several features:

* Being a room admin, it keeps a foothold in each of our rooms and spaces.
  No matter what happens to other admin users in the room or space, the moderator will always allow the Matrix Ops to regain control when needed.

* Moderator bot is subscribed to federated access lists (ACLs) from other servers we trust.
  So, if a person or spam-bot is banned from communities we follow, the same account is automatically banned from our Ubuntu Matrix homeserver.
  This blocks spam before it can even start. 

* Other Matrix homeservers can listen to our access list and gain the same advantages, so that accounts we ban are automatically banned on friendly homeservers as well.

* Room users can ask for help in the Matrix Ops room in case of a spam wave, and server-level bans can be performed by Matrix Ops team through the moderator bot.


## Why do we need to grant admin permissions to the moderator bot?

* It ensures that a malicious user trying to take over a room cannot kick out the bot.

* It ensures the Matrix Operators can always regain control of a room, even if all admins leave, lose their accounts, or are locked out of the platform.
  Due to how Matrix federation works, it might otherwise be impossible to regain control of a room, even as a server admin.
 
* It allows the bot to configure sensitive settings such as default power levels.


## Who will ask me for this permission?

All official communication about these permissions will come from either the {ref}`Matrix Council <matrix-council>` or one of the {ref}`Operators <matrix-operators>`.
