(Loupe-test-plan)=
# Loupe test plan

Below are the test cases that should be run when `loupe` is updated to new major releases in the development version of Ubuntu. These should also be run for all `loupe` Stable Release Updates.

Loupe is the default image viewer of Ubuntu Desktop, starting with Ubuntu 25.10

All tests are meant to be executed from a GNOME Wayland desktop session (the default Ubuntu Desktop session).


## Open Loupe

1. Open "Image Viewer" from the applications menu
2. Verify that you are presented with a screen to open files


## View an image

1. Open "Image Viewer"
2. Click "Open Files"
3. Verify that the file selector dialog showed up
4. Choose any image file
5. Verify that the image is displayed
6. Verify that the filename is displayed on the titlebar


## Open from Files

1. Open the "Files" app
2. Right Click > Open With Image Viewer
3. Verify that the image is displayed


## Zoom

1. Open an image in "Image Viewer"
2. Zoom with a mouse wheel or touchpad gesture
3. Verify that the image view is zoomed accordingly
4. Press the '{kbd}`+`' and '{kbd}`-`' keys
5. Verify that the image view is zoomed accordingly


## Image manipulation

1. Click the "Edit Image" button on the titlebar
2. Crop the image by resizing with the handles
3. Align the cropping by clicking the various aspect-ratio buttons
4. Click the tick-mark to apply the cropping
5. Verify that the preview was cropped
6. Click the "Rotate Clockwise" and "Rotate Counter Clockwise" buttons
7. Verify that the preview is rotated accordingly
8. Click the "Mirror Vertically" and "Mirror Horizontally" buttons
9. Verify that the preview is flipped accordingly
10. Click "Save" > "Save As..."
11. Verify that the file saver dialog showed up
12. Enter a file name
13. Click "Save"
14. Verify that the new file is visible in the "Files" app


## Navigation

1. Open an image in "Image Viewer"
2. Click the "Toggle Fullscreen" button on the titlebar
3. Verify that the window became fullscreen, and the image is still visible
4. Untoggle fullscreen
5. Verify that the window returned to its previous dimensions
6. Click the "Image Properties" button on the titlebar
7. Verify that a sidebar opened
8. Verify that, to your best knowledge, the information in the sidebar is correct
9. Click the "Main Menu" hamburger button on the titlebar
10. Click "New Window"
11. Verify that a new window appeared in its empty view
12. Click the "Main Menu" hamburger button on the titlebar
13. Click "Keyboard Shortcuts"
14. Verify that a window opened describing the available shortcuts


## Print

1. Open an image in "Image Viewer"
2. Click the "Main Menu" hamburger button on the titlebar
3. Click "Print..."
4. Verify that the print dialog showed up
5. Verify that printing to PDF works as expected


## Set as background

1. Open an image in "Image Viewer"
2. Click the "Main Menu" hamburger button on the titlebar
3. Click "Set as Background"
4. Verify that a dialog showed up with a preview of a generic desktop
5. Click "Set"
6. Verify that the image was set as the desktop wallpaper
