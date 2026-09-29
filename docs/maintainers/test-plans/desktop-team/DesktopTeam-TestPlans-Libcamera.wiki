(Libcamera-test-plan)=
# Libcamera test plan


## Install the packages

```none
$ sudo apt install libcamera-tools gstreamer1.0-libcamera
```


## Check that your camera is listed

```none
$ cam -l
```


## Capture an image

```none
$ cam --camera=1 --capture=1 --file=image.ppm
```

:::{note}
`cam` has limited pixel conversion support, the above may not work.
:::


## Verify that the captured image is correct

```none
$ eog image.jpg
```


## Check that the `gstreamer` plugin is working

```none
$ gst-launch-1.0 libcamerasrc ! videoconvert ! autovideosink
```

(you might need to specify a `camera-name=...` if more than 1 camera is available)


## Run the camera compliance tests

```none
$ lc-compliance -c "camera_name"
```

(you can get "camera_name" by doing `lc-compliance 2>&1 | tail -n 1 | cut -c 3-`, and yes the name is slightly confusing and include the leading \_ chars)


## Try an application using `libcamera`

To be added once we have a client software available in the archive
