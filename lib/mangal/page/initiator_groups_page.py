from base_page import *


class InitiatorGroupsPage(BasePage):
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/igroups'
        super(InitiatorGroupsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchIGroups"]'

        # 'Create' button (with drop-down menu list) on grid's toolbar
        self._selectors['menuCreate'] = '//a[@data-mg-comp="initiatorgroupgrid-create"]'
        self._selectors['mItmCreate'] = '//div[@data-mg-comp="initiatorgroupgrid-create-btn-menu"]'

        # 'Edit' button (with drop-down menu list) on grid's toolbar
        self._selectors['menuEdit'] = '//a[@data-mg-comp="properties"]'
        self._selectors['mItmEdit'] = '//div[@data-mg-comp="igroup-grid-edit-properties-btn-menu"]'

        # 'Delete' and 'Refresh' buttons on grid's toolbar
        self._selectors['btnDelete'] = '//a[@data-mg-comp="deleteIGroup_ToolBtn"]'
        self._selectors['btnRefresh'] = '//div[@data-mg-comp="igroups-grid"]/div[starts-with(@id, "toolbar")]/div/div/a[@data-mg-comp="refresh_ToolBtn"]'

        # Initiator Groups main grid
        self._selectors['gridInitiatorGroups'] = '//div[@data-mg-comp="igroups-grid"]'

    def setupComponents(self):
        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver,
            selector=self.selectors.sBoxSearch)

        self.components['menuCreate'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuCreate)
        self.components['mItmCreate'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmCreate)
        self.mItmCreate.mapItems(items=['Initiator Group', 'LUNs'])
        self.menuCreate.addItems(items=self.mItmCreate)

        self.components['menuEdit'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuEdit)
        self.components['mItmEdit'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmEdit)
        self.mItmEdit.mapItems(items=['Name', 'Initiators', 'OS Type'])
        self.menuEdit.addItems(items=self.mItmEdit)

        self.components['btnDelete'] = button.Button(driver=self.driver,
            selector=self.selectors.btnDelete)
        self.components['btnRefresh'] = button.Button(driver=self.driver,
            selector=self.selectors.btnRefresh)

        self.components['gridInitiatorGroups'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridInitiatorGroups)

        # Component uniquely identifying given page
        self.components['token'] = self.sBoxSearch
