import random
from base_page import *
from header_page import HeaderPage


class LoginPage(BasePage):
    def __init__(self, **kwargs):
        path = '#dashboard'
        super(LoginPage, self).__init__(path=path, **kwargs)
        self.locale = None

    def setupSelectors(self):
        # Company branding elements
        self._selectors['imgCompanyLogo'] = '//img'
        self._selectors['lblProductName'] = '//div[contains(@class, "login-body")]/div/div/div[starts-with(@id, "container")]/span/div/div/div[contains(@id, "header")]/div/div/div/div/span'
        self._selectors['lblProductVersion'] = '//span[@class="mg-mars-version"]'

        # Input controls
        self._selectors['lblUsername'] = '//table[@data-mg-comp="username"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        self._selectors['txtUsername'] = '//input[@name="username"]'
        self._selectors['imgInvalidUsername'] = '//table[@data-mg-comp="username"]/tbody/tr/td[contains(@id, "sideErrorCell")]/div'
        self._selectors['lblPassword'] = '//table[@data-mg-comp="password"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        self._selectors['txtPassword'] = '//input[@name="password"]'
        self._selectors['imgInvalidPassword'] = '//table[@data-mg-comp="password"]/tbody/tr/td[contains(@id, "sideErrorCell")]/div'
        self._selectors['btnSignIn'] = '//a[@data-mg-comp="signInButton"]'

        # Links on help menu
        self._selectors['linkHelp'] = '//a[@class="hlp"]'
        self._selectors['linkSupport'] = '//a[@target="_blank"]'
        self._selectors['linkNetApp'] = '//a[@class="netApp"]'

        # Menu button 'Locale' and its item list
        self._selectors['menuLocale'] = '//div[@data-mg-comp="localeSelector"]/a'
        self._selectors['mItmLocale'] = '//div[@data-mg-comp="locales"]'

    def setupComponents(self):
        self.components['imgCompanyLogo'] = image.Image(driver=self.driver,
            selector=self.selectors.imgCompanyLogo, name=self.name)
        self.components['lblProductName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblProductName, name=self.name)
        self.components['lblProductVersion'] = label.Label(driver=self.driver,
            selector=self.selectors.lblProductVersion, name=self.name)
        self.components['lblUsername'] = label.Label(driver=self.driver,
            selector=self.selectors.lblUsername, name=self.name)
        self.components['txtUsername'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtUsername, name=self.name)
        self.components['lblPassword'] = label.Label(driver=self.driver,
            selector=self.selectors.lblPassword, name=self.name)
        self.components['txtPassword'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtPassword, name=self.name)
        self.components['btnSignIn'] = button.Button(driver=self.driver,
            selector=self.selectors.btnSignIn, name=self.name)

        self.components['linkHelp'] = link.Link(driver=self.driver,
            selector=self.selectors.linkHelp, name=self.name)
        self.components['linkSupport'] = link.Link(driver=self.driver,
            selector=self.selectors.linkSupport, name=self.name)
        self.components['linkNetApp'] = link.Link(driver=self.driver,
            selector=self.selectors.linkNetApp, name=self.name)

        self.components['menuLocale'] = menu.Menu(driver=self.driver,
            selector=self.selectors.menuLocale, name=self.name)
        self.components['mItmLocale'] = menu.MenuItems(driver=self.driver,
            selector=self.selectors.mItmLocale, name=self.name)
        self.mItmLocale.mapItems(items=['en', 'es', 'de', 'fr', 'ja', 'ko', 'zh'])
        self.menuLocale.addItems(items=self.mItmLocale)
        # Component uniquely identifying given page
        self.components['token'] = self.lblProductName

    def getRandomLocale(self):
        """
            Returns locale selected randomly ('en', 'es' etc.)
        """
        locales = ['en', 'es', 'de', 'fr', 'ja', 'ko', 'zh']
        return locales[random.randint(0, len(locales) - 1)]

    def selectLocale(self, locale):
        """
            Select locale from login page's locale menu by mapping locale abbreviation to
              corresponding index of menu item.
            @param locale: Locale abbreviation, one of: 'en', 'es', 'de', 'fr', 'ja', 'ko', 'zh'.
        """
        self.menuLocale.select(item=locale)
        LOG.l4('Set locale:', locale)

    def signIn(self, username, password, locale=None, openPage=True):
        LOG.l4('Logging in')
        if openPage and (not self.isOpen()):
            self.open()
            self.waitUntilOpen()

        self.selectLocale(locale)

        self.txtUsername.setText(username)
        LOG.l4('Set username:', username)

        self.txtPassword.setText(password)
        LOG.l4('Set password:', password)

        self.btnSignIn.waitUntilEnabled()
        self.btnSignIn.click()
        LOG.l5("Clicked button 'Sign In'.")

        HeaderPage(driver=self.driver).waitUntilOpen()
        LOG.l4('Login performed.')
