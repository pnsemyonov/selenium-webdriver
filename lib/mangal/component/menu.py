from selenium.webdriver.common.action_chains import ActionChains
from base_component import *


class Menu(BaseComponent):
    """
        Model menu button with drop-down item list. Support nested (parent-child relating) item
          lists.
    """
    def __init__(self, driver, selector, name='', items=None):
        """
            @param element: Instance of BaseComponent representing head web element of menu button
              element. Ex. LoginPage().btnLocale
            @param items: Instance of MenuItems representing head web element of drop-down menu item
              list. Ex. LoginPage().localeMenuItems
            @param name: Name of component
        """
        super(Menu, self).__init__(driver=driver, selector=selector, name=name)
        self.items = items

    def isEnabled(self):
        """
            Check if head button of menu is enabled. This behaves like Button component: doing
              inspection of attribute 'class' (if it has 'x-item-disabled').
        """
        if 'x-item-disabled' in self.getAttribute(attributeName='class', suppressLog=True):
            isEnabled = False
        else:
            isEnabled = True
        LOG.l5('%s.isEnabled(): %s' % (self.name, isEnabled))
        return isEnabled

    def isItemEnabled(self, item):
        """
            Check if specified item (in root or nested item list) is enabled (not grayed out).
        """
        if isinstance(item, str):
            # Enclose single item name into list as MenuItems.select() works with name(s) as list
            item = [item]
        if not self.isExpanded():
            self.expand()
        # Call first-level item list to perform hovering over list
        return self.items.isItemEnabled(item)

    def isExpanded(self):
        """
            Check if menu is expanded (menu button has been clicked).
            @return: True if expanded, False if collapsed
        """
        if 'x-menu-active' in self.getAttribute(attributeName='class', suppressLog=True):
            isExpanded = True
        else:
            isExpanded = False
        LOG.l5('%s.isExpanded(): %s' % (self.name, isExpanded))
        return isExpanded

    def expand(self):
        """
            Expand menu (by clicking menu button).
        """
        if 'x-menu-active' not in self.getAttribute(attributeName='class', suppressLog=True):
            self.element.click()
            LOG.l4('%s.expand()' % self.name)

    def select(self, item):
        """
            Perform item selection (by clicking on menu item) from menu item list(s).
            @param item: Item name (single-level menu) or list of them (multi-level menu).
              Examples:
                item='Mapping': Performs selection of item named 'Mapping' from main item list of
                  menu.
                item=['State', 'Offline']: Performs double selection by navigating to item 'State'
                  on first tier of menu, then clicking on item 'Offline' on child item list.
        """
        # If 'item' is not list, assuming single-level menu
        if isinstance(item, str):
            # Enclose single item name into list as MenuItems.select() works with name(s) as list
            item = [item]
        if not self.isExpanded():
            self.expand()
        # Call first-level item list to perform selection
        self.items.select(item)

    def addItems(self, items):
        """
            Add main menu item list to trigger (menu button)
        """
        self.items = items
        LOG.l5('%s.addItems(items=%s)' % (self.name, items.name))

    def getItems(self):
        """
            Returns dictionary of menu item names (nested in case of multi-level menu). As example,
              menu
                Size
                State
                  Online
                  Offline
              where 'Online' and 'Offline' are in child item list of item 'State' will return the
              following structure:
              {
                'Size': None,
                'State': [
                  {
                    'Online': None,
                    'Offline': None
                  }
                ]
              }
        """
        if not self.isExpanded():
            self.expand()
        items = self.items.getItems()
        LOG.l5('%s.getItems():\n%s' % (self.name, items))
        return items


