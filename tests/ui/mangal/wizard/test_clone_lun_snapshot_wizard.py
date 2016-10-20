#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Clone a Snapshot Copy' wizard"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import random
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.page.lun_details_page import LUNDetailsPage
from mangal.wizard.clone_lun_snapshot_wizard import *
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


class TestCloneLUNSnapshotWizard(FRTestCase):
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

        self.marscluster.igroup.destroyAll()
        LOG.info('Initiator groups destroyed.')

        self._deleteDependentConsistencyGroups()
        LOG.info('Consistency groups destroyed.')

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

    def test_clone_no_ig_cg(self):
        """
            Verify LUN snapshot cloning when no initiator/consistency groups exist.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap'
        cloneName = lunName + '_clone_0'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        luns = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', luns)

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        LOG.info('Snapshot created:\n', snapshots)

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        self._navigateToLUNSnapshotsPage(lunName=lunName)

        LOG.step('Opening wizard')
        wizard = CloneLUNSnapshotWizard(driver=self.driver)
        wizard.open(lunName=lunName, lunSnapshotName=snapshotName)
        LOG.info('Wizard open.')

        LOG.step('Verifying default details of LUN snapshot clone')
        self.assertTrue(wizard.activePage.lblSubtitle.getText() == snapshotName)
        LOG.info('LUN snapshot name:', wizard.activePage.lblSubtitle.getText())

        self.assertTrue(wizard.activePage.txtName.getText() == cloneName)
        LOG.info('LUN snapshot clone name:', wizard.activePage.txtName.getText())
        self.assertFalse(wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        LOG.info('Parent consistency group is enabled:',
            wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        wizard.activePage.dLstMappedTo.expand()
        wizard.selectInitiatorGroupsPage.waitUntilOpen()
        initiatorGroups = wizard.selectInitiatorGroupsPage.gridInitiatorGroups.find()
        self.assertFalse(initiatorGroups)
        LOG.info('Initiator groups available:', initiatorGroups)
        wizard.activePage.dLstMappedTo.collapse()

        LOG.step('Cloning LUN snapshot')
        wizard.activePage.submit()
        self._verifyClone(snapshotName=snapshotName, cloneName=cloneName)

    def test_clone_not_mapped(self):
        """
            Verify LUN snapshot cloning when initiator and consistency groups exist but not mapped.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap'
        cloneName = lunName + '_clone_0'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        parentConsistencyGroupName = 'Parent-CG'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        LOG.info('LUN created:\n', luns)

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        LOG.info('Snapshot created:\n', snapshots)

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        originalInitiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(originalInitiatorGroups) == initiatorGroupsNumber)
        LOG.info('Initiator groups created:\n', originalInitiatorGroups)

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        self._navigateToLUNSnapshotsPage(lunName=lunName)

        LOG.step('Opening wizard')
        wizard = CloneLUNSnapshotWizard(driver=self.driver)
        wizard.open(lunName=lunName, lunSnapshotName=snapshotName)
        LOG.info('Wizard open.')

        LOG.step('Verifying default details of LUN snapshot clone')
        self.assertTrue(wizard.activePage.txtName.getText() == cloneName)
        LOG.info('Default LUN snapshot clone name:', wizard.activePage.txtName.getText())
        wizard.activePage.dLstMappedTo.expand()
        wizard.selectInitiatorGroupsPage.waitUntilOpen()
        initiatorGroups = wizard.selectInitiatorGroupsPage.gridInitiatorGroups.find()
        self.assertTrue(len(initiatorGroups) == len(originalInitiatorGroups))
        mappedInitiatorGroups = [initiatorGroup for initiatorGroup in initiatorGroups if
            initiatorGroup['selected'] == True]
        self.assertFalse(mappedInitiatorGroups)
        LOG.info('Mapped initiator groups:', mappedInitiatorGroups)
        wizard.activePage.dLstMappedTo.collapse()
        self.assertTrue(wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        LOG.info('Parent consistency group is enabled:',
            wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        consistencyGroups = wizard.activePage.cBoxParentConsistencyGroup.getItems()
        self.assertTrue(parentConsistencyGroupName in consistencyGroups)
        LOG.info('Consistency groups available:', consistencyGroups)

        LOG.step('Cloning LUN')
        wizard.activePage.submit()
        self._verifyClone(snapshotName=snapshotName, cloneName=cloneName)

    def test_clone_mapped(self):
        """
            Verify LUN snapshot cloning when mapped to initiator and consistency groups.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap'
        cloneName = lunName + '_clone_0'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        parentConsistencyGroupName = 'Parent-CG'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        LOG.info('LUN created:\n', luns)

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        LOG.info('Snapshot created:\n', snapshots)

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        originalInitiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(originalInitiatorGroups) == initiatorGroupsNumber)
        LOG.info('Initiator groups created:\n', originalInitiatorGroups)

        LOG.step('Mapping LUN snapshot to initiator groups')
        self.marscluster.lun.map({'name': lunName, 'igroup': originalInitiatorGroups[0]['name']})
        self.marscluster.lun.map({'name': lunName, 'igroup': originalInitiatorGroups[-1]['name']})
        LOG.info('LUN snapshot initiator group mapping:', self.marscluster.lun.mapped_show())

        LOG.step('Creating consistency group')
        self.marscluster.cg.create({'name': parentConsistencyGroupName, 'members': lunName})
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        lun = [lun for lun in self.marscluster.lun.show(json=True) if lun['name'] ==
            parentConsistencyGroupName + '/' + lunNamePrefix + '_1'][0]
        LOG.info('Consistency group created and mapped:', lun['maps'])

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        self._navigateToLUNSnapshotsPage(lunName=lunName)

        LOG.step('Opening wizard')
        wizard = CloneLUNSnapshotWizard(driver=self.driver)
        wizard.open(lunName=lunName, lunSnapshotName=snapshotName)
        LOG.info('Wizard open.')

        LOG.step('Verifying default details of LUN snapshot clone')
        self.assertTrue(wizard.activePage.txtName.getText() == cloneName)
        LOG.info('Default LUN snapshot clone name:', wizard.activePage.txtName.getText())
        wizard.activePage.dLstMappedTo.expand()
        wizard.selectInitiatorGroupsPage.waitUntilOpen()
        initiatorGroups = wizard.selectInitiatorGroupsPage.gridInitiatorGroups.find()
        self.assertTrue(len(initiatorGroups) == len(originalInitiatorGroups))
        mappedInitiatorGroups = [initiatorGroup for initiatorGroup in initiatorGroups if
            initiatorGroup['selected'] == True]
        self.assertTrue(len(mappedInitiatorGroups) == 2)
        self.assertTrue(mappedInitiatorGroups[0]['initiator_group'] in
            [originalInitiatorGroups[0]['name'], originalInitiatorGroups[-1]['name']])
        self.assertTrue(mappedInitiatorGroups[1]['initiator_group'] in
            [originalInitiatorGroups[0]['name'], originalInitiatorGroups[-1]['name']])
        LOG.info('Mapped initiator groups:', mappedInitiatorGroups)
        wizard.activePage.dLstMappedTo.collapse()
        self.assertTrue(wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        LOG.info('Parent consistency group is enabled:',
            wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        consistencyGroups = wizard.activePage.cBoxParentConsistencyGroup.getItems()
        self.assertTrue(parentConsistencyGroupName in consistencyGroups)
        LOG.info('Consistency groups available:', consistencyGroups)

        LOG.step('Cloning LUN snapshot')
        wizard.activePage.submit()
        self._verifyClone(snapshotName=snapshotName, cloneName=cloneName)

        luns = self.marscluster.lun.show(json=True)
        clone = [lun for lun in luns if lun['name'] == cloneName][0]
        mappedInitiatorGroups = [group['igroup-name'] for group in clone['maps']]
        self.assertTrue(len(mappedInitiatorGroups) == 2)
        self.assertTrue(mappedInitiatorGroups[0] in [originalInitiatorGroups[0]['name'],
            originalInitiatorGroups[-1]['name']])
        self.assertTrue(mappedInitiatorGroups[1] in [originalInitiatorGroups[0]['name'],
            originalInitiatorGroups[-1]['name']])
        LOG.info('Mapped initiator groups:', mappedInitiatorGroups)

    def test_clone_sequent(self):
        """
            Verify auto-naming of clone when previous auto-named clone already exists.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap'
        cloneName = lunName + '_clone_0'
        sequentCloneName = lunName + '_clone_1'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        LOG.info('LUN created:\n', luns)

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        LOG.info('Snapshot created:\n', snapshots)

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        self._navigateToLUNSnapshotsPage(lunName=lunName)

        LOG.step('Opening wizard')
        wizard = CloneLUNSnapshotWizard(driver=self.driver)
        wizard.open(lunName=lunName, lunSnapshotName=snapshotName)
        LOG.info('Wizard open.')

        LOG.step('Cloning LUN snapshot')
        wizard.activePage.submit()
        self._verifyClone(snapshotName=snapshotName, cloneName=cloneName)

        LOG.step('Opening wizard')
        wizard.open(lunName=lunName, lunSnapshotName=snapshotName)
        LOG.info('Wizard open.')

        LOG.step('Sequent cloning of LUN snapshot')
        wizard.activePage.submit()
        self._verifyClone(snapshotName=snapshotName,
            cloneName=sequentCloneName)

    def test_dialog_not_available(self):
        """
            Verify dialog not available when no or >= 2 LUNs selected.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        lunSnapshotNamePrefix = lunName + '_snap_'
        lunSnapshotCount = 4

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        luns = self.marscluster.lun.show(json=True)
        LOG.info('LUN created:\n', luns)

        LOG.step('Creating LUN snapshots')
        for count in range(lunSnapshotCount):
            self.marscluster.snapshot.create(luns=lunName, name=lunSnapshotNamePrefix + str(count))
        snapshots = self.marscluster.snapshot.show(json=True)
        LOG.info('Snapshot created:\n', snapshots)

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        self._navigateToLUNSnapshotsPage(lunName=lunName)

        LOG.step('Unselecting all LUN snapshots in grid')
        self.lunSnapshotsPage.gridSnapshots.unselect()
        snapshots = self.lunSnapshotsPage.gridSnapshots.find(selected=True)
        self.assertFalse(snapshots)
        LOG.info('Selected LUN snapshots:', snapshots)

        LOG.step("Verifying button 'Clone' disabled")
        self.assertFalse(self.lunSnapshotsPage.btnClone.isEnabled())
        LOG.info("Button 'Clone' is enabled:", self.lunSnapshotsPage.btnClone.isEnabled())

        LOG.step('Selecting 1 LUN snapshot in grid')
        self.lunSnapshotsPage.gridSnapshots.unselect()
        self.lunSnapshotsPage.gridSnapshots.select(name=lunSnapshotNamePrefix + '1')
        snapshots = self.lunSnapshotsPage.gridSnapshots.find(selected=True)
        self.assertTrue(len(snapshots) == 1)
        LOG.info('Selected LUN snapshots:', snapshots)

        LOG.step("Verifying button 'Clone' enabled")
        self.assertTrue(self.lunSnapshotsPage.btnClone.isEnabled())
        LOG.info("Button 'Clone' is enabled:", self.lunSnapshotsPage.btnClone.isEnabled())

        LOG.step('Selecting 2 LUN snapshots in grid')
        self.lunSnapshotsPage.gridSnapshots.unselect()
        self.lunSnapshotsPage.gridSnapshots.select(name=[lunSnapshotNamePrefix + '1',
            lunSnapshotNamePrefix + '2'])
        snapshots = self.lunSnapshotsPage.gridSnapshots.find(selected=True)
        self.assertTrue(len(snapshots) == 2)
        LOG.info('Selected LUN snapshots:', snapshots)

        LOG.step("Verifying button 'Clone' disabled")
        self.assertFalse(self.lunSnapshotsPage.btnClone.isEnabled())
        LOG.info("Button 'Clone' is enabled:", self.lunSnapshotsPage.btnClone.isEnabled())

    def test_dialog_cancel(self):
        """
            Verify closing wizard without submission does not affect LUN and its mappings.
        """
        lunNamePrefix = 'LuN'
        lunName = lunNamePrefix + '_1'
        snapshotName = lunName + '_snap'

        LOG.step('Creating LUNs')
        self.luns.create(count=1, size='1g', prefix=lunNamePrefix)
        luns = self.marscluster.lun.show(json=True)
        lunCount = len(luns)
        LOG.info('LUN created:\n', luns)

        LOG.step('Creating LUN snapshot')
        self.marscluster.snapshot.create(luns=lunName, name=snapshotName)
        snapshots = self.marscluster.snapshot.show(json=True)
        LOG.info('Snapshot created:\n', snapshots)

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        self._navigateToLUNSnapshotsPage(lunName=lunName)

        LOG.step('Opening wizard')
        wizard = CloneLUNSnapshotWizard(driver=self.driver)
        wizard.open(lunName=lunName, lunSnapshotName=snapshotName)
        LOG.info('Wizard open.')

        LOG.step('Closing wizard')
        wizard.cancel()
        LOG.info('Wizard closed.')

        LOG.step('Verifying no LUN snapshot clone has been created.')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == lunCount)
        LOG.info('No clone has been created.')

    def testTeardown(self):
        self.driver.close()

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()

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

    def _deleteDependentConsistencyGroups(self):
        while True:
            consistencyGroups = self.marscluster.cg.show(json=True)
            if not consistencyGroups:
                break
            else:
                for consistencyGroup in consistencyGroups:
                    if 'cg' not in consistencyGroup:
                        self.marscluster.cg.delete(name=consistencyGroup['name'])

    def _navigateToLUNSnapshotsPage(self, lunName):
        LOG.step('Navigating to LUN Snapshots page...')
        self.lunsPage.gridLUNs.clickLink(name=lunName, click={'name': lunName})
        self.lunDetailsPage.waitUntilOpen()
        self.lunDetailsPage.tabSnapshots.click()
        self.lunSnapshotsPage.waitUntilOpen()
        LOG.info('Browser landed on LUN Snapshots page.')

    def _verifyClone(self, snapshotName, cloneName):
        luns = self.marscluster.lun.show(json=True)
        snapshots = self.marscluster.snapshot.show(json=True)
        snapshot = [snapshot for snapshot in snapshots if snapshot['name'] == snapshotName][0]
        clone = [lun for lun in luns if (lun.get('parent-snapshot') == snapshotName and lun['name']
            == cloneName)][0]
        self.assertTrue(clone)
        self.assertTrue(clone['size'] == snapshot['lun-info']['size'])
        LOG.info("Clone size equal to snapshot size:", clone['size'])
        self.assertTrue(clone['parent'] == snapshot['object'])
        LOG.info("Cloned parent is original LUN:", clone['parent'])


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testCloneLUNSnapshotWizard = TestCloneLUNSnapshotWizard()
    sys.exit(testCloneLUNSnapshotWizard.numberOfFailedTests())
