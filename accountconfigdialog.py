#    https://launchpad.net/wxbanker
#    accountconfigdialog.py: Copyright 2007-2009 Mike Rooney <mrooney@ubuntu.com>
#
#    This file is part of wxBanker.
#
#    wxBanker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wxBanker is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with wxBanker.  If not, see <http://www.gnu.org/licenses/>.

import wx
from transactionctrl import TransactionCtrl

try:
    import gnomekeyring
except ImportError:
    gnomekeyring = None


class MintConfigPanel(wx.Config):
    def  __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.RED)
        self.headerText = wx.StaticText(self, -1, _("wxBanker can synchronize account balances online if you have an account with mint.com"))

        self.usernameBox = wx.TextCtrl(self)
        self.passwordBox = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.saveAuthCheck = wx.CheckBox(self, label="Save Mint.com authentication in keyring")
        self.closeButton = wx.Button(self, id=wx.ID_OK)

        gridSizer = wx.GridSizer(2, 2, 3, 3)
        gridSizer.Add(wx.StaticText(self, label=_("Username")))
        gridSizer.Add(self.usernameBox)
        gridSizer.Add(wx.StaticText(self, label=_("Password")))
        gridSizer.Add(self.passwordBox)

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.headerText)
        self.Sizer.AddSpacer(10)
        self.Sizer.Add(gridSizer)
        self.Sizer.Add(self.saveAuthCheck)
        self.Sizer.AddStretchSpacer(1)
        self.Sizer.Add(self.closeButton)
        self.saveAuthCheck.Enable(bool(gnomekeyring))
        

class RecurringConfigPanel(wx.Panel):
    def __init__(self, parent, account):
        self.Account = account
        wx.Panel.__init__(self, parent)
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.AddSpacer(5)
        
        self.staticBox = wx.StaticBox(self, label=_("Transaction details"))
        self.staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        
        self.transactionCtrl = TransactionCtrl(self, editing=True)
        
        self.transactions = self.Account.GetRecurringTransactions()
        
        if not self.transactions:
            self.setupNoRecurringTransactions()
        else:
            self.setupRecurringTransactions()
        
        self.staticBoxSizer.Add(self.transactionCtrl)
        self.Sizer.AddSpacer(10)
        self.Sizer.Add(self.staticBoxSizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
            
    def setupNoRecurringTransactions(self):
        self.staticBox.Hide()
        self.transactionCtrl.Hide()
        self.Sizer.Add(wx.StaticText(self, label=_("This account currently has no recurring transactions.")), flag=wx.ALIGN_CENTER)
        
    def setupRecurringTransactions(self):
        strings = [rt.GetDescriptionString() for rt in self.transactions]
        choice = wx.Choice(self, choices=strings)
        
        self.Sizer.Add(choice, flag=wx.EXPAND)
        self.transactionCtrl.FromRecurring(self.transactions[0])

class AccountConfigDialog(wx.Dialog):
    def __init__(self, parent, account):
        wx.Dialog.__init__(self, parent, title=account.Name, size=(600, 400))
        self.Sizer = wx.BoxSizer()
        self.notebook = wx.aui.AuiNotebook(self, style=wx.aui.AUI_NB_TOP)
        self.Sizer.Add(self.notebook, 1, wx.EXPAND)
        
        self.recurringPanel = RecurringConfigPanel(self, account)
        self.notebook.AddPage(self.recurringPanel, _("Recurring Transactions"))
        
    def createMintConfigPanel(self):
        panel = wx.Panel(self)
