(apport-package-hooks)=
# Apport package hooks

```{admonition} Migrated content
This page has been migrated from the Ubuntu Wiki "as is".
It may contain inaccuracies, may not be up-to-date, and may require
formatting, language, or other corrections.
```

These are lists of packages that provide apport hooks and the actually hooks that exist in `/usr/share/apport/package-hooks`.  They were last updated on 02/13/2012.


(packages-with-apport-hooks)=
## Packages with apport hooks

* {pkg}`alsa-driver`
* {pkg}`apache2`
* {pkg}`apparmor`
* {pkg}`apport`
* {pkg}`audacity`
* {pkg}`banshee`
* {pkg}`bind9`
* {pkg}`bluez`
* {pkg}`byobu`
* {pkg}`cairo-dock`
* {pkg}`checkbox`
* {pkg}`cheese`
* {pkg}`chromium-browser`
* {pkg}`compiz`
* {pkg}`conky`
* {pkg}`connman`
* {pkg}`console-setup`
* {pkg}`cryptsetup`
* {pkg}`cups`
* {pkg}`cups-driver-gutenprint`
* {pkg}`cups-filters`
* {pkg}`cups-pdf`
* {pkg}`debian-installer`
* {pkg}`desktopcouch`
* {pkg}`devicekit-disks`
* {pkg}`dkms`
* {pkg}`dovecot`
* {pkg}`eclipse`
* {pkg}`eucalyptus`
* {pkg}`evince`
* {pkg}`firefox`
* {pkg}`foo2zjs`
* {pkg}`foomatic-db`
* {pkg}`foomatic-db-engine`
* {pkg}`foomatic-filters`
* {pkg}`ghostscript`
* {pkg}`gnome-control-center`
* {pkg}`gnome-media-player`
* {pkg}`gnome-screensaver`
* {pkg}`grub-common`
* {pkg}`gwibber`
* {pkg}`hplip`
* {pkg}`indicator-applet`
* {pkg}`indicator-power`
* {pkg}`indicator-weather`
* {pkg}`isc-dhcp-client`
* {pkg}`isc-dhcp-server`
* {pkg}`jockey`
* {pkg}`libatasmart4`
* {pkg}`libfm`
* {pkg}`libmtp`
* {pkg}`libvirt`
* {pkg}`linux`
* {pkg}`login`
* {pkg}`lxappearance`
* {pkg}`lxinput`
* {pkg}`lxlauncher`
* {pkg}`lxpanel`
* {pkg}`lxrandr`
* {pkg}`lxterminal`
* {pkg}`m2300w`
* {pkg}`magicicada`
* {pkg}`mdadm`
* {pkg}`min12xxw`
* {pkg}`mtdev`
* {pkg}`mysql-dfsg-5.1`
* {pkg}`mythplugins`
* {pkg}`myththemes`
* {pkg}`mythtv`
* {pkg}`nautilus`
* {pkg}`network-manager`
* {pkg}`notify-osd`
* {pkg}`nova`
* {pkg}`ntp`
* {pkg}`nut`
* {pkg}`nux`
* {pkg}`openssh`
* {pkg}`pcmanfm`
* {pkg}`php5`
* {pkg}`plymouth`
* {pkg}`printer-driver-c2050`
* {pkg}`printer-driver-c2esp`
* {pkg}`ptouch-driver`
* {pkg}`pulseaudio`
* {pkg}`pxljr`
* {pkg}`qemu-kvm`
* {pkg}`quickly`
* {pkg}`rastertosag-gdi`
* {pkg}`rhythmbox`
* {pkg}`rss-glx`
* {pkg}`simple-scan`
* {pkg}`sl-modem`
* {pkg}`snmp`
* {pkg}`software-center`
* {pkg}`splix`
* {pkg}`sudo`
* {pkg}`synaptic`
* {pkg}`system-config-printer`
* {pkg}`telepathy-mission-control`
* {pkg}`thunderbird`
* {pkg}`totem`
* {pkg}`ubiquity`
* {pkg}`ubuntuone-client`
* {pkg}`ubuntu-vm-builder`
* {pkg}`udev`
* {pkg}`udisks`
* {pkg}`unity`
* {pkg}`unity-2d`
* {pkg}`update-manager`
* {pkg}`upgrade-system`
* {pkg}`ureadahead`
* {pkg}`virtualbox`
* {pkg}`virtualbox-guest-dkms`
* {pkg}`vlc`
* {pkg}`xorg`
* {pkg}`xul-ext-mozvoikko`
* {pkg}`yelp`


