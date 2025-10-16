(matrix-spam)=
# Dealing with spam

Matrix occasionally has spam waves.
Sometimes, spammers target specific communities like the Ubuntu community.
While the Ubuntu Matrix Operators work hard to block the spam before you even see it, they cannot (yet) catch everything.
However, there are a few things you can do yourself to protect yourself.


## Don't engage

The most important rule is to **never engage directly with the spammers**!
Spammers are trying to get your attention.
They want you to get upset and want you to respond to them.
Ignoring them is the best response.


## Disable image previews

Many Matrix clients like Element allow you to disable image previews.
Since some spammers send disturbing images, it's best to turn image previews off.
This way, you won't see these images before our moderator bot removes them.

To turn image previews off in Element Desktop, select your profile picture in the top left corner of the app, click {guilabel}`All Settings` -> {guilabel}`Preferences`, and turn the following settings off:

* {guilabel}`Autoplay GIFs`

* {guilabel}`Autoplay videos`

* {guilabel}`Show previews/thumbnails for images`


## Block invites from banned users

Sometimes, spam comes in the form of rogue invites to problematic rooms.
By default, banned users can still send you invites, but Element has an experimental feature that allows you to block invites of everyone we ban.

1. In Element Desktop, select your profile picture in the top left corner of the app, click {guilabel}`All Settings` -> {guilabel}`Labs`, and turn on {guilabel}`New ways to ignore people`.
1. Then, go to {guilabel}`Ignored users` to the section {guilabel}`Subscribed lists` and add `!fTjMjIzNKEsFlUIiru:neko.dev`.
   This is a community maintained list of spammers.


## Ignore invites and users

To avoid spam from rogue invites, you can also ignore the user.
By doing this, that user will not be able to send you another invite.
The method to ignore the user is different depending on which app you're using.

* On Element Desktop and Element Web, click on the invite (but don't accept it), and click **{guilabel}`Reject & Ignore user`**.
* If you're using Element Android, or another client, you need to type **`/ignore @user:example.com`** in the message box in a room and press {guilabel}`Send`.
  Make sure to change the username in this command to the user inviting you.

You can also ignore users that you are already in a room with you by clicking on the profile picture of the user and clicking {guilabel}`Ignore`.


## Contact the Ubuntu Matrix Operators

If you're targeted by spam, please let the Ubuntu Matrix Operators know in the {matrix}`Ubuntu Matrix Ops <matrix-ops>` room.
We're constantly trying to improve our tooling to block the spam before you even see it.
We're also working with other communities on Matrix to defend against spam together.
However, if something slips through the cracks, please let us know.

If you receive spam invites, it can help the Operators if you let us know (in the Matrix Ops room) what the full username and the room ID is of the spammers.
Certain Matrix clients such as {spellexception}`Neochat` allow you to get a room ID without entering it.
You can do that by right-clicking, choosing {guilabel}`Room Settings`, and copying the {guilabel}`Room ID`.


## Contact your homeserver admins

If you're using a `matrix.org` account, you can report spam invites by sending an email to `abuse@matrix.org`.

