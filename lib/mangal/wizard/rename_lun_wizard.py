from rename_wizard import *
from mangal.page.luns_page import LUNsPage


class RenameLUNPage(RenamePage):
    """
        Single page of dialog 'Rename LUN'.
    """
    def renameLUN(self, name):
        super(RenameLUNPage, self).rename(name=name)
        LOG.l4("%s.renameLUN(name='%s')" % (self.name, name))


class RenameLUNWizard(RenameWizard):
    """
        Edit name of selected LUN in grid on All Storage -> LUNs page.
    """
    def __init__(self, driver):
        super(RenameLUNWizard, self).__init__(driver=driver)
        self.addPage(name='renameLUNPage', page=RenameLUNPage(driver=self.driver,
            parentName=self.name))

    def open(self, name):
        """
            Select LUN in grid by given name, then open rename dialog.
            @param name: Name of LUN which to select in grid.
        """
        lunsPage = LUNsPage(driver=self.driver)
        lunsPage.waitUntilOpen()
        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(name=name)
        # In menu 'Edit', select item 'Name'.
        lunsPage.menuEdit.select(item='Name')

        self.renameLUNPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4("%s.open(name='%s')" % (self.name, name))
