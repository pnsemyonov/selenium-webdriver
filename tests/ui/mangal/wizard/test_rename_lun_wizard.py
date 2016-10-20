#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Rename LUN' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.rename_lun_wizard import *
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


class TestRenameLUNWizard(FRTestCase):
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

    def test_valid_name(self):
        """
            Verify LUN renaming with valid name.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = '1g'
        lunNamePrefix = 'LuN'
        lunNewName = 'NewName'
        self.luns.create(count=lunCount, size=lunSize, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.node.lun.show(json=True))

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Renaming LUN in dialog')
        wizard = RenameLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Old LUN name:', lunNamePrefix + '_1')
        wizard.renameLUNPage.renameLUN(name=lunNewName)
        LOG.info('New LUN name:', lunNewName)
        wizard.renameLUNPage.submit()
        LOG.info('Rename submitted.')

        LOG.step('Verifying LUN name has been changed')
        lun = self.lunsPage.gridLUNs.find(name=lunNewName)
        self.assertTrue(len(lun) == 1)
        self.assertTrue(lun[0]['name'] == lunNewName)
        LOG.info('LUN found:\n', lun)

    def test_invalid_name(self):
        """
            Verify LUN renaming with invalid name.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = '1g'
        lunNamePrefix = 'LuN'
        lunNewName = 'NewName*&#@1A_^?,'
        self.luns.create(count=lunCount, size=lunSize, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.node.lun.show(json=True))

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Renaming LUN in dialog')
        wizard = RenameLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Old LUN name:', lunNamePrefix + '_1')
        wizard.renameLUNPage.renameLUN(name=lunNewName)
        LOG.info('New LUN name:', lunNewName)

        LOG.step('Verifying name error message')
        wizard.activePage.lblNameError.waitUntilPresent()
        LOG.info('Name error message:', wizard.activePage.lblNameError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_unicode_name(self):
        """
            Verify error message on setting LUN name containing Unicode characters.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = '1g'
        lunNamePrefix = 'LuN'
        lunNewName = u'Fran\u00e7ais'
        self.luns.create(count=lunCount, size=lunSize, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.node.lun.show(json=True))

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Renaming LUN in dialog')
        wizard = RenameLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Old LUN name:', lunNamePrefix + '_1')
        wizard.renameLUNPage.renameLUN(name=lunNewName)
        LOG.info('New LUN name:', lunNewName)

        LOG.step('Verifying LUN invalid name error message')
        wizard.activePage.lblNameError.waitUntilVisible()
        LOG.info('Error message:', wizard.activePage.lblNameError.getText())

    def test_dialog_cancel(self):
        """
            Verify LUN name remains intact on dialog cancel.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = '1g'
        lunNamePrefix = 'LuN'
        lunNewName = 'NewName'
        self.luns.create(count=lunCount, size=lunSize, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.node.lun.show(json=True))

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Assigning new LUN name in dialog')
        wizard = RenameLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Old LUN name:', lunNamePrefix + '_1')
        wizard.renameLUNPage.renameLUN(name=lunNewName)
        LOG.info('New LUN name:', lunNewName)

        LOG.step('Canceling dialog without submission')
        wizard.cancel()
        LOG.info('Dialog cancelled.')

        LOG.step('Verifying LUN name has not been changed')
        luns = self.lunsPage.gridLUNs.find(name=lunNamePrefix + '_1')
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['name'] == lunNamePrefix + '_1')
        LOG.info('LUNs with old name:\n', luns)
        luns = self.lunsPage.gridLUNs.find(name=lunNewName)
        self.assertTrue(len(luns) == 0)
        LOG.info('LUNs with new name:\n', luns)

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
    testRenameLUNWizard = TestRenameLUNWizard()
    sys.exit(testRenameLUNWizard.numberOfFailedTests())
