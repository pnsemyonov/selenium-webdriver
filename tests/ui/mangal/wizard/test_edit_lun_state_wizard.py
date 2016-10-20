#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'LUN -> Edit -> State' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import time
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.edit_lun_state_wizard import *
from frlog import LOG
from frargs import ARGS
from frutil import getFQDN
from frtestcase import FRTestCase
from frexceptions import *


ARGS.parser.add_argument(
    '--locale',
    type=str,
    choices=['en', 'es', 'de', 'fr', 'ja', 'ko', 'zh'],
    help="Locale: English, Spanish, German, French, Japanese, Korean, Chinese.")

ARGS.parser.add_argument(
    '--username', type=str,
    default='admin',
    help="Administrator's name on Mars controller")

ARGS.parser.add_argument(
    '--password', type=str,
    default='changeme',
    help="Administrator's password on Mars controller")


class TestEditLUNStateWizard(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.locale = ARGS.values.locale
        self.webUIHostName = getFQDN(self.marscluster.getMasterNode().hostname)

    def testSetup(self):
        self.driver = self.getDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.headerPage = HeaderPage(driver=self.driver)
        self.allStoragePage = AllStoragePage(driver=self.driver)
        self.lunsPage = LUNsPage(driver=self.driver)

        self.node = self.marscluster
        self.luns = express.Luns(node=self.marscluster)

        LOG.step('Signing in')
        self.loginPage.open()
        self.loginPage.waitUntilOpen()
        if self.locale is None:
            self.locale = self.loginPage.getRandomLocale()
        self.loginPage.signIn(username=self.username, password=self.password, locale=self.locale)
        LOG.info('Signed in with username: %s, password: %s, locale: %s.' % (self.username,
            self.password, self.locale))
        LOG.info('Browser landed on header page.')

        LOG.info('Navigating to LUNs page...')
        self.headerPage.btnManager.click()
        self.allStoragePage.tabLUNs.click()
        self.lunsPage.waitUntilOpen()
        LOG.info('Browser landed on LUNs page.')

    def test_single_lun_offline_online(self):
        """
            Verify single LUN's state change from Online to Offline.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Taking LUN offline')
        wizard = EditLUNStateWizard(driver=self.driver)
        wizard.openTakeOffline(name=lunNamePrefix + '_1')
        wizard.activePage.submit()
        LOG.info('Taking offline submitted.')

        LOG.step('Verifying LUN state')

        lunState = {lun['name']: lun['lun-state'] for lun in
            self.node.lun.show(json=True)}[lunNamePrefix + '_1']
        self.assertTrue(lunState == 'offline')
        LOG.info('LUN state:', lunState)

        LOG.step('Taking LUN online')
        wizard.takeOnline(name=lunNamePrefix + '_1')
        LOG.info('Taking online submitted.')

        LOG.step('Verifying LUN state')
        lunState = {lun['name']: lun['lun-state'] for lun in
            self.node.lun.show(json=True)}[lunNamePrefix + '_1']
        self.assertTrue(lunState == 'online')
        LOG.info('LUN state:', lunState)

    def test_multiple_luns_offline_online(self):
        """
            Verify multiple LUNs' state change from Online to Offline.
        """
        LOG.step('Creating LUNs')
        lunCount = 7
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Taking all LUNs offline')
        wizard = EditLUNStateWizard(driver=self.driver)
        wizard.openTakeOffline(name=lunNamePrefix, matchPattern=True)
        wizard.activePage.submit()
        LOG.info('Taking offline submitted.')

        LOG.step("Verifying LUNs' state")
        luns = {lun['name']: lun['lun-state'] for lun in self.node.lun.show(json=True)}
        for lunName in luns:
            self.assertTrue(luns[lunName] == 'offline')
            LOG.info("LUN: %s, state: %s" % (lunName, luns[lunName]))

        LOG.step('Taking all LUNs online')
        wizard.takeOnline(name=lunNamePrefix, matchPattern=True)
        LOG.info('Taking online submitted.')

        # Let UI to communicate with the server and update LUNs.
        time.sleep(3)

        LOG.step("Verifying LUNs' state")
        luns = {lun['name']: lun['lun-state'] for lun in self.node.lun.show(json=True)}
        for lunName in luns:
            self.assertTrue(luns[lunName] == 'online')
            LOG.info("LUN: %s, state: %s" % (lunName, luns[lunName]))

    def test_offline_cancel(self):
        """
            Verify 'Take Offline -> Cancel' does cancel dialog gracefully, state not affected.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Taking LUN offline')
        wizard = EditLUNStateWizard(driver=self.driver)
        wizard.openTakeOffline(name=lunNamePrefix + '_1')
        LOG.info("'Take Offline' page is open.")

        LOG.step('Canceling dialog')
        wizard.cancel()
        LOG.info('Dialog cancelled.')

        LOG.step('Verifying LUN state has not been changed')
        lunState = {lun['name']: lun['lun-state'] for lun in
            self.node.lun.show(json=True)}[lunNamePrefix + '_1']
        self.assertTrue(lunState == 'online')
        LOG.info('LUN state:', lunState)

    def test_online_not_available(self):
        """
            Verify that 'Take Online' is not available for selected LUNs with status 'Online'.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step("Selecting LUN '%s'" % lunNamePrefix + '_1')
        self.lunsPage.gridLUNs.select(name=lunNamePrefix + '_1')
        LOG.info('LUN selected.')

        LOG.step("Verifying menu 'State -> Online' is disabled for LUN in online")
        isOnlineEnabled = self.lunsPage.menuEdit.isItemEnabled(item=['State', 'Online'])
        self.assertFalse(isOnlineEnabled)
        LOG.info("Menu 'Edit': Item 'State -> Online' is enabled:", isOnlineEnabled)

        LOG.step("Verifying menu 'State -> Offline' is enabled for LUN in online")
        isOfflineEnabled = self.lunsPage.menuEdit.isItemEnabled(item=['State', 'Offline'])
        self.assertTrue(isOfflineEnabled)
        LOG.info("Menu 'Edit': Item 'State -> Offline' is enabled:", isOfflineEnabled)

    def test_offline_not_available(self):
        """
            Verify that 'Take Offline' is not available for selected LUNs with status 'Offline'.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Taking LUN offline')
        wizard = EditLUNStateWizard(driver=self.driver)
        wizard.openTakeOffline(name=lunNamePrefix + '_1')
        wizard.activePage.submit()
        LOG.info('Taking offline submitted.')

        LOG.step('Verifying LUN state')
        lunState = {lun['name']: lun['lun-state'] for lun in
            self.node.lun.show(json=True)}[lunNamePrefix + '_1']
        self.assertTrue(lunState == 'offline')
        LOG.info('LUN state:', lunState)

        LOG.step("Selecting LUN '%s'" % lunNamePrefix + '_1')
        self.lunsPage.gridLUNs.select(name=lunNamePrefix + '_1')
        LOG.info('LUN selected.')

        LOG.step("Verifying menu 'State -> Offline' is disabled for LUN in offline")
        isOfflineEnabled = self.lunsPage.menuEdit.isItemEnabled(item=['State', 'Offline'])
        self.assertFalse(isOfflineEnabled)
        LOG.info("Menu 'Edit': Item 'State -> Offline' is enabled:", isOfflineEnabled)

        LOG.step("Verifying menu 'State -> Online' is enabled for LUN in offline")
        isOnlineEnabled = self.lunsPage.menuEdit.isItemEnabled(item=['State', 'Online'])
        self.assertTrue(isOnlineEnabled)
        LOG.info("Menu 'Edit': Item 'State -> Online' is enabled:", isOnlineEnabled)

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
    testEditLUNStateWizard = TestEditLUNStateWizard()
    sys.exit(testEditLUNStateWizard.numberOfFailedTests())
