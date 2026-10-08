(Localsearch-test-plan)=
# Localsearch test plan

:::{note}
`localsearch` has been part of `main` since Ubuntu 26.04 LTS (resolute).
:::


## `localsearch`

This is the manual test plan for GNOME's `localsearch` (previously known as `tracker-miners` prior to GNOME 47), the file indexing, metadata extraction, and search provider for the Ubuntu desktop. Its backend database is powered by `tinysparql` (formerly `tracker`).


### Setup

* Use a computer with a standard Ubuntu GNOME session installed.
* Ensure the `localsearch` and `tinysparql` packages are installed.
* Open **Settings** -> **Search** and verify that the global search toggle is enabled.
* Open **Settings** -> **Search** -> **Search Locations** and ensure standard directories like **Documents**, **Music**, and **Pictures** are enabled.


### Basic file indexing and shell integration

* Open a terminal.
* Create a uniquely named empty file in your Documents directory: `touch ~/Documents/localsearch-test-1234.txt`
* Wait approximately 5 to 10 seconds for `localsearch` to detect and index the new file.
* Press the {kbd}`Super` key to open the GNOME Shell Activities overview.
* Type `localsearch-test-1234` in the search bar.

**Expected Results**

* The file `localsearch-test-1234.txt` should appear in the search results under the "Files" category.


### Nautilus (Files) integration

* Open the **Files** (Nautilus) application.
* Navigate to your Home directory.
* Click the search icon (magnifying glass) in the header bar or press {kbd}`Ctrl` + {kbd}`F`.
* Type `localsearch-test-1234`.

**Expected Results**

* The file `localsearch-test-1234.txt` should appear in the search results.
* Delete the file (`rm ~/Documents/localsearch-test-1234.txt`) and perform the search again; it should no longer appear in the results.


### Content and full-text extraction

* Open a terminal.
* Create a text file containing a unique string: `echo "localsearch-unique-content-string-99" > ~/Documents/content-test.txt`
* Wait a few moments for the file's content to be extracted and indexed.
* Press the {kbd}`Super` key to open the GNOME Shell overview.
* Type `localsearch-unique-content-string-99` in the search bar.

**Expected Results**

* The file `content-test.txt` is displayed in the search results, proving that full-text content indexing is functioning correctly.
* Remove the file after testing: `rm ~/Documents/content-test.txt`


### Media metadata extraction

* Copy a sample image (e.g., JPG or PNG) into your **Pictures** directory.
* Rename the file to something unique, e.g., `localsearch-media-test.jpg`.
* Open a terminal and run `localsearch info ~/Pictures/localsearch-media-test.jpg` (adjust the path if necessary).

**Expected Results**

* The command should output extracted metadata specific to the media file type (e.g., dimensions, format, MIME type, and EXIF data).


### Settings and search locations

* Open **Settings** -> **Search**.
* Click on **Search Locations**.
* Turn off the toggle for the **Documents** directory.
* Create a new test file in the Documents directory: `touch ~/Documents/localsearch-ignored-1234.txt`
* Wait a few moments, then press the {kbd}`Super` key and search for `localsearch-ignored-1234`.

**Expected Results**

* The file should **not** appear in the search results, as the directory was excluded from indexing.

* Go back to **Settings** -> **Search** -> **Search Locations** and toggle **Documents** back on.
* Wait a few moments and search again for `localsearch-ignored-1234`.

**Expected Results**

* The file should now appear in the search results.
* Remove the file after testing: `rm ~/Documents/localsearch-ignored-1234.txt`


### Command line operations

* Open a terminal.
* Run the status command: `localsearch status`

**Expected Results**

* The output displays the status of the file system indexers (e.g., `Idle`, `Indexing`) and provides statistics on the indexed data.
* The command executes cleanly without crashes, core dumps, or DBus connection errors.
