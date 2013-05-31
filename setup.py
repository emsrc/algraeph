#!/usr/bin/env python

"""
distutils setup script for distributing Algraeph source

To install Algraeph sources:

    $ python setup.py install
    
or:

    $ python setup.py install --prefix ~/tmp
    
    
To build an Algraeph source distribution:

    $ python setup.py sdist
"""

from distutils.core import setup
from imp import load_source
from os import remove, walk
from os.path import exists, join
from shutil import rmtree

# "from graeph import release" won't work 
release = load_source("release", "lib/graeph/release.py")

if exists('MANIFEST'): remove('MANIFEST')
if exists("build"): rmtree("build")

sdist_options = dict( 
    dist_dir="dist-sdist",
    formats=["zip","gztar","bztar"],)


# data and doc dirs get installed under sys.prefix/share/algraeph-x.x
data_dir = join("share", "%s-%s" % (release.name, release.version))
data_files = [(data_dir, ["README", "INSTALL", "COPYING", "CHANGES"])]

for top in ("doc", "data"):
    for dir_path, dirs, files in walk(top):
        if not ".svn" in dir_path: 
            install_dir = join(data_dir, dir_path)
            files = [ join(dir_path, fname)
                      for fname in files
                      if not "*~" in fname ]
            data_files.append((install_dir, files))

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
    requires = ["networkx", "wx", "daeso", "daeso_nl"],
    provides = ["%s (%s)" % (release.name, release.version)],
    platforms = "POSIX, Mac OS X, MS Windows",
    scripts = ["bin/%s.py" % release.name],
    data_files = data_files,
    options = dict(
        sdist = sdist_options),
)

    


