(how-to-upload-packages-to-a-ppa)=
# How to upload packages to a PPA

A **PPA** (Personal Package Archive) is a personal repository on Launchpad where you can upload your own packages to be built by Launchpad. This page will assume you have already created or updated a package and are ready to build and upload. For information on how to do that, see {ref}`Create a New Package <how-to-create-a-new-package>`. 

In order to create and upload packages to PPAs, you will need to add your OpenPGP keys to Launchpad. Information on how to generate and import an OpenPGP key into Launchpad can be found at [Launchpad's help page](https://launchpad.net/+help-registry/openpgp-keys.html).

To manage PPAs, we will use the `ppa-dev-tools` snap. To install it, run
```
$ sudo snap install ppa-dev-tools
```

To upload files to PPAs, the tool `dput` is used. Install it (alongside many other useful Ubuntu development tools) with
```
$ sudo apt install ubuntu-dev-tools
```

# Creating a PPA

To create your PPA, run 
```
$ ppa create my-cool-new-ppa
```

If this is your first time using `ppa-dev-tools`, you may need to authenticate with Launchpad. To do this, `ppa-dev-tools` will output a link you can use to grant it authorization to work with your Launchpad account (in some cases, the link will automatically open in your browser. If not, you can manually copy-paste it or CTRL+Click in supported terminals). 

# Building and Uploading your Package

You only need to build *source* packages locally to upload them to a PPA. To do this, navigate to your package's directory (containing the `debian` folder) and use the `debuild` command (the `-k` flag ensures your build is signed with your OpenPGP key, a requirement to upload):

```
$ debuild -S -sa -k'email_associated_with_key@your_email.com'
```

This will produce a `.changes` file in the parent directory. Use `dput` to upload it:

```
$ dput ppa:your-launchpad-name/my-cool-new-ppa ../my-cool-package.changes
```

# Launchpad Builds

Now that the source package has been uploaded to Launchpad, its automated build systems will create binary packages from your source for various different architectures. This can take a long time, so `ppa-dev-tools` includes a tool to allow you to check how many builds are still in progress within a PPA. Use

```
$ ppa wait your-launchpad-name/my-cool-new-ppa
```

to receive a periodically updated report of your builds.

# Installing your Package

Once your package has built for the desired architecture, you can install it on any Ubuntu machine (whose version matches that of the package) using `apt`:

```
$ sudo add-apt-repository ppa:your-launchpad-name/my-cool-new-ppa
$ sudo apt update
$ sudo apt install my-cool-package
```

# Extra pre-upload checks with `dput-ng`

If you are often uploading packages, you may want to use `dput-ng`. This is a wrapper around `dput` that warns you or blocks uploading of the package if it does not conform to certain standards. 

If you installed `ubuntu-dev-tools`, the version of `dput` you are using is already `dput-ng`. If not, you can get it directly with
```
$ sudo apt install dput-ng
```

The Ubuntu Server Team has its own checks usable through the `ubuntu-helpers` repository including (but not limited to):
- Checking if your package closes a Launchpad bug.
- Checking if your package wasn't built/signed by a container or virtual machine user (e.g `root` or `ubuntu`).
- Checking if the referenced LP bug isn't a placeholder (like #99999999).

To set up the Server Team's check suite, use the following commands (`python3-termcolor` is a Python module required to run the check scripts):
```
$ sudo apt install python3-termcolor
$ git clone https://git.launchpad.net/~ubuntu-server/ubuntu-helpers 
$ ln -s ~/.dput.d ./ubuntu-helpers/cpaelzer/.dput.d/
```
You can also copy instead of symlinking if you want to make your own changes to the checking scripts.
