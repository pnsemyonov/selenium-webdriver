"""
    Base class for Mangal components.
"""

import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../lib"))

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException
from frlog import LOG
from mariner.timeout import Timeout
from mangal.exceptions import ComponentException, ComponentFailedStateException, \
    ComponentNotFoundException


class BaseComponent(object):
    """
        Base class for all derived components such as Label, Menu, Grid etc. Provides:
          - Creation of component using given XPath selector
          - Recovery of component after StaleElementReferenceException occurred on dynamic web pages
          - Base functionality of components
          - Access to native attributes of underlying WebDriver.WebElement
          - State inspection
          - Access to child components of component
    """


    class Element(object):
        """
            Wrapper for WebDriver.WebElement. Translates attribute calls to WebElement attribute
              calls. Provides recovery of underlying WebElement in case of
              StaleElementReferenceException.
        """
        def __init__(self, driver, selector, name):
            self.driver = driver
            self.selector = selector
            self.webDriver = driver.getWebDriver()
            self.element = None
            self.name = name

        def __getattr__(self, attributeName):
            # Acquires attributes names corresponding WebElement's ones (ex. 'find_element' etc.)
            self.attributeName = attributeName
            return self.callAttribute

        def callAttribute(self, *args, **kwargs):
            """
                Translates attribute names to corresponding attribute calls. Takes care of
                  named/unnamed parameters.
                @param args: Unnamed parameters (ex. 'admin' in send_keys('admin')). Optional.
                @param kwargs: Named parameters (ex. {'name': 'class'} in
                  get_attribute(name='class'))
            """
            timeout = Timeout(timeout=self.driver.timeout, description="%s.element.%s(%s, %s): selector='%s'. Time out."
                % (self.name, self.attributeName, args, kwargs, self.selector))
            while True:
                if not timeout.exceeded(raiseException=False):
                    if self.element is None:
                        try:
                            # Base web element of component, instance of WebDriver.WebElement. In
                            #   complex components, such as ComboBox or Grid, it is head element
                            #   which all other element/components are related to as children.
                            self.element = self.webDriver.find_element_by_xpath(xpath=self.selector)
                        except NoSuchElementException:
                            self.element = None
                            time.sleep(self.driver.delay)
                            continue
                    try:
                        attribute = getattr(self.element, self.attributeName)
                        # TODO: Investigate if there more elegant solutions are.
                        if callable(attribute):
                            if len(args) and len(kwargs):
                                result = attribute(*args, **kwargs)
                            elif len(args):
                                result = attribute(*args)
                            elif len(kwargs):
                                result = attribute(**kwargs)
                            else:
                                result = attribute()
                        else:
                            result = attribute
                        break
                    except (StaleElementReferenceException, ElementNotVisibleException):
                        self.element = None
                        time.sleep(self.driver.delay)
                else:
                    raise ComponentNotFoundException(message="%s.element.%s(%s, %s): selector='%s'. Time out."
                    % (self.name, self.attributeName, args, kwargs, self.selector),
                    driver=self.driver, takeScreenshot=False)
            LOG.l5('%s.element.%s(%s, %s)' % (self.name, self.attributeName, args, kwargs))
            return result


    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver..
            @param selector: XPath of head (base) web element of component.
            @param name: Name of parent page as <page_class_name> (ex. 'LoginPage').
        """
        self.driver = driver
        self.webDriver = self.driver.getWebDriver()
        self.selector = selector
        # Add component name to page class name (ex. 'LoginPage.btnSignIn')
        self.name = name + '.' + self.__class__.__name__
        self.element = self.Element(driver=self.driver, selector=self.selector, name=self.name)

    def getAttribute(self, attributeName, suppressLog=False):
        """
            Returns attribute of HTML node of base WebElement of component such as 'id', 'class',
              'data-mg-comp' etc. Do not confuse with Python object's attribute which __getattr__
              above deals with.
            @param attributeName: Name of attribute of HTML node.
            @return: Attribute of HTML node.
        """
        attribute = self.element.get_attribute(name=attributeName)
        if not suppressLog:
            LOG.l5("%s.getAttribute(attributeName='%s'): '%s'" % (self.name, attributeName,
                attribute))
        return attribute

    def getCSSProperty(self, propertyName):
        """
            Return value of CSS property of base element (value of property consisted in attribute
              'style'). Ex. <div style='display:none'>, where getCSSProperty(propertyName='display')
              will be 'none'.
            @param propertyName: Name of CSS property (ex. 'border-style', 'background-color').
            @return: Value of CSS property (ex. 'solid dotted', 'red').
        """
        cssProperty = self.element.value_of_css_property(property_name=propertyName)
        LOG.l5("%s.getCSSProperty(%s): '%s'" % (self.name, propertyName, cssProperty))
        return cssProperty

    def isPresent(self, suppressLog=False):
        """
            Inspects if element is present (can be found) in DOM.
              Note: This is not equal to isVisible(), as element could be present in DOM but hidden.
            @return: True if present, otherwise False.
        """
        try:
            # To determine if component is present, we just 'touch' it using __getattr__ above with
            #   any attribute.
            if self.element.id():
                isPresent = True
        except ComponentNotFoundException:
            isPresent = False
        if not suppressLog:
            LOG.l5('%s.isPresent(): %s' % (self.name, isPresent))
        return isPresent

    def waitUntilPresent(self):
        """
            Wait until base element of component is present in DOM. Useful for checking if web page
              or component have been loaded.
              Note: Present <> enabled, element can easily be disabled still being present.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilPresent(): Time out.'
            % self.name)
        while not self.isPresent(suppressLog=True):
            if timeout.exceeded(raiseException=False):
                raise ComponentNotFoundException(message='%s.waitUntilPresent(): Time out.' %
                self.name, driver=self.driver, screenshotName=self.name + '.waitUntilPresent')
            time.sleep(self.driver.delay)
        LOG.l5('%s.waitUntilPresent()' % self.name)

    def waitUntilAbsent(self):
        """
            Wait until base element of component has completely disappeared from DOM.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilAbsent(): Time out.'
            % self.name)
        while self.isPresent(suppressLog=True):
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.waitUntilAbsent(): Time out.' %
                self.name, driver=self.driver, screenshotName=self.name + '.waitUntilAbsent')
            time.sleep(self.driver.delay)
        LOG.l5('%s.waitUntilAbsent()' % self.name)

    def isVisible(self, suppressLog=False):
        """
            Inspect if base HTML element is visible. Setting <... style='display:none>' hides
              element from visibility on web page, still retaining it in DOM.
            @return: True if base element of component visible, otherwise False.
        """
        try:
            isVisible = self.element.is_displayed()
        except ComponentNotFoundException:
            isVisible = False
        if not suppressLog:
            LOG.l5('%s.isVisible(): %s' % (self.name, isVisible))
        return isVisible

    def waitUntilVisible(self):
        """
            Wait until base element of component has become visible on web page.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilVisible(): Time out.'
            % self.name)
        while not self.isVisible(suppressLog=True):
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.waitUntilVisible(): Time out.' %
                self.name, driver=self.driver, screenshotName=self.name + '.waitUntilVisible')
            time.sleep(self.driver.delay)
        LOG.l5('%s.waitUntilVisible()' % self.name)

    def waitUntilHidden(self):
        """
            Wait until base element of component became invisible on web page; still, it's present
              in DOM, the same as isDisplayed() == False.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilHidden(): Time out.'
            % self.name)
        while self.isVisible(suppressLog=True):
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.waitUntilHidden(): Time out.' %
                self.name, driver=self.driver, screenshotName=self.name + '.waitUntilHidden')
            time.sleep(self.driver.delay)
        LOG.l5('%s.waitUntilHidden()' % self.name)

    def getChild(self, relativePath):
        """
            Returns child web element of component (wrapped in BaseComponent) using relative XPath.
            @param relativePath: XPath of child element in reference to selector of component.
            @return: Instance of BaseComponent with found child element as base element.
        """
        # Sanitize relative path to remove duplicated '/' and ensure leading one
        childPath = self.selector + '/' + '/'.join(filter(None, relativePath.split('/')))
        try:
            if self.element.find_element_by_xpath(xpath=childPath):
                childComponent = BaseComponent(driver=self.driver, selector=childPath,
                name=self.name + '.child')
        except (NoSuchElementException, ComponentNotFoundException):
            raise ComponentNotFoundException(message="%s.getChild(relativePath='%s'): Child component not found."
            % (self.name, childPath), driver=self.driver, screenshotName=self.name + '.getChild')
        return childComponent

    def getChildren(self, relativePath):
        """
            Returns child web elements of component (wrapped in instances of BaseComponent) using
              relative XPath. Used, as example, for finding item elements in menu item list.
            @param relativePath: XPath of child elements in reference to selector of component.
            @return: List of instances of BaseComponent with found child elements as base elements.
        """
        # Sanitize path to remove duplicated '/' and ensure leading one
        relativePath = '/' + '/'.join(filter(None, relativePath.split('/')))
        children = []
        childIndex = 1
        while True:
            childPath = self.selector + relativePath + '[%s]' % str(childIndex)
            try:
                if self.element.find_element_by_xpath(xpath=childPath):
                    childComponent = BaseComponent(driver=self.driver, selector=childPath,
                    name=self.name + '.child')
                    children.append(childComponent)
            except NoSuchElementException:
                break
            childIndex += 1
        return children
