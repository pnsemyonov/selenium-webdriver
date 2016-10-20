#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Edit IDs' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import express
import random
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.edit_lun_ids_wizard import *

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


class TestEditLUNIDsWizard(FRTestCase):
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

        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.luns = express.Luns(node=self.marscluster)
        self.marscluster.igroup.destroyAll()

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

    def test_single_mapping(self):
        """
            Verify setting ID for LUN with single initiator group mapping.
        """
        newID = 173

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix='LuN')
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        groupNames = self.createInitiatorGroups(prefix='IG', number=1)

        LOG.step('Mapping LUN to initiator group')
        self.marscluster.lun.map({'name': 'LuN_1', 'igroup': groupNames[0]})
        LOG.info('LUN mapped:\n', self.marscluster.lun.mapping_show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNIDsWizard(driver=self.driver)
        wizard.open(name='LuN_1')
        LOG.info('Wizard open.')

        LOG.step('Verifying default ID')
        ids = wizard.activePage.getIDs()
        self.assertTrue(len(ids) == 1)
        self.assertTrue(ids['IG-0'] == '0')
        LOG.info('Default ID set:', ids['IG-0'])

        LOG.step('Setting new ID: %s' % newID)
        wizard.activePage.setIDs(ids={'IG-0': newID})
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying new ID')
        lun = self.marscluster.lun.show(json=True)[0]
        self.assertTrue(lun['maps'][0]['lun-id'] == newID)
        LOG.info('LUN mapping ID set to:', lun['maps'][0]['lun-id'])

    def test_multiple_mappings(self):
        """
            Verify setting IDs for LUN with multiple initiator group mappings.
        """
        initiatorGroupsNumber = 5
        maxID = 4095

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix='LuN')
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        # List of initiator group names with default IDs
        ids = {groupName: 0 for groupName in self.createInitiatorGroups(prefix='IG',
            number=initiatorGroupsNumber)}

        LOG.step('Mapping LUN to initiator groups')
        for groupName in ids:
            self.marscluster.lun.map({'name': 'LuN_1', 'igroup': groupName})
        LOG.info('LUN mapped:\n', self.marscluster.lun.mapping_show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNIDsWizard(driver=self.driver)
        wizard.open(name='LuN_1')
        LOG.info('Wizard open.')

        LOG.step('Setting random IDs')
        uniqueIDs = []
        for groupName in ids:
            # To avoid duplicated IDs.
            while True:
                id = random.randint(0, maxID)
                if id not in uniqueIDs:
                    uniqueIDs.append(id)
                    ids[groupName] = id
                    LOG.info("Initiator group '%s': ID set to %s" % (groupName, id))
                    break
        wizard.activePage.setIDs(ids=ids)
        wizard.activePage.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying LUN mapping IDs')
        mappings = self.marscluster.lun.show(json=True)[0]['maps']
        self.assertTrue(len(mappings) == len(ids))
        for mapping in mappings:
            self.assertTrue(mapping['lun-name'] == 'LuN_1')
            self.assertTrue(mapping['lun-id'] == ids[mapping['igroup-name']])
            LOG.info("Initiator group '%s': ID=%s" % (mapping['igroup-name'],
                ids[mapping['igroup-name']]))

    def test_fail_original_id(self):
        """
            Verify button 'OK' is disabled when original ID was typed in.
        """
        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix='LuN')
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        self.createInitiatorGroups(prefix='IG', number=1)

        LOG.step('Mapping LUN to initiator group')
        self.marscluster.lun.map({'name': 'LuN_1', 'igroup': 'IG-0'})
        LOG.info('LUN mapped:\n', self.marscluster.lun.mapping_show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNIDsWizard(driver=self.driver)
        wizard.open(name='LuN_1')
        LOG.info('Wizard open.')

        LOG.step('Typing in original ID')
        ids = wizard.activePage.getIDs()
        self.assertTrue(len(ids) == 1)
        id = ids['IG-0']
        LOG.info('Original ID:', id)
        wizard.activePage.setIDs(ids={'IG-0': id})
        newID = wizard.activePage.getIDs()['IG-0']
        LOG.info('Typed ID:', newID)
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_fail_invalid_id(self):
        """
            Verify typing invalid ID filters out non-numeric characters.
        """
        validIDPart = '700'
        invalidIDPart = 'W-'

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix='LuN')
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        self.createInitiatorGroups(prefix='IG', number=1)

        LOG.step('Mapping LUN to initiator group')
        self.marscluster.lun.map({'name': 'LuN_1', 'igroup': 'IG-0'})
        LOG.info('LUN mapped:\n', self.marscluster.lun.mapping_show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNIDsWizard(driver=self.driver)
        wizard.open(name='LuN_1')
        LOG.info('Wizard open.')

        LOG.step('Typing in invalid ID: %s' % validIDPart + invalidIDPart)
        wizard.activePage.setIDs(ids={'IG-0': validIDPart + invalidIDPart})
        typedText = wizard.activePage.getIDs()['IG-0']
        self.assertTrue(typedText == validIDPart)
        LOG.info('Typed value:', typedText)

    def test_max_id(self):
        """
            Verify error message appears when ID exceeds upper limit (4095).
        """
        maxID = 4095

        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix='LuN')
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        self.createInitiatorGroups(prefix='IG', number=1)

        LOG.step('Mapping LUN to initiator group')
        self.marscluster.lun.map({'name': 'LuN_1', 'igroup': 'IG-0'})
        LOG.info('LUN mapped:\n', self.marscluster.lun.mapping_show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNIDsWizard(driver=self.driver)
        wizard.open(name='LuN_1')
        LOG.info('Wizard open.')

        LOG.step('Typing in maximal acceptable ID: %s' % maxID)
        wizard.activePage.setIDs(ids={'IG-0': maxID})
        self.assertTrue(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Typing in ID exceeding maximal: %s' % (maxID + 1))
        wizard.activePage.setIDs(ids={'IG-0': maxID + 1})
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_fail_nonunique_id(self):
        """
            Verify error message when typed ID is used by another LUN mapped to the same initiator
              group.
        """
        LOG.step('Creating 2 LUNs')
        self.luns.create(count=2, size='1g', prefix='LuN')
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        self.createInitiatorGroups(prefix='IG', number=1)

        LOG.step('Mapping LUNs to the same initiator group')
        self.marscluster.lun.map({'name': 'LuN_1', 'igroup': 'IG-0'})
        self.marscluster.lun.map({'name': 'LuN_2', 'igroup': 'IG-0'})
        mappings = self.marscluster.lun.mapping_show(json=True)
        LOG.info('LUN mapped:\n', mappings)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNIDsWizard(driver=self.driver)
        wizard.open(name=mappings[0]['lun-name'].encode('utf-8'))
        LOG.info('Wizard open for LUN:', mappings[0]['lun-name'])

        LOG.step('Setting ID same as another LUN')
        wizard.activePage.setIDs(ids={mappings[1]['lun-id']})
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_dialog_cancel(self):
        """
            Verify ID remains unchanged on canceling dialog without submission.
        """
        LOG.step('Creating LUN')
        self.luns.create(count=1, size='1g', prefix='LuN')
        LOG.info('LUN created:\n', self.marscluster.lun.show(json=True))

        self.createInitiatorGroups(prefix='IG', number=1)

        LOG.step('Mapping LUN to initiator group')
        self.marscluster.lun.map({'name': 'LuN_1', 'igroup': 'IG-0'})
        originalMappings = self.marscluster.lun.mapping_show(json=True)
        LOG.info('LUN mapped:\n', originalMappings)

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening wizard')
        wizard = EditLUNIDsWizard(driver=self.driver)
        wizard.open(name='LuN_1')
        LOG.info('Wizard open.')

        newID = '305'
        LOG.step('Setting new ID: %s' % newID)
        wizard.activePage.setIDs(ids={'IG-0': newID})
        ids = wizard.activePage.getIDs()
        self.assertTrue(ids['IG-0'] == newID)
        LOG.info('Typed ID:', ids['IG-0'])

        LOG.step('Canceling dialog without submission')
        wizard.cancel()
        LOG.info('Dialog closed.')

        LOG.step('Verifying mappings have not been changed')
        mappings = self.marscluster.lun.mapping_show(json=True)
        self.assertTrue(len(mappings) == len(originalMappings))
        self.assertTrue(mappings[0]['igroup-name'] == originalMappings[0]['igroup-name'])
        LOG.info('Initiator group:', originalMappings[0]['igroup-name'])
        self.assertTrue(mappings[0]['lun-name'] == originalMappings[0]['lun-name'])
        LOG.info('LUN:', originalMappings[0]['lun-name'])
        self.assertTrue(mappings[0]['lun-id'] == originalMappings[0]['lun-id'])
        LOG.info('LUN ID:', originalMappings[0]['lun-id'])

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

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()
        LOG.info('Browser closed.')
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.marscluster.igroup.destroyAll()


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testEditLUNIDsWizard = TestEditLUNIDsWizard()
    sys.exit(testEditLUNIDsWizard.numberOfFailedTests())
