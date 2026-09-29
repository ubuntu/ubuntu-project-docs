(GnomeTextEditor-test-plan)=
# GNOME Text Editor test plan

Since `gnome-text-editor` doesn't include autopkgtests we will follow a manual testplan to verify updates.
MIR reference {lpbug}`1971973`


## Open and edit some files

* Try opening different file formats (txt, C, python, makefile, yaml, ...) from `nautilus` (select in open with if that's not configured as your default editor)

* Check that the editor opens the files as expected and that the corresponding syntax mode is selected (coloring should be right, the document type is displayed in the cog menu on the right of the headbar)

* Edit, save the change and reopen the file to ensure the changes were properly saved


## Open a file from a remote share

* Browse a remote location in `nautilus` (ssh, ftp, smb)

* Open a file from there with `gnome-text-editor`

* Do some change and save them


## Verify that the standard options work as expected

* Use to cog, toggle the lines number display, verify they are correctly displayed or not

* Use to cog, toggle the margin display, verify it's correctly displayed or not

* Use to cog, toggle the spell checking. Typo a word in the document and verify that it's underlined and a correct spelling is suggested on right click

* Browse the preferences and toggle the different options, verify they reflect directly on the UI

* Review the keybindings help dialog and verify those are working, most common actions betng

* Use {kbd}`ctrl` + {kbd}`F` to search in the document, including case sensitive and regexp

* Use {kbd}`ctrl` + {kbd}`H` to replace a string

* Use {kbd}`ctrl` + {kbd}`P` and print the document to a pdf, verify that `evince` is able to load it

* Use {kbd}`ctrl` + {kbd}`O` and open a file

* Use {kbd}`ctrl` + {kbd}`S` to save changes

* Use {kbd}`ctrl` + {kbd}`Z` to undo changes
