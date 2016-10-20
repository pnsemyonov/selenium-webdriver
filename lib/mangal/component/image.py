from base_component import *


class Image(BaseComponent):
    """
        Image component.
    """
    def __init__(self, driver, selector, name=''):
        """
            @param driver: Instance of Mangal.Driver
            @param selector: Selector of button element
            @param name: Name of component
        """
        super(Image, self).__init__(driver=driver, selector=selector, name=name)
