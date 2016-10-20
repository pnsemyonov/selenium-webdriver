#!/usr/bin/env python

purpose = """Mangal UI LUN Snapshots Page: Functional testing of 'Rename Snapshot Copy' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.page.lun_details_page import LUNDetailsPage
from mangal.page.lun_snapshots_page import LUNSnapshotsPage
from mangal.wizard.rename_lun_snapshot_wizard import *
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


class TestRenameLUNSnapshotWizard(FRTestCase):
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
        self.lunDetailsPage = LUNDetailsPage(driver=self.driver)
        self.lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver)

        LOG.step('Cleaning out cluster content')
        snapshots = self.marscluster.snapshot.show(json=True)
        for snapshot in snapshots:
            self.marscluster.snapshot.delete(name=snapshot['name'], lun=snapshot['object'])
        self.assertFalse(self.marscluster.snapshot.show(json=True))
        LOG.info('Snapshots destroyed.')

        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.assertFalse(self.marscluster.lun.show(json=True))
        LOG.info('LUNs destroyed.')

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

        LOG.step('Navigating to LUNs page')
        self.headerPage.btnManager.click()
        self.allStoragePage.tabLUNs.click()
        self.lunsPage.waitUntilOpen()
        LOG.info('Browser landed on LUNs page.')

    def test_valid_name(self):
        """
            Verify LUN snapshot renaming with valid name.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap_0'
        snapshotNewName = snapshotName + '.m'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if (snapshot['name'] == snapshotName and
            snapshot['object'] == lunName)][0]
        snapshotUUID = snapshot['uuid']
        LOG.info('Snapshot created:\n', snapshot)

        LOG.step("LUN '%s': Opening Snapshots page" % lunName)
        lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver, url=self.webUIHostName +
            ('/#manager/storage/allstorage/luns/%s/snapshot' % lunName))
        lunSnapshotsPage.open()
        lunSnapshotsPage.waitUntilOpen()
        LOG.info('LUN Snapshots page is open.')

        LOG.step('Renaming LUN snapshot in dialog')
        wizard = RenameLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=snapshotName)
        LOG.info('Old snapshot name:', snapshotName)
        wizard.renameLUNSnapshotPage.renameLUNSnapshot(name=snapshotNewName)
        LOG.info('New snapshot name:', snapshotNewName)
        wizard.renameLUNSnapshotPage.submit()
        LOG.info('Rename submitted.')

        LOG.step('Verifying LUN snapshot name has been changed')
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if snapshot['uuid'] == snapshotUUID][0]
        self.assertTrue(snapshot['name'] == snapshotNewName)
        LOG.info('LUN snapshot has been renamed:\n', snapshot)

    def test_invalid_name(self):
        """
            Verify LUN snapshot renaming with invalid name.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap_0'
        snapshotNewName = snapshotName + '*&#@1A_^?,'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if (snapshot['name'] == snapshotName and
            snapshot['object'] == lunName)][0]
        snapshotUUID = snapshot['uuid']
        LOG.info('Snapshot created:\n', snapshot)

        LOG.step("LUN '%s': Opening Snapshots page" % lunName)
        lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver, url=self.webUIHostName +
            ('/#manager/storage/allstorage/luns/%s/snapshot' % lunName))
        lunSnapshotsPage.open()
        lunSnapshotsPage.waitUntilOpen()
        LOG.info('LUN Snapshots page is open.')

        LOG.step('Renaming LUN snapshot in dialog')
        wizard = RenameLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=snapshotName)
        LOG.info('Old snapshot name:', snapshotName)
        wizard.renameLUNSnapshotPage.renameLUNSnapshot(name=snapshotNewName)
        LOG.info('New snapshot name:', snapshotNewName)

        LOG.step('Verifying LUN snapshot name error message')
        wizard.activePage.lblNameError.waitUntilPresent()
        LOG.info('Name error message:', wizard.activePage.lblNameError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Verifying LUN snapshot has not been renamed')
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if snapshot['uuid'] == snapshotUUID][0]
        self.assertTrue(snapshot['name'] == snapshotName)
        LOG.info('LUN snapshot has not been renamed:\n', snapshot)

    def test_unicode_name(self):
        """
            Verify error message on setting LUN snapshot name containing Unicode characters.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap_0'
        snapshotNewName = snapshotName + u'Fran\u00e7ais'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if (snapshot['name'] == snapshotName and
            snapshot['object'] == lunName)][0]
        snapshotUUID = snapshot['uuid']
        LOG.info('Snapshot created:\n', snapshot)

        LOG.step("LUN '%s': Opening Snapshots page" % lunName)
        lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver, url=self.webUIHostName +
            ('/#manager/storage/allstorage/luns/%s/snapshot' % lunName))
        lunSnapshotsPage.open()
        lunSnapshotsPage.waitUntilOpen()
        LOG.info('LUN Snapshots page is open.')

        LOG.step('Renaming LUN snapshot in dialog')
        wizard = RenameLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=snapshotName)
        LOG.info('Old snapshot name:', snapshotName)
        wizard.renameLUNSnapshotPage.renameLUNSnapshot(name=snapshotNewName)
        LOG.info('New snapshot name:', snapshotNewName)

        LOG.step('Verifying LUN snapshot name error message')
        wizard.activePage.lblNameError.waitUntilPresent()
        LOG.info('Name error message:', wizard.activePage.lblNameError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Verifying LUN snapshot has not been renamed')
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if snapshot['uuid'] == snapshotUUID][0]
        self.assertTrue(snapshot['name'] == snapshotName)
        LOG.info('LUN snapshot has not been renamed:\n', snapshot)

    def test_dialog_not_available(self):
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap_0'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if (snapshot['name'] == snapshotName and
            snapshot['object'] == lunName)][0]
        snapshotUUID = snapshot['uuid']
        LOG.info('Snapshot created:\n', snapshot)

        LOG.step("LUN '%s': Opening Snapshots page" % lunName)
        lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver, url=self.webUIHostName +
            ('/#manager/storage/allstorage/luns/%s/snapshot' % lunName))
        lunSnapshotsPage.open()
        lunSnapshotsPage.waitUntilOpen()
        LOG.info('LUN Snapshots page is open.')

        LOG.step('Unselecting all LUN snapshots in grid')
        lunSnapshotsPage.gridSnapshots.unselect()
        selectedSnapshots = lunSnapshotsPage.gridSnapshots.find(selected=True)
        self.assertFalse(selectedSnapshots)
        LOG.info('LUN snapshots selected in grid:', selectedSnapshots)

        LOG.step("Verifying menu 'Edit' is unavailable")
        self.assertFalse(lunSnapshotsPage.menuEdit.isEnabled())
        LOG.info("Menu 'Edit' is enabled:", lunSnapshotsPage.menuEdit.isEnabled())

    def test_dialog_cancel(self):
        """
            Verify LUN snapshot name remains intact on dialog cancel.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap_0'
        snapshotNewName = snapshotName + '.m'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if (snapshot['name'] == snapshotName and
            snapshot['object'] == lunName)][0]
        snapshotUUID = snapshot['uuid']
        LOG.info('Snapshot created:\n', snapshot)

        LOG.step("LUN '%s': Opening Snapshots page" % lunName)
        lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver, url=self.webUIHostName +
            ('/#manager/storage/allstorage/luns/%s/snapshot' % lunName))
        lunSnapshotsPage.open()
        lunSnapshotsPage.waitUntilOpen()
        LOG.info('LUN Snapshots page is open.')

        LOG.step('Renaming LUN snapshot in dialog')
        wizard = RenameLUNSnapshotWizard(driver=self.driver)
        wizard.open(name=snapshotName)
        LOG.info('Old snapshot name:', snapshotName)
        wizard.renameLUNSnapshotPage.renameLUNSnapshot(name=snapshotNewName)
        self.assertTrue(wizard.activePage.txtName.getText() == snapshotNewName)
        LOG.info('New snapshot name:', snapshotNewName)

        LOG.step('Canceling dialog without submission')
        wizard.cancel()
        LOG.info('Dialog cancelled.')

        LOG.step('Verifying LUN snapshot has not been renamed')
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if snapshot['uuid'] == snapshotUUID][0]
        self.assertTrue(snapshot['name'] == snapshotName)
        LOG.info('LUN snapshot has not been renamed:\n', snapshot)

    def testTeardown(self):
        self.driver.close()
        LOG.info('Driver closed.')

    def suiteTeardown(self):
        self.driver.quit()
        LOG.info('Driver quit.')

        LOG.step('Deleting snapshots')
        snapshots = self.marscluster.snapshot.show(json=True)
        for snapshot in snapshots:
            self.marscluster.snapshot.delete(name=snapshot['name'], lun=snapshot['object'])
        self.assertFalse(self.marscluster.snapshot.show(json=True))
        LOG.info('Snapshots deleted.')

        LOG.step('Destroying LUNs')
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        LOG.info('LUNs destroyed.')


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testRenameLUNSnapshotWizard = TestRenameLUNSnapshotWizard()
    sys.exit(testRenameLUNSnapshotWizard.numberOfFailedTests())
