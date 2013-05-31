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
subclasses of GraphView and ViewMenu specific to Graphml format
"""

__author__ = "Erwin Marsi <e.marsi@gmail.com>"



import wx

from graeph.graphview import BasicGraphView, BasicViewMenu
from graeph.pubsub import subscribe, unsubscribe, send, receive
from graeph.graphml.dotgraph import GraphmlDotGraphPair


class GraphmlGraphView(BasicGraphView):
    """
    Graph viewer for graph pairs in Graphml format
    """
     
    
    def initDotGraphPair(self, msg=None):
        """
        Initialize the dot visualization for Graphml graphs
        """
        self.dotGraphPair = GraphmlDotGraphPair()

        
    def initViewMenu(self, msg=None):
        """
        Initialise the pop-up menu for Graphml graph viewing options
        """
        self.viewMenu = GraphmlViewMenu(self, self.aligner, self.algraephFrame)
        




class GraphmlViewMenu(BasicViewMenu):
    """
    Pop-up menu with viewing options for Graphml graphs
    """
    pass
    