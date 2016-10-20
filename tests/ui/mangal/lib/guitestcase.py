#!/usr/bin/env python
purpose = """
GUITestCase Class
"""

import sys
import os

# add the library path
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../rest/lib"))

from frtestcase import *
from frutil import *
from mangal.page.base_page import BasePage
from mangal.page.login.login import Login
from mangal.page.logout.logout import Logout
from utils import *

# Add arguments understood by this class
ARGS.parser.add_argument(
    "--browser", type=str,
    default="firefox",
    help="Browser to run the GUI automation")

ARGS.parser.add_argument(
    "--maximizewindow",
    default=True,
    help="Maximize Windwos: True or False")

class GuiTestCase(FRTestCase):
    def __init__(self):
        FRTestCase.__init__(self)

    def suiteSetup(self):
        LOG.step('suiteSetup: Setup of web browser')
        self.m = self.mars[0]
        controller_name = self.m.hostname
        self.homepage = "http://%s" % getFQDN(controller_name)
        self.driver = self.setupWebDriver(homepage=self.homepage)

    def testSetup(self):
        LOG.step('TestSetup: login before you start the test case')
        if not ARGS.values.no_mars:
            cleanup_sal(self.m)
        self.driver.load(self.homepage)
        login = Login(self.driver)
        login.performLogin()

    def testTeardown(self):
        # Need to logout first before calling quit
        LOG.step('Completing testTeardown')
        logout = Logout(self.driver)
        logout.performLogout()
        self.driver.close()
        sleep(3)

    def suiteTeardown(self):
        LOG.step('suiteTeardown: closing All browsers and delete session')
        self.driver.quit()

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    m = GuiTestCase()
    m.suiteSetup()