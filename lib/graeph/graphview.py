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



from os import getcwd
from os.path import basename, splitext

import wx.html

from graeph.pubsub import ( subscribe, save_subscribe, unsubscribe, send,
                            receive, is_subscribed )
from graeph.dotgraph import BasicDotGraphPair
from graeph.graphviz import ( update_image_file, update_image_map, get_html,
                              draw, get_output_formats )
    
    
class GraphView(wx.html.HtmlWindow):
    """
    Minimal class for viewing graphs
    """
    
    def __init__(self, parent, aligner, algraephFrame):
        wx.html.HtmlWindow.__init__(self, parent,
                                    style=wx.NO_FULL_REPAINT_ON_RESIZE|wx.SUNKEN_BORDER)
        self.aligner = aligner
        self.algraephFrame = algraephFrame

        self.initDotGraphPair()
        
        self.from_node_prefix = self.dotGraphPair.from_subgraph.node_prefix
        self.to_node_prefix = self.dotGraphPair.to_subgraph.node_prefix
        
        self.initViewMenu()
        self.replaceViewMenu()
        
        self.subscribe()
        
     
    def initDotGraphPair(self):
        """
        Initialize the dot visualization.
        Must be provided by any subclass of GraphView.
        """
        self.dotGraphPair = DotGraphPair()   
        

    def initViewMenu(self):
        """
        Initialise the context-sensitive pop-up menu for graph viewing options.
        Must be provided by any subclass fo GraphView. 
        """
        self.viewMenu = ViewMenu(self, self.aligner, self.algraephFrame)
        
        
    def replaceViewMenu(self):
        """
        Replace the View menu in the menu bar with the new View menu
        """
        menuBar = self.algraephFrame.GetMenuBar()
        pos = menuBar.FindMenu("View")
        menuBar.Replace(pos, self.viewMenu, "View")        

        
    def Destroy(self):
        # When a new corpus is loaded, the current GraphView object is destroyed 
        # and a new one  is initialised.
        # We need to unsubscibe the methods of the old object to make sure they
        # are no longer called by pubsub, which would result in a PyDeadObject exception.
        # Hence this override of Destroy.
        self.unsubscribe()
        wx.html.HtmlWindow.Destroy(self)
        
   
    def subscribe(self):
        """
        subscribe handlers for events send by aligner 
        """
        self.subscribe_stage_1()
        self.subscribe_stage_2()
        self.subscribe_stage_3()
        
        
    def subscribe_stage_1(self):
        pass
    
    def subscribe_stage_2(self):
        # newGraphPair
        subscribe(self.updateFromGraph, "newGraphPair.viz")
        subscribe(self.updateToGraph, "newGraphPair.viz")        
        subscribe(self.updateAlignment, "newGraphPair.viz")
        
        # newRelation
        subscribe(self.updateAlignment, "newRelation.viz")

    
    def subscribe_stage_3(self):
        # newGraphPair
        subscribe(self.updateImageFile, "newGraphPair.gui")
        subscribe(self.updateImageMap, "newGraphPair.gui")
        subscribe(self.updateHtmlPage, "newGraphPair.gui")
        
        # newRelation
        subscribe(self.updateImageFile, "newRelation.gui")
        subscribe(self.updateImageMap, "newRelation.gui")
        subscribe(self.updateHtmlPage, "newRelation.gui")
        
        
    def unsubscribe(self):
        # called when GraphView object is destoyed
        unsubscribe(self.updateFromGraph)
        unsubscribe(self.updateToGraph)
        unsubscribe(self.updateAlignment)
        unsubscribe(self.updateImageFile)
        unsubscribe(self.updateImageMap)
        unsubscribe(self.updateHtmlPage)
    
    # ------------------------------------------------------------------------------    
    # Event handlers
    # ------------------------------------------------------------------------------     

    def OnCellMouseHover(self, cell, x, y):
        # auto changing of cursor shape when mouse hovers over links seems to
        # fail with image maps, so implement explicitly here
        if cell.GetLink(x,y):
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        else:
            self.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        
    
    def OnCellClicked(self, cell, x, y, event):
        linkinfo = cell.GetLink(x, y)

        if event.RightUp():
            self.onViewPopupMenu(linkinfo, event)
        elif linkinfo:
            self.onNodeSelection(linkinfo)
            
        
    def onNodeSelection(self, linkinfo):
        node = linkinfo.GetHref()
        
        if node.startswith(self.from_node_prefix):
            node = node[len(self.from_node_prefix):]
            self.aligner.set_from_node(node)
        elif node.startswith(self.to_node_prefix):
            node = node[len(self.to_node_prefix):]
            self.aligner.set_to_node(node)

            
    def onViewPopupMenu(self, linkinfo, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.viewMenu, pos)            
    
    # ------------------------------------------------------------------------------                
    # ViewMenu handlers
    # ------------------------------------------------------------------------------          
        
    # no handlers because minimal ViewMenu is empty
    
    # ------------------------------------------------------------------------------    
    # Dotgraph updates
    # ------------------------------------------------------------------------------    

    def updateFromGraph(self, msg=None):  
        receive(self.updateFromGraph, msg)
        from_graph = self.aligner.get_from_graph()
        self.dotGraphPair.from_subgraph.update_structure(from_graph)

        
    def updateToGraph(self, msg=None): 
        receive(self.updateToGraph, msg)
        to_graph = self.aligner.get_to_graph()
        self.dotGraphPair.to_subgraph.update_structure(to_graph)

    
    def updateAlignment(self, msg=None):
        receive(self.updateAlignment, msg)
        from_graph = self.aligner.get_from_graph()
        to_graph = self.aligner.get_to_graph()
        graph_pair = self.aligner.get_graph_pair()
        self.dotGraphPair.update_structure(graph_pair, from_graph, to_graph)        
    
    # ------------------------------------------------------------------------------
    # Image(map) updates
    # ------------------------------------------------------------------------------

    def updateImageFile(self, msg=None):
        """
        call graphviz to update the image file
        """
        receive(self.updateImageFile, msg)
        update_image_file(self.dotGraphPair.to_string())

        
    def updateImageMap(self, msg=None):
        """
        call graphviz to update the image map
        """
        receive(self.updateImageMap, msg)
        update_image_map(self.dotGraphPair.to_string())

        
    def updateHtmlPage(self, msg=None):
        """
        reload html page and reposition scroll bars
        """
        receive(self.updateHtmlPage, msg)
        
        # Backup current scroll positions
        # This is not perfect, because the size of the image may change
        # (e.g. with or without dependency relation labels)
        xpos, ypos = self.GetViewStart()
        
        html = get_html()
        self.SetPage(html)
        
        # Restore scroll positions
        self.Scroll(xpos, ypos)
        

            
        
