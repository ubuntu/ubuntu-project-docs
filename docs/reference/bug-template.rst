.. _reference-sru-bug-template:

SRU bug template
----------------

::

    [ Impact ]

     * An explanation of the effects of the bug on users and justification
       for backporting the fix to the stable release.

     * In addition, it is helpful, but not required, to include an
       explanation of how the upload fixes this bug.

    [ Test Plan ]

     * detailed instructions how to reproduce the bug

     * these should allow someone who is not familiar with the affected
       package to reproduce the bug and verify that the updated package
       fixes the problem.

     * if other testing is appropriate to perform before landing this
       update, this should also be described here.

    [ Where problems could occur ]

     * Think about what the upload changes in the software. Imagine the
       change is wrong or breaks something else: how would this show up?

     * It is assumed that any SRU candidate patch is well-tested before
       upload and has a low overall risk of regression, but it's important
       to make the effort to think about what ''could'' happen in the event
       of a regression.

     * This must never be "None" or "Low", or entirely an argument as to why
       your upload is low risk.

     * This both shows the SRU team that the risks have been considered,
       and provides guidance to testers in regression-testing the SRU.

    [ Other Info ]

     * Anything else you think is useful to include

     * Make sure to explain any deviation from the norm, to save the SRU
       reviewer from having to infer your reasoning, possibly incorrectly.
       This should also help reduce review iterations, particularly when the
       reason for the deviation is not obvious.

     * Anticipate questions from users, SRU, +1 maintenance, security teams
       and the Technical Board and address these questions in advance
