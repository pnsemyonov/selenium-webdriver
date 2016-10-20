#!/usr/bin/env python

purpose = """Unit test of Create LUNs Wizard"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../.."))

import time
import express
from selenium.webdriver.common.keys import Keys
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
    default='en',
    help="Locale: 'en' (English), 'es' (Spanish), 'de' (German), 'fr' (French), 'ja' (Japanese), 'ko' (Korean), 'zh' (Chinese)")

ARGS.parser.add_argument(
    '--username', type=str,
    default='admin',
    help="Administrator's name on Mars controller")

ARGS.parser.add_argument(
    '--password', type=str,
    default='changeme',
    help="Administrator's password on Mars controller")

class TestCreateLUNsWizard(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.webUIHostName = getFQDN(self.mars[0].hostname)

    def testSetup(self):
        self.driver = self.getDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.headerPage = HeaderPage(driver=self.driver)
        self.allStoragePage = AllStoragePage(driver=self.driver)
        self.lunsPage = LUNsPage(driver=self.driver)

        self.loginPage.signIn(username=self.username, password=self.password)

    def test_wizard_create_luns_define_single_lun_no_input(self):
        title = 'Create LUNs'
        stepDescription = 'Step 1 of 2: Define LUN properties'
        numberOfLUNs = '1'
        namePlaceholder = 'Enter LUN Name'
        sizePlaceholder = 'Enter LUN Size'
        sizeUnit = 'GiB'
        consistencyGroupDescription = 'A consistency group allows you to back up and clone multiple LUNs as a group.'

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()

        LOG.step('Verifying title of front page')
        self.assertTrue(wizard.activePage.lblTitle.getText() == title)
        LOG.info('Title:', wizard.activePage.lblTitle.getText())

        LOG.step('Verifying step description of front page')
        self.assertTrue(wizard.activePage.lblStepDescription.getText() == stepDescription)
        LOG.info('Step description:', wizard.activePage.lblStepDescription.getText())

        LOG.step('Verifying default number of LUNs')
        self.assertTrue(wizard.activePage.dLstNumberOfLUNs.getText() == numberOfLUNs)
        LOG.info('Number of LUNs:', wizard.activePage.dLstNumberOfLUNs.getText())

        LOG.step('Verifying default LUN name (blank)')
        self.assertTrue(wizard.activePage.txtName.getText() == '')
        self.assertTrue(wizard.activePage.txtName.getAttribute(attributeName='placeholder') ==
            namePlaceholder)
        LOG.info('LUN name:', "'", wizard.activePage.txtName.getText(), "'")
        LOG.info('LUN name placeholder:',
            wizard.activePage.txtName.getAttribute(attributeName='placeholder'))

        LOG.step('Verifying default LUN size (blank)')
        self.assertTrue(wizard.activePage.txtSize.getText() == '')
        self.assertTrue(wizard.activePage.txtSize.getAttribute(attributeName='placeholder') ==
            sizePlaceholder)
        LOG.info('LUN size:', "'", wizard.activePage.txtSize.getText(), "'")
        LOG.info('LUN size placeholder:',
            wizard.activePage.txtSize.getAttribute(attributeName='placeholder'))

        LOG.step('Verifying default LUN size unit')
        self.assertTrue(wizard.activePage.dLstSizeUnit.getText() == sizeUnit)
        LOG.info('LUN size unit:', wizard.activePage.dLstSizeUnit.getText())

        LOG.step("Verifying default state of check box 'Add to a consistency group'")
        self.assertFalse(wizard.activePage.chkAddToConsistencyGroup.isSelected())
        LOG.info('Check box is selected:', wizard.activePage.chkAddToConsistencyGroup.isSelected())

        LOG.step('Verifying consistency group description')
        self.assertTrue(wizard.activePage.lblConsistencyGroupDescription.getText() ==
        consistencyGroupDescription)
        LOG.info('Description:', wizard.activePage.lblConsistencyGroupDescription.getText())

        LOG.step("Verifying button 'Next' state")
        self.assertFalse(wizard.activePage.btnNext.isEnabled())
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step("Verifying button 'Cancel' state")
        self.assertTrue(wizard.activePage.btnCancel.isEnabled())
        LOG.info("Button 'Cancel' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

    def test_wizard_create_luns_define_single_lun_input_check(self):
        # TODO: File a bug 'This field is required' -> 'Name: This field is required'
        nameErrorBlank = 'This field is required'
        sizeErrorBlank = 'Size: This field is required'
        # TODO: File a bug error message has end point while other messages do not.
        sizeErrorLimit = 'Size: LUN size must be between 512 bytes and 64 TiB.'
        lowerInvalidBoundarySize = '511'
        lowerValidBoundarySize = '512'
        higherValidBoundarySize = pow(1024, 4) * 64
        higherInvalidBoundarySize = pow(1024, 4) * 64 + 1

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Wizard landed on front page.')

        LOG.step('Verifying no error messages on page by default.')
        self.assertFalse(wizard.activePage.lblNameError.isPresent() and wizard.activePage.lblNameError.isVisible())
        LOG.info('LUN name error message is not visible on page.')
        self.assertFalse(wizard.activePage.lblSizeError.isPresent() and wizard.activePage.lblSizeError.isVisible())
        LOG.info('LUN size error message is not visible on page.')

        LOG.step('Verifying error message on moving focus off LUN name text box')
        wizard.activePage.txtName.setFocus()
        wizard.activePage.txtSize.setFocus()
        wizard.activePage.lblNameError.waitUntilPresent()
        self.assertTrue(wizard.activePage.lblNameError.isVisible())
        LOG.info('LUN name error message is visible on page.')
        wizard.activePage.lblSizeError.waitUntilAbsent()
        LOG.info('LUN size error message is not visible on page.')

        LOG.step('Verifying error message on moving focus off LUN size text box')
        wizard.activePage.txtName.setFocus()
        wizard.activePage.lblNameError.waitUntilPresent()
        self.assertTrue(wizard.activePage.lblNameError.isVisible())
        LOG.info('LUN name error message is visible on page.')
        wizard.activePage.lblSizeError.waitUntilPresent()
        self.assertTrue(wizard.activePage.lblSizeError.isVisible())
        LOG.info('LUN size error message is visible on page.')

        LOG.step('Verifying LUN size error message on size not in between %s B and %s TiB' % (lowerValidBoundarySize,
        higherValidBoundarySize / pow(1024, 4)))
        wizard.activePage.dLstSizeUnit.select(item='B')
        wizard.activePage.txtSize.setText(text=lowerInvalidBoundarySize)
        wizard.activePage.lblSizeError.waitUntilPresent()
        wizard.activePage.lblSizeError.waitUntilText(text=sizeErrorLimit)
        LOG.info("Size: %s B: '%s'" % (lowerInvalidBoundarySize, wizard.activePage.lblSizeError.getText()))

        wizard.activePage.txtSize.clear()
        wizard.activePage.txtSize.setText(text=lowerValidBoundarySize)
        wizard.activePage.lblSizeError.waitUntilAbsent()
        LOG.info('Size: %s B: No error.' % lowerValidBoundarySize)

        wizard.activePage.txtSize.clear()
        wizard.activePage.txtSize.setText(text=higherValidBoundarySize)
        wizard.activePage.lblSizeError.waitUntilAbsent()
        LOG.info('Size: %s B: No error.' % higherValidBoundarySize)

        wizard.activePage.txtSize.clear()
        wizard.activePage.txtSize.setText(text=higherInvalidBoundarySize)
        wizard.activePage.lblSizeError.waitUntilPresent()
        self.assertTrue(wizard.activePage.lblSizeError.isVisible() and wizard.activePage.lblSizeError.getText() ==
        sizeErrorLimit)
        LOG.info("Size: %s B: '%s'" % (higherInvalidBoundarySize, wizard.activePage.lblSizeError.getText()))

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

    def test_wizard_create_luns_define_multiple_luns_auto_no_input(self):
        numberOfLUNs = '3'
        prefixPlaceholder = 'Enter Prefix'
        suffix = '## (01, 02, ...)'
        startAt = '1'
        # TODO: File a bug 'Enter size' -> 'Enter Size'
        sizePlaceholder = 'Enter size'
        sizeUnit = 'GiB'

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()

        LOG.step('Selecting multiple LUNs')
        wizard.activePage.dLstNumberOfLUNs.select(item=numberOfLUNs)
        self.assertTrue(wizard.activePage.dLstNumberOfLUNs.getText() == str(numberOfLUNs))
        LOG.info('Number of LUNs:', wizard.activePage.dLstNumberOfLUNs.getText())

        LOG.step('Verifying LUN name and size auto-definition is selected by default')
        self.assertTrue(wizard.activePage.rBtnAutoNameAndSize.isSelected())
        LOG.info('LUN name and size auto-definition is selected:', wizard.activePage.rBtnAutoNameAndSize.isSelected())

        LOG.step('Verifying LUN name and size manual definition is unselected by default')
        self.assertFalse(wizard.activePage.rBtnManuallyNameAndSize.isSelected())
        LOG.info('LUN name and size manual definition is selected:',
        wizard.activePage.rBtnManuallyNameAndSize.isSelected())

        LOG.step('Verifying default LUN name prefix (blank)')
        self.assertTrue(wizard.activePage.txtPrefix.getText() == '')
        self.assertTrue(wizard.activePage.txtPrefix.getAttribute(attributeName='placeholder') ==
            prefixPlaceholder)
        LOG.info('LUN name prefix:', wizard.activePage.txtPrefix.getText())
        LOG.info('LUN name prefix placeholder:',
            wizard.activePage.txtPrefix.getAttribute(attributeName='placeholder'))

        LOG.step("Verifying default LUN name suffix ('%s')" % suffix)
        self.assertTrue(wizard.activePage.dLstSuffix.getText() == suffix)
        LOG.info('LUN name suffix:', wizard.activePage.dLstSuffix.getText())

        LOG.step('Verifying LUN name suffix start')
        self.assertTrue(wizard.activePage.txtStartAt.getText() == startAt)
        LOG.info('LUN name suffix starts at:', wizard.activePage.txtStartAt.getText())

        LOG.step('Verifying default LUN size (blank)')
        self.assertTrue(wizard.activePage.txtAutoSize.getText() == '')
        self.assertTrue(wizard.activePage.txtAutoSize.getAttribute(attributeName='placeholder') ==
            sizePlaceholder)
        LOG.info('LUN size:', "'", wizard.activePage.txtAutoSize.getText(), "'")
        LOG.info('LUN size placeholder:',
            wizard.activePage.txtAutoSize.getAttribute(attributeName='placeholder'))

        LOG.step("Verifying default LUN size unit ('%s')" % sizeUnit)
        self.assertTrue(wizard.activePage.dLstAutoSizeUnit.getText() == sizeUnit)
        LOG.info('LUN size unit:', wizard.activePage.dLstAutoSizeUnit.getText())

        LOG.step("Verifying button 'Next' state")
        self.assertFalse(wizard.activePage.btnNext.isEnabled())
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step("Verifying button 'Cancel' state")
        self.assertTrue(wizard.activePage.btnCancel.isEnabled())
        LOG.info("Button 'Cancel' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

    def test_wizard_create_luns_define_multiple_luns_auto_input_check(self):
        numberOfLUNs = '3'
        prefix = 'LUN'
        sizeErrorBlank = 'Size: This field is required'
        sizeErrorLimit = 'Size: LUN size must be between 512 bytes and 64 TiB.'
        lowerInvalidBoundarySize = '511'
        lowerValidBoundarySize = '512'
        higherValidBoundarySize = pow(1024, 4) * 64
        higherInvalidBoundarySize = pow(1024, 4) * 64 + 1
        # TODO: File a bug to remove space before colon
        defaultPreview = 'Preview : 01'
        customPrefix = 'LuN'
        customSuffix = '####'
        customStartAt = 50

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Wizard landed on LUN definition page.')

        LOG.step('Selecting multiple LUNs')
        wizard.activePage.dLstNumberOfLUNs.select(item=numberOfLUNs)
        self.assertTrue(wizard.activePage.dLstNumberOfLUNs.getText() == str(numberOfLUNs))
        LOG.info('Number of LUNs:', wizard.activePage.dLstNumberOfLUNs.getText())

        LOG.step('Selecting LUN name and size auto-definition')
        wizard.activePage.rBtnAutoNameAndSize.select()
        self.assertTrue(wizard.activePage.rBtnAutoNameAndSize.isSelected())
        LOG.info('LUN name and size auto-definition is selected:', wizard.activePage.rBtnAutoNameAndSize.isSelected())

        LOG.step('Verifying no LUN size error message by default')
        self.assertFalse(wizard.activePage.lblAutoSizeError.isPresent())
        LOG.info('LUN size error message is not visible.')

        LOG.step('Verifying LUN size error message show up on text box clearance')
        wizard.activePage.txtAutoSize.sendKeys('1')
        time.sleep(.5)
        wizard.activePage.txtAutoSize.sendKeys(Keys.BACK_SPACE)
        wizard.activePage.lblAutoSizeError.waitUntilPresent()
        wizard.activePage.lblAutoSizeError.waitUntilText(text=sizeErrorBlank)
        LOG.info('LUN size error message is visible.')

        LOG.step('Verifying LUN size error message on size not in between %s B and %s TiB' % (lowerValidBoundarySize,
        higherValidBoundarySize / pow(1024, 4)))
        wizard.activePage.dLstAutoSizeUnit.select(item='B')
        wizard.activePage.txtAutoSize.setText(text=lowerInvalidBoundarySize)
        wizard.activePage.lblAutoSizeError.waitUntilPresent()
        wizard.activePage.lblAutoSizeError.waitUntilText(text=sizeErrorLimit)
        LOG.info("Size: %s B: '%s'" % (lowerInvalidBoundarySize, wizard.activePage.lblAutoSizeError.getText()))

        wizard.activePage.txtAutoSize.clear()
        wizard.activePage.txtAutoSize.setText(text=lowerValidBoundarySize)
        wizard.activePage.lblAutoSizeError.waitUntilAbsent()
        LOG.info('Size: %s B: No error.' % lowerValidBoundarySize)

        wizard.activePage.txtAutoSize.clear()
        wizard.activePage.txtAutoSize.setText(text=higherValidBoundarySize)
        wizard.activePage.lblAutoSizeError.waitUntilAbsent()
        LOG.info('Size: %s B: No error.' % higherValidBoundarySize)

        wizard.activePage.txtAutoSize.clear()
        wizard.activePage.txtAutoSize.setText(text=higherInvalidBoundarySize)
        wizard.activePage.lblAutoSizeError.waitUntilPresent()
        LOG.info("Size: %s B: '%s'" % (wizard.activePage.txtAutoSize.getText(),
        wizard.activePage.lblAutoSizeError.getText()))
        self.assertTrue(wizard.activePage.lblAutoSizeError.isVisible() and
        wizard.activePage.lblAutoSizeError.getText() == sizeErrorLimit)
        LOG.info("Size: %s B: '%s'" % (higherInvalidBoundarySize, wizard.activePage.lblAutoSizeError.getText()))

        LOG.step('Verifying auto-name default preview')
        self.assertTrue(wizard.activePage.lblPreview.getText() == defaultPreview)
        LOG.info('Auto-name default preview:', wizard.activePage.lblPreview.getText())

        LOG.step('Verifying auto-name custom preview')
        wizard.activePage.txtPrefix.setText(text=customPrefix)
        LOG.info('Custom prefix:', customPrefix)
        wizard.activePage.dLstSuffix.select(item=customSuffix, exact=False)
        LOG.info('Custom suffix:', customSuffix)
        wizard.activePage.txtStartAt.clear()
        wizard.activePage.txtStartAt.setText(text=customStartAt)
        LOG.info('Custom number starts at:', customStartAt)
        customName = customPrefix + str(customStartAt).rjust(len(customSuffix), '0')
        wizard.activePage.lblPreview.waitUntilText(text=customName)
        self.assertTrue(wizard.activePage.lblPreview.getText() == ('Preview : ' + customName))
        LOG.info('Auto-name custom preview:', wizard.activePage.lblPreview.getText())

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

    def test_wizard_create_luns_define_multiple_luns_manually_no_input(self):
        numberOfLUNs = 2
        namePlaceholder = 'Enter LUN Name'
        sizePlaceholder = 'Enter LUN Size'

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Wizard landed on LUN definition page.')

        LOG.step('Selecting multiple LUNs')
        wizard.activePage.dLstNumberOfLUNs.select(item=str(numberOfLUNs))
        self.assertTrue(wizard.activePage.dLstNumberOfLUNs.getText() == str(numberOfLUNs))
        LOG.info('Number of LUNs:', wizard.activePage.dLstNumberOfLUNs.getText())

        LOG.step('Selecting LUN name and size manual definition')
        wizard.activePage.rBtnManuallyNameAndSize.select()

        LOG.step('Verifying LUN name and size default values')
        for lunIndex in range(1, numberOfLUNs + 1):
            LOG.info('LUN index:', lunIndex)

            txtName = textbox.TextBox(driver=self.driver,
            selector=wizard.activePage.selectors.txtManuallyName(index=lunIndex))
            self.assertFalse(txtName.getText())
            LOG.info("Name: '%s'" % txtName.getText())
            self.assertTrue(txtName.getAttribute(attributeName='placeholder') == namePlaceholder)
            LOG.info('Name placeholder:', txtName.getAttribute(attributeName='placeholder'))

            txtSize = textbox.TextBox(driver=self.driver,
            selector=wizard.activePage.selectors.txtManuallySize(index=lunIndex))
            self.assertFalse(txtSize.getText())
            LOG.info("Size: '%s'" % txtSize.getText())
            self.assertTrue(txtSize.getAttribute(attributeName='placeholder') == sizePlaceholder)
            LOG.info('Size placeholder:', txtSize.getAttribute(attributeName='placeholder'))

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

    def test_wizard_create_luns_define_multiple_luns_manually_input_check(self):
        numberOfLUNs = 2
        nameErrorBlank = 'This field is required'
        sizeErrorBlank = 'Size: This field is required'

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Wizard landed on LUN definition page.')

        LOG.step('Selecting multiple LUNs')
        wizard.activePage.dLstNumberOfLUNs.select(item=str(numberOfLUNs))
        self.assertTrue(wizard.activePage.dLstNumberOfLUNs.getText() == str(numberOfLUNs))
        LOG.info('Number of LUNs:', wizard.activePage.dLstNumberOfLUNs.getText())

        LOG.step('Selecting LUN name and size manual definition')
        wizard.activePage.rBtnManuallyNameAndSize.select()

        LOG.step('Verifying error messages on moving off LUN name and size text boxes')
        for lunIndex in range(1, numberOfLUNs + 1):
            LOG.info('LUN index:', lunIndex)

            lblNameError = label.Label(driver=self.driver,
            selector=wizard.activePage.selectors.lblManuallyNameError(index=lunIndex))
            lblSizeError = label.Label(driver=self.driver,
            selector=wizard.activePage.selectors.lblManuallySizeError(index=lunIndex))
            self.assertFalse(lblNameError.isPresent() and lblNameError.isVisible())
            LOG.info('LUN name error message is not visible.')
            self.assertFalse(lblSizeError.isPresent() and lblSizeError.isVisible())
            LOG.info('LUN size error message is not visible.')

            txtName = textbox.TextBox(driver=self.driver,
            selector=wizard.activePage.selectors.txtManuallyName(index=lunIndex))
            txtSize = textbox.TextBox(driver=self.driver,
            selector=wizard.activePage.selectors.txtManuallySize(index=lunIndex))

            txtName.setFocus()
            txtSize.setFocus()
            txtName.setFocus()

            LOG.info('Error messages triggered.')
            lblNameError.waitUntilText(text=nameErrorBlank)
            LOG.info('LUN name error message:', lblNameError.getText())
            lblSizeError.waitUntilText(text=sizeErrorBlank)
            LOG.info('LUN size error message:', lblSizeError.getText())

        LOG.step("Verifying button 'Next' is disabled when LUN properties undefined")
        self.assertFalse(wizard.activePage.btnNext.isEnabled())
        LOG.info("Button 'Cancel' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step('Verifying error messages disappear when LUN properties defined')
        for lunIndex in range(1, numberOfLUNs + 1):
            LOG.info('LUN index:', lunIndex)

            txtName = textbox.TextBox(driver=self.driver,
            selector=wizard.activePage.selectors.txtManuallyName(index=lunIndex))
            txtSize = textbox.TextBox(driver=self.driver,
            selector=wizard.activePage.selectors.txtManuallySize(index=lunIndex))

            txtName.setText(text=('LuN-' + str(lunIndex)))
            LOG.info('LUN name:', txtName.getText())
            txtSize.setText(text=lunIndex)
            LOG.info('LUN size:', txtSize.getText())

            lblNameError = label.Label(driver=self.driver,
            selector=wizard.activePage.selectors.lblManuallyNameError(index=lunIndex))
            lblSizeError = label.Label(driver=self.driver,
            selector=wizard.activePage.selectors.lblManuallySizeError(index=lunIndex))

            lblNameError.waitUntilAbsent()
            LOG.info('LUN name error message is not visible.')
            lblSizeError.waitUntilAbsent()
            LOG.info('LUN size error message is not visible.')

        LOG.step("Verifying button 'Next' is enabled")
        self.assertTrue(wizard.activePage.btnNext.isEnabled())
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.activePage.isOpen())
        LOG.info('Front page is open:', wizard.activePage.isOpen())

    def test_wizard_create_luns_define_single_lun_manually_add_to_consistency_group_no_input(self):
        lunName = 'LuN-1'
        lunSize = 1
        newConsistencyGroup = 'Enter consistency group name'
        consistencyGroupError = 'Select parent consistency group or enter new consistency group or provide both of them.'
        newConsistencyGroupName = 'CG-New'
        newConsistencyGroupConfirmation = 'New consistency group: '

        self.deleteConsistencyGroups()

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Wizard landed on LUN definition page.')

        LOG.step('Defining LUN properties')
        wizard.activePage.txtName.setText(text=lunName)
        LOG.info('LUN name:', wizard.activePage.txtName.getText())
        wizard.activePage.txtSize.setText(text=lunSize)
        LOG.info('LUN size:', wizard.activePage.txtSize.getText())

        LOG.step('Enabling CG mapping')
        wizard.activePage.chkAddToConsistencyGroup.select()
        self.assertTrue(wizard.activePage.chkAddToConsistencyGroup.isSelected())
        LOG.info("Check box 'Add to a consistency group' is selected.")

        LOG.step('Verifying parent group is None')
        self.assertTrue(wizard.activePage.cBoxParentConsistencyGroup.getText() == 'None')
        LOG.info('Parent consistency group:', wizard.activePage.cBoxParentConsistencyGroup.getText())

        LOG.step('Verifying consistency group default settings')
        self.assertFalse(wizard.activePage.txtNewConsistencyGroup.getText())
        LOG.info("New consistency group text box value: '%s'",
            wizard.activePage.txtNewConsistencyGroup.getText())
        self.assertTrue(wizard.activePage.txtNewConsistencyGroup.getAttribute(attributeName='placeholder')
            == newConsistencyGroup)
        LOG.info('New consistency group text box placeholder:',
        wizard.activePage.txtNewConsistencyGroup.getAttribute(attributeName='placeholder'))

        LOG.step('Verifying consistency group error message when text box in dirty state')
        wizard.activePage.txtNewConsistencyGroup.setFocus()
        wizard.activePage.cBoxParentConsistencyGroup.element.click()
        self.assertTrue(wizard.activePage.lblConsistencyGroupError.isPresent() and
        wizard.activePage.lblConsistencyGroupError.isVisible() and
        wizard.activePage.lblConsistencyGroupError.getText() == consistencyGroupError)
        LOG.info('Consistency group error message is present:', wizard.activePage.lblConsistencyGroupError.isPresent())
        LOG.info('Consistency group error message is visible:',
        wizard.activePage.lblConsistencyGroupError.isVisible())
        LOG.info('Consistency group error message:', wizard.activePage.lblConsistencyGroupError.getText())

        LOG.step("Verifying button 'Next' availability")
        self.assertFalse(wizard.activePage.btnNext.isEnabled())
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step('Specifying new consistency group')
        wizard.activePage.txtNewConsistencyGroup.setText(text=newConsistencyGroupName)
        LOG.info('New consistency group:', wizard.activePage.txtNewConsistencyGroup.getText())

        LOG.step("Verifying error message disappeared and button 'Next' enabled")
        time.sleep(.5)
        self.assertFalse(wizard.activePage.lblConsistencyGroupError.isPresent())
        LOG.info('Consistency group error message is present:', wizard.activePage.lblConsistencyGroupError.isPresent())
        self.assertTrue(wizard.activePage.btnNext.isEnabled())
        LOG.info("Button 'Next' is enabled:", wizard.activePage.btnNext.isEnabled())

        LOG.step('Navigating to confirmation page')
        wizard.goNext()
        wizard.goNext()
        self.assertTrue(wizard.confirmPage.isOpen())
        LOG.info('Confirmation page is open:', wizard.confirmPage.isOpen())

        LOG.step('Verifying new consistency group is presented on confirmation page')
        self.assertTrue(wizard.activePage.lblNewConsistencyGroup.isPresent())
        LOG.info('New consistency group is present:', wizard.activePage.lblNewConsistencyGroup.isPresent())
        self.assertTrue(wizard.activePage.lblNewConsistencyGroup.isVisible())
        LOG.info('New consistency group is visible:', wizard.activePage.lblNewConsistencyGroup.isVisible())
        self.assertTrue(wizard.activePage.lblNewConsistencyGroup.getText() == (newConsistencyGroupConfirmation +
        newConsistencyGroupName))
        LOG.info('New consistency group confirmation text:', wizard.activePage.lblNewConsistencyGroup.getText())

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        self.assertTrue(wizard.activePage.btnCancel.isEnabled())
        LOG.info("Button 'Cancel' is enabled:", wizard.activePage.btnCancel.isEnabled())
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.confirmPage.isOpen())
        LOG.info('Confirmation page is open:', wizard.confirmPage.isOpen())

        LOG.step('Deleting Consistency groups')
        self.deleteConsistencyGroups()
        LOG.info('Consistency groups deleted.')

    def test_wizard_create_luns_define_multiple_luns_auto_map_to_initiator_group(self):
        numberOfLUNs = 5
        prefix = 'LuN'
        lunSize = 3
        initiatorGroupNames = ['IG-1', 'IG-2', 'IG-3', 'IG-4', 'IG-5', 'IG-6', 'IG-7']
        numberOfFilteredGroups = 5

        LOG.step('Deleting initiator groups')
        self.mars[0].lun.unmapAll()
        self.mars[0].igroup.destroyAll()
        self.assertFalse(self.mars[0].igroup.show(json=True))
        LOG.info('Initiator groups:\n', self.mars[0].igroup.show(json=True))

        LOG.step('Creating new initiator groups')
        initiators = self.mars[0].fcp.initiator_show(json=True)
        for groupName in initiatorGroupNames:
            self.mars[0].igroup.create(name=groupName, ostype='linux', initiators=initiators[0]['wwpn'])
        LOG.info('Initiator groups:\n', self.mars[0].igroup.show(json=True))

        LOG.step('Creating wizard')
        wizard = CreateLUNsWizard(driver=self.driver)

        LOG.step('Opening front page of dialog')
        wizard.open()
        self.assertTrue(wizard.defineLUNsPage.isOpen())
        LOG.info('Wizard landed on LUN definition page.')

        LOG.step('Selecting multiple LUNs')
        wizard.activePage.dLstNumberOfLUNs.select(item=str(numberOfLUNs))
        self.assertTrue(wizard.activePage.dLstNumberOfLUNs.getText() == str(numberOfLUNs))
        LOG.info('Number of LUNs:', wizard.activePage.dLstNumberOfLUNs.getText())

        LOG.step('Selecting LUN name and size auto-definition')
        wizard.activePage.rBtnAutoNameAndSize.select()
        self.assertTrue(wizard.activePage.rBtnAutoNameAndSize.isSelected())
        LOG.info('LUN name and size auto-definition is selected:', wizard.activePage.rBtnAutoNameAndSize.isSelected())

        LOG.step('Setting LUN properties')
        wizard.activePage.txtPrefix.setText(text=prefix)
        LOG.info('Custom prefix:', prefix)
        wizard.activePage.txtAutoSize.setText(text=lunSize)
        LOG.info('LUN size:', lunSize)

        LOG.step('Navigating to initiator group selection page')
        wizard.goNext()
        self.assertTrue(wizard.selectInitiatorGroupsPage.isOpen())
        LOG.info('Initiator group selection page is open:', wizard.selectInitiatorGroupsPage.isOpen())

        LOG.step('Verifying initiator groups in grid')
        gridRows = wizard.activePage.gridInitiatorGroups.find()
        LOG.info('Grid rows:\n', gridRows)
        self.assertTrue(len(gridRows) == len(initiatorGroupNames))
        LOG.info('Number of resulting rows (%s) == number of provided group names (%s)' % (len(gridRows),
        len(initiatorGroupNames)))
        for row in gridRows:
            self.assertTrue(row['initiator_groups'] in initiatorGroupNames)
            LOG.info("Grid: Initiator group '%s' found in provided group names." % row['initiator_groups'])

        LOG.step('Selecting 2 first rows')
        wizard.activePage.gridInitiatorGroups.select(initiator_groups=initiatorGroupNames[:numberOfFilteredGroups])
        selectedRows = wizard.activePage.gridInitiatorGroups.find(selected=True)
        LOG.info('Selected rows:\n', selectedRows)

        LOG.step('Verifying only selected rows are visible')
        wizard.activePage.chkShowOnlySelectedInitiatorGroups.select()
        self.assertTrue(wizard.activePage.chkShowOnlySelectedInitiatorGroups.isSelected())
        LOG.info('Filtering check box is selected:', wizard.activePage.chkShowOnlySelectedInitiatorGroups.isSelected())
        visibleRows = wizard.activePage.gridInitiatorGroups.find()
        LOG.info('Visible grid rows (groups):\n', visibleRows)
        self.assertTrue(len(visibleRows) == numberOfFilteredGroups)
        LOG.info('Number of visible rows (%s) == provided one (%s)' % (len(visibleRows), numberOfFilteredGroups))

        LOG.step('Navigating to confirmation page')
        wizard.goNext()
        self.assertTrue(wizard.confirmPage.isOpen())
        LOG.info('Confirmation page is open:', wizard.confirmPage.isOpen())

        LOG.step('Verifying LUN mapping in grid on confirmation page')
        lunRows = wizard.activePage.gridLUNs.find()
        LOG.info('Rows to confirm:\n', lunRows)
        self.assertTrue(len(lunRows) == numberOfLUNs)
        LOG.info('Number of LUN rows in grid (%s) == provided number of LUNs (%s)' % (len(lunRows), numberOfLUNs))
        selectedGroups = [row['initiator_groups'] for row in selectedRows]
        lunNames = [prefix + str(lunIndex).rjust(2, '0') for lunIndex in range(1, numberOfLUNs + 1)]
        for lunIndex in range(numberOfLUNs):
            self.assertTrue(lunRows[lunIndex]['name'] in lunNames)
            LOG.info("LUN '%s' is found in grid." % lunRows[lunIndex]['name'])
            for groupName in selectedGroups:
                self.assertTrue(groupName in lunRows[lunIndex]['mapped_to'])
                LOG.info('LUN mapping found in row:', groupName)

        LOG.step("Closing the dialog by clicking button 'Cancel'")
        wizard.activePage.btnCancel.click()

        LOG.step("Verifying the dialog has been closed")
        self.assertFalse(wizard.confirmPage.isOpen())
        LOG.info('Confirmation page is open:', wizard.activePage.isOpen())

        LOG.step('Deleting initiator groups')
        self.mars[0].lun.unmapAll()
        self.mars[0].igroup.destroyAll()
        self.assertFalse(self.mars[0].igroup.show(json=True))
        LOG.info('Initiator groups:\n', self.mars[0].igroup.show(json=True))

    def deleteConsistencyGroups(self):
        groups = self.mars[0].cg.show(json=True)
        for group in groups:
            self.mars[0].cg.delete(name=group['name'])

    def testTeardown(self):
        self.driver.quit()


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testCreateCreateLUNsWizard = TestCreateLUNsWizard()
    sys.exit(testCreateLUNsWizard.numberOfFailedTests())
