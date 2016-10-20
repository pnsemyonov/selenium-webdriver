from base_page import *


class LoginFailedPage(BasePage):
    def __init__(self, **kwargs):
        path = '#dashboard'
        super(LoginFailedPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        self._selectors['lblTitle'] = '//div[contains(@class, "mg-message-box")]/div[contains(@id, "header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        self._selectors['lblDescription'] = '//div[contains(@class, "mg-message-box")]/div[contains(@id, "body")]/span/div/div[@data-mg-comp="msg"]/span/div'
        self._selectors['btnOK'] = '//div[@data-mg-comp="footer"]/div/div/a'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblDescription'] = label.Label(driver=self.driver,
            selector=self.selectors.lblDescription, name=self.name)
        self.components['btnOK'] = button.Button(driver=self.driver, selector=self.selectors.btnOK,
            name=self.name)
