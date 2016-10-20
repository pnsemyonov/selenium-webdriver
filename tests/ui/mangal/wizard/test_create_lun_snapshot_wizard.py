#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Create Snapshot Copy' dialog"""

import os
import sys
import time
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import express

from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.create_lun_snapshot_wizard import *

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


class TestCreateLUNSnapshotWizard(FRTestCase):
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

        self.marscluster.snapshot.deleteAll()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.luns = express.Luns(node=self.marscluster)

        LOG.step('Signing in')
        self.loginPage.open()
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

    def test_create_default_name(self):
        """
            Verify snapshot creation with default snapshot name.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening dialog')
        wizard = CreateLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Dialog is open.')

        LOG.step('Verifying snapshot default name')
        self.assertTrue(wizard.activePage.txtName.getText() == lunNamePrefix + '_1_snap_0')
        LOG.info('Snapshot name:', wizard.activePage.txtName.getText())

        LOG.step('Creating snapshot copy')
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying snapshot has been created')
        snapshots = self.marscluster.snapshot.show(json=True)
        self.assertTrue(len(snapshots) == 1)
        self.assertTrue(snapshots[0]['create-time-object'] == lunNamePrefix + '_1')
        LOG.info('LUN name:', snapshots[0]['create-time-object'])
        self.assertTrue(snapshots[0]['name'] == lunNamePrefix + '_1_snap_0')
        LOG.info('Snapshot name:', snapshots[0]['name'])

    def test_create_custom_name(self):
        """
            Verify snapshot creation with customized name.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        snapshotName = 'Snapshot-100'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening dialog')
        wizard = CreateLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Dialog is open.')

        LOG.step('Creating snapshot copy')
        LOG.info('Setting snapshot name')
        wizard.activePage.setName(name=snapshotName)
        self.assertTrue(wizard.activePage.txtName.getText() == snapshotName)
        LOG.info('Snapshot name set:', wizard.activePage.txtName.getText())
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying snapshot has been created')
        snapshots = self.marscluster.snapshot.show(json=True)
        self.assertTrue(len(snapshots) == 1)
        self. assertTrue(snapshots[0]['create-time-object'] == lunNamePrefix + '_1')
        LOG.info('LUN name:', snapshots[0]['create-time-object'])
        self.assertTrue(snapshots[0]['name'] == snapshotName)
        LOG.info('Snapshot name:', snapshots[0]['name'])

    def test_fail_invalid_name(self):
        """
            Verify error message when snapshot name is invalid.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        snapshotName = 'Snap$hot'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening dialog')
        wizard = CreateLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Dialog is open.')

        LOG.step('Verifying error message on invalid snapshot name')
        wizard.activePage.setName(name=snapshotName)
        self.assertTrue(wizard.activePage.txtName.getText() == snapshotName)
        LOG.info('Snapshot name set:', wizard.activePage.txtName.getText())
        self.assertTrue(wizard.activePage.lblNameError.isVisible())
        LOG.info('Error message displayed:', wizard.activePage.lblNameError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_create_sequent(self):
        """
            Verify default name has increased number when snapshot with default name exists.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening dialog')
        wizard = CreateLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Dialog is open.')

        LOG.step('Creating snapshot with default name')
        self.assertTrue(wizard.activePage.txtName.getText() == lunNamePrefix + '_1_snap_0')
        LOG.info('Default snapshot name set:', wizard.activePage.txtName.getText())
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Subsequent creation of snapshot with default name')
        wizard.open(name=lunNamePrefix + '_1')
        self.assertTrue(wizard.activePage.txtName.getText() == lunNamePrefix + '_1_snap_1')
        LOG.info('Default snapshot name set:', wizard.activePage.txtName.getText())
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step("Verifying snapshots' names")
        snapshotNames = [snapshot['name'] for snapshot in self.marscluster.snapshot.show(json=True)]
        self.assertTrue(len(snapshotNames) == 2)
        self.assertTrue((lunNamePrefix + '_1_snap_0') in snapshotNames)
        LOG.info('Snapshot found:', lunNamePrefix + '_1_snap_0')
        self.assertTrue((lunNamePrefix + '_1_snap_1') in snapshotNames)
        LOG.info('Snapshot found:', lunNamePrefix + '_1_snap_1')

    def test_dialog_not_available(self):
        """
            Verify the dialog is not available when 0 or > 2 LUNs selected in grid.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Verifying dialog is unavailable when no LUNs selected')
        self.lunsPage.gridLUNs.unselect()
        selectedLUNs = self.lunsPage.gridLUNs.find(selected=True)
        self.assertFalse(selectedLUNs)
        LOG.info('Selected LUNs:', selectedLUNs)
        self.assertFalse(self.lunsPage.menuCreate.isItemEnabled(item='Snapshot copy'))
        LOG.info("Menu item 'Snapshot copy' enabled:",
            self.lunsPage.menuCreate.isItemEnabled(item='Snapshot copy'))

        LOG.step('Verifying dialog is unavailable when multiple LUNs selected')
        self.lunsPage.gridLUNs.unselect()
        self.lunsPage.gridLUNs.select(name=[lunNamePrefix + '_1', lunNamePrefix + '_2'])
        selectedLUNs = [lun['name'] for lun in self.lunsPage.gridLUNs.find(selected=True)]
        self.assertTrue(len(selectedLUNs) == 2)
        LOG.info('Selected LUNs:', selectedLUNs)
        self.assertFalse(self.lunsPage.menuCreate.isItemEnabled(item='Snapshot copy'))
        LOG.info("Menu item 'Snapshot copy' enabled:",
            self.lunsPage.menuCreate.isItemEnabled(item='Snapshot copy'))

    def test_dialog_cancel(self):
        """
            Verify canceling dialog without submission leaves LUNs and snapshots intact.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening dialog')
        wizard = CreateLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Dialog is open.')

        LOG.step('Canceling dialog without submission')
        wizard.cancel()
        LOG.info('Dialog closed.')

        LOG.step('Verifying no snapshots have been created')
        snapshots = self.marscluster.snapshot.show(json=True)
        self.assertFalse(snapshots)
        LOG.info('Created snapshots:', snapshots)

    def testTeardown(self):
        self.driver.close()

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()
        self.marscluster.snapshot.deleteAll()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        LOG.info('LUNs & snapshots cleaned up.')


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testCreateLUNSnapshotWizard = TestCreateLUNSnapshotWizard()
    sys.exit(testCreateLUNSnapshotWizard.numberOfFailedTests())
