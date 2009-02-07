# -*- coding: iso-8859-15 -*-
#
#    https://launchpad.net/wxbanker
#    menubar.py: Copyright 2007, 2008 Mike Rooney <michael@wxbanker.org>
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

import wx, webbrowser, os
from wx.lib.wordwrap import wordwrap
from wx.lib.pubsub import Publisher

import version, localization, debug
from currencies import CurrencyStrings
from csvimportframe import CsvImportFrame

class BankMenuBar(wx.MenuBar):
    ID_AUTOSAVE = wx.NewId()
    ID_FAQ = wx.NewId()
    ID_QUESTION = wx.NewId()
    ID_REPORTBUG = wx.NewId()
    IDS_CURRENCIES = [wx.NewId() for i in range(len(CurrencyStrings))]
    ID_IMPORT_CSV = wx.NewId()
    
    def __init__(self, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        
        # File menu.
        fileMenu = wx.Menu()
        self.saveMenuItem = fileMenu.Append(wx.ID_SAVE)
        self.autoSaveMenuItem = fileMenu.AppendCheckItem(self.ID_AUTOSAVE, _("Auto-save"), _("Automatically save changes"))
        
        # Settings menu.
        settingsMenu = wx.Menu()
        
        ## TRANSLATORS: Put the ampersand (&) before the letter to use as the Alt shortcut.
        currencyMenu = wx.MenuItem(settingsMenu, -1, _("&Currency"), _("Select currency to display"))
        currencyMenu.SetBitmap(wx.ArtProvider.GetBitmap("wxART_money"))
        
        currencies = wx.Menu()
        # Add an entry for each available currency.
        for i, cstr in enumerate(CurrencyStrings):
            item = wx.MenuItem(currencies, self.IDS_CURRENCIES[i], cstr)
            currencies.AppendItem(item)
        currencyMenu.SetSubMenu(currencies)
        
        settingsMenu.AppendItem(currencyMenu)
        
        # Tools menu.
        toolsMenu = wx.Menu()
        
        importCsvMenu = wx.MenuItem(toolsMenu, self.ID_IMPORT_CSV, _("Import from CSV"), _("Import transactions from a CSV file"))
        toolsMenu.AppendItem(importCsvMenu)
        
        # Help menu.
        helpMenu = wx.Menu()
        
        ## TRANSLATORS: Put the ampersand (&) before the letter to use as the Alt shortcut.
        faqItem = wx.MenuItem(helpMenu, self.ID_FAQ, _("View &FAQs"), _("View Frequently Asked Questions online"))
        faqItem.Bitmap = wx.ArtProvider.GetBitmap("wxART_comments")
        helpMenu.AppendItem(faqItem)
        
        ## TRANSLATORS: Put the ampersand (&) before the letter to use as the Alt shortcut.
        questionItem = wx.MenuItem(helpMenu, self.ID_QUESTION, _("Ask a &Question"), _("Ask a question online"))
        questionItem.Bitmap = wx.ArtProvider.GetBitmap("wxART_user_comment")
        helpMenu.AppendItem(questionItem)
        
        ## TRANSLATORS: Put the ampersand (&) before the letter to use as the Alt shortcut.
        bugItem = wx.MenuItem(helpMenu, self.ID_REPORTBUG, _("&Report a Bug"), _("Report a bug to the developer online"))
        bugItem.Bitmap = wx.ArtProvider.GetBitmap("wxART_bug")
        helpMenu.AppendItem(bugItem)
        
        ## TRANSLATORS: Put the ampersand (&) before the letter to use as the Alt shortcut.
        aboutItem = helpMenu.Append(wx.ID_ABOUT, _("&About"), _("More information about wxBanker"))
        
        # Add everything to the main menu.
        self.Append(fileMenu, _("&File"))
        self.Append(settingsMenu, _("&Settings"))
        self.Append(toolsMenu, _("&Tools"))
        self.Append(helpMenu, _("&Help"))
        
        self.Bind(wx.EVT_MENU, self.onClickAbout)
        helpMenu.Bind(wx.EVT_MENU, self.onClickAbout)
        
        Publisher.subscribe(self.onAutoSaveToggled, "controller.autosave_toggled")
        
    def onMenuEvent(self, event):
        ID = event.Id
        
        if ID in self.IDS_CURRENCIES:
            self.onSelectCurrency(self.IDS_CURRENCIES.index(ID))
        else:
            handler = {
                self.ID_AUTOSAVE: self.onClickAutoSave,
                self.ID_FAQ: self.onClickFAQs,
                self.ID_QUESTION: self.onClickAskQuestion,
                self.ID_REPORTBUG: self.onClickReportBug,
                self.ID_IMPORT_CSV: self.onClickImportCsv,
                wx.ID_ABOUT: self.onClickAbout,
            }.get(ID, lambda e: e.Skip())
            
            handler(event)
            
    def onAutoSaveToggled(self, message):
        val = message.data
        debug.debug("Updating UI for auto-save: %s" % val)
        
        self.autoSaveMenuItem.Check(val)
        self.saveMenuItem.Enable(not val)
            
    def onClickAutoSave(self, event):
        Publisher().sendMessage("user.autosave_toggled", event.Checked())
        
    def onSelectCurrency(self, currencyIndex):
        Publisher().sendMessage("user.currency_changed", currencyIndex)
        
    def onClickFAQs(self, event):
        webbrowser.open("https://answers.launchpad.net/wxbanker/+faqs")
        
    def onClickAskQuestion(self, event):
        webbrowser.open("https://launchpad.net/wxbanker/+addquestion")
        
    def onClickReportBug(self, event):
        webbrowser.open("https://launchpad.net/wxbanker/+filebug")
        
    def onClickAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "wxBanker"
        info.Version = str(version.NUMBER)
        info.Copyright = _("Copyright") + " 2007, 2008 Mike Rooney (michael@wxbanker.org)"
        info.Description = _("A lightweight personal finance management application.")
        info.WebSite = ("https://launchpad.net/wxbanker", "https://launchpad.net/wxbanker")

        info.Developers = [
            'Mike Rooney (michael@wxbanker.org)',
        ]
        info.Artists = [
            'Mark James (www.famfamfam.com/lab/icons/silk/)',
        ]
        translators = [
            'sl: Primo� Jer�e (jerse@inueni.com)',
            'es: Diego J. Romero L�pez (diegojromerolopez@gmail.com)',
            'hi: Ankur Kachru (ankurkachru@gmail.com)',
        ]
        info.Translators = [unicode(s, 'iso-8859-15') for s in translators]
        
        licenseDir = os.path.dirname(__file__)
        info.License = open(os.path.join(licenseDir, 'COPYING.txt')).read()

        wx.AboutBox(info)
        
    def onClickImportCsv(self, event):
        CsvImportFrame()
