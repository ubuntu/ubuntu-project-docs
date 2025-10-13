.. _howto-handle-autopkgtest-failure:

Handle an autopkgtest failure
-----------------------------

See also: :ref:`Explanation → Autopkgtest failures
<explanation-autopkgtest-failures>`

1. Determine if the failure represents a regression caused by the SRU,
   or if it is a false positive that will not cause a regression if the
   SRU is released to -updates.
2. If this is a real regression, follow :ref:`How-to → Report a
   regression <howto-report-regression>` instead.
3. Submit autopkgtest retries if you consider this appropriate, such as
   if you think the cause of the failure is a flaky test. If this
   resolves the issue, no further action is required.
4. If possible, submit further SRUs into -proposed that resolve the
   issue, such as [TBC]
5. Post an explanation to the relevant bug containing your analysis that
   describes how you arrive at your conclusion that this is a false
   positive.
