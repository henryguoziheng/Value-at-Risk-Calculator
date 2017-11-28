# -*- coding: utf-8 -*-


from __future__ import division
import wx
import pandas as pd
import datetime
import pandas_datareader as pdr
from UI import PanelOne, PanelTwo
from VaR import GetVaR

__author__ = 'Henry'
__date__ = '2017-11-26'


class PanelOnex(PanelOne):
    def main_button_click(self, event):
        temp = self.position.GetValue().split(' ')
        position = [int(x) for x in temp]
        alpha = float(1 - float(self.confidence.GetValue()))
        #print alpha
        simulationNum = int(self.simuNum.GetValue())

        T = float(self.period.GetValue())

        temp2 = self.stockList.GetValue().split((' '))
        temp2 = [str(x) for x in temp2]


        df = pd.DataFrame()

        endDate = datetime.datetime.strptime(str(self.endDate.GetValue()),'%Y-%m-%d')
        startDate = (endDate - datetime.timedelta(days = 1825)).strftime('%Y-%m-%d')

        for i in temp2:
            tempData = pdr.get_data_yahoo(i, start = startDate, end = endDate)     # Revise Later
            df[i] = tempData['Adj Close']

        stockData = df.reset_index(drop = True)
        #print stockData


        test = GetVaR(simulationNum, stockData, position, T)

        var = test.getStockVaR(alpha)
        avar = test.getStockAVaR(alpha)

        self.m_textCtrl6.SetValue(str(var))
        self.m_textCtrl7.SetValue(str(avar))


class PanelTwox(PanelTwo):
    def main_button_click(self, event):
        temp = self.position.GetValue().split(' ')
        position = [int(x) for x in temp]
        alpha = float(1 - float(self.confidence.GetValue()))
        simulationNum = int(self.simuNum.GetValue())

        T = float(self.period.GetValue())

        stockData = pd.read_excel(str(self.location.GetValue()))
        stockData = stockData.drop('Date', axis = 1)
        #print stockData


        test = GetVaR(simulationNum, stockData, position, T)

        var = test.getStockVaR(alpha)
        avar = test.getStockAVaR(alpha)

        self.m_textCtrl6.SetValue(str(var))
        self.m_textCtrl7.SetValue(str(avar))



class MainWindow(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Option Calculator")

        self.panel_one = PanelOnex(self)
        self.panel_two = PanelTwox(self)
        self.panel_two.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel_one, 1, wx.EXPAND)
        self.sizer.Add(self.panel_two, 1, wx.EXPAND)
        self.SetSizer(self.sizer)


        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        switch_panels_menu_item = fileMenu.Append(wx.ID_ANY,
                                                  "Switch Panels",
                                                  "Some text")
        self.Bind(wx.EVT_MENU, self.onSwitchPanels,
                  switch_panels_menu_item)
        menubar.Append(fileMenu, '&Tool')
        self.SetMenuBar(menubar)


    def onSwitchPanels(self, event):
        """"""
        if self.panel_one.IsShown():
            self.SetTitle("Panel Two Showing")
            self.panel_one.Hide()
            self.panel_two.Show()
        else:
            self.SetTitle("Panel One Showing")
            self.panel_one.Show()
            self.panel_two.Hide()
        self.Layout()


app = wx.App()
main_win = MainWindow()
main_win.Show()
app.MainLoop()