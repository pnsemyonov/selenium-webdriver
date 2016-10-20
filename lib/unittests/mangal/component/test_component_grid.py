#!/usr/bin/env python

purpose = """Unit test of Mangal UI API Grid component"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../.."))

import express
from mangal.page.luns_page import LUNsPage
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from frlog import LOG
from frargs import ARGS
from frutil import getFQDN
from frtestcase import FRTestCase
from frexceptions import *


ARGS.parser.add_argument(
    '--locale',
    type=str,
    choices=['en', 'es', 'de', 'fr', 'ja', 'ko', 'zh'],
    default='en',
    help="Locale: English, Spanish, German, French, Japanese, Korean, Chinese.")

ARGS.parser.add_argument(
    '--username', type=str,
    default='admin',
    help="Administrator's name on Mars controller")

ARGS.parser.add_argument(
    '--password', type=str,
    default='changeme',
    help="Administrator's password on Mars controller")

ARGS.parser.add_argument(
    '--lunsize', type=str,
    default='1m',
    help='Size of LUNs to be created. Default: 1m')


class TestComponentGrid(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.locale = ARGS.values.locale
        self.lunSize = ARGS.values.lunsize
        self.node = self.mars[0]
        self.webUIHostName = getFQDN(self.mars[0].hostname)

    def testSetup(self):
        self.driver = self.getDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.headerPage = HeaderPage(driver=self.driver)
        self.allStoragePage = AllStoragePage(driver=self.driver)
        self.lunsPage = LUNsPage(driver=self.driver)

        self.mars[0].lun.unmapAll()
        self.mars[0].lun.destroyAll()
        self.luns = express.Luns(node=self.node, cleanup=True)

        self.loginPage.signIn(username=self.username, password=self.password, locale=self.locale)

        LOG.step('Navigating to All Storage -> LUNs page')
        self.headerPage.btnManager.waitUntilPresent()
        self.headerPage.btnManager.click()
        self.allStoragePage.tabLUNs.waitUntilPresent()
        self.allStoragePage.tabLUNs.click()
        self.lunsPage.gridLUNs.waitUntilPresent()
        LOG.info("Grid is present on web page.")

    def test_component_grid_sort(self):
        prefixLower = 'EARTH'
        prefixMiddle = 'MARS'
        prefixUpper = 'VENUS'
        lunCount = 3

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixLower))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixLower)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixMiddle))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixMiddle)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixUpper))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixUpper)

        self.lunsPage.btnRefresh.click()

        LOG.step('Creating LUNs grid object')
        gridLUNs = self.lunsPage.gridLUNs

        LOG.step('Getting grid initial sorting')
        LOG.info('Grid sorted by:\n', gridLUNs.sortedBy())

        for columnName in gridLUNs.columnNames:
            if columnName != 'selected':
                LOG.step("Sorting grid by column '%s' in ascending order" % columnName)
                gridLUNs.sort(column=columnName, ascend=True)
                sortedBy = gridLUNs.sortedBy()
                self.assertTrue(sortedBy['column'] == columnName)
                self.assertTrue(sortedBy['ascend'])
                LOG.info('Grid sorted by:\n', sortedBy)

                LOG.step("Sorting grid by column '%s' in descending order" % columnName)
                gridLUNs.sort(column=columnName, ascend=False)
                sortedBy = gridLUNs.sortedBy()
                self.assertTrue(sortedBy['column'] == columnName)
                self.assertFalse(sortedBy['ascend'])
                LOG.info('Grid sorted by:\n', sortedBy)

        LOG.step("Sorting grid by column name 'Serial Number' (non-normalized)")
        gridLUNs.sort(column='Serial Number', ascend=True)
        sortedBy = gridLUNs.sortedBy()
        self.assertTrue(sortedBy['column'] == 'serial_number')
        LOG.info('Grid sorted by:\n', sortedBy)

        LOG.step("Sorting grid by column 'Name' in ascending order")
        gridLUNs.sort(column='name', ascend=True)
        rows = gridLUNs.find()
        self.assertTrue(rows[0]['name'] == prefixLower + '_1')
        LOG.info('First row:', rows[0]['name'])
        self.assertTrue(rows[-1]['name'] == prefixUpper + '_' + str(lunCount))
        LOG.info('Last row:', rows[-1]['name'])

        LOG.step("Sorting grid by column 'Name' in descending order")
        gridLUNs.sort(column='name', ascend=False)
        rows = gridLUNs.find()
        self.assertTrue(rows[0]['name'] == prefixUpper + '_' + str(lunCount))
        LOG.info('First row:', rows[0]['name'])
        self.assertTrue(rows[-1]['name'] == prefixLower + '_1')
        LOG.info('Last row:', rows[-1]['name'])

        LOG.step('Attempting to sort grid by selectable column (checkbox)')
        try:
            gridLUNs.sort(column='selected')
        except AttributeError:
            LOG.info("Unable to sort by selectable column.")

    def test_component_grid_select(self):
        prefixLower = 'ERIS'
        prefixMiddle = 'PLUTO'
        prefixUpper = 'SEDNA'
        lunCount = 3

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixLower))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixLower)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixMiddle))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixMiddle)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixUpper))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixUpper)

        self.lunsPage.btnRefresh.click()

        LOG.step('Creating LUNs grid object')
        gridLUNs = self.lunsPage.gridLUNs

        LOG.step('Selecting rows by name')
        gridLUNs.select(name=prefixLower + '_1')
        for row in gridLUNs.find(selected=True):
            self.assertTrue(row['name'].startswith(prefixLower))
        LOG.info('Selected rows:\n', gridLUNs.find(selected=True))

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()

        LOG.step("Selecting rows by name pattern '%s' (leading)" % prefixMiddle)
        gridLUNs.select(name=prefixMiddle, matchPattern=True)
        for row in gridLUNs.find(selected=True):
            self.assertTrue(row['name'].startswith(prefixMiddle))
        LOG.info('Selected rows:\n', gridLUNs.find(selected=True))

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()

        LOG.step("Selecting rows by name pattern '_1' (trailing)")
        gridLUNs.select(name='_1', matchPattern=True)
        for row in gridLUNs.find(selected=True):
            self.assertTrue('_1' in row['name'])
        LOG.info('Selected rows:\n', gridLUNs.find(selected=True))

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()
        self.assertFalse(gridLUNs.find(selected=True))
        LOG.info('Selected rows:\n', gridLUNs.find(selected=True))

    def test_component_grid_select_complex_filter(self):
        prefixLower = 'CARPO'
        prefixMiddle = 'DIA'
        prefixUpper = 'LEDA'
        lunCount = 3

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixLower))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixLower)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixMiddle))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixMiddle)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixUpper))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixUpper)

        self.lunsPage.btnRefresh.click()

        LOG.step('Creating LUNs grid object')
        gridLUNs = self.lunsPage.gridLUNs

        LOG.step("Selecting rows by complex filter: name contains '%s' or '%s'" % (prefixLower, prefixUpper))
        gridLUNs.select(name=[prefixLower, prefixUpper], matchPattern=True, valuesCondition='OR')
        selectedRows = gridLUNs.find(selected=True)
        for row in selectedRows:
            self.assertTrue((prefixLower in row['name']) or (prefixUpper in row['name']))
        LOG.info('Selected rows:\n', selectedRows)

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()

        LOG.step('Selecting all rows')
        gridLUNs.select()
        totalRows = len(gridLUNs.find())
        selectedRows = len(gridLUNs.find(selected=True))
        self.assertTrue(totalRows == selectedRows)
        LOG.info('Total rows:', totalRows)
        LOG.info('Selected rows:', selectedRows)

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()

        LOG.step("Selecting all rows then unselecting them by complex filter: name contains '%s' or '%s'" %
        (prefixLower, prefixUpper))
        gridLUNs.select()
        gridLUNs.unselect(name=[prefixLower, prefixUpper], matchPattern=True, valuesCondition='OR')
        unselectedRows = gridLUNs.find(selected=False)
        for row in unselectedRows:
            self.assertTrue((prefixLower in row['name']) or (prefixUpper in row['name']))
        LOG.info('Unselected rows:\n', unselectedRows)

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()

        LOG.step('Attempting to select rows by false filter condition (non-existing value)')
        gridLUNs.select(name=['NIX', 'STYX'], matchPattern=True, valuesCondition='OR')
        selectedRows = gridLUNs.find(selected=True)
        self.assertFalse(selectedRows)
        LOG.info('Selected rows:\n', selectedRows)

    def test_component_grid_select_repeat(self):
        """
            Test cases applying (un)selection to rows being already in target state
        """
        prefixLower = 'LARISSA'
        prefixMiddle = 'PROTEUS'
        prefixUpper = 'TRITON'
        lunCount = 3

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixLower))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixLower)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixMiddle))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixMiddle)

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixUpper))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixUpper)

        self.lunsPage.btnRefresh.click()

        LOG.step('Creating LUNs grid object')
        gridLUNs = self.lunsPage.gridLUNs
        LOG.step('Attempting to select already selected rows (row by row)')
        gridLUNs.select(name=prefixLower, matchPattern=True)
        selectedRows1Pass = gridLUNs.find(selected=True)
        LOG.info('Selected rows (first pass):\n', len(selectedRows1Pass))
        gridLUNs.select(name=prefixLower, matchPattern=True)
        selectedRows2Pass = gridLUNs.find(selected=True)
        self.assertTrue(len(selectedRows1Pass) == len(selectedRows2Pass))
        for row1Pass in selectedRows1Pass:
            self.assertTrue(row1Pass['name'] in [row2Pass['name'] for row2Pass in selectedRows2Pass])
        LOG.info('Selected rows (second pass):\n', len(selectedRows2Pass))

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()

        LOG.step('Attempting to select already selected rows (head selector)')
        gridLUNs.select()
        selectedRows1Pass = gridLUNs.find(selected=True)
        LOG.info('Selected rows (initial state):\n', len(selectedRows1Pass))
        gridLUNs.select()
        selectedRows2Pass = gridLUNs.find(selected=True)
        self.assertTrue(len(selectedRows1Pass) == len(selectedRows2Pass))
        LOG.info('Selected rows (repeated selection with head selector):\n', len(selectedRows2Pass))

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()

        LOG.step('Attempting to unselect already unselected rows (row by row)')
        unselectedRows = gridLUNs.find(selected=False)
        gridLUNs.unselect(name=prefixLower, matchPattern=True)
        unselectedRows2Pass = gridLUNs.find(selected=False)
        self.assertTrue(len(unselectedRows) == len(unselectedRows2Pass))
        LOG.info('Unselected rows number (initial state):', len(unselectedRows))
        LOG.info('Unselected rows number (repeated unselection):', len(unselectedRows2Pass))

        LOG.step('Attempting to unselect already unselected rows (head selector)')
        gridLUNs.unselect()
        unselectedRowsHeadSelector = gridLUNs.find(selected=False)
        self.assertTrue(len(unselectedRows) == len(unselectedRowsHeadSelector))
        LOG.info('Unselected rows number (initial state):', len(unselectedRows))
        LOG.info('Unselected rows number (repeated unselection with head selector):',
        len(unselectedRowsHeadSelector))

    def test_component_grid_find(self):
        prefixLower = 'JUPITER'
        prefixMiddle = 'NEPTUNE'
        prefixUpper = 'URANUS'
        lunCount = 3

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixLower))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixLower)

        self.lunsPage.btnRefresh.click()

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixMiddle))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixMiddle)

        self.lunsPage.btnRefresh.click()

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefixUpper))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefixUpper)

        self.lunsPage.btnRefresh.click()

        LOG.step('Creating LUNs grid object')
        gridLUNs = self.lunsPage.gridLUNs

        LOG.step("Finding rows by name '%s'" % prefixMiddle)
        foundRows = gridLUNs.find(name=prefixMiddle, matchPattern=True)
        for row in foundRows:
            self.assertTrue(prefixMiddle in row['name'])
        LOG.info('Found rows:\n', foundRows)

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()
        selectedRows = gridLUNs.find(selected=True)
        self.assertFalse(selectedRows)
        LOG.info('Selected rows:\n', selectedRows)

        LOG.step("Finding rows by multiple names '%s' and '%s' (pattern matching)" % (prefixLower, prefixUpper))
        foundRows = gridLUNs.find(name=[prefixLower, prefixUpper], matchPattern=True)
        for row in foundRows:
            self.assertTrue((prefixLower in row['name']) or (prefixUpper in row['name']))
        LOG.info('Found rows:\n', foundRows)

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()
        selectedRows = gridLUNs.find(selected=True)
        self.assertFalse(selectedRows)
        LOG.info('Selected rows:\n', selectedRows)

        LOG.step("Finding rows by multiple names '%s_1' and '%s_3' (exact matching)" % (prefixLower, prefixUpper))
        foundRows = gridLUNs.find(name=[prefixLower + '_1', prefixUpper + '_3'])
        for row in foundRows:
            self.assertTrue((prefixLower + '_1' in row['name']) or (prefixUpper + '_3' in row['name']))
        LOG.info('Found rows:\n', foundRows)

        LOG.step('Unselecting all rows')
        gridLUNs.unselect()
        selectedRows = gridLUNs.find(selected=True)
        self.assertFalse(selectedRows)
        LOG.info('Selected rows:\n', selectedRows)

        LOG.step('Finding all rows')
        foundRows = gridLUNs.find()
        LOG.info('Found rows:\n', len(foundRows))
        gridLUNs.unselect()
        unselectedRows = gridLUNs.find(selected=False)
        self.assertTrue(len(foundRows) == len(unselectedRows))
        LOG.info('Unselected rows:\n', len(unselectedRows))

    def test_component_grid_multi_page(self):
        prefix = 'IO'
        lunCount = 135

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefix))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefix)

        LOG.step('Creating LUNs grid object')
        gridLUNs = self.lunsPage.gridLUNs

        LOG.info('Pages:', gridLUNs.pages)

        LOG.step('Navigating to page 1')
        gridLUNs.goToPage(number=1)
        self.assertTrue(gridLUNs.page == 1)
        LOG.info('Page:', gridLUNs.page)
        self.assertFalse(gridLUNs.hasFirstPage)
        LOG.info('Has first page:', gridLUNs.hasFirstPage)
        self.assertFalse(gridLUNs.hasPreviousPage)
        LOG.info('Has previous page:', gridLUNs.hasPreviousPage)
        if gridLUNs.pages > 1:
            self.assertTrue(gridLUNs.hasNextPage)
            self.assertTrue(gridLUNs.hasLastPage)
        else:
            self.assertFalse(gridLUNs.hasNextPage)
            self.assertFalse(gridLUNs.hasLastPage)
        LOG.info('Has next page:', gridLUNs.hasNextPage)
        LOG.info('Has last page:', gridLUNs.hasLastPage)

        LOG.step('Navigating to next page')
        gridLUNs.goNextPage()
        self.assertTrue(gridLUNs.page == 2)
        LOG.info('Page:', gridLUNs.page)
        self.assertTrue(gridLUNs.hasFirstPage)
        LOG.info('Has first page:', gridLUNs.hasFirstPage)
        self.assertTrue(gridLUNs.hasPreviousPage)
        LOG.info('Has previous page:', gridLUNs.hasPreviousPage)
        if gridLUNs.pages > 2:
            self.assertTrue(gridLUNs.hasNextPage)
            self.assertTrue(gridLUNs.hasLastPage)
        else:
            self.assertFalse(gridLUNs.hasNextPage)
            self.assertFalse(gridLUNs.hasLastPage)
        LOG.info('Has next page:', gridLUNs.hasNextPage)
        LOG.info('Has last page:', gridLUNs.hasLastPage)

        LOG.step('Navigating through all pages: first, next until last, previous until first, last')
        gridLUNs.goFirstPage()
        LOG.info('Page:', gridLUNs.page)
        while gridLUNs.page < gridLUNs.pages:
            gridLUNs.goNextPage()
            LOG.info('Page:', gridLUNs.page)
        if gridLUNs.pages > 1:
            self.assertTrue(gridLUNs.hasFirstPage)
            self.assertTrue(gridLUNs.hasPreviousPage)
            self.assertTrue(gridLUNs.page == gridLUNs.pages)
            self.assertFalse(gridLUNs.hasNextPage)
            self.assertFalse(gridLUNs.hasLastPage)
        while gridLUNs.page > 1:
            gridLUNs.goPreviousPage()
            LOG.info('Page:', gridLUNs.page)
        self.assertTrue(gridLUNs.page == 1)

        LOG.step("Navigating to non-existing page")
        try:
            gridLUNs.goToPage(number=(gridLUNs.pages + 1))
        except LookupError as e:
            LOG.info(e.message)

    def test_component_grid_click_link(self):
        prefix = 'SATURN'
        lunCount = 3

        LOG.step("Creating %s LUNs with name prefix '%s'" % (lunCount, prefix))
        self.luns.create(count=lunCount, size=self.lunSize, prefix=prefix)

        self.lunsPage.btnRefresh.click()

        LOG.step('Creating LUNs grid object')
        gridLUNs = self.lunsPage.gridLUNs

        for rowCount in range(1, lunCount + 1):
            LOG.step("Clicking on link '%s' in cell name='%s'" % (prefix + '_' + str(rowCount),
                prefix + '_' + str(rowCount)))
            gridLUNs.clickLink(name=prefix + '_' + str(rowCount), click={'name': prefix + '_' +
                str(rowCount)})
            self.driver.back()
            LOG.info('Navigated back in browser history')

    def testTeardown(self):
        try:
            LOG.info("Destroying existing LUNs...")
            del self.luns
        except Exception as e:
            raise FailedProductException(e)
        self.driver.quit()


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testComponentGrid = TestComponentGrid()
    sys.exit(testComponentGrid.numberOfFailedTests())
