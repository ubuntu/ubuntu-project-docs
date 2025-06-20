Launchpad
=========

Launchpad is a software collaboration and hosting platform similar to platforms
like `GitHub`_. Launchpad is also the platform where the :term:`Ubuntu` project lives.
This is one of the major differences between the Ubuntu and :term:`Debian`
infrastructure.

.. note::

    Although the Ubuntu project is probably the largest user base of Launchpad, 
    Launchpad can be used by anyone. 

Launchpad features, among others, are:

- **Bugs**: :term:`Bug Tracking System`
- **Code**: :term:`source code <Source Code>` hosting with :term:`Git` or :term:`Bazaar`,
  :term:`version control <Version Control System>` and :term:`code review <Code Review>` features
- **Answers**: community support site and knowledge base
- **Translations**: collaboration platform for localizing software
- **Blueprints**: feature planning and specification tracking
- Ubuntu :term:`package <Package>` building and hosting
- Team/Group management

While platforms like GitHub put users and groups at the top level, Launchpad
puts projects at the top level. If you take Ubuntu as an example, you can
see that you can access it at the top level: `https://launchpad.net/ubuntu`.
Users and groups begin with a ``~``, for instance `https://launchpad.net/~ubuntu-foundations-team`.

Why not use platforms like GitHub?
----------------------------------

Although Launchpad's :term:`UI` and :term:`UX` are a bit dated, Launchpad offers an
unparalleled Ubuntu package building and hosting infrastructure that
no other platform offers. Even simple requirements like building for architectures
like :term:`PowerPC`, :term:`s390x`, or :term:`RISC-V` can not be fulfilled by GitHub 
or similar platforms.

Personal Package Archive (PPA)
------------------------------

Launchpad PPA repositories allow you to build installable Ubuntu packages for multiple
:term:`architectures <Architecture>` and to host them in your own software
:term:`repository <Repository>`. 

Using a PPA is straightforward; you don't need the approval of anyone, therefore users 
have to enable it manually. See how to :ref:`InstallPackagesFromPPA`.

This is useful when you want to test a change, or to show others that a change
builds successfully or is installable. Some people have special permission to
trigger the :term:`autopkgtests <autopkgtest>` for packages in a PPA.

.. tip::

    You can ask in the :term:`IRC` channel ``#ubuntu-devel`` if someone can trigger 
    autopkgtests in your PPA if you don't have the permission.

git-based workflow for the development of Ubuntu source packages
----------------------------------------------------------------

Launchpad hosts a :term:`git-ubuntu` importer service that maintains
a view of the entire packaging version history of Ubuntu :term:`source packages <Source Package>` using
git repositories with a common branching and tagging scheme. The git-ubuntu
:term:`CLI` provides tooling and automation that understands these repositories
to make the development of Ubuntu itself easier.

You can see the web-view of these repositories when you click on the "Code" tab
of any source package on Launchpad, for example, in the
`"hello" source package <https://code.launchpad.net/ubuntu/+source/hello>`_ as
shown in the following screenshot:

.. image:: /images/GitUbuntuRepositoryOfTheHelloPackage.png
   :align: center
   :width: 35 em
   :alt: Screenshot of the Launchpad Code page for the hello source package with an arrow pointing to the Code tab. 

Text markup
-----------

Launchpad has some markup features that you can use when you e.g. report bugs, write comments, create merge proposals.

See the `TODO: add link to new LP docs` reference for more details.

Getting help
------------

If you need help with Launchpad you can choose any of the following methods:

IRC chat rooms
~~~~~~~~~~~~~~

On the ``irc.libera.chat`` :term:`IRC` server you will find the ``#launchpad`` channel, where you
can ask the Launchpad team and the Ubuntu community for help.

Mailing lists
~~~~~~~~~~~~~

If you prefer to ask for help via email, you can write to the
`launchpad-users <https://launchpad.net/~launchpad-users>`_ 
mailing list (``launchpad-users@lists.launchpad.net``).

Ask a question
~~~~~~~~~~~~~~

As mentioned above, Launchpad has a `community FAQ feature <https://answers.launchpad.net/launchpad>`_
(called "Answers") where
you can see other people's questions or ask one yourself. Use can use the *Answers*
feature of the Launchpad project on Launchpad itself.

Report a bug
~~~~~~~~~~~~

If you encounter any bug related to Launchpad, you can submit a bug report to the
:term:`Bug Tracking System` of the Launchpad project `on Launchpad itself <https://bugs.launchpad.net/launchpad>`_.

Staging environment
-------------------

Before new features are deployed to the production environment they get
`deployed to a staging environment <https://qastaging.launchpad.net/>`_ where
the changes can get tested.

You can use the staging environment, to try out Launchpad features.

API
---

Launchpad has a web :term:`API` that you can use to interact with its services.
This makes it easy for developer communities like Ubuntu's to
automate specific workflows.

You can find the reference `documentation for the web API <https://launchpad.net/+apidoc/>`_ on Launchpad.

The Launchpad team even created an :term:`open source <Open Source Software>`
Python library, `launchpadlib <https://help.launchpad.net/API/launchpadlib>`_.

Resources
---------

- `Launchpad home page <Launchpad_>`_
- `The Launchpad software project on Launchpad itself <https://launchpad.net/launchpad>`_
    - `Launchpad bug tracker <https://bugs.launchpad.net/launchpad>`_
    - `Launchpad questions and answers <https://answers.launchpad.net/launchpad>`_
- `Launchpad wiki <https://help.launchpad.net/>`_
- `Launchpad development wiki <https://dev.launchpad.net/>`_
- `Launchpad blog <https://blog.launchpad.net/>`_
