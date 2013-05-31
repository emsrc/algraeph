# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2013 by 
# Erwin Marsi and TST-Centrale
#
#
# This file is part of the Algraeph program.
#
# The Algraeph program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# The Algraeph program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
provides a wrapper to call graphviz programs through a subprocess pipe 
"""

__author__ = "Erwin Marsi <e.marsi@gmail.com>"



from subprocess import Popen, PIPE
from os import close, unlink, environ
from tempfile import mkstemp
from atexit import register
from sys import platform

from graeph.log import graphviz_logger as log
from graeph.pubsub import send


class GraphvizError(Exception):
    # TODO derive from AlgraephError
    pass



__graphviz_exec = "dot"
__img_format = "png"

tmp_fd, __img_file = mkstemp(suffix="." + __img_format)
close(tmp_fd)
register(unlink, __img_file)

__img_map = None

__no_node = "no_node"


# The Grahviz installer for Mac OS X puts dot in /usr/local/bin.
# The default PATH for an App run from the GUI is /bin:/usr/bin.
# Hence this Mac-specific hack to extend the path.
if platform == "darwin":
    environ["PATH"] += ":/usr/local/bin"


def set_graphviz_exec(graphviz_exec):
    """
    set the name of the graphviz executable,
    possibly a full path
    """
    global __graphviz_exec
    __graphviz_exec = graphviz_exec
    
    
def get_output_formats(graphviz_exec=None):
    """
    return a list of all output formats supported by graphviz
    """
    command = ( graphviz_exec or __graphviz_exec) + " -Txxx"
    proc = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)   
    stdout, stderr = proc.communicate()
    
    if '"xxx" not recognized' in stderr:
        stderr = stderr.split("Use one of:")[-1]
        return stderr.split()
    else:
        raise GraphvizError(stderr)

    
def draw(graph, graphviz_exec=None, img_format=None, img_file=__img_file):
    """
    draw graph using graphviz
    """
    log.debug("call to daeso.graphviz.draw")
    # output graph just once, as cmap is never updated without an image update first
    if img_format != "cmap":
        log.debug("graph=\n" + graph)
    
    # FIXME: on Mac OS X, when the applications is build with py2app , the
    # subprocess shell does NOT read ~/.bashrc or ~/.profile, and therefore
    # the PATH variable contains only the system wide definition from
    # /etc/profile, that is PATH="/bin:/sbin:/usr/bin:/usr/sbin".
    # Hence a dot in /opt/local/bin or /usr/local/bin will NOT be found.
    # Perhaps add some smart searching here?
    if not graphviz_exec:
        graphviz_exec =  __graphviz_exec
        
    # tricky: the defaults for function parameters are initialized only once,
    # and are therefore not updated when __grapviz_exec or __img_format change!
    command = "%s -T %s" % ( graphviz_exec, ( img_format or __img_format ) )
    
    if img_file: command += " -o " + img_file

    log.debug(command)
    
    # Due to a bug in subprocess, we have to assign an explicit handle to all streams
    # See http://www.py2exe.org/index.cgi/Py2ExeSubprocessInteractions
    proc = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # Drawing can be slow, so it is crucial to use communicate,
    # which waits for the process to complete.
    
    # Graph must be utf8 encoded on OS X, otherwise weird errors.    
    stdout, stderr = proc.communicate(graph.encode("utf-8"))
    
    log.debug("stdout=\n" + stdout)
    log.debug("stderr=\n" + stderr)
    
    if stderr:
        if "command not found" in stderr:
            stderr += ( "\nThe graphviz program '%s' " % graphviz_exec +
                        "is not in your path: %s \n" % environ.get("PATH") +
                        "Add the directory containing this program "
                        "to your PATH environment variable, "
                        "or use the '--graphviz' command line option "
                        "to supply the path to this program.")
        raise GraphvizError(stderr)
    
    # stdout will be empty when output goes to a file 
    return stdout


def update_image_file(graph):
    log.debug("call to daeso.graphviz.update_image_file")
    send(update_image_file, "statusDescription", "Loading image...")
    draw(graph)
    send(update_image_file, "statusDescription")

    
def update_image_map(graph):
    log.debug("call to daeso.graphviz.update_image_map")
    global __img_map
    send(update_image_map, "statusDescription", "Loading image map...")
    __img_map = draw(graph, img_format="cmap", img_file=None)
    send(update_image_map, "statusDescription")


def get_html():
    log.debug("call to daeso.graphviz.get_html")
    return ( '<map name="graph">\n%s\n</map>\n' % __img_map +
             '<img src="%s" border="0" usemap="#graph">' % __img_file)    


