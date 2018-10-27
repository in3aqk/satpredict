#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
from libs.gui import Gui



if __name__ == "__main__":
    app = wx.App(False)
    gui = Gui(None)
    gui.Show()
    app.MainLoop()
   
