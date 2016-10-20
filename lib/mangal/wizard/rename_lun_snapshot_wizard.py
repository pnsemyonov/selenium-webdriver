from rename_wizard import *
from mangal.page.lun_snapshots_page import LUNSnapshotsPage


class RenameLUNSnapshotPage(RenamePage):
    """
        Single page of dialog 'Rename Snapshot Copy' on LUN Snapshots page.
    """
    def renameLUNSnapshot(self, name):
        super(RenameLUNSnapshotPage, self).rename(name=name)
        LOG.l4("%s.renameLUNSnapshot(name='%s')" % (self.name, name))


class RenameLUNSnapshotWizard(RenameWizard):
    """
        Edit name of selected LUN Snapshot in grid on All Storage -> LUN details -> Snapshots page.
    """
    def __init__(self, driver):
        super(RenameLUNSnapshotWizard, self).__init__(driver=driver)
        self.addPage(name='renameLUNSnapshotPage', page=RenameLUNSnapshotPage(driver=self.driver,
            parentName=self.name))

    def open(self, name):
        """
            Select LUN sapshot in grid by given name, then open rename dialog.
            @param name: Name of LUN snapshot to be selected in grid.
        """
        lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver)
        lunSnapshotsPage.waitUntilOpen()
        # In LUN snapshots grid, select row with given LUN snapshot name by checking row check box.
        lunSnapshotsPage.gridSnapshots.unselect()
        lunSnapshotsPage.gridSnapshots.select(name=name)
        # In menu 'Edit', select item 'Name'.
        lunSnapshotsPage.menuEdit.select(item='Name')

        self.renameLUNSnapshotPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4("%s.open(name='%s')" % (self.name, name))
