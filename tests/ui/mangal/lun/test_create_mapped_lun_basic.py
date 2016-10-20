#!/usr/bin/env python

purpose = """Create Mapped Lun basic test"""

import sys
import os

# add the library path
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../../ui/rest/lib/"))
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../lib/"))

# system libs
from guitestcase import *
from mangal.page.base_page import BasePage
from mangal.page.igroups.igroup import *
from mangal.page.lun import *

class CreateMappedLunBasic(GuiTestCase):

    def test_GUI_create_mapped_lun(self):
        """
        Create a lun mapped to igroup.
        1. Create an igroup.
        2. Create a lun.
        3. Map to this igroup.
        4. Verify lun created.
        """
        lunname = generate_lun_name()
        lunsize = generate_lun_size(type=None)
        ig_name = generate_igroup_name(type="all")
        self._igroup_create(ig_name)
        self._mapped_lun_create(lunname, lunsize, ig_name)

    def _mapped_lun_create(self, lunname, size, ig_name):
        lun_wizard = LunWizard(self.driver)
        lun_wizard.load(retries=4)

        lun_wizard.defineProperties(lunname, size)
        lun_wizard.clickNext()
        lun_wizard.clickLunMapGrid()
        lun_wizard.clickNext()
        lun_wizard.verificationLunRecord(g_lunwizard_grid,lunname,ig_name)
        lun_wizard.clickFinish()

        sleep(3)
        lun_wizard.verification(g_mapped_lun_success_verification)
        sleep(3)
        lun_wizard.clickClose()
        sleep(3)

    def _igroup_create(self, ig_name):
        igroup_wizard = IgroupWizard(self.driver)
        igroup_wizard.load()
        igroup_wizard.defineProperties(ig_name)
        igroup_wizard.clickOk()
        sleep(5)
        igroup_wizard.verification(g_one_to_one_of_one)

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    lcb = CreateMappedLunBasic()
    sys.exit(lcb.numberOfFailedTests())
