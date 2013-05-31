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


__author__ = "Erwin Marsi <e.marsi@gmail.com>"



import wx
import wx.html

from sys import prefix
from os import getcwd, getenv
from os.path import dirname, exists, join as pathjoin, normpath



class HelpViewFrame(wx.Frame):
    
    def __init__(self, parent, title): 
        wx.Frame.__init__(self, parent, title=title, size=(600,600))
        self.html = wx.html.HtmlWindow(self)
        
        
    def loadDoc(self, appName, appVersion, docName):
        
        (path, failed_paths) = self.findDocs(appName, appVersion, docName)
        
        if path:
            self.html.LoadFile(path)
        else:
            msg = "<b>Error: cannot find documentation at any of the following locations</b><br><br>"
            msg += "<br>".join(failed_paths)
            self.html.SetPage(msg) 
        
        self.Show()

        
    def findDocs(self, appName, appVersion, docName): 
        search_paths = [getcwd()]
        
        # are we in the DAESO dev tree?
        if getenv("DAESO_BASE",""):
            unix_path = "trunk/software/intern/%s/doc" % appName
            os_path = pathjoin(getenv("DAESO_BASE",""), normpath(unix_path)) 
            search_paths.append(os_path)
            
        # are we in a standard bin dir with docs in ../doc ?
        os_path = normpath(pathjoin(getcwd(), "../doc"))
        search_paths.append(os_path)
            
        # are we a source distribution? 
        unix_path = "share/%s-%s/doc" % (appName, appVersion)
        os_path = pathjoin(prefix, normpath(unix_path))
        search_paths.append(os_path)
            
        # are we a Mac OS X application bundle?
        if getenv("RESOURCEPATH"):
            search_paths.append(getenv("RESOURCEPATH"))
            
        # are we a MS Win binary from iss installer?
        os_path = pathjoin(getcwd(), "doc")
        search_paths.append(os_path)
        
        failed_paths = []
        
        for path in search_paths:
            path = pathjoin(path, docName)
            if exists(path):
                return (path, None)
            failed_paths.append(path)
        else:
            return (None, failed_paths)
        