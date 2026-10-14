(changes-file-headers)=
# Changes file headers

git-ubuntu understands the following custom changes file headers:

`Vcs-Git`
: Points to the git repository where the rich history can be found.

`Vcs-Git-Ref`
: The ref which when fetched contains the rich history.

`Vcs-Git-Commit`
: The commit hash of your rich history. This must match your upload.

When git-ubuntu imports your upload, it will look in the location specified by
these headers for the rich history. If present and if they match your upload,
then it will use your commit instead of synthesizing its own.

For now, only Launchpad git URLs are accepted to avoid the risk from a
malicious git repository host. `git-ubuntu prepare-upload` will check
that the URL will be acceptable.
