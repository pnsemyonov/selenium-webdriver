from base_page import *


class HeaderPage(BasePage):
    def __init__(self, **kwargs):
        path = '#dashboard'
        super(HeaderPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        self._selectors['btnDashboard'] = '//a[@data-mg-comp="show-dashboard-button"]'
        self._selectors['btnManager'] = '//a[@data-mg-comp="show-manager-button"]'
        self._selectors['lblTitle'] = '//div[@data-mg-comp="cluster-name"]'

        # Menu 'User' at top-right
        self._selectors['menuUser'] = '//a[@data-mg-comp="user-button"]'

        # Menu item list under 'User' button
        self._selectors['mItmUser'] = '//div[@data-mg-comp="mars-header-user-menu"]'

        # Menu 'Info' (shown as '?') at top-right
        self._selectors['menuInfo'] = '//a[@data-mg-comp="infobutton"]'

        # Menu item list under 'Info' button
        self._selectors['mItmInfo'] = '//div[@data-mg-comp="mars-header-info-menu"]'

    def setupComponents(self):
        self.components['btnDashboard'] = button.Button(driver=self.driver,
            selector=self.selectors.btnDashboard, name=self.name)
        self.components['btnManager'] = button.Button(driver=self.driver,
            selector=self.selectors.btnManager, name=self.name)
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)

        self.components['menuUser'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuUser, name=self.name)
        self.components['mItmUser'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmUser, name=self.name)
        self.mItmUser.mapItems(items=['Change Password', 'Sign Out'])
        self.menuUser.addItems(items=self.mItmUser)

        self.components['menuInfo'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuInfo, name=self.name)
        self.components['mItmInfo'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmInfo, name=self.name)
        self.mItmInfo.mapItems(items=['About this Cluster', 'Technical Support',
            'Help on System Manager'])
        self.menuInfo.addItems(items=self.mItmInfo)
        # Component uniquely identifying given page
        self.components['token'] = self.btnDashboard
