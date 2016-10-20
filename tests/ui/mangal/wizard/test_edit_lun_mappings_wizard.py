#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Edit Mappings' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import random
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.edit_lun_mappings_wizard import *
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


class TestEditLUNMappingsWizard(FRTestCase):
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

    def test_no_ig(self):
        """
            Verify wizard's grid is empty when no initiators groups exist.
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

        LOG.step('Opening wizard')
        wizard = EditLUNMappingsWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open')

        LOG.step('Verifying no initiator groups are available')
        initiatorGroups = wizard.activePage.gridInitiatorGroups.find()
        self.assertFalse(initiatorGroups)
        LOG.info('Initiators groups available:', initiatorGroups)

        LOG.step("Verifying button 'OK' is disabled")
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' enabled:", wizard.activePage.btnOK.isEnabled())

    def test_mapped(self):
        """
            Verify proper LUN mapping on wizard's page.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Mapping LUN to initiator groups')
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[0]['name']})
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[-1]['name']})
        LOG.info('LUN mapped:\n', self.marscluster.lun.mapping_show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNMappingsWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open')

        self.assertTrue(wizard.activePage.lblName.getText() == lunNamePrefix + '_1')

        LOG.step('Verifying LUN mapping')
        groups = wizard.activePage.gridInitiatorGroups.find()
        self.assertTrue(len(initiatorGroups) == len(groups))
        for group in groups:
            if (group['initiator_groups'] == initiatorGroups[0]['name']) or \
            (group['initiator_groups'] == initiatorGroups[-1]['name']):
                self.assertTrue(group['selected'] == True)
                LOG.info("LUN '%s' mapped to initiator group: %s" % (lunNamePrefix + '_1',
                    group['initiator_groups']))
            else:
                self.assertFalse(group['selected'] == True)

    def test_not_mapped(self):
        """
            Verify no mapping on wizard's page when LUN not mapped.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNMappingsWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open')

        self.assertTrue(wizard.activePage.lblName.getText() == lunNamePrefix + '_1')

        LOG.step('Verifying LUN not mapped')
        groups = wizard.activePage.gridInitiatorGroups.find()
        self.assertTrue(len(initiatorGroups) == len(groups))
        for group in groups:
            self.assertFalse(group['selected'] == True)
            LOG.info("LUN '%s' mapped to '%s': %s" % (lunNamePrefix + '_1',
                group['initiator_groups'], group['selected']))

    def test_map(self):
        """
            Verify LUN mapping made in wizard.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNMappingsWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open')

        self.assertTrue(wizard.activePage.lblName.getText() == lunNamePrefix + '_1')

        LOG.step('Mapping LUN to initiator groups')
        self.assertTrue(len(initiatorGroups) == len(wizard.activePage.gridInitiatorGroups.find()))
        # Select first and last initiator groups in grid
        wizard.activePage.gridInitiatorGroups.select(initiator_groups=[initiatorGroups[0]['name'],
            initiatorGroups[-1]['name']])
        LOG.info('Initiator groups selected:\n',
            wizard.activePage.gridInitiatorGroups.find(selected=True))
        wizard.activePage.submit()
        LOG.info('Wizard submitted.')

        LOG.step('Verifying LUN mapping')
        mappedGroups = [group['igroup-name'] for group in
            self.marscluster.lun.mapping_show(json=True)]
        self.assertTrue(len(mappedGroups) == 2)
        self.assertTrue(initiatorGroups[0]['name'] in mappedGroups)
        LOG.info("LUN '%s' mapped to initiator group: %s" % (lunNamePrefix + '_1',
            initiatorGroups[0]['name']))
        self.assertTrue(initiatorGroups[-1]['name'] in mappedGroups)
        LOG.info("LUN '%s' mapped to initiator group: %s" % (lunNamePrefix + '_1',
            initiatorGroups[-1]['name']))

    def test_remap(self):
        """
            Verify proper LUN re-mapping on wizard's page.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Mapping LUN to initiator groups')
        # Map to first and last initiator groups
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[0]['name']})
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[-1]['name']})
        LOG.info('LUN mapped:\n', self.marscluster.lun.mapping_show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNMappingsWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open')

        LOG.step('Re-mapping LUN')
        # Map LUN to second initiator group instead of 1st and last ones
        wizard.activePage.selectInitiatorGroups(name=[initiatorGroups[1]['name']])
        LOG.info('Mapping set to initiator group:', initiatorGroups[1]['name'])
        wizard.activePage.submit()
        LOG.info('Wizard submitted.')

        LOG.step('Verifying LUN mapping')
        lunMapping = self.marscluster.lun.mapping_show(json=True)
        self.assertTrue(len(lunMapping) == 1)
        self.assertTrue(lunMapping[0]['igroup-name'] == initiatorGroups[1]['name'])
        LOG.info("LUN '%s' mapped to initiator group: %s" % (lunNamePrefix + '_1',
            lunMapping[0]['igroup-name']))

    def test_unmap(self):
        """
            Verify LUN un-mapping on wizard's page.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Mapping LUN to initiator groups')
        # Map to first and last initiator groups
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[0]['name']})
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[-1]['name']})
        LOG.info('LUN mapped:\n', [lun for lun in self.marscluster.lun.mapping_show(json=True) if
            lun['lun-name'] == lunNamePrefix + '_1'][0])

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNMappingsWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Unselecting all initiator groups')
        wizard.activePage.selectInitiatorGroups()
        self.assertFalse(wizard.activePage.gridInitiatorGroups.find(selected=True))
        LOG.info('Selected initiator groups:',
            wizard.activePage.gridInitiatorGroups.find(selected=True))
        wizard.activePage.submit()
        LOG.info('Wizard submitted.')

        LOG.step('Verifying LUN has been um-mapped')
        lunMapping = [lun for lun in self.marscluster.lun.mapping_show(json=True) if lun['lun-name']
            == lunNamePrefix + '_1']
        self.assertFalse(lunMapping)
        LOG.info("LUN '%s' has no mappings." % (lunNamePrefix + '_1'))

    def test_dialog_cancel(self):
        """
            Verify LUN mapping remains intact on wizard cancellation.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Mapping LUN to initiator groups')
        # Map to first and last initiator groups
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[0]['name']})
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[-1]['name']})
        originalMappings = [lun for lun in self.marscluster.lun.mapping_show(json=True) if
            lun['lun-name'] == lunNamePrefix + '_1']
        LOG.info('LUN mapped:\n', originalMappings)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNMappingsWizard(driver=self.driver)
        wizard.open(name=lunNamePrefix + '_1')
        LOG.info('Wizard open.')

        LOG.step('Canceling wizard')
        wizard.cancel()
        LOG.info('Wizard closed without submission.')

        LOG.step('Verifying LUN mappings')
        mappings = [lun['igroup-name'] for lun in self.marscluster.lun.mapping_show(json=True) if
            lun['lun-name'] == lunNamePrefix + '_1']
        self.assertTrue(len(originalMappings) == len(mappings))
        for mapping in originalMappings:
            self.assertTrue(mapping['igroup-name'] in mappings)
            LOG.info("LUN '%s' mapped to initiator group: %s" % (lunNamePrefix + '_1',
                mapping['igroup-name']))
        LOG.info('LUN mappings remain intact.')

    def test_dialog_not_available(self):
        """
            Verify menu item 'Edit -> Mappings' not available when multiple LUNs selected in grid.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunSize = 2
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        self.luns.create(count=lunCount, size=str(lunSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Mapping LUN to initiator groups')
        # Map to first and last initiator groups
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[0]['name']})
        self.marscluster.lun.map({'name': lunNamePrefix + '_1', 'igroup':
            initiatorGroups[-1]['name']})
        originalMappings = [lun for lun in self.marscluster.lun.mapping_show(json=True) if
            lun['lun-name'] == lunNamePrefix + '_1']
        LOG.info('LUN mapped:\n', originalMappings)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Selecting multiple LUNs')
        self.lunsPage.gridLUNs.select()
        LOG.info('LUNs selected:\n', self.lunsPage.gridLUNs.find(selected=True))

        LOG.step("Checking state of menu 'Edit'")
        self.assertFalse(self.lunsPage.menuEdit.isItemEnabled(item='Mappings'))
        LOG.info("Menu item 'Edit -> Mappings' is enabled:",
            self.lunsPage.menuEdit.isItemEnabled(item='Mappings'))

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
    testEditLUNMappingsWizard = TestEditLUNMappingsWizard()
    sys.exit(testEditLUNMappingsWizard.numberOfFailedTests())
