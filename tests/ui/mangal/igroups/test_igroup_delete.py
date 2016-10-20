#!/usr/bin/env python

purpose = """Igroup Delete basic test"""

import sys
import os

sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../../ui/rest/lib/"))
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../lib/"))

from test_igroup_create_pos import *
from utils import *

class IgroupDeleteTestCase(GuiTestCase):
    def test_igroup_delete_without_initiators(self):
        """
        1. Create an igroup with no initiators
        2. Delete igroup - verify deletion is success
        """
        ig_name = generate_igroup_name()
        self._igroup_create(ig_name)
        self._igroup_delete(ig_name)

    def _igroup_create(self, ig_name):
        igroup_wizard = IgroupWizard(self.driver)
        igroup_wizard.load()
        igroup_wizard.defineProperties(ig_name)
        igroup_wizard.clickOk()
        time.sleep(5)
        igroup_wizard.verification(g_one_to_one_of_one)

    def _igroup_delete(self, ig_name):
        igroup_wizard = IgroupWizard(self.driver)
        igroup_wizard.clickGrid()
        igroup_wizard.clickDelete()
        time.sleep(5)
        igroup_wizard.verification(g_no_data_to_display)

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    e = IgroupDeleteTestCase()
    sys.exit(e.numberOfFailedTests())
