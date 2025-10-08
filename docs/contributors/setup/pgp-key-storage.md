(pgp-key-storage)=
# PGP Key Recommendations

# Introduction

The Ubuntu Project relies heavily on PGP keys for critical operations. These
serve to authenticate individuals, sign uploads to the Ubuntu Archive and
Personal Package Archives (PPAs), and facilitate confidential communication.
Given their multifaceted utility and integral role in maintaining the integrity
and security of the project, PGP keys are consequently high-value targets for
malicious attacks.

# Overview

| Key Security Practice | Description |
| :---- | :---- |
| {ref}`pgp-strong-passphrases` | Use long, complex, and unique passphrases for PGP keys. |
| {ref}`pgp-hardware-security-keys` | Use devices like YubiKeys for PGP key workflows. |
| {ref}`pgp-encrypted-offline-storage` | Maintain encrypted offline storage of the main PGP key in a safe place. |
| {ref}`pgp-redundant-hardware-keys` | Configure two identical hardware keys to prevent single points of failure. |
| {ref}`pgp-expiration-dates-and-regular-key-audits` | Use an expiration date, and on renewal, review your key security practices. |
| {ref}`pgp-control-and-ownership` | Control and ownership of cryptographic keys. |

Please be aware that {ref}`pgp-these-policies-are-not-static` and require to follow a set of complex {ref}`pgp-setup-guidelines`.

(pgp-strong-passphrases)=
## Strong passphrases

For many years, project members have been encouraged to protect their PGP keys
with strong passphrases. While passphrases are recommended to provide a
foundational layer of security, their effectiveness as a sole defense mechanism
becomes questionable with the increasing availability of computational power
capable of brute-forcing even complex passphrases.

Practical recommendations all derive from the entropy given by the passphrase:
* These passwords do not need to be super comfortable as they are for the main
  key, following the guidance of using {ref}`pgp-hardware-security-keys` and
  sub-keys you will not need it for daily use.
