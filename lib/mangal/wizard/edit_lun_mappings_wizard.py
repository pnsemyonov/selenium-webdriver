import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.base_wizard import *


class EditMappingsPage(BasePage):
    """
        Single page of dialog 'Edit Mappings'.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(EditMappingsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Edit Mappings' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunIgMapEditDialog"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # LUN's name label below title
        self._selectors['lblName'] = '//div[@data-mg-comp="subTitle"]'

        # Grid and its tool bar components
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchGrid"]'
        self._selectors['lblShowOnlySelectedInitiatorGroups'] = '//table[@data-mg-comp="showSelectedRowOnly"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'
        self._selectors['chkShowOnlySelectedInitiatorGroups'] = '//table[@data-mg-comp="showSelectedRowOnly"]'
        self._selectors['gridInitiatorGroups'] = '//div[@data-mg-comp="lunIgMapEditDialog-searchAndSelectIgroup"]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="lunIgMapEditDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//div[@data-mg-comp="lunIgMapEditDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName)

        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver,
            selector=self.selectors.sBoxSearch)
        self.components['lblShowOnlySelectedInitiatorGroups'] = label.Label(driver=self.driver,
            selector=self.selectors.lblShowOnlySelectedInitiatorGroups)
        self.components['chkShowOnlySelectedInitiatorGroups'] = \
            checkbox.CheckBox(driver=self.driver,
            selector=self.selectors.chkShowOnlySelectedInitiatorGroups)
        self.components['gridInitiatorGroups'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridInitiatorGroups)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def selectInitiatorGroups(self, name=None):
        """
            On dialog page 'Edit Mappings' selects specified initiator groups.
        """
        self.gridInitiatorGroups.unselect()
        if name is not None:
            self.gridInitiatorGroups.select(initiator_groups=name)
        LOG.l4('EditLUNMappingsWizard.EditMappingsPage.selectInitiatorGroups(name=%s)' % name)

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('EditLUNMappingsWizard.EditMappingsPage.submit()')


class EditLUNMappingsWizard(BaseWizard):
    """
        Edit mappings of selected LUN(s) in grid on All Storage -> LUNs page.
    """
    def __init__(self, driver):
        super(EditLUNMappingsWizard, self).__init__(driver=driver)
        self.addPage(name='editMappingsPage', page=EditMappingsPage(driver=self.driver))

    def open(self, name):
        """
            Select LUN in grid by given name, then open dialog.
            @param name: Name of LUN which to select in grid.
        """
        if isinstance(name, list) and len(name) != 1:
            raise FailedConfigException('Wizard accepts single LUN name as argument.')
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabLUNs.click()
        lunsPage = LUNsPage(driver=self.driver)

        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(name=name)

        # In menu 'Edit', select item 'Name'.
        lunsPage.menuEdit.select(item='Mappings')
        self.editMappingsPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('EditLUNMappingsWizard.open()')
