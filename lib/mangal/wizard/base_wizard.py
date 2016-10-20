import re
from collections import OrderedDict
from frlog import LOG
from mangal.exceptions import PageNotFoundException


class BaseWizard(object):
    """
        Model wizard (multi-page dialog).
        Wizard serves as container of its page and implements access and basic navigation between
          them. Page utility methods are implemented in page classes.
    """
    def __init__(self, driver):
        self.driver = driver
        self._pages = OrderedDict()
        self.activePageNumber = -1
        self.activePage = None
        self.name = self.__class__.__name__

    def __getattr__(self, attributeName):
        # Get page as class attribute by page's name
        if attributeName in self._pages:
            attribute = self._pages[attributeName]
        else:
            raise AttributeError("%s.__getattr__(attributeName='%s'): Attribute not found." %
            (self.name, attributeName))
        return attribute

    def __getitem__(self, item):
        # Get page by its name (ex. wizard['frontPage'])
        if isinstance(item, str):
            if item in self._pages:
                value = self._pages[item]
            else:
                raise PageNotFoundException(message='%s: Page not found: %s' % (self.name, item),
                    driver=self.driver)
        # Get page by its index (ex. wizard[3])
        elif isinstance(item, int):
            if 0 <= item < len(self):
                value = self._pages[self._pages.keys()[item]]
            else:
                raise IndexError('%s: Page not found: [%s]' % (self.name, item))
        else:
            raise ValueError('%s: Invalid page specifier type: %s' % (self.name, type(item)))
        return value

    def __iter__(self):
        for pageName in self._pages:
            yield self._pages[pageName]

    def __len__(self):
        return len(self._pages)

    def getActivePage(self):
        return self.activePage

    def getActivePageNumber(self):
        return self.activePageNumber

    def addPage(self, name, page):
        """
            Add page to wizard.
            @param name: Name of page as it will appear in wizard
            @param: Instance of wizard's page (ex. DefineLUNsPage(driver))
        """
        self._pages[name] = page

    def open(self):
        """
            Steps to open dialog (ex. close active dialog, navigate to particular page, open menu
              etc. To be overwritten in sub-class.
        """
        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        pass

    def goNext(self):
        """
            Navigate to next page of dialog by clicking on button 'Next'.
            Can be overwritten in sub-class to address page's specifics (say, page has button
              'btnFinish' rather than 'btnNext').
        """
        # Active page has own method 'goNext'
        if hasattr(self.activePage, 'goNext') and callable(self.activePage.goNext):
            self.activePage.goNext()
            self[self.activePageNumber + 1].waitUntilOpen()
            self.activePageNumber += 1
            self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        # Active page has no method 'goNext', thus use wizard's generic solution
        elif hasattr(self.activePage, 'btnNext'):
            self.activePage.btnNext.waitUntilEnabled()
            self.activePage.btnNext.click()
            # Wait for next page of dialog to be open
            self[self.activePageNumber + 1].waitUntilOpen()
            self.activePageNumber += 1
            self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        else:
            raise PageException(message='%s.%s.goNext(): Cannot proceed to next page.' % (self.name,
                self.activePage.name), driver=self.driver, screenshotName=self.name + '.goNext')

    def goBack(self):
        """
            Navigate back to previous page of dialog by clicking on button 'Back'.
            Can be overwritten in sub-class.
        """
        if hasattr(self.activePage, 'goBack') and callable(self.activePage.goBack):
            self.activePage.goBack()
            self[self.activePageNumber - 1].waitUntilOpen()
            self.activePageNumber -= 1
            self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        elif hasattr(self.activePage, 'btnBack'):
            self.activePage.btnBack.waitUntilEnabled()
            self.activePage.btnBack.click()
            # Wait for previous page of dialog to be open
            self[self.activePageNumber - 1].waitUntilOpen()
            self.activePageNumber -= 1
            self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
        else:
            raise PageException(message='%s.%s.goBack(): Cannot proceed back to previous page.' %
                (self.name, self.activePage.name), screenshotName=self.name + '.goBack')

    def submit(self):
        """
            Submit dialog by clicking on button 'OK'.
        """
        self.activePage.btnOK.waitUntilEnabled()
        self.activePage.btnOK.click()
        self.activePage.waitUntilClosed()
        LOG.l4('%s.submit()' % self.name)

    def cancel(self):
        """
            Cancel dialog by clicking on button 'Cancel'.
            Can be overwritten in sub-class.
        """
        if hasattr(self.activePage, 'cancel') and callable(self.activePage.cancel):
            self.activePage.cancel()
            self.activePage.waitUntilClosed()
            self.activePageNumber = -1
            self.activePage = None
        elif hasattr(self.activePage, 'btnCancel'):
            self.activePage.btnCancel.waitUntilEnabled()
            self.activePage.btnCancel.click()
            # Wait for page to be closed
            self.activePage.waitUntilClosed()
            self.activePageNumber = -1
            self.activePage = None
        else:
            raise PageException(message='%s.%s.cancel(): Page cannot be canceled.' % (self.name,
                self.activePage.name), screenshotName=self.name + '.cancel')
        LOG.l4('%s.cancel()' % self.name)

    def close(self):
        """
            Close dialog by clicking on button 'Close' (if any).
            Can be overwritten in sub-class to address page's specifics.
        """
        # Active page has own method 'close'
        if hasattr(self.activePage, 'close') and callable(self.activePage.close):
            self.activePage.close()
            self[self.activePageNumber].waitUntilClosed()
            self.activePageNumber = -1
            self.activePage = None
        # Active page has no method 'close', thus use wizard's generic solution
        elif hasattr(self.activePage, 'btnClose'):
            self.activePage.btnClose.waitUntilEnabled()
            self.activePage.btnClose.click()
            # Wait until page is closed
            self[self.activePageNumber].waitUntilClosed()
            self.activePageNumber = -1
            self.activePage = None
        else:
            raise PageException(message='%s.%s.goNext(): Cannot proceed to next page.' % (self.name,
                self.activePage.name), screenshotName=self.name + '.close')

    def hasNext(self):
        """
            Check if moving to next page is applicable to active one (i.e. if it has respecting
              buttons 'Next'/'Finish' etc. or has method 'hasNext').
        """
        hasNext = False
        if hasattr(self.activePage, 'hasNext') and callable(self.activePage.hasNext):
            hasNext = self.activePage.hasNext()
        elif hasattr(self.activePage, 'btnNext'):
            hasNext = True
        return hasNext

    def hasBack(self):
        """
            Check if moving back to previous page is applicable to active one (i.e. if it has button
              'Back' or has method 'hasBack').
        """
        hasBack = False
        if hasattr(self.activePage, 'hasBack') and callable(self.activePage.hasBack):
            hasBack = self.activePage.hasBack()
        elif hasattr(self.activePage, 'btnBack'):
            hasBack = True
        return hasBack


