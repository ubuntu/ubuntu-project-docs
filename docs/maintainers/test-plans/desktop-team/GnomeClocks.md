(GnomeClocks-test-plan)=
# GNOME Clocks test plan

:::{note}
`gnome-clocks` has been part of `main` since Ubuntu 23.10 (mantic). It was in `universe` in earlier releases.
:::

Since `gnome-clocks` doesn't include autopkgtests we will follow a manual test plan to verify updates.
MIR reference {lpbug}`2032670`


## Extra timezones

* start the software, the 'world' tab is select

* click on the top left '+' icon

* search for some important cities and add them

check that the local time displayed for those is correct


## GNOME calendar integration

display the `gnome-shell` calendar drop-down and verify that the new timezones and their local time are included now


## Alarms

* go to the alarms tab

* set up an alarm

* verify that you get a beeping sound and a notification at the time defined


## Stopwatch

* go to the stopwatch tab

* click start

* verify with another device that the count is correct

* click lap

it should add an entry with the time at the time of the action and keep counting


## Timer

* define a time

* click play

* verify that once the counter reach zero a sound is played and a notification displayed
