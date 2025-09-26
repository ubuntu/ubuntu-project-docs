(membership-in-packageset)=
# Membership in Package Set

Upload rights can be given for certain **Package Sets**, such as 'server' or 'desktop'.
The original design intent was for the Package Set level (also called "Per Package Uploaders (PPU)") to be applied to individuals who will only be working on a very small set of packages.

For this reason, some people skip this level and head straight for {ref}`MOTU <membership-in-MOTU>` or {ref}`Core Dev <membership-in-core-dev>`.
If you already have strong packaging experience via another distro, you can certainly consider doing this.

That said, even if you intend to *eventually* apply for Core Dev membership, gaining Package Set first can be an effective way to build towards those roles, allowing you to upload your own work (within limits), and participate in reviews and {ref}`sponsorship <sponsorship>`.


(packageset-training-and-preparation)=
## Training and preparation

We're going to describe an idealized training program here; however, no two applications are exactly the same, and there is a lot of flexibility in expectations.
This is particularly true for Package Set given that it is, by definition, of limited scope.
Just be prepared to give extra justification if you diverge substantially from the expectations listed below.


### The basics

Ideally, you should have a solid mastery of the basic packaging skills for Debian/Ubuntu distributions, including the following:

* {ref}`Fixing bugs in packages <fix-a-bug-in-a-package>`
* Building binary packages from source, using `sbuild` or `debuild` in a
  `chroot` or `lxc` environment
* Creating the initial packaging for new software
* Merging updates from Debian
* Backporting patches
* Forwarding bugs and patches to Debian and to upstream maintainers
* Stable Release Update (SRU) process

Make sure you've done each of the above items at least a couple of times.
If you're not comfortable with any of these, plan on doing some additional practice with them.


### More advanced

You should also work towards understanding some more advanced packaging topics:

* The purpose of the {ref}`different files in debian/ <debian-directory>`

* [Debian policy](http://www.debian.org/doc/debian-policy/)

* {ref}`Ubuntu's release process <release-cycle>`, including the {ref}`freeze exception process <freeze-exceptions>`

* Running {ref}`autopkgtest <run-package-tests>`

* Troubleshooting the {ref}`migration of packages <proposed-migration>` from `-proposed`.

While you may not have direct experience with some (or most) of these topics,
you should know enough about the concepts to be able to talk about them.


### Package specialization

In addition to Ubuntu packaging, you need to have some technical expertise with the subset of software you'll be working on, and the processes and procedures standardized for them.
For example, for the Ubuntu Server team you would need to have experience with technologies such as systemd and networking, and processes such as using git-ubuntu for package maintenance.

Keep in mind the DMB's perspective follows the "Need to unblock" principle:
They want to approve applications that will either reduce contributor friction or save work for sponsors.
Establishing yourself as an area expert and a resource for contributors helps prove the former, and your volume and frequency of uploads justifies the latter.

Collaboration with the upstream(s) related to the software in your Package Set is important as well.
Gain experience with your upstreams' bug reporting processes, patch review processes, and testing/CI systems if you haven't yet.
In general, the more you narrow your focus on specific packages, the more you'll need to develop your collaboration with their upstream(s).

On the other hand, if you are a Canonical employee you will need to be able to negotiate the distinction between Ubuntu governance and Canonical priorities within your area of focus.
Sometimes, these can appear to collide and require a certain level of diplomacy to find solutions that work well for both sides.
The less experience you have in Debian or other open source communities, the more thought you'll want to put into this.

Finally, you'll know you're past ready for applying if anyone ever asks, "How do you not already have upload rights??"


## Further information

* {ref}`dmb-aspects-of-a-good-application`
* {ref}`joining-a-role`

Once you've been granted Package Set upload permissions, there are at least three distinct directions you could embark on, depending on your goals:

* MOTU, if you want to go deeper into the Ubuntu packaging world.
* Membership in packaging teams at other distributions, if you want to broaden the reach of your software.
* Upstream maintainer in your project(s) of interest, if you want to focus more on the development of the software itself.


-----

### Package Sets and seed updates

Ubuntu distribution is {ref}`organized into seeds <seed-management>`. The basic seeds, which define what goes into the Archive's `main` component, are:
`minimal`, `boot`, `standard`, `desktop`, `ship`, `live`, and `supported`.
There are many other seeds, which can be seen at:

* [DMB -- packageset](https://git.launchpad.net/~developer-membership-board/+git/packageset/tree/)

* [Core Dev -- Ubuntu](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/ubuntu/tree/)

* [Core Dev -- platform](https://git.launchpad.net/~ubuntu-core-dev/ubuntu-seeds/+git/platform/tree/)

For some seeds, we currently have an automated way to guarantee that the packages included in (or removed from) a seed are automatically included (or excluded) from its Package Set equivalent (thus guaranteeing, or denying, upload permissions to a developer with rights to this Package Set).

The process to automatically generate this 1:1 mapping (among seeds <--> Package Sets) is described at:
[DMB -- packageset](https://git.launchpad.net/~developer-membership-board/+git/packageset/tree/) README file.




