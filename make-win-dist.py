#!/usr/bin/env python

"""
Create a stand-alone MS Windows distribution of Algraeph

Assumes that the graeph, daeso, daeso_nl and networkx packages are
installed (i.e. available through sys.path or PYTHONPATH).
Retrieves version and other info from graeph.release.
"""    
import glob
import sys
import os
import shutil
import subprocess

# setup function seems to ignore its script_args keyword, so add py2app
# command to argv *before* importing setup
sys.argv.append("py2exe")

from distutils.core import setup
import py2exe

from graeph import release


shutil.rmtree("build", ignore_errors=True)

try:
    os.remove("MANIFEST")
except os.error:
    pass

data_files = [ # include MSVC runtime dll
              ("Microsoft.VC90.CRT", glob.glob("py26_ms_dlls/*")),
               # include gdiplus.dll required by wxpython
              ("", ["py26_wx_dlls/gdiplus.dll"]) ]

py2exe_options = dict(
    dist_dir = "dist-win",
    # ElementTree is not automatically included in the dependencies,
    packages = ["daeso", "daeso_nl", "xml.etree"],
    # to prevent an py2exe error message about not finding this dll
    dll_excludes = ["MSVCP90.dll"],
    bundle_files = 1)

setup(
    name = release.name,
    version = release.version,
    description = release.description,
    long_description = release.long_description,
    author = release.author,
    author_email = release.author_email,
    url = release.url,
    license = release.license,
    packages = ["graeph", "graeph.alpino", "graeph.graphml"],
    package_dir = { "" : "lib" },
    windows = ["bin/algraeph.py"],
    platforms = "MS Windows",
    data_files = data_files,
    zipfile = None,
    options = dict(
        py2exe = py2exe_options)
)


# some brute-force cleaning
# when not using bundle_files=1 and zipfile=None
# shutil.rmtree("dist-win/tcl")

# for name in "tk85.dll tcl85.dll _tkinter.pyd".split():
#    os.remove("dist-win/" + name)

# Create MS Windows installer using Inno setup
# Check the info in iss\algraeph.iss
os.system("iss\\run.bat")
