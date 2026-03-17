(mir-other-release)=
# MIR - promoting in other releases

A common case is the need to promote something while it is already in main in
another release. Examples:
- forward: used to be in min in releases N and N+1 - then dropped to universe in N+2, but now is needed again in N+3
- backward: is in main in release N and N+1, but now is also needed in release N-1

For both of these examples the process depends on how much time has passed
and how valid the old review and analysis still is.

If in doubt what is appropriate for your case, please join the
{ref}`MIR team meeting <mir-team-meeting>` and ask.

## Needs a (re-)review

If it turns out that there never was an MIR, or that a lot of the old
assumptions and pre-requisites are no more true this goes the path of
a {ref}`mir-rereview`.

## Fine to pass

The MIR team usually looks out for the following aspects to decide if an
existing MIR still applies:

- Was checked by more or less the same rules as of today
- Prerequisites like adding tests or hardening the software that have been done to get it promoted are present in the target release
- There have been no assumptions as part of the MIR approval which are untrue in the target release
- No massive set of open security issues in this other version
