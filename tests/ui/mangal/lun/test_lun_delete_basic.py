#!/usr/bin/env python

purpose = """Lun Delete basic test"""

import sys
import os

sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../../../ui/rest/lib/"))
sys.path.append(os.path.realpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../lib/"))

# system libs
from guitestcase import *
from mangal.page.base_page import BasePage
from mangal.page.delete_lun import *
from mangal.page.lun import *

class LunDeleteBasic(GuiTestCase):

    def test_GUI_delete_unmapped_lun(self):
        """
        Delete a lun that is not mapped to an igroup.
        1. Create a lun
        2. Select lun in lun-grid
        3. Launch Delete window, click checkbox, hit OK
        4. Validate lun deleted.
        """
        lunname = generate_lun_name()
        lunsize = generate_lun_size(type=None)
        LOG.info( "Delete lun : %s" % lunname)
        self._lun_create(lunname, lunsize)
        self._lun_delete(lunname)

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

    def _lun_delete(self, name):
        LOG.info("Start clicks to delete lun")
        lun_wizard = LunWizard(self.driver)
        lun_wizard.clickGrid()
        lun_wizard.clickDelete()

        delete_lun = DeleteLun(self.driver)
        delete_lun.checkDivName(name) # Verify that name displayed in the subtitle
        time.sleep(3)
        delete_lun.checkConfirmation() # Click Yes, delete lun and all its data
        time.sleep(3)
        delete_lun.clickOkay()
        time.sleep(3)
        delete_lun.verification(g_successful_deletion) # Verify Grid does not contain any data

if __name__ == '__main__':
    ARGS.parseArgs(purpose)
    lcb = LunDeleteBasic()
    sys.exit(lcb.numberOfFailedTests())
