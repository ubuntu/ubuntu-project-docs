(FileRoller-test-plan)=
# File Roller test plan


## Start File Roller

1. Start File Roller from the launcher or desktop overview

   The program is opened and reports that no archive is open.


## Create an archive

1. Use {kbd}`Ctrl` + {kbd}`n` or navigate the main menu to "New Archive". Type a name with an archive extension, e.g. `u.tar`.

2. Use the + button to add some stuff to it.

   `tar tf u.tar` lists the files that were added in the previous step.


## Inspect an archive

1. `wget https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/file-roller/44.3-1/file-roller_44.3.orig.tar.xz`.

2. `file-roller file-roller_44.3.orig.tar.xz`.

   File Roller opens and you after entering `file-roller-44.3` you see its source tree.

   {kbd}`Alt` + {kbd}`Return` or 'main menu -> Properties' identifies the archive as an application/x-xz-compressed-tar.


## Extract an archive

1. Click the 'extract' button on the upper left corner.

2. Choose '`/tmp`' as the target location.

   Dialog says that extraction completed successfully.

3. Click show the files.

   Your file manager opens and displays the `/tmp` directory. The `file-roller-44.3` directory is inside.


## Alter an archive's contents

1. Select any file, right-click it and rename.

   `tar tf file-roller_44.3.orig.tar.xz` reflects the rename.
