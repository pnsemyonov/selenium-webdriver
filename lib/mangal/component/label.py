from base_component import *


class Label(BaseComponent):
    """
        Label component.
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of label element
            @param name: Name of component
        """
        super(Label, self).__init__(driver=driver, selector=selector, name=name)

    def getText(self):
        text = self.element.text()
        LOG.l5("%s.getText(): '%s'" % (self.name, text))
        return text

    def waitUntilText(self, text, exact=False):
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilText(%s): Time out.'
            % (self.name, text))
        while not ((self.element.text() == text) or ((not exact) and (text in
        self.element.text()))):
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.waitUntilText(%s): Time out.' %
                (self.name, text), driver=self.driver, screenshotName=self.name + '.waitUntilText')
            time.sleep(self.driver.delay)
        LOG.l5("%s.waitUntilText(text='%s')" % (self.name, text))
