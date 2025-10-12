To run the {term}`autopkgtests <autopkgtest>` for real, run the following command provided by the [`ppa-dev-tools` snap](https://snapcraft.io/ppa-dev-tools) to get links to all the autopkgtests:

(updating-rust-autopkgtests-url-command)=

```none
$ ppa tests \
    ppa:<lpuser>/rustc-<X.Y>-merge \
    --release <release> \
    --show-url
```

Click all of the links except i386 to trigger the autopkgtests for each target architecture.

Re-run the same `ppa tests ...` command to check the status of the autopkgtests themselves.

The infrastructure can be a little flaky at times. If you get a "BAD" reponse (instead of a "PASS" or "FAIL"), then you just need to retry it.
