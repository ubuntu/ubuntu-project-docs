.. _filesystem-hierarchy-standard:

Filesystem hierarchy standard
=============================

Ubuntu adheres to the `Filesystem Hierarchy Standard (FHS) <https://refspecs.linuxfoundation.org/fhs.shtml>`_. FHS prescribes the structure and organization of directories and files in UNIX-like operating systems. It also promotes uniformity in documentation across systems.

The FHS prescribes required directories, their roles, and their minimum expected contents. It provides a framework for separating shareable from unshareable files and static from variable files.

So, compliance with the FHS ensures that software developers and system administrators can predict where files reside.


File classification
-------------------

FHS classifies files based on two main distinctions. This classification determines their placement in the directory structure:

- **Shareable vs. unshareable:** Shareable files can be stored on one host and used by others. Examples include libraries in ``/usr/lib`` and documentation in ``/usr/share/doc``. Unshareable files are specific to a single system and cannot be shared. Examples include system configuration files in ``/etc`` and user-specific files in ``/home``.
- **Static vs. Variable:** Static files include binaries, libraries, documentation, and other files that don't change without the system administrator's intervention. Examples include files in ``/usr/bin``, ``/usr/lib``, or ``/etc``. Variable files change during normal system operation. Examples include mail files in /``var/mail`` and PID files in ``/run``.

These distinctions are interrelated as a file can fall into both classifications. For example:

- Files in ``/var/mail`` are shareable and variable.
- Files in ``/etc`` are unshareable and static.

However, static and variable files should be separated since static files can reside on read-only media and don't require frequent backups. To support this, the /var hierarchy was introduced to isolate variable files from static directories like ``/usr``, making ``/usr`` safely mountable as read-only.


Core filesystem hierarchies
---------------------------

The FHS prescribes three main filesystem hierarchies for UNIX-like operating systems:

- the root filesystem (``/``) hierarchy
- the ``/usr`` hierarchy
- the ``/var`` hierarchy

The standard requires these hierarchies to maintain compatibility across UNIX-like systems and support features like read-only mounting of ``/usr``. Each hierarchy contains specific subdirectories with defined purposes.


Root filesystem (``/``) hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The root filesystem is the top-level directory of the filesystem hierarchy. It contains all the essential components needed to boot, restore, recover, and repair the system. It must remain minimal to ensure reliability, portability, and ease of recovery.

A minimal root filesystem has the following benefits:

- supports mounting from minimal media, such as recovery disks
- avoids storing unshareable, system-specific files on networked systems
- reduces the risk and impact of data corruption
- supports systems with limited storage or a separate partition

The root filesystem must not contain application-specific directories. All additional components should be in ``/usr`` or ``/var``.

The following are the required directories in the root filesystem:

+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| Directory  | Purpose                                                                                                                           |
+============+===================================================================================================================================+
| ``/bin``   | for essential user command binaries used by all users, such as ``cp``, ``ls``, ``sh``, ``mount``                                  |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/boot``  | for static files for the bootloader, including the kernel                                                                         |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/dev``   | for device files representing system hardware                                                                                     |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/etc``   | for host-specific system configuration files and must not contain binary executables                                              |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/lib``   | for shared libraries and kernel modules required by binaries in ``/bin`` and ``/sbin``                                            |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/media`` | holds mount points for removable media such as USB drives or CDs                                                                  |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/mnt``   | holds temporary mount point for filesystems intended for manual use by system administrators                                      |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/opt``   | holds add-on application packages, with each package in its own subdirectory                                                      |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/run``   | stores runtime variable data cleared on boot, including process IDs and UNIX-domain sockets                                       |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/sbin``  | for essential system binaries for booting and system recovery, such as ``fsck`` and ``shutdown``                                  |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/srv``   | for site-specific data served by the system, such as web or FTP data                                                              |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/tmp``   | holds temporary files, which are not preserved across reboots                                                                     |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/usr``   | secondary hierarchy for read-only user utilities and applications                                                                 |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``/var``   | for variable data like logs, mail, and spool files                                                                                |
+------------+-----------------------------------------------------------------------------------------------------------------------------------+

The following directories may be present in the root filesystem if the corresponding subsystems are installed:

+---------------------+--------------------------------------------+
| Directory           | Purpose                                    |
+=====================+============================================+
| ``/home``           | for user home directories                  |
+---------------------+--------------------------------------------+
| ``/lib<qualifier>`` | for alternate format libraries             |
+---------------------+--------------------------------------------+
| ``/root``           | serves as home directory of the root user  |
+---------------------+--------------------------------------------+


``/usr`` hierarchy
~~~~~~~~~~~~~~~~~~

The ``/usr`` hierarchy contains shareable, read-only data. It must not contain any host-specific or variable files to:

- support safe mounting across multiple systems
- support read-only operation
- separate variable data from static program files
- maintain consistency across UNIX-like systems

Large software packages must not use a direct subdirectory under ``/usr``. Instead, they should reside in structured paths like ``/usr/share``, ``/usr/lib``, or ``/opt``.

The following are the required directories in the ``/usr`` hierarchy:

+------------------+----------------------------------------------------------------------------------------------+
| Directory        | Purpose                                                                                      |
+==================+==============================================================================================+
| ``/usr/bin``     | serves as primary directory for user-executable programs                                     |
+------------------+----------------------------------------------------------------------------------------------+
| ``/usr/lib``     | contains object files, libraries, and internal binaries for programs,                        |          
|                  | with subdirectories used per application for architecture-dependent files                    |
+------------------+----------------------------------------------------------------------------------------------+
| ``/usr/local``   | reserved for system administrator use when installing local software                         |
+------------------+----------------------------------------------------------------------------------------------+
| ``/usr/sbin``    | holds non-essential system binaries for administration and                                   |
|                  | used by root, but not required for boot or recovery                                          |
+------------------+----------------------------------------------------------------------------------------------+
| ``/usr/share``   | stores read-only, architecture-independent data such as documentation, icons, and manuals    |
+------------------+----------------------------------------------------------------------------------------------+


``/var`` hierarchy
~~~~~~~~~~~~~~~~~~

The ``/var`` hierarchy stores variable data files. These include system logs, mail, print spool files, cache data, and files generated at runtime. Files in ``/var`` are modified frequently during system operation. This separation from the static filesystem in ``/usr`` ensures that the ``/usr`` filesystem remains read-only.

``/var`` should be minimal to reduce the risk of system corruption and to simplify management. Also, applications must not add top-level directories in ``/var`` without a system-wide implication.

The following are the required directories in the ``/var`` hierarchy:

+-------------------+--------------------------------------------------------------------------------------------------+
| Directory         | Purpose                                                                                          |
+===================+==================================================================================================+
| ``/var/cache``    | stores application-generated cache data. The data must be safely disposable and reproducible     |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/lib``      | holds variable state information specific to applications                                        |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/local``    | holds variable data for software stored in ``/usr/local``                                        |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/lock``     | contains lock files to coordinate access to resources                                            |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/log``      | stores system log files and directories                                                          |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/opt``      | holds variable data for add-on software packages in ``/opt``                                     |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/run``      | holds transient runtime data, such as ``PID`` files                                              |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/spool``    | contains spool directories for tasks like mail and printing                                      |
+-------------------+--------------------------------------------------------------------------------------------------+
| ``/var/tmp``      | holds temporary files that are preserved between reboots                                         |
+-------------------+--------------------------------------------------------------------------------------------------+
