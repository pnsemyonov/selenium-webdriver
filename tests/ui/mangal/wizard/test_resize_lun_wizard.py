#!/usr/bin/env python

purpose = """Mangal UI LUNs Page: Functional testing of 'Resize LUN' dialog"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

import express

from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.resize_lun_wizard import *

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


class TestResizeLUNWizard(FRTestCase):
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

    def test_valid_size(self):
        """
            Verify LUN resizing with valid size.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunOldSize = 2
        lunNewSize = 10
        lunSizeUnit = 'G'
        lunNamePrefix = 'LuN'
        self.luns.create(count=lunCount, size=str(lunOldSize) + lunSizeUnit, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Resizing LUN in dialog')
        wizard = ResizeLUNWizard(driver=self.driver, locale=self.locale)
        wizard.open(name=lunNamePrefix + '_1')

        LOG.info('Old LUN size:', str(lunOldSize) + lunSizeUnit)
        wizard.resizeLUNPage.resizeLUN(size=str(lunNewSize) + lunSizeUnit)
        LOG.info('New LUN size:', wizard.resizeLUNPage.txtSize.getText() +
            wizard.resizeLUNPage.dLstSizeUnit.getText())
        wizard.resizeLUNPage.submit()
        LOG.info('Resize submitted.')

        LOG.step('Verifying LUN size has been changed as specified')
        luns = self.lunsPage.gridLUNs.find(name=lunNamePrefix + '_1')
        self.assertTrue(len(luns) == 1)
        resultSize = float(Utility.getSizeValue(size=luns[0]['size']).replace(',', '.'))
        resultSizeUnit = Utility.getSizeUnit(size=luns[0]['size'])
        self.assertTrue(resultSize == lunNewSize)
        self.assertTrue(resultSizeUnit == lunSizeUnit)
        LOG.info('LUN found: name=%s, size=%s.' % (luns[0]['name'], luns[0]['size']))

    def test_invalid_size(self):
        """
            Verify error message on LUN resizing with invalid size.
            Verify LUN size remains intact.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunOldSize = 104857600
        lunNamePrefix = 'LuN'
        lunNewSize = '65t'
        self.luns.create(count=lunCount, size=lunOldSize, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Setting new LUN size in dialog')
        wizard = ResizeLUNWizard(driver=self.driver, locale=self.locale)
        wizard.open(name=lunNamePrefix + '_1')
        wizard.resizeLUNPage.resizeLUN(size=lunNewSize)
        LOG.info('New LUN size:', wizard.resizeLUNPage.txtSize.getText() +
            wizard.resizeLUNPage.dLstSizeUnit.getText())
        self.assertTrue(wizard.activePage.lblSizeError.isVisible())
        LOG.info('Error message displayed:',
            wizard.activePage.lblSizeError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Canceling dialog')
        wizard.cancel()
        LOG.info('Dialog closed.')

        LOG.step('Verifying no changes have been made for LUNs sizes')
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        for lun in self.marscluster.lun.show(json=True):
            self.assertTrue(lun['size'] == lunOldSize)
            LOG.info("LUN '%s': size %s is intact." % (lun['name'], lun['size']))

    def test_terminal_size(self):
        """
            Test verifies LUN resizing to minimum and maximum sizes respecting given size unit.
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

            LOG.step("Creating LUNs with size unit '%s'" % sizeUnit)
            if sizeUnit not in ['B', 'K']:
                self.marscluster.lun.create(name=nameLow, size='0.5k')
            self.marscluster.lun.create(name=nameHigh, size='0.5k')
            luns = self.marscluster.lun.show(json=True)
            LOG.info('LUNs created:\n', luns)

            # Refresh LUN grid
            self.lunsPage.btnRefresh.click()
            self.lunsPage.btnRefresh.waitUntilEnabled()

            # Skip assigning the same size with low size units. Reducing LUN size is not available.
            if sizeUnit not in ['B', 'K']:
                LOG.step("Opening wizard for LUN '%s'" % nameLow)
                wizard = ResizeLUNWizard(driver=self.driver, locale=self.locale)
                wizard.open(name=nameLow)
                LOG.info('Wizard opened.')

                LOG.step("Modifying LUN size to be minimal: size='%s'" % sizeLow)
                wizard.activePage.resizeLUN(size=sizeLow)
                wizard.activePage.submit()
                LOG.info('Resize submitted.')

                sizeToCreate = sizes[sizeUnit]['low'] * sizes[sizeUnit]['multiplier']
                # Sizes of LUNs are rounded up to 512-byte bound
                if sizeToCreate % 512 > 0:
                    sizeToCreate = int(sizeToCreate / 512) * 512 + 512
                lunsToCreate[nameLow] = sizeToCreate

            LOG.step("Opening wizard for LUN '%s'" % nameHigh)
            wizard = ResizeLUNWizard(driver=self.driver, locale=self.locale)
            wizard.open(name=nameHigh)
            LOG.info('Wizard opened.')

            LOG.step("Modifying LUN size to be maximal: size='%s'" % sizeHigh)
            wizard.activePage.resizeLUN(size=sizeHigh)
            wizard.activePage.submit()
            LOG.info('Resize submitted.')

            lunsToCreate[nameHigh] = sizes[sizeUnit]['high'] * sizes[sizeUnit]['multiplier']
            createdLUNs = self.marscluster.lun.show(json=True)

            LOG.step('Verifying modified LUN size is as specified')
            for lun in createdLUNs:
                self.assertTrue(lun['size'] == lunsToCreate[lun['name']])
                LOG.info("Size of LUN '%s' (bytes): %s" % (lun['name'], lun['size']))

            LOG.step('Cleaning up LUNs')
            luns = express.Luns(node=self.marscluster, cleanup=True)
            del luns
            LOG.info('LUNs destroyed.')

    def test_same_size(self):
        """
            Verify error message on LUN resizing with the same (initial) size.
            Verify LUN size remain intact.
        """
        LOG.step('Creating LUN')
        lunName = 'LuN'
        lunSize = 104857600
        self.marscluster.lun.create(name=lunName, size=lunSize)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Setting same LUN size in dialog')
        wizard = ResizeLUNWizard(driver=self.driver, locale=self.locale)
        wizard.open(name=lunName)
        wizard.resizeLUNPage.resizeLUN(size=str(lunSize) + 'B')
        LOG.info('New LUN size:', wizard.resizeLUNPage.txtSize.getText() +
            wizard.resizeLUNPage.dLstSizeUnit.getText())
        wizard.activePage.btnOK.click()

        LOG.info('Dialog title notifies failure:', wizard.activePage.lblTitle.getText())
        self.assertTrue(wizard.activePage.lblSameSizeError.isVisible())
        LOG.info('Error message displayed:', wizard.activePage.lblSameSizeError.getText())
        self.assertFalse(wizard.activePage.btnOK.isEnabled())
        LOG.info("Button 'OK' is enabled:", wizard.activePage.btnOK.isEnabled())

        LOG.step('Canceling dialog')
        wizard.cancel()
        LOG.info('Dialog closed.')

        LOG.step('Verifying no change have been made for LUN size')
        luns = self.marscluster.lun.show(json=True)
        self.assertTrue(len(luns) == 1)
        self.assertTrue(luns[0]['size'] == lunSize)
        LOG.info("LUN '%s': size %s is intact." % (luns[0]['name'], luns[0]['size']))

    def test_dialog_cancel(self):
        """
            Verify LUN size remains intact on dialog canceling.
        """
        LOG.step('Creating LUNs')
        lunCount = 3
        lunOldSize = 104857600
        lunNamePrefix = 'LuN'
        lunNewSize = '1t'
        self.luns.create(count=lunCount, size=lunOldSize, prefix=lunNamePrefix)
        LOG.info('LUNs created:\n', self.marscluster.lun.show(json=True))

        # Refresh LUN grid
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()

        LOG.step('Setting new LUN size in dialog')
        wizard = ResizeLUNWizard(driver=self.driver, locale=self.locale)
        wizard.open(name=lunNamePrefix + '_1')
        wizard.resizeLUNPage.resizeLUN(size=lunNewSize)
        LOG.info('New LUN size:', wizard.resizeLUNPage.txtSize.getText() +
            wizard.resizeLUNPage.dLstSizeUnit.getText())

        LOG.step('Canceling dialog')
        wizard.cancel()
        LOG.info('Dialog closed.')

        LOG.step('Verifying no changes have been made for LUNs sizes')
        self.lunsPage.btnRefresh.click()
        self.lunsPage.btnRefresh.waitUntilEnabled()
        for lun in self.marscluster.lun.show(json=True):
            self.assertTrue(lun['size'] == lunOldSize)
            LOG.info("LUN '%s': size %s is intact." % (lun['name'], lun['size']))

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
    testResizeLUNWizard = TestResizeLUNWizard()
    sys.exit(testResizeLUNWizard.numberOfFailedTests())