class Utility(object):
    @staticmethod
    def getSizeUnit(size):
        matchSize = re.search('^([0-9]*[.,]?[0-9]+)\s*([bmkgtBMKGT]?i?[bBo]?)?$', str(size),
        re.IGNORECASE)
        # 'K', 'M'...
        return matchSize.group(2)[:1].upper()

    @staticmethod
    def getSizeValue(size):
        matchSize = re.search('^([0-9]*[.,]?[0-9]+)\s*([bmkgtBMKGT]?i?[bBo]?)?$', str(size),
        re.IGNORECASE)
        return matchSize.group(1)

    @staticmethod
    def getLocalizedSizeFormat(size, locale):
        """
            English, Japanese, Korean and Chinese locales use '.' (period) as decimal separator in
              numbers, while Spanish, German and French use ',' (comma). The function converts size
              (as number) into localized size text (ex. 512 - > '512', 2.5 -> '2.5' or '2,5').
              See [Bug 26180].
            @param size: Size as number (integer or decimal).
            @param locale: 'en', 'es', 'de', 'fr', 'ja', 'ko', 'zh'.
            @return: Localized size as text (ex. '2,5').
        """
        sizeText = Utility.getSizeValue(size=str(size))
        if locale in ['es', 'de', 'fr']:
            sizeText = sizeText.replace('.', ',')
        return sizeText

    @staticmethod
    def getLocalizedSizeUnit(sizeUnit, locale):
        """
            Returns localized fully-specified size unit (ex. 'KiB', 'GiB') based on short size unit
              (ex. 'K', 'g'). As example, English locale assumes 'KiB', while corresponding French
              size unit is 'Kio' (kilo-octet). Used for selection from size unit drop-down list.
            @param sizeUnit: Short size unit: 'b', 'K', 'G' etc.
            @param locale: 'en', 'es', 'de', 'fr', 'ja', 'ko', 'zh'.
            @return: Fully-specified localized size unit: 'KiB', 'Tio' etc.
        """
        sizeUnit = sizeUnit.upper()
        if locale == 'fr':
            sizeUnit += ('' if sizeUnit == 'B' else 'io')
        else:
            sizeUnit += ('' if sizeUnit == 'B' else 'iB')
        return sizeUnit
