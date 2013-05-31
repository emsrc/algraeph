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




class DotGraph(object):
    """
    Abstract base class for converting a DaesoGraph instance (a source/target
    graph aligned in a parallel graph corpus) or a GraphPair instance (a
    matching of source and target nodes) to a Graphviz dot graph.
    
    To avoid confusion about the term "graph", we will use the following
    naming convention:
    
        * dgraph: a dot graph, i.e. an DotGraph instance (including any of its
        subclasses)
        
        * stgraph: a target/source graph, i.e. a DaesoGraph instance (including
        subclasses like AlpinoGraph).
        
        * agraph: an alignment graph, i.e. a GraphPair instance
        
        * xgraph: a stgraph or agraph, i.e. any graph derived from networkx's
        DiGraph class.
        
    Analogously, we will use dnode, stnode, anode and xnode, as well as dedge,
    stedge, aedge, xedge.
    
    DotGraph provides update methods, like update_nodes or update_edges, which
    can be called to create/update specific parts of the dot graph. A full
    update is enforced by calling the update_structure method. Update methods
    usually take one or more nx_graph arguments, representing a source/target
    graph or a node alignment.

    The string defining the current dot graph can be obtained by callling the
    to_string method, which can be drawn using dot program
    """
    
    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------

    def __init__(self,
                 name="",
                 node_prefix="",
                 dgraph_attr={},
                 node_attr={},
                 edge_attr={}):
        """
        @keyword name: name of the dot graph
        
        @keyword node_prefix: a prefix string attached to a node to form the
            label of a dot node

        @keyword dgraph_attr: dict of default dot graph attributes

        @keyword node_attr: dict of default dot node attributes

        @keyword edge_attr: dict of default dot edge attributes
        
        See http://www.graphviz.org/doc/info/attrs.html
        """
        # node_prefix in used to distinguish source nodes from target nodes
        self.node_prefix = node_prefix
        self._init_view_options()
        
        self._start_graph(name)
        self.update_attribs(dgraph_attr, node_attr, edge_attr)
        self._init_structure()
        self._finish_graph()
        
        
    def label_edges_option(self, state=False):
        """
        set the label edges option, which determines whether of not edges are
        labeled
        """
        if state:
            self.edge_statement = self._labeled_edge_statement
        else:
            self.edge_statement = self._unlabeled_edge_statement
        
    
    def update_structure(self, xgraph):
        """
        update the whole dot graph
        """
        self.update_nodes(xgraph)
        self.update_edges(xgraph)

        
    def update_nodes(self, xgraph):
        node_statements = [ self._node_statement(xgraph, xnode) 
                            for xnode in xgraph 
                            if self._is_visible(xnode) ]
        self.nodes = "\n".join(node_statements)

        
    def update_edges(self, xgraph=()):
        edge_statements = [ self.edge_statement(xnode1, xnode2, xedge) 
                            for xnode1, xnode2, xedge in xgraph.edges(data=True)
                            if ( self._is_visible(xnode1) and
                                 self._is_visible(xnode2) ) ]
        self.edges = "\n".join(edge_statements)


    def update_attribs(self, dgraph_attr=None, node_attr=None, edge_attr=None):
        # either store the attribs or make all three args obligatory... 
        self.attribs = ""
        self._set_attribs('graph', dgraph_attr or self.dgraph_attr)
        self._set_attribs('node', node_attr or self.node_attr)
        self._set_attribs('edge', edge_attr or self.edge_attr)
        
        
    def to_string(self):
        return "\n".join(self._parts()) 
    
    # ------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------

    def _init_view_options(self):
        """
        reset all viewing options to their default value
        """
        self.label_edges_option()


    def _init_structure(self):
        self.nodes = self.edges = ""
        

    def _start_graph(self, name):
        self.head = 'strict digraph ' + name + ' {'  
        
        
    def _set_attribs(self, elem, dict):
        setattr(self, elem + "_attr", dict)

        # skip when empty
        if dict:
            # assume all values are strings, already quoted/escaped where neccessary
            self.attribs += "\n" + elem + self._attribs_str(dict)


    def _attribs_str(self, dict):
        return " [" + ",".join([ '%s="%s"' % t 
                                 for t in dict.iteritems() ]) + "];"
    
    
    def _is_visible(self, xnode):
        return True

        
    def _node_statement(self, xgraph, xnode, **kwargs):
        """
        get the statement for a dot node corresponding to a node (from a
        DaesoGraph or GrapPair instance)
        """
        kwargs["label"] = self._node_label(xgraph, xnode)
        kwargs["URL"] = dnode = self._dot_node(xnode)
        
        return ( dnode + 
                 " [" + 
                 ",".join('%s="%s"' % pair for pair in kwargs.iteritems()) +
                 "];" )
    
    
    def _node_label(self, xgraph, xnode):
        """
        get the label of a node (from a DaesoGraph or GrapPair instance)
        """
        label = xgraph.node[xnode].get("label", "")
        return label.replace('"', '\\"')

    
    def _dot_node(self, xnode):
        """
        get the dot node corresponding to a node (from a DaesoGraph or
        GrapPair instance)
        """
        return self.node_prefix + xnode


    def _labeled_edge_statement(self, xnode1, xnode2, xedge):
        """
        get the statement for a labeled dot edge corresponding to an edge
        (from a DaesoGraph or GrapPair instance)
        """
        return '%s -> %s [label="%s"];' % ( self._dot_node(xnode1),
                                            self._dot_node(xnode2),
                                            xedge["label"] )

    
    def _unlabeled_edge_statement(self,  xnode1, xnode2, xedge=None):
        """
        get the statement for a unlabeled dot edge corresponding to an edge
        (from a DaesoGraph or GrapPair instance)
        """
        return '%s -> %s;' % ( self._dot_node(xnode1),
                               self._dot_node(xnode2) )


    def _finish_graph(self):
        self.tail = '}'
        
        
    def _parts(self):
        return self.head, self.attribs, self.nodes, self.edges, self.tail

    

            
