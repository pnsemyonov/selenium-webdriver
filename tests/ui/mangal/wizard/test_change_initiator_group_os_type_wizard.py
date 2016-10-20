#!/usr/bin/env python

purpose = """Mangal UI Initiator Groups Page: Functional testing of 'Change Initiator Group OS Type' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import time
import random
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from mangal.wizard.change_initiator_group_os_type_wizard import *
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


class TestChangeInitiatorGroupOSTypeWizard(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.locale = ARGS.values.locale
        self.webUIHostName = getFQDN(self.marscluster.getMasterNode().hostname)

    def testSetup(self):
        self.driver = self.getDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)

        LOG.info('Destroying existing LUNs...')
        self.marscluster.lun.unmapAll()
        self.marscluster.lun.destroyAll()
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

    def test_change_os_type(self):
        """
            Verify changing of OS type for initiator group.
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        osTypes = ['Windows', 'Linux', 'VMware', 'Xen']

        initiatorGroups = self._createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount)
        initiatorGroupName = initiatorGroups[0]

        LOG.step('Changing OS type of initiator group in dialog')
        wizard = ChangeInitiatorGroupOSTypeWizard(driver=self.driver)
        for osType in osTypes:
            LOG.step('Opening dialog')
            wizard.open(initiator_groups=initiatorGroupName)
            LOG.info('Dialog open for initiator group:', initiatorGroupName)

            LOG.step('Setting OS type: %s' % osType)
            wizard.activePage.setOSType(osType=osType)
            wizard.submit()
            LOG.info('OS type set and dialog submitted')

            LOG.step('Verifying OS type has been changed')
            initiatorGroup = [initiatorGroup for initiatorGroup in
                self.marscluster.igroup.show(json=True) if initiatorGroup['name'] ==
                initiatorGroupName][0]
            self.assertTrue(initiatorGroup['ostype'] == osType.lower())
            LOG.info('OS type has been changed to:', initiatorGroup['ostype'])

    def test_change_os_type_related_groups(self):
        """
            Verify dialog window 'Change related initiator groups' pops up when user change OS type
              for one of related (having same WWPN and OS type) initiator groups.
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG_'
        originalOSType = 'Windows'
        newOSType = 'Xen'

        LOG.step('Creating multiple related initiator groups')
        wwpn = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
        for count in range(initiatorGroupCount):
            self.marscluster.igroup.create(name=initiatorGroupPrefix + str(count),
                ostype=originalOSType, initiators=wwpn)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupCount)
        initiatorGroupName = initiatorGroups[0]['name']
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Opening dialog')
        wizard = ChangeInitiatorGroupOSTypeWizard(driver=self.driver)
        wizard.open(initiator_groups=initiatorGroupName)
        LOG.info('Dialog open for initiator group:', initiatorGroupName)

        LOG.step('Setting initiator group OS type to: %s' % newOSType)
        wizard.activePage.setOSType(osType=newOSType)
        wizard.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying related groups are listed on confirmation page')
        wizard.changeRelatedInitiatorGroupsPage.waitUntilOpen()
        listedGroupsNames = wizard.activePage.lblInitiatorGroups.getText()
        relatedGroupsNames = [groupName['name'] for groupName in initiatorGroups[1:]]
        for groupName in relatedGroupsNames:
            self.assertTrue(groupName in listedGroupsNames)
            LOG.info('Initiator group listed on page:', groupName)

        LOG.step('Submitting changes of related initiator groups')
        wizard.activePage.submit()
        LOG.info('Dialog closed.')

        LOG.step('Verifying related initiator groups have been changed')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        for initiatorGroup in initiatorGroups:
            self.assertTrue(initiatorGroup['ostype'] == newOSType.lower())
            LOG.info("Initiator group '%s' has OS type: %s" % (initiatorGroup['name'],
                initiatorGroup['ostype']))

    def test_change_os_type_multiple_groups(self):
        """
            Verify OS type change for multiple initiator groups.
        """
        initiatorGroupCount = 10
        initiatorGroupPrefix = 'IG_'
        originalOSType = 'Windows'
        newOSType = 'Xen'

        LOG.step('Creating multiple related initiator groups')
        for count in range(initiatorGroupCount):
            wwpn = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=initiatorGroupPrefix + str(count),
                ostype=originalOSType, initiators=wwpn)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupCount)
        initiatorGroupName = initiatorGroups[0]['name']
        LOG.info('Initiator groups created:\n', initiatorGroups)

        selectedGroupNames = [initiatorGroup['name'] for initiatorGroup in
            initiatorGroups[:initiatorGroupCount / 2]]
        LOG.step('Opening dialog')
        wizard = ChangeInitiatorGroupOSTypeWizard(driver=self.driver)
        wizard.open(initiator_groups=selectedGroupNames)
        LOG.info('Dialog open for initiator groups:', selectedGroupNames)

        LOG.step('Setting initiator group OS type to: %s' % newOSType)
        wizard.activePage.setOSType(osType=newOSType)
        wizard.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying OS type has been changed for selected initiator groups only')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        for initiatorGroup in initiatorGroups:
            if initiatorGroup['name'] in selectedGroupNames:
                self.assertTrue(initiatorGroup['ostype'] == newOSType.lower())
            else:
                self.assertTrue(initiatorGroup['ostype'] == originalOSType.lower())
            LOG.info("Initiator group '%s' has OS type: %s" % (initiatorGroup['name'],
                initiatorGroup['ostype']))

    def test_change_os_type_multiple_related_groups(self):
        """
            Verify OS type change for multiple related initiator groups.
        """
        initiatorGroupCount = 10
        initiatorGroupPrefix = 'IG_'
        originalOSType = 'Windows'
        newOSType = 'Xen'

        LOG.step('Creating multiple related initiator groups')
        wwpn = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
        for count in range(initiatorGroupCount):
            self.marscluster.igroup.create(name=initiatorGroupPrefix + str(count),
                ostype=originalOSType, initiators=wwpn)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupCount)
        initiatorGroupName = initiatorGroups[0]['name']
        LOG.info('Initiator groups created:\n', initiatorGroups)

        selectedGroupNames = [initiatorGroup['name'] for initiatorGroup in
            initiatorGroups[:initiatorGroupCount / 2]]
        LOG.step('Opening dialog')
        wizard = ChangeInitiatorGroupOSTypeWizard(driver=self.driver)
        wizard.open(initiator_groups=selectedGroupNames)
        LOG.info('Dialog open for initiator groups:', selectedGroupNames)

        LOG.step('Setting initiator group OS type to: %s' % newOSType)
        wizard.activePage.setOSType(osType=newOSType)
        wizard.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying related groups are listed on confirmation page')
        wizard.changeRelatedInitiatorGroupsPage.waitUntilOpen()
        listedGroupsNames = wizard.activePage.lblInitiatorGroups.getText()
        relatedGroupsNames = [groupName['name'] for groupName in initiatorGroups[initiatorGroupCount
            / 2:]]
        for groupName in relatedGroupsNames:
            self.assertTrue(groupName in listedGroupsNames)
            LOG.info('Initiator group listed on page:', groupName)

        LOG.step('Submitting changes of related initiator groups')
        wizard.activePage.submit()
        LOG.info('Dialog closed.')

        LOG.step('Verifying OS type has been changed for all related initiator groups')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        for initiatorGroup in initiatorGroups:
            self.assertTrue(initiatorGroup['ostype'] == newOSType.lower())
            LOG.info("Initiator group '%s' has OS type: %s" % (initiatorGroup['name'],
                initiatorGroup['ostype']))

    def test_dialog_cancel(self):
        """
            Verify OS type of initiator group remains intact on dialog cancel.
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        originalOStype = 'Windows'
        newOSType = 'Xen'

        LOG.step('Creating initiator groups')
        initiatorGroups = self._createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount, osType=originalOStype)
        LOG.info('Initiator groups created:', initiatorGroups)

        LOG.step('Opening dialog')
        wizard = ChangeInitiatorGroupOSTypeWizard(driver=self.driver)
        wizard.open(initiator_groups=initiatorGroups[0])
        LOG.info('Dialog open for initiator group:', initiatorGroups[0])

        LOG.step('Setting initiator group OS type to: %s' % newOSType)
        wizard.activePage.setOSType(osType=newOSType)
        self.assertTrue(wizard.activePage.dLstOSType.getText() == newOSType)
        LOG.info('OS type set to:', wizard.activePage.dLstOSType.getText())

        LOG.step('Canceling dialog without submission')
        wizard.cancel()
        LOG.info('Dialog closed.')

        LOG.step('Verifying initiator group OS type remains original')
        initiatorGroup = [group for group in self.marscluster.igroup.show(json=True) if
            group['name'] == initiatorGroups[0]][0]
        self.assertTrue(initiatorGroup['ostype'] == originalOStype.lower())
        LOG.info('Initiator froup OS type has not been changed:', initiatorGroup['ostype'])

    def _createInitiatorGroups(self, prefix, number, osType='vmware'):
        LOG.step('Creating initiator group(s)')
        for groupNumber in range(number):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=prefix + '-' + str(groupNumber),
                ostype=osType.lower(), initiators=fictiveWWPN)
        groupNames = [group['name'] for group in self.marscluster.igroup.show(json=True)]
        LOG.info('Initiator group(s) created:', groupNames)
        return groupNames

    def testTeardown(self):
        self.driver.close()
        LOG.info('Driver closed.')

    def suiteTeardown(self):
        LOG.step('Quitting browser')
        self.driver.quit()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.marscluster.igroup.destroyAll()
        LOG.info('LUNs & initiator groups destroyed.')

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testChangeInitiatorGroupOSTypeWizard = TestChangeInitiatorGroupOSTypeWizard()
    sys.exit(testChangeInitiatorGroupOSTypeWizard.numberOfFailedTests())
