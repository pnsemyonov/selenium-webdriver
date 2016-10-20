import os
import sys
sys.path.append(os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../.."))

from express.utils import *
from mangal.page.base_page import *
from mangal.page.header_page import HeaderPage
from mangal.page.all_storage_page import AllStoragePage
from mangal.page.luns_page import LUNsPage
from wizard.base_wizard import *


class DefineLUNsPage(BasePage):
    """
        Define 'Create LUNs. Step 1 of 2' page shown as pop-up dialog window in front of main UI
    """
    def __init__(self, locale, **kwargs):
        path = '#manager/storage/allstorage/luns'
        self.locale = locale
        super(DefineLUNsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # 'Create LUNs' label
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunCreateWiz"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # 'Step x of y: ...' label
        self._selectors['lblStepDescription'] = '//div[@data-mg-comp="subHeader"]/span/div'
        # 'Number of LUNs' label
        self._selectors['lblNumberOfLUNs'] = '//table[@data-mg-comp="numOfLuns"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # 'Number of LUNs' drop-down list
        self._selectors['dLstNumberOfLUNs'] = '//table[@data-mg-comp="numOfLuns"]'
        # Items of drop-down list
        self._selectors['dItmNumberOfLUNs'] = '//body/div[contains(@class, "mg-list-lun-count")]'

        # Elements visible on UI when number of LUNs = 1
        # 'Name' label
        self._selectors['lblName'] = '//table[@data-mg-comp="inputName"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # LUN name text box
        self._selectors['txtName'] = '//table[@data-mg-comp="inputName"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        # 'The field is required' error text below text box
        self._selectors['lblNameError'] = '//table[@data-mg-comp="inputName"]/tbody/tr/td[contains(@id, "bodyEl")]/div/ul/li'
        # 'Size' label
        self._selectors['lblSize'] = '//table[@data-mg-comp="singleLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/div/div/table[starts-with(@id, "mg-lun-size-widget")]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # LUN size text box
        self._selectors['txtSize'] = '//table[@data-mg-comp="singleLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/div/div/table[starts-with(@id, "mg-lun-size-widget")]/tbody/tr/td[contains(@id, "bodyEl")]/div[@class="x-box-layout-ct"]/div/div/table[@data-mg-comp="inputSize"]/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td/input'
        # 'Size: This field is required' error text below LUN size text box
        self._selectors['lblSizeError'] = '//table[@data-mg-comp="singleLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/div/div/table[starts-with(@id, "mg-lun-size-widget")]/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "errorEl")]/ul/li'
        # Size unit (KiB/MiB/GiB) drop-down list
        self._selectors['dLstSizeUnit'] = '//table[@data-mg-comp="singleLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/div/div/table[starts-with(@id, "mg-lun-size-widget")]/tbody/tr/td[contains(@id, "bodyEl")]/div[@class="x-box-layout-ct"]/div/div/table[@data-mg-comp="inputUnit"]'
        # Items of size unit drop-down list
        self._selectors['dItmSizeUnit'] = '//body/div[contains(@class, "mg-list-size-unit")]'

        # Elements visible on UI when number of LUNs > 1
        # 'Name and size' label
        self._selectors['lblNameAndSize'] = '//table[@data-mg-comp="multiLunWidget"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Auto-name and size radio button
        self._selectors['rBtnAutoNameAndSize'] = '//table[@data-mg-comp="autoRadio"]'
        # 'Auto-name and size' label
        self._selectors['lblAutoNameAndSize'] = '//table[@data-mg-comp="autoRadio"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'
        # Manually name and size radio button
        self._selectors['rBtnManuallyNameAndSize'] = '//table[@data-mg-comp="manualRadio"]'
        # 'Manually name and size' label
        self._selectors['lblManuallyNameAndSize'] = '//table[@data-mg-comp="manualRadio"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'

        # Elements become visible on UI when 'Auto-name and size' radio button is selected
        # 'Prefix' label
        self._selectors['lblPrefix'] = '//table[@data-mg-comp="namePrefix"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Prefix text box
        self._selectors['txtPrefix'] = '//table[@data-mg-comp="namePrefix"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        # 'Suffix' label
        self._selectors['lblSuffix'] = '//span[starts-with(@id, "mg-widget-auto-name")]/div/table[starts-with(@id, "fieldcontainer")]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Suffix drop-down list
        self._selectors['dLstSuffix'] = '//table[@data-mg-comp="nameSuffix"]'
        # Items of suffix drop-down list
        self._selectors['dItmSuffix'] = '//body/div[contains(@class, "mg-list-name-suffix")]'
        # 'Start at' label
        self._selectors['lblStartAt'] = '//span[starts-with(@id, "mg-widget-auto-name")]/div/table[starts-with(@id, "fieldcontainer")]/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "containerEl")]/div[contains(@id, "innerCt")]/div/table[starts-with(@id, "displayfield")]/tbody/tr/td[contains(@id, "bodyEl")]/div'
        # 'Start at' text box
        self._selectors['txtStartAt'] = '//table[@data-mg-comp="nameStartAt"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        # 'Preview' label (below suffix text box)
        self._selectors['lblPreview'] = '//span[starts-with(@id, "mg-widget-auto-name")]/div/div/span/div'
        # 'Size' label
        self._selectors['lblAutoSize'] = '//span[starts-with(@id, "mg-auto-lun-name-widget")]/div/table/tbody/tr/td[contains(@id, "labelCell")]/label'
        # Size text box
        self._selectors['txtAutoSize'] = '//span[starts-with(@id, "mg-auto-lun-name-widget")]/div/table/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "containerEl")]/div[contains(@id, "innerCt")]/div/table[starts-with(@id, "mg-numberfield")]/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[starts-with(@id, "mg-numberfield")]/input'
        # Size unit drop-down list
        self._selectors['dLstAutoSizeUnit'] = '//span[starts-with(@id, "mg-auto-lun-name-widget")]/div/table/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "containerEl")]/div[contains(@id, "innerCt")]/div/table[starts-with(@id, "combobox")]'
        # Items of size unit drop-down list
        self._selectors['dItmAutoSizeUnit'] = '//body/div[contains(@class, "mg-list-size-unit")]'
        # 'Size: This field is required' error message (below size text box)
        self._selectors['lblAutoSizeError'] = '//span[starts-with(@id, "mg-auto-lun-name-widget")]/div/table/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "errorEl")]/ul/li'

        # Elements become visible on UI when 'Manually name and size' radio button is pressed.
        #   Presence of {index} signature points us to that CSS selector will be handled in dynamic
        #   way, by replacing {index} with an integer corresponding to particular LUN details
        #   section in list of sections (which are <table>s).
        # 'Enter LUN Name' text box (indexed)
        self._selectors['txtManuallyName'] = '//table[@data-mg-comp="multiLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/span/div/div/div/div/table[{index}]/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "containerEl")]/div/div/table[@data-mg-comp="inputName"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        # 'Enter LUN Size' text box (indexed)
        self._selectors['txtManuallySize'] = '//table[@data-mg-comp="multiLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/span/div/div/div/div/table[{index}]/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "containerEl")]/div/div/table[starts-with(@id, "mg-lun-size-widget")]/tbody/tr/td[contains(@id, "bodyEl")]/div/div/div/table[@data-mg-comp="inputSize"]/tbody/tr/td[contains(@id, "bodyEl")]/table/tbody/tr/td[starts-with(@id, "mg-numberfield")]/input'
        # Manually defined LUN size drop-down list (indexed)
        self._selectors['dLstManuallySizeUnit'] = '//table[@data-mg-comp="multiLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/span/div/div/div/div/table[{index}]/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "containerEl")]/div/div/table[starts-with(@id, "mg-lun-size-widget")]/tbody/tr/td[contains(@id, "bodyEl")]/div/div/div/table[@data-mg-comp="inputUnit"]'
        # Items of manually defined LUN size drop-down list
        # <div>s representing drop-down lists of size units (B, KiB, MiB, GiB, TiB) appear in HTML
        #   tree dynamically once a drop-down expanded, not allowing to locate div's by their
        #   indices. So, active <div> may be located by absence of 'display: none' in its style.
        self._selectors['dItmManuallySizeUnit'] = '//body/div[contains(@class, "mg-list-size-unit") and not(contains(@style, "display: none"))]'
        # 'Size: <error>' message label (below 'Enter LUN Name' text box) (indexed)
        self._selectors['lblManuallyNameError'] = '//table[@data-mg-comp="multiLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/span/div/div/div/div/table[{index}]/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "errorEl")]/ul/li[1]'
        self._selectors['lblManuallySizeError'] = '//table[@data-mg-comp="multiLunWidget"]/tbody/tr/td[contains(@id, "bodyEl")]/div/span/div/div/div/div/table[{index}]/tbody/tr/td[contains(@id, "bodyEl")]/div[contains(@id, "errorEl")]/ul/li[2]'

        # Elements of 'Add to a consistency group' section (become visible when 'Add to consistency
        #   group' checkbox is checked)
        # 'Add to consistency group' checkbox
        self._selectors['chkAddToConsistencyGroup'] = '//fieldset[@data-mg-comp="cg-fieldset"]/legend/span/div/table'
        # 'Add to consistency group' label
        self._selectors['lblAddToConsistencyGroup'] = '//fieldset[@data-mg-comp="cg-fieldset"]/legend/span/div/div'
        # 'A consistency group allows you to back up...' description label
        self._selectors['lblConsistencyGroupDescription'] = '//fieldset[@data-mg-comp="cg-fieldset"]/legend/span/div/div/span'
        # 'Parent consistency group' label
        self._selectors['lblParentConsistencyGroup'] = '//table[@data-mg-comp="parentCG"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # 'Select a parent' combo box
        self._selectors['cBoxParentConsistencyGroup'] = '//table[@data-mg-comp="parentCG"]'
        # 'Select a parent' combo box item list
        self._selectors['cItmParentConsistencyGroup'] = '//body/div[starts-with(@id, "treepanel")]'
        # 'New consistency group' label
        self._selectors['lblNewConsistencyGroup'] = '//table[@data-mg-comp="newCG"]/tbody/tr/td[contains(@id, "labelCell")]/label'
        # 'Enter consistency group name' text box
        self._selectors['txtNewConsistencyGroup'] = '//table[@data-mg-comp="newCG"]/tbody/tr/td[contains(@id, "bodyEl")]/input'
        self._selectors['lblConsistencyGroupError'] = '//fieldset[@data-mg-comp="cg-fieldset"]/div/span/div/div[@id="mg-lundef-error-msg-el"]/ul/li[1]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnBack'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="back"]'
        self._selectors['btnNext'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="next"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblStepDescription'] = label.Label(driver=self.driver,
            selector=self.selectors.lblStepDescription, name=self.name)
        self.components['lblNumberOfLUNs'] = label.Label(driver=self.driver,
            selector=self.selectors.lblNumberOfLUNs, name=self.name)
        self.components['dLstNumberOfLUNs'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstNumberOfLUNs, name=self.name)
        self.components['dItmNumberOfLUNs'] = dropdownlist.DropDownItems(driver=self.driver,
            selector=self.selectors.dItmNumberOfLUNs, name=self.name)
        self.dLstNumberOfLUNs.addItems(items=self.dItmNumberOfLUNs)
        self.components['lblName'] = label.Label(driver=self.driver,
            selector=self.selectors.lblName, name=self.name)
        self.components['txtName'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtName, name=self.name)
        self.components['lblNameError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblNameError, name=self.name)
        self.components['lblSize'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSize, name=self.name)
        self.components['txtSize'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtSize, name=self.name)
        self.components['lblSizeError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSizeError, name=self.name)
        self.components['dLstSizeUnit'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstSizeUnit, name=self.name)
        self.components['dItmSizeUnit'] = dropdownlist.DropDownItems(driver=self.driver,
            selector=self.selectors.dItmSizeUnit, name=self.name)
        self.dLstSizeUnit.addItems(items=self.dItmSizeUnit)
        self.components['lblNameAndSize'] = label.Label(driver=self.driver,
            selector=self.selectors.lblNameAndSize, name=self.name)
        self.components['rBtnAutoNameAndSize'] = radiobutton.RadioButton(driver=self.driver,
            selector=self.selectors.rBtnAutoNameAndSize, name=self.name)
        self.components['lblAutoNameAndSize'] = label.Label(driver=self.driver,
            selector=self.selectors.lblAutoNameAndSize, name=self.name)
        self.components['rBtnManuallyNameAndSize'] = radiobutton.RadioButton(driver=self.driver,
            selector=self.selectors.rBtnManuallyNameAndSize, name=self.name)
        self.components['lblManuallyNameAndSize'] = label.Label(driver=self.driver,
            selector=self.selectors.lblManuallyNameAndSize, name=self.name)
        self.components['lblPrefix'] = label.Label(driver=self.driver,
            selector=self.selectors.lblPrefix, name=self.name)
        self.components['txtPrefix'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtPrefix, name=self.name)
        self.components['lblSuffix'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSuffix, name=self.name)
        self.components['dLstSuffix'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstSuffix, name=self.name)
        self.components['dItmSuffix'] = dropdownlist.DropDownItems(driver=self.driver,
            selector=self.selectors.dItmSuffix, name=self.name)
        self.dLstSuffix.addItems(items=self.dItmSuffix)
        self.components['lblStartAt'] = label.Label(driver=self.driver,
            selector=self.selectors.lblStartAt, name=self.name)
        self.components['txtStartAt'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtStartAt, name=self.name)
        self.components['lblPreview'] = label.Label(driver=self.driver,
            selector=self.selectors.lblPreview, name=self.name)
        self.components['lblAutoSize'] = label.Label(driver=self.driver,
            selector=self.selectors.lblAutoSize, name=self.name)
        self.components['txtAutoSize'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtAutoSize, name=self.name)
        self.components['dLstAutoSizeUnit'] = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstAutoSizeUnit, name=self.name)
        self.components['dItmAutoSizeUnit'] = dropdownlist.DropDownItems(driver=self.driver,
            selector=self.selectors.dItmAutoSizeUnit, name=self.name)
        self.dLstAutoSizeUnit.addItems(items=self.dItmAutoSizeUnit)
        self.components['lblAutoSizeError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblAutoSizeError, name=self.name)

        # As all 'Manually...' controls are indexed (selector has '{index}'), they should be created
        #   in end script rather than here.
        # As example, to create component object corresponding LUN name text box in 3rd row of group
        #   'Manually name and size', use:
        #     from mangal.component.textbox import TextBox
        #     textBox = TextBox(driver=self.driver,
        #     selector=self.selectors.txtManuallyName(index=1))

        self.components['lblManuallyNameError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblManuallyNameError, name=self.name)
        self.components['lblManuallySizeError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblManuallySizeError, name=self.name)
        self.components['chkAddToConsistencyGroup'] = checkbox.CheckBox(driver=self.driver,
            selector=self.selectors.chkAddToConsistencyGroup, name=self.name)
        self.components['lblAddToConsistencyGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.lblAddToConsistencyGroup, name=self.name)
        self.components['lblConsistencyGroupDescription'] = label.Label(driver=self.driver,
            selector=self.selectors.lblConsistencyGroupDescription, name=self.name)
        self.components['lblParentConsistencyGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.lblParentConsistencyGroup, name=self.name)
        self.components['cBoxParentConsistencyGroup'] = combobox.ComboBox(driver=self.driver,
            selector=self.selectors.cBoxParentConsistencyGroup, name=self.name)
        self.components['cItmParentConsistencyGroup'] = combobox.ComboBoxItems(driver=self.driver,
            selector=self.selectors.cItmParentConsistencyGroup, name=self.name)
        self.cBoxParentConsistencyGroup.addItems(items=self.cItmParentConsistencyGroup)
        self.components['lblNewConsistencyGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.lblNewConsistencyGroup, name=self.name)
        self.components['txtNewConsistencyGroup'] = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtNewConsistencyGroup, name=self.name)
        self.components['lblConsistencyGroupError'] = label.Label(driver=self.driver,
            selector=self.selectors.lblConsistencyGroupError, name=self.name)
        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel, name=self.name)
        self.components['btnBack'] = button.Button(driver=self.driver,
            selector=self.selectors.btnBack, name=self.name)
        self.components['btnNext'] = button.Button(driver=self.driver,
            selector=self.selectors.btnNext, name=self.name)
        # Component uniquely identifying given page
        self.components['token'] = self.dLstNumberOfLUNs

    def defineSingleLUN(self, name, size):
        """
            On dialog page 'Step 1 of 1: Define LUN properties' define:
              - Number of LUNs
              - Name
              - Size and size unit
            @param name: Name of LUN
            @param size: Size of LUN ('1024 K', '2GB' etc.)
        """
        # Verify proper page is displayed
        self.dLstNumberOfLUNs.waitUntilPresent()
        # Select single LUN
        self.dLstNumberOfLUNs.select(item='1')
        self.txtName.clear()
        self.txtName.setText(text=name)

        # Extract from provided size ('1024 K', '2GB' etc.) included size unit ('K', 'M' etc.)
        sizeUnit = Utility.getLocalizedSizeUnit(sizeUnit=Utility.getSizeUnit(size=size),
            locale=self.locale)
        # Select size unit ('KiB', 'Gib')
        self.dLstSizeUnit.select(item=sizeUnit)
        self.txtSize.clear()
        sizeText = Utility.getLocalizedSizeFormat(size=size, locale=self.locale)
        self.txtSize.setText(text=sizeText)

    def defineMultipleLUNsAuto(self, number, size, prefix, suffix=None, startAt=None):
        self.dLstNumberOfLUNs.waitUntilPresent()
        self.dLstNumberOfLUNs.select(item=str(number))

        self.rBtnAutoNameAndSize.select()

        self.txtPrefix.clear()
        self.txtPrefix.setText(text=prefix)

        if suffix is not None:
            self.dLstSuffix.select(item=suffix)

        if startAt is not None:
            self.txtStartAt.clear()
            self.txtStartAt.setText(text=str(startAt))

        sizeUnit = Utility.getLocalizedSizeUnit(sizeUnit=Utility.getSizeUnit(size=size),
            locale=self.locale)
        self.dLstAutoSizeUnit.select(item=sizeUnit)
        self.txtAutoSize.clear()
        sizeText = Utility.getLocalizedSizeFormat(size=size, locale=self.locale)
        self.txtAutoSize.setText(text=sizeText)

    def defineMultipleLUNsManually(self, lunsProperties):
        """
            Define properties of multiple LUNs set manually (not using auto-naming with
               prefix/suffix).
            @param lunsProperties: List of dictionaries specifying properties of LUNs to create.
            Ex.:
            [
                {
                    'name': 'LuN_1',
                    'size': '120M'
                }, ...
            ]
        """
        self.dLstNumberOfLUNs.waitUntilPresent()
        # As many LUNs as many list's elements provided
        self.dLstNumberOfLUNs.select(item=str(len(lunsProperties)))

        self.rBtnManuallyNameAndSize.waitUntilPresent()
        self.rBtnManuallyNameAndSize.select()

        dItmManuallySizeUnit = dropdownlist.DropDownItems(driver=self.driver,
        selector=self.selectors.dItmManuallySizeUnit, name=self.name)
        for lunIndex in range(len(lunsProperties)):
            txtName = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtManuallyName(index=lunIndex + 1), name=self.name)
            txtName.clear()
            txtName.setText(text=lunsProperties[lunIndex]['name'])

            txtSize = textbox.TextBox(driver=self.driver,
            selector=self.selectors.txtManuallySize(index=lunIndex + 1), name=self.name)
            txtSize.clear()
            size = lunsProperties[lunIndex]['size']
            sizeUnit = Utility.getLocalizedSizeUnit(sizeUnit=Utility.getSizeUnit(size=size),
                locale=self.locale)
            sizeText = Utility.getLocalizedSizeFormat(size=size, locale=self.locale)
            txtSize.setText(text=sizeText)

            dLstSizeUnit = dropdownlist.DropDownList(driver=self.driver,
            selector=self.selectors.dLstManuallySizeUnit(index=lunIndex + 1), name=self.name)
            dLstSizeUnit.addItems(items=dItmManuallySizeUnit)
            dLstSizeUnit.select(item=sizeUnit)

    def addToConsistencyGroup(self, parentConsistencyGroup=None, newConsistencyGroup=None):
        self.chkAddToConsistencyGroup.select()
        if (parentConsistencyGroup is not None) and (newConsistencyGroup is not None):
            if not self.cBoxParentConsistencyGroup.isEnabled():
                raise AttributeError("Parent consistency group '%s' does not exist." %
                parentConsistencyGroup)
        if parentConsistencyGroup is not None:
            self.cBoxParentConsistencyGroup.select(item=parentConsistencyGroup)
        if newConsistencyGroup is not None:
            self.txtNewConsistencyGroup.clear()
            self.txtNewConsistencyGroup.setText(text=newConsistencyGroup)


class SelectInitiatorGroupsPage(BasePage):
    """
        Define 'Create LUNs. Step 2 of 2' page shown as pop-up dialog window in front of main UI
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(SelectInitiatorGroupsPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunCreateWiz"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        self._selectors['lblStepDescription'] = '//body/div[@data-mg-comp="lunCreateWiz"]/div[contains(@id, "body")]/span/div/div[starts-with(@id, "container")]/span/div'
        self._selectors['sBoxSearch'] = '//table[@data-mg-comp="searchGrid"]'
        self._selectors['chkShowOnlySelectedInitiatorGroups'] = '//table[@data-mg-comp="showSelectedRowOnly"]'
        self._selectors['lblShowOnlySelectedInitiatorGroups'] = '//table[@data-mg-comp="showSelectedRowOnly"]/tbody/tr/td[contains(@id, "bodyEl")]/div/label'
        self._selectors['gridInitiatorGroups'] = '//div[@data-mg-comp="lunMapPanel"]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnBack'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="back"]'
        self._selectors['btnNext'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="next"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblStepDescription'] = label.Label(driver=self.driver,
            selector=self.selectors.lblStepDescription, name=self.name)
        self.components['sBoxSearch'] = searchbox.SearchBox(driver=self.driver,
            selector=self.selectors.sBoxSearch, name=self.name)
        self.components['chkShowOnlySelectedInitiatorGroups'] =\
        checkbox.CheckBox(driver=self.driver,
            selector=self.selectors.chkShowOnlySelectedInitiatorGroups, name=self.name)
        self.components['lblShowOnlySelectedInitiatorGroups'] = label.Label(driver=self.driver,
            selector=self.selectors.lblShowOnlySelectedInitiatorGroups, name=self.name)
        self.components['gridInitiatorGroups'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridInitiatorGroups, name=self.name)
        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel, name=self.name)
        self.components['btnBack'] = button.Button(driver=self.driver,
            selector=self.selectors.btnBack, name=self.name)
        self.components['btnNext'] = button.Button(driver=self.driver,
            selector=self.selectors.btnNext, name=self.name)
        # Component uniquely identifying given page
        self.components['token'] = self.chkShowOnlySelectedInitiatorGroups

    def selectInitiatorGroups(self, initiatorGroups):
        """
            On dialog page 'Step 2 of 2: Select initiatot groups(s)' selects (checks) rows with
              provided IG(s)
        """
        self.gridInitiatorGroups.select(initiator_groups=initiatorGroups)


class ConfirmPage(BasePage):
    """
        Define 'Create LUNs. Confirm the following information...' page shown as pop-up dialog
          window in front of UI
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(ConfirmPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunCreateWiz"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        self._selectors['lblStepDescription'] = '//body/div[@data-mg-comp="lunCreateWiz"]/div[contains(@id, "body")]/span/div/div[starts-with(@id, "container")]/span/div'
        self._selectors['lblNewConsistencyGroup'] = '//div[@data-mg-comp="lunSummaryPanel"]/div[starts-with(@id, "toolbar")]/div/div/div'
        self._selectors['gridLUNs'] = '//div[@data-mg-comp="lunSummaryPanel"]'

        # Buttons at the bottom of the dialog
        self._selectors['btnCancel'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'
        self._selectors['btnBack'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="back"]'
        self._selectors['btnFinish'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="finish"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblStepDescription'] = label.Label(driver=self.driver,
            selector=self.selectors.lblStepDescription, name=self.name)
        self.components['lblNewConsistencyGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.lblNewConsistencyGroup, name=self.name)
        self.components['gridLUNs'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridLUNs, name=self.name)
        self.components['btnCancel'] = button.Button(driver=self.driver,
            selector=self.selectors.btnCancel, name=self.name)
        self.components['btnBack'] = button.Button(driver=self.driver,
            selector=self.selectors.btnBack, name=self.name)
        self.components['btnFinish'] = button.Button(driver=self.driver,
            selector=self.selectors.btnFinish, name=self.name)
        # Component uniquely identifying given page
        self.components['token'] = [self.gridLUNs, self.btnFinish]

    def hasNext(self):
        return True

    def goNext(self):
        self.btnFinish.waitUntilEnabled()
        self.btnFinish.click()


class ClosePage(BasePage):
    """
        Define 'Create LUNs. Created ... LUNs.' page (final page of the dialog) shown as pop-up
          dialog window on UI.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/luns'
        super(ClosePage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        self._selectors['lblCheckSign'] = '//body/div[@data-mg-comp="lunCreateWiz"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "iconEl")]'
        self._selectors['lblTitle'] = '//body/div[@data-mg-comp="lunCreateWiz"]/div[contains(@class, "x-header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        self._selectors['lblNewConsistencyGroup'] = '//div[@data-mg-comp="summaryToolBar_parentCG"]'
        self._selectors['gridLUNs'] = '//div[@data-mg-comp="lunSummaryPanel"]'
        self._selectors['btnClose'] = '//div[@data-mg-comp="lunCreateWiz"]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="close"]'

    def setupComponents(self):
        self.components['lblCheckSign'] = label.Label(driver=self.driver,
            selector=self.selectors.lblCheckSign, name=self.name)
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblNewConsistencyGroup'] = label.Label(driver=self.driver,
            selector=self.selectors.lblNewConsistencyGroup, name=self.name)
        self.components['gridLUNs'] = grid.Grid(driver=self.driver,
            selector=self.selectors.gridLUNs, name=self.name)
        self.components['btnClose'] = button.Button(driver=self.driver,
            selector=self.selectors.btnClose, name=self.name)
        # Component(s) uniquely identifying given page (it's unlikely that different pages will have
        #   components with same selectors)
        self.components['token'] = [self.gridLUNs, self.btnClose]

    def hasNext(self):
        return False

    def hasBack(self):
        return False

    def close(self):
        self.btnClose.waitUntilEnabled()
        self.btnClose.click()


class CreateLUNsWizard(BaseWizard):
    def __init__(self, driver, locale='en'):
        super(CreateLUNsWizard, self).__init__(driver=driver)
        self.addPage(name='defineLUNsPage', page=DefineLUNsPage(driver=self.driver, locale=locale))
        self.addPage(name='selectInitiatorGroupsPage',
        page=SelectInitiatorGroupsPage(driver=self.driver))
        self.addPage(name='confirmPage', page=ConfirmPage(driver=self.driver))
        self.addPage(name='closePage', page=ClosePage(driver=self.driver))

    def open(self):
        # Select menu item 'Create -> LUNs'
        HeaderPage(driver=self.driver).btnManager.click()
        AllStoragePage(driver=self.driver).tabLUNs.click()
        LUNsPage(driver=self.driver).menuCreate.select(item='LUNs')
        self.defineLUNsPage.waitUntilOpen()
        self.activePageNumber = 0
        self.activePage = self._pages[self._pages.keys()[self.activePageNumber]]