class MenuItems(BaseComponent):
    """
        Model menu item list, either dropped down from menu button or expanded from item of parent
          menu.
    """
    def __init__(self, driver, selector, name='', children=None):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: XPath selector of head element
            @param name: Name of component
            @param children: Key-valued pairs of names of menu items with associated menu
              item lists (instances of MenuItems). Ex. {'Mapping': MenuItems(...)}
        """
        super(MenuItems, self).__init__(driver=driver, selector=selector, name=name)
        if children is None:
            self.children = {}
        else:
            self.children = children
        self.itemRelativePath = '/div/div[starts-with(@id, "menu")]/div/div'
        # Maps English text to indices of items. Allows to use English-text items in non-English
        #   locales.
        self.mappedItems = None

    def addItems(self, item, childItems):
        """
            Attach child menu items to parent item. May be called multiple times for multiple child
              menus.
            @param item: Name of menu item. Ex. item='Mapping'.
            @param childItems: Instance of MenuItems representing child menu item list.
        """
        self.children[item] = childItems
        LOG.l5('%s.addItems(item=%s, childItems=%s)' % (self.name, item, childItems.name))

    def mapItems(self, items):
        """
            Map English text to menu items by their order of appearance. Ex. ['Change Password',
              'Sign Out']
        """
        self.mappedItems = items
        LOG.l5('%s.mapItems(items=%s)' % (self.name, self.mappedItems))

    def getItems(self):
        """
            Return menu item names with item names of child menus (optionally).
        """
        itemComponents = self.getChildren(relativePath=self.itemRelativePath)
        itemTexts = []
        # For each item in menu
        for itemCount in range(len(itemComponents)):
            itemName = self.mappedItems[itemCount]
            itemSelector = itemComponents[itemCount].selector + '/a/span'
            itemText = BaseComponent(driver=self.driver, selector=itemSelector, name=self.name +
            '.item').element.text()
            # If item has child menu
            if itemName in self.children:
                # To create WebElement in BaseComponent, we need to access it somehow
                if itemComponents[itemCount].id:
                    # Hover over item to expose its code in HTML (code section with menu elements
                    #   appears in HTML once menu expanded)
                    ActionChains(driver=self.webDriver).move_to_element(itemComponents[itemCount].element).perform()
                # Addressing item element either by name or index
                BaseComponent(driver=self.driver,
                selector=self.children[itemName].selector).waitUntilPresent()
                # Add name of item as key and its child menu items as value
                itemTexts.append({itemName: self.children[itemName].getItems()})
            # If item has no child menu
            else:
                # Add item name (mapped) and item text (of item's web element)
                itemTexts.append({itemName: itemText})
        LOG.l5('%s.getItems(): %s' % (self.name, itemNames))
        return itemNames

    def select(self, item):
        """
            Make selection in current list.
            @param item: Item passed as list of item names (ex. ['Mapping'], ['State', 'Online'])
              either single-leveled or multi-leveled (nested menus).
        """
        itemComponents = self.getChildren(relativePath=self.itemRelativePath)
        # Pick menu item by its its index obtained with name. If menu is nested, pick 1st name from
        #   item names list: ['State', 'Online'] => 'State'
        itemIndex = self.mappedItems.index(item[0])
        itemComponent = itemComponents[itemIndex]
        # If multiple item names passed assuming item has sub-menu (nested).
        #   itemComponent.element.id() is used to vivify WebElement
        if len(item) > 1 and itemComponent.element.id():
            ActionChains(driver=self.webDriver).move_to_element(itemComponent.element.element).perform()
            BaseComponent(driver=self.driver,
                selector=self.children[item[0]].selector).waitUntilPresent()
            LOG.l4("%s.select.expand(item='%s')" % (self.name, itemComponent.element.text()))
            # Pass to child MenuItems only leftover names/indices (first one has been used here)
            self.children[item[0]].select(item=item[1:])
        # Single item name assuming item has no child menu
        else:
            itemText = itemComponent.element.text()
            itemComponent.element.click()
            LOG.l4("%s.select(item='%s')" % (self.name, itemText))

    def isItemEnabled(self, item):
        """
            Check if specified item (in root or nested item list) is enabled (not grayed out).
        """
        itemComponents = self.getChildren(relativePath=self.itemRelativePath)
        # Pick menu item by its its index obtained with name. If menu is nested, pick 1st name from
        #   item names list: ['State', 'Online'] => 'State'
        itemIndex = self.mappedItems.index(item[0])
        itemComponent = itemComponents[itemIndex]
        # If multiple item names passed assuming item has sub-menu (nested).
        #   itemComponent.element.id() is used to vivify WebElement
        if len(item) > 1 and itemComponent.element.id():
            ActionChains(driver=self.webDriver).move_to_element(itemComponent.element.element).perform()
            BaseComponent(driver=self.driver,
                selector=self.children[item[0]].selector).waitUntilPresent()
            LOG.l4("%s.isItemEnabled.expand(item='%s')" % (self.name, item[0]))
            # Pass to child MenuItems only leftover names/indices (first one has been used here)
            isItemEnabled = self.children[item[0]].isItemEnabled(item=item[1:])
        # Single item name assuming item has no child menu
        else:
            isItemEnabled = not ('x-menu-item-disabled' in itemComponent.getAttribute('class'))
            LOG.l4("%s.isItemEnabled(item='%s')" % (self.name, item[0]))
        return isItemEnabled
