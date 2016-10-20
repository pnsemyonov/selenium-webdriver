import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from mangal.wizard.base_wizard import *


class ChangeInitiatorGroupOSTypePage(BasePage):
    """
        Dialog page 'Change Initiator Group OS Type'.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/igroups'
        super(ChangeInitiatorGroupOSTypePage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Rename Initiator Group' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="igOsTypeDialog"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # Label with initiator group name
        self._selectors['lblSubtitle'] = '//div[@data-mg-comp="subTitle"]'

        # Label 'OS Type'
        self._selectors['lblOSType'] = '//table[@data-mg-comp="igosType"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Drop-down list 'OS Type'
        self._selectors['dLstOSType'] = '//table[@data-mg-comp="igosType"]'
        # Items of drop-down list
        self._selectors['dItmOSType'] = '//body/div[contains(@class, "x-boundlist")]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="igOsTypeDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnOK'] = '//div[@data-mg-comp="igOsTypeDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)
        self.components['lblSubtitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSubtitle)

        self.components['lblOSType'] = label.Label(driver=self.driver,
            selector=self.selectors.lblOSType)
        self.components['dLstOSType'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstOSType)
        self.components['dItmOSType'] = dropdownlist.DropDownItems(driver=self.driver,
            selector=self.selectors.dItmOSType)
        self.dLstOSType.addItems(items=self.dItmOSType)

        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def setOSType(self, osType):
        """
            Sets OS type for initiator group.
            @param osType: OS type to be set to initiator group ('Windows', 'Linux', 'VMware',
              'Xen').
        """
        self.dLstOSType.select(item=osType)
        LOG.l4("ChangeInitiatorGroupOSTypeWizard.%s.setOSType(osType='%s')" % (self.name, osType))


class ChangeRelatedInitiatorGroupsPage(BasePage):
    """
        Dialog page 'Change related initiator groups' (pops up when user change OS type of one of
          related initiator groups).
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/igroups'
        super(ChangeRelatedInitiatorGroupsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # Label 'Change related initiator groups'
        self._selectors['lblTitle'] = '//body/div[contains(@class, "mg-message-box")]/div[contains(@id, "header")]/div/div/div/div/span'

        # Compound message (includes list of related initiator groups)
        self._selectors['lblMessage'] = '//body/div[contains(@class, "mg-message-box")]/div[contains(@id, "body")]/span/div/div[@data-mg-comp="msg"]/span/div'
        # List of related initiator groups' (is included into compound message)
        self._selectors['lblInitiatorGroups'] = '//body/div[contains(@class, "mg-message-box")]/div[contains(@id, "body")]/span/div/div[@data-mg-comp="msg"]/span/div/div/ul'

        # Buttons at the bottom of the dialog
        self._selectors['btnNo'] = '//body/div[contains(@class, "mg-message-box")]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnYes'] = '//body/div[contains(@class, "mg-message-box")]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle)

        self.components['lblMessage'] = label.Label(driver=self.driver,
            selector=self.selectors.lblMessage)
        self.components['lblInitiatorGroups'] = label.Label(driver=self.driver,
            selector=self.selectors.lblInitiatorGroups)

        self.components['btnNo'] = button.Button(driver=self.driver,
            selector=self.selectors.btnNo)
        self.components['btnYes'] = button.Button(driver=self.driver,
            selector=self.selectors.btnYes)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle

    def submit(self):
        """
            Submit page by clicking button 'Yes'
        """
        self.btnYes.click()
        self.waitUntilClosed()
        LOG.l4('%s.submit()' % self.name)

    def cancel(self):
        """
            Close page by clicking button 'No'
        """
        self.btnno.click()
        self.waitUntilClosed()
        LOG.l4('%s.cancel()' % self.name)


class ChangeInitiatorGroupOSTypeWizard(BaseWizard):
    """
        Edit OS type of selected initiator group in grid on All Storage -> Initiator Groups page.
    """
    def __init__(self, driver):
        super(ChangeInitiatorGroupOSTypeWizard, self).__init__(driver=driver)
        self.addPage(name='changeInitiatorGroupOSTypePage',
            page=ChangeInitiatorGroupOSTypePage(driver=self.driver))
        self.addPage(name='changeRelatedInitiatorGroupsPage',
            page=ChangeRelatedInitiatorGroupsPage(driver=self.driver))

    def open(self, initiator_groups):
        """
            @param initiator_groups: Name or names (as list) of initiator group(s) to select in
              grid.
        """
        # Select menu item 'Create -> LUNs'
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabInitiatorGroups.click()
        initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)
        initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiator_groups)
        initiatorGroupsPage.menuEdit.select(item='OS Type')
        self.changeInitiatorGroupOSTypePage.waitUntilOpen()
        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4("ChangeInitiatorGroupOSTypeWizard.open(initiator_groups='%s')" % initiator_groups)

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.activePage.btnOK.waitUntilEnabled()
        self.activePage.btnOK.click()
        if self.changeRelatedInitiatorGroupsPage.isOpen():
            self.activePageNumber += 1
            self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        else:
            self.changeInitiatorGroupOSTypePage.waitUntilClosed()
        LOG.l4('%s.submit()' % self.name)
