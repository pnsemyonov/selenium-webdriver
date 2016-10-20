#!/usr/bin/env python

purpose = """Mangal: Initiator Groups page: Functional testing of 'Change Initiators' wizard"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import re
import random
import express
import frutil
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.change_initiators_wizard import *
from frlog import LOG
from frargs import ARGS
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


class TestChangeInitiatorsWizard(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.locale = ARGS.values.locale
        self.webUIHostName = frutil.getFQDN(self.marscluster.getMasterNode().hostname)

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

    def test_verify_wwpns_not_assigned(self):
        """
            Verify dialog shows WWPNs unselected in grid when they are not assigned to initiator
              group.
        """
        initiatorGroupName = 'IG-1'

        LOG.step('Creating initiator group with no WWPNs assigned')
        self.marscluster.igroup.create(name=initiatorGroupName, ostype='vmware')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        self.assertFalse(initiatorGroups[0]['initiators'])
        LOG.info('Initiator group created:\n', initiatorGroups[0])

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = ChangeInitiatorsWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroupName)
        LOG.info('Wizard open.')

        LOG.step('Verifying defaults')
        self.assertTrue(wizard.activePage.lblTitle.isVisible())
        LOG.info('Title is visible:', wizard.activePage.lblTitle.getText())
        self.assertTrue(wizard.activePage.lblSubtitle.getText() == initiatorGroupName)
        LOG.info('Initiator group name is visible:', wizard.activePage.lblSubtitle.getText())

        LOG.step('Verifying no WWPNs assigned to initiator group')
        wwpns = wizard.activePage.gridInitiatorWWPNs.find(selected=True)
        selectedWWPNs = wizard.activePage.gridInitiatorWWPNs.find(selected=True)
        self.assertFalse(selectedWWPNs)
        LOG.info('Selected WWPNs:', selectedWWPNs)

    def test_verify_wwpns_assigned(self):
        """
            Verify dialog shows WWPNs selected in grid when they are assigned to initiator group.
        """
        initiatorGroupName = 'IG-1'

        LOG.step('Creating initiator group with WWPNs assigned')
        fictiveWWPNs = []
        for _ in range(2):
            fictiveWWPNs.append(':'.join(re.findall('..', format(random.randrange(sys.maxint),
                'x').rjust(16, 'f'))))
        self.marscluster.igroup.create(name=initiatorGroupName, ostype='vmware',
            initiators=','.join(fictiveWWPNs))
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        self.assertTrue(len(initiatorGroups[0]['initiators']) == 2)
        LOG.info('Initiator group created:\n', initiatorGroups[0])

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = ChangeInitiatorsWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroupName)
        LOG.info('Wizard open.')

        LOG.step('Verifying defaults')
        self.assertTrue(wizard.activePage.lblTitle.isVisible())
        LOG.info('Title is visible:', wizard.activePage.lblTitle.getText())
        self.assertTrue(wizard.activePage.lblSubtitle.getText() == initiatorGroupName)
        LOG.info('Initiator group name is visible:', wizard.activePage.lblSubtitle.getText())

        LOG.step('Verifying WWPNs assigned to initiator group')
        selectedWWPNs = wizard.activePage.gridInitiatorWWPNs.find(selected=True)
        self.assertTrue(len(selectedWWPNs) == 2)
        for wwpn in selectedWWPNs:
            self.assertTrue(wwpn['initiator_group'] in fictiveWWPNs)
            LOG.info("WWPN assigned to initiator group '%s': %s" % (wwpn['initiator_group'],
                initiatorGroupName))

    def test_add_wwpns(self):
        """
            Verify adding new WWPNs and assigning them to initiator group.
        """
        initiatorGroupName = 'IG-1'
        newWWPNsNumber = 3

        LOG.step('Creating initiator group without WWPNs')
        self.marscluster.igroup.create(name=initiatorGroupName, ostype='vmware')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        self.assertFalse(initiatorGroups[0]['initiators'])
        LOG.info('Initiator group created:\n', initiatorGroups[0])

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = ChangeInitiatorsWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroupName)
        LOG.info('Wizard open.')

        fictiveWWPNs = []
        for _ in range(newWWPNsNumber):
            fictiveWWPNs.append(':'.join(re.findall('..', format(random.randrange(sys.maxint),
                'x').rjust(16, 'f'))))
        LOG.step('Adding new WWPNs to list: %s' % fictiveWWPNs)
        wizard.activePage.addWWPNs(wwpns=fictiveWWPNs)
        selectedWWPNs = [wwpn for wwpn in wizard.activePage.getWWPNs() if wwpn['selected']]
        self.assertTrue(len(selectedWWPNs) == newWWPNsNumber)
        for wwpn in selectedWWPNs:
            self.assertTrue(wwpn['initiator_group'] in fictiveWWPNs)
            LOG.info('WWPN added and selected in list:', wwpn['initiator_group'])

        LOG.step('Verifying WWPNs have been assigned to initiator group')
        initiatorGroup = self.marscluster.igroup.show(json=True)[0]
        for wwpn in fictiveWWPNs:
            self.assertTrue(wwpn in initiatorGroup['initiators'])
        for wwpn in initiatorGroup['initiators']:
            self.assertTrue(wwpn in fictiveWWPNs)
            LOG.info("WWPN '%s' has beed assigned to initiator group." % wwpn)

    def test_reassign_wwpns(self):
        """
            Verify changing initiator WWPNs in dialog.
        """
        initiatorGroupName = 'IG-1'
        newWWPNsNumber = 7

        LOG.step('Generating fictive WWPNs')
        fictiveWWPNs = []
        for _ in range(newWWPNsNumber):
            fictiveWWPNs.append(':'.join(re.findall('..', format(random.randrange(sys.maxint),
                'x').rjust(16, 'f'))))
        LOG.info('Fictive WWPNs generated:', fictiveWWPNs)

        LOG.step('Creating initiator group with half of WWPNs assigned')
        # Assign half of WWPNs
        wwpns = ','.join(fictiveWWPNs[:newWWPNsNumber / 2])
        self.marscluster.igroup.create(name=initiatorGroupName, ostype='vmware', initiators=wwpns)
        initiatorGroup = self.marscluster.igroup.show(json=True)[0]
        LOG.info('Initiator group created:\n', initiatorGroup)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = ChangeInitiatorsWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroupName)
        LOG.info('Wizard open.')

        LOG.step('Verifying assigned WWPNs are shown and selected in grid')
        selectedWWPNs = [wwpn['initiator_group'] for wwpn in wizard.activePage.getWWPNs() if
            wwpn['selected']]
        for wwpn in fictiveWWPNs[:newWWPNsNumber / 2]:
            self.assertTrue(wwpn in selectedWWPNs)
            LOG.info("WWPN '%s' shown selected in grid." % wwpn)

        LOG.step('Reassigning of another half of WWPNs to initiator group')
        wizard.activePage.addWWPNs(wwpns=fictiveWWPNs[newWWPNsNumber / 2:])
        wizard.activePage.setWWPNs(wwpns=fictiveWWPNs[newWWPNsNumber / 2:])
        selectedWWPNs = [wwpn['initiator_group'] for wwpn in wizard.activePage.getWWPNs() if
            wwpn['selected']]
        for wwpn in fictiveWWPNs[newWWPNsNumber / 2:]:
            self.assertTrue(wwpn in selectedWWPNs)
            LOG.info("WWPN '%s' shown selected in grid." % wwpn)

        LOG.step('Submitting dialog')
        wizard.close()
        LOG.info('Dialog submitted.')

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Verifying WWPN reassignment has been done.')
        initiatorGroup = self.marscluster.igroup.show(json=True)[0]
        for wwpn in fictiveWWPNs[newWWPNsNumber / 2:]:
            self.assertTrue(wwpn in initiatorGroup['initiators'])
        for wwpn in initiatorGroup['initiators']:
            self.assertTrue(wwpn in selectedWWPNs)
            LOG.info("WWPN '%s' has been assigned to initiator group." % wwpn)

    def test_dialog_not_available(self):
        """
            Verify menu 'Edit' on Initiator Groups page is disabled when no initiator group
              selected.
        """
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        self._createInitiatorGroups(prefix= initiatorGroupPrefix, number=initiatorGroupNumber)

        LOG.step('Navigating to Initiator Groups page')
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabInitiatorGroups.click()
        self.assertTrue(self.initiatorGroupsPage.isOpen())
        LOG.info('Initiator Groups page is open:', self.initiatorGroupsPage.isOpen())

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Unselecting all initiator groups in grid')
        self.initiatorGroupsPage.gridInitiatorGroups.unselect()
        initiatorGroups = self.initiatorGroupsPage.gridInitiatorGroups.find(selected=True)
        self.assertFalse(initiatorGroups)
        LOG.info('Selected initiator groups:', initiatorGroups)

        LOG.step("Verifying menu 'Edit' is disabled")
        self.assertFalse(self.initiatorGroupsPage.menuEdit.isEnabled())
        LOG.info("Menu 'Edit' is enabled:", self.initiatorGroupsPage.menuEdit.isEnabled())

    def testTeardown(self):
        self.driver.close()

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.marscluster.igroup.destroyAll()
        LOG.info('LUNs & initiator groups destroyed.')

    def _createInitiatorGroups(self, prefix, number):
        LOG.step('Creating initiator group(s)')
        for groupNumber in range(number):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=prefix + '-' + str(groupNumber), ostype='vmware',
                initiators=fictiveWWPN)
        groupNames = [group['name'] for group in self.marscluster.igroup.show(json=True)]
        LOG.info('Initiator group(s) created:', groupNames)
        return groupNames


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testChangeInitiatorsWizard = TestChangeInitiatorsWizard()
    sys.exit(testChangeInitiatorsWizard.numberOfFailedTests())
