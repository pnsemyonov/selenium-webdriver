#!/usr/bin/env python

purpose = """Unit test of Mangal GUI Menu Component"""

import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../.."))

import time
import express
from mangal.page.login_page import LoginPage
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.create_luns_wizard import DefineLUNsPage
from frlog import LOG
from frargs import ARGS
from frutil import getFQDN
from frtestcase import FRTestCase
from frexceptions import *
from selenium.webdriver.support.ui import WebDriverWait


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

class TestComponentMenu(FRTestCase):
    def suiteSetup(self):
        self.username = ARGS.values.username
        self.password = ARGS.values.password
        self.webUIHostName = getFQDN(self.mars[0].hostname)

    def testSetup(self):
        self.driver = self.setupDriver()
        self.loginPage = LoginPage(driver=self.driver, url=self.webUIHostName)
        self.headerPage = HeaderPage(driver=self.driver)
        self.allStoragePage = AllStoragePage(driver=self.driver)
        self.lunsPage = LUNsPage(driver=self.driver)
        self.defineLUNsPage = DefineLUNsPage(driver=self.driver)

    def test_component_menu(self):
        LOG.step('Opening login page')
        self.loginPage.open()

        LOG.step("Getting item list of menu 'Locale'")
        LOG.info('Menu items:\n', self.loginPage.menuLocale.getItems())

        LOG.step('Selecting locale menu item')
        self.loginPage.selectLocale(locale=ARGS.values.locale)
        LOG.info('Locale hypertext reference:',
            self.loginPage.menuLocale.getAttribute(attributeName='href'))

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
        self.loginPage.btnSignIn.waitUntilPresent()
        self.loginPage.btnSignIn.waitUntilEnabled()
        self.loginPage.btnSignIn.click()

        LOG.step("Clicking on button 'Manager'")
        self.headerPage.btnManager.waitUntilPresent()
        self.headerPage.btnManager.click()

        LOG.step("Clicking on tab 'LUNs'")
        self.allStoragePage.tabLUNs.click()

        LOG.step("Selecting item 'LUNs' in menu 'Create'")
        self.lunsPage.menuCreate.waitUntilPresent()
        self.lunsPage.menuCreate.select(item='LUNs')

        LOG.step("Confirming dialog 'Create LUNs' popped up")
        self.defineLUNsPage.lblTitle.waitUntilPresent()
        LOG.info('Dialog title is present:', self.defineLUNsPage.lblTitle.isPresent())

        LOG.step("Closing dialog by clicking on button 'Cancel'")
        self.defineLUNsPage.btnCancel.click()

        LOG.step("Selecting item 'Sign Out' from user menu")
        self.headerPage.menuUser.waitUntilPresent()
        self.headerPage.menuUser.select(item='Sign Out')

        LOG.step('Verifying browser comes back to login page')
        self.loginPage.imgCompanyLogo.waitUntilPresent()
        LOG.info('Company logo is present on page:', self.loginPage.imgCompanyLogo.isPresent())

    def testTeardown(self):
        self.driver.quit()


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    testComponentMenu = TestComponentMenu()
    sys.exit(testComponentMenu.numberOfFailedTests())