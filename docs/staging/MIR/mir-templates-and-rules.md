(mir-templates-and-rules)=
# Templates and rules

It is the task of the **reporter**/**reviewer** to evaluate all the entries
listed in *RULE* sections and, based on that, to answer or adapt all
*TODO* entries to create the content for the MIR request or the review
feedback respectively.

The sum of *RULE* sections is not meant to be complete without the
*TODO* entries. Only when combined do they define the full rules as that allows
to avoid duplication.

On one hand the *TODO* entries shall cover everything we expect from a
report. These shall help to create a concise yet complete content of
each report/review.

On the other hand the *RULE* entries provide additional background,
details, options and interpretation help.

In many cases where rules are rather simple they only appear as *TODO*
as they do not need additional explanation.

The **reporter**/**reviewer** is tasked to use the templates the following way:

1. Copy the full template below into an editor of your choice.

1. Read the lines starting with *RULE* for all aspects of the MIR.

1. For each line marked with *TODO*:

   1. Adapt the line to provide the correct answer matching the package(s) that
      you request.

   1. In some of those lines you'll need to replace placeholders '`TBD`' and
      '`TBDSRC`' with whatever matches your request.

   1. Remove the *TODO* prefix when you are sure you answered a statement.

   1. Some *TODO* lines can just be removed if they do not apply to the case,
      for example if you do not have "additional reasons" to state.

   1. Sometimes, mutually exclusive options are provided like "link to CVE" or
      "no security issues in the past". Leave only those statements that apply.
      To assist the template-user, those alternatives are marked like *TODO-A:,
      TODO-B:, ...*. Of those, one would usually expect only one option to
      remain in the final content.

   1. The MIR team **reviewer** will have to judge, therefore all their
      statements start in an *OK:* section.
      
      Any time a violation is found the statement is moved to the *Problems:*
      area and flagged with what is missing/expected.
      
      If no *Problems:* are present leave just the alternative *Problems: None*
      for posting the review.

1. Remove the lines starting with *RULE* after you have processed them.

1. Eventually all you will have left are the categories *Availability*,
   *Rationale*, etc ... and therein the answers that the MIR process expects

1. You can, and are encouraged to, always add more details/background that make
   the case clearer and more comprehensible.

1. Update the MIR Bug:

   1. **Reporter**: File the MIR bug based on the processed template as the bug
      description.

      In case of a single context/reasoning, but multiple packages to promote,
      please make a Launchpad bug for each package. One central package may be
      chosen to maintain the shared context of related packages. Other packages
      must be tracked by and link to the central package. See the
      [central Pacemaker MIR](https://bugs.launchpad.net/ubuntu/+source/pcs/+bug/1953341)
      as an example.

   1. **MIR team**: Review and add a comment to the bug that contains the review
