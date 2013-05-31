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
dotgraph subclasses specific to Graphml format
"""

__author__ = "Erwin Marsi <e.marsi@gmail.com>"




from graeph.dotgraph import BasicDotSubGraph, BasicDotGraphPair


class GraphmlDotSubGraph(BasicDotSubGraph):
    pass



class GraphmlDotGraphPair(BasicDotGraphPair):
    
    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------

    def __init__(self,
                 name="",
                 node_prefix="",
                 graph_attr=dict(splines="true", 
                                 #ordering="out",
                                 ranksep=0.25,
                                 nodesep=0.1,
                                 # size of margin depends on particular version of dot...
                                 #margin=-0.25
                                 ),
                 node_attr=dict(fontname="sans",
                                fontsize="9",
                                #style="bold",
                                height=".1",
                                shape="plaintext"),
                 edge_attr=dict(fontname="sans",
                                color="limegreen", 
                                fontsize="8",
                                weight="0",
                                constraint="false"
                                #arrowhead="none",
                                #style="dashed,bold"
                                #headclip="false",
                                #tailclip="false"
                                ),
                 from_graph_attr=dict(color="white", 
                                      #ordering="out"
                                      ),
                 from_node_attr=dict(fontcolor="blue"),
                 from_edge_attr=dict(weight="100",
                                     style="solid",
                                     color="gray",
                                     arrowhead="none",
                                     constraint="true",
                                     #headclip="true",
                                     #tailclip="true",                               
                                     ),
                 to_graph_attr=dict(color="white",
                                    #ordering="out"
                                    ),
                 to_node_attr=dict(fontcolor="red"),
                 to_edge_attr=dict(weight="100",
                                   style="solid",
                                   color="gray",
                                   arrowhead="none",
                                   constraint="true",
                                   #headclip="true",
                                   #tailclip="true",                                
                                   ),
                                   subgraph_class=GraphmlDotSubGraph):
        
        BasicDotGraphPair.__init__(self, name,
                                   node_prefix, graph_attr, node_attr, edge_attr, from_graph_attr,
                                   from_node_attr, from_edge_attr, to_graph_attr, to_node_attr,
                                   to_edge_attr, subgraph_class)
