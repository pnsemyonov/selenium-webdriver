import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from selenium.webdriver.common.keys import Keys
from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.base_wizard import *


class EditIDsPage(BasePage):
    """
        Single page of dialog 'Edit IDs'.
    """
    class LUNIDGrid(grid.Grid):
        """
            Customized version of Grid component. Use with caution as the only generic Grid's
              property it uses is relative path to table. All other Grid's properties/methods will
              fail.
        """
        def __init__(self, driver, selector, name=''):
            super(EditIDsPage.LUNIDGrid, self).__init__(driver=driver, selector=selector, name=name)

    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(EditIDsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Edit IDs' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunIdEditDialog"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'

        # LUN's name label below title
        self._selectors['lblLUNName'] = '//div[@data-mg-comp="subTitle"]'

        # Initiator groups grid
        self._selectors['gridInitiatorGroups'] = '//div[@data-mg-comp="lunIdMappinGrid"]'
        # That's tricky. In grid, once user clicked on cell 'LUN ID', its underlying HTML element
        #   <div> becomes hidden, and actual focus moves into dedicated element <input> which is
        #   shared across all the cells 'LUN ID' of each row in grid. Thus, to send keys into cell
        #   'LUN ID', it's essential to 1) click on <div>, then 2) send keys into vivified <input>.
        self._selectors['txtLUNID'] = '//table[@data-mg-comp="lun-id"]/tbody/tr/td[contains(@class, "x-form-item-body")]/input'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="lunIdEditDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//div[@data-mg-comp="lunIdEditDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblLUNName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblLUNName)
        self.components['gridInitiatorGroups'] = label.Label(driver=self.driver,
            selector=self.selectors.gridInitiatorGroups)
        self.components['txtLUNID'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtLUNID)
        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def getCellObjects(self):
        """
            Returns grid as collection of BaseComponents representing row and cells: [<row_1>,
              <row_2>, ...] where row is [<cell_1>, <cell_2>, ...] where cell is instance of
              BaseComponent.
        """
        # Relative path from head element of row to its cells.
        cellRelativePath = '/td/table/tbody/tr[contains(@class, "x-grid-data-row")]/td'
        grid = self.LUNIDGrid(driver=self.driver, selector=self.selectors.gridInitiatorGroups,
            name='LUNIDGrid')
        # Get list of BaseComponents representing rows in grid.
        rows = grid.getChildren(relativePath=grid.tableRelativePath)
        result = []
        for row in rows:
            # Get cells (as list of BaseComponents) in given row.
            cells = row.getChildren(cellRelativePath)
            # Add row (as list of cells).
            result.append(cells)
        return result

    def getIDs(self):
        """
            Returns pairs <initiator_group>: <lun_id> from grid. Ex.:
                {
                    'IG-1': 0,
                    'IG-2': 100,
                    ...
                }
        """
        rows = self.getCellObjects()
        # Pairs of <initiator_group_name>: <lun_id>.
        result = {}
        for row in rows:
            # Ex.: {'IG-1': 100}
            result[row[0].element.text()] = row[1].element.text()
        LOG.l4('EditLUNIDsPageWizard.%s.getIDs(): %s', (self.name, result))
        return result

    def setIDs(self, ids):
        """
            For each specified initiator group sets its corresponding ID.
            @param ids: Dictionary where each element describes initiator group name (key) and its
              ID (integer from 0 to 4095):
                {
                    'IG-1': 0,
                    'IG-2': 1,
                    ...
                }
        """
        rows = self.getCellObjects()
        for row in rows:
            initiatorGroupName = row[0].element.text()
            if initiatorGroupName in ids:
                # Most inner element of 'LUN ID' cell is <div>
                #   (tr[class*='x-grid-data-row']/td[2]/div).
                inputElement = row[1].getChild(relativePath='/div')
                # First, click inside cell frame represented by <div>.
                inputElement.element.click()
                # At this point, <div> obtained CSS property 'visibility: hidden'.
                # Wait until shared <input> has received focus.
                self.txtLUNID.waitUntilVisible()
                self.txtLUNID.clear()
                if isinstance(ids[initiatorGroupName], int):
                    id = str(ids[initiatorGroupName])
                else:
                    id = ids[initiatorGroupName]
                # Put text into <input>, not <div>.
                self.txtLUNID.setText(text=id)
                # Move focus out of input box to activate <div> back.
                row[0].element.click()
        LOG.l4('EditLUNIDsPageWizard.%s.setID(ids=%s)' % (self.name, ids))

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.waitUntilEnabled()
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('EditLUNIDsPageWizard.%s.submit()' % self.name)


class EditLUNIDsWizard(BaseWizard):
    """
        Edit name of selected LUN in grid on All Storage -> LUNs page.
    """
    def __init__(self, driver):
        super(EditLUNIDsWizard, self).__init__(driver=driver)
        self.addPage(name='editIDsPage', page=EditIDsPage(driver=self.driver))

    def open(self, name):
        """
            Select LUN in grid by given name, then open 'Edit IDs' dialog.
            @param name: Name of LUN which to select in grid.
        """
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabLUNs.click()
        lunsPage = LUNsPage(driver=self.driver)

        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(name=name)

        # In menu 'Edit', select item 'ID'.
        lunsPage.menuEdit.select(item='ID')
        self.editIDsPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('%s.open()' % self.name)
