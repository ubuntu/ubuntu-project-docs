(GVFS-test-plan)=
# GVFS test plan

Verify that

`grep gvfs /proc/mounts`

lists a FUSE mount in `$XDG_RUNTIME_DIR` (typically `/run/user/...`).

In Nautilus address bar, type a remote server to which you have access.

```none
sftp://{user[:password]}@{domain}
```

Verify that the virtual file system is mounted and the folders can be navigated normally.

Start the `gnome-text-editor`, hit "open" and load a file from the virtual file system, modify it, save it (wait for the progress bar at the top to finish), close the editor and verify that your modifications are reflected in the server with `cat $XDG_RUNTIME_DIR/gvfs/sftp*/path/to/file`.


## Admin

Using an user in the `sudo` group

```none
$ gnome-text-editor admin:///etc/sudoers
```

Should prompt you for your password and be able to open `sudoers`


## Archive (Ubuntu 26.04 and older only)

```none
$ /usr/libexec/gvfsd-archive file=file:///path/to/archive.zip
```

And check that the archive is listed in the `nautilus` sidebar and browseable


## FTP

```none
$ gio mount ftp://ftp.alsa-project.org/pub/lib/
$ gio list ftp://ftp.alsa-project.org/pub/lib/
$ gio mount -u ftp://ftp.alsa-project.org/pub/lib/
```

Use "anonymous" user with empty password
It should let you mount, list the content and unmount the share


## Mounts monitor

```none
$ gio mount -o
```

Connect an USB stick to the computer and check the monitor correctly lists the event.
If there is a working partition on the device verify that it gets mounted and is listed in the `nautilus` sidebar


## Network

```none
$ gio list network:
```

Should list local network `dnssd` available resources (similar to the corresponding `nautilus` section).

If you have none, then set a samba share up as described in <https://ubuntu.com/tutorials/install-and-configure-samba#3-setting-up-samba>.


## One Drive

In `gnome-control-center` attach to a Microsoft 365 account.

If you do not have any, create a file in your One Drive account <https://onedrive.live.com/>.

Verify that after attachment, the file manager Nautilus gets a new entry in its left vertical pane corresponding to your One Drive account, and that you can find your files in it.

Move one file from your local file system into the "My files" folder of the One Drive file system, then verify that the new file is now present in <https://onedrive.live.com/>.


## Recent

```none
$ gio list -ldu recent:
```

Should list recently open documents (equivalent to the corresponding `nautilus` section, only works for files opened through the GTK APIs compatible)


## SMB

If you have access to some SMB share try browsing them from the `nautilus` `smb://` location


## Trash

```none
$ gio list trash:
```

Should list files deleted in `nautilus` (similar to the corresponding `nautilus` section)
