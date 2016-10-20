import sys
import os
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))
from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.wizard.base_wizard import *


class RenamePage(BasePage):
    """
        Single page of dialogs 'Rename LUN/Initiator Group'.
    """
    def __init__(self, **kwargs):
        super(RenamePage, self).__init__(**kwargs)

    def setupSelectors(self):
        # 'Rename Initiator Group' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="renameDialog"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # Label with initiator group name
        self._selectors['lblSubtitle'] = '//div[@data-mg-comp="subTitle"]'

        # Initiator group name label
        self._selectors['lblName'] = '//table[@data-mg-comp="renameInput"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Initiator group name text box
        self._selectors['txtName'] = '//table[@data-mg-comp="renameInput"]/tbody/tr/td[contains(@id, "bodyEl")]/input'

        # LUN's name error message
        self._selectors['lblNameError'] = '//table[@data-mg-comp="renameInput"]/tbody/tr/td[contains(@id, "bodyEl")]/div/ul/li'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="renameDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//div[@data-mg-comp="renameDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

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

    def rename(self, name):
        """
            On dialog page 'Rename LUN/Initiator Group' perform:
              - Clear name text box
              - Populate name text box with new name
              - Confirm by clicking on button 'OK'
            @param name: New name of initiator group.
        """
        self.txtName.clear()
        self.txtName.setText(text=name)

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.waitUntilEnabled()
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('%s.submit()' % self.name)


class RenameWizard(BaseWizard):
    """
        To be overwritten in RenameLUNWizard/RenameInitiatorGroupWizard etc.
    """
    pass
