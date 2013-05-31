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

     
class TokenView(wx.TextCtrl):        

    def __init__(self, parent, aligner, color):
        # wx.TE_RICH2 is required to get coloured text on MSW
        wx.TextCtrl.__init__(self, parent, -1, size=(-1,50),
                             style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        # Disable TokenView???
        # Pro:
        # - draws focus, so scrolling the graph window with mouse wheel does not work
        # - prevents blinking cursor 
        # Contra:
        # - disabling turns background grey on MSW
        # - prevents copy on OSX
        #self.Enable(False)
        self.SetForegroundColour(color)
        self.aligner = aligner
        self.subscribe()
        
    
    def subscribe(self):
        subscribe(self.updateTokens, "newGraphPair.gui")
        
        
    def updateTokens(self, msg=None):
        receive(self.updateTokens, msg)   
        self.SetValue(self.getTokens())
        

        
class FromGraphTokenView(TokenView):
    
    def getTokens(self):
        return self.aligner.get_from_graph_tokens()
    
        
        
class ToGraphTokenView(TokenView):
    
    def getTokens(self):
        return self.aligner.get_to_graph_tokens()
    
    
    
class FromNodeTokenView(TokenView):
    
    def subscribe(self):
        TokenView.subscribe(self)
        subscribe(self.updateTokens, "newNodeSelect.gui")
        
    def getTokens(self):
        return self.aligner.get_from_node_tokens()
    
        
        
class ToNodeTokenView(TokenView):
    
    def subscribe(self):
        TokenView.subscribe(self)
        subscribe(self.updateTokens, "newNodeSelect.gui")
    
    def getTokens(self):
        return self.aligner.get_to_node_tokens()
        
        
