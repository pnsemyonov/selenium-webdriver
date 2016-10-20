#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Clone LUN' wizard"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import random
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.clone_lun_wizard import *
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


class TestCloneLUNWizard(FRTestCase):
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

        LOG.step('Cleaning out cluster content')
        LOG.info('Destroying LUNs...')
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.assertFalse(self.marscluster.lun.show(json=True))
        LOG.info('Done.')
        LOG.info('Destroying existing initiator groups...')
        self.marscluster.igroup.destroyAll()
        LOG.info('Done.')
        LOG.info('Destroying existing consistency groups...')
        self.deleteDependentConsistencyGroups()
        LOG.info('Done.')

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

    def deleteDependentConsistencyGroups(self):
        while True:
            consistencyGroups = self.marscluster.cg.show(json=True)
            if not consistencyGroups:
                break
            else:
                for consistencyGroup in consistencyGroups:
                    if 'cg' not in consistencyGroup:
                        self.marscluster.cg.delete(name=consistencyGroup['name'])

    def test_clone_no_ig_cg(self):
        """
            Verify LUN cloning when no initiator/consistency groups exist.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        originalLUNs = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', originalLUNs)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = CloneLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Verifying default details of LUN clone')
        self.assertTrue(wizard.activePage.txtName.getText() == lunNamePrefix + '_1_clone_0')
        LOG.info('Default LUN clone name:', wizard.activePage.txtName.getText())
        self.assertFalse(wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        LOG.info('Parent consistency group is enabled:',
            wizard.activePage.cBoxParentConsistencyGroup.isEnabled())
        wizard.activePage.dLstMappedTo.expand()
        wizard.selectInitiatorGroupsPage.waitUntilOpen()
        initiatorGroups = wizard.selectInitiatorGroupsPage.gridInitiatorGroups.find()
        self.assertFalse(initiatorGroups)
        LOG.info('Initiator groups available:', initiatorGroups)
        wizard.activePage.dLstMappedTo.collapse()

        LOG.step('Cloning LUN')
        wizard.activePage.submit()
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == len(originalLUNs) + 1)
        lun = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1'][0]
        clonedLUN = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1_clone_0'][0]
        self.assertTrue(clonedLUN['size'] == lun['size'])
        LOG.info("Cloned LUN's size equal to original:", clonedLUN['size'])
        self.assertTrue(clonedLUN['parent'] == lunNamePrefix + '_1')
        LOG.info("Cloned LUN's parent is original LUN:", clonedLUN['parent'])

    def test_clone_not_mapped(self):
        """
            Verify LUN cloning when initiator and consistency groups exist but not mapped.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        parentConsistencyGroupName = 'Parent-CG'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        originalLUNs = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', originalLUNs)

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        originalInitiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', originalInitiatorGroups)

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = CloneLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Verifying default details of LUN clone')
        self.assertTrue(wizard.activePage.txtName.getText() == lunNamePrefix + '_1_clone_0')
        LOG.info('Default LUN clone name:', wizard.activePage.txtName.getText())
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
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == len(originalLUNs) + 1)
        lun = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1'][0]
        clonedLUN = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1_clone_0'][0]
        self.assertTrue(clonedLUN['size'] == lun['size'])
        LOG.info("Cloned LUN's size equal to original:", clonedLUN['size'])
        self.assertTrue(clonedLUN['parent'] == lunNamePrefix + '_1')
        LOG.info("Cloned LUN's parent is original LUN:", clonedLUN['parent'])

    def test_clone_mapped(self):
        """
            Verify LUN cloning when mapped to initiator and consistency groups.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        parentConsistencyGroupName = 'Parent-CG'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        originalLUNs = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', originalLUNs)

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        originalInitiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', originalInitiatorGroups)

        LOG.step('Mapping LUN to initiator groups')
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            originalInitiatorGroups[0]['name']})
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            originalInitiatorGroups[-1]['name']})
        LOG.info('LUN initiator group mapping:', self.marscluster.lun.mapped_show())

        LOG.step('Creating consistency group')
        self.marscluster.cg.create({'name': parentConsistencyGroupName, 'members': lunNamePrefix +
            '_1'})
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        lun = [lun for lun in self.marscluster.lun.show(json=True) if lun['name'] ==
            parentConsistencyGroupName + '/' + lunNamePrefix + '_1'][0]
        LOG.info('Consistency group created and mapped:', lun['maps'])

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = CloneLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Verifying default details of LUN clone')
        self.assertTrue(wizard.activePage.txtName.getText() == lunNamePrefix + '_1_clone_0')
        LOG.info('Default LUN clone name:', wizard.activePage.txtName.getText())
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

        LOG.step('Cloning LUN')
        wizard.activePage.submit()
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == len(originalLUNs) + 1)
        clonedLUN = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1_clone_0'][0]
        self.assertTrue(clonedLUN['size'] == lun['size'])
        LOG.info("Cloned LUN's size equal to original:", clonedLUN['size'])
        self.assertTrue(clonedLUN['parent'] == parentConsistencyGroupName + '/' + lunNamePrefix +
            '_1')
        LOG.info("Cloned LUN's parent is original LUN:", clonedLUN['parent'])
        mappedInitiatorGroups = [group['igroup-name'] for group in clonedLUN['maps']]
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
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        parentConsistencyGroupName = 'Parent-CG'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        originalLUNs = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', originalLUNs)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = CloneLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Cloning LUN')
        wizard.activePage.submit()
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == len(originalLUNs) + 1)
        clonedLUN = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1_clone_0'][0]
        self.assertTrue(clonedLUN['size'] == lun['size'])
        LOG.info("Cloned LUN's size equal to original:", clonedLUN['size'])
        self.assertTrue(clonedLUN['parent'] == lunNamePrefix + '_1')
        LOG.info("Cloned LUN's parent is original LUN:", clonedLUN['parent'])

        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = CloneLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Sequent cloning of LUN')
        wizard.activePage.submit()
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == len(originalLUNs) + 2)
        clonedLUN = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1_clone_1'][0]
        self.assertTrue(clonedLUN['size'] == lun['size'])
        LOG.info("Cloned LUN's size equal to original:", clonedLUN['size'])
        self.assertTrue(clonedLUN['parent'] == lunNamePrefix + '_1')
        LOG.info("Cloned LUN's parent is original LUN:", clonedLUN['parent'])

    def test_dialog_not_available(self):
        """
            Verify dialog not available when no or >= 2 LUNs selected.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        originalLUNs = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', originalLUNs)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Unselecting all LUNs in grid')
        self.lunsPage.gridLUNs.unselect()
        luns = self.lunsPage.gridLUNs.find(selected=True)
        self.assertFalse(luns)
        LOG.info('Selected LUNs:', luns)

        LOG.step("Verifying button 'Clone' disabled")
        self.assertFalse(self.lunsPage.btnClone.isEnabled())
        LOG.info("Button 'Clone' is enabled:", self.lunsPage.btnClone.isEnabled())

        LOG.step('Selecting 1 LUN in grid')
        self.lunsPage.gridLUNs.unselect()
        self.lunsPage.gridLUNs.select(name=lunNamePrefix + '_1')
        luns = self.lunsPage.gridLUNs.find(selected=True)
        self.assertTrue(len(luns) == 1)
        LOG.info('Selected LUNs:', luns)

        LOG.step("Verifying button 'Clone' enabled")
        self.assertTrue(self.lunsPage.btnClone.isEnabled())
        LOG.info("Button 'Clone' is enabled:", self.lunsPage.btnClone.isEnabled())

        LOG.step('Selecting 2 LUNs in grid')
        self.lunsPage.gridLUNs.unselect()
        self.lunsPage.gridLUNs.select(name=[lunNamePrefix + '_1', lunNamePrefix + '_2'])
        luns = self.lunsPage.gridLUNs.find(selected=True)
        self.assertTrue(len(luns) == 2)
        LOG.info('Selected LUNs:', luns)

        LOG.step("Verifying button 'Clone' disabled")
        self.assertFalse(self.lunsPage.btnClone.isEnabled())
        LOG.info("Button 'Clone' is enabled:", self.lunsPage.btnClone.isEnabled())

    def test_dialog_cancel(self):
        """
            Verify closing wizard without submission does not affect LUN and its mappings.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 1
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        originalLUNs = self.marscluster.lun.show(json=True)
        LOG.info('LUNs created:\n', originalLUNs)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = CloneLUNWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Closing wizard')
        wizard.cancel()
        LOG.info('Wizard closed.')

        LOG.step('Verifying no LUN clone has been created.')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == len(originalLUNs))
        LOG.info('No clone has been created.')

        LOG.step('Verifying original LUN remained intact.')
        originalLUN = [lun for lun in originalLUNs if lun['name'] == lunNamePrefix + '_1'][0]
        lun = [lun for lun in luns if lun['name'] == lunNamePrefix + '_1'][0]
        self.assertTrue(originalLUN['size'] == lun['size'])
        self.assertFalse(lun['igroups'])
        LOG.info('LUN mapping has not been changed.')

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
    testCloneLUNWizard = TestCloneLUNWizard()
    sys.exit(testCloneLUNWizard.numberOfFailedTests())
