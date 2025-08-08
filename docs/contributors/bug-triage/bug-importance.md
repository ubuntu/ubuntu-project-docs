(bug-importance)=
# Bug importance

Ubuntu uses the following guidelines for assigning **importance** to a bug. The
importance of the bug signifies the priority it should be given by the person
who will fix it.


## Meanings of importance values

Undecided
: The default for new bugs. This also means there is insufficient information
  to determine the importance.

Wishlist
: Missing functionality. These aren't always bugs, but can be ideas for new
  features. They can also be requests to have software packaged for Ubuntu.

: If it is non-trivial to implement, it should rather be written as a feature
  specification (see [Feature Specifications](https://wiki.ubuntu.com/FeatureSpecifications).

: These can be bugs that affect an experimental extension or non-essential
  feature of a given package/project.

: Bugs that would only be fixed on a best-effort or outside-contribution basis
  might also be considered wishlist. 

Low
: Bugs that affect functionality, but to a lesser extent than most bugs. Some
  examples are:

  * Bugs with easy work-arounds
  * Bugs that affect unusual end-user configurations or uncommon hardware
  * Bugs that affect a non-essential aspect and limited scope of the application
  * Bugs with a moderate impact on a non-core[^2] application
  * Cosmetic/usability issues that do not limit the functionality of a
    non-core[^2] application
  * Non-ideal default configurations 

Medium
: Most bugs are of medium importance -- examples are:

  * A bug with a moderate impact on a core[^1] application
  * A bug with a severe impact on a non-core[^2] application
  * A bug impacting accessibility of a non-core[^2] application
  * A usability issue that does not limit the functionality of a core[^1]
    application
  * A problem with a non-essential hardware component (removable network card,
    camera, webcam, music player, sound card, power management feature, printer,
    etc.) 

High
: A bug that fulfills any of the following criteria:

  * Has a severe impact on a small portion of Ubuntu users (estimated)
  * Makes a default Ubuntu installation generally unusable for some users
    * For example, if the system fails to boot, or X fails to start, on a
      certain make and model of computer 
  * A problem with an essential hardware component (disk controller, built-in
    networking, video card, keyboard, mouse)
  * Has a moderate impact on a large portion of Ubuntu users (estimated)
  * Prevents the application or any dependencies from functioning correctly at
    all
  * Renders essential features or functionality of the application (or
    dependencies) broken or ineffective
  * Impacts accessibility of a core[^1] application 

Critical
: A bug that has a severe impact on a large portion of Ubuntu users:

  * Causes data corruption
  * Crashes the entire operating system
    * For example, if the system fails to boot, or X fails to start, on various
      makes and models of computer 
  * Renders the system temporarily or permanently unusable
  * Severely affects applications beyond the package responsible for the root
    cause 


## Who can change the importance?

You need to be a member of {ref}`Ubuntu Bug Control <bug-control-team>`, either
through direct membership or because of your membership in another team, to set
the importance of a bug.

If you are a Bug Control team member, you can change the importance of a bug
report by clicking on the current {guilabel}`Status` or {guilabel}`Importance`,
in the yellow line and under the {guilabel}`Affects` column header, which will
reveal a sub menu. You can then choose a new importance in the drop down box.

If you are not in the Bug Control team, you need to ask a Bug Control team
member to set the importance for you. Paste the bug number in the `#ubuntu-bugs`
IRC channel and say you think the bug should be set to importance 'Wishlist /
Low / Medium / High / Critical'.
Someone will notice your comment and set the importance for you, although not
necessarily immediately.


[^1]: A "core" package can be identified as being part of a task in the `apt-cache` headers. You can see the `apt-cache` headers by running `apt-cache show <package>` in a terminal, and looking at the "Task: " field in the output.

[^2]: A "non-core" package can be identified as a package that is not part of a task, and is not in `main`. You can see the `apt-cache` headers by running `apt-cache show <package>` in a terminal, and looking at the "Task: " field in the output.
