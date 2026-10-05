(GStreamer-test-plan)=
# GStreamer test plan


## Test plan for GStreamer


### Video codecs

Find/utilize some test content for each codec. [Fluster](https://github.com/fluendo/fluster) is one reliable
source of test content, so are the [GStreamer integration suites](https://gitlab.freedesktop.org/gstreamer/gst-integration-testsuites). The more the better. Running thumbnail software in personal video libraries is also a good check.

For each file, play it with the default media player and ensure it
looks "ok". Also play it with `GST_DEBUG=*:1 gst-play-1.0` and ensure
nothing bad happens.

Some codecs will require modifications to a clean install. Such cases
will be highlighted below.

Hardware configuration entails the set of tests to perform. Decide now
if you are on testing Intel, AMD, NVIDIA.


#### VP8

Try `vp8_variable_resolution.webm`

This is a very weird file, but it should play for a few seconds, and
show frames of varying resolutions. There should be a women with
slider bars next to her visible.

As a royalty free codec, VP8 test files should play on a fresh installation.


#### AV1

At the time of writing, AV1 decoders are still being shipped only in the -bad plugin set. This should be fixed since there's no reason not to support AV1 out of the box.

Open `Schiddler7.mkv-aom-q-28-1920-1080-P3.mkv` in the default media
player and ensure the codec installation wizard works, and that subsequently the media plays properly.

Rationale: AV1 aligns well with Ubuntu philosophy, we should support
that as standard. The input files cover the majority of AV1 coding
tools, especially film grain. Decoder see (see Fluster below) cover more.


#### H.264

Open `Big_Buck_Bunny_720_10s_30MB.mp4` in the default media player and ensure the codec installation wizard works, and that subsequently the media plays properly.

* Ensure the files plays out correctly for the 10 seconds
* Run whatever is the default media player from the CLI. Ensure no warnings / errors are printed

Rationale: H.264 is ubiquitous. It must be default available or very easily installable for UX.

See: {lpbug}`2121434`


#### H.265

Open `4K HEVC 59.940 Broadcast Capture Sample.mkv` in the default media player and ensure the codec installation wizard works, and that subsequently the media plays properly.

Rationale: H.265 is also very popular, but very patent encumbered.


#### Hardware acceleration

Intel/AMD,

```none
gst-launch-1.0 filesrc location=h264_high_yuv420p_720p.mp4 ! qtdemux ! h264parse ! vah264dec ! videoconvert ! autovideosink
```

```none
gst-launch-1.0 filesrc location='4K HEVC 59.940 Broadcast Capture Sample.mkv' ! matroskademux ! h265parse ! vah265dec ! videoconvert ! autovideosink
```

NVIDIA,

```none
gst-launch-1.0 filesrc location='4K HEVC 59.940 Broadcast Capture Sample.mkv' ! matroskademux ! h265parse ! vdpauh265dec ! vdpauvideopostprocess ! autovideosink
```

Intel,

```none
gst-launch-1.0 filesrc location=h265_Main10_yuv420p10le_4K.mkv ! matroskademux ! h265parse ! msdkh265dec ! videoconvert ! autovideosink
```

TODO: Vulkan


#### Fluster

Fluster is a decoder conformance test-suite. At the time of writing, the full test database requires 14GB of space and takes many hours to run. Due to driver instability, there will also be many crashes, meaning automation is very challenging.

Instead, a cut-down version of the test-suite is prepared. Run the following script and ensure nothing catches fire.

`run_fluster.sh`


### Audio codecs

Pipewire is the default sound sever at the time of writing, but most applications still use the old Pulse API's, so make sure that works to some approximation.

First, find your input device. In the instructions it happens to be `alsa_card.usb-0c76_USB_PnP_Audio_Device-00`. A list of device can be seen with `pactl list`.

```none
gst-launch-1.0 -e pulsesrc device=alsa_card.usb-0c76_USB_PnP_Audio_Device-00 ! queue ! audioconvert ! audioresample !  opusenc audio-type=voice ! oggmux ! filesink location=test.ogg
```

Open `test.ogg` and check you can clearly hear the sounds you made.

Now do the same wit the FFmpeg AAC coder. You will need `gstreamer1.0-libav`,

```none
gst-launch-1.0 -e pulsesrc device=alsa_card.usb-0c76_USB_PnP_Audio_Device-00 ! queue ! audioconvert ! audioresample ! avenc_aac aac-coder=fast ! avmux_mp4 ! filesink location=test.mp4
```

Open `test.mp4` and check you can clearly hear the sounds you made.

Check Pipewire. Use `gst-device-monitor-1.0 Audio/Source` to find your `target-object`. In the examples mine is 66.

```none
gst-launch-1.0 -e pipewiresrc target-object=66  ! queue ! audioconvert ! audioresample !  opusenc audio-type=voice ! oggmux ! filesink location=test.ogg
```

Open `test.ogg` and check you can clearly hear the sounds you made.


### Development libraries

Ensure a few packages that use GStreamer can build from source, and that there's no issues installing the GStreamer binary packages for development.

GNOME Snapshot,

```none
git clone https://salsa.debian.org/ubuntu-dev-team/snapshot.git
cd snapshot
sudo apt build-dep .
dpkg-buildpackage -us -uc
./debian/gnome-snapshot/usr/bin/snapshot
```

Check the camera is working. Check you can record etc.

Run the following Python script to check a very basic `GObject` introspection client works correctly,

`test-gi.py`

A test video signal should be displayed.


### Integrations

Check the `gst-launch-1.0` command lines printed by,

```none
gst-device-monitor-1.0 Video/Source
```

And ensure they all work as expected.

For camera sources, additionally check `libcamera` integration.

```none
$ cam -l
1: 'Razer Kiyo Pro' (\_SB_.PCI0.GPP7.UP00.DP60.XH00.RHUB.POT2-2:1.0-1532:0e05)
$ cam -c1 --info
[6:58:46.380269937] [61938]  INFO Camera camera_manager.cpp:326 libcamera v0.5.0
[6:58:46.463388242] [61941]  WARN V4L2 v4l2_pixelformat.cpp:346 Unsupported V4L2 pixel format H264
Using camera \_SB_.PCI0.GPP7.UP00.DP60.XH00.RHUB.POT2-2:1.0-1532:0e05 as cam0
0: 1920x1080-NV12
* Pixelformat: NV12 (640x360)-(1920x1080)/(+0,+0)
  - 640x360
  - 640x480
  - 1280x720
  - 1920x1080
* Pixelformat: MJPEG (640x360)-(1920x1080)/(+0,+0)
  - 640x360
  - 640x480
  - 1280x720
  - 1920x1080
* Pixelformat: YUYV (640x360)-(1920x1080)/(+0,+0)
  - 640x360
  - 640x480
  - 1280x720
  - 1920x1080
```

Ensure the various formats work as expected. For instance, to check MJPEG @ 1080p,

```none
qcam  -s pixelformat=MJPEG,width=1920,height=1080
```

Check the GStreamer element works in an analogous way to `libcamera` above,

```none
gst-launch-1.0 libcamerasrc ! image/jpeg,width=1920,height=1080 ! jpegdec ! videoconvert ! glimagesink
```

Same again for the Pipewire integration

```none
gst-launch-1.0 pipewiresrc target-object=377 ! image/jpeg,width=1920,height=1080 ! jpegdec ! videoconvert ! glimagesink
```

Try other source formats.

Now ensure all the `gst-launch-1.0` pipelines for audio sources work,

```none
gst-device-monitor-1.0 Audio/Source
```

Open GNOME Snapshot (Camera app), and while it's open, check that

```none
pw-v4l2 gst-launch-1.0 v4l2src ! videoconvert ! autovideosink
```

Works as expected.
