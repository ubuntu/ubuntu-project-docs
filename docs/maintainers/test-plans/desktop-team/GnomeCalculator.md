(GnomeCalculator-test-plan)=
# GNOME Calculator test plan


## Test cases for Gnome Calculator


### Activities integration

This test will check that mathematical operations can be previewed in the Gnome Activities overview

* Open Activities with the "{kbd}`Meta`" key, or by clicking the button in the top-left corner of the desktop
* Type a mathematical expression, such as `7+2`
  * A result entry is shown with `7+2 = 9`


### Opening and closing

This test will check that Gnome Calculator can be opened either from a terminal window or from the applications menu, and shutdown

* Open a terminal window, type `gnome-calculator` at the prompt and hit the "{kbd}`Enter`" key
  * Calculator opens
* Click the top right "X" of the window's title bar to close the application
  * Calculator closes
* Open Gnome Calculator from your FAMILY menu
  * Calculator opens


### Menu options

This test will check that Gnome Calculator's Application menu options work as expected

* Navigate to Mode -> Basic
  * Calculator's GUI changes to provide buttons suitable for basic equations
  * Equations are entered in standard mathematical form. For example to add 7 and 2 enter the following: 7+2
* Navigate to Mode -> Advanced
  * Calculator's GUI changes to provide buttons suitable for advanced mathematics such as Trigonometry
  * Trigonometry calculations can be performed using the sin, cos, and tan functions. For example sin 45
* Navigate to Mode -> Financial
  * Calculator's GUI changes to provide buttons suitable for financial equations
  * Financial functions cannot be performed using the keyboard and the following buttons are available: Ctrm, Ddb, Fv, Gpm, Pmt, Pv, Rate, Sln, Syd and Term
* Navigate to Mode -> Programming
  * Calculator's GUI changes to provide buttons suitable for computer programmers
  * When in programming mode there is a drop down menu for binary ({kbd}`Ctrl` + {kbd}`B` keys), octal ({kbd}`Ctrl` + {kbd}`O` keys) and hexadecimal ({kbd}`Ctrl` + {kbd}`H` keys) and the 'á' button opens a dialogue to convert characters to character codes
* From the Hamburger menu select one of the given options for 'Number format'
  * The format used to display results change accordingly to the selection made
* From the Hamburger menu navigate to Preferences
  * Preferences dialogue window opens
* Decrease/increase the value of decimal places to show
  * The number of decimal places, if trailing zeroes and if thousands separators are shown, change accordingly
* Tick the 'Trailing zeroes' option
  * The format used to display results shows trailing zeroes
* Tick the 'Thousands separators' option
  * The format used to display results shows digit grouping
* Click the 'Angle units' drop-down list and select one of the given options
  * The unit used to display results, when performing trigonometry calculations, change accordingly to the selection made
* Click the 'Word size' drop-down list and select one of the given options
  * The results when performing boolean algebra calculations, using the AND, OR and XOR operators, change accordingly to the selection made
* From the Hamburger menu navigate to About Calculator
  * A dialogue window opens and the "Credits" and "Legal" buttons correctly display the associated information
* From the Hamburger menu navigate to Contents
  * Calculator Help dialogue window opens


## What could go wrong

Gnome Calculator provides a shell plugin to preview mathematical expressions in the Activities overview search bar.

If there is a bug in the plugin, the shell might become unresponsive or consume a high amount of CPU resources.
