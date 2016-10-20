from base_page import *


class ConsistencyGroupsPage(BasePage):
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/cgs'
        super(ConsistencyGroupsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # Search box
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchForConsistencyGroup"]'

        # 'Create' drop-down list
        self._selectors['menuCreate'] = '//a[@data-mg-comp="cg-createSplitbutton"]'
        self._selectors['mItmCreate'] = '//div[@data-mg-comp="cggrid-create-btn-menu"]'

        # 'Edit' drop-down list
        self._selectors['menuEdit'] = '//a[@data-mg-comp="cggrid-edit"]'
        self._selectors['mItmEdit'] = '//div[@data-mg-comp="cggrid-edit-btn-menu"]'

        # 'Clone', 'Delete' and 'Refresh' buttons on grid's toolbar
        self._selectors['btnClone'] = '//a[@data-mg-comp="cloneCG_ToolBtn"]'
        self._selectors['btnDelete'] = '//a[@data-mg-comp="deleteCG_ToolBtn"]'
        self._selectors['btnRefresh'] = '//div[@data-mg-comp="cgs-grid"]/div[starts-with(@id, "toolbar")]/div/div/a[@data-mg-comp="refresh_ToolBtn"]'

        # Consistency Groups main grid
        self._selectors['gridConsistencyGroups'] = '//div[@data-mg-comp="cgs-grid"]'

    def setupComponents(self):
        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver,
            selector=self.selectors.sBoxSearch, name=self.name)

        self.components['menuCreate'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuCreate, name=self.name)
        self.components['mItmCreate'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmCreate, name=self.name)
        self.mItmCreate.mapItems(items=['Consistency group', 'Snapshot copy', 'LUNs'])
        self.menuCreate.addItems(items=self.mItmCreate)

        self.components['menuEdit'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuEdit, name=self.name)
        self.components['mItmEdit'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmEdit, name=self.name)
        self.mItmEdit.mapItems(items=['Name'])
        self.menuEdit.addItems(items=self.mItmEdit)

        self.components['btnClone'] = button.Button(driver=self.driver,
            selector=self.selectors.btnClone, name=self.name)
        self.components['btnDelete'] = button.Button(driver=self.driver,
            selector=self.selectors.btnDelete, name=self.name)
        self.components['btnRefresh'] = button.Button(driver=self.driver,
            selector=self.selectors.btnRefresh, name=self.name)

        self.components['gridConsistencyGroups'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridConsistencyGroups, name=self.name)

        # Component uniquely identifying given page
        self.components['token'] = self.sBoxSearch
