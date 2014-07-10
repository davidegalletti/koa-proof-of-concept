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
