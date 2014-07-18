import importlib

class xmlMinidom():
    @staticmethod    
    def getString(xmldoc, tag):
        try:
            return xmldoc.getElementsByTagName(tag)[0].firstChild.data
        except:
            return ""

    @staticmethod    
    def getStringAttribute(xmldoc, tag):
        try:
            return xmldoc.attributes[tag].firstChild.data
        except:
            return "" 
        
    @staticmethod    
    def getNaturalAttribute(xmldoc, tag):
        '''
        a natural number; if it's not there -1 is returned
        '''
        try:
            return int(xmldoc.attributes[tag].firstChild.data)
        except:
            return -1

def load_class(module_name, class_name):
    """
    dynamically load a class from a string
    """
    module = importlib.import_module(module_name)
    # Finally, we retrieve the Class
    return getattr(module, class_name)