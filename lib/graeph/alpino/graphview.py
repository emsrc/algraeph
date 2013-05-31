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
subclasses of GraphView and ViewMenu specific to Alpino format
"""

__author__ = "Erwin Marsi <e.marsi@gmail.com>"



import wx

from graeph.graphview import BasicGraphView, BasicViewMenu
from graeph.pubsub import subscribe, unsubscribe, send, receive
from graeph.alpino.dotgraph import AlpinoDotGraphPair


class AlpinoGraphView(BasicGraphView):
    """
    Graph viewer for graph pairs in Alpino format
    """
    
    def __init__(self, parent, aligner, algraephFrame):
        BasicGraphView.__init__(self, parent, aligner, algraephFrame)
        self.Bind(wx.EVT_CHAR, self.onChar)
        
        
    def initDotGraphPair(self, msg=None):
        """
        Initialize the dot visualization for Alpino graphs
        """
        self.dotGraphPair = AlpinoDotGraphPair()

        
    def initViewMenu(self, msg=None):
        """
        Initialise the pop-up menu for Alpino graph viewing options
        """
        self.viewMenu = AlpinoViewMenu(self, self.aligner, self.algraephFrame)
        
    
    def subscribe_stage_1(self):
        BasicGraphView.subscribe_stage_1(self) 
        subscribe(self.updateAutoFolded, "newGraphPair.viz") 
        subscribe(self.updateFolded, "newGraphPair.viz")  
        subscribe(self.updateAutoFolded, "autoFoldEqualsChanged")
        
        
    def subscribe_stage_3(self):
        # NB order of subscripton is relevant
        BasicGraphView.subscribe_stage_3(self)
        
        # orderNodesChanged
        subscribe(self.updateFromGraph, "orderNodesChanged")
        subscribe(self.updateToGraph, "orderNodesChanged")
        subscribe(self.updateImageFile, "orderNodesChanged")
        subscribe(self.updateImageMap, "orderNodesChanged")
        subscribe(self.updateHtmlPage, "orderNodesChanged")
        
        # autoFoldEqualsChanged
        subscribe(self.updateFromGraph, "autoFoldEqualsChanged")
        subscribe(self.updateToGraph, "autoFoldEqualsChanged")
        subscribe(self.updateAlignment, "autoFoldEqualsChanged")
        subscribe(self.updateFolded, "autoFoldEqualsChanged")
        subscribe(self.updateImageFile, "autoFoldEqualsChanged")
        subscribe(self.updateImageMap, "autoFoldEqualsChanged")
        subscribe(self.updateHtmlPage, "autoFoldEqualsChanged")
        
        
    def unsubscribe(self):
        BasicGraphView.unsubscribe(self)
        unsubscribe(self.updateAutoFolded)

        
    # ------------------------------------------------------------------------------    
    # Event handlers
    # ------------------------------------------------------------------------------ 
        
    def onOrderNodes(self, evt):
        """
        handler for the 'Order Nodes' option in AlpinoViewMenu 
        """
        self.dotGraphPair.from_subgraph.order_nodes_option(evt.Checked())
        self.dotGraphPair.to_subgraph.order_nodes_option(evt.Checked())
        send(self.onOrderNodes, "orderNodesChanged")
        
        
    def onAutoFoldEquals(self, evt):
        """
        handler for the 'Auto Fold Equals' option in AlpinoViewMenu 
        """
        send(self.onAutoFoldEquals, "autoFoldEqualsChanged")
        
        
    def onChar(self, evt):
        # TODO: this is an hack that relies on the Daeso relation set 
        # - should be solved in a better way 
        keycode = evt.GetKeyCode()
        
        if keycode < 256:
            char = chr(keycode)
        else:
            char = None
        
        if char == "n":
            try:
                self.aligner.set_node_pair_relation("none")
            except KeyError:
                # nodes were not aligned
                pass
        elif char == "e":
            self.aligner.set_node_pair_relation("equals")
        elif char == "r":
            self.aligner.set_node_pair_relation("restates")
        elif char == "g":
            self.aligner.set_node_pair_relation("generalizes")
        elif char == "s":
            self.aligner.set_node_pair_relation("specifies")
        elif char == "i":
            self.aligner.set_node_pair_relation("intersects")
        else:
            evt.Skip()
    
    # ------------------------------------------------------------------------------    
    # Dotgraph updates
    # ------------------------------------------------------------------------------    
    
    def updateAutoFolded(self, msg=None):
        receive(self.updateAutoFolded, msg)

        if self.viewMenu.isChecked("Auto Fold Equals"):  
            from_graph = self.aligner.get_from_graph()
            to_graph = self.aligner.get_to_graph()

            from_equal_nodes, to_equal_nodes = \
            self.aligner.get_auto_fold_equal_nodes()
        
            for from_node in from_equal_nodes:
                self.dotGraphPair.from_subgraph._fold_node(from_graph, from_node)
                
            for to_node in to_equal_nodes:
                self.dotGraphPair.to_subgraph._fold_node(to_graph, to_node)
        else:
            # Unfolding only the auto-folded nodes is difficult, because one
            # or more predecessors of an auto-folded nody may have been be
            # manually folded. We obviously cannot unfold a subtree without
            # unfolding the folded predecesors as well. Keeping track of these
            # relations would require a lot of administration. Instead we just
            # unfold all nodes.
            self.dotGraphPair.from_subgraph.unfold_all()
            self.dotGraphPair.to_subgraph.unfold_all()
            
            

            

class AlpinoViewMenu(BasicViewMenu):
    """
    Pop-up menu with viewing options for Alpino graphs
    
    Adds node ordering option to the standard menu 
    """
        
    
    def appendFoldOptions(self):
        BasicViewMenu.appendFoldOptions(self)
        
        item = self.Append(-1, 
                           "Auto Fold Equals",
                           "Automatically fold all nodes that are aligned with "
                           "with an equals relation",
                           wx.ITEM_CHECK)        
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onAutoFoldEquals,
                                item)    
        
        #self.auto_fold_equals_item_id = item.GetId()
        
        
    def appendNodeViewOptions(self):
        BasicViewMenu.appendNodeViewOptions(self)
        
        item = self.Append(-1, 
                           "&Order Nodes",
                           "Force the nodes to appear in strict order",
                           wx.ITEM_CHECK)
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onOrderNodes,
                                item)
        
        
        
     