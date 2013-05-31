#!/usr/bin/env python

"""
Create a stand-alone Mac OS X distribution of Algraeph in the zip file
dist/algraeph_0.x_mac-os-x.zip

Should not run under virtualenv.
Assumes that the graeph, daeso, daeso_nl and networkx packages are
installed (i.e. availabel through sys.path or PYTHONPATH).
Cleans the build and dist dirs.
Retrieves version and other info from graph.release.
"""

import sys

# setup function seems to ignore its script_args keyword, so add py2app
# command to argv *before* importing setup
sys.argv.append("py2app")

import os
import shutil
import subprocess

from graeph import release

# clean build dir
try:
    shutil.rmtree("build")
except OSError:
    pass


dist_dir="dist-py2app"    

# py2app seems to overwrite old .app, which gives strange results, so we
# better clean
try:
    shutil.rmtree(dist_dir + "/algraeph.app")
except OSError:
    pass


py2app_options = dict(
    argv_emulation = True,
    # we assume that all required packages (graeph, daeso, daeso_nl, networkx) 
    # are in PYTHONPATH
    use_pythonpath = True,
    # numpy is imported by daeso_nl but not required for Algraeph
    excludes = ["numpy"],
    # additional data files which are copied to 
    # Algraeph.app/Contents/Resources/ 
    resources = ["README", "INSTALL", "COPYING","CHANGES", "doc"],
    dist_dir = dist_dir,
    iconfile='var/algraeph.icns',

)


# weird bugs occur if setup is imported before the build dir is deleted... 
from setuptools import setup

setup(
    script_args = ["py2app"],
    setup_requires = ["py2app"],
    app = ["bin/algraeph.py"],
    options = {"py2app": py2app_options},
)

# using zipfile is too much trouble because ZipFile class has no method to
# recursively add directories
name = "algraeph_%s_mac-os-x" % release.version

command = ( "cd %s && " % dist_dir +
            "rm -rf " + name + " && " +
            "mkdir " + name + " && " +
            "cp -r algraeph.app " + name + "/. && " +
            "cp ../COPYING " + name + "/. && " +
            "cp ../INSTALL " + name + "/. && " +
            "cp ../README " + name + "/. && " +
            "cp ../CHANGES " + name + "/. && " +
            "cp -r ../data " + name + "/. && " +
            "zip -r " + name + ".zip " + name + " --exclude '*svn*' && " +
            "rm -rf " + name )

subprocess.call(command, shell=True)


