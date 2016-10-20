from dropdownlist import *


class ComboBox(DropDownList):
    """
        Extends functionality of drop-down list: Gives ability to enter text into active text
          section beside selection from list of values.
    """
    def __init__(self, driver, selector, name=''):
        super(ComboBox, self).__init__(driver=driver, selector=selector, name=name)

    def clear(self):
        self.inputElement.element.clear()
        LOG.l4('%s.clear()' % self.name)

    def setText(self, text):
        """
            Enter text in text section of combobox.
        """
        newText = self.inputElement.getAttribute(attributeName='value', suppressLog=True) + text
        self.inputElement.element.send_keys(text)
        timeout = Timeout(timeout=self.driver.timeout, description='%s.setText(%s): Time out.' %
            (self.name, text))
        while self.inputElement.getAttribute(attributeName='value', suppressLog=True) != newText:
            if timeout.exceeded(raiseException=False):
                raise ComponentFailedStateException(message='%s.setText(%s): Time out.' %
                (self.name, text), driver=self.driver, screenshotName=self.name + '.setText')
            time.sleep(self.driver.delay)
        LOG.l4("%s.setText(text='%s')" % (self.name, text))

class ComboBoxItems(DropDownItems):
    """
        Represent list of items of combobox list. Should be attached to ComboBoxList instance using
          addItems().
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver.
            @param selector: Selector of head element of item list (ex. '//body/div[contains(@class,
              "mg-list-size")]').
            @param name: Name of component.
        """
        super(ComboBoxItems, self).__init__(driver=driver, selector=selector, name=name)
        # List item elements
        self.itemRelativePath = '/div[starts-with(@id, "treepanel")]/div/table/tbody/tr'
