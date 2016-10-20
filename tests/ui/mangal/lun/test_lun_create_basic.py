#!/usr/bin/env python

purpose = """Lun create basic tests"""

import sys
import os

# add the library path
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../rest/lib/"))

from frargs import ARGS
from frtestcase import *
from frutil import *
#from mangal.driver import Driver
from mangal.globals import *
from mangal.page.base_page import BasePage
from mangal.page.lun import *
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


class LunCreateBasic(FRTestCase):
    def __init__(self):
        FRTestCase.__init__(self)

    def suiteSetup(self):
        LOG.step('suiteSetup: Setup of web browser')
        self.m = self.mars[0]
        controller_name = self.m.hostname
        self.homepage = "http://%s" % getFQDN(controller_name)
        #self.driver = Driver(ARGS.values.driverHost, ARGS.values.port, ARGS.values.browser, ARGS.values.maximizewindow, self.homepage)
        self.driver = self.setupWebDriver(homepage=self.homepage)
        self.driver.load(self.homepage)
        self.basepage = BasePage(self.driver)
        self.basepage.performLogin()

    def testSetup(self):
        if not ARGS.values.no_mars:
            cleanup_sal(self.m)

    def test_lun_create_size_min(self):
        """
        1. create a lun that has size smaller than block size(min allowed size).
        """
        lunname = generate_lun_name()
        lunsize = generate_lun_size("MinMinus1")
        print "lun_create_size_min is %s" % lunsize
        self._lun_create(lunname, lunsize)

    def test_lun_create_name_with_all_allowed_chars(self):
        """
        1. create a lun with a name that contains all allowed chars.
        """
        lunname = generate_lun_name(type="all")
        lunsize = generate_lun_size(type=None)
        print "lun_create_name_with_all_allowed_chars is %s" % lunname
        self._lun_create(lunname, lunsize)

    def test_lun_create_name_length_max(self):
        """
        1. create a lun with a name that has max allowed # of chars.
        """
        lunname = generate_lun_name(type="max")
        lunsize = generate_lun_size(type=None)
        print "lun_create_name_length_max is %s" % lunname
        self._lun_create(lunname, lunsize)

    def test_lun_create_name_length_min(self):
        """
        1. create a lun with a name that has min allowed # of chars.
        """
        lunname = generate_lun_name(type="min")
        lunsize = generate_lun_size(type=None)
        print "lun_create_name_length_min is %s" % lunname
        self._lun_create(lunname, lunsize)

    def _lun_create(self, name, size):
        lun_wizard = LunWizard(self.driver)
        lun_wizard.load(retries=4)
        lun_wizard.defineProperties(name, size)
        lun_wizard.clickNext()
        lun_wizard.clickNext()
        lun_wizard.clickFinish()
        time.sleep(3)
        lun_wizard.verification(g_lun_success_verification)
        time.sleep(3)
        lun_wizard.clickClose()
        time.sleep(3)

    def testTeardown(self):
        LOG.step('Completing testTeardown')

    def suiteTeardown(self):
        LOG.step('suiteTeardown: closing browser')
        self.driver.quit()

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    lcb = LunCreateBasic()
    sys.exit(lcb.numberOfFailedTests())
