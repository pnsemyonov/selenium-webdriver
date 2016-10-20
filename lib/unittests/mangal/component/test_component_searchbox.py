#!/usr/bin/env python

purpose = """Unit test of Mangal GUI SearchBox Component"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../.."))

import time
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from frlog import LOG
from frargs import ARGS
from frutil import getFQDN
from frtestcase import FRTestCase


ARGS.parser.add_argument(
    '--locale', type=str,
    help="Locale: 'en' (English), 'es' (Spanish), 'de' (German), 'fr' (French), 'ja' (Japanese), 'ko' (Korean), 'zh' (Chinese)")

ARGS.parser.add_argument(
    '--username', type=str,
    default='admin',
    help="Administrator's name on Mars controller")

ARGS.parser.add_argument(
    '--password', type=str,
    default='changeme',
    help="Administrator's password on Mars controller")

class TestComponentSearchBox(FRTestCase):
    def suiteSetup(self):
        self.locale = ARGS.values.locale
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.webUIHostName = getFQDN(self.marscluster.hostname)

        self.luns = express.Luns(node=self.marscluster)

    def testSetup(self):
        self.driver = self.setupDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.headerPage = HeaderPage(driver=self.driver)
        self.allStoragePage = AllStoragePage(driver=self.driver)
        self.lunsPage = LUNsPage(driver=self.driver)

        LOG.step('Signing in')
        self.loginPage.open()
        self.loginPage.waitUntilOpen()
        self.loginPage.signIn(username=self.username, password=self.password, locale=self.locale)
        LOG.info('Signed in with username: %s, password: %s, locale: %s.' % (self.username,
            self.password, self.locale))
        LOG.info('Browser landed on header page.')

        LOG.step('Navigating to LUNs page')
        self.headerPage.btnManager.click()
        self.allStoragePage.tabLUNs.click()
        self.lunsPage.waitUntilOpen()
        LOG.info('Browser landed on LUNs page.')

        LOG.step('Creating LUNs')
        self.lunNamePrefix = 'LuN'
        self.lunCount = 20
        self.luns.create(count=self.lunCount, size='1g', prefix=self.lunNamePrefix)
        luns = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', [lun['name'] for lun in luns])

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

    def test_search(self):
        """
            Search for single/multiple row(s) in grid. Verify displayed rows satisfy search key.
        """
        LOG.step('Searching for unique value: %s' % self.lunNamePrefix + '_' + str(self.lunCount))
        self.lunsPage.sBoxSearch.setText(text=self.lunNamePrefix + '_' + str(self.lunCount))
        luns = self.lunsPage.gridLUNs.find()
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['name'] == self.lunNamePrefix + '_' + str(self.lunCount))
        LOG.info('LUNs displayed:', luns)

        LOG.step('Searching for multiple values: %s' % self.lunNamePrefix + '_1*')
        self.lunsPage.sBoxSearch.clear()
        self.lunsPage.sBoxSearch.setText(text=self.lunNamePrefix + '_1')
        luns = [lun['name'] for lun in self.lunsPage.gridLUNs.find()]
        # 'LuN_1', 'LuN_10' ... 'LuN_19'
        self.assertTrue(len(luns) == 11)
        for lun in luns:
            self.assertTrue(lun.startswith(self.lunNamePrefix + '_1'))
        LOG.info('LUNs displayed:', luns)

    def testTeardown(self):
        self.driver.close()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        LOG.info('LUNs destroyed.')

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testComponentSearchBox = TestComponentSearchBox()
    sys.exit(testComponentSearchBox.numberOfFailedTests())