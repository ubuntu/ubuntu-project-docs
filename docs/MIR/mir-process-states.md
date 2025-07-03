(mir-process-states)=
# Process states

The {ref}`overview <main-inclusion-review>` aims to clarify and provide an easy
simplified entry to the topic. This page on instead outlined the detailed
meaning of all MIR related bug states. That allows to understand the
implications of such states and indicates the next course of action based on
a MIR bugs current state.

```{mermaid}
%% mermaid flowcharts documentation: https://mermaid.js.org/syntax/flowchart.html
%%{ init: { "flowchart": { "curve": "monotoneY", "htmlLabels": true } } }%%
flowchart TD
    %% Styles
    classDef Invisible stroke-width:0,fill:#00000000 

    %% States
    Unassigned["<b><i>1.</i> New / Confirmed¹<br>(unassigned)</b>"]
    AssignedToMirTeamMember["<b><i>2.</i> New / Confirmed¹<br>(assigned to<br>MIR team member)</b>"]
    AssignedToSecurityTeamMember["<b><i>3.</i> New / Confirmed¹<br>(assigned to<br>Security team)</b>"]
    WontFix[["<b><i>7.</i> Won't Fix</b>"]]
    InProgress["<b><i>4.</i> In Progress</b>"]
    FixCommitted["<b><i>5.</i> Fix Committed</b>"]
    FixReleased[["<b><i>6.</i> Fix Released</b>"]]
    Incomplete["<b><i>8.</i> Incomplete</b>"]
    Invalid[["<b><i>9.</i> Invalid</b>"]]

    %% Meta States
    Start((" ")):::Invisible
    BugCreated>"Bug created"]
    IsSecurityReviewNeeded{{"is Security Review needed"}}
    Reviewed{{"Reviewed<br><i>(report added as<br>bug comment)</i>"}}
    QuestionsArise>"Questions or Requests<br>arise"]
    
    %% Transitions
    Start-->|"create MIR bug<br>following the template"| BugCreated
    BugCreated-->|"subscribe Launchpad team<br><code>~ubuntu-mir</code> to the bug"|Unassigned

    Unassigned -->|"triaged at MIR team meeting"| AssignedToMirTeamMember
    AssignedToMirTeamMember --> IsSecurityReviewNeeded -->|"yes"| AssignedToSecurityTeamMember

    IsSecurityReviewNeeded -->|"no"| Reviewed
    AssignedToSecurityTeamMember --> Reviewed
    Reviewed -->|"MIR team NACK"| WontFix
    Reviewed -->|"MIR team ACK"| InProgress

    InProgress -->|"Dependency/Seed change that<br>pulls package(s) into <code>main</code>/<code>restricted</code>"| FixCommitted
    FixCommitted -->|"Archive Admin (AA)</br>promotes package(s)"| FixReleased

    AssignedToSecurityTeamMember --> QuestionsArise
    AssignedToMirTeamMember --> QuestionsArise
    QuestionsArise --> Incomplete
    Incomplete -->|"Questions or<br>Requests resolved"| Unassigned
    Incomplete -->|"no response by the bug<br>reporter/driver within 60 days"| Invalid
```

| State                                                       | Explanation |
|-------------------------------------------------------------|-------------|
| *1.* New / Confirmed[^1] (unassigned)                       | Bug is queued for assignment to an MIR team member |
| *2.* New / Confirmed[^1] (assigned to MIR team member)      | On the TODO list of the assigned MIR team member |
| *3.* New / Confirmed[^1] (assigned to Security team member) | On the TODO list of the Security team member |
| *4.* In Progress                                            | MIR team ACK (and if needed, Security team ACK) done, but now needs the Dependency / Seed change to happen to pull package(s) into `main`/`restricted` |
| *5.* Fix Committed                                          | All of the above done; waiting for an Archive Admin to promote the package(s) to `main`/`restricted` |
| *6.* Fix Released                                           | Case resolved by an Archive Admin |
| *7.* Won\'t Fix                                             | Final NACK from MIR team or bug reporter gave up |
| *8.* Incomplete                                             | Questions / Requests were raised for the bug reporter to resolve / clarify |
| *9.* Invalid[^1]                                            | No response within 60 days when in `Incomplete` state |
| *10.* Invalid[^1]                                           | Not promoted to main by owning-team 2 years after MIR approval |

[^1]: Since many people set Launchpad bugs to `Confirmed` once they verified 
     the validity of a problem, MIR bugs often get set to `Confirmed`. Since 
     `Confirmed` does not have any meaning for our process, we will handle
     `New` and `Confirmed` as if they are the same.


```{note}
All other states are undefined and should be resolved to one of the defined
states -– otherwise they might be completely missed on the weekly checks.
```

```{hint}
Transitioning from *2.*/*3.* to *4.*/*5.*/*8.*: The successor of assigned `New`
states depends *(as seen by multiple arrows in the state diagram)* on the
package(s) current state in the archive: 
* A NACK from the MIR or Security team will result in the `7. Won't Fix` state.
  A former reviewer will get unassigned. (If there is context to believe that 
  there might be a follow up by the reporter the reviewer might remain assigned.)
* In case of an ACK from the MIR team (and, if required the Security team), if 
  the package(s) is/are already tried to be pulled into `main`/`restricted` 
  then the next state is `5. (Fix Committed)`, otherwise the next state is 
  `4. In Progress`. Seen in:
  * [component mismatches for `main`/`restricted`](https://people.canonical.com/~ubuntu-archive/component-mismatches.svg) 
  * [component mismatches for `proposed`](https://people.canonical.com/~ubuntu-archive/component-mismatches-proposed.svg)
```

