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
    

def system_dep(pkg, noetic, only = None):

    dashed = pkg.replace('_', '-')

    if noetic:
        return [f'ros-noetic-{dashed}']

    dev = f"lib{dashed}-dev"
    lib = f"ros-{dashed}"
    py = f'python3-{dashed}'
    if only == 'dev':
        return [dev]
    elif only == 'lib':
        return [lib]
    elif only == 'py':
        return [py]
    
    if pkg.endswith('_msgs'):
        return [dev, py,lib]
    
    if pkg in ('roscpp', 'rosconsole', 'roscpp_serialization', 'rostime'):
        return [dev]
    return [lib, py]
    

src = os.path.dirname(__file__) + '/baxter_src'
pkg = 'ros-baxter'
ver = '1.3.0'
dest = f'{pkg}_{ver}'

# find depends that are non-ROS
ros_pkg = check_output(f'ls {src}/install/share').split()
#ros_pkg = [line.split()[-1] for line in ros_pkg]

apt_pkg = check_output('apt list').splitlines()
apt_pkg = set(line.split('/')[0] for line in apt_pkg)

# source should be compiled as such, on a Noetic setup
#run(f'catkin_make install --cmake-args -DCATKIN_ENABLE_TESTING=OFF')


for noetic in (False,True):

    target = 'noetic' if noetic else 'community'

    print('Creating package for ' + target)

    prefix = '/opt/ros/noetic' if noetic else '/usr'

    # copy to pkg
    base = f'{dest}{prefix}'
    share = f'{base}/share'

    if os.path.exists(dest):
        run(f'sudo rm -rf {dest}')

    # prep directories
    os.makedirs(f'{dest}/DEBIAN')

    ignored = ['*__pycache__*']
    if noetic:
        ignored.append('control_msgs')

    shutil.copytree(f'{src}/install', base, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*ignored))

    # remove unwanted files
    for f in os.listdir(base):
        if not os.path.isdir(base+'/'+f):
            os.remove(base+'/'+f)

    # pkgconfig dir
    pkgconfig = f'{base}/lib/pkgconfig'

    if not noetic:
        os.mkdir(base + '/bin')
        # create links to baxter nodes
        for root, subdirs,files in os.walk(f'{base}/lib'):
            if f'{base}/lib/baxter_' in root:
                for f in files:
                    run(f'ln -s {root[len(dest):]}/{f} {base}/bin/baxter_{f}')

        # move pkgconfig files to share
        run(f'mv {base}/lib/pkgconfig {base}/share')
        pkgconfig = f'{base}/share/pkgconfig'

    # adapt pkgconfig files to this prefix
    prefix_sed = prefix.replace('/','\\/')
    for pc in os.listdir(pkgconfig):
        run(f'sed -i "s/^prefix=.*$/prefix={prefix_sed}/" {pkgconfig}/{pc}')

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
                    for sysdep in system_dep(dep, noetic):
                        if sysdep in apt_pkg or noetic:
                            print(f'Found system depend {sysdep} for {pkg}')
                            depends[dep].append(sysdep)
                            found = True
                    depends[dep] = ', '.join(depends[dep])
                if not found:
                    print(f'{dep} is an unknown dependency for {pkg}')
                    depends[dep] = None

    base_depends = {}
    base_depends['dev'] = ['actionlib-msgs', 'diagnostic-msgs', 'roscpp']
    base_depends['lib'] = ['diagnostic-msgs']
    base_depends['py'] = ['roslaunch','rostopic','rosservice','rosnode']

    base_depends = [system_dep(pkg, noetic, only)[0] for only,pkgs in base_depends.items() for pkg in pkgs]

    depends = ', '.join(base_depends + [dep for dep in depends.values() if dep])

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
Description: Base Baxter ROS 1 packages for use with ROS {target} version
''')

    # chown and create pkg
    print('Changing permissions...')
    run(f'sudo chmod 0775 {dest} -R')
    run(f'sudo chown root:root {dest} -R')
    run(f'dpkg-deb -b {dest}')

    idx = dest.rfind('_')

    shutil.move(dest+'.deb', f'{dest[:idx]}[{target}]{dest[idx:]}.deb')
