try:
    import selenium
except ImportError:
    raise ImportError("As root Install python-selenium by running: 'pip install selenium'")

import os
import time

import express
from frlog import LOG
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Driver(object):
    """
        Wrapper for Selenium Remote WebDriver class.
    """
    def __init__(self, driverHostname, driverPort, browser, maximizeWindow=True):
        """
            @param driverHostname: Host name on which instance of Remote WebDriver is running.
              Ex. 'mvm-win35'
            @param driverPort: Port number which WebDriver is communicating over. Ex. 4444
            @param browser: Type of browser which is open by WebDriver: 'firefox' or 'chrome'.
            @param maximizeWindow: If True (default), maximize newly opened window in browser.
        """
        LOG.info('Instantiating Mangal.Driver...')
        self.driverHostname = driverHostname
        self.driverPort = driverPort
        self.browser = browser
        self.timeout = 10
        self.delay = .3
        self._maximizeWindow = maximizeWindow
        self._start()

    def _start(self):
        self.capabilities = None
        if self.browser == 'firefox':
            self.capabilities = DesiredCapabilities.FIREFOX.copy()
        elif self.browser == 'chrome':
            self.capabilities = DesiredCapabilities.CHROME.copy()
        else:
            raise FailedConfigException('Unsupported type of browser:', browser)
        self.webDriver = webdriver.Remote(command_executor='http://%s:%s/wd/hub' %
        (self.driverHostname, self.driverPort), desired_capabilities=self.capabilities)
        if self._maximizeWindow:
            self.maximizeWindow()

    def getWebDriver(self):
        return self.webDriver

    def forward(self):
        LOG.l4('Navigating forward in browser history')
        self.webDriver.forward()

    def back(self):
        LOG.l4('Navigating back in browser history')
        self.webDriver.back()

    def close(self):
        LOG.l4('Closing browser active window')
        try:
            self.webDriver.close()
        except WebDriverException, e:
            LOG.l4('WebDriver.close():', e.msg)

    def quit(self):
        LOG.l4('Quitting WebDriver')
        try:
            self.webDriver.quit()
        except WebDriverException, e:
            LOG.l4('WebDriver.quit():', e.msg)

    def maximizeWindow(self):
        """
            Maximize browser's active window
        """
        self.webDriver.maximize_window()

    def takeScreenshot(self, name):
        """
            Save screenshot of active web page to PNG file.
            @param name: Name of screenshot file.
        """
        if LOG.getLogDir() is not None:
            logDirectory = LOG.getLogDir()
        else:
            logDirectory = os.getcwd()
        pathFileName = os.path.join(logDirectory, name + '.' +
            express.getUnixTime(formatstr='%Y%m%d_%H%M%S') + '.png')
        self.webDriver.save_screenshot(pathFileName)
        LOG.l4("Mangal.Driver: takeScreenshot(): Saved into '%s'" % pathFileName)

    def setBrowser(self, browser):
        self.browser = browser
