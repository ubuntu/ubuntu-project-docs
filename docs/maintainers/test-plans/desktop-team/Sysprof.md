(Sysprof-test-plan)=
# Sysprof test plan

Below are the test cases that should be run when any of `sysprof`, `libdex`, or `libpanel` are updated to new major releases in the development version of Ubuntu. These should also be run for any Stable Release Update for `sysprof`, `libdex`, or `libpanel`.

Below are the test cases that should be run when any of `gnome-builder`, `libdex`, or `libpanel` are updated to new major releases in the development version of Ubuntu. These should also be run for any Stable Release Update for `gnome-builder`, `libdex`, or `libpanel`.


## Test case

1. From a terminal, run `sudo apt install sysprof`
2. Open _Sysprof_
3. On the _Profiler_ tab, enable all the options except for _Sample JavaScript Stacks_ (since `yelp` is not a GJS app)
4. On the _Application_ tab, enter `yelp` in the _Command Line_ field. (`yelp` is the default Help app for Ubuntu Desktop.)
5. On the _Counters_ tab, enable all options
6. On the _D-Bus_ tab, enable the _Session Bus_ option
7. On the _Graphics_ tab, enable all options
8. Click _Record to Memory_
9. You will likely be prompted to enter your password to run the profiler with elevated permissions. Enter your password. Sysprof will begin profiling now with a time counter.
10. Wait for the Help app to fully launch then click _Stop Recording_ in the `sysprof` dialog. This will probably take several seconds.
11. Close the Help app.
12. The `sysprof` app will take a few moments to finish loading the profile data.
13. Click each item in the sidebar. Each item should show content. The graphics tab may not show any content. The Network tab may not show any activity unless you have another network app like your web browser running and actively communicating with web servers.
14. After reviewing the profiled data, close the Sysprof app.


## What could go wrong

The Sysprof app is a standalone app but is proposed to be installed by default in Ubuntu Desktop 24.10. A critical bug could mean that users are unable to use this system profiling app.

`libsysprof-capture-4-dev` is a dependency of several GNOME development libraries (`libglib2.0-dev` [proposed for Ubuntu 24.10], `libgtk-4-dev` [proposed for Ubuntu 24.10], `libsoup2.4-dev`, `libsoup-3.0-dev`, and `libgtksourceview-5-dev`). A critical enough bug could make it impossible to build apps using those libraries, although that is unlikely to happen in an SRU since there is an autopkgtest specifically for `libsysprof-capture-4-dev` to detect this kind of bug. `sysprof` libraries are not a dependency of the runtime library itself (`libglib2.0-0` etc.) so a bug in `sysprof` won't otherwise affect usage of Ubuntu apps.


## What could go wrong (`libdex`)

`libdex` is only currently used by the GNOME Builder and Sysprof apps.

GNOME Builder is a standalone app that is not installed by default by any Ubuntu flavor. If there is a critical bug preventing GNOME Builder from being usable, a developer could use another IDE such as Visual Studio Code.

GNOME Builder is also distributed as a Flatpak and developers could use that if Ubuntu's .deb version is not working. (The .deb version of GNOME Builder installs `flatpak` by default anyway since that's how the build and run command is implemented for GNOME apps.)

The Sysprof app is also a standalone app but is proposed to be installed by default in Ubuntu Desktop 24.10. A critical bug in `libdex` could mean that users are unable to use this system profiling app.

This is mitigated by testing that both apps still run with the new `libdex` version.

`libdex` is also used by `libsysprof-capture-4-dev`. `libsysprof-capture-4-dev` is a dependency of several GNOME development libraries (`libglib2.0-dev` [proposed for Ubuntu 24.10], `libgtk-4-dev` [proposed for Ubuntu 24.10], `libsoup2.4-dev`, `libsoup-3.0-dev`, and `libgtksourceview-5-dev`). A critical enough bug could make it impossible to build apps using those libraries, although that is unlikely to happen in an SRU since there is an autopkgtest specifically for `libsysprof-capture-4-dev` to detect this kind of bug. `sysprof` libraries are not a dependency of the runtime library itself (`libglib2.0-0` etc.) so a bug in `sysprof` won't otherwise affect usage of Ubuntu apps.


## What could go wrong (`libpanel`)

`libpanel` is only currently used by the GNOME Builder and Sysprof apps.

GNOME Builder is a standalone app that is not installed by default by any Ubuntu flavor. If there is a critical bug preventing GNOME Builder from being usable, a developer could use another IDE such as Visual Studio Code.

GNOME Builder is also distributed as a Flatpak and developers could use that if Ubuntu's .deb version is not working. (The .deb version of GNOME Builder installs `flatpak` by default anyway since that's how the build and run command is implemented for GNOME apps.)

The Sysprof app is also a standalone app but is proposed to be installed by default in Ubuntu Desktop 24.10. A critical bug in `libpanel` could mean that users are unable to use this system profiling app.

This is mitigated by testing that both apps still run with the new `libpanel` version.


## Other info

It might be more interesting to test `gnome-weather` instead. It is a `gjs` app so would use `sysprof`'s support for profiling `gjs` apps. But `gjs` is not yet compiled with `sysprof` support. The Ubuntu Desktop team will investigate this after `sysprof` is allowed into Ubuntu main.

`gnome-weather` is also a network app so it could enable the network panel to show useful information.

`gnome-weather` is installed by default only in Ubuntu Desktop's Expanded installation option so we would need to add another step to the test case to install it.
