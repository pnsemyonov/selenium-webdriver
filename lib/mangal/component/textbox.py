from base_component import *


class TextBox(BaseComponent):
    """
        Model text box.
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of wrapped WebElement.
            @param name: Name of component.
        """
        super(TextBox, self).__init__(driver=driver, selector=selector, name=name)

    def clear(self):
        self.element.clear()
        LOG.l4('%s.clear()' % self.name)

    def getText(self):
        text = self.getAttribute(attributeName='value', suppressLog=True)
        LOG.l5("%s.getText(): '%s'" % (self.name, text))
        return text

    def setFocus(self):
        self.element.click()
        LOG.l4('%s.setFocus()' % self.name)

    def setText(self, text):
        oldText = self.getText()
        self.sendKeys(value=text, suppressLog=True)
        LOG.l4("%s.setText(text='%s')" % (self.name, text))

    def sendKeys(self, value, suppressLog=False):
        self.element.send_keys(value)
        if not suppressLog:
            LOG.l4("%s.sendKeys(value='%s')" % (self.name, value))

    def waitUntilText(self, text, exact=False):
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilText(%s): Time out.'
            % (self.name, text))
        while not ((self.getText() == text) or ((not exact) and (text in
        self.getText()))):
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.waitUntilText(%s): Time out.' %
                (self.name, text), driver=self.driver, screenshotName=self.name + '.waitUntilText')
            time.sleep(self.driver.delay)
        LOG.l5("%s.waitUntilText(text='%s')" % (self.name, text))
