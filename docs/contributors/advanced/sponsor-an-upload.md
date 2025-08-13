(sponsor-an-upload)=
# How to sponsor an upload

Members of the {term}`Ubuntu Sponsors` and {term}`Ubuntu Security Sponsors`
teams have the right to sponsor patches or new packages. If you are interested
in {ref}`sponsoring <sponsorship>`, and have gained upload rights, you can
apply to join these teams.

See {ref}`path-to-upload-rights` for details on how to apply for upload rights.


(sponsor-a-package)=
## Sponsor a package

This is similar to uploading your own `.changes` file, except that after
ensuring that the upload follows all quality standards, you will sign the
content of the proposing person with your key.

To achieve that, the tools used in package build (like `dpkg-buildpackage`
and `debsign`) need to be told to use your key. Otherwise these tools would
identify the person referred to in the changelog stanza (the person who
{ref}`requested sponsorship <find-a-sponsor>`), and try to sign with their key
instead.

To define the key you want to be used for signing you can:

* Set the environment variable `DEB_SIGN_KEYID` (see the
  {manpage}`dpkg-buildpackage(1)` manual page for more details)
* Or, where desired, add the argument `-k${GPGKEY}` -- assuming you have your
  key stored in that variable and in long (>=16) format.