class DotSubGraph(DotGraph):
    """
    Abstract base class for converting a DaesoGraph instance (a source/target
    graph aligned in a parallel graph corpus) to a Graphviz dot graph.
    
    Adds support for marking the selected nodes. 
    """

    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------

    def mark_selected_nodes_option(self, state=False):
        """
        set the mark selected nodes option, which determines whether or not
        the currently selected source/target nodes are highlighted
        """
        if state:
            self.update_node_focus = self._update_node_focus
        else:
            self.update_node_focus = self._clear_node_focus

    # ------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------
        
    def _init_view_options(self):
        DotGraph._init_view_options(self)
        self.mark_selected_nodes_option()
        
        
    def _init_structure(self):
        DotGraph._init_structure(self)
        self.node_focus = ""
            

    def _start_graph(self, name):
        # A subgraph's name has the prefix "cluster", 
        # its nodes are drawn in a distinct rectangle of the layout.
        self.head = 'subgraph cluster_' + name + ' {'     
            
    
    def _parts(self):
        # adds self.node_focus
        return ( self.head, self.attribs, self.nodes, self.edges,
                 self.node_focus, self.tail )


    def _update_node_focus(self, stnode=None):
        if stnode:
            # adds additional formatting to node defined earlier
            self.node_focus = ( '%s [fillcolor="yellow",style="filled,rounded"];' %
                                self._dot_node(stnode))
        else:
            self._clear_node_focus()

            
    def _clear_node_focus(self, *args, **kwargs):
        self.node_focus = ""



