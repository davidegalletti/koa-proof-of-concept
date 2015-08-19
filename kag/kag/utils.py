import importlib
from datetime import datetime

from django.conf import settings

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

class poor_mans_logger():
        
    def log(self, message):
        logfile = open('/tmp/' + settings.LOG_FILE_NAME + '.log', "a")
        logfile.write(str(datetime.now()) + " " + message + "\n")
        logfile.close
        
    def debug(self, message):
        self.log("Debug: " + message)
        
    def info(self, message):
        self.log("Info: " + message)
        
    def warning(self, message):
        self.log("Warning: " + message)
        
    def error(self, message):
        self.log("Error: " + message)

    def critical(self, message):
        self.log("Critical: " + message)


class Choices():
    # in lower case as they are brought to lower before verification
    FORMAT = ['xml','json','html','browse']
    SCHEME = ['http','https']

