(mir-process-states)=
# Process states

The {ref}`overview <main-inclusion-review>` aims to clarify and provide an easy
simplified entry to the topic. This page instead outlines the detailed
meaning of all MIR related bug states. This allows one to understand the
implications of such states and indicates the next course of action based on
an MIR bug's current state.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
%%{ init: { "flowchart": { "curve": "monotoneY", "htmlLabels": true } } }%%
flowchart TD
    %% Styles
    classDef Invisible stroke-width:0,fill:#00000000

    %% States
    ToReview["<b><i>1.</i> New / Confirmed¹<br>(unassigned)</b>"]
    AssignedToMirTeamMember["<b><i>2.</i> New / Confirmed¹<br>(assigned to<br>MIR team member)</b>"]
    AssignedToSecurityTeamMember["<b><i>3.</i> New / Confirmed¹<br>(assigned to<br>Security team)</b>"]
    WontFix[["<b><i>7.</i> Won't Fix<br>(unassigned)</b>"]]
    InProgress["<b><i>4.</i> In Progress<br>(unassigned)</b>"]
    FixCommitted["<b><i>5.</i> Fix Committed<br>(unassigned<br>ubuntu-archive subscribed)</b>"]
    FixReleased[["<b><i>6.</i> Fix Released<br>(unassigned)</b>"]]
    Incomplete["<b><i>8.</i> Incomplete<br>(assigned to<br>the reporter)</b>"]
    Invalid[["<b><i>9.</i> Invalid<br>(unassigned)</b>"]]

    %% Meta States
    Start((" ")):::Invisible
    BugCreated>"Bug created"]

    %% Transitions
    Start-->|"<div style='background:#8BC34A'><i>a)</i> create MIR bug</div>"| BugCreated
    BugCreated-->|"<div style='background:#8BC34A'><i>b)</i> subscribe <code>~ubuntu-mir</code></div>"|ToReview

    ToReview -->|"<div style='background:#4ECDC4'><i>c)</i> triaged by MIR team</div>"| AssignedToMirTeamMember

    AssignedToMirTeamMember -->|"<div style='background:#4ECDC4'><i>d</i>) MIR team ACK</div>"| InProgress
    AssignedToMirTeamMember -->|"<div style='background:#4ECDC4'><i>e</i>) MIR team ACK,<br>Security needed</div>"| AssignedToSecurityTeamMember
    AssignedToMirTeamMember -->|"<div style='background:#4ECDC4'><i>f</i>) MIR team NACK</div>"| WontFix
    AssignedToMirTeamMember -->|"<div style='background:#4ECDC4'><i>g</i>) needs questions/actions</div>"| Incomplete

    AssignedToSecurityTeamMember -->|"<div style='background:#DBB3B1'><i>h</i>) Security ACK</div>"| InProgress
    AssignedToSecurityTeamMember -->|"<div style='background:#DBB3B1'><i>i</i>) Security NACK</div>"| WontFix
    AssignedToSecurityTeamMember -->|"<div style='background:#DBB3B1'><i>j</i>) needs questions/actions</div>"| Incomplete

    Incomplete -->|"<div style='background:#8BC34A'><i>k</i>) questions/actions resolved</div>"| ToReview
    WontFix -->|"<div style='background:#8BC34A'><i>l</i>) situation changes</div>"| ToReview
    InProgress -->|"<div style='background:#8BC34A'><i>m)</i> package(s) pulled into main</div>"| FixCommitted

    FixCommitted -->|"<i>n)</i> Archive Admin</br>promotes package(s)"| FixReleased

    Incomplete -->|"<div style='background:#4ECDC4'><i>o)</i> no response</div>"| Invalid
```

| Index | State               | Assignee / Subscriber                   | State-Explanation |
|-------|---------------------|-----------------------------------------|-------------|
| *1.*  | New / Confirmed[^1] | (unassigned)                            | Bug is queued for assignment to an MIR team member |
| *2.*  | New / Confirmed[^1] | (assigned to MIR team member)           | On the TODO list of the assigned MIR team member |
| *3.*  | New / Confirmed[^1] | (assigned to Security team member)      | On the TODO list of the Security team member |
| *4.*  | In Progress         | (unassigned)                            | MIR team ACK (and if needed, Security team ACK) done, but now needs the Dependency / Seed change to happen to pull package(s) into `main`/`restricted` |
| *5.*  | Fix Committed       | (unassigned, ubuntu-archive subscribed) | All of the above done; waiting for an Archive Admin to promote the package(s) to `main`/`restricted` |
| *6.*  | Fix Released        | (unassigned)                            | Case resolved by an Archive Admin |
| *7.*  | Won\'t Fix          | (unassigned)                            | Final NACK from MIR team or bug reporter gave up |
| *8.*  | Incomplete          | (assigned to the reporter)              | Questions / Requests were raised for the bug reporter to resolve / clarify |
| *9.*  | Invalid[^1]         | (unassigned)                            | No response within 60 days when in `Incomplete` state |

[^1]: Since many people set Launchpad bugs to `Confirmed` once they verified
     the validity of a problem, MIR bugs often get set to `Confirmed`. Since
     `Confirmed` does not have any meaning for our process, we will handle
     `New` and `Confirmed` as if they are the same.

| Index | Transition-Explanation                                             | Responsible to set state and assignee|
|-------|--------------------------------------------------------------------|--------------------------------------|
| *a.*  | Create MIR bug following the template                              | Reporter/Driver                      |
| *b.*  | Subscribe Launchpad team ~ubuntu-mir                               | Reporter/Driver                      |
| *c.*  | Triaged at MIR team meeting                                        | MIR team                             |
| *d.*  | MIR team ACK (report added as comment)                             | MIR team                             |
| *e.*  | MIR team ACK (report added as comment), but security review needed | MIR team                             |
| *f.*  | MIR team NACK                                                      | MIR team                             |
| *g.*  | Needs questions answered or required actions done                  | MIR team                             |
| *h.*  | Security ACK (report added as comment)                             | Security team                        |
| *i.*  | Security NACK (report added as comment)                            | Security team                        |
| *j.*  | Needs questions answered or required actions done                  | Security team                        |
| *k.*  | Questions or requests resolved                                     | Reporter/Driver                      |
| *l.*  | Situation changes, new input given                                 | Reporter/Driver                      |
| *m.*  | Dependency/seed change that pulls package(s) into main             | Reporter/Driver                      |
| *n.*  | Archive Admin promotes package                                     | Archive Admin                        |
| *o.*  | No response by the bug reporter/driver within >=60 days            | MIR team                                     |


```{note}
All other states are undefined and should be resolved to one of the defined
states -– otherwise they might be completely missed on the weekly checks.
```
