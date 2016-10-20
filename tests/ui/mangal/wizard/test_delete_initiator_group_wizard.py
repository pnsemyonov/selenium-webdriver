#!/usr/bin/env python

purpose = """Mangal UI Initiator Groups page: Functional testing of initiator group deletion"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import re
import random
import time
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from mangal.page.delete_mapped_initiator_group_page import *
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


class TestDeleteInitiatorGroupWizard(FRTestCase):
    """
        In fact, there is no such a wizard as 'Delete Initiator Group', this is just function on
          clicking button 'Delete'.
    """
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
        self.initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)

        LOG.step('Cleaning out cluster content')
        LOG.info('Destroying LUNs...')
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.assertFalse(self.marscluster.lun.show(json=True))
        LOG.info('Done.')
        LOG.info('Destroying existing initiator groups...')
        self.marscluster.igroup.destroyAll()
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

        LOG.info('Navigating to Initiator Groups page...')
        self.headerPage.btnManager.click()
        self.allStoragePage.tabInitiatorGroups.click()
        self.initiatorGroupsPage.waitUntilOpen()
        LOG.info('Browser landed on Initiator Groups page.')

    def test_delete_single(self):
        """
            Verify deletion of single unmapped initiator group.
        """
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 5

        initiatorGroupNames = self._createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupNumber)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Selecting initiator group in grid')
        self.initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiatorGroupNames[0])
        selectedGroups = self.initiatorGroupsPage.gridInitiatorGroups.find(selected=True)
        self.assertTrue(len(selectedGroups) == 1)
        self.assertTrue(selectedGroups[0]['initiator_group'] == initiatorGroupNames[0])
        LOG.info('Initiator group selected:', initiatorGroupNames[0])

        LOG.step('Deleting and verifying initiator group has been deleted')
        self.initiatorGroupsPage.btnDelete.click()
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupNumber - 1)
        self.assertFalse(initiatorGroupNames[0] in [group['name'] for group in initiatorGroups])
        LOG.info("Initiator group '%s' is not present:\n" % initiatorGroupNames[0].encode('utf-8'),
            initiatorGroups)

    def test_delete_multi(self):
        """
            Verify deletion of multiple unmapped initiator groups.
        """
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 9

        initiatorGroupNames = self._createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupNumber)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Selecting initiator groups in grid')
        self.initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=
            initiatorGroupNames[:initiatorGroupNumber / 2])
        selectedGroups = self.initiatorGroupsPage.gridInitiatorGroups.find(selected=True)
        self.assertTrue(len(selectedGroups) == initiatorGroupNumber / 2)
        LOG.info('Initiator group selected:', selectedGroups)

        LOG.step('Deleting and verifying initiator group has been deleted')
        self.initiatorGroupsPage.btnDelete.click()
        # Give some time to perform operation
        time.sleep(2)
        initiatorGroupNames = [group['name'] for group in self.marscluster.igroup.show(json=True)]
        self.assertTrue(len(initiatorGroupNames) == initiatorGroupNumber - (initiatorGroupNumber /
            2))
        for group in selectedGroups:
            self.assertFalse(group['initiator_group'] in initiatorGroupNames)
            LOG.info('Initiator group is not present:', group['initiator_group'])

    def test_delete_mapped(self):
        """
            Verify warning when initiator group with mapped LUN is getting deleted.
        """
        lunName = 'lun1'
        initiatorGroupName = 'ig1'

        LOG.step('Creating initiator group')
        fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
        self.marscluster.igroup.create(name=initiatorGroupName, ostype='windows',
            initiators=fictiveWWPN)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        LOG.info('Initiator group created:\n', initiatorGroups[0])

        LOG.step('Creating and mapping LUN')
        self.marscluster.lun.create(name=lunName, size='1g')
        self.marscluster.lun.map(name=lunName, igroup=initiatorGroups[0]['name'])
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        self.assertTrue(len(luns[0]['maps']) == 1)
        self.assertTrue(luns[0]['maps'][0]['igroup-name'] == initiatorGroupName)
        LOG.info('LUN created:\n', luns[0])

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Deleting initiator group: %s' % initiatorGroupName)
        self.initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiatorGroupName)
        self.initiatorGroupsPage.btnDelete.click()
        deleteMappedInitiatorGroupPage = DeleteMappedInitiatorGroupPage(driver=self.driver)
        deleteMappedInitiatorGroupPage.waitUntilOpen()
        LOG.info('Warning message window open:', deleteMappedInitiatorGroupPage.lblTitle.getText())
        deleteMappedInitiatorGroupPage.btnClose.click()

        LOG.step('Verifying initiator group has not been deleted')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        LOG.info('Initiator group exists:', initiatorGroups[0]['name'])

    def test_delete_multi_mapped(self):
        """
            Verify warning when multiple initiator groups with mapped LUNs are getting deleted.
        """
        initiatorGroupPrefix = 'ig'
        initiatorGroupNumber = 3
        lunsPrefix = 'lun'

        initiatorGroupNames = self._createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating and mapping LUNs')
        self.luns.create(count=initiatorGroupNumber, size='1g', prefix=lunsPrefix)
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == initiatorGroupNumber)
        LOG.info('LUNs created:\n', luns)
        for count in range(len(luns)):
            self.marscluster.lun.map(name=luns[count]['name'], igroup=initiatorGroupNames[count])
        luns = self.marscluster.lun.show(json=True)
        for count in range(len(luns)):
            self.assertTrue(len(luns[count]['maps']) == 1)
            self.assertTrue(luns[count]['maps'][0]['igroup-name'] == initiatorGroupNames[count])
        LOG.info('LUNs mapped to initiator groups:\n', [(lun['name'], lun['maps']) for lun in luns])

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Deleting all initiator groups at once: %s' % initiatorGroupNames)
        self.initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiatorGroupNames)
        self.initiatorGroupsPage.btnDelete.click()
        deleteMappedInitiatorGroupPage = DeleteMappedInitiatorGroupPage(driver=self.driver)
        deleteMappedInitiatorGroupPage.waitUntilOpen()
        LOG.info('Warning message window open:', deleteMappedInitiatorGroupPage.lblTitle.getText())
        deleteMappedInitiatorGroupPage.btnClose.click()

        LOG.step('Verifying initiator groups have not been deleted')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupNumber)
        LOG.info('Initiator groups exist:', initiatorGroups)

    def test_delete_multi_mixed(self):
        """
            Verify warning when at least one of multiple selected initiator groups has mapping with
              LUN.
        """
        initiatorGroupPrefix = 'ig'
        initiatorGroupNumber = 3
        lunName = 'lun1'

        initiatorGroupNames = self._createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating LUN')
        self.marscluster.lun.create(name=lunName, size='1g')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        LOG.info('LUN created:\n', luns[0])

        LOG.step('Mapping LUN to one of initiator groups')
        self.marscluster.lun.map(name=lunName, igroup=initiatorGroupNames[0])
        lun = self.marscluster.lun.show(json=True)[0]
        self.assertTrue(len(lun['maps']) == 1)
        self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroupNames[0])
        LOG.info("LUN '%s' mapped to initiator group: %s" %(lun['name'],
            lun['maps'][0]['igroup-name']))

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Deleting all initiator groups at once: %s' % initiatorGroupNames)
        self.initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiatorGroupNames)
        self.initiatorGroupsPage.btnDelete.click()
        deleteMappedInitiatorGroupPage = DeleteMappedInitiatorGroupPage(driver=self.driver)
        deleteMappedInitiatorGroupPage.waitUntilOpen()
        LOG.info('Warning message window open:', deleteMappedInitiatorGroupPage.lblTitle.getText())
        deleteMappedInitiatorGroupPage.btnClose.click()

        LOG.step('Verifying initiator groups have not been deleted')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupNumber)
        LOG.info('Initiator groups exist:', initiatorGroups)

    def test_delete_not_available(self):
        """
            Verify deletion is not available when no initiator groups selected in grid.
        """
        initiatorGroupPrefix = 'ig'
        initiatorGroupNumber = 3

        initiatorGroupNames = self._createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupNumber)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Deselecting all initiator groups in grid')
        self.initiatorGroupsPage.gridInitiatorGroups.unselect(initiator_group=initiatorGroupNames)
        selectedGroups = self.initiatorGroupsPage.gridInitiatorGroups.find(selected=True)
        self.assertFalse(selectedGroups)
        LOG.info('Selected initiator groups:', selectedGroups)

        LOG.step("Verifying button 'Delete' is disabled in tool bar")
        self.assertFalse(self.initiatorGroupsPage.btnDelete.isEnabled())
        LOG.info("Button 'Delete' is enabled:", self.initiatorGroupsPage.btnDelete.isEnabled())

    def testTeardown(self):
        self.driver.close()

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.marscluster.igroup.destroyAll()
        LOG.info('LUNs & initiator groups destroyed.')

    def _createInitiatorGroups(self, prefix, number, osType='vmware'):
        LOG.step('Creating initiator group(s)')
        for groupNumber in range(number):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=prefix + '-' + str(groupNumber),
                ostype=osType.lower(), initiators=fictiveWWPN)
        groupNames = [group['name'] for group in self.marscluster.igroup.show(json=True)]
        LOG.info('Initiator group(s) created:', groupNames)
        return groupNames

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testDeleteInitiatorGroupWizard = TestDeleteInitiatorGroupWizard()
    sys.exit(testDeleteInitiatorGroupWizard.numberOfFailedTests())
