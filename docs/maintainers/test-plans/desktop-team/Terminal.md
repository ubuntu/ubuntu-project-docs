(Terminal-test-plan)=
# Terminal test plan

Since the **Terminal** doesn't have a test suite or autopkgtests, we rely on a manual test plan to verify functionality after updates to new versions. These tests should be run before every SRU and when updating `ptyxis` to a new major version in Ubuntu's development series.


## Open the terminal with the global keyboard shortcut

Press {kbd}`Ctrl` + {kbd}`Alt` + {kbd}`T`. The Terminal app should start. No other terminal app should be launched with that default keyboard shortcut.


## Open a new tab

1. Open the terminal
2. Use `cd /` to change the directory to the `/` directory
3. Click the **+** button to open a new tab
4. A new tab should open with the same current working directory
5. Use {kbd}`Ctrl` + {kbd}`Shift` + {kbd}`T` to open a new tab
6. A new tab should open with the same current working directory

:::{note}
This feature is not yet working for Ptyxis but will be fixed before we switch the default terminal to Ptyxis ({lpbug}`2083705`).
:::


## Default font

The default font for the terminal content area should be Ubuntu Mono.


## Default keyboard shortcuts

Open the **☰** menu and click _Keyboard Shortcuts_. Test each listed keyboard shortcut one by one. Close the _Keyboard Shortcuts_ dialog before testing each shortcut.


## Zoom

Open the ☰ menu and use the **-** and **+** buttons to adjust the zoom of the terminal content area. The zoom should change immediately.


## Screen reader

1. Use the global keyboard shortcut {kbd}`Alt` + {kbd}`Windows key` + {kbd}`S` to toggle on the screen reader
2. Open the Terminal
3. Enter `ls /`
4. The screenreader should read your command as you type it, then the contents of the `/` folder, and finally your terminal prompt
5. Use the global keyboard shortcut {kbd}`Alt` + {kbd}`Windows key` + {kbd}`S` to toggle off the screen reader


## Notifications for long running background commands

1. Open the Terminal
2. Run this command: `sleep 5`
3. Immediately switch to a different tab or window
4. A few seconds later, you should receive a notification to let you know that the `sleep 5` command has completed
5. Run `sleep 5` again but this time keep your focus on the console
6. A few seconds later, the command should complete but there shouldn't be a notification.


## Dark theme support

* Open the **☰** menu. Verify that switching between Light, Dark, and Automatic style modes works correctly to change the colors for the terminal preferences dialog.

Currently colors are not configured to change for the terminal window decoration or the terminal content area based on the Light/Dark style.


## Red style for root

In a terminal window, run the command `sudo su`

The terminal titlebar should change color to red. After entering your password, you can run the command `exit` to exit root mode. The terminal titlebar should change back to the normal theme (light or dark).

The color change actually works even if you aren't authenticated as root yet. That's an implementation detail/bug and may change.


## Alternate style for remote

In a terminal window, run a command like `ssh exampleuser@example.com`

The terminal titlebar should change color to a different shade of purple. After entering your password, you can run the command `exit` to exit the ssh session. The terminal titlebar should change back to the normal Ubuntu purple.

The color change actually works even if you aren't connecting to the remote server yet. That's an implementation detail/bug and may change.


## Features not implemented for Ptyxis yet


### Open the terminal from the file browser

* Enter a folder in the default file browser (`nautilus`).

* Right click on either the empty space in the main view or on a different directory.

* Choose _Open in Terminal_. A Terminal window should open with the current working directory set to the selected directory
