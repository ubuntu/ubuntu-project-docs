GNOME had a micro release exception granted by the Technical Board in
June 2012. Since the granting of micro release exceptions was made more
generic and then decisions delegated to the SRU team directly, the
documentation of this exception was removed.

However, GNOME does not meet the new generic terms on the QA
requirement. The policy requires a TB exception. Since this was granted
previously, including the consideration of QA, we can treat this as
"grandfathered".

Therefore, GNOME has a microrelease exception as follows, which applies
regardless of the additional QA requirements in the current general MRE
policy:

-  "GNOME (only the core modules and apps, not the entirety of what is
   hosted on gnome.org) (approved on 2012-06-22)"
-  Clarifying this is ongoing
   `here <https://discourse.ubuntu.com/t/scope-of-gnome-mru/18041/3>`__,
   the first cut is “the set of apps in
   `core <https://gitlab.gnome.org/GNOME/gnome-build-meta/-/tree/master/elements/core>`__,
   plus the direct dependencies in
   `sdk <https://gitlab.gnome.org/GNOME/gnome-build-meta/-/tree/master/elements/sdk>`__\ ”.

Microrelease updates to gnome-shell are at risk of regressing packages
providing gnome-shell extensions as we discovered in the case of `LP:
#1892245 <https://bugs.launchpad.net/ubuntu/+source/gnome-shell-extension-dash-to-panel/+bug/1892245>`__.
Going forward, the SRU team would like to see suitable mitigations for
this type of regression before publishing gnome-shell microrelease
updates, such as through thorough testing of reverse dependencies.

Vala is not considered part of GNOME for the purposes of micro release
updates. Regardless of this, the Vala situation is special as it’s
generally necessary to also rebuild reverse build dependencies for a
Vala SRU to have any effect. If Vala microrelease updates are desired,
this will need to be justified and requested independently (whether as a
one-off or a standing documented case).

References:

-  https://lists.ubuntu.com/archives/technical-board/2012-June/001327.html
-  https://lists.ubuntu.com/archives/technical-board/2012-June/001298.html
