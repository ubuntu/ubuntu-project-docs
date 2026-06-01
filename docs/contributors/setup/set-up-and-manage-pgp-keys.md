(set-up-and-manage-pgp-keys)=
# Set up and manage PGP keys

In this page, we outline how to set up and use PGP keys to fulfil the policies
and goals outlined in {ref}`pgp-key-storage` for usage in the Ubuntu project.

## Outcome

The high level goal is to keep private key material **off disk** and use hardware keys for day-to-day operations.

1. One long-term **primary key** (C), used only to certify subkeys and locked away in a safe place
2. Multiple **signing subkeys** (S) used for signing (one per YubiKey)
3. One **encryption subkey** (E) used for encryption on all YubiKeys
4. Subkeys only stored on a YubiKey (smartcard) – not on disk
5. A fallback plan in case one YubiKey is lost, expired or compromised
6. Works with Launchpad/Ubuntu uploads, signed git commits and encryption


## Prerequisites

### Hardware

You need one YubiKey per subkey. The YubiKey(s) must support OpenPGP.

(gpg-prerequisites-packages)=
### Packages

Install the following packages:

```shell
sudo apt update
sudo apt install -y gnupg scdaemon pcscd
sudo systemctl enable --now pcscd.socket
```

### GnuPG

[GnuPG](https://gnupg.org/) is an encryption tool that helps manage your {term}`encryption keys <Signing Key>`. You’ll need it later to be able to add a {term}`signature <Signature>` to each {ref}`upload <uploading-to-the-archive>`.

Eventually the {term}`private key <Signing Key>` will represent your identity and therefore must be {ref}`kept safe <pgp-key-storage>` and out of reach of other entities.

It is **best practice** to generate the primary key on an *offline* machine (or at least an offline session) and only use it to create/rotate subkeys. Using a Ubuntu Live image is also a great option as the system is ephemeral and no key will remain on disk once this process is completed.

If that’s too heavy, you can still do this on your main machine, but make sure to clear all keys from your hard drive before you get back online and **treat the backup step as non-negotiable**.


## Step by Step instructions

The following sections will guide you through creating a primary key and
putting the associated subkeys onto hardware keys. After these steps follows
a section about {ref}`pgp-key-day-2-operations`.

### Step 1 — Create the primary key

If you already have a primary key you can skip this step.

```shell
gpg --expert --full-generate-key
```

Pick your key type:

* Type: (9) ECC (sign and encrypt) (or RSA 4096 if you have strict compatibility needs)
* For ECC: Curve 25519 is a common modern choice

Now you must:

* Set an expiration (e.g., 1–2 years) — you can extend this later
* Set a passphrase to protect your primary key

List your keys:

```none
>gpg --list-secret-keys --keyid-format=long
gpg: checking the trustdb
gpg: marginals needed: 3  completes needed: 1  trust model: pgp
gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
gpg: next trustdb check due at 2031-02-02
------------------------
sec   ed25519/1234567890ABCDEF 2026-02-03 [SC] [expires: 2031-02-02]
      1234567890ABCDEF1234567890ABCDEF123456
uid                 [ultimate] Foo Bar <foo.bar@company.com>
uid                 [ultimate] Some One <some.1@gmail.com>
ssb   cv25519/DEADBEEFDEADBEEF 2026-02-03 [E] [expires: 2031-02-02]
```

For the further steps in this how-to export the fingerprint into an environment variable (replace with yours):

```
export KEYFPR="YOUR_PRIMARY_KEY_FINGERPRINT"
```

The primary key fingerprint in the previous example is: `C272017B1AC7539AFC0E6DBCAA7EED1BC821DF7D`

```{important}
If \- for now \- you only wanted to create the software key and do not intend to use individual subkeys and hardware keys you may jump to section {ref}`make-your-keys-known` and then be done for now.
```


(pgp-step-2-add-subkeys)=
### Step 2 — Add subkeys

This section shows how to create Signing and Encryption subkeys using the `gpg` tool:

**2.1 Add a signing subkey**

```shell
gpg --expert --edit-key "$KEYFPR"
```

Inside the `gpg>` prompt, add your subkey using:

```none
gpg> addkey
```

- Pick `ECC (sign only)`
- Select curve type: `Curve 25519` (default as of now)
- Set expiration (refer to {ref}`pgp-expiration-dates-and-regular-key-audits`)

If you want to set up multiple redundant YubiKeys (allow {ref}`different expiration <pgp-expiration-dates-and-regular-key-audits>`, allow individual revocation), add another signing key in the same way.

**2.2 Add an encryption subkey**

You can use the same `addkey` command to create an encryption subkey.

- Pick `ECC (encrypt only)`
- Select curve type: `Curve 25519` (current default)
- Set expiration (refer to {ref}`pgp-expiration-dates-and-regular-key-audits`)

**2.3 Save and verify subkeys**

```none
gpg> save
```

Then verify – ensure you have `S`, `C` and `E` entries:

```shell
gpg --list-secret-keys --with-subkey-fingerprint --keyid-format=long "$KEYFPR"
```

This output shows something like:

```none
sec   ed25519/1234567890ABCDEF 2026-02-03 [SC] [expires: 2031-02-02]
      1234567890ABCDEF1234567890ABCDEF123456
uid                 [ultimate] Foo Bar <foo.bar@company.com>
uid                 [ultimate] Some One <some.1@gmail.com>
ssb   cv25519/DEADBEEFDEADBEEF 2026-02-03 [E] [expires: 2031-02-02]
      DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBE
ssb   ed25519/CAFEBABECAFEBABE 2026-02-03 [S] [expires: 2029-02-02]
      CAFEBABECAFEBABECAFEBABECAFEBABECAFEBA
ssb   ed25519/FAFABABAB0B0B0B0 2026-02-03 [S] [expires: 2028-02-02]
      FAFABABAB0B0B0B0FAFABABAB0B0B0B0FAFABA
```

Which includes:

- A primary key that can be used for signing or certifying the identity of the key chain (SC)
- One subkey for encryption \[E\]
- And two additional subkeys for signing \[S\]

(make-your-keys-known)=
### Step 3 - Make your new key(s) known

If your key is entirely new, or you hereby added additional keys after already uploading the key to the Ubuntu keyserver in the past – you will need to re-upload, otherwise Launchpad will silently reject uploads signed with the (sub)keys.

Use the following command to ensure your public key is uploaded to the Ubuntu keyserver.

```shell
gpg --keyserver hkps://keyserver.ubuntu.com --send-keys "$KEYFPR"
```


### Step 4 — Backup

```{important}
Do this before touching the YubiKey!

This is the part that saves you later.
```

Export your public key:

```shell
gpg --armor --export "$KEYFPR" > /path/to/your/backup/public-key.asc
```

Export your secret keys (primary \+ subkeys):

```shell
gpg --armor --export-secret-keys "$KEYFPR" > /path/to/your/backup/secret-key.asc
```

Generate a revocation certificate:

```shell
gpg --output /path/to/your/backup/revocation.asc --gen-revoke "$KEYFPR"
```

Finally, store these backups **offline** and **encrypted** and remove them from your system.
We acknowledge that this leaves the details of that backup setup intentionally underspecified.
Having any setup that is truly offline and encrypted will in most places be better than what
has been used before.
Here variety is ok and there likely is not only "one right setup", over time
we might add more examples here for your inspiration:

- Multiple (failsave for HW issues, stored in two places) USB thumbdrives (offline), using {manpage}`cryptsetup(8)` (encrypted) to be mounted


(pgp-step-prepare-the-yubikey)=
### Step 5 — Prepare the YubiKey

Insert the YubiKey and verify it is visible. Make sure you have only one YubiKey inserted at a time.

Check if GPG recognizes the YubiKey:

```none
gpg --card-status

Reader ...........: 1050:0407:X:0
Application ID ...: D2760001240100000006349698960000
Application type .: OpenPGP
Version ..........: 3.4
Manufacturer .....: Yubico
Serial number ....: 12345678
Name of cardholder: [not set]
Language prefs ...: [not set]
Salutation .......:
URL of public key : [not set]
Login data .......: [not set]
Signature PIN ....: not forced
Key attributes ...: rsa2048 rsa2048 rsa2048
Max. PIN lengths .: 127 127 127
PIN retry counter : 3 0 3
Signature counter : 0
KDF setting ......: off
UIF setting ......: Sign=off Decrypt=off Auth=off
Signature key ....: [none]
Encryption key....: [none]
Authentication key: [none]
General key info..: [none]
```

If the output says “No such device”, try restarting `gpg-agent`:

```shell
gpgconf --kill gpg-agent
```

Set OpenPGP user info (name/login/url) via:

```shell
gpg --edit-card
```

In the  `gpg\>` prompt you should use the following commands in this order:

```none
admin    - Toggle the usability of privileged commands in this session
passwd   - Set your own admin pin (defaults to 12345678)
passwd   - Set your own standard pin (defaults to 123456)
name     - Set who you are
url      - Set your key's keyserver url for obtaining public key
           like https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x$KEYFPR
uif 1 on - Require touch action for signing
uif 2 on - Require touch action for encryption/decryption
quit
```

These steps set touch interaction for signing and decryption, to protect against
attackers who may have control of your system so they cannot sign something
without your knowledge.

The default already requires the user pin on first usage after the key
has been plugged in, but only once. `gpg> forcesig` can change that to be
always required if you prefer that (less comfort, more security).


```{important}
To prepare a second YubiKey, repeat {ref}`pgp-step-prepare-the-yubikey` with another YubiKey plugged into the system.
```


### Step 6 – Move subkeys to YubiKey

First, you need to move the signing subkey to the signature slot.
Open the key editor, which will start listing the keys:

```none
gpg --edit-key "$KEYFPR"

Secret key is available.

sec  ed25519/1234567890ABCDEF
     created: 2026-02-03  expires: never       usage: SC
     trust: utlimate      validity: unknown
ssb  cv25519/DEADBEEFDEADBEEF
     created: 2026-02-03  expires: 2031-02-02  usage: E
ssb  ed25519/CAFEBABECAFEBABE
     created: 2026-05-14  expires: 2028-05-13  usage: S
ssb  ed25519/FAFABABAB0B0B0B0
     created: 2026-05-14  expires: 2027-08-07  usage: S
[ultimate] (1). Foo Bar <foo.bar@company.com>
[utlimate] (2)  Some One <some.1@gmail.com>
```

Select a key. From the previous example, keys are listed in order,
starting from 0\. To pick the first listed signing key in this example:

```none
gpg> key 2
```

This toggles the selection of subkeys – the selected ones will now show a `*`.

If needed do further (un)select actions with the “key” command to match your needs,
this guide assumes you selected one signing subkey, then:

```none
gpg> keytocard
```

Choose the slot:

* **Signature**

You will be asked for the passphrase of your primary key as well as the admin pin of the hardware key.

Since we want the signing key to only be present on the hardware, issue `save` which **will remove it from the local keyring**.

```none
gpg> save
```

Listing your secret keys will now show that it has been moved to the card represented by `>` after the subkey.

```none
gpg --list-secret-keys --with-subkey-fingerprint
...
ssb>  ed25519 2026-05-14 [S] [expires: 2028-05-13]
      DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF
      Card serial no. = 0006 12345678
```

Next, move the encryption subkey to the encryption slot.

Start over with `gpg --edit-key` again, select the encryption subkey (e.g., key 1),
then chose the Encryption slot.

```{important}
After moving, you will be prompted again to save changes.
**DO NOT SAVE**, since this will delete the encryption key stored in your computer.
We want to keep the encryption key around to use the same one on every hardware key.
```

```none
$ gpg --edit-key "$KEYFPR"
gpg> key 1
# Make sure the key with "usage: E" is selected
gpg> keytocard
# Choose slot Encryption key
gpg> 2
# Leave the tool
gpg> quit
# It should look like this:
# Save changes? (y/N) n
# Quit without saving? (y/N) y
```

```{important}
To handle a second hardware key, run through the steps in this section again with the other hardware key plugged into your system.

At the step of transferring the signing key (Where you selected the first subkey when doing the first iteration of the steps), please select the second signing subkey this time. Combined with the different expiration dates, this ensures they will not both expire at the same time.
```

(step-7-remove-your-keys-from-the-system)=
### Step 7 — Remove your keys from the system

```{important}
Before you go on, ensure that you stored the backups created in step 3 in a safe location.
```

Now that you have two hardware keys (one signature subkey each, and both with the same for encryption) it is time to remove the key material from your local keyring. After that, and after you moved your backups to a safe place – no secret key material will remain on the system itself.

```shell
gpg --delete-secret-keys "$KEYFPR"
```

List your secret keys again to verify they are all known, but not present on the system anymore.

The following output shows:

- The primary key with `#` as (`sec#)` which marks it as offline and not usable.
- Subkeys marked with `>` like (`ssb>)` which marks them as being stored on a smartcard.

```none
$ gpg --list-secret-keys --with-subkey-fingerprint
/home/youruser/.gnupg/pubring.kbx
---------------------------------------------------------
sec#  ed25519 2026-02-03 [SC]
      1234567890ABCDEF1234567890ABCDEF123456
uid                 [ultimate] Foo Bar <foo.bar@company.com>
uid                 [ultimate] Some One <some.1@gmail.com>
ssb>  cv25519 2026-02-03 [E] [expires: 2031-02-02]
      DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBE
      Card serial no. = 0006 12345678
ssb>  ed25519 2026-05-14 [S] [expires: 2028-05-13]
      CAFEBABECAFEBABECAFEBABECAFEBABECAFEBA
      Card serial no. = 0006 12345678
ssb>  ed25519 2026-05-14 [S] [expires: 2027-08-07]
      FAFABABAB0B0B0B0FAFABABAB0B0B0B0FAFABA
      Card serial no. = 0006 12345678
```

### Step 8 — Git commit signing

First, you need to configure Git. To enable signing git commits, set the `commit.gpgsign` option.
Either per repository:

```shell
git config commit.gpgsign true
```

Or globally:

```shell
git config --global commit.gpgsign true
```

If you have more than one primary key with the same UID (username and mail), you can specify which key to use for signing.

```shell
git config --global user.signingkey "$KEYFPR"
```

If you want to sign a single commit:

```shell
git commit -S
```

Test commit signing:

```shell
cd $(mktemp -d)
git init
git commit -S -m "test signed commit" --allow-empty
git log -1 --show-signature
```

You should see: **Good signature**.

Finally, verification.

Do not forget to upload your public key in the different Git servers hosting your work. This shows how you can do it for GitHub:

```shell
gpg --armor --export "$KEYFPR"
```

Copy/paste into GitHub → Settings → SSH and GPG keys.


### Step 9 — Launchpad and Ubuntu upload signing

Ensure Launchpad knows about your public key to associate your username, and thereby its permissions, with your signed uploads: [https://launchpad.net/\~](https://launchpad.net/~)\<your-launchpad-username\>/+editpgpkeys.

After building a package, you can sign the `.changes` file using `debsign.`

```shell
debsign <filename>_source.changes
```

It will determine the signature needed from the email in the changelog stanza.
If this does not work out of the box, you might need to explicitly configure your signing key by exporting the `DEBSIGN_KEYID="$KEYFPR"`.

You can try uploading a package to a PPA {ref}`as described in the project documentation <how-to-upload-packages-to-a-ppa>` using the key associated with your Launchpad account.


(pgp-key-day-2-operations)=
## Day 2 operations

This section covers some critical operations that you might need to look into
some time later, some of which require the use of your backup of these keys.

### Let another system use the same keys

You received your new computer and want to import your key.

There is no need to copy private keys, they move with the hardware keys now plugged in here.

First install the {ref}`packages mentioned in the prerequisites <gpg-prerequisites-packages>`.

Then plug in the YubiKey and check if it is detected:

```shell
gpg --card-status
```

This should be the same as what you saw when setting up the hardware key.

You can import your key automatically using the URL you set on your YubiKey at setup time.
Or get it from the keyserver directly by specifying which key you need.

Import via the YubiKey's stored URL:
```shell
gpg --edit-card
gpg> fetch
```

It should show:

```none
# gpg: requesting key from 'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x$YOURKEY'
# gpg: key DEADBEEFDEADBEEF: public key "Your Name <yourname@example.com>" imported
# gpg: Total number processed: 1
# gpg:               imported: 1
```

Otherwise import the `.asc` public key you backed up, and run:

```shell
gpg --import /path/to/your/backup/public-key.asc
```

Verify that your keys have been imported:

```shell
gpg --list-keys
```

Trust yourself (well, your key):

```none
gpg --edit-key "$KEYFPR"
gpg> trust
# 5 = I trust ultimately
gpg> 5
# Do you really want to set this key to ultimate trust? (y/N)
gpg> y
gpg> quit
```

To confirm keys are loaded and working correctly try signing with them:

```shell
echo "Ubuntu is awesome" | gpg --clearsign
```


### Updating expiration dates

This section shows how to extend the expiration date of the different keys.
To update the expiration date, you must have access to the private keys, so first import the secret keys from the backup file.

We should avoid interacting with the usual GPG keyring by temporarily creating a new one to do this operation.
This makes the whole process simpler, since you won’t need to remove the secret keys after updating the expiration date.

```shell
export GNUPGHOME="$(mktemp -d -t gnupg-XXXXXXXX)"
export KEYFPR="YOUR_PRIMARY_KEY_FINGERPRINT"

# Import the key
gpg --import /path/to/your/backup/secret-key.asc
gpg --edit-key "$KEYFPR"
```

This lists the keys:

```none
Secret key is available.

sec  ed25519/1234567890ABCDEF
     created: 2026-02-03  expires: never       usage: SC
     trust: ultimate      validity: unknown
ssb  cv25519/DEADBEEFDEADBEEF
     created: 2026-02-03  expires: 2031-02-02  usage: E
ssb  ed25519/CAFEBABECAFEBABE
     created: 2026-05-14  expires: 2028-05-13  usage: S
ssb  ed25519/FAFABABAB0B0B0B0
     created: 2026-05-14  expires: 2027-08-07  usage: S
[ultimate] (1). Foo Bar <foo.bar@company.com>
[utlimate] (2)  Some One <some.1@gmail.com>
```

In the `gpg>` prompts then:

```none
# 1. Extend the primary key if needed (default selected)
gpg> expire
# enter duration (e.g. 1y)
1y
# Repeat to update expiration for other subkeys (key 2, key 3, etc.)
gpg> key 2
gpg> expire
1y
# after updating all keys, save and exit
gpg> save
```

Since we are operating under a temporary `GNUPGHOME`, don't forget to export
the updated public key as your new backup.

```shell
gpg --armor --export "$KEYFPR" > /path/to/your/backup/public-key.asc
```

Now we can safely delete the temporary `GNUPGHOME` and import the updated public key to the real local keychain.

```shell
rm -rf "$GNUPGHOME"
unset GNUPGHOME
gpg --import /path/to/your/backup/public-key.asc
```

Then, upload the updated key to the keyserver as shown in {ref}`make-your-keys-known`.

### If a subkey is compromised

If you followed this guide, then your keys should be safely locked away and backed up, and if only a subkey is compromised, we can use the primary key to generate new subkeys.

Do this the instant you are able\! The longer you wait, the longer anyone with access to your compromised key can sign things on your behalf\!

Import the backup keys as documented in the previous section.
List the imported keys and extract the primary key fingerprint:

```shell
gpg --list-secret-keys
export KEYFPR="YOUR_PRIMARY_KEY_FINGERPRINT"
```

Now edit, select and revoke the compromised/lost subkeys:

```shell
gpg --edit-key "$KEYFPR"
```

Then select the subkey (by index) and revoke it:

```{important}
Warning - this is an irreversible action\!
```

```none
gpg> key $SUBKEY_INDEX
gpg> revkey
```

Save your changes and *immediately* upload to any keyserver(s) to which you previously used your key following the steps of {ref}`make-your-keys-known`.

After doing that repeat steps {ref}`pgp-step-2-add-subkeys` to {ref}`step-7-remove-your-keys-from-the-system`, to create new subkeys to replace the revoked ones on your hardware keys.

### If the primary key is compromised

In this case, you should revoke the entire key using the revocation certificate generated in the backup step.
To do this, acquire your previously generated and backed up revocation certificate and upload it to the keyserver(s):

```{important}
Warning - this is an irreversible action\!
```

```shell
gpg --import /path/to/your/backup/revocation.asc
gpg --keyserver hkps://keyserver.ubuntu.com --send-keys "KEYFPR"
```
