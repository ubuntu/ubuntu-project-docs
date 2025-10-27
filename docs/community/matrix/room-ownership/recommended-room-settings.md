(matrix-recommended-room-settings)=
# Recommended room settings

This article outlines a list of recommended settings for various room types.
If you are looking for specific guides on how to create or configure rooms, check the reference documentation at the bottom of this article.


## General advice on admin roles and power levels

Promoting someone to admin level gives them the highest power level.
They will have full permissions on the room.
It will not be possible to demote them or even remove them from a room in case the room needs to be closed or migrated. 
It is generally advisable to select custom power levels and change room permissions to match.
Reach out on the {matrix}`matrix-ops` room if you require assistance.


## Public rooms

### General settings

* Published addresses should have an address on the Ubuntu homeserver, all lower case, separated by hyphens/dashes if needed, e.g. `#matrix-ops:ubuntu.com`.
* "Publish this room to the public in ubuntu.com's room directory" should be turned on, as outlined in {ref}`matrix-rooms-spaces`.


### Security and privacy

* Encryption: Disabled
* Access: Public
* Who can read history: Anyone


## Private rooms

### General settings

* Published addresses should have an address on the Ubuntu homeserver, all lower case, separated by hyphens/dashes if needed, e.g. `#matrix-ops:ubuntu.com`.
* "Publish this room to the public in ubuntu.com's room directory" should be turned off.


### Security and privacy

* Encryption: Disabled
* Access: Private
* Who can read history: Members only (since the point in time of selecting this option)


## News and announcement rooms

### General settings

* Published addresses should have an address on the Ubuntu homeserver, all lower case, separated by hyphens/dashes if needed, e.g. `#matrix-ops:ubuntu.com`.
* "Publish this room to the public in ubuntu.com's room directory" should be turned on, as outlined in {ref}`matrix-rooms-spaces`.


### Security and privacy

* Encryption: Disabled
* Access: Public
* Who can read history: Anyone


### Roles and permissions

* Send Messages: Custom (10)


## Further reading

* {ref}`matrix-room-creation-public`
* {ref}`matrix-room-creation-private`
* {ref}`matrix-space-creation-public`
* {ref}`matrix-space-creation-private`
* {ref}`matrix-room-configuration-announcements`
* {ref}`matrix-rooms-spaces`

