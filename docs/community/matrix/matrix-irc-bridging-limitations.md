(matrix-irc-bridging-limitations)=
# Matrix-to-IRC bridging limitations

This document outlines what to expect when Ubuntu starts bridging existing IRC channels to Matrix rooms.


## Bridging events from IRC to Matrix

There are no limitations bridging messages from IRC to Matrix.
All features are supported and translated to Matrix events.


## Unavailable or limited Matrix to IRC events

**Redaction**
: Redacting messages on Matrix has no effect on the IRC side. The message just stays as written.

**HTML/Markdown**
: Some Markdown language is supported. For example you can use **bold text**. If a Markdown feature is not supported (like code blocks) the message is usually transmitted as plain text.

**Media sharing**
: Matrix supports sharing images, videos, and files directly in chats. IRC does not inherently support media sharing. Files must be shared via URLs. Any direct media shared on Matrix will typically be converted to a URL when viewed on IRC.

**Reply threads**
: Matrix supports threaded conversations, allowing users to reply to specific messages creating a thread. IRC does not support threads in the same way, so threaded messages from Matrix will appear as standard messages on IRC, potentially losing context.

**Reactions and emojis**
: While both Matrix and IRC support the use of emojis in messages, Matrix also supports message reactions (emoji reactions to messages). These reactions do not have a direct equivalent in IRC and will not be visible.

**Read receipts and typing notifications**
: Matrix provides read receipts and typing notifications to indicate when users are typing a message or have read a message. IRC does not support these features, so they are not available when bridging from Matrix to IRC.

**End-to-end encryption**
: Matrix supports end-to-end encryption in rooms. IRC does not support end-to-end encryption natively; thus, encrypted messages cannot be bridged to IRC without losing encryption.

**Room features**
: Features like room topics are supported by both protocols but may not always sync perfectly across the bridge. Changes made on the Matrix side may not be reflected on IRC or may be subject to limitations based on the IRC network's capabilities. Room avatars on Matrix are not visible on IRC.

**Nicknames and user IDs**
: Matrix allows for more flexibility in usernames and displays, including spaces and special characters. IRC has stricter rules for nicknames (limited character set and length), which might result in automatic adjustments or truncation when bridging.

**Kick/ban synchronization**
: While basic kick and ban actions can be synchronized between Matrix and IRC, the granularity of reasons, temporary bans, and more complex moderation actions may not translate perfectly across the bridge. In general, moderation must be done on both sides.

**Channel modes and permissions**
: IRC has a specific set of channel modes and user permissions that do not have a direct equivalent in Matrix. Bridging these settings can be challenging and may result in a loss of functionality or mismatched permissions. The map below shows the conversion of IRC user modes to Matrix power levels. This enables bridging of IRC Ops to Matrix power levels only -- it does not enable the reverse. If a user has been given multiple modes, the one that maps to the highest power level will be used.

| IRC mode | Matrix permission level |
| -------- | ----------------------- |
| None     | 0                       |
| Voice    | 1                       |
| Operator | 50 (Moderator)          |

