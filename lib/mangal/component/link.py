from base_component import *


class Link(BaseComponent):
    """
        Model web link.
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of link element
            @param name: Name of component
        """
        super(Link, self).__init__(driver=driver, selector=selector, name=name)

    def getText(self):
        text = self.element.text
        LOG.l5('%s.getText(): %s' % (self.name, text))
        return text

    def getHref(self):
        hRef = self.getAttribute(attributeName='href', suppressLog=True)
        LOG.l5("%s.getHref(): '%s'" % (self.name, hRef))
        return hRef

    def click(self):
        self.element.click()
        LOG.l4('%s.click()' % self.name)
