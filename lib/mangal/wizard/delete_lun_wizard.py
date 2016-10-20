import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.base_wizard import *


class DeleteLUNPage(BasePage):
    """
        Single page of dialog 'Delete LUNs'.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(DeleteLUNPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Delete LUNs' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunDeleteDialog"]/div[contains(@id, "header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # LUN name label below title
        self._selectors['lblName'] = '//div[@data-mg-comp="subTitle"]'
        # 'Are you sure you want...' label
        self._selectors['lblMessage'] = '//div[@data-mg-comp="msg"]/span/div'

        # Check box and label 'Yes, delete the LUNs and all their data'
        self._selectors['lblYesDeleteTheLUNs'] = '//table[@data-mg-comp="lunCheckbox"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'
        self._selectors['chkYesDeleteTheLUNs'] = '//table[@data-mg-comp="lunCheckbox"]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//body/div[@data-mg-comp="lunDeleteDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//body/div[@data-mg-comp="lunDeleteDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName)
        self.components['lblMessage'] = label.Label(driver=self.driver,
            selector=self.selectors.lblMessage)

        self.components['lblYesDeleteTheLUNs'] = label.Label(driver=self.driver,
            selector=self.selectors.lblYesDeleteTheLUNs)
        self.components['chkYesDeleteTheLUNs'] = checkbox.CheckBox(driver=self.driver,
            selector=self.selectors.chkYesDeleteTheLUNs)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def confirm(self):
        """
            Confirms LUNs deletion by selecting check box 'Yes, delete the LUNs...'
        """
        self.chkYesDeleteTheLUNs.select()

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.waitUntilEnabled()
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('DeleteLUNWizard.DeleteLUNPage.submit()')


class DeleteLUNWizard(BaseWizard):
    """
        Deletes LUNs selected in grid.
    """
    def __init__(self, driver):
        super(DeleteLUNWizard, self).__init__(driver=driver)
        self.addPage(name='deleteLUNPage', page=DeleteLUNPage(driver=self.driver))

    def open(self, name):
        """
            Select LUN(s) in grid by given name(s), then open 'Delete LUNs' dialog.
            @param name: Name of LUN(s) which to select in grid. 'LUN_Name' if single LUN, list of
              names when multiple LUNs selected (ex. ['LUN_1', 'LUN_2', 'LUN_3']).
        """
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabLUNs.click()
        lunsPage = LUNsPage(driver=self.driver)

        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(name=name)

        lunsPage.btnDelete.waitUntilEnabled()
        lunsPage.btnDelete.click()
        self.deleteLUNPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('DeleteLUNWizard.open()')
