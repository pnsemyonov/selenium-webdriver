import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

import time
from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from mangal.wizard.base_wizard import *

class ResizeLUNPage(BasePage):
    """
        Single page of dialog 'Resize LUN'.
    """
    def __init__(self, locale, **kwargs):
        path = '#manager/storage/allstorage/luns'
        self.locale = locale
        super(ResizeLUNPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Resize LUN' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunResizeDialog"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # LUN name label below title
        self._selectors['lblName'] = '//div[@data-mg-comp="subTitle"]'

        # LUN size label
        self._selectors['lblSize'] = '//div[@data-mg-comp="formpanel"]/div/span/div/table/tbody/tr/td[contains(@id, "labelCell")]/label'
        # LUN size text box
        self._selectors['txtSize'] = '//table[@data-mg-comp="inputSize"]/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[contains(@id, "inputCell")]/input'
        # LUN size unit drop-down list
        self._selectors['dLstSizeUnit'] = '//table[@data-mg-comp="inputUnit"]'
        # LUN size unit drop-down items
        self._selectors['dItmSizeUnit'] = '//body/div[contains(@class, "mg-list-size-unit")]'

        # LUN size error message
        self._selectors['lblSizeError'] = '//div[@data-mg-comp="formpanel"]/div/span/div/table/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "errorEl")]/ul/li'
        # LUN same size error (pops up above size text box)
        self._selectors['lblSameSizeError'] = '//div[@data-mg-comp="subHeader"]/span/div/div'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="lunResizeDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//div[@data-mg-comp="lunResizeDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName)

        self.components['lblSize'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSize)
        self.components['txtSize'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtSize)
        self.components['dLstSizeUnit'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstSizeUnit)
        self.components['dItmSizeUnit'] = dropdownlist.DropDownItems(driver=self.driver,
            selector=self.selectors.dItmSizeUnit)

        self.dLstSizeUnit.addItems(items=self.dItmSizeUnit)
        self.components['lblSizeError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSizeError)
        self.components['lblSameSizeError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSameSizeError)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def resizeLUN(self, size):
        """
            On dialog page 'Resize LUN' perform:
              - Clear LUN size text box
              - Populate LUN size text box with new LUN size
              - Select size unit from drop-down list
              - Confirm by clicking on button OK
            @param size: New size of LUN as string (ex. '1t', '3G' etc.)
        """
        # Extract from provided size ('1024 K', '2GB' etc.) included size unit ('K', 'M' etc.)
        sizeUnit = Utility.getLocalizedSizeUnit(sizeUnit=Utility.getSizeUnit(size=size),
            locale=self.locale)
        # Select size unit ('KiB', 'Gib')
        self.dLstSizeUnit.select(item=sizeUnit)
        self.txtSize.clear()
        sizeText = Utility.getLocalizedSizeFormat(size=size, locale=self.locale)
        self.txtSize.setText(text=sizeText)
        # By undefined reason, typed text isn't propagated immediately after typing, so click on
        #   'OK' submits old value. Sleep helps the things to make up.
        time.sleep(.5)
        LOG.l4("ResizeLUNWizard.ResizeLUNPage.resizeLUN(size='%s')" % size)

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('ResizeLUNWizard.ResizeLUNPage.submit()')


class ResizeLUNWizard(BaseWizard):
    """
        Edit size of selected LUN in grid on All Storage -> LUNs page.
    """
    def __init__(self, driver, locale='en'):
        super(ResizeLUNWizard, self).__init__(driver=driver)
        self.addPage(name='resizeLUNPage', page=ResizeLUNPage(driver=self.driver, locale=locale))

    def open(self, name):
        """
            Select LUN in grid by given name, then open resize dialog.
            @param name: Name of LUN which to select in grid.
        """
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabLUNs.click()
        lunsPage = LUNsPage(driver=self.driver)

        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(name=name)

        # In menu 'Edit', select item 'Name'.
        lunsPage.menuEdit.select(item='Size')
        self.resizeLUNPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('ResizeLUNWizard.open()')
