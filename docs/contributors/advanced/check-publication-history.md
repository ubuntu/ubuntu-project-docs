(check-publication-history)=
# Check publication history

```{note}
Currently this page only contains checking removals, but we can add other sections as
we find them.
```

(checking-removal-reasons)=
## Checking removal reasons 

Sometimes one might want to double check if something was removed and
asynchronous tools like `rmadison` will not immediately update as they need a
publishing run and then some processing. Instead one could check such via
launchpad API or the web.

Commonly known is the source publishing history, which is also linked from the
package. For example in
[publishing history](https://launchpad.net/ubuntu/+source/libsdl2/+publishinghistory)
you can see automatic and manual removals, but also the effects of a package
going through `-proposed` migration.

Less known is that there also is a binary package publishing history, which you
might want to check if e.g. removing a binary for a single architecture. For
example [in this case](https://bugs.launchpad.net/ubuntu/+source/pdfsandwich/+bug/2092549/comments/5)
which can be seen in effect on
[`https://launchpad.net/ubuntu/plucky/armhf/pdfsandwich`](https://launchpad.net/ubuntu/plucky/armhf/pdfsandwich).

