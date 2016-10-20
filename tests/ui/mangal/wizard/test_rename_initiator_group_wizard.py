#!/usr/bin/env python

purpose = """Mangal UI Initiator Groups Page: Functional testing of 'Rename Initiator Group' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import random
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from mangal.wizard.rename_initiator_group_wizard import *
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


class TestRenameInitiatorWizard(FRTestCase):
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

        LOG.info('Navigating to Initiator Groups page...')
        self.headerPage.btnManager.click()
        self.allStoragePage.tabInitiatorGroups.click()
        self.initiatorGroupsPage.waitUntilOpen()
        LOG.info('Browser landed on Initiator Groups page.')

    def test_valid_name(self):
        """
            Verify initiator group renaming with new valid name.
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        newName = 'IG-New'
        initiatorGroups = self.createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Renaming initiator group in dialog')
        wizard = RenameInitiatorGroupWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Old name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.renameInitiatorGroup(name=newName)
        LOG.info('New name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.submit()
        LOG.info('Rename submitted.')

        LOG.step('Verifying initiator group name has been changed')
        initiatorGroups = [group['name'] for group in self.marscluster.igroup.show(json=True)]
        self.assertTrue(newName in initiatorGroups)
        LOG.info("Name '%s' found in initiator groups list:\n%s" % (newName, initiatorGroups))

    def test_invalid_name(self):
        """
            Verify error message when invalid name typed in.
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        newName = 'IG*&#@1A_^?,'
        initiatorGroups = self.createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step("Changing initiator group name with: %s" % newName)
        wizard = RenameInitiatorGroupWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Old name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.renameInitiatorGroup(name=newName)
        LOG.info('New name:', wizard.activePage.txtName.getText())

        LOG.step('Verifying name error message')
        wizard.activePage.lblNameError.waitUntilPresent()
        LOG.info('Name error message:', wizard.activePage.lblNameError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_max_length_name(self):
        """
            Verify error message when name length exceeds limit (96).
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        newName = 'IGx' * 32
        initiatorGroups = self.createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step("Setting initiator group name to maximal length: %s" % newName)
        wizard = RenameInitiatorGroupWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Old name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.renameInitiatorGroup(name=newName)
        LOG.info('New name:', wizard.activePage.txtName.getText())

        LOG.step('Verifying no error messaging')
        wizard.activePage.lblNameError.waitUntilHidden()
        LOG.info('Error message is present:', wizard.activePage.lblNameError.isVisible())
        self.assertTrue(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Setting initiator group name to maximal + 1 length: %s' % (newName + 'Y'))
        wizard.renameInitiatorGroupPage.renameInitiatorGroup(name=newName + 'Y')
        LOG.info('New name:', wizard.activePage.txtName.getText())

        LOG.step('Verifying name error message')
        wizard.activePage.lblNameError.waitUntilVisible()
        LOG.info('Name error message:', wizard.activePage.lblNameError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_unicode_name(self):
        """
            Verify error message on setting initiator group name to contain Unicode characters.
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        newName = u'Fran\u00e7ais'
        initiatorGroups = self.createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step("Changing initiator group name with: %s" % newName)
        wizard = RenameInitiatorGroupWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Old name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.renameInitiatorGroup(name=newName)
        LOG.info('New name:', wizard.activePage.txtName.getText())

        LOG.step('Verifying name error message')
        wizard.activePage.lblNameError.waitUntilPresent()
        LOG.info('Name error message:', wizard.activePage.lblNameError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_rename_mapped(self):
        """
            Verify rename of initiator group which is mapped to LUN.
        """
        lunName = 'LuN'
        lunSize = '1g'
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        newName = 'IG-New'

        LOG.step('Creating and mapping LUN')
        self.luns.create(count=1, size=lunSize, prefix=lunName)
        initiatorGroup = self.createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount)[0]
        self.marscluster.lun.map({'name': lunName + '_1', 'igroup': initiatorGroup})
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        self.assertTrue(len(luns[0]['maps']) == 1)
        self.assertTrue(luns[0]['maps'][0]['igroup-name'] == initiatorGroup)
        LOG.info("LUN '%s' mapped: %s" % (luns[0]['name'], luns[0]['maps']))

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Renaming initiator group in dialog')
        wizard = RenameInitiatorGroupWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroup)
        LOG.info('Old name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.renameInitiatorGroup(name=newName)
        LOG.info('New name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.submit()
        LOG.info('Rename submitted.')

        LOG.step('Verifying initiator group name has been changed')
        initiatorGroups = [group['name'] for group in self.marscluster.igroup.show(json=True)]
        self.assertTrue(newName in initiatorGroups)
        LOG.info("Name '%s' found in initiator groups list:\n%s" % (newName, initiatorGroups))

    def test_dialog_cancel(self):
        """
            Verify initiator group name remains intact on dialog cancel.
        """
        initiatorGroupCount = 3
        initiatorGroupPrefix = 'IG'
        newName = 'IG-New'
        initiatorGroups = self.createInitiatorGroups(prefix=initiatorGroupPrefix,
            number=initiatorGroupCount)

        self.initiatorGroupsPage.btnRefresh.click()
        self.initiatorGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Renaming initiator group in dialog')
        wizard = RenameInitiatorGroupWizard(driver=self.driver)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Old name:', wizard.activePage.txtName.getText())
        wizard.renameInitiatorGroupPage.renameInitiatorGroup(name=newName)
        LOG.info('New name:', wizard.activePage.txtName.getText())

        LOG.step('Canceling dialog without submission')
        wizard.cancel()

        LOG.step('Verifying initiator group name has not been changed')
        initiatorGroups = [group['name'] for group in self.marscluster.igroup.show(json=True)]
        self.assertTrue(newName not in initiatorGroups)
        LOG.info("Name '%s' is not found in initiator groups list:\n%s" % (newName,
            initiatorGroups))

    def createInitiatorGroups(self, prefix, number):
        LOG.step('Creating initiator group(s)')
        for groupNumber in range(number):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=prefix + '-' + str(groupNumber), ostype='vmware',
                initiators=fictiveWWPN)
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
    testRenameInitiatorWizard = TestRenameInitiatorWizard()
    sys.exit(testRenameInitiatorWizard.numberOfFailedTests())