class DotGraphPair(DotGraph):
    """
    Abstract base class for converting a GraphPair instance (a matching of
    source and target nodes) to a Graphviz dot graph.
    
    Adds support for marking the selected alignment and for marking aligned
    nodes.
    """
    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------

    def __init__(self,
                 name="",
                 node_prefix="",
                 graph_attr={},
                 node_attr={},
                 edge_attr={},
                 from_graph_attr={},
                 from_node_attr={},
                 from_edge_attr={},
                 to_graph_attr={},
                 to_node_attr={},
                 to_edge_attr={},
                 subgraph_class=DotSubGraph):

        self.from_node_prefix = "_from_"
        self.to_node_prefix = "_to_"
        
        self.from_subgraph = subgraph_class(
            name="from_graph",
            node_prefix=self.from_node_prefix, 
            dgraph_attr=from_graph_attr,
            node_attr=from_node_attr, 
            edge_attr=from_edge_attr)
        
        self.to_subgraph = subgraph_class(
            name="to_graph",
            node_prefix=self.to_node_prefix, 
            dgraph_attr=to_graph_attr,
            node_attr=to_node_attr, 
            edge_attr=to_edge_attr)

        DotGraph.__init__(self, name, node_prefix, graph_attr, node_attr,
                          edge_attr)
            

    def mark_selected_alignments_option(self, state=False):
        """
        set the mark selected alignments option, which determines whether of
        not the alignment between the currently selected nodes is highlighted
        """
        if state:
            self.update_edge_focus = self._update_edge_focus
        else:
            self.update_edge_focus = self.clear_edge_focus

            
    def mark_aligned_nodes_option(self, state=False):
        """
        set the mark aligned nodes option, which determines whether of
        not aligned nodes are marked (greyed)
        """
        self.mark_aligned = state
        
    
    def update_structure(self, agraph, from_graph, to_graph):
        self._update_tweak(agraph, from_graph, to_graph)
        self.update_nodes(agraph)
        self.update_edges(agraph)

        
    def update_nodes(self, agraph):
        # all nodes are by definition in the source and target graphs
        pass

    
    def update_edges(self, agraph=()):
        # calls _is_visible on subgraphs to check if edge should be drawn
        edge_statements = [ self.edge_statement(snode, tnode, aedge) 
                            for snode, tnode, aedge in agraph.edges(data=True)
                            if ( self.from_subgraph._is_visible(snode) and
                                 self.to_subgraph._is_visible(tnode) ) ]
        self.edges = "\n".join(edge_statements)

        
    def clear_edge_focus(self, *args, **kwargs):
        self.edge_focus = ""
    
    
    # ------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------
    
    def _init_view_options(self):
        DotGraph._init_view_options(self)
        self.mark_selected_alignments_option()
        self.mark_aligned_nodes_option()
        
        
    def _init_structure(self):
        DotGraph._init_structure(self)
        self.mark_selected_alignments_option()
        self.mark_aligned_nodes_option()
        self.tweak = ""
        
        
    def _update_tweak(self, agraph, from_graph, to_graph):
        # A hack to force dot to adhere to the left-to-right order of the two
        # graps. Adding this to the tail does NOT work! A dummy node is needed
        # because without it a manual alignment of the root nodes would always
        # be invisible.

        # root may be None for some types of graphs
        if from_graph.root and to_graph.root:
            from_dnode = self.from_subgraph._dot_node(from_graph.root)
            to_dnode = self.to_subgraph._dot_node(to_graph.root)
            self.tweak = ( "dummy [style=invis];\n" +
                           "%s-> dummy -> %s " % (from_dnode, to_dnode) + 
                           "[constraint=false, style=invis];\n" )


    def _labeled_edge_statement(self, snode, tnode, aedge):
        # calls subgraph._dot_node() to get the right node prefixes
        return '%s -> %s [label="%s"];' % ( self.from_subgraph._dot_node(snode),
                                            self.to_subgraph._dot_node(tnode),
                                            aedge)

    
    def _unlabeled_edge_statement(self, snode, tnode, aedge=None):
        # call subgraph._dot_node() to get the right node prefixes
        return '%s -> %s;' % ( self.from_subgraph._dot_node(snode),
                               self.to_subgraph._dot_node(tnode))

        
    def _parts(self):
        # add tweak, from_graph, to_graph and edge_focus
        return ( self.head,
                 self.attribs,
                 self.tweak,
                 self.from_subgraph.to_string(), 
                 self.to_subgraph.to_string(),
                 self.nodes, 
                 self.edge_focus,
                 self.edges, 
                 self.tail )


    def _update_edge_focus(self, snode, tnode):
        if ( snode and self.from_subgraph._is_visible(snode) and
             tnode and self.to_subgraph._is_visible(snode) ):
            self.edge_focus += "%s->%s [color=yellow];\n" % ( 
                self.from_subgraph._dot_node(snode),
                self.to_subgraph._dot_node(tnode) )

            
            
