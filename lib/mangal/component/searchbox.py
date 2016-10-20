from base_component import *


class SearchBox(BaseComponent):
    """
        Model search box consisting of input text box and magnifying glass button to the right
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of head element
            @param name: Name of component
        """
        super(SearchBox, self).__init__(driver=driver, selector=selector, name=name)

        self.inputElementPath = self.selector + \
        '/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[contains(@id, "inputCell")]/input'
        self.inputElement = BaseComponent(driver=self.driver, selector=self.inputElementPath,
        name=self.name + '.inputElement')

        self.clickableElementPath = self.selector + \
        '/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[starts-with(@id, "ext")]/div'
        self.clickableElement = BaseComponent(driver=self.driver,
        selector=self.clickableElementPath, name=self.name + '.clickableElement')

    def clear(self):
        self.inputElement.element.clear()
        LOG.l4('%s.clear()' % self.name)

    def getText(self):
        text = self.inputElement.getAttribute(attributeName='value', suppressLog=True)
        LOG.l5("%s.getText(): '%s'" % (self.name, text))
        return text

    def setText(self, text):
        self.inputElement.element.send_keys(text)
        LOG.l4("%s.sendText(text='%s')" % (self.name, text))

    def search(self):
        self.clickableElement.element.click()
        LOG.l4('%s.search()' % self.name)
