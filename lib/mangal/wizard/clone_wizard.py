import sys
import os
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))
from mangal.page.base_page import *
from mangal.wizard.base_wizard import *


class ClonePage(BasePage):
    """
        Single page of dialogs 'Clone a LUN/Consistency Group'.
    """
    def __init__(self, **kwargs):
        super(ClonePage, self).__init__(**kwargs)

    def setupSelectors(self):
        # 'Clone a LUN' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="cloneDialog"]/div[contains(@id, "header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # LUN name label below title
        self._selectors['lblSubtitle'] = '//div[@data-mg-comp="subTitle"]'

        # LUN name label next to text box
        self._selectors['lblName'] = '//table[@data-mg-comp="cloneNameInput"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # LUN name text box
        self._selectors['txtName'] = '//table[@data-mg-comp="cloneNameInput"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        # Label 'Mapped to'
        self._selectors['lblMappedTo'] = '//table[@data-mg-comp="cloneIGPicker"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Drop-down list 'Mapped to'
        self._selectors['dLstMappedTo'] = '//table[@data-mg-comp="cloneIGPicker"]'
        # Label 'Parent consistency group'
        self._selectors['lblParentConsistencyGroup'] = '//table[@data-mg-comp="cgName"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Combo box 'Parent consistency group'
        self._selectors['cBoxParentConsistencyGroup'] = '//table[@data-mg-comp="cgName"]'
        # Item list of 'Parent consistency group'
        self._selectors['cItmParentConsistencyGroup'] = '//body/div[starts-with(@id, "treepanel")]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//body/div[@data-mg-comp="cloneDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//body/div[@data-mg-comp="cloneDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblSubtitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSubtitle)

        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName)
        self.components['txtName'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtName)
        self.components['lblMappedTo'] = label.Label(driver=self.driver,
            selector=self.selectors.lblMappedTo)
        self.components['dLstMappedTo'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstMappedTo)
        self.components['lblParentConsistencyGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.lblParentConsistencyGroup)
        self.components['cBoxParentConsistencyGroup'] = combobox.ComboBox(driver=self.driver,
            selector=self.selectors.cBoxParentConsistencyGroup)
        self.components['cItmParentConsistencyGroup'] = combobox.ComboBoxItems(driver=self.driver,
            selector=self.selectors.cItmParentConsistencyGroup)
        self.cBoxParentConsistencyGroup.addItems(items=self.cItmParentConsistencyGroup)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def setName(self, name):
        self.txtName.clear()
        set.txtName.setText(text=name)

    def selectInitiatorGroups(self, initiatorGroups):
        selectInitiatorGroupsPage = SelectInitiatorGroupsPage(driver=self.driver)
        self.dLstMappedTo.expand()
        selectInitiatorGroupsPage.waitUntilOpen()
        selectInitiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiatorGroups)
        self.dLstMappedTo.collapse()
        selectInitiatorGroupsPage.waitUntilClosed()

    def selectParentConsistencyGroup(self, consistencyGroup):
        self.cBoxParentConsistencyGroup.select(item=consistencyGroup)

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.waitUntilEnabled()
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('%s.submit()' % self.name)


class SelectInitiatorGroupsPage(BasePage):
    """
        Page pops up as separate dialog window on expanding combo box 'Mapped to'
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(SelectInitiatorGroupsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Clone a LUN' label
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchGrid"]'
        self._selectors['lblShowOnlySelectedRows'] = '//table[@data-mg-comp="showSelectedRowOnly"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'
        self._selectors['chkShowOnlySelectedRows'] = '//table[@data-mg-comp="showSelectedRowOnly"]'
        self._selectors['gridInitiatorGroups'] = '//body/div[contains(@class, "ig-picker-dropdown")]/span/div/div'

    def setupComponents(self):
        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver,
            selector=self.selectors.sBoxSearch)
        self.components['lblShowOnlySelectedRows'] = label.Label(driver=self.driver,
            selector=self.selectors.lblShowOnlySelectedRows)
        self.components['chkShowOnlySelectedRows'] = checkbox.CheckBox(driver=self.driver,
            selector=self.selectors.chkShowOnlySelectedRows)
        self.components['gridInitiatorGroups'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridInitiatorGroups)
        self.components['token'] = self.chkShowOnlySelectedRows

    def selectInitiatorGroups(self, name):
        self.gridInitiatorGroups.select(initiator_group=name)


class CloneWizard(BaseWizard):
    """
        To be overwritten in CloneLUNWizard/CloneConsistencyGroupWizard etc.
    """
    pass
