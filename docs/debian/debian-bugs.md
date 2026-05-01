(debian-bugs)=
# Reporting bugs in Debian

Debian maintainers use **debbugs**, an email-driven system that requires no authentication. This allows anyone to report bugs—from minor glitches to critical issues—from any system.

The canonical documentation is available at the [Debian Bug Reporting page](https://www.debian.org/Bugs/Reporting).

## Searching for Debian bugs
Use `querybts` (included in the `reportbug` package) to search for existing reports from the command line:

```bash
querybts vim
```
This command allows you to view full reports or filter results using patterns to find specific issues.

---

## Using `reportbug`
Debian recommends the `reportbug` utility to handle the proper email formatting for `submit@bugs.debian.org`. 

### Configuration on Ubuntu
On Ubuntu systems, `reportbug` is configured by default to report to Ubuntu mailing lists. You can override this:
* **One-time:** Use the `-B debian` flag: `reportbug -B debian <package_name>`
* **Permanently:** Edit the `bts` line in `/etc/reportbug.conf`.
* **SMTP:** If `smtphost` is set to an internal Ubuntu relay, you may need to change it to a public relay host.

Run `reportbug --configure` to set up your `~/.reportbugrc` before first use.

---

## Forwarding patches with `submittodebian`
Part of the `ubuntu-dev-tools` package, `submittodebian` is the preferred way to forward patches upstream. It handles **Debian Usertagging** and opens an editor for final patch cleanup.

**Example Workflow:**
```bash
apt-get source xicc
cd xicc-0.2/
# Perform your changes
dch -i 'debian/control: replaced "colour" with "color".'
debuild -S
submittodebian
```
*Note: You must build the source package (`debuild -S`) before running `submittodebian`.*

---

## When to report to Debian
Since most packages in the Ubuntu `universe` are synced from Debian, fixing bugs there prevents unnecessary divergence and helps the **MOTU** (Masters of the Universe) team.

* **Verify:** Ensure the bug applies to Debian and isn't caused by {term}`Ubuntu delta`.
* **Wishlist:** File suggestions as `wishlist` bugs.
* **Patches:** Use `submittodebian` or attach a `debdiff` to a `reportbug` report tagged with **patch**. 

### Mass Bug Filing
For issues affecting 10 or more packages, follow the [Debian Developers Reference](https://www.debian.org/doc/developers-reference/beyond-pkging.html#submit-many-bugs).

---

## After reporting
Link the Debian report to the corresponding Launchpad/Ubuntu bug:
1. Select **"Also affects distribution"** in the Ubuntu bug report.
2. Enter the Debian bug number in the Launchpad bug report to link the Debian fix automatically.