class BasicGraphView(GraphView):
    """
    Basic class for viewing graphs
    """
    
    def initDotGraphPair(self):
        self.dotGraphPair = BasicDotGraphPair()

    
    def initViewMenu(self):
        self.viewMenu = BasicViewMenu(self, self.aligner, self.algraephFrame)
        
        
    def subscribe_stage_1(self):
        GraphView.subscribe_stage_1(self)
        
        # newGraphPair
        subscribe(self.updateEdgeFocus, "newGraphPair.viz")
        subscribe(self.updateNodeFocus, "newGraphPair.viz")
        subscribe(self.unfoldAllNodes, "newGraphPair.viz")
        
        # newRelation
        subscribe(self.updateEdgeFocus, "newRelation.viz")
        
        # newNodeSelect
        subscribe(self.updateNodeFocus, "newNodeSelect.viz")
        subscribe(self.updateEdgeFocus, "newNodeSelect.viz")
        
        # newNodeSelect
        # ********* FIXME: following updates may be superfluous
        subscribe(self.updateAlignment, "newNodeSelect.viz")

        
    def subscribe_stage_3(self):
        GraphView.subscribe_stage_3(self)
        
        # newNodeSelect
        # ********* FIXME: following updates may be superfluous
        subscribe(self.updateImageFile, "newNodeSelect.gui")
        subscribe(self.updateHtmlPage, "newNodeSelect.gui")
        
        # foldNodeChanged
        subscribe(self.updateFromGraph, "foldNodeChanged")
        subscribe(self.updateToGraph, "foldNodeChanged")
        # hidden nodes may be focused or aligned, so we need to refresh
        # node focus, edge focus and aligment as well, which check themselves 
        # if any nodes have now become hidden   
        subscribe(self.updateNodeFocus, "foldNodeChanged")
        subscribe(self.updateEdgeFocus, "foldNodeChanged")
        subscribe(self.updateAlignment, "foldNodeChanged")
        subscribe(self.updateFolded, "foldNodeChanged")
        subscribe(self.updateImageFile, "foldNodeChanged")
        subscribe(self.updateImageMap, "foldNodeChanged")
        subscribe(self.updateHtmlPage, "foldNodeChanged")
        
        # unfoldAllNodes
        subscribe(self.unfoldAllNodes, "unfoldAllNodes")
        subscribe(self.updateFromGraph, "unfoldAllNodes")        
        subscribe(self.updateToGraph, "unfoldAllNodes")      
        subscribe(self.updateAlignment, "unfoldAllNodes")      
        subscribe(self.updateImageFile, "unfoldAllNodes")      
        subscribe(self.updateImageMap, "unfoldAllNodes")      
        subscribe(self.updateHtmlPage, "unfoldAllNodes")
        
        # markSelectedNodesChanged
        subscribe(self.updateNodeFocus, "markSelectedNodesChanged")
        subscribe(self.updateFromGraph, "markSelectedNodesChanged")
        subscribe(self.updateToGraph, "markSelectedNodesChanged")
        subscribe(self.updateImageFile, "markSelectedNodesChanged")
        subscribe(self.updateHtmlPage, "markSelectedNodesChanged")
        
        # markAlignedNodesChanged
        subscribe(self.updateAlignment, "markAlignedNodesChanged")
        subscribe(self.updateImageFile, "markAlignedNodesChanged")
        subscribe(self.updateHtmlPage, "markAlignedNodesChanged")
        
        # labelEdgesChanged
        subscribe(self.updateFromGraph, "labelEdgesChanged")
        subscribe(self.updateToGraph, "labelEdgesChanged")
        subscribe(self.updateImageFile, "labelEdgesChanged")
        subscribe(self.updateImageMap, "labelEdgesChanged")
        subscribe(self.updateHtmlPage, "labelEdgesChanged")
        
        # markSelectedAlignmentsChanged
        subscribe(self.updateEdgeFocus ,"markSelectedAlignmentsChanged")
        subscribe(self.updateAlignment ,"markSelectedAlignmentsChanged")
        subscribe(self.updateImageFile ,"markSelectedAlignmentsChanged")
        subscribe(self.updateHtmlPage ,"markSelectedAlignmentsChanged")
        
        # hideAlignmentsChanged
        subscribe(self.updateAlignment, "hideAlignmentsChanged")
        subscribe(self.updateImageFile, "hideAlignmentsChanged")
        subscribe(self.updateImageMap, "hideAlignmentsChanged")
        subscribe(self.updateHtmlPage, "hideAlignmentsChanged")
        
        # coSelectAlignedNodeChanged
        subscribe(self.updateCoSelectedNode, "coSelectAlignedNodeChanged")
        # self.updateCoSelectedNode() will trigger a "newNodeSelect",
        # so there is no need to subscribe others
        
        
        
    def unsubscribe(self):
        GraphView.unsubscribe(self)
        unsubscribe(self.unfoldAllNodes)
        unsubscribe(self.updateNodeFocus)
        unsubscribe(self.updateEdgeFocus)
        unsubscribe(self.updateCoSelectedNode)
        unsubscribe(self.updateFolded)
        
    # ------------------------------------------------------------------------------    
    # Event handlers
    # ------------------------------------------------------------------------------    
    
    def OnCellClicked(self, cell, x, y, event):
        linkinfo = cell.GetLink(x, y)
        
        # store node for possible use by onToggleFold        
        if linkinfo:
            self.node = linkinfo.GetHref()
        else:
            self.node = ""
        
        if event.ShiftDown():
            self.onToggleFold()
        else:
            GraphView.OnCellClicked(self, cell, x, y, event)
    
            
    def onViewPopupMenu(self, linkinfo, event):
        self.setFoldNodeItem(linkinfo)
        GraphView.onViewPopupMenu(self, linkinfo, event)
        self.resetFoldNodeItem()        

        
    def setFoldNodeItem(self, linkinfo):
        # enable and/or check the "Fold Node" menu item

        if self.node.startswith(self.from_node_prefix):
            node = self.node[len(self.from_node_prefix):]
            graph = self.aligner.get_from_graph()
            
            if graph.node_is_non_terminal(node):
                self.viewMenu.enableFoldNodeItem()
            
            if self.dotGraphPair.from_subgraph.is_folded(node):
                self.viewMenu.checkFoldNodeItem()
                
        elif self.node.startswith(self.to_node_prefix):
            node = self.node[len(self.to_node_prefix):]
            graph = self.aligner.get_to_graph()
            
            if graph.node_is_non_terminal(node):
                self.viewMenu.enableFoldNodeItem()
            
            if self.dotGraphPair.to_subgraph.is_folded(node):
                self.viewMenu.checkFoldNodeItem()
        
    
    def resetFoldNodeItem(self):
        # return to the default state, i.e.
        # disable and uncheck the "Fold Node" menu item
        self.viewMenu.disableFoldNodeItem()
        self.viewMenu.uncheckFoldNodeItem()

        
    def onToggleFold(self, evt=None):    
        if self.node.startswith(self.from_node_prefix):
            node = self.node[len(self.from_node_prefix):]
            graph = self.aligner.get_from_graph()
            
            if graph.node_is_terminal(node):
                return
            
            self.dotGraphPair.from_subgraph.toggle_node_fold(graph, node)
        elif self.node.startswith(self.to_node_prefix):
            node = self.node[len(self.to_node_prefix):]
            graph = self.aligner.get_to_graph()
            
            if graph.node_is_terminal(node):
                return
            
            self.dotGraphPair.to_subgraph.toggle_node_fold(graph, node)
        else:
            # Mouse not on a node. Should not happen, because in that case the
            # "Fold Node" menu item is disabled.
            return
        
        send(self.onToggleFold, "foldNodeChanged")
        
        
    def onUnfoldAllNodes(self, evt):
        """
        handler for the 'Unfold All Nodes' option in GraphmlViewMenu 
        """
        send(self.onUnfoldAllNodes, "unfoldAllNodes")
        
    # ------------------------------------------------------------------------------                
    # ViewMenu handlers
    # ------------------------------------------------------------------------------    
    
    def onMarkAlignedNodes(self, evt):
        """
        handler for the 'Mark Aligned Nodes" in the View menu
        """
        self.dotGraphPair.mark_aligned_nodes_option(evt.Checked())
        send(self.onMarkAlignedNodes, "markAlignedNodesChanged")
        send(self.onMarkAlignedNodes, "statusDescription", 
             "Mark Aligned Nodes option is %s" % evt.Checked())


    def onMarkSelectedNodes(self, evt):
        """
        handler for the 'Mark Selected Nodes" in the View menu
        """
        self.dotGraphPair.from_subgraph.mark_selected_nodes_option(evt.Checked())
        self.dotGraphPair.to_subgraph.mark_selected_nodes_option(evt.Checked())
        send(self.onMarkSelectedNodes, "markSelectedNodesChanged")
        send(self.onMarkSelectedNodes, "statusDescription", 
             "Mark Selected Nodes option is %s" % evt.Checked())
        
        
    def onCoSelectAlignedNode(self, evt):
        """
        handler for the 'Co-select Aligned Node' option in the View menu 
        """
        self.aligner.co_node_selection_mode(evt.Checked())
        send(self.onCoSelectAlignedNode, "coSelectAlignedNodeChanged")
        send(self.onCoSelectAlignedNode, "statusDescription", 
             "Co-select Aligned Node option is %s" % evt.Checked())
            

    def onLabelEdges(self, evt):
        """
        handler for the 'Label Edges' option in the View menu 
        """
        self.dotGraphPair.from_subgraph.label_edges_option(evt.Checked())
        self.dotGraphPair.to_subgraph.label_edges_option(evt.Checked())
        send(self.onLabelEdges, "labelEdgesChanged")
        send(self.onLabelEdges, "statusDescription", 
             "Label Edges option is %s" % evt.Checked())
        
        
    def onMarkSelectedAlignments(self, evt):
        """
        handler for the 'Mark Selected Alignments' option in View menu 
        """
        self.dotGraphPair.mark_selected_alignments_option(evt.Checked())
        send(self.onLabelEdges, "markSelectedAlignmentsChanged")
        send(self.onMarkSelectedAlignments, "statusDescription", 
             "Mark Selected Alignments option is %s" % evt.Checked())
        
    
    def onHideAlignments(self, evt):
        """
        handler for the 'Hide Alignments' option in View menu 
        """
        self.dotGraphPair.hide_alignments_option(evt.Checked())
        send(self.onHideAlignments, "hideAlignmentsChanged")
        send(self.onHideAlignments, "statusDescription", 
             "Hide Alignments option is %s" % evt.Checked())
        
        
    def onSaveImage(self, evt):
        """
        handler for the 'Save Image' option in View menu 
        """
        formats = get_output_formats()
        
        if "png" in formats:
            formats.remove("png")
            formats = ["png"] + formats
        else:
            formats.remove("dot")
            formats = ["dot"] + formats
            
        wildcard = ""
        
        for s in formats:
            wildcard += s + " (*." + s + ")|" + "*." + s + "|"
            
        wildcard = wildcard[:-1]
        
        filename = self.aligner.get_corpus_filename()
        filename = splitext(basename(filename))[0]
        filename += "_%d" % self.aligner.get_graph_pair_counter()[0]
        filename += "." + formats[0]
        
        dlg = wx.FileDialog(self, "Save image...", 
                            defaultFile=filename,
                            defaultDir=self.aligner.get_corpus_dir() or getcwd(),
                            style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT,
                            wildcard =wildcard)
        
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            if " " in file:
                file = '"' + file + '"'
            form = formats[dlg.GetFilterIndex()]
            
            send(self.onSaveImage, "statusDescription", "Saving image to file %s ..." % file)
            draw(self.dotGraphPair.to_string(), img_file=file, img_format=form)
            send(self.onSaveImage, "statusDescription", "Saved image to file %s" % file)
            
        dlg.Destroy()

            
    ## Some experimental code to draw on the screen
    ##def OnCellMouseHover(self, cell, x, y):
        ##try:
            ##print cell.GetLink(x,y).GetHref()
            ##print cell.GetLink(x,y).GetTarget()
            
            ##dc = wx.ClientDC(self)
            ##dc.DrawCircle(100,100,25)
            
        ##except:
            ##pass
            
                    
    # ------------------------------------------------------------------------------    
    # Dotgraph updates
    # ------------------------------------------------------------------------------    
    
    def unfoldAllNodes(self, msg=None):
        receive(self.unfoldAllNodes, msg)
        
        self.dotGraphPair.from_subgraph.unfold_all()
        self.dotGraphPair.to_subgraph.unfold_all()
        
        
    def updateFolded(self, msg):
        receive(self.updateFolded, msg)
        
        self.dotGraphPair.from_subgraph.update_folded()
        self.dotGraphPair.to_subgraph.update_folded()
        
        
    def updateCoSelectedNode(self, msg=None):
        receive(self.updateCoSelectedNode, msg)
        
        from_node = self.aligner.get_from_node()
        
        if from_node:
            self.aligner.set_from_node(from_node)
        else:
            to_node = self.aligner.get_to_node()
        
            if to_node:
                self.aligner.set_to_node(to_node)

         
    def updateNodeFocus(self, msg=None): 
        receive(self.updateNodeFocus, msg)

        from_graph = self.aligner.get_from_graph()
        to_graph = self.aligner.get_to_graph()
        
        from_node = self.aligner.get_from_node()
        self.dotGraphPair.from_subgraph.update_node_focus(from_node)
        
        to_node = self.aligner.get_to_node()
        self.dotGraphPair.to_subgraph.update_node_focus(to_node)
        
        
    def updateEdgeFocus(self, msg=None): 
        receive(self.updateEdgeFocus, msg)
        
        self.dotGraphPair.clear_edge_focus()  
        
        from_node = self.aligner.get_from_node()
        to_node = self.aligner.get_aligned_to_node()
        self.dotGraphPair.update_edge_focus(from_node, to_node) 
        
        to_node= self.aligner.get_to_node()
        from_node = self.aligner.get_aligned_from_node()
        self.dotGraphPair.update_edge_focus(from_node, to_node) 

        

        
        
        
