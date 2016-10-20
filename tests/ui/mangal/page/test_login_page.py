#!/usr/bin/env python

purpose = """Mangal UI login page components validation and login functionality"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))

from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.login_failed_page import LoginFailedPage

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
    '--invalidusername', type=str,
    default='nimda',
    help="Invalid administrator's name on Mars controller")

ARGS.parser.add_argument(
    '--password', type=str,
    default='changeme',
    help="Administrator's password on Mars controller")

ARGS.parser.add_argument(
    '--invalidpassword', type=str,
    default='emegnahc',
    help="Invalid administrator's password on Mars controller")


class TestLoginPage(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.invalidUsername = ARGS.values.invalidusername
        self.password = ARGS.values.password
        self.invalidPassword = ARGS.values.invalidpassword
        self.locale = ARGS.values.locale
        self.webUIHostName = getFQDN(self.marscluster.getMasterNode().hostname)

    def testSetup(self):
        self.driver = self.getDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.headerPage = HeaderPage(driver=self.driver)
        self.loginFailedPage = LoginFailedPage(driver=self.driver)

        LOG.step('Opening login page')
        self.loginPage.open()

        if self.locale is None:
            self.locale = self.loginPage.getRandomLocale()

        LOG.step('Selecting locale: %s' % self.locale)
        self.loginPage.selectLocale(locale=self.locale)
        LOG.info('Selected locale: %s' % self.locale)

    def test_validate_components(self):
        """
            This validates availability of components on login page.
        """
        supportLinkHRef = 'http://support.netapp.com/'
        productName = 'FlashRay System Manager'

        LOG.step('Validating help links availability')

        self.loginPage.linkHelp.waitUntilPresent()
        self.assertTrue(self.loginPage.linkHelp.isPresent())
        self.assertTrue(self.loginPage.linkHelp.isVisible())
        LOG.info('Help link available.')

        self.assertTrue(self.loginPage.linkSupport.isPresent())
        self.assertTrue(self.loginPage.linkSupport.isVisible())
        self.assertTrue(self.loginPage.linkSupport.getHref() == supportLinkHRef)
        LOG.info('Support link available.')

        self.assertTrue(self.loginPage.linkNetApp.isPresent())
        self.assertTrue(self.loginPage.linkNetApp.isVisible())
        LOG.info('Company page link available.')

        LOG.step('Validating company branding availability')

        self.assertTrue(self.loginPage.imgCompanyLogo.isPresent())
        self.assertTrue(self.loginPage.imgCompanyLogo.isVisible())
        LOG.info('Company logo available.')

        self.assertTrue(self.loginPage.lblProductName.isPresent())
        self.assertTrue(self.loginPage.lblProductName.isVisible())
        self.assertTrue(productName in self.loginPage.lblProductName.getText())
        LOG.info('Product name label available.')

        self.assertTrue(self.loginPage.lblProductVersion.isPresent())
        self.assertTrue(self.loginPage.lblProductVersion.isVisible())
        LOG.info('Product version label available.')

        LOG.step('Validating input controls availability')

        self.assertTrue(self.loginPage.lblUsername.isPresent())
        self.assertTrue(self.loginPage.lblUsername.isVisible())
        LOG.info('Username label available.')

        self.assertTrue(self.loginPage.lblPassword.isPresent())
        self.assertTrue(self.loginPage.lblPassword.isVisible())
        LOG.info('Password label available.')

        self.assertTrue(self.loginPage.txtUsername.isPresent())
        self.assertTrue(self.loginPage.txtUsername.isVisible())
        LOG.info('Username input box available.')

        self.assertTrue(self.loginPage.txtPassword.isPresent())
        self.assertTrue(self.loginPage.txtPassword.isVisible())
        LOG.info('Password input box available.')

        self.assertTrue(self.loginPage.btnSignIn.isPresent())
        self.assertTrue(self.loginPage.btnSignIn.isVisible())
        LOG.info('Sign-in button available.')

        self.assertTrue(self.loginPage.menuLocale.isPresent())
        self.assertTrue(self.loginPage.menuLocale.isVisible())
        self.assertTrue(self.loginPage.menuLocale.isEnabled())
        LOG.info('Locale selection menu available.')

    def test_valid_login(self):
        LOG.step('Typing username')

        self.loginPage.txtUsername.setText(self.username)
        self.assertTrue(self.loginPage.txtUsername.getText() == self.username)
        LOG.info('Username:', self.loginPage.txtUsername.getText())

        LOG.step('Typing password')

        self.loginPage.txtPassword.waitUntilPresent()
        self.loginPage.txtPassword.setText(self.password)
        self.assertTrue(self.loginPage.txtPassword.getText() == self.password)
        LOG.info('Password:', self.loginPage.txtPassword.getText())

        LOG.step("Clicking on button 'Sign In'")

        self.loginPage.btnSignIn.waitUntilEnabled()
        self.loginPage.btnSignIn.click()

        LOG.step("Expecting button 'Manager' on header page")

        self.headerPage.btnManager.waitUntilPresent()
        self.assertTrue(self.headerPage.btnManager.isPresent())
        self.assertTrue(self.headerPage.btnManager.isEnabled())
        self.assertTrue(self.headerPage.btnManager.isVisible())
        LOG.info("Button 'Manager' is present on web page.")

        LOG.step('Logging out web page')

        self.headerPage.menuUser.select(item='Sign Out')
        self.loginPage.waitUntilLoaded()

        LOG.step('Verifying login page is open')
        self.loginPage.lblProductName.waitUntilPresent()
        self.assertTrue(self.loginPage.lblProductName.isPresent())
        self.assertTrue(self.loginPage.lblProductName.isVisible())
        LOG.info('Product name label is present on login page.')

    def test_invalid_username(self):
        self._testInvalidInputs(username=self.invalidUsername, password=self.password)

    def test_invalid_password(self):
        self._testInvalidInputs(username=self.username, password=self.invalidPassword)

    def test_invalid_inputs(self):
        self._testInvalidInputs(username=self.invalidUsername, password=self.invalidPassword)

    def test_blank_username(self):
        self._testInvalidInputs(password=self.password)

    def test_blank_password(self):
        self._testInvalidInputs(username=self.username)

    def test_blank_inputs(self):
        self._testInvalidInputs()

    def _testInvalidInputs(self, username='', password=''):
        LOG.step('Clearing username input box')

        self.loginPage.txtUsername.waitUntilPresent()
        self.loginPage.txtUsername.clear()

        if username:
            LOG.step('Typing username')

            self.loginPage.txtUsername.setText(username)
            self.assertTrue(self.loginPage.txtUsername.getText() == username)
        LOG.info('Username:', self.loginPage.txtUsername.getText())

        LOG.step('Clearing password input box')

        self.loginPage.txtPassword.clear()

        if password:
            LOG.step('Typing password')

            self.loginPage.txtPassword.setText(password)
            self.assertTrue(self.loginPage.txtPassword.getText() == password)
        LOG.info('Password:', self.loginPage.txtPassword.getText())

        # One or both credentials are blank
        if (not username) or (not password):
            LOG.step("Verifying sign-in button is disabled")

            self.assertFalse(self.loginPage.btnSignIn.isEnabled())
            LOG.info('Sign-in button disabled')
        # One or both credentials are invalid
        else:
            LOG.step("Clicking on button 'Sign In'")

            self.loginPage.btnSignIn.waitUntilPresent()
            self.loginPage.btnSignIn.waitUntilEnabled()
            self.loginPage.btnSignIn.click()

            LOG.step("Expecting login failed dialog")

            self.loginFailedPage.lblTitle.waitUntilPresent()
            LOG.info('Title label is present on login failed page')

            LOG.step('Closing login failed dialog')

            self.loginFailedPage.btnOK.click()
            self.loginPage.waitUntilLoaded()
            self.loginPage.lblProductName.waitUntilPresent()
            LOG.info('Product name label is present on login page')

    def testTeardown(self):
        self.driver.close()

    def suiteTeardown(self):
        LOG.step('suiteTeardown: Closing browser')
        self.driver.quit()

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testLoginPage = TestLoginPage()
    sys.exit(testLoginPage.numberOfFailedTests())
