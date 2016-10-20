from base_page import *


class LUNSnapshotsPage(BasePage):
    """
        LUN details page -> Snapshots tab.
    """
    def __init__(self, **kwargs):
        super(LUNSnapshotsPage, self).__init__(**kwargs)

    def setupSelectors(self):
        # Search box (next to button 'Create' in tool bar)
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchForSnapshots"]'

        # Button 'Create' on grid's toolbar
        self._selectors['btnCreate'] = '//a[@data-mg-comp="createSnapshot_ToolBtn"]'

        # Menu 'Edit' on grid's toolbar
        self._selectors['menuEdit'] = '//a[@data-mg-comp="lun-snanshot-editProperties"]'
        # List of 'Edit' menu items
        self._selectors['mItmEdit'] = '//div[@data-mg-comp="lun-snapshot-edit-btn-menu"]'

        # 'Clone', 'Delete' and 'Refresh' buttons on grid's toolbar
        self._selectors['btnClone'] = '//a[@data-mg-comp="createCloneFromSnapshot_ToolBtn"]'
        self._selectors['btnRestore'] = '//a[@data-mg-comp="restoreSnapshot_ToolBtn"]'
        self._selectors['btnDelete'] = '//a[@data-mg-comp="deleteSnapshot_ToolBtn"]'

        self._selectors['btnRefresh'] = '//div[@data-mg-comp="snapshot-grid"]/div[starts-with(@id, "toolbar")]/div/div/a[@data-mg-comp="refresh_ToolBtn"]'

        # Snapshots main grid
        self._selectors['gridSnapshots'] = '//div[@data-mg-comp="snapshot-grid"]'

    def setupComponents(self):
        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver, selector=self.
        selectors.sBoxSearch, name=self.name)

        # Button 'Create'
        self.components['btnCreate'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCreate, name=self.name)

        # Menu 'Edit'
        self.components['menuEdit'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuEdit, name=self.name)
        self.components['mItmEdit'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmEdit, name=self.name)
        self.mItmEdit.mapItems(items=['Name'])
        self.menuEdit.addItems(items=self.mItmEdit)

        # Buttons 'Clone', 'Delete', 'Refresh'
        self.components['btnClone'] = button.Button(driver=self.driver,
            selector=self.selectors.btnClone, name=self.name)
        self.components['btnRestore'] = button.Button(driver=self.driver,
            selector=self.selectors.btnRestore, name=self.name)
        self.components['btnDelete'] = button.Button(driver=self.driver,
            selector=self.selectors.btnDelete, name=self.name)

        self.components['btnRefresh'] = button.Button(driver=self.driver,
            selector=self.selectors.btnRefresh, name=self.name)

        # Snapshots grid
        self.components['gridSnapshots'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridSnapshots, name=self.name)

        # Component uniquely identifying given page
        self.components['token'] = self.sBoxSearch