class ViewMenu(wx.Menu):
    """
    Minimal class for (empty) pop-up menu with (no) viewing options
    
    self.graphView (a subclass of GraphView) must provide handlers for all
    wx.EVT_MENU. However, binding must occur at the level of algraephFrame,
    otherwise menu events from the View menu in the menu bar will be
    unhandled! 
    """
    
    def __init__(self, graphView, aligner, algraephFrame):
        wx.Menu.__init__(self) 
        self.graphView = graphView
        self.aligner = aligner
        self.algraephFrame = algraephFrame
        
        self.makeMenu()
        
        
    def makeMenu(self):
        """
        subclasses must implement this method for adding menu items
        """
        pass

    
    def isChecked(self, item_text):
        """
        returns True if a menu itme with this name is checked
        """
        for item in self.GetMenuItems():
            if item.GetItemLabelText() == item_text:
                return item.IsChecked()
            
            
        
class BasicViewMenu(ViewMenu):
    """
    Basic class for pop-up menu with basic viewing options
    """    
    
    def checkFoldNodeItem(self):
        self.Check(self.fold_item_id, True)
  
    def uncheckFoldNodeItem(self):
        self.Check(self.fold_item_id, False)


    def enableFoldNodeItem(self):
        self.Enable(self.fold_item_id, True)
        
    def disableFoldNodeItem(self):
        self.Enable(self.fold_item_id, False)    
        
        
    def makeMenu(self):
        self.appendFoldOptions()
        self.AppendSeparator()
        self.appendNodeViewOptions()
        self.AppendSeparator()
        self.appendEdgeViewOptions()
        self.AppendSeparator()
        self.appendAlignmentViewOptions()
        self.AppendSeparator()
        self.appendOtherViewOptions()


    def appendFoldOptions(self):
        fold_item = self.Append(-1, 
                                "&Fold Node",
                                "Hide all descendants of this node",
                                wx.ITEM_CHECK)
        self.fold_item_id = fold_item.GetId()
        self.disableFoldNodeItem()
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onToggleFold,
                                fold_item)
        
        
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onUnfoldAllNodes,
                                self.Append(-1, 
                                            "&Unfold All Nodes\tCtrl-U",
                                            "Reveal all descendants of all nodes"))        
        
    def appendNodeViewOptions(self):
        item = self.Append(-1, 
                           "Mark Aligned &Nodes",
                           "Mark nodes which are already aligned",
                           wx.ITEM_CHECK)
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onMarkAlignedNodes,
                                item)
        
        item = self.Append(-1, 
                           "&Mark Selected Nodes\tCtrl-M",
                           "Highlight currently selected nodes",
                           wx.ITEM_CHECK)
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onMarkSelectedNodes,
                                item)
        
        item = self.Append(-1, 
                           "&Co-select Aligned Node\tCtrl-K",
                           "Automatically select the aligned node in the other graph",
                           wx.ITEM_CHECK)
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onCoSelectAlignedNode,
                                item)
        
        
    def appendEdgeViewOptions(self):
        item = self.Append(-1, 
                           "&Label Edges",
                           "Label edges with relations",
                           wx.ITEM_CHECK)
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onLabelEdges,
                                item)
        
        
    def appendAlignmentViewOptions(self):
        item = self.Append(-1, 
                           "Mark Selected &Alignments\tCtrl-A",
                           "Highlight the currently selected alignments",
                           wx.ITEM_CHECK)
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onMarkSelectedAlignments,
                                item)
        
        item = self.Append(-1, 
                           "&Hide Alignments\tCtrl-H",
                           "Hides all alignments except those of the selected nodes(s)",
                           wx.ITEM_CHECK)
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onHideAlignments,
                                item)
        
        
    def appendOtherViewOptions(self):
        self.algraephFrame.Bind(wx.EVT_MENU,
                                self.graphView.onSaveImage,
                                self.Append(-1, 
                                            "Save &Image",
                                            "save current image of graphs to a file"))

 
# this funny statement is to trick py2exe into including these modules
# in the list of dependencies when building an exe
if False:
    from graeph.alpino import graphview, dotgraph
    from graeph.graphml import graphview, dotgraph