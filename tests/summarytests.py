#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    https://launchpad.net/wxbanker
#    summarytests.py: Copyright 2007-2009 Mike Rooney <mrooney@ubuntu.com>
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

import testbase, bankobjects
import unittest, datetime

# Set up some constants / shortcuts
today = datetime.date.today()
one = datetime.timedelta(1)


class SummaryTests(testbase.TestCaseWithController):
    def get(self, transactionsData, *args):
        # Remove all existing accounts, it is assumed that none exist
        for account in self.Model.Accounts:
            self.Model.RemoveAccount(account.Name)

        a = self.Model.CreateAccount("A")
        for (date, amount) in transactionsData:
            a.AddTransaction(amount=amount, date=date)

        return self.Model.GetXTotals(*args)

    def testGetTenPointsWithNoTransactions(self):
        result = self.get([], 10)
        self.assertEqual(result[0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(result[1], datetime.date.today())
        # Make sure it is close to zero but not zero.
        self.assertNotEqual(result[2], 0)
        self.assertAlmostEqual(result[2], 0)

    def testGetPointsWithOneTransaction(self):
        result = self.get([("2008/1/6", 1)], 3)
        self.assertEqual(result[0], [1.0, 1.0, 1.0])

        result = self.get([(today, 1)], 2)
        self.assertEqual(result[0], [1.0, 1.0])
        self.assertEqual(result[1], today)
        self.assertNotEqual(result[2], 0)

    def testGetOnePointWithTwoTransactionsYesterdayAndToday(self):
        result = self.get([(today-one, 1), (today, 2)], 1)
        self.assertEqual(result[0], [3.0])
        self.assertEqual(result[1], today - one)
        self.assertEqual(result[2], 1.0)

    def testGetPointsWithTwoSequentialDays(self):
        self.assertEqual(self.get([(today-one, 1), (today, 2)], 4)[0], [1.0, 1.0, 1.0, 3.0])
        self.assertEqual(self.get([(today, 1), (today+one, 2)], 2)[0], [1.0, 3.0])
        self.assertEqual(self.get([(today, 1), (today+one, 2)], 3)[0], [1.0, 1.0, 3.0])

    def testGetPointsWithNonSequentialDays(self):
        self.assertEqual(self.get([(today-one*9, 1), (today, 2)], 10)[0], [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 3.0])
        self.assertEqual(self.get([(today, 1), (today+one*2, 2), (today+one*9, 3)], 10)[0], [1.0, 1.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 6.0])

    def testGetPointsWithRange(self):
        daterange = (today+one, today+one*2)
        points, start, dpp = self.get([(today, 3), (today+one, 5), (today+one*2, 7), (today+one*3, 11)], 2, None, daterange)
        self.assertEqual(points, [5.0, 12.0])
        self.assertEqual(start, today+one)
        self.assertEqual(dpp, 0.5)

    def testGetPointsWithRangeNoTransactions(self):
        result = self.get([], 10, None, (today-one, today+one))
        self.assertEqual(result[0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(result[1], datetime.date.today())
        # Make sure it is close to zero but not zero.
        self.assertNotEqual(result[2], 0)
        self.assertAlmostEqual(result[2], 0)

    def testRaisesExceptionOnInvalidDateRange(self):
        self.assertRaises(bankobjects.InvalidDateRangeException, lambda: self.get([(today, 1)], 1, None, (today-one, today)))
        self.assertRaises(bankobjects.InvalidDateRangeException, lambda: self.get([(today, 1)], 10, None, (today, today+one)))

if __name__ == "__main__":
    unittest.main()