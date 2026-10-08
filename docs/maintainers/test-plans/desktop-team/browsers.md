(browsers-test-plan)=
# Browsers test plan

* **Test plan for component**: browsers


## Description

This is a common test plan shared across all of Ubuntu's browser packages. For the browser-specific test plans, see:

* `firefox` (TBD)
* {ref}`chromium <Chromium-test-plan>`


## Initial setup

* Install the snap or deb package depending on your distro version and whichever browser you'd like to test (for example, starting with impish, `firefox` is only available as a snap, whereas on Focal and earlier versions it was primarily a deb).


## Automated tests

* Ensure that the [autopkgtests](https://autopkgtest.ubuntu.com) for your package of choice pass on the amd64, i386, arm64, and armhf architectures.


## Manual tests

What follows is a series of manual tests for browser packages, to be used as a starting point for testing/validating browser packages. Please note that the list is not comprehensive/exhaustive, and is meant to be a starting point and guideline to your manual testing.


### about page(s)

* Open the browser's about page, and verify the correctness of version number, user agent string, profile directory, and the status of GPU support.

  * In Firefox, go to <about:support>.
  * In Chromium, go to <about:version> and <about:gpu>.


### Custom URL scheme handling

* Verify that clicking <mailto:foobar@nospam.org> opens your default email client and starts composing a message.

* Browse to <https://snapcraft.io/0ad>, click on the green {guilabel}`Install` button, then click the {guilabel}`View in Desktop store` button and verify that it opens the software store on the details page for 0 A.D.


### Default browser

#### In GNOME Settings

1. In Settings, open the Default Applications panel (`gnome-control-center default-apps`).

1. Verify that the right browser is indicated as the default browser. On Ubuntu the default is currently Firefox.

1. If you are testing another browser package, try setting it as the default browser and test that it remains the default after upgrading its package.

#### In the browser preferences

1. If supported by the browser, use its preferences system to set it as the default browser.

    - In Firefox: <about:preferences#general>
    - In Chromium: <about:settings/defaultBrowser>

1. Open the Settings application's Default Applications panel. If you previously had it open, change to another panel and then back to Default Applications, to trigger a reload of its displayed settings values.

1. Verify that this browser is now the default browser.

1. Check that the browser remains the default after upgrading it.

#### Reset the default browser

1. From the Settings application, change the default browser to another browser. You will need more than one browser install to test this.

1. In the browser you're testing, verify that it correctly detects no longer being the default browser and that its button to make itself the default browser is visible and active.

1. From the Settings application, change the default browser to the browser you're testing

1. In the browser, verify that it correctly detects being the default browser and optionally that its button to make itself the default browser is now hidden or disabled.

### Search engine referrals

* Verify that when doing a web search from the address bar or search bar of the browser, the referral code is correctly set as a URL parameter.

    * For Google: `client=ubuntu`
    * For other search engines, something like: `t=canonical`


### Downloads

* Download a tarball (e.g. [grace_5.1.25.orig.tar.gz](https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/grace/1:5.1.25-13/grace_5.1.25.orig.tar.gz)). Open the browser's downloads view.

    * Verify that the file is fully downloaded.
    * Verify that you can open the parent folder containing it (this should open `nautilus` or your default file manager).
    * Verify that you can open the downloaded file from the browser (e.g. for a tarball it should open in an archive manager like `file-roller`).

* Download a [sample DOC(X) file](https://interoperability.blob.core.windows.net/files/MS-DOC/%5bMS-DOC%5d-221115.docx) and verify:

    * Verify that the file is fully downloaded.
    * Verify that you can open its parent folder.
    * Verify that you can open the downloaded file from the browser (in this case it should open in LibreOffice Writer).

* If the browser supports rendering and displaying PDF files directly in the browser itself (like `firefox` and `chromium` do), open a [sample PDF file](https://helpx.adobe.com/pdf/acrobat_reference.pdf), which should open and render in the browser.

  * Verify that you can scroll through the pages.
  * Verify that you can zoom in an out.
  * Verify that you can save (download) the file to disk.


### HTML5

* Browse to <https://html5test.com>.

    * Verify that the browser was correctly detected.
    * Verify that the score is as expected (this will vary from browser to browser).


### Geolocation

* Browse to <https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API/Using_the_Geolocation_API#result>.

    * Verify that you get prompted to allow/deny geolocation access.
    * Allow access, and verify that your approximate location is found.


### WebRTC

* Browse to <https://mozilla.github.io/webrtc-landing/gum_test.html>.

    * Verify that camera, microphone, and screen capture are working as expected.

    :::{important}
    Make sure to test both sharing the entire screen, and sharing specific windows, under Wayland; there have been breakages in the past.
    :::


### WebGL

* Browse to <https://webglsamples.org/aquarium/aquarium.html>.

    * Verify that on real hardware you get a good FPS (60) with the default number of sprites (500 fishes).


### Safe browsing warnings

* Browse to <https://testsafebrowsing.appspot.com>

    * Try clicking on some of the links, and verify that you get appropriate dissuasive warnings.


### Video playback

* Browse to <https://www.youtube.com> and watch any video.

  * Verify that you can pause and resume the video.
  * Verify that you can enter and exit full-screen.
  * Verify that while the video is playing, the screensaver or screen blanking is inhibited.

* Watch any 360° video on YouTube (for instance <https://www.youtube.com/watch?v=wczdECcwRw0>) and verify that you can pan with the mouse to move around in the scene while it's playing back.
