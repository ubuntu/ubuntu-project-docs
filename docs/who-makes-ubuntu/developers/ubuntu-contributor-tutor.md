(ubuntu-contributor-tutor)=
# Ubuntu contributor tutor

```{include} ../_dmb-series.md
```


The {ref}`patch-pilots` are your continuous helper to get contributions reviewed, but they can't replace a mentor.
A mentor is often the best guide for learning Ubuntu development, but admittedly they can be hard to find.
So if you do not have a mentor, the (AI-based) Ubuntu contributor tutor provided on this page can help to close some of that gap - it can provide independent, self-paced lessons, practice, and feedback.
It complements, rather than replaces, mentors, sponsors, reviewers, and community discussion.

The tutor supports your packaging, policy, processes, and contribution skills acquisition, with Developer Membership Board (DMB) application preparation as one possible mission.
It adapts to your experience, uses current documentation, and combines short lessons with practice and feedback.
Its instructions are a single, provider-neutral file; no tutor-specific installation or `npx` dependencies or any such are needed.

The tutor is not an official readiness assessment or a DMB decision.
AI-generated explanations and feedback can be wrong.
Check the cited sources, and discuss contribution and application decisions with mentors, sponsors, relevant teams, or the DMB.


## Use the tutor

Give this instruction to an AI agent that can fetch web pages and follow their instructions:

```text
Read https://ubuntu.com/project/docs/who-makes-ubuntu/developers/ubuntu-contributor-tutor.instructions and use its instructions to teach me.
```

Web access is required for this invocation and for checking current sources.
For persistent learning records, use an agent with file access. It is recommended to start it in a directory where it may create an `ubuntu-learning` directory with your permission.
Hands-on package work also requires an appropriate local development environment, see {ref}`how-to-set-up-for-ubuntu-development` for basic prerequisites.

If your agent cannot fetch URLs, clone this documentation repository and give it the local path `docs/_extra/who-makes-ubuntu/developers/ubuntu-contributor-tutor.instructions` instead.
The tutor still needs access to current documentation and other online resources, so using a local prompt does not make the complete experience offline.

Do not include secrets or private evidence in the conversation.
Your chosen AI provider processes the material that you paste or upload.
The tutor will prefer public evidence and will ask before external actions such as posting, uploading, or sending messages.
