(matrix-changing-addresses)=
# Change the main address of a room or space

In this guide, we will change the main address of a room or space to `ubuntu.com`.

A room or space may have any number of addresses and the main address can be published to the public directory of the homeserver it belongs to for discovery.
Changing and publishing the main address requires changes to be made by a user belonging to the homeserver of that address with power level 50 (moderator) or above.


## Quick Guide

After inviting a user from the `ubuntu.com` homeserver and giving them power level 50+ (moderator), they'll create a local address in settings, set it as the main address and turn on publishing to the homeserver's public directory.

After that, their privileges can be removed and they don't need to remain (see: {ref}`Caveats <matrix-change-address-caveats>`).


## Step-by-step guide


### As the room/space admin

1. Invite a trusted Ubuntu user from the `ubuntu.com` homeserver to your room or space.

1. Set the Ubuntu user's power level to 50 (Moderator) or above.


### As an Ubuntu user

1. Enter the room or space.

1. Open settings:

   Rooms
   : Right-click on the room's icon on the left bar and click {guilabel}`Settings`.

   Spaces
   : Click on the name of the space at the top of the left bar just below the {guilabel}`Search` field.
   : Click {guilabel}`Settings`.
   : Click {guilabel}`Visibility`.

1. Scroll down until you see the title {guilabel}`Published Addresses` and note the address in the {guilabel}`Main address` drop-down.
   If there's no address, ask the admin what they'd like the address to be.

1. Scroll down until you see the title {guilabel}`Local Addresses` and click {guilabel}`Show more` if applicable.

1. In the address input field, enter the {guilabel}`Main address` you noted above without the leading `#` or trailing `:ubuntu.com`.
   E.g. an address of `#my-room:matrix.org` would be entered as `my-room`.

1. Click the {guilabel}`Add` button.

1. Scroll up until you see the title {guilabel}`Published Addresses`, click the {guilabel}`Main address` drop-down and select the new address you added.
   You may need to refresh your browser if it's not visible.

   ```{note}
   It's important not to delete the local address that's been selected as the main address because it's a pointer to that address, not a copy.
   ```

1. Toggle the slider next to "Publish this room to the public in ubuntu.com's room directory?" to "On".
   You may need to refresh your browser to set it.


### As the room/space admin

Privileges can now be removed from the invited Ubuntu user and they don't need to remain in the room or space (see: {ref}`Caveats <matrix-change-address-caveats>`).


(matrix-change-address-caveats)=
## Caveats

* A room or space must have at least one Ubuntu user as a member for it to be visible on the public directory of the `ubuntu.com` homeserver.

* In {guilabel}`Settings` for rooms, or {guilabel}`Setting > Visibility` for spaces, only an Ubuntu user can see (or toggle with power level 50+) the setting for publishing to `ubuntu.com`'s public directory.
  For everyone else it will appear off.

* Members of any power level can add local addresses or delete the local addresses they've created even if they're in use as the main address.
  Care should be taken when relying on addresses that were not created by trusted users though these addresses are easy to replace.

