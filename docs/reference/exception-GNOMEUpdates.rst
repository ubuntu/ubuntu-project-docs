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
-  GNOME provides a list of what they consider core as a part of the
   release. The lists are found at
   \`https://download.gnome.org/teams/releng/$GNOME_VERSION/versions\`
   (eg: https://download.gnome.org/teams/releng/42.0/versions). A Debian
   maintainer produces a helpfully-parsed version of this list with
   upstream names matched to source package names at
   https://people.debian.org/~fpeters/gnome/debian-gnome-42-status.html.
   (Older GNOME versions are also available, but these do not have the
   upstream name->source package transformation applied).
-  In addition GNOME-provided lists, we additionally consider the
   following packages to be under the MRE exception:

   -  

      -  evolution
      -  evolution-ews
      -  file-roller
      -  gedit
      -  gnome-terminal
      -  gnome-tweaks
      -  seahorse
      -  everything that the gnome-games apt package directly depends on

-  As an exception to the GNOME-provided list, vala is **not** covered
   by this MRE. Relevant bug fixes to vala are rare, and require special
   handling (as all rdepends must be rebuilt for any fixes to be picked
   up).

SRU-team tooling to automatically check if a package falls under the
GNOME MRE is in progress. Until that is complete, the following lists
are authoritative for MRE purposes:

-  `BionicGnomeMreList <BionicGnomeMreList>`__
-  `FocalGnomeMreList <FocalGnomeMreList>`__
-  `JammyGnomeMreList <JammyGnomeMreList>`__
-  `KineticGnomeMreList <KineticGnomeMreList>`__

Microrelease updates to gnome-shell are at risk of regressing packages
providing gnome-shell extensions as we discovered in the case of `LP:
#1892245 <https://bugs.launchpad.net/ubuntu/+source/gnome-shell-extension-dash-to-panel/+bug/1892245>`__.
For Ubuntu 22.04, most shell extensions have been removed from the
archive, and all remaining ones will be smoke-tested as a part of any
gnome-shell SRUs.

Mutter is also a special case, as it is a shared critical component with
Ubuntu Budgie. Mutter SRUs must be tested against the Budgie session in
addition to the Ubuntu/Ubuntu on Xorg/GNOME/GNOME Classic sessions.

References:

-  https://lists.ubuntu.com/archives/technical-board/2012-June/001327.html
-  https://lists.ubuntu.com/archives/technical-board/2012-June/001298.html
-  https://discourse.ubuntu.com/t/scope-of-gnome-mru/18041/42
