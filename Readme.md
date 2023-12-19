# Baxter packages for ROS 1

These packages are the legacy version of Baxter's packages from Rethink Robotics.

They have been ported to Python3 and can be used either with Noetic or the Community edition.

## Installing from Debian packages

Two Debian files are available for an easy install:

- a `noetic` version to use with e.g. Ubuntu 20.04, with `ros-noetic-` dependencies
- a `community` version to use with any distro, with Debian `ros` dependencies

The `community` version will install `baxter_tools` scripts in `/usr/bin` with `baxter_` prefix, to easily run and setup your robot. The `control_msgs` package will be included in the `community` version as this package is not available in Debian.

## Installing from source

The Debian packages can be re-generated with the `create_baxter_deb.py` script.

It should be done on Ubuntu 20.04/Noetic, and assumes a workspace lies in `baxter_src/src`.

- Copy all packages in this directory
- Run `catkin_make install`
- Run `create_baxter_deb.py`
