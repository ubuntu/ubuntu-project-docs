(Nautilus-test-plan)=
# Nautilus test plan


## Start Files

* Start Nautilus (Files) from the launcher or desktop overview
  * the file manager view is opened and displays the content of the user directory


## Create and rename a folder

* In the current directory right click on a blank section and select 'New Folder'.
  * A dialog prompting for the folder name is displayed
* Enter a name for the folder and press {kbd}`enter` or click the confirmation button
  * A folder with the entered name appears in the directory
* Rename the folder to 'test'
  * The folders name is changed to 'test'


## Move files

* Create a file
* Drag and drop the file to a folder
  * check that the file correctly got moved to the folder
* Do the same by using the context menu 'move to' item


## Delete and restore

* Create a 'test' folder
* Right click on 'test' folder and select Move to Trash
  * test folder is removed. Trash folder icon is changed to Not empty
* Click the Trash Icon in the sidebar
  * the Trash show the 'test' folder
* Right click on the 'test' item and select 'Restore from the Trash'
  * the directory should be back to the original location


## Search

* Click the Search Icon in the top
* Input 'test'
  * the 'test' folder is listed


## Recent files

* Double click in the 'test' folder
* Create a text file there and open it with the Text Editor
* Close the Editor
* Click the Recent Icon in the sidebar
  * the file should be listed
* Right click on the file and select 'Remove from Recent'
  * the item shouldn't be listed in the recent view anymore


## Template

```none
$ echo "A text template" > ~/Templates/Txt
```

(replace 'Templates' by the directory set for `XDG_TEMPLATES_DIR` in `XDG_TEMPLATES_DIR` if needed)

* In `nautilus` right click on a blank section and select New Document, then 'Txt' in the dialog and confirm
  * A document named 'Txt' with the content 'A text template' should be created in the current directory


## Remote servers

If you have access to samba shares on your local network click on 'Other locations' in the sidebar and browse to them

Try to connect to a ssh server you have access to by doing {kbd}`ctrl` + {kbd}`L` and typing `ssh://<name_or_ip>`


## External devices

* Connect an external storage device to the computer (USB stick, phone in file sharing mode, ...)
  * check that it's listed in the sidebar
* Click on the corresponding item
  * check that you can browse the drive, open or copy files


## Email

Try to left click on a file and pick the 'email...' option. A composer dialog from the email client configured as default for the user should be triggered with the file attached.

Note that the feature only works with `thunderbird` if the '`nautilus-sendto`' package is installed.

Without `nautilus-sendto` `thunderbird` would get no file attached to the composer but the feature should still work with `evolution` or `geary`.


## File chooser dialog (Ubuntu 26.04 and newer)

If testing on Ubuntu Desktop 26.04, Nautilus is used to implement the `xdg-desktop-portal` file chooser.

Launch Firefox, and navigate to <https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/file#try_it>

* Click "Browse..."
  * Verify that the file chooser dialog has appeared.
* Select any file
  * Verify that the filename is correctly shown next to the "Browse..." button you clicked earlier.
