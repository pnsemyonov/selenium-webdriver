from base_component import *


class DropDownList(BaseComponent):
    """
        Drop-down list component. Unlike sub-classed combo box, text section of drop-down list is
          not editable.
        Template of base web element node selector:
            ...
    """
    def __init__(self, driver, selector, name='', items=None):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of head element of drop-down list
            @param name: Name of component
            @param items: Instance of DropDownItems, represents list of available items in expanded
              drop-down list
        """
        super(DropDownList, self).__init__(driver=driver, selector=selector, name=name)

        self.clickableElementRelativePath = '/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[starts-with(@id, "ext")]/div'
        self.clickableElement = BaseComponent(driver=self.driver, selector=self.selector +
        self.clickableElementRelativePath, name=self.name + '.clickableElement')

        self.inputElementRelativePath = '/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[contains(@id, "inputCell")]/input'
        self.inputElement = BaseComponent(driver=self.driver, selector=self.selector +
        self.inputElementRelativePath, name=self.name + '.inputElement')

        # Its 'class' has 'x-pickerfield-open' when list expanded
        self.pickerElementRelativePath = '/tbody/tr/td[contains(@id, "bodyEl")]'
        self.pickerElement = BaseComponent(driver=self.driver, selector=self.selector +
        self.pickerElementRelativePath, name=self.name + '.pickerElement')
        self.items = items

    def addItems(self, items):
        """
            Specify items in drop-down list.
            @param items: Instance of DropDownItems.
        """
        self.items = items

    def getText(self):
        """
            Return text of current item
        """
        text = self.inputElement.getAttribute(attributeName='value', suppressLog=True)
        LOG.l5("%s.getText(): '%s'" % (self.name, text))
        return text

    def getItems(self):
        """
            Get list of items in drop-down list (ex. ['B', 'KiB', 'MiB', ...]).
        """
        wasExpanded = self.isExpanded()
        self.expand()
        items = self.items.getItems()
        if not wasExpanded:
            self.collapse()
        LOG.l5('%s.getItems():\n%s' % (self.name, items))
        return items

    def isEnabled(self):
        """
            False if control is disabled (it looks like regular label without any controls).
        """
        elementClass = self.getAttribute(attributeName='class', suppressLog=True)
        if ('mg-item-disabled' in elementClass) or ('x-form-readonly' in elementClass):
            isEnabled = False
        else:
            isEnabled = True
        LOG.l5('%s.isEnabled(): %s' % (self.name, isEnabled))
        return isEnabled

    def isExpanded(self):
        """
            True if drop-down list is expanded, False if collapsed.
        """
        if 'x-pickerfield-open' in self.pickerElement.getAttribute(attributeName='class',
        suppressLog=True):
            isExpanded = True
        else:
            isExpanded = False
        LOG.l5('%s.isExpanded(): %s' % (self.name, isExpanded))
        return isExpanded

    def expand(self):
        """
            Expand drop-down list by clicking on clickableElement if list is collapsed.
        """
        if not self.isExpanded():
            self.clickableElement.element.click()
            timeout = Timeout(timeout=self.driver.timeout, description='%s.expand(): Time out.' %
                self.name)
            while not self.isExpanded():
                if timeout.exceeded(raiseException=False):
                    raise ComponentFailedStateException(message='%s.expand(): Time out.' %
                    self.name, driver=self.driver, screenshotName=self.name + '.expand')
                time.sleep(self.driver.delay)
            LOG.l4('%s.expand()' % self.name)

    def collapse(self):
        """
            Collapse drop-down list by clicking on clickableElement if list is expanded.
        """
        if self.isExpanded():
            self.clickableElement.element.click()
            timeout = Timeout(timeout=self.driver.timeout, description='%s.collapse(): Time out.' %
                self.name)
            while self.isExpanded():
                if timeout.exceeded(raiseException=False):
                    raise ComponentFailedStateException(message='%s.collapse(): Time out.' %
                    self.name, driver=self.driver, screenshotName=self.name + '.collapse')
                time.sleep(self.driver.delay)
            LOG.l4('%s.collapse()' % self.name)

    def select(self, item, exact=False):
        """
            Perform item selection in drop-down list by clicking on item.
        """
        # List should be expanded prior to access it.
        self.expand()
        self.items.select(item, exact=exact)
        LOG.l4("%s.select(item='%s')" % (self.name, item))


class DropDownItems(BaseComponent):
    """
        Represent list of items of drop-down list. Should be attached to DropDownList instance using
          addItems().
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver.
            @param selector: Selector of head element of item list (ex. '//body/div[contains(@class,
              "mg-list-size")]'). All drop-downs have the same element sub-tree, so see examples of
               selectors of drop-downs on LoginPage, DefineLUNsPage etc.
            @param name: Name of component
        """
        super(DropDownItems, self).__init__(driver=driver, selector=selector, name=name)
        # List item elements
        self.itemRelativePath = '/div/ul/li'

    def getItems(self):
        """
            Return values of item list elements as list.
        """
        items = [item.element.text() for item in
            self.getChildren(relativePath=self.itemRelativePath)]
        LOG.l5('%s.getItems():\n%s' % (self.name, items))
        return items

    def select(self, item, exact):
        """
            Make selection from drop-down list either by value of item or by its index.
            @param item: Index of item (integer, 1 to number of items) or value of item (its display
              text)
            @param exact: If True, exact matching; otherwise match list items by pattern
        """
        itemComponents = self.getChildren(relativePath=self.itemRelativePath)
        # If 'item' has been passed as index of item in drop-down item list (1-based)
        if isinstance(item, int):
            if item > len(itemComponents):
                raise IndexError("%s.select(item='%s'): Item index exceeds number of items (%s)." %
                (self.name, item, len(itemComponents)))
            itemComponent = itemComponents[item]
        # 'item' has been passed as value of menu item (ex. 'GiB')
        else:
            # Find menu item by its name
            itemFound = False
            for itemComponent in itemComponents:
                if ((not exact) and (item in itemComponent.element.text())) or (item ==
                itemComponent.element.text()):
                    itemFound = True
                    break
            if not itemFound:
                raise LookupError("%s.select(item='%s'): Item not found." % (self.name, item))
        itemComponent.element.click()
        LOG.l4("%s.select(item='%s')" % (self.name, item))