(apport-hooks)=
## Apport hooks

The '->' indicates the hook is a symbolic link to another one.  For example, lots of the xorg packages use the same hook.

* source_alsa-driver.py
* source_apparmor.py
* source_linux.py
* source_debian-installer.py
* source_apport.py
* source_linux-meta.py -> source_linux.py
* source_byobu.py
* source_checkbox.py
* source_compiz.py
* source_cups.py
* source_gutenprint.py
* source_evince.py
* firefox.py
* source_foo2zjs.py
* source_foomatic-db.py
* source_foomatic-db-engine.py
* source_foomatic-filters.py
* source_ghostscript.py
* source_gnome-power-manager.py
* source_hplip.py
* source_jockey.py
* source_libvirt-bin.py
* source_m2300w.py
* source_mdadm.py
* source_min12xxw.py
* mysql-server-5.1.py
* source_nautilus.py
* source_network-manager.py
* source_network-manager-applet.py -> source_network-manager.py
* source_notify-osd.py
* source_pulseaudio.py
* source_pxljr.py
* source_qemu-kvm.py
* source_rss-glx.py
* source_splix.py
* source_system-config-printer.py
* source_totem.py
* source_ubiquity.py
* source_ubuntuone-client.py
* udev.py
* usplash.py
* source_xorg.py
* source_xterm.py -> source_xorg.py
* source_xserver-xorg-video-vesa.py -> source_xorg.py
* source_xserver-xorg-video-sis.py -> source_xorg.py
* source_xserver-xorg-video-savage.py -> source_xorg.py
* source_xserver-xorg-video-radeon.py -> source_xorg.py
* source_xserver-xorg-video-radeonhd.py -> source_xorg.py
* source_xserver-xorg-video-psb.py -> source_xorg.py
* source_xserver-xorg-video-openchrome.py -> source_xorg.py
* source_xserver-xorg-video-nouveau.py -> source_xorg.py
* source_xserver-xorg-video-nv.py -> source_xorg.py
* source_xserver-xorg-video-mga.py -> source_xorg.py
* source_xserver-xorg-video-intel.py -> source_xorg.py
* source_xserver-xorg-video-geode.py -> source_xorg.py
* source_xserver-xorg-video-fbdev.py -> source_xorg.py
* source_xserver-xorg-video-ati.py -> source_xorg.py
* source_xserver-xorg-input-synaptics.py -> source_xorg.py
* source_xserver-xorg-input-mouse.py -> source_xorg.py
* source_xserver-xorg-input-keyboard.py -> source_xorg.py
* source_xserver-xorg-input-joystick.py -> source_xorg.py
* source_xserver-xorg-input-evdev.py -> source_xorg.py
* source_xserver-xorg-input-elographics.py -> source_xorg.py
* source_xorg_server.py -> source_xorg.py
* source_xrandr.py -> source_xorg.py
* source_xkeyboard-config.py -> source_xorg.py
* source_xinit.py -> source_xorg.py
* source_xfree86-driver-synaptics.py -> source_xorg.py
* source_xf86-input-evtouch.py -> source_xorg.py
* source_x11-xserver-utils.py -> source_xorg.py
* source_wacom-tools.py -> source_xorg.py
* source_fglrx-installer.py -> source_xorg.py
* source_nvidia-graphics-drivers-180.py -> source_xorg.py
* source_nvidia-graphics-drivers-177.py -> source_xorg.py
* source_nvidia-graphics-drivers-173.py -> source_xorg.py
* source_nvidia-graphics-drivers-96.py -> source_xorg.py
* source_nvidia-graphics-drivers-71.py -> source_xorg.py
* source_mesa.py -> source_xorg.py
* source_libxcb.py -> source_xorg.py
* source_libx11.py -> source_xorg.py
* source_libdrm.py -> source_xorg.py
* xserver-xorg-core.py -> source_xorg.py
* source_xscreensaver.py
* conky.py
* source_cups-pdf.py
* source_upgrade-system.py
* source_virtualbox-ose.py
* source_vlc.py
* source_yelp.py
