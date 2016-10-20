#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Create Consistency Group' wizard"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.consistency_groups_page import ConsistencyGroupsPage
from mangal.wizard.create_consistency_group_wizard import *
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


class TestCreateConsistencyGroupWizard(FRTestCase):
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
        self.consistencyGroupsPage = ConsistencyGroupsPage(driver=self.driver)

        LOG.step('Cleaning out cluster content')
        LOG.info('Destroying LUNs...')
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        self.assertFalse(self.marscluster.lun.show(json=True))
        LOG.info('Done.')
        LOG.info('Deleting consistency groups...')
        while True:
            consistencyGroups = self.marscluster.cg.show(json=True)
            if consistencyGroups:
                self.marscluster.cg.delete(name=consistencyGroups[0]['name'])
            else:
                break
        self.assertFalse(self.marscluster.cg.show(json=True))
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

        LOG.info('Navigating to Consistency Groups page...')
        self.headerPage.btnManager.click()
        self.allStoragePage.tabConsistencyGroups.click()
        self.consistencyGroupsPage.waitUntilOpen()
        LOG.info('Browser landed on Consistency Groups page.')

    def test_create_minimal(self):
        """
            Verify new consistency group creation when only name specified.
        """
        consistencyGroupName = 'cg1'

        LOG.step('Opening wizard')
        wizard = CreateConsistencyGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Verifying default parameters')
        self.assertFalse(wizard.activePage.txtName.getText())
        LOG.info("Default name: %s" % wizard.activePage.txtName.getText())
        candidates = wizard.activePage.gridCandidates.find()
        self.assertFalse(candidates)
        LOG.info('Candidates:', candidates)

        LOG.step('Setting consistency group name')
        wizard.activePage.setName(name=consistencyGroupName)
        name = wizard.activePage.txtName.getText()
        self.assertTrue(name == consistencyGroupName)
        LOG.info('Consistency group name set:', name)

        LOG.step('Submitting dialog')
        wizard.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying consistency group has been created')
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == consistencyGroupName)
        self.assertFalse(consistencyGroups[0]['members'])
        LOG.info('Consistency group created:', consistencyGroups[0]['name'])

    def test_create_mapped_lun(self):
        """
            Verify new consistency group creation with mapped LUNs.
        """
        lunNamePrefix = 'lun'
        lunCount = 5
        consistencyGroupName = 'cg1'

        LOG.step('Creating LUNs')
        for count in range(lunCount):
            self.marscluster.lun.create(name=lunNamePrefix + str(count), size='1g')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == lunCount)
        LOG.info('LUNs created:', [lun['name'] for lun in luns])

        LOG.step('Opening wizard')
        wizard = CreateConsistencyGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Verifying LUNs are present as candidates')
        candidates = [candidate['candidates'] for candidate in
            wizard.activePage.getCandidates()]
        self.assertTrue(len(candidates) == lunCount)
        for lun in luns:
            self.assertTrue(lun['name'] in candidates)
        LOG.info('Candidates:', candidates)

        LOG.step('Setting consistency group name')
        wizard.activePage.setName(name=consistencyGroupName)
        name = wizard.activePage.txtName.getText()
        self.assertTrue(name == consistencyGroupName)
        LOG.info('Consistency group name set:', name)

        LOG.step('Setting LUN as candidate to map')
        wizard.activePage.setCandidates(candidates=lunNamePrefix + '0')
        setCandidates = wizard.activePage.gridCandidates.find(selected=True)
        self.assertTrue(len(setCandidates) == 1)
        self.assertTrue(setCandidates[0]['candidates'] == lunNamePrefix + '0')
        LOG.info('Candidate set:', setCandidates[0]['candidates'])

        LOG.step('Submitting dialog')
        wizard.submit()
        LOG.info('Dialog submitted.')

        LOG.step('Verifying consistency group has been created')
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == consistencyGroupName)
        self.assertTrue(len(consistencyGroups[0]['members']) == 1)
        self.assertTrue(consistencyGroups[0]['members'][0]['name'] == consistencyGroupName + '/' +
            lunNamePrefix + '0')
        LOG.info('Consistency group has been created and mapped:', consistencyGroups[0])

    def test_create_nested_cg(self):
        """
            Verify new consistency group creation with under another consistency group.
        """
        parentName = 'cgPr'
        childName = 'cgCh'

        LOG.step('Creating child consistency group')
        self.marscluster.cg.create(name=childName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == childName)
        LOG.info('Child consistency group created:', consistencyGroups[0])

        self.consistencyGroupsPage.btnRefresh.click()
        self.consistencyGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening dialog with no consistency groups selected')
        self.consistencyGroupsPage.gridConsistencyGroups.unselect()
        self.assertFalse(self.consistencyGroupsPage.gridConsistencyGroups.find(selected=True))
        wizard = CreateConsistencyGroupWizard(driver=self.driver)
        wizard.open()
        self.assertFalse(wizard.activePage.lblSubtitle.isVisible())
        LOG.info('Wizard open.')

        LOG.step('Creating parent consistency group: %s' % parentName)
        wizard.activePage.setName(name=parentName)
        wizard.activePage.setCandidates(candidates=childName + '/')
        wizard.submit()
        LOG.info('Dialog closed.')

        LOG.step('Verifying child consistency group has been added to parent one')
        consistencyGroups = self.marscluster.cg.show(json=True)
        parentConsistencyGroup = [consistencyGroup for consistencyGroup in consistencyGroups if
            consistencyGroup['name'] == parentName][0]
        self.assertTrue(len(parentConsistencyGroup['members']) == 1)
        self.assertTrue(parentConsistencyGroup['members'][0]['name'] == parentName + '/' +
            childName)
        LOG.info('Parent consistency group has been created:', parentConsistencyGroup)

    def test_create_nested_cg_selected(self):
        """
            Verify new consistency group creation under another consistency group selected in grid.
        """
        parentName = 'cgPr'
        childName = 'cgCh'

        LOG.step('Creating parent consistency group')
        self.marscluster.cg.create(name=parentName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentName)
        LOG.info('Parent consistency group created:', consistencyGroups[0])

        self.consistencyGroupsPage.btnRefresh.click()
        self.consistencyGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Opening dialog with parent consistency groups selected')
        wizard = CreateConsistencyGroupWizard(driver=self.driver)
        wizard.open(parentConsistencyGroup=parentName)
        self.assertTrue(wizard.activePage.lblSubtitle.getText() == parentName)
        LOG.info('Wizard open.')

        LOG.step('Creating child consistency group: %s' % childName)
        wizard.activePage.setName(name=childName)
        wizard.submit()
        LOG.info('Dialog closed.')

        LOG.step('Verifying child consistency group has been added to parent one')
        consistencyGroups = self.marscluster.cg.show(json=True)
        parentConsistencyGroup = [consistencyGroup for consistencyGroup in consistencyGroups if
            consistencyGroup['name'] == parentName][0]
        self.assertTrue(len(parentConsistencyGroup['members']) == 1)
        self.assertTrue(parentConsistencyGroup['members'][0]['name'] == parentName + '/' +
            childName)
        LOG.info('Parent consistency group has been created:', parentConsistencyGroup)

    def test_dialog_cancel(self):
        """
            Verify closing dialog without submission has no effect.
        """
        consistencyGroupName = 'cg1'

        LOG.step('Opening dialog')
        wizard = CreateConsistencyGroupWizard(driver=self.driver)
        wizard.open()
        LOG.info('Wizard open.')

        LOG.step('Setting name for new consistency group')
        wizard.activePage.setName(name=consistencyGroupName)
        self.assertTrue(wizard.activePage.txtName.getText() == consistencyGroupName)
        LOG.info('Consistency group name set:', wizard.activePage.txtName.getText())

        LOG.step('Canceling dialog without submission')
        wizard.cancel()
        LOG.info('Dialog cancelled.')

        LOG.step('Verifying no consistency group has been created')
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertFalse(consistencyGroups)
        LOG.info('Consistency groups:', consistencyGroups)

    def test_dialog_not_available(self):
        """
            Verify dialog is not available when 2 or more consistency groups selected in grid.
        """
        namePrefix = 'cg'
        consistencyGroupsNumber = 5

        LOG.step('Creating multiple consistency groups')
        for count in range(consistencyGroupsNumber):
            self.marscluster.cg.create(name=namePrefix + str(count))
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == consistencyGroupsNumber)
        LOG.info('Consistency groups created:', [consistencyGroup['name'] for consistencyGroup in
            consistencyGroups])

        self.consistencyGroupsPage.btnRefresh.click()
        self.consistencyGroupsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Selecting multiple consistency groups in grid')
        self.consistencyGroupsPage.gridConsistencyGroups.select(name=[namePrefix + '0', namePrefix +
            '3'])
        selectedConsistencyGroups = \
            self.consistencyGroupsPage.gridConsistencyGroups.find(selected=True)
        self.assertTrue(len(selectedConsistencyGroups) == 2)
        LOG.info('Consistency groups selected in grid:', [consistencyGroup['name'] for
            consistencyGroup in selectedConsistencyGroups])

        LOG.step('Verifying dialog is not available for given selection')
        self.assertFalse(self.consistencyGroupsPage.menuCreate.isItemEnabled(item='Consistency group'))
        LOG.info('Dialog is available:',
            self.consistencyGroupsPage.menuCreate.isItemEnabled(item='Consistency group'))

    def testTeardown(self):
        self.driver.close()

    def suiteTeardown(self):
        LOG.step('Closing browser')
        self.driver.quit()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        consistencyGroups = self.marscluster.cg.show(json=True)
        for consistencyGroup in consistencyGroups:
            self.marscluster.cg.delete(name=consistencyGroup['name'])
        self.assertFalse(self.marscluster.cg.show(json=True))


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testCreateConsistencyGroupWizard = TestCreateConsistencyGroupWizard()
    sys.exit(testCreateConsistencyGroupWizard.numberOfFailedTests())
