from clone_wizard import *
from mangal.page.lun_snapshots_page import LUNSnapshotsPage


class CloneLUNSnapshotWizard(CloneWizard):
    """
        Clone LUN snapshot selected in grid.
    """
    def __init__(self, driver):
        super(CloneLUNSnapshotWizard, self).__init__(driver=driver)
        self.addPage(name='cloneSnapshotPage', page=ClonePage(driver=self.driver,
            parentName=self.name))
        self.addPage(name='selectInitiatorGroupsPage',
            page=SelectInitiatorGroupsPage(driver=self.driver, parentName=self.name))

    def open(self, lunName, lunSnapshotName):
        """
            Select LUN snapshot in grid by given name, then open 'Clone a Snapshot Copy' dialog.
            @param name: Name of LUN snapshot which to select in grid.
        """
        lunSnapshotsPage = LUNSnapshotsPage(driver=self.driver)
        lunSnapshotsPage.waitUntilOpen()
        lunSnapshotsPage.gridSnapshots.unselect()
        lunSnapshotsPage.gridSnapshots.select(name=lunSnapshotName)
        lunSnapshotsPage.btnClone.click()

        self.cloneSnapshotPage.waitUntilOpen()

        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        LOG.l4("%s.open(lunName='%s', lunSnapshotName='%s')" % (self.name, lunName,
            lunSnapshotName))
