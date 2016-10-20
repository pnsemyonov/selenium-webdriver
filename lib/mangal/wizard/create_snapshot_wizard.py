import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

import time
from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.base_wizard import *


class CreateSnapshotPage(BasePage):
    """
        Single page of dialog 'Create Snapshot Copy'.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(CreateSnapshotPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Rename LUN' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="snapshotCreateDialog"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # LUN's name label
        self._selectors['lblSubtitle'] = '//div[@data-mg-comp="subTitle"]'

        # Label 'Name' (snapshot name)
        self._selectors['lblName'] = '//table[@data-mg-comp="createSnapshotInput"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Text box 'Name' (snapshot name)
        self._selectors['txtName'] = '//table[@data-mg-comp="createSnapshotInput"]/tbody/tr/td[contains(@id, "bodyEl")]/input'

        # Snapshot name error message
        self._selectors['lblNameError'] = '//table[@data-mg-comp="createSnapshotInput"]/tbody/tr/td[contains(@id, "bodyEl")]/div/ul/li'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="snapshotCreateDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//div[@data-mg-comp="snapshotCreateDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblSubtitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSubtitle)

        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName)
        self.components['txtName'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtName)

        self.components['lblNameError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblNameError)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def setName(self, name):
        """
            On dialog page 'Create Snapshot Copy' perform:
              - Clear snapshot name text box
              - Populate snapshot name text box with new name
            @param name: Name of new snapshot.
        """
        self.txtName.clear()
        self.txtName.setText(text=name)
        # Let the form to update value
        time.sleep(.5)
        LOG.l4('%s.setName(name=%s)' % (self.name, name))

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('%s.submit()' % self.name)


class CreateSnapshotWizard(BaseWizard):
    """
        Creates snapshot of selected LUN/consistency group in grid on All Storage ->
          LUNs/Consistency Groups page.
        To be overwritten in CreateLUNSnapshotWizard/CreateConsistencyGroupSnapshotWizard.
    """
    pass
