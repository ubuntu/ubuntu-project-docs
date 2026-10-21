(sign-ubuntu-code-of-conduct)=
# Sign the Ubuntu Code of Conduct

Signing the [Ubuntu Code of Conduct](https://launchpad.net/codeofconduct) is a
prerequisite for contributing to Ubuntu. It requires a GPG key associated with
your Launchpad account.

Complete the following steps in a Linux terminal.

## 1. Generate and Publish a GPG Key

Generate the key, list it to find the key ID, and publish it to the Ubuntu
keyserver:

```bash
# generate a gpg key
gpg --full-generate-key

# retrieve your key id and fingerprint
gpg --list-secret-keys --keyid-format LONG

# publish your key to the Ubuntu keyserver
gpg --keyserver http://keyserver.ubuntu.com --send-keys <KEY-ID>
```

- Your Key ID is the 16-character hexadecimal string following `rsa4096/`.
- Your Fingerprint is the long 40-character hexadecimal string on the line directly beneath `sec`.

## 2. Import the Key to Launchpad

Copy your full 40-character fingerprint, and go to the [Launchpad OpenPGP Keys Page](https://launchpad.net/~/+editpgpkeys) and add the key's fingerprint. Paste the fingerprint into the **Fingerprint** field and click **Import Key**.

Launchpad will fetch your key from keyserver.ubuntu.com and send an encrypted confirmation email to your registered email address.

## 3. Decrypt the confirmation email from Launchpad

Open the email from Launchpad and copy everything from
`-----BEGIN PGP MESSAGE-----` through `-----END PGP MESSAGE-----` into a text
file, then decrypt it:

```bash
# copy and paste the content of the message to a local text file
vim launchpad-email.txt

# decrypt the message
gpg --decrypt launchpad-email.txt
```

Then find the confirmation URL output in your terminal, and open it in your browser to complete the key verification.

```bash
# find the URL output in the decrypted message
cat launchpad-email.txt
```

## 4. Download and Sign the Code of Conduct

- Visit the [Ubuntu Codes of Conduct](https://launchpad.net/codeofconduct) page.
- Download the latest Code of Conduct document (e.g., `UbuntuCodeofConduct-2.0.txt`)
- Clearsign the file:

```bash
gpg --clearsign UbuntuCodeofConduct-2.0.txt
```

This creates a signed file named `UbuntuCodeofConduct-2.0.txt.asc` in the same directory.

## 5. Submit the signed Code of Conduct

Open UbuntuCodeofConduct-2.0.txt.asc in your terminal:

```bash
cat UbuntuCodeofConduct-2.0.txt.asc
```

Copy the entire contents of the file, including the `-----BEGIN PGP SIGNED MESSAGE-----` header and `-----END PGP SIGNATURE-----` footer.

Return to the [Ubuntu Codes of Conduct](https://launchpad.net/codeofconduct) page, and paste the signed text into the submission box.
