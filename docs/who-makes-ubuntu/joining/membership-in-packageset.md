(membership-in-packageset)=
# Membership in Package Set

Upload rights can be given for certain **Package Sets**, such as 'server' or
'desktop'. The original design intent was for the Package Set level (also called
"Per Package Uploaders") to be applied to individuals who will only be working
on a very small set of packages.

For this reason, some people skip this level and head straight for
{ref}`MOTU <membership-in-MOTU>` or {ref}`Core Dev <membership-in-core-dev>`
instead. If you already have strong packaging experience via another distro,
you can certainly consider doing this.

That said, even if you intend to *eventually* apply for Core Dev membership,
gaining Package Set first can be an effective way to build towards those roles,
allowing you to upload your own work (within limits), and participate in reviews
and {ref}`sponsorship <sponsorship>`.


## Application process

1. **Important** Check the
   [Developer Membership Board (DMB) agenda](https://wiki.ubuntu.com/DeveloperMembershipBoard/Agenda)
   to see when the DMB next meeting is, and to check the queue of applications.
   Only 2 applications are considered each meeting so if there's a queue, make
   sure to reserve a spot for when you think you'll be ready for consideration.

1. {ref}`packageset-create-wiki-page`

1. {ref}`packageset-training-and-preparation`, as needed

1. {ref}`packageset-prepare-application-form` on your wiki page

1. {ref}`packageset-collect-endorsements`

1. [Apply for team membership](https://wiki.ubuntu.com/DeveloperMembershipBoard/ApplicationProcess)
   by announcing on the `devel-permissions@` mailing list and adding your name
   to the DMB agenda (if you haven't already)

1. Review past meeting logs to get a sense of what to expect

1. Attend the meeting, answer questions, and receive your votes


(packageset-create-wiki-page)=
### Create a short wiki page for yourself

You can create your page at: `https://wiki.ubuntu.com/FirstnameLastname/`

On this page you should (at least):

* Introduce yourself and your past Ubuntu-related work

* Include a "Contact Information" section with

  * Your IRC nickname

  * Your Launchpad ID

You can look at other people's pages for ideas of other things you can include.
You'll be reusing this text in your membership applications later.


(packageset-training-and-preparation)=
### Training and preparation

We're going to describe an idealized training program here; however, no two
applications are exactly the same, and there is a lot of flexibility in
expectations. This is particularly true for Package Set given that it is, by
definition, of limited scope. Just be prepared to give extra justification if
you diverge substantially from the expectations listed below.


#### The basics

Ideally, you should have a solid mastery of the
basic packaging skills for Debian/Ubuntu
distributions, including the following:

* {ref}`Fixing bugs in packages <fix-a-bug-in-a-package>`
* Building binary packages from source, using `sbuild` or `debuild` in a
  `chroot` or `lxc` environment
* Creating the initial packaging for new software
* Merging updates from Debian
* Backporting patches
* Forwarding bugs and patches to Debian and to upstream maintainers
* Stable Release Update (SRU) process

Make sure you've done each of the above items at least a couple of times. If
you're not comfortable with any of these, plan on doing some additional
practice with them.


#### More advanced

You should also work towards understanding some more advanced packaging topics:

* The purpose of the
  {ref}`different files in debian/ <debian-directory>`

* [Debian policy](http://www.debian.org/doc/debian-policy/)

* [Ubuntu's release process](https://wiki.ubuntu.com/UbuntuDevelopment/ReleaseProcess),
  including the {ref}`freeze exception process <request-a-freeze-exception>`

* Running {ref}`autopkgtest <run-package-tests>`

* Troubleshooting the
  [migration of packages](https://wiki.ubuntu.com/ProposedMigration) from
  `-proposed`.

While you may not have direct experience with some (or most) of these topics,
you should know enough about the concepts to be able to talk about them.


#### Package specialization

In addition to Ubuntu packaging, you need to have some technical expertise
with the subset of software you'll be working on, and the processes and
procedures standardized for them. For example, for the Ubuntu Server team you
would need to have experience with technologies such as systemd and networking,
and processes such as using git-ubuntu for package maintenance.

Keep in mind the DMB's perspective follows the "Need to unblock" principle:
They want to approve applications that will either reduce contributor friction
or save work for sponsors. Establishing yourself as an area expert and a resource
for contributors helps prove the former, and your volume and frequency of
uploads justifies the latter.

Collaboration with the upstream(s) related to the software in your Package Set
is important as well. Gain experience with your upstreams' bug reporting
processes, patch review processes, and testing/CI systems if you haven't yet.
In general, the more you narrow your focus on specific packages, the more you'll
need to develop your collaboration with their upstream(s).

On the other hand, if you are a Canonical employee you will need to be able to
negotiate the distinction between Ubuntu governance and Canonical priorities
within your area of focus. Sometimes, these can appear to collide and require a
certain level of diplomacy to find solutions that work well for both sides. The
less experience you have in Debian or other open source communities, the more
thought you'll want to put into this.

Finally, you'll know you're past ready for applying if anyone ever asks, "How
do you not already have upload rights??"


(packageset-prepare-application-form)=
### Prepare your application form

Load `https://wiki.ubuntu.com/[FirstnameLastname]/PackagesetDeveloperApplication`,
making sure to replace `[FirstnameLastname]` with what you used to create your
{ref}`personal wiki page <packageset-create-wiki-page>`.

Select {guilabel}`Ubuntu Development/Developer Application Template` from the list of
templates, and follow the directions on how to fill it out. 

```{note}
You can look at
[past applications](https://wiki.ubuntu.com/Home?action=fullsearch&context=180&value=DeveloperApplication&titlesearch=Titles)
such as
[`Paride`'s](https://wiki.ubuntu.com/ParideLegovini/UbuntuServerDeveloperApplication)
if you need some examples.
```

Specify at the top that you're "applying for upload rights to the Ubuntu Server
Package Set", replacing "Ubuntu Server" as appropriate, or listing out the
exact, specific packages.


(packageset-collect-endorsements)=
### Collect endorsements

To gain upload rights, you'll need to collect endorsements from people who have
sponsored your packages. If you work for Canonical, ask in your team's regular
discussion channels, and individually contact each sponsor who is not in your
team.

It's good form to only ask people who have sponsored multiple packages for you,
or that have worked with you on particularly tricky packaging efforts. You want
to strike a good balance between quality and quantity here.


## Further information

* [Thoughts from `rbasak` on how he assesses applications](https://wiki.ubuntu.com/RobieBasak/DMB/CoreDev)
* [Ubuntu Wiki overview of Ubuntu development](https://wiki.ubuntu.com/UbuntuDevelopers)

Once you've been granted Package Set upload permissions, there are at least
three distinct directions you could embark on, depending on your goals:

* MOTU, if you want to go deeper into the Ubuntu packaging world.
* Membership in packaging teams at other distributions, if you want to broaden
  the reach of your software.
* Upstream maintainer in your project(s) of interest, if you want to focus
  more on the development of the software itself.

