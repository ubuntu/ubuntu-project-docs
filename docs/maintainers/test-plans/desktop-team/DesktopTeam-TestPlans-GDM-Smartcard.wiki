(GDM-Smartcard-test-plan)=
# GDM smartcard test plan


## GDM SRU smartcard testing

Smartcard login with the various GDM profiles can be simluated using software smartcards, a "simplified" way is to use [these scripts](https://salsa.debian.org/gnome-team/gdm/-/blob/debian/latest/debian/tests/sssd-gdm-smartcard-pam-auth-tester.sh?ref_type=heads) that create certificates and virtual smartcards.

While they should not be destructive by default (as they are designed to restore everything they change at system level), it's recommended to test the scripts in a VM with SSH access so that it's easier to verify the outcome.

```none
sudo apt install softhsm2 pamtester openssl
sudo apt-mark auto softhsm2 pamtester
git clone https://salsa.debian.org/gnome-team/gdm gdm
```

Now in a SSH terminal (or a tty) run:

```none
sudo env PIN=554433 WAIT=1 bash ./gdm/debian/tests/sssd-gdm-smartcard-pam-auth-tester.sh
```

Once `gdm` will be started, it will try the smartcard authentication at first, so type the user name you want to log in with (but only the user that launched the previous command with `sudo` will be the one allowed).

So ensure that the `$SUDO_USER` is the only one allowed to login (and only with the specified PIN number) and that no one else is.

Hitting {kbd}`Enter`, the tool iterates through various GDM smart card configurations (`gdm-smartcard-sssd-exclusive` and `gdm-smartcard-sssd-or-password`), using different kinds of certificates, but in all the cases the `$SUDO_USER` should be allowed to login with Smartcard only or also with password as fallback (in the `gdm-smartcard-sssd-or-password` case).

For what concerns the GDM UI testing, once the first 2 steps have been tested, the test is considered to pass.
