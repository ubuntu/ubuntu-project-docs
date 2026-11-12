(Evince-test-plan)=
# Evince test plan

:::{note}
The `evince` package was part of `main` through Ubuntu 24.04 LTS (noble). From Ubuntu 25.10 (questing) onward, it was replaced by {ref}`Papers <Papers-test-plan>` and moved to `universe`. This test plan is kept for reference when working with older Ubuntu LTS releases.
:::


## PDF file


This test will check that Evince can display PDFs correctly

* Open `Document Viewer`
  * Document viewer launches
* Open a pdf by selecting file, open and choosing a pdf file
  * The selected PDF is displayed correctly


## Functionality


This test will check that Evince functions normally

* Open a pdf by selecting file --> open then choosing a pdf file
* Make sure that Evince is not in fullscreen mode
* Press {kbd}`F11`
  * Evince enters fullscreen mode
* Press {kbd}`F11` again
  * Evince exits fullscreen mode and restores the window size and position correctly
* Make sure sidebar is displayed
* Press {kbd}`F9`
  * Evince hides the sidebar
* Press {kbd}`F9`
  * Evince displays a sidebar with page thumbnails or the document index
* Press {kbd}`ctrl` + {kbd}`left`
  * The pdf is rotated left
* Press {kbd}`ctrl` + {kbd}`right`
  * The pdf is rotated right
  * Evince displays the rotated document correctly
