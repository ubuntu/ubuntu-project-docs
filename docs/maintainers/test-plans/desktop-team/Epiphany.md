(Epiphany-test-plan)=
# Epiphany test plan

Below are the test cases that should be run when `epiphany-browser` is updated to a new major release in the development version of Ubuntu. These should also be run for any Stable Release Update for `epiphany-browser`.


## Test case

0. Epiphany has build tests that will fail the build if they fail. Ensure the build is successful on all architectures.
1. Install the Epiphany updates
2. Visit <https://ubuntu.com/> . Verify that the website loads and appears to work as expected.
3. Visit <https://jeremy.bicha.net/> In the address bar, there should be a 📖 icon. Click it to activate Reader Mode. The site should reload in a simplified view suitable for reading.
4. From a terminal run
   `sudo apt install gstreamer1.0-plugins-bad`
5. Visit <https://youtu.be/sgcVp5RHy4Q> . The video and audio should play.


## What could go wrong

`epiphany` is not seeded in any Ubuntu desktop flavor so users are likely to have another web browser available if things were to go wrong and know how to install it.

As a component of GNOME core, there is a micro-release exception for `epiphany-browser`

{ref}`GNOME micro release exceptions <reference-exception-GNOMEUpdates>`.
