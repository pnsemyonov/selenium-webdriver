import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.base_wizard import *


class TakeLUNOfflinePage(BasePage):
    """
        Single page of dialog 'Take LUN(s) Offline'.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(TakeLUNOfflinePage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Take LUN(s) Offline' label
        self._selectors['lblTitle'] = '//body/div[contains(@class, "mg-message-box")]/div[contains(@id, "header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # LUN name label below title
        self._selectors['lblName'] = '//div[@data-mg-comp="subTitle"]'

        # 'Are you sure you want...' label
        self._selectors['lblMessage'] = '//div[@data-mg-comp="msg"]/span/div'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//body/div[contains(@class, "mg-message-box")]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnTakeOffline'] = '//body/div[contains(@class, "mg-message-box")]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName)

        self.components['lblMessage'] = label.Label(driver=self.driver,
            selector=self.selectors.lblMessage)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnTakeOffline'] = button.Button(driver=self.driver,
            selector=self.selectors.btnTakeOffline)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def submit(self):
        """
            Submit dialog by clicking on button 'Take Offline'.
        """
        self.btnTakeOffline.click()
        self.waitUntilClosed()
        LOG.l4('EditLUNStateWizard.TakeLUNOfflinePage.submit()')


class EditLUNStateWizard(BaseWizard):
    """
        Edits state of selected LUN(s) in grid: 'Online' and 'Offline'.
    """
    def __init__(self, driver):
        super(EditLUNStateWizard, self).__init__(driver=driver)
        self.addPage(name='takeLUNOfflinePage', page=TakeLUNOfflinePage(driver=self.driver))

    def takeOnline(self, **filterAttrs):
        """
            Selects LUN(s) in grid by names(s), then selects menu item Edit -> state -> Online.
            @param filterAttrs: Filtering condition applied to rows of grid. See satisfyFilters().
        """
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabLUNs.click()
        lunsPage = LUNsPage(driver=self.driver)

        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(**filterAttrs)

        menuEdit = lunsPage.menuEdit
        # In menu 'Edit', select item 'Name'.
        menuEdit.select(item=['State', 'Online'])
        LOG.l4('EditLUNStateWizard.takeOnline()')

    def openTakeOffline(self, **filterAttrs):
        """
            Select LUN(s) in grid by given name(s), then open 'Take LUNs Offline' dialog.
            @param filterAttrs: Filtering condition applied to rows of grid. See satisfyFilters().
        """
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabLUNs.click()
        lunsPage = LUNsPage(driver=self.driver)

        # In LUNs grid, select rows satisfying filter conditions by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(**filterAttrs)

        menuEdit = lunsPage.menuEdit
        # In menu 'Edit', select item 'Name'.
        menuEdit.select(item=['State', 'Offline'])

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('EditLUNStateWizard.openTakeOffline()')
