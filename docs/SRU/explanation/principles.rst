.. _explanation-principles:

Principles
----------

We carefully manage what we change in a stable Ubuntu release for the
following principles:

1. **Minimise regressions**

2. **User confidence**

3. **Maintain usefulness**

A fourth principle is simply to focus on **user experience**, but this
of course applies across Ubuntu and isn't SRU-specific.

.. _explanation-minimise-regression:

Minimise regression
~~~~~~~~~~~~~~~~~~~

Behaviour a user reasonably relies upon that works today must not break
tomorrow as a result of an update. In a stable release, this includes
*any* user interface change! Exception: behaviour that we deem buggy
must necessarily change in order to fix it. [Expand on this]. See `xkcd
spacebar heater <https://xkcd.com/1172/>`_.

In contrast to pre-release versions, official releases of Ubuntu are
subject to much wider use, and by a different demographic of users.
During development, changes to the distribution primarily affect
developers, early adopters and other advanced users, all of whom have
elected to use pre-release software at their own risk.

Users of the official release, in contrast, expect a high degree of
stability. They use their Ubuntu system for their day-to-day work, and
problems they experience with it can be extremely disruptive. Many of
them are less experienced with Ubuntu and with Linux, and expect a
reliable system which does not require their intervention.

Stable release updates are automatically recommended to a very large
number of users, and so it is critically important to treat them with
great caution.

Confidence
~~~~~~~~~~

We must maintain confidence in the stability of our stable releases.
This requires consistent application of policy, documented diligence,
rationale for exceptions, etc. "Headline/outrage avoidance"

What do we mean by stability?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. There's stability as in "things don't crash". That's easy.

2. There's stability as in "things behave in the way that upstream meant
them to behave". This is mostly a superset of "things don't crash".

3. There's stability as in **predictability** - if the user did
something yesterday it will do the same thing today.

We want stability in all three of these senses for the "stable release",
but with a much higher emphasis on the third than in other contexts.

Maintain usefulness
~~~~~~~~~~~~~~~~~~~

We make exceptions to keep the distribution useful. E.g. Firefox,
hardware enablement, Internet protocol [need to expand on this].
