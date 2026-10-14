(Showtime-test-plan)=
# Showtime test plan

Below are the test cases that should be run when Showtime is updated to new major releases in the development version of Ubuntu. These should also be run for all Showtime Stable Release Updates.

Showtime is the default media player of the Ubuntu Desktop, starting with Ubuntu 26.04

All tests are meant to be executed from a GNOME Wayland desktop session (the default Ubuntu Desktop session).


## Open Showtime

1. Open "Video Player" from the applications menu
2. Verify that you are presented with a screen to open media


## View a media file

1. Open "Video Player"
2. Click "Open..."
3. Verify that the file selector dialog showed up
4. Choose any video file
5. Verify that video is played back successfully
6. Verify the scrubbing (seeking) works successfully using the playback slider, and the forward/backward buttons.
7. Verify that rotation works (available in the cog menu)
8. Verify that changing the playback speed works. Try scrubbing at different playback speeds.
9. Repeat for as many codecs as you have available. Ideally {H.264,H.265,AV1,VP9} x {Opus, AAC}.


## Open from Files

1. Open the "Files" app
2. Right Click, Open With Video Player
3. Verify that the media plays back.


## Screenshot

1. Open a media file in "Video Player"
2. Enter the burger menu at the top of the interface and select "Take Screenshot"
3. Save the screenshot, and ensure it is correct.


## Help menu

1. Open "Video Player"
2. Enter the burger menu at the top of the interface and select "About Video Player"
3. Ensure the information is correct.