* If you prefer memorability: use 6+ [Diceware words](https://en.wikipedia.org/wiki/Diceware)
  (or a memorable sentence of 20–30 characters).
* If you use a password manager/generator: create a random 16+ character password (include upper/lower/digits/symbols).
* Never reuse the passphrase for other accounts.
* If you store the private key and its passphrase, please do so separately in secure locations (sorry - outlining that would be an even more complex document, probably only able to list good and bad examples).

(pgp-hardware-security-keys)=
## Hardware Security Keys

To mitigate the elevated risks associated with a compromised PGP key, the Ubuntu
Project strongly encourages, though does not strictly mandate, the adoption of
hardware security keys that support PGP operations. Devices such as some
YubiKey models, designed with secure elements, offer a significant enhancement
to purely file-based PGP key protection. We are not selecting a particular
manufacturer like Yubikey or model, alternatives like
[TKey](https://www.tillitis.se/products/tkey/) are just as valid. Check their
capabilities against the recommended setup outlined here when selecting one.

The primary benefits of using hardware security keys include:

* **Reduced Accessibility:** By storing the PGP key on a dedicated hardware
  device, its accessibility is significantly reduced. This offers a more robust
  defense even if the host system where the key is typically used is compromised
  by an attack or subject to potential access from others
* **Controlled Access:** Hardware security keys prevent unauthorized access to
  the PGP key, ensuring that only individuals with physical possession of the
  device and knowledge of any associated unlock mechanisms can perform PGP
  operations. This adds a crucial layer of control over who can manage and use
  the key.

By generating subkeys (see below) directly on the hardware key you furthermore
gain the ability to create an
[attestation certificate](https://developers.yubico.com/PGP/Attestation.html).
Such a certificate can be published by you to allow verification of your key by
third-parties.

It furthermore is recommended to configure the key for user-presence, in
combination with attestation `Fixed` is the suggested
[touch policy](https://docs.yubico.com/software/yubikey/tools/ykman/OpenPGP_Commands.html#touch-policies).

(pgp-encrypted-offline-storage)=
## Encrypted Offline Storage

A typical setup would usually consist of a locked-away, offline, main PGP key
("Certify key") generated in software, and derived from that subkeys deployed
on the hardware security keys that are used for regular operations.
That encrypted offline main PGP key is then the final safeguard to recover,
but also has no need to be comfortable or quick to reach and hence can make
use of various extra levels of protection against physical and digital attacks.

To make an example what such extra protection could be like: When the key is
generated or in the rare cases it is later needed, for example
to generate new subkeys, it is suggested to do so on an offline (no network)
live (boot from trusted unmodified medium) system and never use the associated
passphrase on any other system.

(pgp-redundant-hardware-keys)=
## Redundant Hardware Keys

To further enhance the resilience of PGP key management and mitigate the risk of
single points of failure, it is recommended to set up and utilize two hardware
security keys configured with subkeys of the same key set up on both devices.
This redundancy ensures continued access to credentials even if one hardware
security key fails, which could be particularly critical if a developer
is traveling.

In general, such redundancy is especially important for the non-PGP use cases of
hardware security keys, like FIDO2/WebAuthn. Since in such cases the keys are
generated using the on-chip HSM, you would not have a software copy. Therefore
it's recommended to keep one key in a safe location, e.g. do not keep the pair
on the same keychain as they would be affected by the same disaster.

(pgp-expiration-dates-and-regular-key-audits)=
## Expiration dates and Regular Key Audits

There are no mandated PGP key expiration dates yet, but a common good security
practice is to set a regular, short expiration date, such as 1 to 2 years, with
the two enrolled hardware tokens having expirations offset by at least 3 months
(to avoid getting locked out from both keys expiring at once). You can do this
by setting up subkeys for signature/encryption/authentication, which can have
individual expiry dates.

It is not important to set an expiration on the offline main PGP key, as it
could easily be used to extend its own expiration date. But on sub-keys this
can be very effective and recommended.
The use case as {term}`signing keys <Signing Key>` is point-in-time action
anyway, but if sub-keys are used for encryption/decryption communication, for
example in confidential mail exchanges - then you would usually want to be able
to use that sub-key for as long as you want/need to be able to decrypt whatever
was encrypted by others for you.
In case of a sub-key used for such communication has expired but is still
needed, its expiration meta data can updated be via your ongoing control
of the main key.

The somewhat regular refreshing of expiration dates is also a great anchor
point to have users revisit the setup and current policies.
They further act as a "dead man's switch" to prevent permanent use of
compromised or forgotten subkeys.

Other than time and expiration a key can also be withdrawn by using a
revocation certificate. To be able to do so in case it is needed it can be
good preparation to generate such a certificate right away. This shall be
stored as safe as the main key, because it is rarely needed and there is the
risk that anyone with access could publish it.

(pgp-control-and-ownership)=
# Control and ownership of cryptographic keys

The Ubuntu developer as an individual is the only person authorised by
Ubuntu Project and is therefore expected to have exclusive control of the
{term}`Signing Key`. It is identifying the developer as an individual - Not a
role, not a Ubuntu team membership nor a company team membership.

Therefore the goal for the developer is to be in sole control and ownership of
the hardware key, knowledge of the passphrase and control of the systems it is
plugged into. Hardware keys are beneficial in this case as they can help to
avoid exfiltration if compromised and furthermore allow to separate ownership
of the computer from that of the hardware key.

Still users need to remain vigilant against sophisticated attacks despite the
use of hardware keys. An attack vector can be to subtly alter or present
misleading information during signing operations. Always try to independently
verify the content being signed, even when using a hardware key, to ensure it
precisely matches the intended data and is free from malicious alterations.

(pgp-these-policies-are-not-static)=
# These policies are not static

While not strictly mandatory yet, project members of any level are advised to
explore all key security practices outlined above into their workflow for PGP
operations. If you are an active member of the project and accrue more elevated
permissions over time, then following those practices should be considered even
more important for you.

We furthermore expect to gradually increase these requirements, for example
eventually mandating the use of such hardware security keys. Contributing
companies and organizations are encouraged to consider if their control and
resources allow making it mandatory for their participating staff earlier.

We are aware that interactions with the Archive are not limited only to
signing uploads \- to achieve the desired level of security, associated
interfaces such as the Launchpad API must also grow the feature to support
similar mechanisms. Otherwise only identity, but not other equally critical
interactions, would be protected. This is being pushed for and guidance about
their usage will be included here once possible.

(pgp-setup-guidelines)=
# Setup Guidelines

The guide on an {ref}`Ubuntu developer’s initial setup <gnupg>` so far only
outlines the basic usage of PGP keys. Guides on setting up and using PGP-capable
hardware security keys shall be provided via the project's documentation once
we standardize more on it.

Until then, starting with these articles on
[Using your YubiKey with OpenPGP](https://support.yubico.com/hc/en-us/articles/360013790259-Using-Your-YubiKey-with-OpenPGP)
and the [YubiKey Guide](https://drduh.github.io/YubiKey-Guide) are a great way
to begin.

# Alternatives

Hardware-backed PGP keys are the recommended solution because they provide
protections against key extraction and local compromise, while staying
rather comfortable and convenient to use — they can enforce confirmation for
phishing resistance, keep private keys off disk for safer backups, and support
modern curves/attestation for stronger cryptographic provenance.

But no option is without risk: Advances in cryptanalysis, discovery of
implementation flaws, vendor lock-in, or just increases in raw computational
power can weaken any current scheme. We also have to recognize that hardware
keys may not be accessible to everyone. To offset that, we maintain cautious
skepticism against any implementation.

If you now happen to distrust the recommended solution the most or it is
unavailable to you, what then? In that case it is worth to think about
alternatives. This multi-faceted approach aims to balance security and
practicality while acknowledging the dynamic nature of cryptographic
resilience.

Alternative safeguards and key storage models may be acceptable as well,
provided they are documented here in full on pages of their own, subject to a
review before adoption and referenced from the list below to keep things
together. Such a review must include security experts (including the Ubuntu
security team), tech-board (does it fit the project), authors (to ensure
clarity), and the wider project community through an open, non-rushed review
process that permits broad participation and iterative feedback.

There isn't yet a defined set of requirements such an alternative recommendation
would need to fulfil to be considered as trusted. The first to be processed
will need to identify that through discussion and colaboration. Initial
thoughts, pros and cons are in this
[mailing list discussion](https://lists.ubuntu.com/archives/ubuntu-devel/2025-September/043448.html).

Approved alternative recommendations:

* (TBD - None approved yet)

# Yet incomplete aspects

These recommendations can already be tremendously helpful, but there are
related aspects that are known to still be missing. Tracking them here
within the document itself for easier reader awareness to avoid searching
for them in vain.

* The {ref}`pgp-setup-guidelines` are not yet defined in detail.
* It would be great to add what actions to take if a key or signing compromise
  is suspected.
* Set of requirements an alternative recommendation would need to fulfil
* Outline what "in a secure location" could be in a sub-article. That will
  probably never be complete, but could list acknowledged known good/bad cases.
