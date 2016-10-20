#!/usr/bin/env python

purpose = """Unit test of Create LUNs Wizard"""

import os
import sys
import random
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import time
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.create_luns_wizard import *
from frlog import LOG
from frargs import ARGS
from frutil import getFQDN
from frtestcase import FRTestCase
from frexceptions import *


ARGS.parser.add_argument(
    '--locale', type=str,
    help="Locale: 'en' (English), 'es' (Spanish), 'de' (German), 'fr' (French), 'ja' (Japanese), 'ko' (Korean), 'zh' (Chinese)")

ARGS.parser.add_argument(
    '--username', type=str,
    default='admin',
    help="Administrator's name on Mars controller")

ARGS.parser.add_argument(
    '--password', type=str,
    default='changeme',
    help="Administrator's password on Mars controller")

ARGS.parser.add_argument(
    '--timeout', type=int,
    default=10,
    help="Timeout on interaction with components")


class TestCreateLUNsWizard(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.locale = ARGS.values.locale
        self.timeout = ARGS.values.timeout
        self.webUIHostName = getFQDN(self.marscluster.getMasterNode().hostname)

    def testSetup(self):
        self.driver = self.getDriver()
        self.driver.timeout = self.timeout
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.headerPage = HeaderPage(driver=self.driver)
        self.allStoragePage = AllStoragePage(driver=self.driver)
        self.lunsPage = LUNsPage(driver=self.driver)

        LOG.info('Destroying existing LUNs...')
        self.marscluster.lun.unmapAll()
        self.marscluster.lun.destroyAll()
        self.assertFalse(self.marscluster.lun.show(json=True))
        LOG.info('Done.')
        LOG.info('Destroying existing initiator groups...')
        self.marscluster.igroup.destroyAll()
        LOG.info('Done.')
        LOG.info('Destroying existing consistency groups...')
        self.deleteDependentConsistencyGroups()
        LOG.info('Done.')

        if self.locale is None:
            self.locale = self.loginPage.getRandomLocale()
        self.loginPage.signIn(username=self.username, password=self.password, locale=self.locale)

    def test_single_lun_invalid_name(self):
        """
            Test verifies inability of creation of single LUN with invalid name.
        """
        name = 'LuN:$1001'
        numberOfLUNs = '1'
        size = '3g'

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Front page is open:', wizard.defineLUNsPage.isOpen())

        LOG.step("Calling method: defineSingleLUN(name='%s', size='%s')" % (name, size))
        wizard.activePage.defineSingleLUN(name=name, size=size)

        LOG.step('Verifying error message as name is invalid')
        self.assertTrue(wizard.activePage.lblNameError.isPresent())
        LOG.info('Error message is present:', wizard.activePage.lblNameError.isPresent())
        wizard.activePage.lblNameError.isVisible()
        LOG.info('Error message is visible:', wizard.activePage.lblNameError.isVisible())
        LOG.info('Error message:', wizard.activePage.lblNameError.isPresent())

        LOG.step("Verifying button 'Next' is disabled.")
        self.assertFalse(wizard.activePage.btnNext.isEnabled())
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

    def test_single_lun_max_length_name(self):
        """
            Test verifies creation of single LUNs with maximum length of name (255).
        """
        name = 'LuN__' + ('0' * 250)
        size = '3g'

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Front page is open:', wizard.defineLUNsPage.isOpen())

        LOG.step("Calling method: defineSingleLUN(name='%s', size='%s')" % (name, size))
        wizard.activePage.defineSingleLUN(name=name, size=size)

        LOG.step('Verifying no name error message present on page.')
        self.assertFalse(wizard.activePage.lblNameError.isPresent())
        LOG.info('Name error message is present:', wizard.activePage.lblNameError.isPresent())

        LOG.step('Finishing wizard')
        wizard.goNext()
        wizard.selectInitiatorGroupsPage.waitUntilOpen()
        LOG.info('Proceeded to page', wizard.selectInitiatorGroupsPage.name)
        wizard.goNext()
        wizard.confirmPage.waitUntilOpen()
        LOG.info('Proceeded to page', wizard.confirmPage.name)
        wizard.goNext()
        wizard.closePage.waitUntilOpen()
        LOG.info('Proceeded to page', wizard.closePage.name)
        wizard.closePage.close()
        wizard.closePage.waitUntilClosed()
        LOG.info('Wizard closed.')

        LOG.step('Verifying created LUNs have provided name')
        self.assertTrue(self.marscluster.lun.show(json=True)[0]['name'] == name)
        LOG.info('LUN name:', self.marscluster.lun.show(json=True)[0]['name'])

    def test_single_lun_terminal_size(self):
        """
            Test verifies creation of single LUN with minimum and maximum sizes respecting given size unit.
        """
        sizes = {
            'B': {
                'low': 512,
                'high': long(64) * pow(1024, 4),
                'multiplier': 1
            },
            'K': {
                'low': 0.5,
                'high': long(64) * pow(1024, 3),
                'multiplier': 1024
            },
            'M': {
                'low': 0.001,
                'high': long(64) * pow(1024, 2),
                'multiplier': 1024 ** 2
            },
            'G': {
                'low': 0.001,
                'high': long(64) * 1024,
                'multiplier': 1024 ** 3
            },
            'T': {
                'low': 0.001,
                'high': 64,
                'multiplier': 1024 ** 4
            }
        }
        lunsToCreate = {}

        for sizeUnit in sizes:
            nameLow = 'LuN_' + sizeUnit + '_low'
            sizeLow = str(sizes[sizeUnit]['low']) + sizeUnit
            nameHigh = 'LuN_' + sizeUnit + '_high'
            sizeHigh = str(sizes[sizeUnit]['high']) + sizeUnit

            LOG.step('Creating wizard')
            wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
            wizard.open()
            self.assertTrue(wizard.defineLUNsPage.isOpen())
            LOG.info('Wizard created.')

            LOG.step("Creating LUN with minimal size: name='%s', size='%s')" % (nameLow, sizeLow))
            wizard.activePage.defineSingleLUN(name=nameLow, size=sizeLow)
            wizard.goNext()
            wizard.goNext()
            wizard.goNext()
            wizard.closePage.close()
            LOG.info('Wizard closed.')

            sizeToCreate = sizes[sizeUnit]['low'] * sizes[sizeUnit]['multiplier']
            # Sizes of LUNs are rounded up to 512-byte bound
            if sizeToCreate % 512 > 0:
                sizeToCreate = int(sizeToCreate / 512) * 512 + 512
            lunsToCreate[nameLow] = sizeToCreate

            LOG.step('Creating wizard')
            wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
            wizard.open()
            self.assertTrue(wizard.defineLUNsPage.isOpen())
            LOG.info('Wizard created.')

            LOG.step("Creating LUN with minimal size: name='%s', size='%s')" % (nameHigh, sizeHigh))
            wizard.activePage.defineSingleLUN(name=nameHigh, size=sizeHigh)
            wizard.goNext()
            wizard.goNext()
            wizard.goNext()
            wizard.closePage.close()
            LOG.info('Wizard closed.')

            lunsToCreate[nameHigh] = sizes[sizeUnit]['high'] * sizes[sizeUnit]['multiplier']

            createdLUNs = self.marscluster.lun.show(json=True)
            self.assertTrue(len(createdLUNs) == 2)

            LOG.step('Verifying size of created LUNs is as specified')
            for lun in createdLUNs:
                self.assertTrue(lun['size'] == lunsToCreate[lun['name']])
                LOG.info("Size of LUN '%s' (bytes): %s" % (lun['name'], lun['size']))

            LOG.step('Destroying LUNs')
            self.marscluster.lun.destroyAll()
            self.assertFalse(self.marscluster.lun.show(json=True))
            LOG.info('All LUNs destroyed.')

    def test_single_lun_map_new_parent_cg(self):
        """
            Test verifies creation of single LUN mapped to newly created parent consistency group.
        """
        lunName = 'LuN'
        consistencyGroupName = 'New-CG'

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size='1G')
        wizard.activePage.addToConsistencyGroup(newConsistencyGroup=consistencyGroupName)
        LOG.step("Navigating to 'Select Initiator Groups' page")
        wizard.goNext()
        wizard.selectInitiatorGroupsPage.waitUntilOpen()
        LOG.info("Browser landed on 'Select Initiator Groups' page")

        LOG.step("Navigating to 'Confirm' page")
        wizard.goNext()
        wizard.confirmPage.waitUntilOpen()
        LOG.info("Browser landed on 'Confirm' page")

        LOG.step('Navigating back to front page')
        wizard.goBack()
        wizard.activePage.waitUntilOpen()
        wizard.goBack()
        wizard.activePage.waitUntilOpen()
        LOG.info("Browser landed on 'Define LUNs' page")

        LOG.step('Verifying LUN definitions')
        self.assertTrue(wizard.activePage.dLstNumberOfLUNs.getText() == '1')
        LOG.info('Number of LUNs:', wizard.activePage.dLstNumberOfLUNs.getText())
        self.assertTrue(wizard.activePage.txtName.getText() == lunName)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        self.assertTrue(wizard.activePage.txtSize.getText() == '1')
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())
        self.assertTrue(wizard.activePage.chkAddToConsistencyGroup.isSelected())
        LOG.info('Add to consistency group:', wizard.activePage.chkAddToConsistencyGroup.isSelected())
        self.assertTrue(wizard.activePage.txtNewConsistencyGroup.getText() == consistencyGroupName)
        LOG.info('Consistency group name:', wizard.activePage.txtNewConsistencyGroup.getText())

        LOG.step('Navigating to confirmation page')
        wizard.goNext()
        wizard.activePage.waitUntilOpen()
        wizard.goNext()
        wizard.confirmPage.waitUntilOpen()
        LOG.info('Browser landed on confirmation page')

        LOG.step('Verifying LUNs to create')
        luns = wizard.activePage.gridLUNs.find()
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['name'] == lunName)
        LOG.info('LUNs to create:\n', luns)

        LOG.step("Navigating to 'Close' page")
        wizard.goNext()
        wizard.closePage.waitUntilOpen()
        LOG.info("Browser landed on 'Close' page")

        wizard.closePage.close()
        LOG.info('Wizard closed.')

        LOG.step('Verifying LUN has been created and mapped to consistency group')
        lun = self.marscluster.lun.show(json=True)[0]
        self.assertTrue(lunName in lun['name'])
        self.assertTrue(lun['cg'] == consistencyGroupName)
        LOG.info('LUN name: %s; consistency group: %s' % (lun['name'], lun['cg']))

    def test_single_lun_map_exist_parent_cg(self):
        """
            Test verifies creation of single LUN mapped to existing parent consistency group.
        """
        lunName = 'LuN'
        parentConsistencyGroupName = 'Parent-CG'

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size='1G')
        wizard.activePage.addToConsistencyGroup(parentConsistencyGroup=parentConsistencyGroupName)
        wizard.goNext()
        wizard.goNext()
        wizard.goNext()
        wizard.closePage.close()
        LOG.info('Wizard closed.')

        LOG.step('Verifying LUN has been created and mapped to existing consistency group')
        lun = self.marscluster.lun.show(json=True)[0]
        self.assertTrue(lunName in lun['name'])
        self.assertTrue(lun['cg'] == parentConsistencyGroupName)
        LOG.info('LUN name: %s; consistency group: %s' % (lun['name'], lun['cg']))

    def test_single_lun_map_exist_new_parent_cg(self):
        """
            Test verifies creation of single LUN mapped to existing parent and new consistency groups.
        """
        lunName = 'LuN'
        parentConsistencyGroupName = 'Parent-CG'
        newConsistencyGroupName = 'New-CG'

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size='1G')
        wizard.activePage.addToConsistencyGroup(parentConsistencyGroup=parentConsistencyGroupName,
        newConsistencyGroup=newConsistencyGroupName)
        wizard.goNext()
        wizard.goNext()
        wizard.goNext()
        wizard.closePage.close()
        LOG.info('Wizard closed.')

        LOG.step('Verifying mapped LUN has been created')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['name'] == (parentConsistencyGroupName + '/' + newConsistencyGroupName + '/' + lunName))
        self.assertTrue(luns[0]['cg'] == (parentConsistencyGroupName + '/' + newConsistencyGroupName))
        LOG.info("LUN created: 'name': '%s'; 'cg': '%s'" % (luns[0]['name'], luns[0]['cg']))
        mappingFound = False
        for consistencyGroup in self.marscluster.cg.show(json=True):
            if consistencyGroup['name'] == luns[0]['cg']:
                mappingFound = True
        self.assertTrue(mappingFound)
        LOG.info('Mapped consistency group found.')

    def test_single_lun_map_single_ig(self):
        """
            Test verifies creation of single LUN mapped to single initiator group with single WWPN.
        """
        lunName = 'LuN'
        lunSize = '1G'
        initiatorGroupName = 'IG-1'

        LOG.step('Creating initiator group')
        wwpn = self.marscluster.fcp.initiator_show(json=True)[0]['wwpn']
        self.marscluster.igroup.create(name=initiatorGroupName, ostype='vmware', initiators=wwpn)
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == 1)
        self.assertTrue((initiatorGroups[0]['name'] == initiatorGroupName) and (initiatorGroups[0]['initiators'][0] ==
        wwpn))
        LOG.info("Initiator group created: name: '%s'; initiators: '%s'" % (initiatorGroups[0]['name'],
        initiatorGroups[0]['initiators']))

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size=lunSize)
        LOG.info("Properties defined: name: '%s'; size: '%s'" % (lunName, lunSize))
        wizard.goNext()
        wizard.selectInitiatorGroupsPage.selectInitiatorGroups(initiatorGroups=initiatorGroupName)
        LOG.info("Initiator groups selected: '%s'" % initiatorGroupName)
        wizard.goNext()
        wizard.goNext()
        wizard.closePage.close()
        LOG.info('Wizard closed.')

        LOG.step('Verifying LUN has been created and mapped to initiator group')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['name'] == lunName)
        self.assertTrue(luns[0]['maps'][0]['igroup-name'] == initiatorGroupName)
        self.assertTrue(luns[0]['maps'][0]['lun-name'] == lunName)
        self.assertTrue(luns[0]['igroups'][0] == initiatorGroupName)
        LOG.info("LUN created: name: '%s'; igroup-name: '%s'" % (lunName, initiatorGroupName))

    def test_single_lun_map_multi_ig_different_wwpn(self):
        """
            Test verifies creation of single LUN mapped to multiple initiator groups with different
              WWPNs (one initiator per group).
        """
        lunName = 'LuN'
        lunSize = '1G'
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        initiatorGroupNames = []

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
            initiatorGroupNames.append(initiatorGroupName + str(initiatorIndex))
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupsNumber)
        # Verify all created IGs are in list of IGs were to be created
        for initiatorGroupIndex in range(len(initiatorGroups)):
            del initiatorGroupNames[initiatorGroupNames.index(initiatorGroups[initiatorGroupIndex]['name'])]
        self.assertFalse(initiatorGroupNames)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size=lunSize)
        LOG.info("LUN properties defined: name: '%s'; size: '%s'" % (lunName, lunSize))
        wizard.goNext()
        # Select all created IGs
        initiatorGroupNames = [initiatorGroup['name'] for initiatorGroup in initiatorGroups]
        wizard.selectInitiatorGroupsPage.selectInitiatorGroups(initiatorGroups=initiatorGroupNames)
        LOG.info('Initiator groups selected:\n', initiatorGroupNames)
        wizard.goNext()
        wizard.goNext()
        wizard.closePage.close()
        LOG.info('Wizard closed.')

        LOG.step('Verifying LUN has been created and mapped to initiator groups')
        initiatorGroups = self.marscluster.igroup.show(json=True)
        for initiatorGroup in initiatorGroups:
            self.assertTrue(initiatorGroup['lun-maps'][0]['lun-name'] == lunName)
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        for initiatorGroupName in [initiatorGroup['name'] for initiatorGroup in initiatorGroups]:
            self.assertTrue(initiatorGroupName in luns[0]['igroups'])
        LOG.info("LUN created: name: '%s'; lun-maps:\n'%s'" % (lunName, luns[0]['igroups']))

    def test_multi_lun_auto_start_low(self):
        """
            Test verifies creation of multiple LUNs with values of 'Start At' shorter than suffix (ex. 2 digits in
            'start at' = 55 is shorter than 4 pounds in suffix '####') are justified to number of pounds (i.e. prefix
            'LuN_' and 'start at' 55' gets translated to 'LuN_0055').
        """
        numberOfLUNs = 10
        lunNamePrefix = 'LuN_'
        lunSize = '1G'
        startAt = 99

        for suffixIndex in range(4):
            suffix = '#' * (suffixIndex + 1)
            LOG.step("Creating LUNs with suffix '%s' and starting at %s" % (suffix, str(startAt)))
            LOG.step('Creating wizard')
            wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
            wizard.open()
            LOG.info('Wizard created.')

            LOG.step('Defining multiple LUNs')
            wizard.activePage.defineMultipleLUNsAuto(number=numberOfLUNs, size=lunSize, prefix=lunNamePrefix,
            suffix=(suffix + ' '), startAt=startAt)
            LOG.info("LUN properties defined: number: %s; size: %s, prefix: '%s'; suffix: '%s'; start at: %s" %
            (numberOfLUNs, lunSize, lunNamePrefix, (suffix + ' '), startAt))
            wizard.goNext()
            wizard.goNext()
            wizard.goNext()
            wizard.closePage.close()
            LOG.info('Wizard closed.')

            LOG.step('Verifying LUN names')
            lunNames = [lun['name'] for lun in self.marscluster.lun.show(json=True)]
            for lunIndex in range(startAt, (startAt + numberOfLUNs)):
                lunName = lunNamePrefix + str(lunIndex).rjust(suffixIndex + 1, '0')
                self.assertTrue(lunName in lunNames)
                LOG.info('LUN found:', lunName)

            LOG.step('Destroying LUNs')
            self.marscluster.lun.destroyAll()
            self.assertFalse(self.marscluster.lun.show(json=True))
            LOG.info('All LUNs destroyed.')

    def test_multi_lun_auto_start_high(self):
        """
            Test verifies creation of multiple LUNs with values of 'Start At' longer than suffix (ex. 5 digits in
            'start at' = 55555 is longer than 4 pounds in suffix '####') are not truncated to number of pounds (i.e.
            'LuN_55555' is not becoming 'LuN_5555').
        """
        numberOfLUNs = 10
        lunNamePrefix = 'LuN_'
        lunSize = '1G'
        startAt = 55555

        for suffixIndex in range(4):
            suffix = '#' * (suffixIndex + 1)
            LOG.step("Creating LUNs with suffix '%s' and starting at %s" % (suffix, str(startAt)))
            LOG.step('Creating wizard')
            wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
            wizard.open()
            LOG.info('Wizard created.')

            LOG.step('Defining multiple LUNs')
            wizard.activePage.defineMultipleLUNsAuto(number=numberOfLUNs, size=lunSize, prefix=lunNamePrefix,
            suffix=(suffix + ' '), startAt=startAt)
            LOG.info("LUN properties defined: number: %s; size: %s, prefix: '%s'; suffix: '%s'; start at: %s" %
            (numberOfLUNs, lunSize, lunNamePrefix, (suffix + ' '), startAt))
            wizard.goNext()
            wizard.goNext()
            wizard.goNext()
            wizard.closePage.close()
            LOG.info('Wizard closed.')

            LOG.step('Verifying LUN names')
            lunNames = [lun['name'] for lun in self.marscluster.lun.show(json=True)]
            for lunIndex in range(startAt, (startAt + numberOfLUNs)):
                self.assertTrue((lunNamePrefix + str(lunIndex)) in lunNames)
                LOG.info('LUN found:', lunNamePrefix + str(lunIndex))

            LOG.step('Destroying LUNs')
            self.marscluster.lun.destroyAll()
            self.assertFalse(self.marscluster.lun.show(json=True))
            LOG.info('All LUNs destroyed.')

    def test_multi_lun_terminal_size(self):
        """
            Test verifies creation of multiple LUNs with minimum and maximum sizes respecting given size unit.
        """
        # Could be increased with bigger capacity storage. Now is supports 2 LUNs at 64 TB.
        sizes = {
            'B': {
                'low': 512,
                'high': long(64) * pow(1024, 4),
                'multiplier': 1
            },
            'K': {
                'low': 0.5,
                'high': long(64) * pow(1024, 3),
                'multiplier': 1024
            },
            'M': {
                'low': 0.001,
                'high': long(64) * pow(1024, 2),
                'multiplier': 1024 ** 2
            },
            'G': {
                'low': 0.001,
                'high': long(64) * 1024,
                'multiplier': 1024 ** 3
            },
            'T': {
                'low': 0.001,
                'high': 64,
                'multiplier': 1024 ** 4
            }
        }
        lunsToCreate = {}

        for sizeUnit in sizes:
            nameLow = 'LuN_' + sizeUnit + '_low'
            sizeLow = str(sizes[sizeUnit]['low']) + sizeUnit
            nameHigh = 'LuN_' + sizeUnit + '_high'
            sizeHigh = str(sizes[sizeUnit]['high']) + sizeUnit

            LOG.step('Creating wizard')
            wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
            wizard.open()
            self.assertTrue(wizard.defineLUNsPage.isOpen())
            LOG.info('Wizard created.')

            LOG.step("Creating 2 LUNs with minimal and maximal sizes: name=['%s', '%s'], size=['%s', '%s'])" % (nameLow,
            nameHigh, sizeLow, sizeHigh))
            lunsProperties = [
                {
                    'name': nameLow,
                    'size': sizeLow
                }, {
                    'name': nameHigh,
                    'size': sizeHigh
                }
            ]
            wizard.activePage.defineMultipleLUNsManually(lunsProperties=lunsProperties)
            wizard.goNext()
            wizard.goNext()
            wizard.goNext()
            wizard.closePage.close()
            LOG.info('Wizard closed.')

            sizeToCreate = sizes[sizeUnit]['low'] * sizes[sizeUnit]['multiplier']
            # Sizes of LUNs are rounded up to 512-byte bound
            if sizeToCreate % 512 > 0:
                sizeToCreate = int(sizeToCreate / 512) * 512 + 512
            lunsToCreate[nameLow] = sizeToCreate

            lunsToCreate[nameHigh] = sizes[sizeUnit]['high'] * sizes[sizeUnit]['multiplier']

            createdLUNs = self.marscluster.lun.show(json=True)

            LOG.step('Verifying size of created LUNs is as specified')
            for lun in createdLUNs:
                self.assertTrue(lun['size'] == lunsToCreate[lun['name']])
                LOG.info("Size of LUN '%s' (bytes): %s" % (lun['name'], lun['size']))

            LOG.step('Destroying LUNs')
            self.marscluster.lun.destroyAll()
            self.assertFalse(self.marscluster.lun.show(json=True))
            LOG.info('All LUNs destroyed.')

    def test_multi_lun_map_exist_new_parent_cg(self):
        """
            Test verifies creation of multiple LUNs mapped to existing parent and new consistency groups.
        """
        parentConsistencyGroupName = 'Parent-CG'
        newConsistencyGroupName = 'New-CG'
        lunsProperties = [
            {
                'name': 'LuN-1',
                'size': '1G'
            }, {
                'name': 'LuN-2',
                'size': '1G'
            }, {
                'name': 'LuN-3',
                'size': '1G'
            }, {
                'name': 'LuN-4',
                'size': '1G'
            }, {
                'name': 'LuN-5',
                'size': '1G'
            }, {
                'name': 'LuN-6',
                'size': '1G'
            }, {
                'name': 'LuN-7',
                'size': '1G'
            }, {
                'name': 'LuN-8',
                'size': '1G'
            }, {
                'name': 'LuN-9',
                'size': '1G'
            }, {
                'name': 'LuN-10',
                'size': '1G'
            }
        ]

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Creating %s LUNs mapped to existing parent and new consistency groups' % len(lunsProperties))
        wizard.activePage.defineMultipleLUNsManually(lunsProperties=lunsProperties)
        wizard.activePage.addToConsistencyGroup(parentConsistencyGroup=parentConsistencyGroupName,
        newConsistencyGroup=newConsistencyGroupName)
        wizard.goNext()
        wizard.goNext()
        wizard.goNext()
        wizard.closePage.close()
        LOG.info('Wizard closed.')

        LOG.step('Verifying LUNs have been created and mapped to consistency groups')
        lunNames = [lunProperties['name'] for lunProperties in lunsProperties]
        luns = self.marscluster.lun.show(json=True)
        for lun in luns:
            self.assertTrue(lun['name'].split('/')[-1] in lunNames)
            self.assertTrue(lun['cg'] == parentConsistencyGroupName + '/' + newConsistencyGroupName)
            LOG.info("LUN found: name: '%s'; cg: '%s'" % (lun['name'], lun['cg']))

    def test_multi_lun_map_multi_ig_different_wwpn(self):
        """
            Test verifies creation of multiple LUNs defined manually and mapped to multiple initiator groups with
            different WWPNs.
        """
        initiatorGroupName = 'IG-'
        initiatorGroupsNumber = 5
        initiatorGroupNames = []

        lunsProperties = [
            {
                'name': 'LuN-1',
                'size': '1G'
            }, {
                'name': 'LuN-2',
                'size': '1G'
            }, {
                'name': 'LuN-3',
                'size': '1G'
            }, {
                'name': 'LuN-4',
                'size': '1G'
            }, {
                'name': 'LuN-5',
                'size': '1G'
            }, {
                'name': 'LuN-6',
                'size': '1G'
            }, {
                'name': 'LuN-7',
                'size': '1G'
            }, {
                'name': 'LuN-8',
                'size': '1G'
            }, {
                'name': 'LuN-9',
                'size': '1G'
            }, {
                'name': 'LuN-10',
                'size': '1G'
            }
        ]

        LOG.step('Creating initiator groups')
        for initiatorIndex in range(initiatorGroupsNumber):
            fictiveWWPN = format(random.randrange(sys.maxint), 'x').rjust(16, 'f')
            self.marscluster.igroup.create(name=(initiatorGroupName + str(initiatorIndex)),
                ostype='vmware', initiators=fictiveWWPN)
            initiatorGroupNames.append(initiatorGroupName + str(initiatorIndex))
        initiatorGroups = self.marscluster.igroup.show(json=True)
        self.assertTrue(len(initiatorGroups) == initiatorGroupsNumber)
        # Verify all created IGs are in list of IGs were to be created
        for initiatorGroupIndex in range(len(initiatorGroups)):
            del initiatorGroupNames[initiatorGroupNames.index(initiatorGroups[initiatorGroupIndex]['name'])]
        self.assertFalse(initiatorGroupNames)
        LOG.info('Initiator groups created:\n', initiatorGroups)

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Creating %s LUNs mapped to multiple initiator groups with different WWPNs' %
            len(lunsProperties))
        wizard.activePage.defineMultipleLUNsManually(lunsProperties=lunsProperties)
        LOG.info('LUNs properties defined:\n', lunsProperties)
        wizard.goNext()
        # Select all created IGs
        initiatorGroupNames = [initiatorGroup['name'] for initiatorGroup in initiatorGroups]
        wizard.selectInitiatorGroupsPage.selectInitiatorGroups(initiatorGroups=initiatorGroupNames)
        LOG.info('Initiator groups selected:\n', initiatorGroupNames)
        wizard.goNext()
        wizard.goNext()
        # Give some time to complete operation
        time.sleep(2)
        wizard.closePage.close()
        LOG.info('Wizard closed.')

        LOG.step('Verifying LUNs have been created and mapped to initiator groups')
        lunNames = [lunProperties['name'] for lunProperties in lunsProperties]
        luns = self.marscluster.lun.show(json=True)
        initiatorGroupNames = [initiatorGroup['name'] for initiatorGroup in self.marscluster.igroup.show(json=True)]
        for lun in luns:
            self.assertTrue(lun['name'] in lunNames)
            del lunNames[lunNames.index(lun['name'])]
            lunMapNames = [map['igroup-name'] for map in lun['maps']]
            for initiatorGroupName in initiatorGroupNames:
                self.assertTrue(initiatorGroupName in lunMapNames)
            LOG.info("LUN found: name: '%s''; maps:\n%s" % (lun['name'], lunMapNames))

    def test_dialog_not_available(self):
        """
            Verify wizard cannot proceed (button 'Next' is disabled) when inputs are not fully
            populated.
        """
        lunName = 'LuN'
        lunSize = '10'
        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver, locale=self.locale)
        wizard.open()
        LOG.info('Wizard created.')

        LOG.step('Verifying proceed is disabled')
        self.assertFalse(wizard.activePage.txtName.getText())
        LOG.info("Name: '%s'" % wizard.activePage.txtName.getText())
        self.assertFalse(wizard.activePage.txtSize.getText())
        LOG.info("Size: '%s'" % wizard.activePage.txtSize.getText())
        wizard.activePage.btnNext.waitUntilDisabled()
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step('Setting only LUN name')
        wizard.activePage.txtName.setText(text=lunName)
        self.assertTrue(wizard.activePage.txtName.getText() == lunName)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())
        wizard.activePage.btnNext.waitUntilDisabled()
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step('Setting only LUN size')
        wizard.activePage.txtName.clear()
        wizard.activePage.txtSize.setText(text=lunSize)
        self.assertTrue(wizard.activePage.txtSize.getText() == lunSize)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())
        wizard.activePage.btnNext.waitUntilDisabled()
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step('Setting LUN name & size')
        wizard.activePage.txtName.setText(text=lunName)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())
        wizard.activePage.btnNext.waitUntilEnabled()
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

    def deleteDependentConsistencyGroups(self):
        while True:
            consistencyGroups = self.marscluster.cg.show(json=True)
            if not consistencyGroups:
                break
            else:
                for consistencyGroup in consistencyGroups:
                    if 'cg' not in consistencyGroup:
                        self.marscluster.cg.delete(name=consistencyGroup['name'])

    def testTeardown(self):
        self.driver.quit()
        luns = express.Luns(node=self.marscluster, cleanup=True)
        del luns
        LOG.info('LUNs destroyed.')


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testCreateLUNsWizard = TestCreateLUNsWizard()
    sys.exit(testCreateLUNsWizard.numberOfFailedTests())
