#!/bin/env python3
import os
import shutil
import subprocess
from shlex import split
import sys


def error_exit(error):
    print(error)
    sys.exit(0)

    
def run(cmd, cwd = None):
    subprocess.run(split(cmd), cwd=cwd)


def check_output(cmd):
    return subprocess.check_output(split(cmd)).decode()
    

def system_dep(pkg, legacy):

    dashed = pkg.replace('_', '-')

    if not legacy:
        return [f'ros-noetic-{dashed}']

    dev = f"lib{dashed}-dev"
    lib = f"ros-{dashed}"
    py = f'python3-{dashed}'
    
    if pkg.endswith('_msgs'):
        return [dev, py,lib]
    
    if pkg in ('roscpp', 'rosconsole', 'roscpp_serialization', 'rostime'):
        return [dev]
    return [lib, py]
    

src = os.path.dirname(__file__) + '/baxter_src'
pkg = 'ros-baxter'
ver = '1.2.1'
dest = f'{pkg}_{ver}'

# find cmake path
cmake_prefix = []
for d in os.listdir('/usr/share'):
    if os.path.exists(f'/usr/share/{d}/package.xml'):
        cmake_prefix.append(f'/usr/share/{d}')
cmake_prefix = ':'.join(cmake_prefix)

# find depends that are non-ROS
ros_pkg = check_output(f'ls {src}/install/share').split()
#ros_pkg = [line.split()[-1] for line in ros_pkg]

apt_pkg = check_output('apt list').splitlines()
apt_pkg = set(line.split('/')[0] for line in apt_pkg)

# source should be compiled as such
#base_dir = os.path.abspath(os.curdir)
#os.chdir(src)
#run(f'catkin_make install --cmake-args -DCATKIN_ENABLE_TESTING=OFF')
#os.chdir(base_dir)

for distro in ('community','noetic'):

    legacy = distro == 'community'

    install = '/usr' if legacy else f'/opt/ros/{distro}'

    # copy to pkg
    base = f'{dest}{install}'
    share = f'{base}/share'

    if os.path.exists(dest):
        run(f'sudo rm -rf {dest}')

    # prep directories
    os.makedirs(f'{dest}/DEBIAN')

    ignored = ['*__pycache__*']
    if not legacy:
        ignored.append('control_msgs')

    shutil.copytree(f'{src}/install', base, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*ignored))
    # remove non-wanted file
    run(f'rm -rf {base}/lib/pkgconfig')
    for f in os.listdir(base):
        if not os.path.isdir(base+'/'+f):
            os.remove(base+'/'+f)

    if legacy:
        os.mkdir(base + '/bin')
        # create links to baxter nodes
        for root, subdirs,files in os.walk(f'{base}/lib'):
            if f'{base}/lib/baxter_' in root:
                for f in files:
                    run(f'ln -s {root[len(dest):]}/{f} {base}/bin/baxter_{f}')

        #
        #os.makedirs(f'{dest}/etc/profile.d')
        #with open(f'{dest}/etc/profile.d/ros_package_path.sh', 'w') as f:
            #f.write('''export ROS_PACKAGE_PATH=/usr/share
        #alias enable_robot="python3 /usr/lib/baxter_tools/enable_robot.py"
        #alias tuck_arms="python3 /usr/lib/baxter_tools/tuck_arms.py"
        #''')

    run(f'sudo chmod 0777 {dest} -R')

    depends = {}
    for pkg in os.listdir(share):
        xml = f'{share}/{pkg}/package.xml'
        if not os.path.exists(xml):
            continue

        with open(xml) as f:
            xml = f.read().splitlines()

        for line in xml:
            if '</run_depend>' in line or '</depend>' in line and 'ROS_PYTHON_VERSION == 2' not in line:
                # extract depend
                dep = line.replace('>', '<').split('<')[2]
                if dep in depends:
                    continue
                found = False
                if dep in ros_pkg and dep not in ignored:
                    print(f'Found in-place depend {dep} for {pkg}')
                    depends[dep] = ''
                    found = True
                elif dep in apt_pkg:
                    depends[dep] = dep
                    found = True
                else:
                    depends[dep] = []
                    for sysdep in system_dep(dep, legacy):
                        if sysdep in apt_pkg or not legacy:
                            print(f'Found system depend {sysdep} for {pkg}')
                            depends[dep].append(sysdep)
                            found = True
                    depends[dep] = ', '.join(depends[dep])
                if not found:
                    print(f'{dep} is an unknown dependency for {pkg}')
                    depends[dep] = None

    if legacy:
        base_depends = 'libactionlib-msgs-dev, libdiagnostic-msgs-dev, ros-diagnostic-msgs, libroscpp-dev, python3-roslaunch'
    else:
        base_depends = '{ros}-actionlib-msgs, {ros}-diagnostic-msgs, {ros}-roscpp, {ros}-roslaunch'.format(ros='ros-' + distro)

    depends = ', '.join([base_depends] + [dep for dep in depends.values() if dep])

    # create config
    size = check_output(f'du -s --block-size=1024 {dest}/').split('\t')[0]

    with open(f'{dest}/DEBIAN/control','w') as f:
        f.write(f'''Package: ros-baxter
Version: {ver}
Section: Development
Priority: optional
Architecture: all
Essential: no
Installed-Size: {size}
Depends: {depends}
Maintainer: olivier.kermorgant@ec-nantes.fr
Description: Base Baxter ROS 1 packages for use with ROS {distro} version
''')

    # chown and create pkg
    print('Changing permissions...')
    run(f'sudo chmod 0775 {dest} -R')
    run(f'sudo chown root:root {dest} -R')
    print(f'Creating package for {distro}')
    run(f'dpkg-deb -b {dest}')

    idx = dest.rfind('_')

    shutil.move(dest+'.deb', f'{dest[:idx]}[{distro}]{dest[idx:]}.deb')
