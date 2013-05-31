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
from os.path import basename, dirname

import wx
from wx.lib.splitter import MultiSplitterWindow

from graeph.aligner import Aligner
from graeph.tokenview import (FromGraphTokenView, ToGraphTokenView,
                                    FromNodeTokenView, ToNodeTokenView)
from graeph.graphview import GraphView
from graeph.relationview import RelationView
from graeph.commentview import CommentView
from graeph.helpview import HelpViewFrame
from graeph.pubsub import subscribe, receive
from graeph import release




class AlgraephFrame(wx.Frame):
    wildcard = "Parallel Graph Corpus (*.pgc)|*.pgc|Parallel Graph Corpus (*.xml)|*.xml"
    
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title="Algraeph")

        self.initModel()
        
        self.makeMenuBar()
        self.makeSplits()
        self.makeStatusBar()
        
        self.subscribe()

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Maximize()
        
        
    def initModel(self):
        self.aligner = Aligner()
        
        
    def subscribe(self):
        subscribe(self.updateStatusbar, "statusDescription") 
        subscribe(self.updateStatusbarCounter, "newGraphPair.gui") 
        subscribe(self.updateSplitterWindow, "newCorpus")
        subscribe(self.updateWindowTitle, "newCorpusName")   
        subscribe(self.updateDisabledWidgets, "newCorpus")        
        

    # ------------------------------------------------------------------------
    # widget construction methods
    # ------------------------------------------------------------------------
        
    def makeSplits(self):
        splitter1 = wx.SplitterWindow(self, style=wx.SP_3DSASH)
        graphTokens = GraphTokenPanel(splitter1, self.aligner)
               
        splitter2 = wx.SplitterWindow(splitter1, -1, style=wx.SP_3DSASH) 
        self.graphView = GraphViewPanel(splitter2, self.aligner, self)
        bottom = BottomPanel(splitter2, self.aligner)
        
        splitter1.SetMinimumPaneSize(graphTokens.GetBestSize()[1])
        splitter2.SetMinimumPaneSize(bottom.GetBestSize()[1])
        
        splitter2.SetSashGravity(1.0)
        
        splitter1.SplitHorizontally(graphTokens, splitter2, graphTokens.GetBestSize()[1])
        splitter2.SplitHorizontally(self.graphView, bottom, bottom.GetBestSize()[1])
        
        # save for resizing when the numbr of relations in bottom panel changes
        self.splitterWindow = splitter2
        
        
    def menuData(self):
        return ( ("&File",
                  dict(text="&Open\tCtrl-O", help="Open corpus", handler=self.onMenuOpen),
                  dict(text="&Save\tCtrl-S", help="Save corpus", handler=self.onMenuSave, enable=False),
                  dict(text="Save &As", help="Save corpus as", handler=self.onMenuSaveAs, enable=False),
                  dict(text="&Quit\tCtrl-Q", help="Quit", handler=self.onClose, id=wx.ID_EXIT)),
                  ("&Go",
                   dict(text="&Prev\tCtrl-P", help="Previous graph pair", handler=self.onMenuPrev, enable=False),
                   dict(text="&Next\tCtrl-N", help="Next graph pair", handler=self.onMenuNext, enable=False),
                   dict(text="&Goto\tCtrl-G", help="Goto graph pair", handler=self.onMenuGoto, enable=False)),
                   ("&View", ),
                   ("&Help",
                    dict(text="&Algraeph User Manual\tCtrl-?", help="Read online user manual", 
                         handler=self.onMenuHelp, id=wx.ID_HELP),
                    dict(text="Algraeph &License", help="Read online license", 
                         handler=self.onMenuLicense),
                    dict(text="&About Algraeph", help="Information about Algraeph", 
                         handler=self.onMenuAbout, id=wx.ID_ABOUT))
                     )

    
    def makeMenuBar(self):                     
        menuBar = wx.MenuBar() 
        self.disabledMenuItems = []
        
        for eachMenuData in self.menuData(): 
            menuLabel = eachMenuData[0] 
            menuItems = eachMenuData[1:] 
            menuBar.Append(self.makeMenu(menuItems), menuLabel)
        
        self.SetMenuBar(menuBar)


    def makeMenu(self, menuData):                                 
        menu = wx.Menu() 
        
        for data in menuData: 
            if not data: 
                menu.AppendSeparator() 
                continue 
            
            menuItem = menu.Append(id=data.get("id", -1), 
                                   text=data["text"],
                                   help=data.get("help", ""),
                                   kind=data.get("kind", wx.ITEM_NORMAL)) 
            self.Bind(wx.EVT_MENU, data["handler"], menuItem)
            
            if not data.get("enable", True):
                menuItem.Enable(False)
                self.disabledMenuItems.append(menuItem)
                
            
        return menu    
    

    def makeStatusBar(self):
        self.statusBar = self.CreateStatusBar() 
        self.statusBar.SetFieldsCount(2) 
        self.statusBar.SetStatusWidths([-3, -1]) 
        
    # ------------------------------------------------------------------------
    # event methods
    # ------------------------------------------------------------------------
    
    #def onNew(self, evt):
    #    pass
    
    def onMenuOpen(self, evt):
        try:
            if not self.saveChanges():
                return
        except:
            # Error is reported by saveChanges.
            # Return and hope that user can solve the error
            # otherwise the system is locked
            return
        
        dlg = wx.FileDialog(self, "Open corpus...", 
                            self.aligner.get_corpus_dir() or getcwd(),
                            style=wx.FD_OPEN,
                            wildcard = self.wildcard)
        
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.openCorpus(filename)
            
        dlg.Destroy()

        
    def onMenuSave(self, evt):
        self.aligner.save_corpus()

        
    def onMenuSaveAs(self, evt):
        dlg = wx.FileDialog(self, "Save corpus as...", 
                            self.aligner.get_corpus_dir() or getcwd(),
                            style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT,
                            wildcard = self.wildcard)
        
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.aligner.save_corpus(filename)
            
        dlg.Destroy()
        
        
    def onMenuPrev(self, evt):
        self.aligner.goto_prev_graph_pair()

        
    def onMenuNext(self, evt):
        self.aligner.goto_next_graph_pair()
        
        
    def onMenuGoto(self, evt):
        dlg = wx.TextEntryDialog(self, 'Goto graph pair number:', 'Goto')

        if dlg.ShowModal() == wx.ID_OK:
            try:
                i = int(dlg.GetValue())
            except ValueError:
                pass
            else:
                # aligner ignores out-of-bounds index
                self.aligner.goto_graph_pair(i - 1)

        dlg.Destroy()        
        
    
    def onMenuHelp(self, evt):
        help_frame = HelpViewFrame(self, title="Algraeph User Manual") 
        help_frame.loadDoc(release.name, release.version, "algraeph-user-manual.htm")
        
        
    def onMenuLicense(self, evt):
        lic_frame = HelpViewFrame(self, title="Algraeph License") 
        lic_frame.loadDoc(release.name, release.version, "GPL.html")
    

    def onMenuAbout(self, evt):
        
        info = wx.AboutDialogInfo()
        info.AddDeveloper("%s <%s>" % (release.author, release.author_email))
        info.SetName(release.name)
        info.SetDescription("%s\n%s" % (release.description, release.url))
        info.SetVersion(release.version)
        info.SetCopyright("Copyright %s\nReleased under %s" % 
                          (release.copyright, release.license))
        #info.SetWebSite("https://github.com/emsrc/algraeph")
        wx.AboutBox(info)

        
    def onClose(self, evt):
        self.Destroy()

        
    def Destroy(self):
        try:
            if self.saveChanges():
                wx.Frame.Destroy(self)                
        except:
            # Error is reported by saveChanges.
            # Return and hope that user can solve the error
            # otherwise the system is locked
            return

        
    #-------------------------------------------------------------------------------
    # Listeners
    #-------------------------------------------------------------------------------
    
    def updateStatusbar(self, msg=None):
        # subscriptions:
        # - statusDescription
        
        receive(self.updateStatusbar, msg)
        self.statusBar.SetStatusText(msg.data or "Ready", 0)
        
        
    def updateStatusbarCounter(self, msg=None):
        # subscriptions:
        # - statusDescription
        receive(self.updateStatusbarCounter, msg)
        self.statusBar.SetStatusText("%d of %d graph pairs" % self.aligner.get_graph_pair_counter(), 1)

        name = self.aligner.get_corpus_filename()
        
        if name:
            self.SetTitle("Algraeph:  %s  (%s)" % ( basename(name), dirname(name)))
        else:
            self.SetTitle("Algraeph")

            
    def updateWindowTitle(self, msg=None):
        # subscriptions: 
        # - newCorpus      
        receive(self.updateWindowTitle, msg)
        name = self.aligner.get_corpus_filename()
        
        if name:
            self.SetTitle("Algraeph: %s (%s)" % (basename(name), dirname(name)))
        else:
            self.SetTitle("Algraeph")
            
        
    def updateSplitterWindow(self, msg=None):
        # subscriptions: 
        # - newCorpus        
        receive(self.updateSplitterWindow, msg)
        bottom = self.splitterWindow.GetWindow2()
        bestSize = bottom.GetBestSize()[1]
        self.splitterWindow.SetMinimumPaneSize(bestSize)
        self.splitterWindow.SetSashPosition(-bestSize)
        
        
    def updateDisabledWidgets(self,  msg=None):
        # subscriptions: 
        # - newCorpus
        receive(self.updateDisabledWidgets, msg)
        
        for menuItem in self.disabledMenuItems:
            menuItem.Enable(True)

        
    #-------------------------------------------------------------------------------
    # Support methods
    #-------------------------------------------------------------------------------
    
    # file
    
    def openCorpus(self, filename):
        try:
            self.aligner.open_corpus(filename)
        except Exception, inst:
            # assume aligner will reset the corpus to a valid state
            self.reportError(str(inst))
            raise
    
    def saveChanges(self):
        """
        Checks if changes need to saved.
        Returns True if 
        1. corpus is unchanged, or
        2. changes are succesfully saved, or
        3. user opted to discard changes
        Returns False if user cancelled.
        Raises an exception if saving failed for some reason,
        and reports the error to the user
        """
        if self.aligner.corpus_changed():
            dlg = wx.MessageDialog(self,
                                   'The corpus has been modified. Save changes?',
                                   'Save',
                                    wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)            
            reply = dlg.ShowModal() 
            
            if reply == wx.ID_YES:
                try:
                    self.aligner.save_corpus()
                except Exception, inst:
                    # notify user
                    self.reportError(str(inst))
                    # pass on exception so caller can handle it as well 
                    raise
                finally:
                    dlg.Destroy()
                    
                state = True
            elif reply == wx.ID_NO:
                state = True
            elif reply == wx.ID_CANCEL:
                state = False
            
            dlg.Destroy()
        else:
            state = True

        return state
    
    
    # warning & error
            
    def reportError(self, message, caption="Error"):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

        
        


