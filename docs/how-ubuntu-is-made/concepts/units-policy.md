# Units Policy

## Rationale

There are two ways to represent big numbers: You could either display them in multiples of 1000 = 10^3 (base 10) or 1024 = 2^10 (base 2). If you divide by 1000, you probably use the [SI prefix names](http://en.wikipedia.org/wiki/SI_prefixes#List_of_SI_prefixes), if you divide by 1024, you probably use the [IEC prefix names](http://en.wikipedia.org/wiki/Binary_prefix#Prefixes). The problem starts with dividing by 1024. Many applications use the [SI prefix names](http://en.wikipedia.org/wiki/SI_prefixes#List_of_SI_prefixes) for it and some use the [IEC prefix names](http://en.wikipedia.org/wiki/Binary_prefix#Prefixes). The current situation is a mess. If you see [SI prefix names](http://en.wikipedia.org/wiki/SI_prefixes#List_of_SI_prefixes) you do not know whether the number is divided by 1000 or 1024. There is already a Brainstorm idea for it: [Fix file size confusion](http://brainstorm.ubuntu.com/idea/21184/).

## Policy

- Applications must use [IEC standard](http://en.wikipedia.org/wiki/IEC_60027) for base-2 units:

  - 1 KiB = 1,024 bytes (Note: big k)
  - 1 MiB = 1,024 KiB = 1,048,576 bytes
  - 1 GiB = 1,024 MiB = 1,048,576 KiB = 1,073,741,824 bytes
  - 1 TiB = 1,024 GiB = 1,048,576 MiB = 1,073,741,824 KiB = 1,099,511,627,776 bytes

- Applications must use [SI standard](http://en.wikipedia.org/wiki/International_System_of_Units) for base-10 units:

  - 1 kB = 1,000 bytes (Note: small k)
  - 1 MB = 1,000 kB = 1,000,000 bytes
  - 1 GB = 1,000 MB = 1,000,000 kB = 1,000,000,000 bytes
  - 1 TB = 1,000 GB = 1,000,000 MB = 1,000,000,000 kB = 1,000,000,000,000 bytes

- It is not allowed to use the [SI standard](http://en.wikipedia.org/wiki/International_System_of_Units) for base-2 units:

  - 1 kB != 1,024 bytes
  - KB (with a big k) does not exist

### Implementation

There are two ways to fix the abuse of the SI standard for base-2:

1. Correct the application to divide by 1,000 and keep on using SI prefixes.
2. Correct the application to keep on dividing by 1,024 but use the IEC prefixes.

#### Correct basis

Use base-10 for:

- network bandwidth (for example, 6 Mbit/s or 50 kB/s)
- disk sizes (for example, 500 GB hard drive or 4.7 GB DVD)

Use base-2 for:

- RAM sizes (for example, 2 GiB RAM)

For file sizes there are two possibilities:

1. Show both, base-10 and base-2 (in this order). An example is the Linux kernel: "2930277168 512-byte hardware sectors: (1.50 TB/1.36 TiB)"
2. Only show base-10, or give the user the opportunity to decide between base-10 and base-2 (the default must be base-10).

### Exception

The application can keep their previous behavior for backwards compatibility if the following points apply. The application may add an option to display the sizes in base-10, too.

- is a command-line tool
- is often parsed by machine (for example, the output is used in scripts)
- only the prefix is displayed and not the unit (for example, M instead of MB)

Some applications which fall under this rule are:

- df
- du
- ls

### Use cases

- Alice does not know much about computers. She is familiar with the SI prefix system (1 kg = 1000 g, 1 km = 1000 m). She quickly understands that 1 kB is 1000 bytes.
- Bob uses Ubuntu and Windows. He wants to see the same numbers for file sizes in Nautilus as in Windows Explorer so that he can simply compare them. Therefore, Nautilus needs to display the file sizes in base-2.

### Bug reports

Tag bugs that violate this policy with [units-policy](https://bugs.launchpad.net/ubuntu/+bugs?field.tag=units-policy).

## Additional notes

There is no third "standard" in the form of the [O'Reilly Style Guide](http://oreilly.com/oreilly/author/stylesheet.html). It only specified abbreviations for 1,024 (K) and 1,000 (k), but not for 1,048,576 and 1,000,000 and so on.

### Bugs in this policy

These devices are labelled in a way that this policy fails to account for:

- CD-ROM sizes are specified in MiB, but the manufacturers label this "MB" (a "700 MB" CD-ROM contains approximately 700 MiB = 737 MB).
- Memory (RAM, ROM) is specified in base 2, but labelled with SI prefixes. For example, a "512 MB" RAM contains 512 MiB = 536.9 MB.
- Most small floppy disks are measured in base 2, but labelled with SI prefixes.
- A floppy labeled with "1.44 MB" contains 1.44 x 1000 x 1024 bytes = 1.41 MiB = 1.47 MB, which doesn't follow either convention.

## References

### General

- http://en.wikipedia.org/wiki/Si_prefix
- http://en.wikipedia.org/wiki/Binary_prefix
- http://physics.nist.gov/cuu/Units/binary.html

### Brainstorm ideas and blueprints

- [Idea #4114: Standardize IEC and SI prefixes](http://brainstorm.ubuntu.com/idea/4114/)
- [Idea #17839: Using Microsoft units for file sizes is confusing](http://brainstorm.ubuntu.com/idea/17839/)
- [Idea #21184: Fix file size confusion](http://brainstorm.ubuntu.com/idea/21184/)
- [Blueprint: Ubuntu Desktop Unit Consistency](https://blueprints.launchpad.net/ubuntu/+spec/desktop-unit-consistency/)

### Other operating systems

- [Debian: Consistent Unit Prefixes](http://wiki.debian.org/ConsistentUnitPrefixes)
- [How Mac OS X reports drive capacity](http://support.apple.com/kb/TS2419) - "In Mac OS X v10.6 Snow Leopard, storage capacity is displayed as per product specifications (base 10). A 200 GB drive shows 200 GB capacity ..."

## Comments and suggestions

- We should not use the naming "SI prefixes" and "IEC prefixes". The more accurate terminology would be "decimal prefixes" and "binary prefixes" This is because IEC is a standard body which happens to use both types of prefixes and SI is a system of units of measurement. ISO and IEC have jointly adopted both prefixes in what is now ISO/IEC 80000. See: [ISO 80000](http://en.wikipedia.org/wiki/ISO_80000)

- The default should be base 2 for file sizes, I don't think that being scientifically accurate matters as KiB and so on are rarely used. People who are not scientifically trained but understand what a kilobyte is assume it to be 1024 bytes, most people haven't heard of a kibibyte and don't want to either. It's not just Windows PCs but on every home computer for the past 25 years 'k', 'KB' or 'kb' has meant 1024 bytes, people who don't know this and do care are a tiny minority. Base 2 applies to websites and file sizes on mobile phones. Go with the flow, it shouldn't be Ubuntu's job to educate the public on SI standards, screw SI standards, this is Linux for human beings not scientists! It should be base 2 and in upper case unless talking about networks. Disks should display both, as the manufacturers talk in base 10 but base 2 is of interest to the users. -- Gaz Davidson

- The default should be base 10 for file sizes. Base 2 should only be used where the thing being measured naturally comes in multiples of a power of 2. File and disk sizes do not; they can be any arbitrary number. People who are not trained in computer science assume that a kilobyte means 1000 bytes, since a kilometer is 1000 meters and a kilogram is 1000 grams. Most people have never heard of dividing by 1024, and don't want to either. It serves no purpose in this context. The reason the base 2 convention exists is to make memory calculations simpler. 16 + 16 = 32, rather than 16.4 + 16.4 = 32.8 or 16.8 + 16.8 = 33.6. But this simplification doesn't apply to file sizes or disk sizes, so using 1024 for file sizes when the user expects 1000 just makes things much more complicated than they need to be. The Linux kernel measures disk sizes in base 10, Mac OS X measures disk and file sizes in base 10, manufacturers measure in base 10, and users are familiar with base 10. They are not familiar with base 2.

- This policy is a real trouble-maker. (See http://ubuntuforums.org/showpost.php?p=8956284&postcount=6). 700 "MB" CDs are apparently 700 MiB, but have always been referred to as 700 MB. The consequence is that people are seeing "oversized" ISOs when they really are properly sized, which is a much bigger issue than someone getting confused about the file size. Additionally, (@last poster) systems such as Windows use base-2, and the quickest way of checking integrity is looking at size.--Ibidem

  - Yes, this policy fixes the problem that has existed for many years and has confused many users, such as not being able to fit 4.7 "GB" on a 4.7 GB DVD. See https://blueprints.launchpad.net/ubuntu/+spec/desktop-unit-consistency for some of the many issues this has caused. Yes, Windows uses the wrong units, which is a major cause of such problems. That's not a rationale for leaving it unfixed.

- File sizes have always been reported on pretty much any OS I can think of as base-2 even when using SI units (wrongly). To now go to changing to base-10 just to use the SI units correctly seems wrong -- why not simply update the MB to MiB, and etc? That way, everything, from RAM sizes, to file sizes, will use the same familiar general sizes, and the units are updated to be correct, and more importantly, educational. So what if hard drive manufacturers use base-10 units? No OS ever has, and to change it to avoid confusion is solving the wrong problem, imo. We should fix the units and presentation, not create even more inconsistency -- I love that command line tools get an exemption in the units policy, and now CD media may too. If we are aiming for less confusion, creating even more inconsistency makes no sense. Why not do something more simple and more logical -- pick the binary measurements that have been in use for decades (hence the cli exemption), and update the SI units to IEC units /everywhere/. Also, I am disappointed to see that Mac OS X has gone to SI units for reporting hard drive sizes as well, although I suspect from their KB article that they still report file sizes using base-2 and using SI units. More inconsistency.

  - Apple OS X uses base 10 for file sizes, as does software like apt/Synaptic, etc.

- I believe people are used to seeing "KB, MB". Please don't change it. This is like moving the window buttons to the left side.

  - It will still be "kB" and "MB" - it will just have the base 10 meaning instead of base 2.

- I think at this point in time most computer users are used to using base-2, even though its far more common to see SI units being incorrectly used. I believe the best way to go about this would to be simply fixing the already existing problems by updating them to the correct unit. Suddenly switching everyone to base-10 rules, which hardly anyone is actually familiar with would -- in my opinion cause more harm then good. Just my 2 cents.

  - I disagree. The vast majority of people use base 10 in everyday life, not base 2. Ask any computer user who isn't technically-oriented how many bytes are in a kilobyte. They'll say 1000. Outside of the US, everyone is familiar with the metric system and SI prefixes, which always have a meaning of 1000s, not 1024s. This is the way they are used in computing, too, for processor speeds (GHz), networking (Mbps), mp3 bitrates (kbps), sizes of hard drives, DVDs, USB flash memory sticks, and other media (GB), camera resolutions (MP), etc. These are all base 10. Dividing by 1024 is not natural or logical - it needs to be taught as an exception to the rule - so it's only the technically-oriented people who have already learned it that need to unlearn it. Most computer users don't even realize it's there.

- The exception on command-line tools is very important (and quite obvious). However, I think it would be great to go as far as adding options to the most commonly used command-line tools, such as --si|--decimal and --iec|--binary. If such patches were propagated upstream (I'm dreading such options restricted to one distribution for the sake of cross-distribution compatibility for scripts), it would allow developers and sysadmins to choose to use them. -- RaphaelPinson

- Also, it would be great to try and get this into FreeDesktop. KDE4 apps already use the xiB convention by default for example. -- RaphaelPinson

- Don't change any numbers, nowhere, never, it will confuse the hell out of the users, both newbies (Windows uses Base-2 everywhere last time I checked) and hackers (I first learned about Base-10 prefixes circa 3 years ago, I grew up with Base-2 and never liked Base-10). If you absolutely think you must change anything, modify the unit names to correctly reflect the numbers. BTW, Nautilus uses "KB" instead of "kb" (I use Jaunty). -- claydragon

  - Couldn't agree more. Hands off the numbers - just change the units if you must. -- KennoVO

- I think KiB, MiB, GiB, etc., are fine and increase clarity and usability, but we should abandon the use of kB, mB, gB entirely because they hold two possible meanings (the popular/defacto meaning (up until a few years back), or the "standard"/unpopular meaning) which make them unreliable and possibly inaccurate. I would be in favor of adjusting all the prefixes to read using the -ibi system. I would also be in favor of seeing a standards body tackling a new way to specify the SI sizes that is unambiguous, maybe by replacing the idea of Byte with that of Octet, for example, where kO could mean, unambiguously, "a thousand octets." -- JeffDay