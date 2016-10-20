from base_component import *


class Button(BaseComponent):
    """
        Button component.
        Template of base web element node selector:
            <a id='button-...' class='x-btn ...'>: Base element
                <span id='button-...-btnWrap' class='x-btn-wrap'>
                    <span class='x-btn-button'>
                        <span class='x-btn-inner ...'>
                        <span class='x-btn-icon-el ...'>
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver.
            @param selector: Selector of base element.
            @param name: Name of component (normally provided automatically while page
              instantiation).
        """
        super(Button, self).__init__(driver=driver, selector=selector, name=name)

    def click(self):
        """
            Performs click action on button.
        """
        self.waitUntilEnabled()
        self.element.click()
        LOG.l4('%s.click()' % self.name)

    def getText(self):
        """
            Returns text of button.
            @return: Text as string.
        """
        text = self.element.text()
        LOG.l5("%s.getText(): '%s'" % (self.name, text))
        return text

    def isEnabled(self):
        """
            Returns state of button on web page.
            @return: True if button bright and clickable, False if dimmed and inactive.
        """
        elementClass = self.getAttribute(attributeName='class', suppressLog=True)
        if 'x-item-disabled' in elementClass:
            isEnabled = False
        else:
            isEnabled = True
        LOG.l5('%s.isEnabled(): %s' % (self.name, isEnabled))
        return isEnabled

    def waitUntilEnabled(self):
        """
            Wait until button has become enabled.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilEnabled(): Time out.'
            % self.name)
        while not self.isEnabled():
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.waitUntilEnabled(): Time out.' %
                self.name, driver=self.driver, screenshotName=self.name + '.waitUntilEnabled')
            time.sleep(self.driver.delay)
        LOG.l5('%s.waitUntilEnabled()' % self.name)

    def waitUntilDisabled(self):
        """
            Wait until button has become disabled.
        """
        timeout = Timeout(timeout=self.driver.timeout, description='%s.waitUntilDisabled(): Time out.'
            % self.name)
        while self.isEnabled():
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.waitUntilDisabled(): Time out.' %
                self.name, driver=self.driver, screenshotName=self.name + '.waitUntilDisabled')
            time.sleep(self.driver.delay)
        LOG.l5('%s.waitUntilDisabled()' % self.name)
