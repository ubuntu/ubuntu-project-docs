.. _investigate-halted-phased-update:

Investigate a halted phased update
----------------------------------

See also: :ref:`Explanation → Phasing <explanation-phasing>`

Here are some tips on how to utilize the phased updates report to
investigate why the phasing has stopped.

When looking at an increased rate of crashes you'll want to look at the
crash(es) with the greatest number of occurrences. Then check to see if
the crash is occurring more frequently (by examining the Occurrences
table) with the updated version of the package. If it is then you want
to sort out why and address the crash in a follow on SRU. If it isn't
then :ref:`contact the SRU team <howto-contact>` regarding overriding
the crash.

When looking at a new error you'll want to confirm that the error is in
fact a new one by using the versions table. The phased-updater currently
checks if the error has been reported about the version immediately
before the current version, so if the previous version wasn't around
very long its possible a specific error wasn't reported about it.
Additionally, you can check to see if the error is really about the
identified package or if it occurs in an underlying library by looking
at the Traceback or Stacktrace e.g. python crashes being reported about
a package using python. If you do not believe the error is a new one or
was not caused by your stable release update then :ref:`contact the SRU
team <howto-contact>` regarding overriding the crash.
