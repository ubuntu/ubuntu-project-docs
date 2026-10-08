(Orca-test-plan)=
# Orca test plan

Below are the test cases that should be run when `orca` or `at-spi2-core` is updated to new major releases in the development version of Ubuntu. These should also be run for all `orca` or `at-spi2-core` Stable Release Updates.


## Test case

Verify that you're able to complete the "Get started with the screen reader" tutorial on Ubuntu Desktop docs: <https://ubuntu.com/desktop/docs/en/latest/tutorial/get-started-with-the-screen-reader/>


## What could go wrong (`orca`)

Orca is the default screen reader used in Ubuntu Desktop and most desktop flavours.
Problems with the screen reader could render the system unusable for people with visually impaired people.

Orca is part of GNOME Core and is included in the GNOME micro release exception

<https://ubuntu.com/project/docs/SRU/reference/exception-GNOME-Updates/>


## What could go wrong (`at-spi2-core`)

`at-spi2-core` is the set of libraries used to build screen readers and accessible applications, used by the `orca` screen reader and GTK3/GTK4 applications in Ubuntu Desktop.
Problems with the screen reader could render the system unusable for people with visually impaired people.

`at-spi2-core` is part of the GNOME Minor Release Exception: <https://ubuntu.com/project/docs/SRU/reference/exception-GNOME-Updates/>
