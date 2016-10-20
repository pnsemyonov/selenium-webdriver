from base_page import *


class LUNDetailsPage(BasePage):
    """
        Page which open when user clicks on LUN name in LUNs grid.
    """
    def __init__(self, **kwargs):
        super(LUNDetailsPage, self).__init__(**kwargs)

    def setupSelectors(self):
        # LUN name next to label 'LUN:'
        self._selectors['lblTitle'] = '//div[@data-mg-comp="manager-header-title"]'
        # LUN stats (Online/Offline, size, number of snapshots) below title
        self._selectors['lblSubtitle'] = '//div[@data-mg-comp="manager-sub-header"]'

        # Tab 'Snapshots'
        self._selectors['tabSnapshots'] = '//div[@data-mg-comp="manager-storage-clusterview-lundetails-tpanel"]/div[contains(@class, "x-tab-bar")]/div[contains(@class, "x-tab-bar-body")]/div[contains(@id, "tabbar")]/div/a[1]'
        # Tab 'Clone History'
        self._selectors['tabCloneHistory'] = '//div[@data-mg-comp="manager-storage-clusterview-lundetails-tpanel"]/div[contains(@class, "x-tab-bar")]/div[contains(@class, "x-tab-bar-body")]/div[contains(@id, "tabbar")]/div/a[2]'

        # Menu 'Actions'
        self._selectors['menuActions'] = '//a[@data-mg-comp="mg-header-action-button"]'
        # Items of menu 'Actions'
        # TODO: File an improvement bug to assign data-mg-comp to <div>.
        self._selectors['mItmActions'] = '//body/div[14]'
        # Items of menu 'Actions -> Edit'
        self._selectors['mItmActionsEdit'] = '//body/div[16]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblSubtitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSubtitle, name=self.name)

        self.components['tabSnapshots'] = button.Button(driver=self.driver,
            selector=self.selectors.tabSnapshots, name=self.name)
        self.components['tabCloneHistory'] = button.Button(driver=self.driver,
            selector=self.selectors.tabCloneHistory, name=self.name)

        # Menu 'Actions'
        self.components['menuActions'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuActions, name=self.name)
        self.components['mItmActions'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmActions, name=self.name)
        self.components['mItmActionsEdit'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmActionsEdit, name=self.name)
        self.mItmActionsEdit.mapItems(items=['Name', 'Size', 'Online', 'Offline'])
        self.mItmActions.mapItems(items=['Create Snapshot Copy', 'Edit', 'Clone', 'Delete'])
        self.mItmActions.addItems(item='Edit', childItems=self.mItmActionsEdit)
        self.menuActions.addItems(items=self.mItmActions)

        # Component uniquely identifying given page
        self.components['token'] = self.tabSnapshots