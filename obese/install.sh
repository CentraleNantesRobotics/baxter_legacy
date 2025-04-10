#!/usr/bin/env bash

# this script is to re-build the deb file on Noble+, installing all dependencies
ROS_ROOT=/opt/ros/obese

mkdir -p ../baxter_src/src
sudo rm -rf $ROS_ROOT ../baxter_src/build ../baxter_src/devel ../baxter_src/logs ../baxter_src/.catkin_tools

sudo mkdir -p $ROS_ROOT
sudo chown $USER $ROS_ROOT

# install system dependencies from .txt file
sudo apt install $(tr '\n' ' ' < system-dependencies.txt)

# clone repos from repos.txt
REPOS="$(realpath $(dirname $0)/repos.txt)"
cd ../baxter_src/src
while read repo; do
  git clone $repo
done <$REPOS

cd ..
# in case we run this from a sourced ROS 2 terminal
unset ROS_DISTRO
unset CMAKE_PREFIX_PATH
unset PYTHONPATH
unset LD_LIBRARY_PATH
catkin config --init --install-space $ROS_ROOT --install -DCATKIN_ENABLE_TESTING=False
catkin build
echo "export ROS_DISTRO=\"obese\"" >> ${ROS_ROOT}/local_setup.sh
echo "export ROS_DISTRO=\"obese\"" >> ${ROS_ROOT}/setup.sh

