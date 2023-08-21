# Baxter packages for ROS 1

These packages are the legacy version of Baxter's packages from Rethink Robotics.

They have been ported to Python3 and can be used either with Noetic or the Community edition.

Debian files can be created with the `create_baxter_deb.py` script after you `catkin_make install` these packages in `baxter_src`.

It will create two `deb` files:

- a `noetic` version to use with e.g. Ubuntu 20.04, with `ros-noetic-` dependencies
- a `community` version to use with any distro, with Debian `ros` dependencies

The `community` version will install `baxter_tools` scripts in `/usr/bin` with `baxter_` prefix, to easily run and setup your robot. The `control_msgs` will be included in the `community` version as this package is not available in Debian.
