#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Create an Initiator Group' wizard"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import re
import random
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.create_initiator_group_wizard import *
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


class TestCreateInitiatorGroupWizard(FRTestCase):
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

    def test_create_minimal(self):
        """
            Verify initiator group creation when name specified explicitly, OS Type is as default.
        """
        initiatorGroupName = 'IG-1'
        defaultOSType = 'Windows'

        LOG.step('Opening wizard')
        wizard = CreateInitiatorGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Verifying default parameters')
        self.assertFalse(wizard.activePage.txtName.getText())
        LOG.info("Default name: %s" % wizard.activePage.txtName.getText())
        self.assertTrue(wizard.activePage.dLstOSType.getText() == defaultOSType)
        LOG.info("Default OS Type: %s" % wizard.activePage.dLstOSType.getText())
        selectedWWPNs = wizard.activePage.gridInitiatorWWPNs.find(selected=True)
        self.assertFalse(selectedWWPNs)
        LOG.info('Selected WWPNs:', selectedWWPNs)

        LOG.step('Setting initiator group name')
        wizard.activePage.setName(name=initiatorGroupName)
        name = wizard.activePage.txtName.getText()
        self.assertTrue(name == initiatorGroupName)
        LOG.info('Initiator group name set:', name)

        LOG.step('Submitting dialog')
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying initiator group has been created')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        LOG.info('Initiator group created:', initiatorGroups[0]['name'])

    def test_create_custom_os_type(self):
        """
            Verify initiator group creation when name and OS type specified explicitly.
        """
        initiatorGroupName = 'IG-1'
        osType = 'Xen'

        LOG.step('Opening wizard')
        wizard = CreateInitiatorGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Setting initiator group name')
        wizard.activePage.setName(name=initiatorGroupName)
        name = wizard.activePage.txtName.getText()
        self.assertTrue(name == initiatorGroupName)
        LOG.info('Initiator group name set:', name)

        LOG.step('Setting OS type: %s' % osType)
        wizard.activePage.setOSType(osType=osType)
        setOSType = wizard.activePage.dLstOSType.getText()
        self.assertTrue(setOSType == osType)
        LOG.info('OS type set:', setOSType)

        LOG.step('Submitting dialog')
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying initiator group has been created')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        LOG.info("Initiator group's name:", initiatorGroups[0]['name'])
        self.assertTrue(initiatorGroups[0]['ostype'] == osType.lower())
        LOG.info("Initiator group's OS type:", initiatorGroups[0]['ostype'])

    def test_create_single_initiator(self):
        """
            Verify initiator group creation when name and OS type specified explicitly, and single
              initiator selected.
        """
        initiatorGroupName = 'IG-1'
        osType = 'Xen'

        LOG.step('Opening wizard')
        wizard = CreateInitiatorGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Setting initiator group name')
        wizard.activePage.setName(name=initiatorGroupName)
        name = wizard.activePage.txtName.getText()
        self.assertTrue(name == initiatorGroupName)
        LOG.info('Initiator group name set:', name)

        LOG.step('Setting OS type: %s' % osType)
        wizard.activePage.setOSType(osType=osType)
        setOSType = wizard.activePage.dLstOSType.getText()
        self.assertTrue(setOSType == osType)
        LOG.info('OS type set:', setOSType)

        LOG.step('Setting single initiator')
        wwpns = wizard.activePage.getWWPNs()
        if wwpns:
            wizard.activePage.setWWPNs(wwpns=wwpns[0]['initiator_group'])
            setWWPNs = wizard.activePage.gridInitiatorWWPNs.find(selected=True)

            self.assertTrue(len(setWWPNs) == 1)
            self.assertTrue(setWWPNs[0]['initiator_group'] == wwpns[0]['initiator_group'])
            LOG.info('Initiator WWPN set:', setWWPNs[0]['initiator_group'])

            LOG.step('Submitting dialog')
            wizard.activePage.submit()
            LOG.info('Dialog submitted.')

            LOG.step('Verifying initiator group has been created')
            initiatorGroups = self.marscluster.igroup.show(json=True)
            self.assertTrue(len(initiatorGroups) == 1)
            self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
            LOG.info("Initiator group's name:", initiatorGroups[0]['name'])
            self.assertTrue(initiatorGroups[0]['ostype'] == osType.lower())
            LOG.info("Initiator group's OS type:", initiatorGroups[0]['ostype'])
            self.assertTrue(initiatorGroups[0]['initiators'][0] == wwpns[0]['initiator_group'])
            LOG.info("Initiator group's WWPN:", wwpns[0]['initiator_group'])
        else:
            LOG.info('No initiators found. Test skipped.')

    def test_create_add_single_initiator(self):
        """
            Verify initiator group creation when name and OS type specified explicitly, and single
              initiator added and selected.
        """
        initiatorGroupName = 'IG-1'
        osType = 'Xen'

        LOG.step('Opening wizard')
        wizard = CreateInitiatorGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Setting initiator group name')
        wizard.activePage.setName(name=initiatorGroupName)
        name = wizard.activePage.txtName.getText()
        self.assertTrue(name == initiatorGroupName)
        LOG.info('Initiator group name set:', name)

        LOG.step('Setting OS type: %s' % osType)
        wizard.activePage.setOSType(osType=osType)
        setOSType = wizard.activePage.dLstOSType.getText()
        self.assertTrue(setOSType == osType)
        LOG.info('OS type set:', setOSType)

        fictiveWWPN = ':'.join(re.findall('..', format(random.randrange(sys.maxint), 'x').rjust(16,
            'f')))
        LOG.step('Adding new initiator: %s' % fictiveWWPN)
        wizard.activePage.addWWPNs(wwpns=fictiveWWPN)
        wwpns = wizard.activePage.getWWPNs()
        foundWWPN = [wwpn for wwpn in wwpns if wwpn['initiator_group'] == fictiveWWPN]
        self.assertTrue(foundWWPN)
        LOG.info('Initiator added:', foundWWPN[0]['initiator_group'])

        LOG.step('Setting single initiator: %s' % fictiveWWPN)
        wizard.activePage.setWWPNs(wwpns=fictiveWWPN)
        setWWPNs = wizard.activePage.gridInitiatorWWPNs.find(selected=True)
        self.assertTrue(len(setWWPNs) == 1)
        self.assertTrue(setWWPNs[0]['initiator_group'] == fictiveWWPN)
        LOG.info('Initiator WWPN set:', setWWPNs[0]['initiator_group'])

        LOG.step('Submitting dialog')
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying initiator group has been created')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        LOG.info("Initiator group's name:", initiatorGroups[0]['name'])
        self.assertTrue(initiatorGroups[0]['ostype'] == osType.lower())
        LOG.info("Initiator group's OS type:", initiatorGroups[0]['ostype'])
        self.assertTrue(initiatorGroups[0]['initiators'][0] == fictiveWWPN)
        LOG.info("Initiator group's WWPN:", wwpns[0]['initiator_group'])

    def test_create_multiple_initiators(self):
        """
            Verify initiator group creation when name and OS type specified explicitly, and multiple
              initiators (either existing or fictive).
        """
        initiatorGroupName = 'IG-1'
        osType = 'Xen'
        initiatorsNumber = 10

        LOG.step('Opening wizard')
        wizard = CreateInitiatorGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Setting initiator group name')
        wizard.activePage.setName(name=initiatorGroupName)
        name = wizard.activePage.txtName.getText()
        self.assertTrue(name == initiatorGroupName)
        LOG.info('Initiator group name set:', name)

        LOG.step('Setting OS type: %s' % osType)
        wizard.activePage.setOSType(osType=osType)
        setOSType = wizard.activePage.dLstOSType.getText()
        self.assertTrue(setOSType == osType)
        LOG.info('OS type set:', setOSType)

        wwpns = wizard.activePage.getWWPNs()
        if len(wwpns) < initiatorsNumber:
            LOG.step('Adding fictive initiators')
            fictiveWWPNs = []
            for wwpnNumber in range(len(wwpns), initiatorsNumber):
                wizard.activePage.addWWPNs(wwpns=fictiveWWPNs)
                fictiveWWPNs.append(':'.join(re.findall('..', format(random.randrange(sys.maxint),
                    'x').rjust(16, 'f'))))
            wizard.activePage.addWWPNs(wwpns=fictiveWWPNs)
            wwpns = [wwpn['initiator_group'] for wwpn in wizard.activePage.getWWPNs()]
            for wwpn in fictiveWWPNs:
                self.assertTrue(wwpn in wwpns)
        else:
            wwpns = [wwpn['initiator_group'] for wwpn in wizard.activePage.getWWPNs()]
        LOG.info('Initiators available:', wwpns)

        LOG.step('Setting all initiators')
        wizard.activePage.setWWPNs(wwpns=wwpns)
        setWWPNs = wizard.activePage.gridInitiatorWWPNs.find(selected=True)
        self.assertTrue(len(setWWPNs) == initiatorsNumber)
        LOG.info('Initiator WWPNs set:\n', setWWPNs)

        LOG.step('Submitting dialog')
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying initiator group has been created')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue(initiatorGroups[0]['name'] == initiatorGroupName)
        LOG.info("Initiator group's name:", initiatorGroups[0]['name'])
        self.assertTrue(initiatorGroups[0]['ostype'] == osType.lower())
        LOG.info("Initiator group's OS type:", initiatorGroups[0]['ostype'])
        self.assertTrue(len(initiatorGroups[0]['initiators']) == initiatorsNumber)
        for initiator in initiatorGroups[0]['initiators']:
            self.assertTrue(initiator in wwpns)
            LOG.info("Initiator group's WWPN:", initiator)

    def test_dialog_cancel(self):
        """
            Verify closing dialog without submission has no effect.
        """
        LOG.step('Opening wizard')
        wizard = CreateInitiatorGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Closing dialog without submission')
        wizard.cancel()
        LOG.info('Dialog closed.')

        LOG.step('Verifying no initiator groups were created')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertFalse(initiatorGroups)
        LOG.info('Initiator groups:', initiatorGroups)

    def testTeardown(self):
        self.driver.close()

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.marscluster.igroup.destroyAll()
        LOG.info('LUNs & initiator groups destroyed.')


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testCreateInitiatorGroupWizard = TestCreateInitiatorGroupWizard()
    sys.exit(testCreateInitiatorGroupWizard.numberOfFailedTests())
