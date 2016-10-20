from base_component import *


class RadioButton(BaseComponent):
    """
        Model radio button.
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of head element of radio button (ex.
              '//table[@data-mg-comp="autoRadio"]')
            @param name: Name of component
        """
        super(RadioButton, self).__init__(driver=driver, selector=selector, name=name)
        self.selectableElementPath = self.selector + \
        '/tbody/tr/td[contains(@id, "bodyEl")]/div/input'
        self.selectableElement = BaseComponent(driver=self.driver,
        selector=self.selectableElementPath, name=self.name + '.selectableElement')

    def isSelected(self):
        if 'x-form-cb-checked' in self.getAttribute(attributeName='class', suppressLog=True):
            isSelected = True
        else:
            isSelected = False
        LOG.l5('%s.isSelected(): %s' % (self.name, isSelected))
        return isSelected

    def select(self):
        if not self.isSelected():
            self.selectableElement.element.click()
            timeout = Timeout(timeout=self.driver.timeout, description='%s.select(): Time out.' %
                self.name)
            while not 'x-form-cb-checked' in self.getAttribute(attributeName='class',
            suppressLog=True):
                if timeout.exceeded(raiseException=False):
                    raise ComponentFailedStateException(message='%s.select(): Time out.' %
                    self.name, driver=self.driver, screenshotName=self.name + '.select')
                time.sleep(self.driver.delay)
            LOG.l4('%s.select()' % self.name)
