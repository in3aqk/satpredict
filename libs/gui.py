# -*- coding: utf-8 -*-

import wx
from libs.satModel import SatModel    

class Gui(wx.Frame):

    _app = None
    _satModel = None

    def __init__(self, *args, **kwargs):
        super(Gui, self).__init__(*args, **kwargs)
        self._satModel = SatModel()
        
        self.initUI()
        

    def initUI(self):
        self.SetSize(800,600)
        self.SetTitle('EasySat By In3aqk Paolo')
        self.Centre()

        
        mainPanel = wx.Panel(self)

       

        

        sizer = wx.BoxSizer(wx.HORIZONTAL)  # la direzione e' verticale
              
        satArr, self.satList = self._satModel.getSats(True)
        
        self.combo = wx.ComboBox(mainPanel,style = wx.CB_READONLY,choices = satArr) 
        self.combo.Bind(wx.EVT_COMBOBOX, self.OnSat) 
        
        #self.box = wx.StaticBox(mainPanel, wx.ID_ANY, "Satellite Data")
        gridSizer = wx.GridSizer(rows=4, cols=2, hgap=5, vgap=5)

        lblSatName = wx.StaticText(mainPanel, wx.ID_ANY, "Sat name:")
        lblSatMode = wx.StaticText(mainPanel, wx.ID_ANY, "Mode:")        
        lblDirection = wx.StaticText(mainPanel, wx.ID_ANY, "Direction:")
        lblUplink = wx.StaticText(mainPanel, wx.ID_ANY, "Uplink:")
        lblDownlink = wx.StaticText(mainPanel, wx.ID_ANY, "Downlink:")

        gridSizer.Add(lblSatName, 0, wx.ALIGN_RIGHT)
        gridSizer.Add(lblSatMode, 0, wx.ALIGN_RIGHT)
        gridSizer.Add(lblDirection, 0, wx.ALIGN_RIGHT)
        gridSizer.Add(lblUplink, 0, wx.ALIGN_RIGHT)
        gridSizer.Add(lblDownlink, 0, wx.ALIGN_RIGHT)
        mainPanel.SetSizer(gridSizer)

        sizer.Add(self.combo,0)
        #sizer.Add(self.box,0)
        mainPanel.SetSizer(sizer)

        self.menuBar()
        
    def OnSat(self, event): 
        i = event.GetSelection()
        print (self.satList[i]["label"],self.satList[i]["value"])
        print (self._satModel.getSatById(self.satList[i]["value"]))
      
       


    def menuBar(self):
        menubar = wx.MenuBar()
       
        menu = wx.Menu()
        quitPrg = menu.Append(-1, "Quit")
        #menu.Append(-1, "seconda voce")
        #menu.Append(-1, "terza voce")
        menubar.Append(menu,"File") 
        
        menu2 = wx.Menu()
        updTle = menu2.Append(-1, "Update Tle")
        #menu2.Append(-1, "seconda voce")
        #menu2.Append(-1, "terza voce")
        menubar.Append(menu2,"Satellites") 

        self.Bind(wx.EVT_MENU, self.quitSattrack, quitPrg)
        self.Bind(wx.EVT_MENU, self.updateTle, updTle)
        
        self.SetMenuBar(menubar)


    def updateTle(self, evt):
        print("Update Tle")

    def quitSattrack(self, evt):
        self.Close()

    def OnQuit(self, e):
        self.Close()