(clang-llvm-packaging)=
# `llvm` and `clang` packaging

Besides the guides for LLVM packaging linked below, LLVM package maintenance also requires staying up-to-date with several different communities.

## LLVM Community
- You should join the [LLVM Discourse](https://discourse.llvm.org/), which has replaced most mailing lists for official upstream communication.
- Optional, but useful, is a digest of LLVM changes so that you don't need to follow every Github and Discourse discussion about a new feature. A good one is https://llvmweekly.org/
- Optional, make use of the [LLVM calendar](https://calendar.google.com/calendar/u/0/embed?src=calendar@llvm.org) to see office hours and other learning opportunities.

## Debian Community
- You should be registered on [Debian Salsa](https://salsa.debian.org/) so that you can collaborate with Debian developers.
- Join appropriate Debian mailing lists, including the [one dedicated to the LLVM packaging team](https://alioth-lists.debian.net/cgi-bin/mailman/listinfo/pkg-llvm-team).
- Debian IRC room for LLVM. Since Ubuntu developers already use Matrix, you can join via a Matrix bridge if you like.  Debian provides [instructions](https://wiki.debian.org/IRC/ElementMatrix) which mostly seem to work save joining a channel.  Instead of the suggestion to use `!join`, once you're registered manually join the corresponding Matrix room. For `#debian-llvm` that would be `#_oftc_#debian-llvm:matrix.org`.



```{toctree}
:maxdepth: 1

LLVM Packaging guide <packaging>
Common issues <issues>
```
