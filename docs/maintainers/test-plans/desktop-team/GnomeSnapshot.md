(GnomeSnapshot-test-plan)=
# GNOME Snapshot test plan

:::{note}
`gnome-snapshot` has been part of `main` since Ubuntu 24.04 LTS (noble).
:::

Since the autopkgtest infrastructure isn't really suitable for camera testing we will require manual testing for updates to `gnome-snapshot`


## Camera is detected

* Start `snapshot` and verify that the camera is correctly detected and the image correctly displayed in the application


## Take a picture

* Ensure the 'photo' button is pressed at the bottom right corner
* Click on the round 'take a picture' button
* There should be a visible effect with a click sound, the picture should be saved in `$XDG_PICTURES_DIR/Camera`


## Take a delayed picture

* Select a delay in the bottom-left selector and go through the steps from the previous section again


## Take a video

* Ensure the 'video' button is pressed at the bottom right corner
* Click on the round 'take a video' button
* The recording timer should display as an overlay on the picture
* Click on the round button again to stop the recording
* A video should be stored in `$XDG_VIDEOS_DIR/Camera`


## Take a delayed video

* Select a delay in the bottom-left selector and go through the steps from the previous section again
