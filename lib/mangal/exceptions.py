"""
    Exception definitions for Mangal.
"""

import sys
import os

sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../lib"))

import inspect
from frexceptions import FRException
from frlog import LOG

__all__ = [
    'MangalException',
    'DriverException',
    'PageException',
    'PageNotFoundException',
    'ComponentException',
    'ComponentNotFoundException'
]


class MangalException(FRException):
    """
        Web UI-related exceptions.
    """
    def __init__(self, message, driver, takeScreenshot=True, screenshotName=None):
        super(MangalException, self).__init__(message)
        if takeScreenshot:
            if screenshotName is None:
                # Compose screenshot name out of records in call stack.
                #   Ex.: test_create_luns_wizard.goNext.waitUntilOpen.isOpen.__init__.20150910_150554.png
                screenshotName = '.'.join([record[3] for record in reversed(inspect.stack()[:-7])])
            driver.takeScreenshot(name=screenshotName)


class DriverException(MangalException):
    pass


class PageException(MangalException):
    pass


class PageNotFoundException(PageException):
    pass


class ComponentException(MangalException):
    pass

class ComponentStaleStateException(ComponentException):
    """
        Thrown when wrapped WebElement of component becomes stale after
          StaleElementReferenceException.
    """
    pass

class ComponentFailedStateException(ComponentException):
    """
        Thrown when component has failed state. As example, component is visible while expectation
          is to have it hidden; or button is non-clickable while performing click.
    """
    pass

class ComponentNotFoundException(ComponentException):
    """
        Thrown when component could not be found on web page.
          If you encounter this exception, you may want to check the following:
            - selector associated with component defined on a page (LoginPage() etc.)
            - if page is loaded in browser
    """
    pass
