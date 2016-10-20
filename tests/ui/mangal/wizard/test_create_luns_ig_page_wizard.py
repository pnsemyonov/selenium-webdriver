#!/usr/bin/env python

purpose = """Functional test of wizard 'Create LUNs' called from 'Initiator Groups' page"""

import os
import sys
import random
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import time
import express
import frutil
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from mangal.wizard.create_luns_ig_page_wizard import *
from frlog import LOG
from frargs import ARGS
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

class TestCreateLUNsIGPageWizard(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.locale = ARGS.values.locale
        self.webUIHostName = frutil.getFQDN(self.marscluster.getMasterNode().hostname)

    def testSetup(self):
        self.driver = self.getDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)

        LOG.info('Destroying existing LUNs...')
        self.marscluster.lun.unmapAll()
        self.marscluster.lun.destroyAll()
        self.assertFalse(self.marscluster.lun.show(json=True))
        LOG.info('Done.')
        LOG.info('Destroying existing initiator groups...')
        self.marscluster.igroup.destroyAll()
        LOG.info('Done.')
        LOG.info('Destroying existing consistency groups...')
        self._deleteDependentConsistencyGroups()
        LOG.info('Done.')

        if self.locale is None:
            self.locale = self.loginPage.getRandomLocale()
        self.loginPage.signIn(username=self.username, password=self.password, locale=self.locale)
        LOG.info('Signed in with username: %s, password: %s, locale: %s.' % (self.username,
            self.password, self.locale))

    def test_single_lun_invalid_name(self):
        """
            Test verifies inability of creation of single LUN with invalid name.
        """
        name = 'LuN:$1001'
        numberOfLUNs = '1'
        size = '3g'
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 5

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)

        LOG.step('Opening dialog')
        wizard.open(initiator_group=initiatorGroups[0])
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Front page is open:', wizard.defineLUNsPage.isOpen())

        LOG.step("Calling: defineSingleLUN(name='%s', size='%s')" % (name, size))
        wizard.activePage.defineSingleLUN(name=name, size=size)

        LOG.step('Verifying error message as name is invalid')
        self.assertTrue(wizard.activePage.lblNameError.isPresent())
        LOG.info('Error message is present:', wizard.activePage.lblNameError.isPresent())
        wizard.activePage.lblNameError.isVisible()
        LOG.info('Error message is visible:', wizard.activePage.lblNameError.isVisible())
        LOG.info('Error message:', wizard.activePage.lblNameError.isPresent())

        LOG.step("Verifying button 'OK' is disabled.")
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

        LOG.step('Verifying no LUNs have been created')
        luns = self.marscluster.lun.show(json=True)
        self.assertFalse(luns)
        LOG.info('LUNs:', luns)

    def test_single_lun_max_length_name(self):
        """
            Test verifies creation of single LUNs with maximum length of name (255).
        """
        name = 'LuN__' + ('0' * 250)
        size = '3g'
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 5

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)

        LOG.step('Opening dialog')
        wizard.open(initiator_group=initiatorGroups[0])
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Front page is open:', wizard.defineLUNsPage.isOpen())

        LOG.step("Calling method: defineSingleLUN(name='%s', size='%s')" % (name, size))
        wizard.activePage.defineSingleLUN(name=name, size=size)

        LOG.step('Verifying no name error message present on page.')
        self.assertFalse(wizard.activePage.lblNameError.isPresent())
        LOG.info('Name error message is present:', wizard.activePage.lblNameError.isPresent())

        LOG.step('Finishing wizard')
        wizard.activePage.submit()
        wizard.activePage.waitUntilClosed()
        LOG.info('Wizard closed.')

        LOG.step('Verifying created LUN has provided name')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['name'] == name)
        LOG.info('LUN name:', luns[0]['name'])

        LOG.step('Verifying LUN has specified mapping')
        self.assertTrue(len(luns[0]['maps']) == 1)
        self.assertTrue(luns[0]['maps'][0]['igroup-name'] == initiatorGroups[0])
        LOG.info('LUN mapping:', luns[0]['maps'])

    def test_single_lun_terminal_size(self):
        """
            Test verifies creation of single LUN with minimum and maximum sizes respecting given size unit.
        """
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3
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

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)
        lunsToCreate = {}

        for sizeUnit in sizes:
            nameLow = 'LuN_' + sizeUnit + '_low'
            sizeLow = str(sizes[sizeUnit]['low']) + sizeUnit
            nameHigh = 'LuN_' + sizeUnit + '_high'
            sizeHigh = str(sizes[sizeUnit]['high']) + sizeUnit

            LOG.step('Opening wizard')
            wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
            wizard.open(initiator_group=initiatorGroups[0])
            self.assertTrue(wizard.defineLUNsPage.isOpen())
            LOG.info('Wizard open.')

            LOG.step("Creating LUN with minimal size: name='%s', size='%s')" % (nameLow, sizeLow))
            wizard.activePage.defineSingleLUN(name=nameLow, size=sizeLow)
            wizard.defineLUNsPage.submit()
            LOG.info('Wizard submitted.')

            sizeToCreate = sizes[sizeUnit]['low'] * sizes[sizeUnit]['multiplier']
            # Sizes of LUNs are rounded up to 512-byte bound
            if sizeToCreate % 512 > 0:
                sizeToCreate = int(sizeToCreate / 512) * 512 + 512
            lunsToCreate[nameLow] = sizeToCreate

            LOG.step('Opening wizard')
            wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
            wizard.open(initiator_group=initiatorGroups[0])
            self.assertTrue(wizard.defineLUNsPage.isOpen())
            LOG.info('Wizard open.')

            LOG.step("Creating LUN with minimal size: name='%s', size='%s')" % (nameHigh, sizeHigh))
            wizard.activePage.defineSingleLUN(name=nameHigh, size=sizeHigh)
            wizard.defineLUNsPage.submit()
            LOG.info('Wizard submitted.')

            lunsToCreate[nameHigh] = sizes[sizeUnit]['high'] * sizes[sizeUnit]['multiplier']

            createdLUNs = self.marscluster.lun.show(json=True)
            self.assertTrue(len(createdLUNs) == 2)

            LOG.step('Verifying sizes and mappings of created LUNs are as specified')
            for lun in createdLUNs:
                self.assertTrue(lun['size'] == lunsToCreate[lun['name']])
                LOG.info("Size of LUN '%s' (bytes): %s" % (lun['name'], lun['size']))
                self.assertTrue(len(lun['maps']) == 1)
                self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroups[0])
                LOG.info("LUN '%s' mapping: %s" % (lun['name'], lun['maps'][0]))

            LOG.step('Destroying LUNs')
            self.marscluster.lun.unmapAll()
            self.marscluster.lun.destroyAll()
            self.assertFalse(self.marscluster.lun.show(json=True))
            LOG.info('All LUNs destroyed.')

    def test_single_lun_map_new_parent_cg(self):
        """
            Test verifies creation of single LUN mapped to newly created parent consistency group.
        """
        lunName = 'LuN'
        lunSize = '1g'
        consistencyGroupName = 'New-CG'
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size=lunSize)
        LOG.info('LUN name:', lunName)
        LOG.info('LUN size:', lunSize)
        wizard.activePage.addToConsistencyGroup(newConsistencyGroup=consistencyGroupName)
        LOG.info("LUN's consistency group:", consistencyGroupName)
        wizard.activePage.submit()
        LOG.info('Wizard submitted.')

        LOG.step('Verifying LUN has been created and mapped to consistency group')
        lun = self.marscluster.lun.show(json=True)[0]
        self.assertTrue(lunName in lun['name'])
        self.assertTrue(lun['cg'] == consistencyGroupName)
        LOG.info('LUN name: %s; consistency group: %s' % (lun['name'], lun['cg']))

        LOG.step('Verifying LUN has specified mapping')
        self.assertTrue(len(lun['maps']) == 1)
        self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroups[0])
        LOG.info('LUN mapping:', lun['maps'])

    def test_single_lun_map_exist_parent_cg(self):
        """
            Test verifies creation of single LUN mapped to existing parent consistency group.
        """
        lunName = 'LuN'
        lunSize = '1g'
        parentConsistencyGroupName = 'Parent-CG'
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        LOG.step('Creating wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size=lunSize)
        LOG.info('LUN name:', lunName)
        LOG.info('LUN size:', lunSize)
        wizard.activePage.addToConsistencyGroup(parentConsistencyGroup=parentConsistencyGroupName)
        LOG.info("LUN's consistency group:", parentConsistencyGroupName)
        wizard.activePage.submit()
        LOG.info('Wizard submitted.')

        LOG.step('Verifying LUN has been created and mapped to existing consistency group')
        lun = self.marscluster.lun.show(json=True)[0]
        self.assertTrue(lunName in lun['name'])
        self.assertTrue(lun['cg'] == parentConsistencyGroupName)
        LOG.info('LUN name: %s; consistency group: %s' % (lun['name'], lun['cg']))

        LOG.step('Verifying LUN has specified mapping')
        self.assertTrue(len(lun['maps']) == 1)
        self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroups[0])
        LOG.info('LUN mapping:', lun['maps'])

    def test_single_lun_map_exist_new_parent_cg(self):
        """
            Test verifies creation of single LUN mapped to existing parent and new consistency groups.
        """
        lunName = 'LuN'
        lunSize = '1g'
        parentConsistencyGroupName = 'Parent-CG'
        newConsistencyGroupName = 'New-CG'
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        LOG.step('Creating wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Wizard created.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size=lunSize)
        LOG.info('LUN name:', lunName)
        LOG.info('LUN size:', lunSize)
        wizard.activePage.addToConsistencyGroup(parentConsistencyGroup=parentConsistencyGroupName,
        newConsistencyGroup=newConsistencyGroupName)
        LOG.info("LUN's consistency group:", parentConsistencyGroupName)
        wizard.activePage.submit()
        LOG.info('Wizard submitted.')

        LOG.step('Verifying mapped LUN has been created')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['name'] == (parentConsistencyGroupName + '/' +
            newConsistencyGroupName + '/' + lunName))
        self.assertTrue(luns[0]['cg'] == (parentConsistencyGroupName + '/' +
            newConsistencyGroupName))
        LOG.info("LUN created: 'name': '%s'; 'cg': '%s'" % (luns[0]['name'], luns[0]['cg']))
        mappingFound = False
        for consistencyGroup in self.marscluster.cg.show(json=True):
            if consistencyGroup['name'] == luns[0]['cg']:
                mappingFound = True
        self.assertTrue(mappingFound)
        LOG.info('Mapped consistency group found.')

        LOG.step('Verifying LUN has specified mapping')
        self.assertTrue(len(luns[0]['maps']) == 1)
        self.assertTrue(luns[0]['maps'][0]['igroup-name'] == initiatorGroups[0])
        LOG.info('LUN mapping:', luns[0]['maps'])

    def test_multi_lun_auto_start_low(self):
        """
            Test verifies creation of multiple LUNs with values of 'Start At' shorter than suffix (ex. 2 digits in
            'start at' = 55 is shorter than 4 pounds in suffix '####') are justified to number of pounds (i.e. prefix
            'LuN_' and 'start at' 55' gets translated to 'LuN_0055').
        """
        numberOfLUNs = 10
        lunNamePrefix = 'LuN_'
        lunSize = '1g'
        startAt = 99
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        for suffixIndex in range(4):
            suffix = '#' * (suffixIndex + 1)
            LOG.step("Creating LUNs with suffix '%s' and starting at %s" % (suffix, str(startAt)))
            LOG.step('Creating wizard')
            wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
            wizard.open(initiator_group=initiatorGroups[0])
            LOG.info('Wizard created.')

            LOG.step('Defining multiple LUNs')
            wizard.activePage.defineMultipleLUNsAuto(number=numberOfLUNs, size=lunSize,
                prefix=lunNamePrefix, suffix=(suffix + ' '), startAt=startAt)
            LOG.info("LUN properties defined: number: %s; size: %s, prefix: '%s'; suffix: '%s'; start at: %s" %
            (numberOfLUNs, lunSize, lunNamePrefix, (suffix + ' '), startAt))
            wizard.activePage.submit()
            LOG.info('Wizard submitted.')

            LOG.step('Verifying LUN names')
            luns = self.marscluster.lun.show(json=True)
            lunNames = [lun['name'] for lun in luns]
            for lunIndex in range(startAt, (startAt + numberOfLUNs)):
                lunName = lunNamePrefix + str(lunIndex).rjust(suffixIndex + 1, '0')
                self.assertTrue(lunName in lunNames)
                LOG.info('LUN found:', lunName)

            LOG.step('Verifying mapping of all LUNs')
            for lun in luns:
                self.assertTrue(len(lun['maps']) == 1)
                self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroups[0])
                LOG.info("LUN '%s' mapping: %s" % (lun['name'], lun['maps'][0]))

                LOG.step('Destroying LUNs')
                self.marscluster.lun.unmapAll()
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
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        for suffixIndex in range(4):
            suffix = '#' * (suffixIndex + 1)
            LOG.step("Creating LUNs with suffix '%s' and starting at %s" % (suffix, str(startAt)))
            LOG.step('Creating wizard')
            wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
            wizard.open(initiator_group=initiatorGroups[0])
            LOG.info('Wizard created.')

            LOG.step('Defining multiple LUNs')
            wizard.activePage.defineMultipleLUNsAuto(number=numberOfLUNs, size=lunSize,
                prefix=lunNamePrefix, suffix=(suffix + ' '), startAt=startAt)
            LOG.info("LUN properties defined: number: %s; size: %s, prefix: '%s'; suffix: '%s'; start at: %s" %
            (numberOfLUNs, lunSize, lunNamePrefix, (suffix + ' '), startAt))
            wizard.activePage.submit()
            LOG.info('Wizard submitted.')

            LOG.step('Verifying LUN names')
            luns = self.marscluster.lun.show(json=True)
            lunNames = [lun['name'] for lun in self.marscluster.lun.show(json=True)]
            for lunIndex in range(startAt, (startAt + numberOfLUNs)):
                self.assertTrue((lunNamePrefix + str(lunIndex)) in lunNames)
                LOG.info('LUN found:', lunNamePrefix + str(lunIndex))

            LOG.step('Verifying mapping of all LUNs')
            for lun in luns:
                self.assertTrue(len(lun['maps']) == 1)
                self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroups[0])
                LOG.info("LUN '%s' mapping: %s" % (lun['name'], lun['maps'][0]))

                LOG.step('Destroying LUNs')
                self.marscluster.lun.unmapAll()
                self.marscluster.lun.destroyAll()
                self.assertFalse(self.marscluster.lun.show(json=True))
                LOG.info('All LUNs destroyed.')

    def test_multi_lun_terminal_size(self):
        """
            Test verifies creation of multiple LUNs with minimum and maximum sizes respecting given size unit.
        """
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3
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

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)
        lunsToCreate = {}

        for sizeUnit in sizes:
            nameLow = 'LuN_' + sizeUnit + '_low'
            sizeLow = str(sizes[sizeUnit]['low']) + sizeUnit
            nameHigh = 'LuN_' + sizeUnit + '_high'
            sizeHigh = str(sizes[sizeUnit]['high']) + sizeUnit

            LOG.step('Opening wizard')
            wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
            wizard.open(initiator_group=initiatorGroups[0])
            self.assertTrue(wizard.defineLUNsPage.isOpen())
            LOG.info('Wizard open.')

            LOG.step("Creating 2 LUNs with minimal and maximal sizes: name=['%s', '%s'], size=['%s', '%s'])"
                % (nameLow, nameHigh, sizeLow, sizeHigh))
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
            wizard.defineLUNsPage.submit()
            LOG.info('Wizard submitted.')

            sizeToCreate = sizes[sizeUnit]['low'] * sizes[sizeUnit]['multiplier']
            # Sizes of LUNs are rounded up to 512-byte bound
            if sizeToCreate % 512 > 0:
                sizeToCreate = int(sizeToCreate / 512) * 512 + 512
            lunsToCreate[nameLow] = sizeToCreate

            lunsToCreate[nameHigh] = sizes[sizeUnit]['high'] * sizes[sizeUnit]['multiplier']

            createdLUNs = self.marscluster.lun.show(json=True)

            LOG.step('Verifying sizes and mappings of created LUNs are as specified')
            for lun in createdLUNs:
                self.assertTrue(lun['size'] == lunsToCreate[lun['name']])
                LOG.info("Size of LUN '%s' (bytes): %s" % (lun['name'], lun['size']))
                self.assertTrue(len(lun['maps']) == 1)
                self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroups[0])
                LOG.info("LUN '%s' mapping: %s" % (lun['name'], lun['maps'][0]))

            LOG.step('Destroying LUNs')
            self.marscluster.lun.unmapAll()
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
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Creating consistency group')
        self.marscluster.cg.create(name=parentConsistencyGroupName)
        consistencyGroups = self.marscluster.cg.show(json=True)
        self.assertTrue(len(consistencyGroups) == 1)
        self.assertTrue(consistencyGroups[0]['name'] == parentConsistencyGroupName)
        LOG.info('Consistency group created:', parentConsistencyGroupName)

        LOG.step('Opening wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Wizard open.')

        LOG.step('Creating %s LUNs mapped to existing parent and new consistency groups' %
            len(lunsProperties))
        wizard.activePage.defineMultipleLUNsManually(lunsProperties=lunsProperties)
        wizard.activePage.addToConsistencyGroup(parentConsistencyGroup=parentConsistencyGroupName,
            newConsistencyGroup=newConsistencyGroupName)
        wizard.activePage.submit()
        LOG.info('Wizard submitted.')

        LOG.step('Verifying LUNs have been created and mapped')
        lunNames = [lunProperties['name'] for lunProperties in lunsProperties]
        luns = self.marscluster.lun.show(json=True)
        for lun in luns:
            self.assertTrue(lun['name'].split('/')[-1] in lunNames)
            self.assertTrue(lun['cg'] == parentConsistencyGroupName + '/' + newConsistencyGroupName)
            LOG.info("LUN found: name: '%s'; cg: '%s'" % (lun['name'], lun['cg']))
            self.assertTrue(len(lun['maps']) == 1)
            self.assertTrue(lun['maps'][0]['igroup-name'] == initiatorGroups[0])
            LOG.info("LUN '%s' mapping: %s" % (lun['name'], lun['maps'][0]))

    def test_invalid_inputs(self):
        """
            Verify wizard cannot proceed (button 'OK' is disabled) when inputs are not fully
            populated.
        """
        lunName = 'LuN'
        lunSize = '10'
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Opening wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Wizard open.')

        LOG.step('Verifying proceed is disabled')
        self.assertFalse(wizard.activePage.txtName.getText())
        LOG.info("Name: '%s'" % wizard.activePage.txtName.getText())
        self.assertFalse(wizard.activePage.txtSize.getText())
        LOG.info("Size: '%s'" % wizard.activePage.txtSize.getText())
        wizard.activePage.btnOK.waitUntilDisabled()
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Setting only LUN name')
        wizard.activePage.txtName.setText(text=lunName)
        self.assertTrue(wizard.activePage.txtName.getText() == lunName)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())
        wizard.activePage.btnOK.waitUntilDisabled()
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Setting only LUN size')
        wizard.activePage.txtName.clear()
        wizard.activePage.txtSize.setText(text=lunSize)
        self.assertTrue(wizard.activePage.txtSize.getText() == lunSize)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())
        wizard.activePage.btnOK.waitUntilDisabled()
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Setting LUN name & size')
        wizard.activePage.txtName.setText(text=lunName)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())
        wizard.activePage.btnOK.waitUntilEnabled()
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

    def test_dialog_cancel(self):
        """
            Verify no LUNs created when dialog closed without submission.
        """
        lunName = 'LuN'
        lunSize = '1g'
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Opening wizard')
        wizard = CreateLUNsIGPageWizard(driver=self.driver, locale=self.locale)
        wizard.open(initiator_group=initiatorGroups[0])
        LOG.info('Wizard open.')

        LOG.step('Defining single LUN')
        wizard.activePage.defineSingleLUN(name=lunName, size=lunSize)
        LOG.info('LUN name:', lunName)
        LOG.info('LUN size:', lunSize)

        LOG.step('Closing wizard without submission')
        wizard.cancel()
        LOG.info('Wizard cancelled.')

        LOG.step('Verifying LUN has not been created')
        luns = self.marscluster.lun.show(json=True)
        self.assertFalse(luns)
        LOG.info('LUNs:', luns)

    def test_dialog_not_available(self):
        """
            Verify item 'LUNs' of menu 'Create' on Initiator Groups page is disabled when no
              initiator group selected.
        """
        initiatorGroupPrefix = 'IG'
        initiatorGroupNumber = 3

        initiatorGroups = self._createInitiatorGroups(prefix= initiatorGroupPrefix,
            number=initiatorGroupNumber)

        LOG.step('Navigating to Initiator Groups page')
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabInitiatorGroups.click()
        initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)
        self.assertTrue(initiatorGroupsPage.isOpen())
        LOG.info('Initiator Groups page is open:', initiatorGroupsPage.isOpen())

        LOG.step('Unselecting all initiator groups in grid')
        initiatorGroupsPage.gridInitiatorGroups.unselect()
        initiatorGroups = initiatorGroupsPage.gridInitiatorGroups.find(selected=True)
        self.assertFalse(initiatorGroups)
        LOG.info('Selected initiator groups:', initiatorGroups)

        LOG.step("Verifying menu item 'Create -> LUNs' is disabled")
        menuCreate = initiatorGroupsPage.menuCreate
        self.assertFalse(menuCreate.isItemEnabled(item='LUNs'))
        LOG.info("Menu item 'Create -> LUNs' is enabled:", menuCreate.isItemEnabled(item='LUNs'))

    def testTeardown(self):
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

    def _deleteDependentConsistencyGroups(self):
        while True:
            consistencyGroups = self.marscluster.cg.show(json=True)
            if not consistencyGroups:
                break
            else:
                for consistencyGroup in consistencyGroups:
                    if 'cg' not in consistencyGroup:
                        self.marscluster.cg.delete(name=consistencyGroup['name'])


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testCreateLUNsIGPageWizard = TestCreateLUNsIGPageWizard()
    sys.exit(testCreateLUNsIGPageWizard.numberOfFailedTests())
