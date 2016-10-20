#!/usr/bin/env python
purpose = """
Igroup create positive test cases
"""
import sys
import os

# add the library path
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../../../lib"))
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../rest/lib/"))
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../lib/"))

# system libs
from guitestcase import *
from mangal.page.base_page import BasePage
from mangal.page.igroups.igroup import *

class IgroupTestCase(GuiTestCase):
    def test_igroup_create_max_char(self):
        """
        1. Create an igroup with no initiator
        """
        ig_name = generate_igroup_name(type="max")
        self._igroup_create(ig_name)

    def test_igroup_create_min_char(self):
        """
        1. Create an igroup with no initiator
        """
        ig_name = generate_igroup_name(type="min")
        self._igroup_create(ig_name)

    def test_igroup_create_all_char(self):
        """
        1. Create an igroup with no initiator
        """
        ig_name = generate_igroup_name(type="all")
        self._igroup_create(ig_name)

    def _igroup_create(self, ig_name):
        igroup_wizard = IgroupWizard(self.driver)
        igroup_wizard.load()
        igroup_wizard.defineProperties(ig_name)
        igroup_wizard.clickOk()
        time.sleep(5)
        igroup_wizard.verification(g_one_to_one_of_one)


if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    e = IgroupTestCase()
    sys.exit(e.numberOfFailedTests())
