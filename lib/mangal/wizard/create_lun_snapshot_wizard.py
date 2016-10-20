from mangal.wizard.create_snapshot_wizard import *
from mangal.page.luns_page import LUNsPage


class CreateLUNSnapshotWizard(CreateSnapshotWizard):
    """
        Creates snapshot of selected LUN in grid on All Storage -> LUNs page.
    """
    def __init__(self, driver):
        super(CreateLUNSnapshotWizard, self).__init__(driver=driver)
        self.addPage(name='createSnapshotPage', page=CreateSnapshotPage(driver=self.driver,
            parentName=self.name))

    def open(self, name):
        """
            Select LUN in grid by given name, then set name of new snapshot.
            @param name: Name of LUN which to select in grid.
        """
        lunsPage = LUNsPage(driver=self.driver)
        lunsPage.waitUntilOpen()
        # In LUNs grid, select row with given LUN name by checking row check box.
        lunsPage.gridLUNs.unselect()
        lunsPage.gridLUNs.select(name=name)

        # In menu 'Create', select item 'Snapshot copy'.
        lunsPage.menuCreate.select(item='Snapshot copy')
        self.createSnapshotPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4('%s.open()' % self.name)
