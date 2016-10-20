import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

import time
from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from mangal.wizard.base_wizard import *


class ChangeInitiatorsPage(BasePage):
    """
        Single page of dialog 'Change Initiator' on Initiator Groups page.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/igroups'
        super(ChangeInitiatorsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Change Initiators' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="initiatorEditDialog"]/div[contains(@id, "header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        self._selectors['lblSubtitle'] = '//body/div[@data-mg-comp="initiatorEditDialog"]/div[contains(@id, "body")]/span/div/div[@data-mg-comp="subTitle"]'

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

        # Button 'Close' at the bottom of the dialog
        self._selectors['btnClose'] = '//body/div[@data-mg-comp="initiatorEditDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblSubtitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSubtitle)

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

        self.components['btnClose'] = button.Button(driver=self.driver,
            selector=self.selectors.btnClose)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def setWWPNs(self, wwpns):
        """
            Adds new WWPN to grid.
        """
        # As the grid is not equipped with 'Select all' checkbox, bulk deselection is not available.
        #   So we need to deselect row by row.
        allWWPNs = [wwpn['initiator_group'] for wwpn in self.getWWPNs()]
        self.gridInitiatorWWPNs.unselect(initiator_group=allWWPNs)
        self.gridInitiatorWWPNs.select(initiator_group=wwpns)
        LOG.l4("ChangeInitiatorsWizard.%s.setWWPNs(wwpns=%s)" % (self.name, wwpns))

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
            # Subsequent input is not performing unless some delay provided.
            time.sleep(.5)

        LOG.l4("ChangeInitiatorsWizard.%s.addWWPNs(wwpns=%s)" % (self.name, wwpns))

    def getWWPNs(self):
        """
            Obtains all WWPNs listed in grid.
        """
        wwpns = self.gridInitiatorWWPNs.find()
        LOG.l4("ChangeInitiatorsWizard.%s.getWWPNs(): %s" % (self.name, wwpns))
        return wwpns

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('ChangeInitiatorsWizard.%s.submit()' % self.name)


class ChangeInitiatorsWizard(BaseWizard):
    """
        Changes WWPNs of selected initiator group from All Storage -> Initiator Groups page.
    """
    def __init__(self, driver):
        super(ChangeInitiatorsWizard, self).__init__(driver=driver)
        self.addPage(name='changeInitiatorsPage', page=ChangeInitiatorsPage(driver=self.driver))

    def open(self, initiator_group):
        """
            Open dialog 'Change Initiators'.
            @param initiator_group: Name of initiator group to select in grid.
        """
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabInitiatorGroups.click()
        initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)
        initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiator_group)
        initiatorGroupsPage.menuEdit.select(item='Initiators')
        self.changeInitiatorsPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('%s.open()' % self.name)
