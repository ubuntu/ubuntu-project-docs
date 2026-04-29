(mir-how-to-use-templates)=
# How to use MIR templates

```{include} _mir-series.md
```





As part of {ref}`the MIR process <main-inclusion-review>`, the templates are
used in the same way whether you are reporting or reviewing. Only the templates
themselves are different.

* The **reporter** uses the {ref}`mir-reporters-template`.
* The **reviewer** uses the {ref}`mir-reviewers-template`.

The template should be used as described in the following sections.


## Copy template

Copy the full template into the editor of your choice.

By going through the sections, assessing the `RULEs` and answering the `TODOs`,
you create the content for the MIR request or the review feedback (according to
whether you are a **reporter** or **reviewer**).


## Read the RULEs

Read all the lines starting with `RULE` for all aspects of the MIR.

The `RULE` lines provide additional background, details, options and help with
interpretation If a rule doesn't need explanation, it appears directly as a
`TODO` (so some sections may not have explicitly-stated `RULEs`).


## Assess the TODOs

`TODOs` cover everything we expect from a report. They create concise yet
complete content for each report/review.

### For reporter and reviewer

1. For each line marked with `TODO`:

   * **Fill**: In some lines you can replace placeholders '`TBD`' and '`TBDSRC`' with
     whatever matches your request.

   * **Choose**: In some lines you need to select from mutually exclusive options. For
     example, "link to CVE" or "no security issues in the past". Leave only
     those statements that apply to your case, and remove any others.

     For clarity, such options are marked like *`TODO-A`:, `TODO-B`:, ...*.
     Of those, *usually* only one option remains in the final content.

   * **Remove** the `TODO` prefix when you are sure you have answered a statement.

1. Lines starting with RULE can be removed entirely after you have fully
   processed that section.


### For reviewers only

The **reviewer** will have to judge, therefore, all their statements start in
an `OK:` section.

Any time a violation is found, the statement is moved to the `Problems:` area
and flagged with what is missing/expected.
      
If there are no `Problems:`, just leave the alternative `Problems: None`
for posting the review.


## Open/update the MIR Bug

### The reporter

As a **reporter**, you can now file the MIR bug, with your processed template
as the bug description.

You can, and are encouraged to, always add more details/background that make
the case clearer and more comprehensible.

In case of a single context/reasoning, but multiple packages to promote, please
make a Launchpad bug for each package. One central package may be chosen to
maintain the shared context of related packages. Other packages must be tracked
by and link to the central package.

See the [central Pacemaker MIR](https://bugs.launchpad.net/ubuntu/+source/pcs/+bug/1953341)
as an example.


### The reviewer

As a **reviewer**, you shall add your review as a comment on the MIR bug.
