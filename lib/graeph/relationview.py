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

from pubsub import subscribe, receive


class RelationView(wx.RadioBox):

    
    def __init__(self, parent, aligner):
        wx.RadioBox.__init__(self, parent, choices=aligner.get_relation_set(),
                             majorDimension=2, style=wx.RA_SPECIFY_COLS)
        self.Enable(False)
        self.Bind(wx.EVT_RADIOBOX, self.onRelationRadiobox)
        self.aligner = aligner
        self.subscribe()


    # ------------------------------------------------------------------------------
    # update handlers
    # ------------------------------------------------------------------------------
        
    def subscribe(self):
        subscribe(self.updateRelation, "newGraphPair.gui")                
        subscribe(self.updateRelation, "newNodeSelect.gui")
        
        # Updating on newRelation seems redundant, but is required
        # when the relation is changed by another method than the radio buttons,
        # e.g. using shortcut keys
        subscribe(self.updateRelation, "newRelation.gui")


    def updateRelation(self, msg=None):
        receive(self.updateRelation, msg)
        relation = self.aligner.get_node_pair_relation()
        self.SetStringSelection(relation)
        
        if self.aligner.nodes_are_selected():
            self.Enable(True)
        else:
            self.Enable(False)


    # ------------------------------------------------------------------------------
    # event handlers
    # ------------------------------------------------------------------------------
    
    def onRelationRadiobox(self, evt):
        relation = self.GetStringSelection()
        self.aligner.set_node_pair_relation(relation)

