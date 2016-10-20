from base_page import *


class AllStoragePage(BasePage):
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(AllStoragePage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        self._selectors['lblTitle'] = '//div[@data-mg-comp="manager-header-title"]'

        self._selectors['tabLUNs'] = '//div[@data-mg-comp="manager-storage-clusterview-tpanel"]/div[1]/div[1]/div[2]/div/a[1]'
        self._selectors['tabConsistencyGroups'] = '//div[@data-mg-comp="manager-storage-clusterview-tpanel"]/div[1]/div[1]/div[2]/div/a[2]'
        self._selectors['tabInitiatorGroups'] = '//div[@data-mg-comp="manager-storage-clusterview-tpanel"]/div[1]/div[1]/div[2]/div/a[last()]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['tabLUNs'] = button.Button(driver=self.driver,
            selector=self.selectors.tabLUNs, name=self.name)
        self.components['tabConsistencyGroups'] = button.Button(driver=self.driver,
            selector=self.selectors.tabConsistencyGroups, name=self.name)
        self.components['tabInitiatorGroups'] = button.Button(driver=self.driver,
            selector=self.selectors.tabInitiatorGroups, name=self.name)

        # Component uniquely identifying given page
        self.components['token'] = self.tabLUNs
