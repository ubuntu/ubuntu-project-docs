(matrix-mjolnir-commands)=
# Mjolnir commands


Mjolnir listens for commands in {matrix}`the management room <management>`.
This room is private and only server moderators are granted access to it.


## Print a list of commands

A comprehensive list of Mjolnir commands can be printed using the command below in {matrix}`the management room <management>`.

```none
!mjolnir help
```


## To enable Mjolnir protection in rooms

This process is well described in {ref}`matrix-rooms-spaces-process`.



## Moderation commands

### Redacting user messages

Redacting messages does not kick or ban a particular user, so they could continue their activity.
In certain cases of spam waves, it might be beneficial to kick and ban as well as redacting.


Redact last 100 messages in a specific room
: Command syntax:
: ```none
: !mjolnir redact <user ID> [room alias/ID] [limit] 
: ```

: Example:
: ```
: !mjolnir redact @user:ubuntu.com #room:ubuntu.com 100
: ```

Redact last 100 messages globally
: Command syntax:
: ```none
: !mjolnir redact <user ID> [limit] 
: ```

: Example:
: ```none
: !mjolnir redact @user:ubuntu.com 100
: ```


### Mute a user

Mute or silence a user by setting their "power level" negative:

```none
!mjolnir powerlevel @user:matrix.org -1 #room:ubuntu.com
```


### Kick a user

Kicking removes a user from a room temporarily.
This is not a permanent ban from the room.


Kick using moderation reports
: With moderation reports, you can click on the "kick" button below a report. Mjolnir will take action and kick the user according to the details in the report.


Manually kick user from specific room
: Command syntax:
: ```none
: !mjolnir kick <glob> [room alias/ID] [reason]
: ```

: Example:
: ```none
: !mjolnir kick @user:ubuntu.com #room:ubuntu.com [spam]
: ```


Manually kick a user from all protected rooms
: Command syntax:
: ```none
: !mjolnir kick <glob> [reason]
: ```

: Example:
: ```none
: !mjolnir kick @user:ubuntu.com spam
: ```


### Ban users

A ban removes a user from a homeserver inefinitely.
This is not a permanent ban from the room.
This action is useful in case of repeat offenders or obvious bot spam action.


Ban using moderation reports
: With moderation reports, you can click on the "ban" button below a report. Mjolnir will take action and ban the user according to the details in the report.


Manually ban user for Code of Conduct violations
: Command syntax:
: ```none
: !mjolnir ban <list shortcode> <user|room|server> <glob> [reason]
: ```

: Example:
: ```none
: !mjolnir ban coc user @user:ubuntu.com inappropriate and aggressive behavior
: ```


Manually ban user for spam
: Command syntax:
: ```none
: !mjolnir ban <list shortcode> <user|room|server> <glob> [reason]
: ```

: Example:
: ```none
: !mjolnir ban spam user @user:ubuntu.com spamming inappropriate messages
: ```


### Ban servers

A server ban prevents users from an entire server to join the ubuntu.com homeserver.
This is particularly useful to block spam waves, when hundreds of users are created on the same homeserver. 

Command syntax:

```none
!mjolnir ban <list shortcode> <user|room|server> <glob> [reason]
```

As you probably guessed, you are not going to ban a user this time, but a server. For example, to ban the `maliciousdomain.tld` domain:

```none
!mjolnir ban spam server maliciousdomain.tld
```


## Full list of commands

```none
!mjolnir                                                            - Print status information
!mjolnir status                                                     - Print status information
!mjolnir status protection <protection> [subcommand]                - Print status information for a protection
!mjolnir ban <list shortcode> <user|room|server> <glob> [reason]    - Adds an entity to the ban list
!mjolnir unban <list shortcode> <user|room|server> <glob> [apply]   - Removes an entity from the ban list 0 - if apply is 'true', the users matching the glob will actually be unbanned
!mjolnir redact <user ID> [room alias/ID] [limit]                   - Redacts messages by the sender in the target room (or all rooms), up to a maximum number of events in the backlog (default 1000)
!mjolnir redact <event permalink>                                   - Redacts a message by permalink
!mjolnir kick <glob> [room alias/ID] [reason]                       - Kicks a user or all of those matching a glob in a particular room or all protected rooms
!mjolnir rules                                                      - Lists the rules currently in use by Mjolnir
!mjolnir rules matching <user|room|server>                          - Lists the rules in use that will match this entity e.g. `!rules matching @foo:example.com` will show all the user and server rules, including globs, that match this user
!mjolnir sync                                                       - Force updates of all lists and re-apply rules
!mjolnir verify                                                     - Ensures Mjolnir can moderate all your rooms
!mjolnir list create <shortcode> <alias localpart>                  - Creates a new ban list with the given shortcode and alias
!mjolnir watch <room alias/ID>                                      - Watches a ban list
!mjolnir unwatch <room alias/ID>                                    - Unwatches a ban list
!mjolnir import <room alias/ID> <list shortcode>                    - Imports bans and ACLs into the given list
!mjolnir default <shortcode>                                        - Sets the default list for commands
!mjolnir deactivate <user ID>                                       - Deactivates a user ID
!mjolnir protections                                                - List all available protections
!mjolnir enable <protection>                                        - Enables a particular protection
!mjolnir disable <protection>                                       - Disables a particular protection
!mjolnir config set <protection>.<setting> [value]                  - Change a protection setting
!mjolnir config add <protection>.<setting> [value]                  - Add a value to a list protection setting
!mjolnir config remove <protection>.<setting> [value]               - Remove a value from a list protection setting
!mjolnir config get [protection]                                    - List protection settings
!mjolnir rooms                                                      - Lists all the protected rooms
!mjolnir rooms add <room alias/ID>                                  - Adds a protected room (may cause high server load)
!mjolnir rooms remove <room alias/ID>                               - Removes a protected room
!mjolnir rooms setup <room alias/ID> reporting                      - Setup decentralized reporting in a room
!mjolnir move <room alias> <room alias/ID>                          - Moves a <room alias> to a new <room ID>
!mjolnir directory add <room alias/ID>                              - Publishes a room in the server's room directory
!mjolnir directory remove <room alias/ID>                           - Removes a room from the server's room directory
!mjolnir alias add <room alias> <target room alias/ID>              - Adds <room alias> to <target room>
!mjolnir alias remove <room alias>                                  - Deletes the room alias from whatever room it is attached to
!mjolnir resolve <room alias>                                       - Resolves a room alias to a room ID
!mjolnir since <date>/<duration> <action> <limit> [rooms...] [reason] - Apply an action ('kick', 'ban', 'mute', 'unmute' or 'show') to all users who joined a room since <date>/<duration> (up to <limit> users)
!mjolnir shutdown room <room alias/ID> [message]                    - Uses the bot's account to shut down a room, preventing access to the room on this server
!mjolnir powerlevel <user ID> <power level> [room alias/ID]         - Sets the power level of the user in the specified room (or all protected rooms)
!mjolnir make admin <room alias> [user alias/ID]                    - Make the specified user or the bot itself admin of the room
!mjolnir help                                                       - This menu
```


# Further reading

* [Matrix documentation: moderating communities](https://matrix.org/docs/communities/moderation/)
* [Moderator's guide to Mjolnir (Bot edition)](https://github.com/matrix-org/mjolnir/blob/main/docs/moderators.md)

