from base_page import *


class LUNsPage(BasePage):
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(LUNsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # Search box (next to button 'Create' in tool bar)
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchForLUN"]'

        # Menu 'Create' on grid's toolbar
        self._selectors['menuCreate'] = '//a[@data-mg-comp="lungrid-create"]'
        # List of 'Create' menu items ('LUNs', 'Snapshot copy')
        self._selectors['mItmCreate'] = '//div[@data-mg-comp="lungrid-create-btn-menu"]'

        # Menu 'Edit' on grid's toolbar
        self._selectors['menuEdit'] = '//a[@data-mg-comp="lungrid-editProperties"]'
        # List of 'Edit' menu items
        self._selectors['mItmEdit'] = '//div[@data-mg-comp="lungrid-editProperties-btn-menu"]'
        # List of 'Edit -> State' sub-menu items
        self._selectors['mItmState'] = '//div[@data-mg-comp="lungrid-editProperties-lunstate-btn-menu"]'

        # 'Clone', 'Delete' and 'Refresh' buttons on grid's toolbar
        self._selectors['btnClone'] = '//a[@data-mg-comp="createCloneForLun_ToolBtn"]'
        self._selectors['btnDelete'] = '//a[@data-mg-comp="deleteLUN_ToolBtn"]'
        self._selectors['btnRefresh'] = '//div[@data-mg-comp="luns-grid"]/div[starts-with(@id, "toolbar")]/div/div/a[@data-mg-comp="refresh_ToolBtn"]'

        # LUNs main grid
        self._selectors['gridLUNs'] = '//div[@data-mg-comp="luns-grid"]'

    def setupComponents(self):
        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver, selector=self.
        selectors.sBoxSearch, name=self.name)

        # Menu 'Create'
        self.components['menuCreate'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuCreate, name=self.name)
        self.components['mItmCreate'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmCreate, name=self.name)
        self.mItmCreate.mapItems(items=['LUNs', 'Snapshot copy'])
        self.menuCreate.addItems(items=self.mItmCreate)

        # Menu 'Edit'
        self.components['menuEdit'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuEdit, name=self.name)
        self.components['mItmEdit'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmEdit, name=self.name)
        self.components['mItmState'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmState, name=self.name)
        self.mItmState.mapItems(items=['Online', 'Offline'])
        self.mItmEdit.mapItems(items=['Name', 'Size', 'Mappings', 'ID', 'State'])
        self.mItmEdit.addItems(item='State', childItems=self.mItmState)
        self.menuEdit.addItems(items=self.mItmEdit)

        # Buttons 'Clone', 'Delete', 'Refresh'
        self.components['btnClone'] = button.Button(driver=self.driver,
            selector=self.selectors.btnClone, name=self.name)
        self.components['btnDelete'] = button.Button(driver=self.driver,
            selector=self.selectors.btnDelete, name=self.name)
        self.components['btnRefresh'] = button.Button(driver=self.driver,
            selector=self.selectors.btnRefresh, name=self.name)

        # LUNs grid
        self.components['gridLUNs'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridLUNs, name=self.name)

        # Component uniquely identifying given page
        self.components['token'] = self.sBoxSearch
