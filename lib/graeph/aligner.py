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



from xml.etree.cElementTree import SubElement
from os.path import dirname

from daeso.pgc.corpus import ParallelGraphCorpus
from daeso.pair import Pair

from graeph.pubsub import send
from graeph.exception import AlgraephException


class Aligner(object):
    """
    the Algraeph application model 
    """
    
    def __init__(self):
        self._corpus = ParallelGraphCorpus()
        # the domain model
        self._changed = False
        self._filename = None
        self._graph_pair = None
        self._graph_pair_index = None
        self._graphs = Pair(None, None)
        self._nodes = Pair(None, None)
        # the special relation which stands for "no relation"
        self._no_relation = "none"
        self._co_node_selection = False
        
    # ------------------------------------------------------------------------------
    # Corpus
    # ------------------------------------------------------------------------------

    def open_corpus(self, filename):
        send(self.open_corpus, "statusDescription", "Loading corpus %s ..." % filename)

        # May raise errors such IOErrors, not an xml file, corrupt format, etc.
        # Use of relax_gb_paths allows graphbank files to be located in the
        # same direcory as the corpus file instead of the location specified
        # in the <file> element
        corpus = ParallelGraphCorpus()
        corpus.read(inf=filename, relax_gb_paths=True)
        
        if not corpus:
            raise AlgraephException("Parallel graph corpus contains no alignments")
        
        self._corpus = corpus
        self._filename = filename
        self._changed = False
            
        send(self.open_corpus, "statusDescription")
        send(self.open_corpus, "newCorpus")
        send(self.open_corpus, "newCorpusName")

        self.goto_graph_pair(0)
        # implies send("newGraphPair"), and sets self._graph_pair,
        # self._graph_pair_index, self._graphs and self._nodes

        
    def save_corpus(self, filename=None):
        if filename:
            self._filename = filename
            send(self.save_corpus, "newCorpusName")
            
        send(self.save_corpus, "statusDescription", "Saving corpus %s ..." % self._filename)        
        
        self._corpus.write(self._filename, pprint=True)
        self._changed = False
            
        send(self.save_corpus, "statusDescription")
        
        
    def get_corpus_len(self):
        return len(self._corpus)
    

    def get_corpus_filename(self):
        return self._filename

    
    def get_corpus_dir(self):
        try:
            return dirname(self._filename)
        except (AttributeError, TypeError):
            return None
    
    
    def corpus_changed(self):
        """
        returns True if the corpus has unsaved changes
        """
        return self._changed
        
    
    # ------------------------------------------------------------------------------
    # Treebanks
    # ------------------------------------------------------------------------------    
 
    def get_graphbanks_format(self):
        # The ParallelGraphCorpus class in principle supports graphbanks in
        # different formats, although untested for the time being. Formats are
        # therefore stored as a property of the graphbanks, but there is no
        # global format defined as a property of the corpus. So getting "the
        # graphbanks format" is not straightforward. We will make the
        # assumption that all graphbanks are in the same format, and there it
        # is sufficient to look at any graphbank linked to an arbitary graph
        # pair.
        return self._corpus[0].get_source_bank().get_format()
        
    # ------------------------------------------------------------------------------
    # Graphs (GraphPair and DaesoGraph)
    # ------------------------------------------------------------------------------    
    
    def get_graph_pair(self):
        return self._graph_pair
    
    
    def goto_prev_graph_pair(self):
        self.goto_graph_pair(self._graph_pair_index - 1)

    def goto_next_graph_pair(self):
        self.goto_graph_pair(self._graph_pair_index + 1)
        
        
    def goto_graph_pair(self, index):
        # don't use try-except here, because negative index is allowed for list
        if 0 <= index < len(self._corpus):
            self._graph_pair = self._corpus[index]
            self._graph_pair_index = index
            self._graphs = self._graph_pair.get_graphs()
            self._nodes = Pair(None, None)
            
            send(self.goto_graph_pair, "newGraphPair.viz")
            send(self.goto_graph_pair, "newGraphPair.gui")
    
        
    def get_from_graph(self):
        return self._graphs.source
    
    def get_to_graph(self):
        return self._graphs.target
    
        
    def get_from_graph_tokens(self):
        return self._graphs.source.get_graph_token_string()
        
    def get_to_graph_tokens(self):
        return self._graphs.target.get_graph_token_string()
    
    
    def get_graph_pair_counter(self):
        # counting starts from 1
        return (self._graph_pair_index + 1, len(self._corpus))
        
    
    # ------------------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------------------
    
    def co_node_selection_mode(self, state=False):
        self._co_node_selection = state
        
    
    def set_from_node(self, node=None):
        self._nodes.source = node
        
        if self._co_node_selection:
            self._nodes.target = self.get_aligned_to_node()
            
        send(self.set_from_node, "newNodeSelect.viz")
        send(self.set_from_node, "newNodeSelect.gui")

        
    def set_to_node(self, node=None):
        self._nodes.target = node
        
        if self._co_node_selection:
            self._nodes.source = self.get_aligned_from_node()
            
        send(self.set_to_node, "newNodeSelect.viz")
        send(self.set_to_node, "newNodeSelect.gui")
            
    
    def get_from_node(self):
        return self._nodes.source

    
    def get_to_node(self):
        return self._nodes.target
    
    
    def nodes_are_selected(self):
        return all(self._nodes)
    
    
    def get_from_node_tokens(self):
        return ( self._graphs.source.get_node_token_string(self._nodes.source) or
                 "" )
        
    
    def get_to_node_tokens(self):
        return ( self._graphs.target.get_node_token_string(self._nodes.target) or
                 "" )
    
    # ------------------------------------------------------------------------------
    # Alignment
    # ------------------------------------------------------------------------------
    
    def get_relation_set(self):
        try:
            return [self._no_relation] + self._corpus.get_relations()
        except TypeError:
            return [self._no_relation]
        
        
    def get_node_pair_relation(self):
        return self._graph_pair.get_align(self._nodes) or self._no_relation
    
        
    def set_node_pair_relation(self, relation):
        if self.nodes_are_selected():
            if relation != self._no_relation:
                self._graph_pair.add_align(self._nodes, relation)
            else:
                self._graph_pair.del_align(self._nodes)
                
            self._changed = True
                
            send(self.set_node_pair_relation, "newRelation.viz")
            send(self.set_node_pair_relation, "newRelation.gui")
    

    def get_aligned_to_node(self):
        """
        Get 'to' node aligned to the selected 'from' node
        """
        return self._graph_pair.get_aligned_target_node(self._nodes.source)
    
    
    def get_aligned_from_node(self):
        """
        Get 'from' node aligned to the selected 'to' node
        """
        return self._graph_pair.get_aligned_source_node(self._nodes.target)

    
    def get_auto_fold_equal_nodes(self):
        """
        Get lists of non-terminal 'from' and 'to' nodes aligned with an 
        'equals' relation
        """
        # ignoring terminals, so the list may be of unequal size
        from_nodes = []
        to_nodes = []
        
        for (nodes, rel) in self._graph_pair.alignments_iter():
            if rel == "equals":
                if self._graphs.source.node_is_non_terminal(nodes.source):
                    from_nodes.append(nodes.source)
                    
                if self._graphs.target.node_is_non_terminal(nodes.target):
                    to_nodes.append(nodes.target)
                    
        return from_nodes, to_nodes
        
    #------------------------------------------------------------------------------
    # Comments
    #------------------------------------------------------------------------------    
        
    def get_comment(self):
        try:
            return self._graph_pair.get_meta_data().find("comment").text
        except AttributeError:
            return ""

    
    def set_comment(self, text):
        meta_data_elem = self._graph_pair.get_meta_data()
        comment_elem = meta_data_elem.find("comment")
        
        if text.strip():
            if comment_elem is None:
                comment_elem = SubElement(meta_data_elem, "comment")
            comment_elem.text = text
        elif comment_elem:
            meta_data_elem.remove(comment_elem)
            
        self._changed = True

