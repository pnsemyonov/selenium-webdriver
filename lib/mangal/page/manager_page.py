from base_page import *


class ManagerPage(BasePage):
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(ManagerPage, self).__init__(path=path, **kwargs)

    def setupElements(self):
        self.elements['btnLUNs'] = '//a[@data-mg-comp="mg-nav-lun-shortcut"]'
        self.elements['btnCreateLUNs'] = '//a[@data-mg-comp="mg-nav-lun-create"]'
        self.elements['btnClusterHealth'] = '//a[@data-mg-comp="nav-health"]'
        self.elements['btnBasicSettings'] = '//a[@data-mg-comp="nav-settings"]'
        self.elements['btnNetworks'] = '//a[@data-mg-comp="nav-networks"]'
        self.elements['btnSoftware'] = '//a[@data-mg-comp="nav-software"]'
        self.elements['btnNodes'] = '//a[@data-mg-comp="nav-nodes"]'
        self.elements['btnInventory'] = '//a[@data-mg-comp="nav-inventory"]'
        self.elements['btnHardwareHealth'] = '//a[@data-mg-comp="nav-hardware-health"]'

    def setupComponents(self):
        self.components['btnLUNs'] = button.Button(driver=self.driver,
            selector=self.selectors.btnLUNs, name=self.name)
        self.components['btnCreateLUNs'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCreateLUNs, name=self.name)
        self.components['btnClusterHealth'] = button.Button(driver=self.driver,
            selector=self.selectors.btnClusterHealth, name=self.name)
        self.components['btnBasicSettings'] = button.Button(driver=self.driver,
            selector=self.selectors.btnBasicSettings, name=self.name)
        self.components['btnNetworks'] = button.Button(driver=self.driver,
            selector=self.selectors.btnNetworks, name=self.name)
        self.components['btnSoftware'] = button.Button(driver=self.driver,
            selector=self.selectors.btnSoftware, name=self.name)
        self.components['btnNodes'] = button.Button(driver=self.driver,
            selector=self.selectors.btnNodes, name=self.name)
        self.components['btnInventory'] = button.Button(driver=self.driver,
            selector=self.selectors.btnInventory, name=self.name)
        self.components['btnHardwareHealth'] = button.Button(driver=self.driver,
            selector=self.selectors.btnHardwareHealth, name=self.name)
