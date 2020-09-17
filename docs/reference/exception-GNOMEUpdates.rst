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

References:

-  https://lists.ubuntu.com/archives/technical-board/2012-June/001327.html
-  https://lists.ubuntu.com/archives/technical-board/2012-June/001298.html
