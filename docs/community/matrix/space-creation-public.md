(matrix-space-creation-public)=
# Create and configure a public space


This short guide walks you through the creation and basic configuration of a public space on the Ubuntu Matrix homeserver.
This guide assumes you are using the Element desktop client.

```{note}
A Matrix Space is technically a type of room.
Reference to rooms in this guide are intentional, to stay aligned with the Element client interface.
```


## Create a public space

1. Click on the {guilabel}`+` icon on the left panel, below your user avatar.

1. Select {guilabel}`Public`.

1. In the {guilabel}`Name` field, type the display name of the space.
   This name can contain upper and lower case characters, spaces, and can be changed later.

1. In the {guilabel}`Address` field, type a space address.
   This should be all lower case.
   Parts of the name can be separated by using dash characters.

1. In the {guilabel}`Description` field, you can add a description of this space.
   This field is optional and can be filled later.

1. Make sure the address is available, then click {guilabel}`Create`.

1. In the next screen, you can create rooms within your space.
   Click {guilabel}`continue` when ready.


## Space configuration

### General settings

1. After your space is created, click on the space name drop-down on the left side of your Element desktop client, under the search bar, and select {guilabel}`Settings`.

1. In the {guilabel}`General` settings, you can change "Name", "Description", and upload an image.

1. Once all changes are confirmed, select {guilabel}`Save changes`.


### Visibility

In the {guilabel}`Visibility` settings, you can:

* Change your space from Public to Private, or Space members.

* Enable or disable space preview.
  Keeping this option enabled is recommended for public spaces.

* Add, remove, or modify local and published addresses.

* If you cannot enable the {guilabel}`Publish this room to the public in the ubuntu.com's room directory?` toggle, please note this is intended behavior.
  Check the steps in the {ref}`public-space-publishing` section to complete this task.


(public-space-publishing)=
## Room publishing and listing under spaces

Please check {ref}`matrix-rooms-spaces) if you'd like to:

* Protect your space and rooms from abuse.
* Publish your space in the server directory.
* Add your space to the Ubuntu Community space.


## Further reading

Congratulations! Your public space is now ready!
If you would like to learn more about the Ubuntu Matrix homeserver, check {ref}`our documentation <matrix-index>`.