class GraphTokenPanel(wx.Panel):
    
    def __init__(self, parent, aligner):
        wx.Panel.__init__(self, parent)
        self.aligner = aligner
        
        fromGraphTokens = FromGraphTokenView(self, aligner, "Blue")
        toGraphTokens = ToGraphTokenView(self, aligner, "Red")
                
        sizer = wx.BoxSizer(wx.HORIZONTAL)        
        sizer.Add(fromGraphTokens, 1, wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT,
                  border=10)
        sizer.Add(toGraphTokens, 1, wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT,
                  border=10)
        self.SetSizer(sizer)

        
class GraphViewPanel(wx.Panel):
    
    def __init__(self, parent, aligner, algraephFrame):
        wx.Panel.__init__(self, parent)
        self.aligner = aligner
        self.algraephFrame = algraephFrame

        # initialise to empty text box as long as no graphbank is loaded
        self.graphView = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.SUNKEN_BORDER)
        self.graphView.Disable()

        self.subscribe()
        
        sizer = wx.BoxSizer() 
        sizer.Add(self.graphView, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        self.SetSizer(sizer)   
    
        
    def subscribe(self):
        subscribe(self.initGraphView, "newCorpus")

        
    def initGraphView(self, msg=None):
        """
        Initialise the graph viewer with a subclass of GraphView 
        appropriate for the format of the graphs in the graph bank
        """
        # we need to know the format of graphs in the graphbanks
        format = self.aligner.get_graphbanks_format()
        assert isinstance(format, basestring)
        
        # import the graph viewer for this format using the following convention:
        # if the format is "abc", 
        # then import a class "AbcGraphView from the module graeph.abc

        formatModuleName = "graeph.%s.graphview" % format
        formatClassName = "%sGraphView" %  format.capitalize()

        # FIXME: this might mask other errors - should be more specific
        try:
            formatModule = __import__(formatModuleName, fromlist=[formatClassName])
            formatClass = getattr(formatModule, formatClassName)
        except (ImportError, AttributeError):
            # handled by top-level 
            raise #AssertionError('No graph viewer class for treebank in %s format' % format)
        
        # In order to properly refresh the panel,
        # we must remove the previous self.graphView from the GraphiewPanel's sizer,
        # reassign a viewer to self.graphView,
        # add it to the sizer,
        # and call the sizer's Layout method
        sizer = self.GetSizer()
        self.graphView.Destroy()
        sizer.Clear(deleteWindows=True)
        self.graphView = formatClass(self, self.aligner, self.algraephFrame)
        sizer.Add(self.graphView, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        sizer.Layout()

        
   
class BottomPanel(wx.Panel):
    
    def __init__(self, parent, aligner):
        wx.Panel.__init__(self, parent)
        self.aligner = aligner
        
        notebook = wx.Notebook(self)
        
        aAlignPage = AlignPage(notebook, self.aligner) 
        aCommentPage = CommentPage(notebook, self.aligner)
        
        sizer = wx.BoxSizer()        
        sizer.Add(notebook, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        self.SetSizer(sizer)
        
        self.subscribe()
        
        self.Disable()

        
    def subscribe(self):
        subscribe(self.updateDisabledWidgets, "newCorpus")           
        
        
    def updateDisabledWidgets(self, msg):
        # subscriptions: 
        # - newCorpus
        receive(self.updateDisabledWidgets, msg)
        self.Enable()
    
    
class AlignPage(wx.Panel):
    """
    the page (tab) called "Align" in the notebook at the bottom panel 
    """
    
    def __init__(self, parent, aligner):
        wx.Panel.__init__(self, parent)
        self.aligner = aligner
        
        parent.AddPage(self, 'Align')    
        
        fromNodeTokens = FromNodeTokenView(self, self.aligner, "Blue") 
        self.relView = RelationView(self, self.aligner)
        toNodeTokens = ToNodeTokenView(self, self.aligner, "Red")
        
        sizer = wx.BoxSizer()
        sizer.Add(fromNodeTokens, 1, wx.EXPAND|wx.LEFT|wx.BOTTOM, border=10)
        sizer.Add(self.relView, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        sizer.Add(toNodeTokens, 1, wx.EXPAND|wx.RIGHT|wx.BOTTOM, border=10)
        self.SetSizer(sizer)

        self.subscribe()
        
        
    def subscribe(self):
        subscribe(self.initRelationView, "newCorpus")
        
        
    def initRelationView(self, msg=None):
        receive(self.initRelationView, msg)
        sizer = self.GetSizer()
        sizer.Detach(self.relView)
        self.relView.Destroy()
        self.relView = RelationView(self, self.aligner)
        sizer.Insert(1, self.relView, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        sizer.Layout()
        
        
        

class CommentPage(wx.Panel):
    """
    the page (tab) called "Comment" in the notebook at the bottom panel 
    """
    
    def __init__(self, parent, aligner):
        wx.Panel.__init__(self, parent)
        self.aligner = aligner     
        
        parent.AddPage(self, 'Comment')
        
        aCommentView = CommentView(self, aligner)
        
        sizer = wx.BoxSizer()
        sizer.Add(aCommentView, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        self.SetSizer(sizer)
        
        
        

class Algraeph(wx.App):
    
    def __init__(self, cl_args=None, redirect=False, filename=None):
        self.cl_args = cl_args
        wx.App.__init__(self, redirect=redirect, filename=filename)


    def OnInit(self):
        self.algraephFrame = AlgraephFrame()        
        self.algraephFrame.Show()
        self.SetTopWindow(self.algraephFrame)
        
        if self.cl_args:
            self.handleCommandLineOptions()
            
        return True

    
    def handleCommandLineOptions(self):
        if self.cl_args.dot_exec:
            from graphviz import set_graphviz_exec
            set_graphviz_exec(self.cl_args.dot_exec)
            
        if self.cl_args.corpus_file:
            self.algraephFrame.openCorpus(self.cl_args.corpus_file)
            
    