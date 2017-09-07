import sys
import logging
import os
import wx

import subprocess
from os.path import isdir, join


class OPEXUploaderGUI(wx.Frame):

    def __init__(self,parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(600,500))
        self.panel = wx.Panel(self)
        pos_x = [20,150]
        pos_y = 30
        line_height = 30
        self.dirname = None

        self.dblabel = wx.StaticText(self.panel, label="Enter Database config :", pos=(pos_x[0], pos_y))
        self.dbedit = wx.TextCtrl(self.panel, value="xnat-dev", pos=(pos_x[1], pos_y), size=(140, -1))
        pos_y += line_height
        self.projectlabel = wx.StaticText(self.panel, label="Enter Project code : ", pos=(pos_x[0], pos_y))
        self.projectedit = wx.TextCtrl(self.panel, pos=(pos_x[1], pos_y), size=(140, -1))
        pos_y += line_height
        self._inputdir = wx.Button(self.panel, label='Choose a directory containing input files', pos=(pos_x[0], pos_y))
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self._inputdir)
        pos_y += line_height
        self.inputlabel = wx.StaticText(self.panel, label="Input dir :", pos=(pos_x[0], pos_y))
        self.inputedit = wx.TextCtrl(self.panel, pos=(pos_x[1], pos_y), size=(340, -1))
        self.Bind(wx.EVT_TEXT, self.EvtInput, self.inputedit)

        pos_y += line_height
        self.optionlist = {'Help': '--help',
                           'Test Connection': '--projects',
                           'CANTAB': '--cantab' ,
                           'AMUNET': '--amunet',
                           'ACE-R': '--acer',
                           'MRIscans': '--mri',
                           'ASHS and Freesurfer': '--mridata'}
        self.runoptionslabel = wx.StaticText(self.panel, label="Select option : ", pos=(pos_x[0], pos_y))
        self.runoptions = wx.ComboBox(self.panel, pos=(pos_x[1], pos_y), size=(150, -1), choices=self.optionlist.keys(), style=wx.CB_DROPDOWN)
        pos_y += line_height
        self._cbCreateSubject = wx.CheckBox(self.panel, label='Create Subjects from data', pos=(pos_x[0], pos_y))
        pos_y += line_height
        self._cbSkiprows = wx.CheckBox(self.panel, label='Skip rows with ABORTED or NOT_RUN', pos=(pos_x[0], pos_y))
        pos_y += line_height
        self._cbChecks = wx.CheckBox(self.panel, label='Test run with validation checks', pos=(pos_x[0], pos_y))
        pos_y += line_height
        self._cbUpdate = wx.CheckBox(self.panel, label='Also update existing expts', pos=(pos_x[0], pos_y))
        self.CreateStatusBar()  # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Input", " Select input directory")
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about this program")
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")  # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Show(True)

        # A button
        self.submit = wx.Button(self.panel, label="Run", pos=(200, 325))
        self.Bind(wx.EVT_BUTTON, self.OnSubmit, self.submit)


    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "Upload OPEX data to XNAT\n(c)2017 QBI Software", "About OPEX Uploader", wx.OK)
        dlg.ShowModal()  # Show it
        dlg.Destroy()  # finally destroy it when finished.

    def OnExit(self, e):
        self.Close(True)  # Close the frame.

    def OnOpen(self, e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.DirDialog(self, "Choose a directory containing input files", self.dirname)
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = str(dlg.GetPath())
            self.StatusBar.SetStatusText("Loaded: %s\n" % self.dirname)
            self.inputedit.SetValue(self.dirname)
        dlg.Destroy()



    def EvtInput(self, event):
        self.dirname = event.GetString()
        self.StatusBar.SetStatusText("Input dir: %s\n" % self.dirname)


    def OnSubmit(self,event):
        """
        Run OPEX Uploader with args
        :return: return code shown in status
        """
        runoption = self.optionlist.get(self.runoptions.GetValue())
        options = [runoption, self.dbedit.GetValue(), self.projectedit.GetValue()]
        self.StatusBar.SetStatusText("Running...")
        if runoption != "--help":
            if (len(runoption)<=0 and len(self.projectedit.GetValue()) <=0):
                self.StatusBar.SetStatusText("Program requires database and project values to proceed")
                return 1
            if runoption != "--projects":
                if self.dirname is None or len(self.dirname) <=0:
                    self.StatusBar.SetStatusText("Please provide data directory to load from")
                    return 1
                else:
                    options.pop(0)
                    options.append(runoption + " " + self.dirname)

                if (self._cbCreateSubject.GetValue()):
                    options.append('--create')
                if (self._cbSkiprows.GetValue()):
                    options.append('--skiprows')
                if (self._cbChecks.GetValue()):
                    options.append('--checks')
                if (self._cbUpdate.GetValue()):
                    options.append('--update')
        print options
        s =" "
        cwd = join(os.getcwd(), "OPEXUploader.py")
        if ('PYTHONEXE' in os.environ):
            pythoncmd = os.environ('PYTHONEXE')
        else:
            pythoncmd = sys.prefix + os.sep + "Scripts" + os.sep + "python.exe"

        cmd = pythoncmd + " " + cwd + " " + s.join(options)
        print(cmd)
        msg=""
        try:
            retcode = subprocess.call(cmd, shell=True)
            if retcode < 0:
                msg = "Program was terminated by signal [" + str(retcode) + "]"
                self.StatusBar.SetStatusText(msg)
                print >> sys.stderr, msg
            elif retcode == 1:
                msg = "Program ran successfully [" + str(retcode) + "]"
                self.StatusBar.SetStatusText(msg)
                print >> sys.stderr, msg
            else:
                msg = "Program error [" + str(retcode) + "] - check output"
                self.StatusBar.SetStatusText(msg)
                print >> sys.stderr, msg
        except OSError as e:
            msg = "Program Execution failed:" + e.message
            print >> sys.stderr, msg

    def __cancelAction(self):
        msg = 'Cancelled by request'
        self.StatusBar.SetStatusText(msg)
        logging.info(msg)
        sys.exit(0)

#Execute the application
if __name__ == "__main__":
    app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
    frame = OPEXUploaderGUI(None, "OPEX XNAT Uploader")  # A Frame is a top-level window.
    frame.Show(True)  # Show the frame.
    app.MainLoop()