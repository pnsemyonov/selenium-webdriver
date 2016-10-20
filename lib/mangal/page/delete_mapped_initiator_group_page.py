from base_page import *


class DeleteMappedInitiatorGroupPage(BasePage):
    """
        Warning window appearing when user attempts to delete initiator group with mapped LUNs
          (Initiator Groups page). Most basic, has only warning message and button 'Close'.
    """
    def __init__(self, **kwargs):
        path = '#manager/storage/allstorage/igroups'
        super(DeleteMappedInitiatorGroupPage, self).__init__(path=path, **kwargs)

    def setupSelectors(self):
        # Title "Initiator group can't be deleted now"
        self._selectors['lblTitle'] = '//body/div[contains(@id, "deleteigroupdialog")]/div[contains(@id, "header")]/div/div/div/div[contains(@id, "header_hd")]/span'
        # Subtitle (is initiator group name when single)
        self._selectors['lblSubtitle'] = '//body/div[contains(@id, "deleteigroupdialog")]/div[contains(@id, "body")]/span/div/div[@data-mg-comp="subTitle"]'

        # Message "Initiator group with mapped LUNs can't be deleted..."
        self._selectors['lblMessage'] = '//body/div[contains(@id, "deleteigroupdialog")]/div[contains(@id, "body")]/span/div/div[@data-mg-comp="msg"]/span/div'

        # Button 'Close'
        self._selectors['btnClose'] = '//body/div[contains(@id, "deleteigroupdialog")]/div[@data-mg-comp="footer"]/div/div/a[@data-mg-comp="cancel"]'

    def setupComponents(self):
        self.components['lblTitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblTitle, name=self.name)
        self.components['lblSubtitle'] = label.Label(driver=self.driver,
            selector=self.selectors.lblSubtitle, name=self.name)

        self.components['lblMessage'] = label.Label(driver=self.driver,
            selector=self.selectors.lblMessage, name=self.name)

        self.components['btnClose'] = button.Button(driver=self.driver,
            selector=self.selectors.btnClose, name=self.name)

        # Component uniquely identifying given page
        self.components['token'] = self.lblTitle
