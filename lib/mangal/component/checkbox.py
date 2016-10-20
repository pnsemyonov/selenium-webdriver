from base_component import *


class CheckBox(BaseComponent):
    """
        Checkbox component.
        Template of base web element node selector:
            <table id='fieldset-...-legendChk' class='x-form-type-checkbox'>: Base element
                <tbody>
                    <tr class='x-form-item-input-row'>
                        <td class='x-field-label-cell'>
                            <label id='...-legendChk-labelEl'>
                        <td class='x-form-item-body ...'>
                            <div class='x-form-cb-wrap-inner ...'>
                                <input id='...-legendChk-inputEl'>

    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of base element of checkbox (ex.
              '//table[@data-mg-comp="showSelectedRowOnly"]') from which target checkbox element
               derived (ex. './tbody/tr/td[...]/div/input')
            @param name: Name of component (set automatically at page instantiation).
        """
        super(CheckBox, self).__init__(driver=driver, selector=selector, name=name)
        # Child element of component which acts as checker.
        self.selectableElementPath = self.selector + '/tbody/tr/td[contains(@id, "bodyEl")]/div/input'
        self.selectableElement = BaseComponent(driver=self.driver,
        selector=self.selectableElementPath, name=name + '.selectableElement')

    def isSelected(self, suppressLog=False):
        elementClass = self.getAttribute(attributeName='class', suppressLog=True)
        if 'x-form-cb-checked' in elementClass:
            isSelected = True
        else:
            isSelected = False
        if not suppressLog:
            LOG.l5('%s.isSelected(): %s' % (self.name, isSelected))
        return isSelected

    def select(self, suppressLog=False):
        if not self.isSelected(suppressLog=True):
            self.selectableElement.element.click()
            timeout = Timeout(timeout=self.driver.timeout, description='%s.select(): Time out.' %
                self.name)
            # Re-examine check box state while timeout has not been reached
            while not self.isSelected(suppressLog=True):
                if timeout.exceeded(raiseException=False):
                    raise ComponentFailedStateException(message='%s.select(): Time out.' %
                    self.name, driver=self.driver, screenshotName=self.name + '.select')
                time.sleep(self.driver.delay)
            if not suppressLog:
                LOG.l4('%s.select()' % self.name)

    def unselect(self, suppressLog=False):
        if self.isSelected(suppressLog=True):
            self.selectableElement.element.click()
            timeout = Timeout(timeout=self.driver.timeout, description='%s.unselect(): Time out.' %
                self.name)
            # Re-examine check box state while timeout has not been reached
            while self.isSelected(suppressLog=True):
                if timeout.exceeded(raiseException=False):
                    raise ComponentFailedStateException(message='%s.unselect(): Time out.' %
                    self.name, driver=self.driver, screenshotName=self.name + '.unselect')
                time.sleep(self.driver.delay)
            if not suppressLog:
                LOG.l4('%s.unselect()' % self.name)

    def setState(self, select=True):
        if select:
            self.select(suppressLog=True)
        else:
            self.unselect(suppressLog=True)
        LOG.l4('%s.setState(select=%s)' % (self.name, select))
