import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from mangal.wizard.base_wizard import *


class CreateInitiatorGroupPage(BasePage):
    """
        Single page of dialog 'Create an Initiator Group'.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(CreateInitiatorGroupPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Create an Initiator Group' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="igCreateDialog"]/div[contains(@id, "header")]/div/div/div/div[contains(@id, "header_hd")]/span'

        # Initiator group name label next to text box
        self._selectors['lblName'] = '//table[@data-mg-comp="igName"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Initiator group name text box
        self._selectors['txtName'] = '//table[@data-mg-comp="igName"]/tbody/tr/td[contains(@id, "bodyEl")]/input'

        # Label 'OS Type'
        self._selectors['lblOSType'] = '//table[@data-mg-comp="osType"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Drop-down list 'OS Type'
        self._selectors['dLstOSType'] = '//table[@data-mg-comp="osType"]'
        # Item list of drop-down list 'OS Type'
        self._selectors['dItmOSType'] = '//body/div[contains(@class, "x-boundlist")]'

        # Search box 'Search WWPNs'
        self._selectors['sBoxSearchWWPNs'] = '//table[@data-mg-comp="searchGrid"]'
        # Check box 'Show only selected initiators'
        self._selectors['chkShowOnlySelectedInitiators'] = '//table[@data-mg-comp="showSelectedRowOnly"]'
        # Label 'Show only selected initiators'
        self._selectors['lblShowOnlySelectedInitiators'] = '//table[@data-mg-comp="showSelectedRowOnly"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'

        # Grid 'Initiator WWPNs'
        self._selectors['gridInitiatorWWPNs'] = '//div[@data-mg-comp="initiatorGrid"]'
        # Text box 'Add WWPN'
        self._selectors['txtAddWWPN'] = '//table[@data-mg-comp="initiatorInput"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        # Button 'Add WWPN'
        self._selectors['btnAddWWPN'] = '//a[@data-mg-comp="addInitiatorBtn"]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//body/div[@data-mg-comp="igCreateDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//body/div[@data-mg-comp="igCreateDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)

        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName)
        self.components['txtName'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtName)

        self.components['lblOSType'] = label.Label(driver=self.driver,
            selector=self.selectors.lblOSType)
        self.components['dLstOSType'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstOSType)
        self.components['dItmOSType'] = dropdownlist.DropDownItems(driver=self.driver,
            selector=self.selectors.dItmOSType)
        self.dLstOSType.addItems(items=self.dItmOSType)

        self.components['sBoxSearchWWPNs'] = searchbox.SearchBox(driver=self.driver,
            selector=self.selectors.sBoxSearchWWPNs)
        self.components['chkShowOnlySelectedInitiators'] = checkbox.CheckBox(driver=self.driver,
            selector=self.selectors.chkShowOnlySelectedInitiators)
        self.components['lblShowOnlySelectedInitiators'] = label.Label(driver=self.driver,
            selector=self.selectors.lblShowOnlySelectedInitiators)

        self.components['gridInitiatorWWPNs'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridInitiatorWWPNs)
        self.components['txtAddWWPN'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtAddWWPN)
        self.components['btnAddWWPN'] = button.Button(driver=self.driver,
            selector=self.selectors.btnAddWWPN)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver, selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def defineInitiatorGroup(self, name, osType=None, wwpns=None):
        self.setName(name=name)
        if osType is not None:
            self.setOSType(osType=osType)
        if wwpns is not None:
            self.setWWPNs(wwpns=wwpns)
        LOG.l4("CreateInitiatorGroupWizard.%s.defineInitiatorGroup(name='%s', osType='%s', wwpns=%s)"
            % (self.name, name, osType, wwpns))

    def setName(self, name):
        self.txtName.clear()
        self.txtName.setText(name)
        LOG.l4("CreateInitiatorGroupWizard.%s.setName(name='%s')" % (self.name, name))

    def setOSType(self, osType):
        self.dLstOSType.select(item=osType)
        LOG.l4("CreateInitiatorGroupWizard.%s.setOSType(osType='%s')" % (self.name, osType))

    def setWWPNs(self, wwpns):
        self.gridInitiatorWWPNs.unselect()
        self.gridInitiatorWWPNs.select(initiator_group=wwpns)
        LOG.l4("CreateInitiatorGroupWizard.%s.setWWPNs(wwpns=%s)" % (self.name, wwpns))

    def addWWPNs(self, wwpns):
        """
            Adds WWPNs to grid 'Initiator WWPNs'.
        """
        if not isinstance(wwpns, list):
            wwpns = [wwpns]
        for wwpn in wwpns:
            self.txtAddWWPN.clear()
            self.txtAddWWPN.setText(text=wwpn)
            self.btnAddWWPN.click()
        LOG.l4("CreateInitiatorGroupWizard.%s.addWWPNs(wwpns=%s)" % (self.name, wwpns))

    def getWWPNs(self):
        wwpns = self.gridInitiatorWWPNs.find()
        LOG.l4("CreateInitiatorGroupWizard.%s.getWWPNs(): %s" % (self.name, wwpns))
        return wwpns

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('CreateInitiatorGroupWizard.%s.submit()' % self.name)


class CreateInitiatorGroupWizard(BaseWizard):
    """
        Create a new initiator group from All Storage -> Initiator Groups page.
    """
    def __init__(self, driver):
        super(CreateInitiatorGroupWizard, self).__init__(driver=driver)
        self.addPage(name='createInitiatorGroupPage',
            page=CreateInitiatorGroupPage(driver=self.driver))

    def open(self):
        """
            Open dialog 'Create an Initiator Group'.
        """
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabInitiatorGroups.click()
        initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)
        initiatorGroupsPage.menuCreate.select(item='Initiator Group')
        self.createInitiatorGroupPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('%s.open()' % self.name)
