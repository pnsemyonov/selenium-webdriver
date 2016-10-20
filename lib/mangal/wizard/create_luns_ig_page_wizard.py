import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.initiator_groups_page import InitiatorGroupsPage
from wizard.base_wizard import *
from wizard.create_luns_wizard import DefineLUNsPage


class DefineLUNsPage(DefineLUNsPage):
    """
        Define 'Create LUNs' page as it appears when its wizard is called form Initiator Groups
          page.
    """
    def __init__(self, locale, **kwargs):
        path = '#manager/storage/allstorage/igroups'
        self.locale = locale
        BasePage.__init__(self, path=path, **kwargs)

    def setupSelectors(self):
        super(DefineLUNsPage, self).setupSelectors()
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="igLunCreateDialog"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # These two components are present only when wizard called from Initiator Groups page.
        # Label 'Initiator Group' (left piece)
        self._selectors['lblInitiatorGroup'] = '//table[@data-mg-comp="igLunCreateFormInitiatorGroup"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Text 'Initiator Group' (right piece with actual value). This is not TextBox instance, but
        #   for clarity it's OK.
        self._selectors['txtInitiatorGroup'] = '//table[@data-mg-comp="igLunCreateFormInitiatorGroup"]/tbody/tr/td[contains(@id, "bodyEl")]/div'

        self._selectors['btnCancel'] = '//div[@data-mg-comp="igLunCreateDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        # This button is present only when wizard called from Initiator Groups page
        self._selectors['btnOK'] = '//div[@data-mg-comp="igLunCreateDialog"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="ok"]'

    def setupComponents(self):
        super(DefineLUNsPage, self).setupComponents()
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblInitiatorGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.lblInitiatorGroup, name=self.name)
        # Element is <div>, so Label is more appropriate than TextBox.
        self.components['txtInitiatorGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.txtInitiatorGroup, name=self.name)
        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel, name=self.name)
        self.components['btnOK'] = button.Button(driver=self.driver,
            selector=self.selectors.btnOK, name=self.name)

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.btnOK.click()
        self.waitUntilClosed()
        LOG.l4('CreateLUNsIGPageWizard.%s.submit()' % self.name)


class CreateLUNsIGPageWizard(BaseWizard):
    """
        Wizard 'Create LUNs' when open from Initiator Groups page.
    """
    def __init__(self, driver, locale='en'):
        super(CreateLUNsIGPageWizard, self).__init__(driver=driver)
        self.addPage(name='defineLUNsPage', page=DefineLUNsPage(driver=self.driver,
            locale=locale))

    def open(self, initiator_group):
        """
            @param initiator_group: Name of initiator group to select in grid.
        """
        # Select menu item 'Create -> LUNs'
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabInitiatorGroups.click()
        initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)
        initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiator_group)
        initiatorGroupsPage.menuCreate.select(item='LUNs')
        self.defineLUNsPage.waitUntilOpen()
        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
