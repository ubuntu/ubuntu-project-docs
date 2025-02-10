:relatedlinks: [Diátaxis](https://diataxis.fr/)

.. _home:

SRU documentation
=================

.. A single sentence that says what the product is, succinctly and
   memorably.

Once an Ubuntu release has been completed and published, updates for it
are only released under certain circumstances, and must follow a special
procedure called a *stable release update* (SRU).

.. A paragraph of one to three short sentences, that describe what the
   product does.

.. A third paragraph of similar length, this time explaining what need the
   product meets.

This documentation describes the principles and processes we follow in
order to keep stable Ubuntu releases stable.

.. Finally, a paragraph that describes whom the product is useful for.

Our documented principles are intended to be read by all Ubuntu users if
they wish to understand what to expect from Ubuntu stable releases, and
are for upstream and Ubuntu developers to read if they wish to
understand what changes would or would not be acceptable to us. The rest
is intended for Ubuntu developers and SRU team members to achieve this
in practice.

Did you **notice a regression** in a package which went to ``-updates``?
Please report this using :ref:`these steps <howto-report-regression>`.

---------

In this documentation
---------------------

.. grid:: 2

   .. grid-item-card:: :doc:`How-to guides <howto/index>`
      :columns: 12
      :link: howto/index
      :link-type: doc

      **Step-by-step guides** covering key operations and common tasks

.. grid:: 2
   :reverse:

   .. grid-item-card:: :doc:`Reference <reference/index>`
      :columns: 6
      :link: reference/index
      :link-type: doc

      **Technical information** - specifications, APIs, architecture

   .. grid-item-card:: :doc:`Explanation <explanation/index>`
      :columns: 6
      :link: explanation/index
      :link-type: doc

      **Discussion and clarification** of key topics

---------

Project and community
---------------------

-  `Read our code of
   conduct <https://ubuntu.com/community/ethos/code-of-conduct>`__: As a
   community, we adhere to the Ubuntu code of conduct.

-  `Get
   support <https://askubuntu.com/questions/tagged/stable-release-updates>`__:
   Ask Ubuntu is a question and answer site for Ubuntu users and
   developers.

-  `Join our online
   chat <https://web.libera.chat/gamja/?channels=%23ubuntu-devel>`__: Meet us
   in ``#ubuntu-devel`` on IRC Libera.Chat.

-  `Report bugs <https://bugs.launchpad.net/sru-docs/+filebug>`__: We
   want to know about the problems, so we can fix them.

-  `Contribute docs <https://launchpad.net/sru-docs>`__: The docs
   sources in Launchpad.

.. toctree::
   :hidden:
   :maxdepth: 2

   explanation/index
   howto/index
   reference/index
   internal