class BasicDotSubGraph(DotSubGraph):
    """
    Basic class for converting a DaesoGraph instance (a source/target graph
    aligned in a parallel graph corpus) to a Graphviz dot graph.
    
    This currently defines the basic support for all graph formats.
    """
    
    # ------------------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------------------
            
    def is_folded(self, stnode):
        return stnode in self.folded_nodes
                
    
    def toggle_node_fold(self, stgraph, stnode):
        """
        toggle node state, either from unfolded to folded or from folded to
        unfolded
        """
        if self.is_folded(stnode):
            self._unfold_node(stgraph, stnode)
        else:
            self._fold_node(stgraph, stnode)

            
    def unfold_all(self):
        # folded_nodes are nodes of which the subtree is folded,
        # but which are themselves still visible
        self.folded_nodes = set()
        # hidden_nodes are nodes which belong to a folded subtree,
        # and are therfore invisible
        self.hidden_nodes = set()
        self.folded = ''
        
        
    def update_folded(self):
        # render folded dnodes with a box 
        self.folded = ""
        # NB some shapes (e.g. diamond, and triangle) result in an image map
        # which is not correctly interpreted by wx.html.HtmlWindow,
        # so upon clicking the id returned is always "no_node"!!!
        
        for stnode in self.folded_nodes:
            # a folded node may have become a hidden node because one of its
            # precursors has been collapesed
            if stnode not in self.hidden_nodes:
                self.folded += '%s [shape=box];\n' % self._dot_node(stnode)
                
        
    # ------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------
        
    def _parts(self):
        # adds folded
        return ( self.head, 
                 self.attribs,
                 self.nodes, 
                 self.edges, 
                 self.node_focus,
                 self.folded, 
                 self.tail )
    
        
    def _init_structure(self):
        DotSubGraph._init_structure(self)
        # this also inits the sets
        self.unfold_all()
        
        
    def _update_node_focus(self, stnode=None):
        if self._is_visible(stnode):
            DotSubGraph._update_node_focus(self, stnode)
        else:
            # clear node focus even if stnode is None
            self._clear_node_focus()   
        
        
    def _is_visible(self, stnode):
        return ( DotSubGraph._is_visible(self, stnode) and
                 stnode not in self.hidden_nodes )
        
    # fold/unfold nodes
            
        
    def _fold_node(self, stgraph, stnode):
        self.folded_nodes.add(stnode)
        
        for child in stgraph.successors(stnode):
            # folding is *not* recursive
            self._hide_node(stgraph, child)
            
        ##self._update_folded()
            
            
    def _hide_node(self, stgraph, stnode):
        self.hidden_nodes.add(stnode)
        
        for child in stgraph.successors(stnode):
            # hiding *is* recursive
            self._hide_node(stgraph, child)
            
            
    def _unfold_node(self, stgraph, stnode):
        try:
            self.folded_nodes.remove(stnode)
        except KeyError:
            # node not folded
            return
        
        for child in stgraph.successors(stnode):
            self._reveal_node(stgraph, child)
            
        ##self._update_folded()
        
        
    def _reveal_node(self, stgraph, stnode):
        try:
            self.hidden_nodes.remove(stnode)
        except KeyError:
            return

        # unless this is itself a folded node, continue to reveal child nodes
        if stnode not in self.folded_nodes:
            for child in stgraph.successors(stnode):
                self._reveal_node(stgraph, child)
    
                
                
class BasicDotGraphPair(DotGraphPair):
    """
    Basic class for converting a GraphPair instance (a matching of source and
    target nodes) to a Graphviz dot graph.
    
    This currently defines the basic support for all graph formats.
    """
    
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
                                 pad=1.0
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
                                   subgraph_class=BasicDotSubGraph):
        
        DotGraphPair.__init__(self, name,
                              node_prefix, graph_attr, node_attr, edge_attr, from_graph_attr,
                              from_node_attr, from_edge_attr, to_graph_attr, to_node_attr,
                              to_edge_attr, subgraph_class)

        
    def hide_alignments_option(self, state=False):
        """
        set the hide alignments option, which determines whether of not all
        alignments are drawn
        """
        if state:
            self.update_edges = self._update_edges_hidden
        else:
            self.update_edges = self._update_edges
            
        
    def update_nodes(self, agraph):
        if self.mark_aligned:
            node_statements = []
            
            for from_node, to_node, rel in agraph.edges(data=True):
                if self.from_subgraph._is_visible(from_node):
                    from_dnode = self.from_subgraph._dot_node(from_node)
                    # not calling self._node_statement, because that requires
                    # a stnode instead of a dnode...
                    node_statements.append('%s [fontcolor=grey];' % from_dnode )
                    
                if self.to_subgraph._is_visible(to_node):
                    to_dnode = self.to_subgraph._dot_node(to_node)
                    node_statements.append('%s [fontcolor=grey];' % to_dnode)
                    
            self.nodes = "\n".join(node_statements)
        else:
            self.nodes = ""
        # All nodes are by definition in from_graph and to_graph,
        # so if aligned nodes are not marked,
        # there is no need to write them again. 
        
        
    # ------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------

    def _init_view_options(self):
        DotGraphPair._init_view_options(self)
        self.hide_alignments_option()
            

    def _update_edges(self, agraph):
        DotGraphPair.update_edges(self, agraph)
        
        
    def _update_edges_hidden(self, agraph):
        """
        Draw no edges
        """
        self.edges = ""

        
 