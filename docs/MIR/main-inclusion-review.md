(main-inclusion-review)=
# Main Inclusion Review (MIR)

Packages in Ubuntu `main` (and `restricted`) are officially
maintained, supported and recommended by the Ubuntu project.
{term}`Canonical` provides security updates, standard support services, and
certain Service Level Agreement (SLA) guarantees for these packages.

Therefore, special consideration is necessary before adding new packages
to `main` or `restricted`. The {ref}`Ubuntu MIR team <about-mir-role>`
reviews packages for promotion:

* from {term}`universe` to {term}`main`.
* from {term}`multiverse` to {term}`restricted`.

Reviewing packages before they can be promoted is the **Main Inclusion Review
(MIR)** process. The purpose of the MIR process is to avoid mistakes that have
caused issues in the past and ensure the long-term maintainability of the
packages in the Package Archive. 


## MIR process overview

```{toctree}
:maxdepth: 1
:hidden:

mir-roles-and-steps
mir-process-states
```

If we reduce the process to its simplest components, it can be described in
only three steps.

First, the process makes the **reporter** think about the package or packages
they want to own. Then, the **reviewer** checks what is submitted and either
approves or raises issues. Finally, any such issues are resolved by the
**reporter**, and then the process is complete and the package can be promoted. 

This process, and the different participants involved, are outlined in more
detail in {ref}`mir-roles-and-steps`.

::::{card-carousel} 3

:::{card}
:img-background: images/mir-step-1-think.png
:link: mir-step-1
:link-type: ref
:::

:::{card}
:img-background: images/mir-step-2-review.png
:link: mir-step-2
:link-type: ref
:::

:::{card}
:img-background: images/mir-step-3-resolve.png
:link: mir-step-3
:link-type: ref
:::
::::

In reality, things are often more complex than that! We use Launchpad (and the
states of bugs in Launchpad) to track the progress of any main inclusion request
as shown in our more detailed {ref}`mir-process-states` breakdown.


## About the MIR team

To find out more about the team who oversees the MIR process, see our page
{ref}`about the MIR team <about-mir-role>`.

There you will also find information on how to contact them if you have an MIR
in progress, or want to submit one, and what to expect from the team.

(mir-submit-bug)=
## File an MIR bug

The MIR process uses templates for both those submitting a request (reporters)
and those reviewing requests (reviewers). To make the process as smooth as
possible, which benefits everyone, we ask that you
{ref}`familiarize yourself with the process <mir-roles-and-steps>` before
filing a request.

* **Reporters**: to file a request, use the {ref}`mir-reporters-template`.

* **Reviewers**: to review a request, use the {ref}`mir-reviewers-template`.

Whether you are a reporter or a reviewer, new to the MIR process or a seasoned
veteran, we have also prepared additional guidance on
{ref}`how to use the templates <mir-how-to-use-templates>` to make the task of
filling out the template as straightforward as possible.


## MIR special cases

Some packages have reasons not to follow the standard MIR process. This section
provides details on these and exceptions.

### Exceptions

```{toctree}
:maxdepth: 1

mir-exceptions-fonts
mir-exceptions-oem
```

### Deviations from the norm

Sometimes cases are special and do not follow the normal procedures, those are
outlined here.

```{toctree}
:maxdepth: 1

mir-rereview
mir-rust
```





