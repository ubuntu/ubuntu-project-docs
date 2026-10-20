(security-team)=
# Security team

The Ubuntu Security team represents multiple teams of people dedicated to keeping Ubuntu and its users secure through fixing vulnerabilities and contributing to Ubuntu's security development.
The primary teams are:

* [Ubuntu Security](https://launchpad.net/~ubuntu-security): responsible for the officially supported packages in Ubuntu
* [MOTU Swat](https://launchpad.net/~motu-swat): helps to coordinate security updates for community-supported packages in Ubuntu

The team tracks security issues that affect Ubuntu in the [Ubuntu CVE Tracker](https://ubuntu.com/security/cves), evaluates new issues as they come in, and publishes fixes as Ubuntu Security Notices.


## Communication

**Report a vulnerability**
: To report a security issue in Ubuntu, file a private bug on [Launchpad](https://bugs.launchpad.net/ubuntu) marked as a security issue, or email [security@ubuntu.com](mailto:security@ubuntu.com). See {ref}`how-to-report-a-bug` for general bug reporting guidance.

**Security notices and information**
: [ubuntu.com/security](https://ubuntu.com/security)


## Meetings

No regular public meeting is currently advertised.


## Authority

The Ubuntu Security team is responsible for security updates to officially supported packages in Ubuntu.
The team decides which issues warrant security updates, and coordinates responsible disclosure when it discovers vulnerabilities during its own audits.


## Contributing

Interested in helping? You can:

* Help triage security bugs in Ubuntu
* Help prepare and test updates for community-supported packages in `universe` (see {ref}`sponsorship` for how to get changes reviewed and uploaded)
* Test proposed security updates to verify they fix the flaw without introducing regressions

Contact the team through the channels above to find out where your help is most needed.


## Additional information

### What the team does

A security vulnerability can be defined as *"a mistake in software that can be directly used by a hacker to gain access to a system or network"* ([MITRE](https://cve.mitre.org/about/terminology.html)).
The Ubuntu Security team and the Ubuntu community work together to find and correct these mistakes through various activities:

**Auditing**
: The Security team often audits software before it becomes officially supported. Once vulnerabilities are found, the team uses responsible disclosure to let others know about the issue.

**Tracking**
: Most flaws in software are found by security researchers and users of the software. These flaws are tracked globally in the [MITRE CVE database](https://cve.mitre.org/), and the Security team tracks issues that affect Ubuntu in the [Ubuntu CVE Tracker](https://ubuntu.com/security/cves). As new issues come in, they are evaluated and triaged, then added to the tracker; as issues are fixed, the CVE entries are updated and retired.

**Fixing**
: After a flaw is found and assigned a CVE ID, it should be fixed. Often the author of the software provides a patch, or a patch is created by other developers, including the Ubuntu Security team.

**Testing**
: Before a security update is made available, it is tested to check that it fixes the flaw and does not introduce any regressions.

**Debian collaboration**
: Debian and Ubuntu share much of the same software, and collaboration between the two distributions' security teams is beneficial to both.

### Security development

The Security team also actively develops protections to help keep Ubuntu users safe from new vulnerabilities, such as {spellexception}`AppArmor`, compiler hardening flags, and the Uncomplicated Firewall ({spellexception}`ufw`).
