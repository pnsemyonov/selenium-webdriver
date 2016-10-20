import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/.."))

import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from component import *
from frlog import LOG
from mariner.timeout import Timeout
from mangal.exceptions import *


class BasePage(object):
    class Selector(object):
        """
            In-transit class allowing use of '<some_page>.selectors.<some_selector>' notation for
              obtaining element selectors from page (ex. 'loginPage.selectors.btnSignIn')
        """
        def __init__(self, selectors):
            self.selectors = selectors

        def __getattr__(self, selectorName):
            # Obtaining parameterized selectors (ex. LoginPage().btnLocaleByIndex(index=2)). Used in
            #   selectors like 'div:nth-child(5)' or '//div[.="some_text"]'. Supporting multiple
            #   arguments: 'div[id^="{some_id}"] > tr[class="{some_class}"]'. You are naming
            #   arguments (argument name enclosed in curly brackets) as you like, but keep
            #   declaration and call consistent.
            #   Declaration:
            #     selectors['numberOfLUNsItm'] = '//body/div[contains(@class, "{class}")]/div/ul/li[.="{index}"]'
            #   Call:
            #     lunsPage.selectors.numberOfLUNsItm(class='mg-list-lun-count', index='12')
            if re.search('{(.*?)}', self.selectors[selectorName]):
                # Passed name of element (ex. 'btnLocaleByIndex') as it's defined on its page
                #   (LoginPage etc.)
                self.selectorName = selectorName
                # Build raw method instance without concrete arguments
                selector = self._getParameterizedSelector
            else:
                selector = self.selectors[selectorName]
            return selector

        def _getParameterizedSelector(self, **kwargs):
            """
                Method obtains argument passed to __getattr__ along with selector name (ex.
                  LoginPage().selectors.btnLocaleByIndex(index=2)), then converts parameterized
                  selector string to target selector.
            """
            # Get selector string by given selector name (self.selectorName), then replace
            #   placeholder {<argument_name>} with given argument (ex. 'div[{index}] -> 'div[3]')
            selector = self.selectors[self.selectorName]
            # Pull out of selector all arguments as list. Ex.
            #   '//div[@class="{className}"]/div[{index}]' -> ['className', 'index']
            arguments = re.findall('{(.*?)}', self.selectors[self.selectorName])
            try:
                # For all argument placeholders (ex. '{number}') found in selector, replace them
                #   with concrete values
                for argument in arguments:
                    selector = selector.replace('{' + argument + '}', str(kwargs[argument]))
            except KeyError:
                raise KeyError('Argument mismatch:\n%s\n%s' % (self.selectors[self.selectorName],
                    str(kwargs)))
            return selector

    def __init__(self, driver, protocol='http', url='', path='', parentName='',
    validateLayout=False):
        self.driver = driver
        self.webDriver = self.driver.getWebDriver()
        self.path = path
        self.url = protocol + '://' + url
        self.validateLayout = validateLayout
        # In wizards, pages can be instantiated with parameter parentName=<wizard_name> to make a
        #   page appeared in logs as ex. 'CloneLUNWizard.SelectInitiatorGroupsPage'
        self.name = ((parentName + '.') if parentName else '') + self.__class__.__name__
        self._selectors = {}
        self.setupSelectors()
        self.components = {}
        self.setupComponents()

    def __getattr__(self, attributeName):
        """
            Attempt to return Element instance by given page element name (ex. 'usernameBox'). If
              named element is absent in page declaration, return attribute of underlying
              selenium.webdriver.remote.webelement.WebElement.
        """
        if attributeName == 'selectors':
            attribute = self.Selector(selectors=self._selectors)
        # Used in base_page.isOpen() for inspection if page's unique component is present (hence
        #   page is open).
        elif attributeName == 'token':
            attribute = self.components['token']
        elif attributeName in self.components:
            attribute = self.components[attributeName]
            attribute.name = '.'.join([self.name, attributeName])
        else:
            raise AttributeError('%s: Invalid attribute: %s' % (self.name, attributeName))
        return attribute

    def setupSelectors(self):
        """
            Define selectors of web page. To be overwritten in concrete pages.
        """
        pass

    def setupComponents(self):
        """
            Define components (sub-classed BaseComponents) of web page. To be overwritten in
              concrete pages.
        """
        pass

    def doValidation(self):
        """
            Validate non-functional requirements of components of page. To be overwritten in
              concrete pages.
        """
        LOG.l3('%s.doValidation(): No validation added.', self.name)

    def open(self, wait=True):
        """
            Open web page in browser.
        """
        LOG.l4("%s.open(): URL='%s'" % (self.name, self.url))
        self.webDriver.get(self.url)
        if wait:
            try:
                self.waitUntilOpen()
            except PageException:
                pass
        if self.validateLayout:
            self.doValidation()
        LOG.l4("%s.open(): Done." % self.name)

    def isOpen(self, suppressLog=False):
        """
            Check if page is loaded and visible by verifying if its unique components ('token') are
              present and visible on page.
            Can be overwritten in sub-classes for better page recognition by inspecting multiple
              page-specific components.
        """
        if hasattr(self, 'token'):
            if not isinstance(self.token, list):
                tokens = [self.token]
            else:
                tokens = self.token
            isOpen = True
            for token in tokens:
                if not (token.isPresent() and token.isVisible()):
                    isOpen = False
                    break
        else:
            raise PageException(message=('%s: Page token is not defined.' % self.name),
                driver=self.driver, screenshotName=self.name + '.isOpen')
        if not suppressLog:
            LOG.l4('%s.isOpen(): %s' % (self.name, isOpen))
        return isOpen

    def reload(self):
        self.webDriver.refresh()
        LOG.l4("%s.reload(): url='%s'" % (self.name, self.url))

    def waitUntilLoaded(self):
        """
            Generic solution, may not be the best in any case. More robust approach is to verify
              presence/readiness of an element belonging to particular page.
        """
        try:
            WebDriverWait(driver=self.webDriver, timeout=self.driver.timeout).until(lambda _:
            self.webDriver.execute_script(script='return document.readyState') == 'complete')
        except TimeoutException:
            raise PageException(message="%s.waitUntilLoaded: Time out." % self.name,
                driver=self.driver, screenshotName=self.name + '.waitUntilLoaded')
        LOG.l4('%s.waitUntilLoaded()' % self.name)

    def waitUntilOpen(self, suppressLog=False):
        """
            Customized solution doing inspection of presence and visibility of page-specific
              components.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilOpen(): Time out.' %
            self.name)
        while not self.isOpen(suppressLog=True):
            if timeout.exceeded(raiseException=False):
                raise PageNotFoundException(message='%s.waitUntilOpen(): Time out.' % self.name,
                    driver=self.driver, screenshotName=self.name + '.waitUntilOpen')
            time.sleep(self.driver.delay)
        if not suppressLog:
            LOG.l5('%s.waitUntilOpen()' % self.name)

    def waitUntilClosed(self):
        """
            Customized solution doing inspection of absence or invisibility of page-specific
              components.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilClosed(): Time out.'
            % self.name)
        while self.isOpen(suppressLog=True):
            if timeout.exceeded(raiseException=False):
                raise PageException(message='%s.waitUntilClosed(): Time out.' % self.name,
                    driver=self.driver, screenshotName=self.name + '.waitUntilClosed')
            time.sleep(self.driver.delay)
        LOG.l5('%s.waitUntilClosed()' % self.name)
