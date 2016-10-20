from clone_wizard import *
from mangal.page.luns_page import LUNsPage


class CloneLUNWizard(CloneWizard):
    """
        Clone LUN selected in grid.
    """
    def __init__(self, driver):
        super(CloneLUNWizard, self).__init__(driver=driver)
        self.addPage(name='cloneLUNPage', page=ClonePage(driver=self.driver, parentName=self.name))
        self.addPage(name='selectInitiatorGroupsPage',
            page=SelectInitiatorGroupsPage(driver=self.driver, parentName=self.name))

    def open(self, name):
        """
            Select LUN in grid by given name, then open 'Clone a LUN' dialog.
            @param name: Name of LUN which to select in grid.
        """
        lunsPage = LUNsPage(driver=self.driver)
        lunsPage.waitUntilOpen()
        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(name=name)
        lunsPage.btnClone.click()

        self.cloneLUNPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4("%s.open(name='%s')" % (self.name, name))
