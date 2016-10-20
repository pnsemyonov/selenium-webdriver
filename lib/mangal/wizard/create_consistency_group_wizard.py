import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from express.utils import *
from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.consistency_groups_page import ConsistencyGroupsPage
from wizard.base_wizard import *


class CreateConsistencyGroupPage(BasePage):
    """
        'Create Consistency Group' single-page dialog is open on selecting 'Consistency group' from
          menu 'Create' on 'All Storage -> Consistency Groups' page.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/cgs'
        super(CreateConsistencyGroupPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # Label 'Create Consistency Group' at the top
        self._selectors['lblTitle'] = '//div[@data-mg-comp="cgCreateDlg"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # If consistency group was selected in grid before dialog open, this label will show group's
        #   name
        self._selectors['lblSubtitle'] = '//div[@data-mg-comp="subTitle"]'

        # Lable 'Name'
        self._selectors['lblName'] = '//table[@data-mg-comp="cgNameInput"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Text box 'Name'
        self._selectors['txtName'] = '//table[@data-mg-comp="cgNameInput"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        # Label 'Members:'
        self._selectors['lblMembers'] = '//div[@data-mg-comp="formpanel"]/div/span/div/table[starts-with(@id, "displayfield")]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # TODO: Members?

        # Search box
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchGrid"]'
        # Label 'Show only selected candidates'
        self._selectors['lblShowOnlySelectedCandidates'] = '//table[@data-mg-comp="showSelectedRowOnly"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'
        # Check box 'Show only selected candidates'
        self._selectors['chkShowOnlySelectedCandidates'] = '//table[@data-mg-comp="showSelectedRowOnly"]'
        # Grid 'Candidates/Mapped to'
        self._selectors['gridCandidates'] = '//div[@data-mg-comp="cg-candidateGrid"]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="cgCreateDlg"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//div[@data-mg-comp="cgCreateDlg"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblSubtitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSubtitle, name=self.name)

        self.components['lblName'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.lblName, name=self.name)
        self.components['txtName'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtName, name=self.name)
        self.components['lblMembers'] = label.Label(driver=self.driver,
            selector=self.selectors.lblMembers, name=self.name)

        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver,
            selector=self.selectors.sBoxSearch, name=self.name)
        self.components['lblShowOnlySelectedCandidates'] = label.Label(driver=self.driver,
            selector=self.selectors.lblShowOnlySelectedCandidates, name=self.name)
        self.components['chkShowOnlySelectedCandidates'] = checkbox.CheckBox(driver=self.driver,
            selector=self.selectors.chkShowOnlySelectedCandidates, name=self.name)
        self.components['gridCandidates'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridCandidates, name=self.name)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel, name=self.name)
        self.components['btnOK'] = button.Button(driver=self.driver, selector=self.selectors.btnOK,
            name=self.name)

        # Component uniquely identifying given page
        self.components['token'] = self.lblShowOnlySelectedCandidates

    def setName(self, name):
        """
            Sets name of new consistency group.
        """
        self.txtName.clear()
        self.txtName.setText(text=name)

    def getCandidates(self):
        """
            Returns list of candidates  in grid.
        """
        return self.gridCandidates.find()

    def setCandidates(self, candidates):
        """
            Selects candidates in grid.
        """
        self.gridCandidates.select(candidates=candidates)


class CreateConsistencyGroupWizard(BaseWizard):
    def __init__(self, driver):
        super(CreateConsistencyGroupWizard, self).__init__(driver=driver)
        self.addPage(name='createConsistencyGroupPage',
        page=CreateConsistencyGroupPage(driver=self.driver))

    def open(self, parentConsistencyGroup=None):
        # Select menu item 'Create -> LUNs'
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabConsistencyGroups.click()
        consistencyGroupsPage = ConsistencyGroupsPage(driver=self.driver)
        if parentConsistencyGroup is not None:
            consistencyGroupsPage.gridConsistencyGroups.unselect()
            consistencyGroupsPage.gridConsistencyGroups.select(name=parentConsistencyGroup)
        menuCreate = consistencyGroupsPage.menuCreate
        menuCreate.select(item='Consistency group')
        self.createConsistencyGroupPage.waitUntilOpen()
        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]

    def close(self):
        if self.createConsistencyGroupPage.btnOK.isEnabled():
            self.createConsistencyGroupPage.btnOK.click()
            self.createConsistencyGroupPage.waitUntilClosed()
            LOG.l4('%s.close()' % self.name)
        else:
            raise FailedConfigException('%s.close(): Unable to close.' % self.name)
