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

from graeph.pubsub import subscribe, receive

        
class CommentView(wx.TextCtrl):
    
    def __init__(self, parent, aligner):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.onEvtText)
        self.aligner = aligner
        self.subscribe()
        
    
    def subscribe(self):
        subscribe(self.updateText, "newGraphPair.gui")
        
        
    def updateText(self, msg=None):
        receive(self.updateText, msg)
        
        text = self.aligner.get_comment()
        
        # text received from aligner has \n for newlines
        if wx.Platform == "__WXMSW__": 
            text = text.replace("\n", "\r\n")
            
        self.SetValue(text)
        

    def onEvtText(self, evt):  
        text = self.GetValue()

        # Each time a "newGraphPair" is send, 
        # subscribed self.updateText is called, 
        # which calls self.SetValue,
        # which causes an EVT_TEXT, 
        # which calls current function,
        # which would cause a call to self.aligner.set_comment,
        # which would toggle the self.aligner._changed attribute,
        # even though the text in unchanged!
        # Hence, we check for a real change here to prevent spurious changes. 
        if text != self.aligner.get_comment():
            # text passed to aligner is assumed to have \n for newlines
            if wx.Platform == "__WXMSW__": 
                text = text.replace("\r\n", "\n")

            self.aligner.set_comment(text)
        