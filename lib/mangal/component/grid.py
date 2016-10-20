import copy
import re
from selenium.webdriver.common.keys import Keys
from base_component import *


class Grid(BaseComponent):
    """
        Represent grid on Mars web UI pages such as LUNs, Consistency Groups, Initiator Groups, grid
          on a dialog.
    """
    def __init__(self, driver, selector, name=''):
        super(Grid, self).__init__(driver=driver, selector=selector, name=name)

        # Selectors of grid elements
        self.selectors = []

        # List of column names
        self.columnNames = []

        # Path to header section in grid element
        self.headerRelativePath = '/div[starts-with(@id, "headercontainer")]/div/div/div'

        self.headerCheckBoxRelativePath = '[contains(@class, "x-column-header-checkbox")]'

        # Path to rows in table section in grid element
        self.tableRelativePath = '/div[contains(@class, "x-grid-with-row-lines") or contains(@class, "x-grid-no-row-lines")]/div/table/tbody/tr'

        # Section of grid containing buttons 'First Page', 'Previous Page' etc.
        self.pagingToolbarPath = './div[@data-mg-comp="gridPaging"]/div/div'

        # Rows in Sencha's grid may be as simple as <tr><td>
        self.dataCellPath = '/td'
        # ...or 'wrapped' ones: <tr><table>...<td>
        self.wrapCellPath = '/td/table/tbody/tr[contains(@class, "x-grid-data-row")]/td'

        # WebElements return values as Unicode strings, we need to encode them to ASCII
        self.charSet = 'ascii'

    def __getattr__(self, attributeName):
        """
            Attempt to return Element instance by given element name (ex. 'btnNextPage')
        """
        self.refreshSelectors()
        if attributeName in self.selectors:
            attribute = self.getChild(relativePath=self.selectors[attributeName])
        elif attributeName in ['hasFirstPage', 'hasPreviousPage', 'page', 'hasNextPage',
        'hasLastPage', 'pages']:
            attribute = self.getPageDetails()[attributeName]
        elif attributeName in ['firstRow', 'lastRow', 'rows']:
            attribute = self.getRowDetails()[attributeName]
        else:
            raise AttributeError('Invalid attribute:', attributeName)
        return attribute

    def refreshSelectors(self):
        # To create web elements of grid. Particularly - paging controls (paging button, row numbers
        #   in 'Displaying...' at bottom of page)
        if not self.selectors:
            self.selectors = {
                'btnFirstPage': '/' + self.pagingToolbarPath + '/a[@data-mg-comp="first"]',
                'btnPreviousPage': '/' + self.pagingToolbarPath + '/a[@data-mg-comp="prev"]',
                'lblCurrentPage': '/' + self.pagingToolbarPath + '/div[.="Page"]',
                'txtCurrentPage': '/' + self.pagingToolbarPath +
                '/table/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[contains(@id, "inputCell")]/input',
                'lblOfNumber': '/' + self.pagingToolbarPath + '/div[@data-mg-comp="afterTextItem"]',
                'btnNextPage': '/' + self.pagingToolbarPath + '/a[@data-mg-comp="next"]',
                'btnLastPage': '/' + self.pagingToolbarPath + '/a[@data-mg-comp="last"]',
                'lblDisplaying': '/' + self.pagingToolbarPath + '/div[@data-mg-comp="displayItem"]'
            }

    def _select(self, select, **filterAttrs):
        """
            Select/unselect grid row by checking/unchecking checkbox
            @param select: Select rows if True, unselect if False
        """
        self.refreshColumnNames()
        # If grid has no checkbox'ed fields
        if 'selected' not in self.columnNames:
            raise AttributeError('Grid rows not selectable.')
        # If filtering attributes provided, go row by row, and select those satisfying filtering
        #   condition
        if filterAttrs:
            # <tr> elements (rows) in grid table
            gridRows = self.getChildren(relativePath=self.tableRelativePath)
            for gridRow in gridRows:
                resultRow = {}
                # <tr class='...'>
                rowClass = gridRow.getAttribute(attributeName='class', suppressLog=True)
                # 'Simplified' version of row
                if 'x-grid-data-row' in rowClass:
                    cellPath = self.dataCellPath
                # 'Complicated' version of row with <table> in place of <td>
                elif 'x-grid-wrap-row' in rowClass:
                    cellPath = self.wrapCellPath
                rowCells = gridRow.getChildren(relativePath=cellPath)
                # Go through all cells in row
                for cellIndex in range(len(self.columnNames)):
                    # <td class='...'>
                    cellClass = rowCells[cellIndex].getAttribute(attributeName='class', suppressLog=True)
                    # If cell represent checkbox
                    if 'x-grid-cell-row-checker' in cellClass:
                        if 'x-grid-row-selected' in rowClass:
                            # 'selected': True
                            resultRow[self.columnNames[cellIndex]] = True
                        else:
                            # 'selected': False
                            resultRow[self.columnNames[cellIndex]] = False
                        # Getting inner (clickable) element of checkbox
                        clickableComponent = rowCells[cellIndex].getChild(relativePath='/div/div')
                    else:
                        # <column_name>: <cell_text>
                        resultRow[self.columnNames[cellIndex]] = rowCells[cellIndex].element.text()
                # If grid row confirms filtering condition
                if self._satisfyFilters(resultRow, filterAttrs):
                    # If checkbox state is opposite to required
                    if ('x-grid-row-selected' in rowClass) != select:
                        clickableComponent.element.click()
                        # Wait until check box is marked as selected
                        timeout = Timeout(timeout=self.driver.timeout, description='%s._select(): Setting row check box state timed out.'
                            % self.name)
                        while ('x-grid-row-selected' in
                        gridRow.getAttribute(attributeName='class', suppressLog=True)) != select:
                            if timeout.exceeded(raiseException=False):
                                raise ComponentFailedStateException(message='%s._select(): Setting row check box state timed out.'
                                % self.name, driver=self.driver, screenshotName=self.name +
                                '._select')
                            time.sleep(self.driver.delay)
        # If no filtering attributes provided, click on 'Select All' checkbox in header
        else:
            # Checkbox in grid's header
            headerCheckBox = self.getChild(relativePath=self.headerRelativePath +
                self.headerCheckBoxRelativePath)
            clickableComponent = headerCheckBox.getChild(relativePath='/div')
            # Both select or unselect, we first check header checkbox to select all
            if 'x-grid-hd-checker-on' not in headerCheckBox.getAttribute(attributeName='class',
            suppressLog=True):
                clickableComponent.element.click()
                timeout = Timeout(timeout=self.driver.timeout, description='%s._select(): Setting header check box state timed out.'
                    % self.name)
                while 'x-grid-hd-checker-on' not in \
                headerCheckBox.getAttribute(attributeName='class', suppressLog=True):
                    if timeout.exceeded(raiseException=False):
                        raise ComponentFailedStateException(message='%s._select(): Setting header check box state timed out.'
                        % self.name, driver=self.driver, screenshotName=self.name + '._select')
                    time.sleep(self.driver.delay)
            # If ordered unselect all, uncheck header checkbox to make all rows unselected
            if not select:
                clickableComponent.element.click()
                timeout = Timeout(timeout=self.driver.timeout, description='%s._select(): Setting header check box state timed out.'
                    % self.name)
                while 'x-grid-hd-checker-on' in headerCheckBox.getAttribute(attributeName='class',
                suppressLog=True):
                    if timeout.exceeded(raiseException=False):
                        raise ComponentFailedStateException(message='%s._select(): Setting header check box state timed out.'
                        % self.name, driver=self.driver, screenshotName=self.name + '._select')
                    time.sleep(self.driver.delay)

    def select(self, **filterAttrs):
        """
            Select rows in grid by specifying filtering parameters (see _satisfyFilters())
        """
        LOG.l4('%s.select(%s)' % (self.name, filterAttrs))
        return self._select(select=True, **filterAttrs)

    def unselect(self, **filterAttrs):
        """
            Unselect rows in grid by specifying filtering parameters (see _satisfyFilters())
        """
        LOG.l4('%s.unselect(%s)' % (self.name, filterAttrs))
        return self._select(select=False, **filterAttrs)

    def sort(self, column, ascend=True):
        """
            Sort the grid by given column in ascending or descending order.
            @param column: Either display name of column or column's index (integer, 0 corresponds
              to first column).
            @param ascend: Sorting order. Ascending if True, otherwise descending
        """
        self.refreshColumnNames()
        order = 'ASC' if ascend else 'DESC'
        cellIndex = None
        if isinstance(column, int):
            cellIndex = column
        elif isinstance(column, str):
            column = column.strip().replace(' ', '_').lower()
            try:
                cellIndex = self.columnNames.index(column)
            except ValueError:
                raise LookupError("Column '%s' is not found." % column)
        if cellIndex is not None:
            headerCells = self.getChildren(relativePath=self.headerRelativePath)
            headerCellClass = headerCells[cellIndex].getAttribute(attributeName='class',
                suppressLog=True)
            if 'x-column-header-checkbox' in headerCellClass:
                raise AttributeError("Unable to sort by checkbox'ed field.")
            if ('x-column-header-sort-' + order) not in headerCellClass:
                clickableComponent = headerCells[cellIndex].getChild(relativePath='/div')
                clickableComponent.element.click()
                # TODO: Wait until completion
        else:
            raise AttributeError("Invalid type of argument.")
        LOG.l4("%s.sort(column=%s, ascend=%s)" % (self.name, column, ascend))

    def sortedBy(self):
        """
            Return tuple consisting of name of column which the grid is sorted by, and sorting order
              - True if ascending, False if descending (ex. ('Serial Number', True))
            @return: 2-element dictionary {'column': <name_of_sorted_cell>, 'ascend': <true_false>},
              ex. {'column': 'serial_number', 'ascend': True}
        """
        self.refreshColumnNames()
        # Elements of header
        headerCells = self.getChildren(relativePath=self.headerRelativePath)
        cellName = None
        for cellIndex in range(len(headerCells)):
            cellClass = headerCells[cellIndex].getAttribute(attributeName='class', suppressLog=True)
            # If cell is marked as sorted in ascending order
            if 'x-column-header-sort-ASC' in cellClass:
                # Get name of cell (ex. 'serial_number')
                cellName = self.columnNames[cellIndex]
                ascend = True
                break
            # Or cell has mark of descending ordering
            elif 'x-column-header-sort-DESC' in cellClass:
                cellName = self.columnNames[cellIndex]
                ascend = False
                break
        if cellName is None:
            result = None
        # If sorted column found
        else:
            # Normalize column name, then combine with ordering (ex. {'column': 'serial_number',
            #   'ascend': True})
            result = {'column': cellName, 'ascend': ascend}
        LOG.l5("%s.sortedBy(): ('column': '%s', 'ascend': %s)" % (self.name, cellName, ascend))
        return result

    def _satisfyFilters(self, attributes, filterAttrs):
        """
            @param attributeCondition: Determines how attributes are compared - AND/OR. Default is
              OR.
            @param valuesCondition: Determines how list values are compared - AND/OR. Default is OR.
            @param matchPattern: If Boolean True, does regex comparison. Default is False.
              Applicable only for attributes and not for values list.
        """
        filterAttrs = copy.deepcopy(filterAttrs)
        LOG.l5('Input Attributes: ', attributes)
        LOG.l5('Input Filters: ', filterAttrs)
        if not len(filterAttrs.keys()):
            return True
        attributeCondition = filterAttrs.get('attributeCondition', 'OR').upper()
        if 'attributeCondition' in filterAttrs:
            del filterAttrs['attributeCondition']
        valuesCondition = filterAttrs.get('valuesCondition', 'OR').upper()
        if 'valuesCondition' in filterAttrs:
            del filterAttrs['valuesCondition']
        matchPattern = filterAttrs.get('matchPattern', False)
        if 'matchPattern' in filterAttrs:
            del filterAttrs['matchPattern']
        attrCount = 0
        for fAttr in filterAttrs.keys():
            if fAttr in attributes:
                if any([isinstance(filterAttrs[fAttr], attributeType) for attributeType in (int,
                str, unicode)]):
                    if matchPattern:
                        if len(re.findall(str(filterAttrs[fAttr]), str(attributes[fAttr]))):
                            if attributeCondition == 'OR':
                                return True
                            else:
                                attrCount += 1
                    else:
                        if str(attributes[fAttr]) == str(filterAttrs[fAttr]):
                            if attributeCondition == 'OR':
                                return True
                            else:
                                attrCount += 1
                # If filterAttrs key is list
                elif isinstance(filterAttrs[fAttr], list):
                    valCount = 0
                    valFound = False
                    for value in filterAttrs[fAttr]:
                        if value in attributes[fAttr]:
                            if valuesCondition == 'OR':
                                valFound = True
                                break
                            else:
                                valCount += 1
                    if attributeCondition == 'OR':
                        if valuesCondition == 'OR' and valFound:
                            return True
                        if valuesCondition == 'AND' and valCount == len(filterAttrs[fAttr]):
                            attrCount += 1
                    if attributeCondition == 'AND':
                        if valuesCondition == 'OR' and valFound:
                            attrCount += 1
                        elif valuesCondition == 'AND' and valCount == len(filterAttrs[fAttr]):
                            attrCount += 1
        if attributeCondition == 'AND' and attrCount == len(filterAttrs):
            return True
        if attributeCondition == 'OR' and attrCount > 0:
            return True
        return False

    def find(self, allPages=False, **filterAttrs):
        """
            Find all rows of grid that satisfy filterAttrs
            @param attributeCondition: Determine how attributes are compared: AND/OR. Default: OR
            @param valuesCondition: Determine how list values are compared: AND/OR. Default: OR
            @return: List of dictionaries representing matching rows of grid
        """
        self.refreshColumnNames()
        if allPages:
            if self.page > 1:
                self.goFirstPage()
            lastPage = self.pages
        # Process current page only
        else:
            lastPage = self.page
        resultRows = []
        while self.page <= lastPage:
            # List of all rows in page
            gridRows = self.getChildren(relativePath=self.tableRelativePath)
            # For each row
            for gridRow in gridRows:
                resultRow = {}
                # Get value of <tr class> representing row
                rowClass = gridRow.getAttribute(attributeName='class', suppressLog=True)
                # 'Simplified' version of row
                if 'x-grid-data-row' in rowClass:
                    cellPath = self.dataCellPath
                # 'Complicated' version of row with <table> in place of <td>
                elif 'x-grid-wrap-row' in rowClass:
                    cellPath = self.wrapCellPath
                rowCells = gridRow.getChildren(relativePath=cellPath)
                # For each cell in current row
                for cellIndex in range(len(self.columnNames)):
                    # <td class>
                    cellClass = rowCells[cellIndex].element.get_attribute('class')
                    # If cell represent checkbox
                    if 'x-grid-cell-row-checker' in cellClass:
                        # If checkbox selected
                        if 'x-grid-row-selected' in rowClass:
                            # {'selected': True}
                            resultRow[self.columnNames[cellIndex]] = True
                        else:
                            # {'selected': False}
                            resultRow[self.columnNames[cellIndex]] = False
                    else:
                        # If cell is not checkbox, get its visible text
                        resultRow[self.columnNames[cellIndex]] = rowCells[cellIndex].element.text()
                # Check if row satisfies filter condition
                if self._satisfyFilters(resultRow, filterAttrs):
                    resultRows.append(resultRow)
            if self.page == lastPage:
                break
            else:
                self.goNextPage()
                # Wait until next page loaded
                WebDriverWait(driver=self.webDriver, timeout=self.driver.timeout).until(lambda _:
                self.webDriver.execute_script(script='return document.readyState') == 'complete')
        LOG.l4('%s.find(%s)' % (self.name, filterAttrs))
        return resultRows

    def refreshColumnNames(self):
        """
            Update list of normalized column names (lower case, ' ' -> '_') in grid(ex. ['selected',
              'name', 'consistency_group', 'size', 'state', 'serial_number', 'mapping',
              'creation_time'])
        """
        if not self.columnNames:
            columnNames = []
            for headerItem in self.getChildren(relativePath=self.headerRelativePath):
                if headerItem.getCSSProperty(propertyName='display') != 'none':
                    headerItemClass = headerItem.getAttribute(attributeName='class',
                        suppressLog=True)
                    columnName = headerItem.getAttribute(attributeName='data-mg-comp',
                        suppressLog=True)
                    # After 'or': some grids have first unnamed column which is not checkbox,
                    #   but its belonging cells are checkboxes. Assumption is to take them as
                    #   'Select all rows' checkboxes.
                    if ('x-column-header-checkbox' in headerItemClass) or (('x-column-header-first'
                    in headerItemClass) and not columnName):
                        columnNames.append('selected')
                    else:
                        if columnName is not None:
                            if 'health_state_column' in columnName:
                                columnNames.append('health_state')
                            else:
                                columnNames.append(columnName)
                        else:
                            raise ValueError("Invalid header element type: tag=%s, id=%s, text=%s" %
                                (headerItem.element.tag_name(), headerItem.element.id(),
                                headerItem.element.text()))
            self.columnNames = columnNames

    def clickLink(self, **filterAttrs):
        """
            Make a click on link in grid cell
            @param filterAttrs: Pairs of column name and sought-for value locating cell (ex. name=
              'LUN_1', serial_number ='800AyF1KMHE8'). Allowed using matchPattern,
              attributeCondition and valuesCondition (look for _satisfyFilters()). This piece
              locates first encountered row in grid which satisfies filtering options
            @param click: 1-element dictionary which specifies name of cell in found row and text
              value presented in cell (ex. click={'consistency_group': 'CG_1'})
        """
        self.refreshColumnNames()
        # Memorize to variable, then remove 'click' from filter attributes
        if 'click' in filterAttrs:
            click = filterAttrs['click']
            del filterAttrs['click']
        else:
            raise AttributeError("Argument 'click' not provided.")
        # Normalize attribute names except those used in _satisfyFilters() (ex. 'Serial Number' ->
        #   'serial_number')
        for attributeKey in filterAttrs:
            if attributeKey not in ['attributeCondition', 'valuesCondition', 'matchPattern']:
                normalizedKey = attributeKey.strip().replace(' ', '_').lower()
                if normalizedKey != attributeKey:
                    filterAttrs[normalizedKey] = filterAttrs[attributeKey]
                    del filterAttrs[attributeKey]
        isLinkFound = False
        cellName = click.keys()[0]
        searchText = click[click.keys()[0]]
        # All rows on current page of grid
        gridRows = self.getChildren(relativePath=self.tableRelativePath)
        # For each row
        for gridRow in gridRows:
            resultRow = {}
            # Row: <tr class>
            rowClass = gridRow.getAttribute(attributeName='class', suppressLog=True)
            # 'Simplified' version of row
            if 'x-grid-data-row' in rowClass:
                cellPath = self.dataCellPath
            # 'Complicated' version of row with <table> in place of <td>
            elif 'x-grid-wrap-row' in rowClass:
                cellPath = self.wrapCellPath
            self.rowCells = gridRow.getChildren(relativePath=cellPath)
            # For each cell in current row
            for cellIndex in range(len(self.columnNames)):
                cellClass = self.rowCells[cellIndex].getAttribute(attributeName='class',
                    suppressLog=True)
                # If cell represents checkbox
                if 'x-grid-cell-row-checker' in cellClass:
                    # If checkbox selected
                    if 'x-grid-row-selected' in rowClass:
                        # {'selected': True}
                        resultRow[self.columnNames[cellIndex]] = True
                    else:
                        # {'selected': False}
                        resultRow[self.columnNames[cellIndex]] = False
                else:
                    resultRow[self.columnNames[cellIndex]] = self.rowCells[cellIndex].element.text()
            # If row satisfies filter condition
            if self._satisfyFilters(resultRow, filterAttrs):
                # TODO: Investigate deeper
                # Get index of cell among all cells in row by name (ex. 'Name' -> 1)
                targetCellIndex = self.columnNames.index(cellName) + 1
                targetCell = gridRow.getChild(relativePath='/td[%s]' % targetCellIndex)
                timeout = Timeout(timeout=self.driver.timeout, description="%s.clickLink(click={'%s': '%s'}): Link not found."
                    % (self.name, cellName, searchText))
                while True:
                    if not timeout.exceeded(raiseException=False):
                        try:
                            # <a> can have various levels of nesting in <td>
                            targetLink = targetCell.element.\
                            find_element_by_xpath(xpath='//a[contains(text(), "{searchText}")]'.
                            format(searchText=searchText))
                            # Click on <a href>
                            targetLink.click()
                            isLinkFound = True
                            break
                        except StaleElementReferenceException:
                            pass
                        time.sleep(self.driver.delay)
                    else:
                        raise ComponentFailedStateException(message="%s.clickLink(click={'%s': '%s'}): Link not found."
                            % (self.name, cellName, searchText), driver=self.driver,
                            screenshotName=self.name + '.clickLink')
                if isLinkFound:
                    break
        if not isLinkFound:
            raise ComponentFailedStateException(message="%s.clickLink(click={'%s': '%s'}): Link not found."
                % (self.name, cellName, searchText), driver=self.driver, screenshotName=self.name +
                '.clickLink')
        LOG.l4("%s.clickLink(click={'%s': '%s'})" % (self.name, cellName, searchText))

    def goToPage(self, number=1):
        """
            Navigate to specified page of grid
        """
        if 1 <= number <= self.pages:
            self.txtCurrentPage.element.clear()
            self.txtCurrentPage.element.send_keys(str(number) + Keys.RETURN)
        else:
            raise LookupError('Invalid page number: %s' % number)
        LOG.l4('%s.goToPage(number=%s)' % (self.name, number))

    def goFirstPage(self):
        """
            Navigate to first page of grid
        """
        if 'x-item-disabled' not in self.btnFirstPage.element.get_attribute(name='class'):
            self.btnFirstPage.element.click()
        else:
            raise ComponentException(message='%s: Unable to navigate to first page.' % self.name,
                driver=self.driver, screenshotName=self.name + '.goFirstPage')
        LOG.l4('%s.goFirstPage()' % self.name)

    def goLastPage(self):
        """
            Navigate to last page of grid
        """
        if 'x-item-disabled' not in self.btnLastPage.element.get_attribute(name='class'):
            self.btnLastPage.element.click()
        else:
            raise ComponentException(message='%s: Unable to navigate to last page.' % self.name,
                driver=self.driver, screenshotName=self.name + '.goLastPage')
        LOG.l4('%s.goLastPage()' % self.name)

    def goPreviousPage(self):
        """
            Navigate to previous page of grid
        """
        if 'x-item-disabled' not in self.btnPreviousPage.element.get_attribute(name='class'):
            self.btnPreviousPage.element.click()
        else:
            raise ComponentException(message='%s: Unable to navigate to previous page.' + self.name,
                driver=self.driver, screenshotName=self.name + '.goPreviousPage')
        LOG.l4('%s.goPreviousPage()' % self.name)

    def goNextPage(self):
        """
            Navigate to next page of grid
        """
        if 'x-item-disabled' not in self.btnNextPage.element.get_attribute(name='class'):
            self.btnNextPage.element.click()
        else:
            raise ComponentException(message='%s: Unable to navigate to next page.' % self.name,
                driver=self.driver, screenshotName=self.name + '.goNextPage')
        LOG.l4('%s.goNextPage()' % self.name)

    def getPageDetails(self):
        """
            Details about pages of grid. Depict paging toolbar on web UI (left bottom)
        """
        hasPaging = False
        try:
            self.element.find_element_by_xpath(xpath=self.pagingToolbarPath)
            hasPaging = True
        except NoSuchElementException:
            pass
        if hasPaging:
            details = {
                'hasFirstPage': 'x-item-disabled' not in
                    self.btnFirstPage.element.get_attribute(name='class'),
                'hasPreviousPage': 'x-item-disabled' not in
                self.btnPreviousPage.element.get_attribute(name='class'),
                'page': int(self.txtCurrentPage.element.get_attribute(name='value')),
                'hasNextPage': 'x-item-disabled' not in
                    self.btnNextPage.element.get_attribute(name='class'),
                'hasLastPage': 'x-item-disabled' not in
                    self.btnLastPage.element.get_attribute(name='class'),
                'pages': int(self.lblOfNumber.element.text().split()[1])
            }
        else:
            details = {
                'hasFirstPage': False,
                'hasPreviousPage': False,
                'page': 1,
                'hasNextPage': False,
                'hasLastPage': False,
                'pages': 1
            }
        LOG.l5('%s.getPageDetails():\n%s' % (self.name, details))
        return details

    def getRowDetails(self):
        """
            Details about rows of grid. Depict row summary next to paging toolbar on web UI (right
              bottom)
        """
        # TODO: Parse any locale pattern
        details = {}
        displaying = self.displayingLbl.element.text().strip()
        if displaying.startswith('Displaying'):
            paging = displaying.split()
            details['firstRow'] = int(paging[1])
            details['lastRow'] = int(paging[3])
            details['rows'] = int(paging[5])
        else:
            details['firstRow'] = details['lastRow'] = details['rows'] = 0
        LOG.l5('%s.getRowDetails():\n%s' % (self.name, details))
        return details
