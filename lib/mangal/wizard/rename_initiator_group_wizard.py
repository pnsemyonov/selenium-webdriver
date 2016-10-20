from rename_wizard import *
from mangal.page.initiator_groups_page import InitiatorGroupsPage


class RenameInitiatorGroupPage(RenamePage):
    """
        Single page of dialog 'Rename Initiator Group'.
    """
    def renameInitiatorGroup(self, name):
        super(RenameInitiatorGroupPage, self).rename(name=name)
        LOG.l4("%s.renameInitiatorGroup(name='%s')" % (self.name, name))


class RenameInitiatorGroupWizard(RenameWizard):
    """
        Edit name of selected initiator group in grid on All Storage -> Initiator Groups page.
    """
    def __init__(self, driver):
        super(RenameInitiatorGroupWizard, self).__init__(driver=driver)
        self.addPage(name='renameInitiatorGroupPage',
            page=RenameInitiatorGroupPage(driver=self.driver, parentName=self.name))

    def open(self, initiator_group):
        """
            @param initiator_group: Name of initiator group to select in grid.
        """
        initiatorGroupsPage = InitiatorGroupsPage(driver=self.driver)
        initiatorGroupsPage.waitUntilOpen()
        initiatorGroupsPage.gridInitiatorGroups.unselect()
        initiatorGroupsPage.gridInitiatorGroups.select(initiator_group=initiator_group)
        initiatorGroupsPage.menuEdit.select(item='Name')

        self.renameInitiatorGroupPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4("%s.open(initiator_group='%s')" % (self.name, initiator_group))
