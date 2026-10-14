(matrix-room-creation-private)=
# Create and configure a private room

This short guide walks you through the creation and basic configuration of a public room on the Ubuntu Matrix homeserver.
This guide assumes you are using the Element desktop client.

```{note}
Anyone with an `ubuntu.com` account can create private rooms on our homeserver.
```


## Create a private room

1. Click on the {guilabel}`All rooms` icon on the top left of your Element desktop client.
   This icon is represented by a house, and can be found below the user avatar.

1. Click on the {guilabel}`+` icon on the left of {guilabel}`Home` and below the compass icon used to search for rooms.
   Select {guilabel}`New Room`.
    
   ```{warning}
   It is important to ensure you are **on your home screen** when clicking on the {guilabel}`+` icon.
   Otherwise, it will try to create a room _inside_ the space you're currently in.
   This will fail in the Ubuntu space.
   If you want to add a room to one of our spaces, first create the room outside of the space, and then follow {ref}`matrix-rooms-spaces`.

1. In the {guilabel}`Name` field, type the display name of the room.
   This name can contain upper and lower case characters, spaces, and can be changed later.

1. The {guilabel}`Topic` field is for the description of your room.
   This field is optional and can be filled later.

1. In the dropdown, select {guilabel}`Private room (invite only)`.

1. The last but most important choice to make is about end-to-end encryption.
   
   ```{warning}
   The recommendation is to toggle encryption off *before* creating the room.
   Disabling encryption later on is not possible.
   Enabling encryption will cause issues with bots, bridges, and overall lower the quality of user experience of your room.
   ```

1. Double-check your settings, then click on {guilabel}`Create room`.


## Room configuration

### General settings

1. After your room is created, click on the room name dropdown on the top of your Element desktop client, and select {guilabel}`Settings`.

1. In the {guilabel}`General` settings, you can change "Room Name", "Room Topic", and add a "Room image".

1. In the {guilabel}`General` settings, you can also check your published addresses, and local addresses.
   If you cannot enable the {guilabel}`Publish this room to the public in the ubuntu.com's room directory?` toggle, please note this is intended behavior.
   Check steps in the {ref}`private-room-publishing` section to complete this task.


## Security and privacy settings

In the {guilabel}`Security & Privacy` settings, you can change your room from Private to Public, or space members.

```{warning}
Please **never enable encryption** for public rooms.
You cannot turn it back off, and it creates a lot of issues with public rooms.
```


(private-room-publishing)=
## Room publishing and listing under spaces

Please check {ref}`matrix-rooms-spaces` if you'd like to:

* Protect your room from abuse
* Publish your room in the server directory
* Add your room to the Ubuntu Community space


## Further reading

Congratulations! Your private room is now ready!
If you would like to learn more about the Ubuntu Matrix homeserver, check {ref}`our documentation <matrix-index>`.
