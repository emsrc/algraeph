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
dotgraph subclasses specific to Alpino format
"""


__author__ = "Erwin Marsi <e.marsi@gmail.com>"



from graeph.dotgraph import BasicDotSubGraph, BasicDotGraphPair


class AlpinoDotSubGraph(BasicDotSubGraph):
    
    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------
        
    def order_nodes_option(self, state=False):
        if state:
            self.update_nodes = self._update_nodes_ordered
        else:
            self.update_nodes = self._update_nodes
            
    # ------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------

    def _init_view_options(self):
        BasicDotSubGraph._init_view_options(self)
        self.order_nodes_option()


    def _update_nodes(self, stgraph):
        self._update_ignored_nodes(stgraph)
        return BasicDotSubGraph.update_nodes(self, stgraph)
    
            
    def _update_nodes_ordered(self, stgraph):
        self._update_ignored_nodes(stgraph)
        self.nodes = ""
        
        # the trick to enforce a partcicular node order in dot is to put all
        # nodes at the same rank and to connect them by an invisible egde
        for node in stgraph:
            if self._is_visible(node):
                self.nodes += self._node_statement(stgraph, node)  + "\n"
                same_rank = []
                
                for suc in stgraph.successors_iter(node):
                    if self._is_visible(suc):
                        same_rank.append(self._dot_node(suc))
                
                if same_rank:
                    self.nodes += ( "\n{ rank=same; " + 
                                    "; ".join(same_rank) + 
                                    "};\n" +
                                    "->".join(same_rank) +
                                    " [style=invis];\n" )  

        
    def _update_ignored_nodes(self, stgraph):
        self._ignored_nodes = set([ 
            stnode 
            for stnode in stgraph 
            if ( stgraph.node_is_punct(stnode) or 
                 stgraph.node_is_index(stnode) ) ])
       
        
    def _node_label(self, stgraph, stnode):
        # tweak node label to become the word rather than the pos for
        # terminals
        if stgraph.node_is_terminal(stnode):
            label = stgraph.node[stnode].get("word", "")
        else:
            label = stgraph.node[stnode].get("label", "")
            
        return label.replace('"', '\\"') 

    
    def _node_statement(self, stgraph, stnode):
        if stgraph.node_is_terminal(stnode):
            return BasicDotSubGraph._node_statement(self, stgraph, stnode)
        else:
            return BasicDotSubGraph._node_statement(self, stgraph, stnode,
                                                    fontcolor="black")
   
        
    def _is_visible(self, stnode):
        return ( BasicDotSubGraph._is_visible(self, stnode) and
                stnode not in self._ignored_nodes )
    
    


class AlpinoDotGraphPair(BasicDotGraphPair):
    
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
                                constraint="false",
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
                                   subgraph_class=AlpinoDotSubGraph):
        
        BasicDotGraphPair.__init__(self, name, node_prefix, 
                                   graph_attr, node_attr, edge_attr, 
                                   from_graph_attr, from_node_attr, from_edge_attr,
                                   to_graph_attr, to_node_attr, to_edge_attr, 
                                   subgraph_class)
        
        