(GnomeShellExtensionTilingAssistant-test-plan)=
# GNOME Shell Tiling Assistant extension test plan

:::{note}
The `gnome-shell-extension-ubuntu-tiling-assistant` binary package was part of `universe` in Ubuntu 24.04 LTS (noble) and `main` from Ubuntu 25.10 (questing) onward. From Ubuntu 26.04 (resolute) onward, it's bundled into the `gnome-shell-ubuntu-extensions` source package rather than shipped standalone.
:::


## GNOME Shell Tiling Assistant extension

It's an extension that the desktop team provides by default to improve tiling abilities of GNOME Shell


### Manual test plan

Given that the extension does not provide any automated testing, we should ensure it works by performing these operations

1. Dragging windows using the pointer to the edges of the screen should show tiling highlights, releasing the pointer should semi-maximize the window.

2. Dragging a window to the top will allow to top-tile a window after a delay

3. When a tile is created and there are enough windows opened, a popup is shown to select which window to use to fill the empty space

4. Tiles groups are created automatically so, focusing a window of a tiling group should automatically raise all the windows of such tiling group, no matter the application they belong to

5. It should be possible to resize multiple windows of a tiling group with a single resize dragging operation

6. Using the keybindings ({kbd}`super` + arrows and {kbd}`super` + keypad numbers) is possible to tile windows
