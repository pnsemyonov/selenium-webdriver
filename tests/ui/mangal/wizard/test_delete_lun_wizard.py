#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'LUN -> Delete' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import time
import pprint
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.delete_lun_wizard import *
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


class TestDeleteLUNWizard(FRTestCase):
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
        # self.luns.setCleanup(True)

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

    def test_delete_single_lun(self):
        """
            Verify single LUN's deletion.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', pprint.pformat(self.marscluster.lun.show(json=True)))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step("Deleting LUN '%s'" % (lunNamePrefix + '_1'))
        wizard = DeleteLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        wizard.activePage.confirm()
        wizard.activePage.submit()
        LOG.info('LUN deletion submitted.')

        LOG.step('Verifying LUN has been deleted')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == lunCount - 1)
        self.assertTrue((lunNamePrefix + '_1') not in [lun['name'] for lun in luns])
        LOG.info('LUNs:\n%s' % pprint.pformat(luns))
        LOG.info("LUN '%s' deleted." % (lunNamePrefix + '_1'))

    def test_delete_multiple_luns(self):
        """
            Verify multiple LUNs' deletion.
        """
        LOG.step('Creating LUNs')
        lunCount = 7
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        lunsToDelete = [lunNamePrefix + '_1', lunNamePrefix + '_2', lunNamePrefix + '_3']
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', pprint.pformat(self.marscluster.lun.show(json=True)))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step("Deleting LUNs: %s" % lunsToDelete)
        wizard = DeleteLUNWizard(driver=self.driver)
        wizard.open(name=lunsToDelete)
        wizard.activePage.confirm()
        wizard.activePage.submit()
        LOG.info('LUN deletion submitted.')

        LOG.step('Verifying LUNs have been deleted')
        luns = [lun['name'] for lun in self.marscluster.lun.show(json=True)]
        self.assertTrue(len(luns) == lunCount - len(lunsToDelete))
        for lunName in lunsToDelete:
            self.assertFalse(lunName in luns)
        LOG.info('Existing LUNs:\n%s' % luns)

    def test_dialog_cancel(self):
        """
            Verify 'Delete LUN -> Cancel' does cancel dialog gracefully, LUN not deleted.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        lunsOriginal = [lun['name'] for lun in self.marscluster.lun.show(json=True)]
        LOG.info('LUNs created:', lunsOriginal)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = DeleteLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Canceling wizard')
        wizard.activePage.confirm()
        wizard.cancel()
        LOG.info('Wizard closed without submission.')

        LOG.step('Verifying LUN has remain intact')
        luns = [lun['name'] for lun in self.marscluster.lun.show(json=True)]
        self.assertTrue(len(luns) == lunCount)
        for lunName in luns:
            self.assertTrue(lunName in lunsOriginal)
        LOG.info('LUNs original: %s' % lunsOriginal)
        LOG.info('LUNs existing: %s' % luns)

    def test_dialog_not_available(self):
        """
            Verify that 'Delete LUN' is not available when no selected LUNs present.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        lunsOriginal = [lun['name'] for lun in self.marscluster.lun.show(json=True)]
        LOG.info('LUNs created:', lunsOriginal)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Unselecting all LUNs in grid')
        self.lunsPage.gridLUNs.unselect()
        self.assertFalse(self.lunsPage.gridLUNs.find(selected=True))
        LOG.info('No LUNs selected in grid.')

        LOG.step("Verifying button 'Delete' is disabled.")
        self.assertFalse(self.lunsPage.btnDelete.isEnabled())
        LOG.info("Button 'Delete' is enabled:", self.lunsPage.btnDelete.isEnabled())

    def testTeardown(self):
        self.driver.close()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        LOG.info('LUNs destroyed.')

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()
        LOG.info('Browser closed.')

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testDeleteLUNWizard = TestDeleteLUNWizard()
    sys.exit(testDeleteLUNWizard.numberOfFailedTests())
