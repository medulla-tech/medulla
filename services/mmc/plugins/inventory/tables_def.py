from mmc.support.mmctools import Singleton

class PossibleQueries(Singleton):
    def init(self, config):
        self.list = config.list
        self.double = config.double
        self.halfstatic = config.halfstatic
        
    def possibleQueries(self, value = None): # TODO : need to put this in the conf file
        if value == None:
            return {
                'list':self.list,
                'double':self.double,
                'halfstatic':self.halfstatic
            }
        else:
            if hasattr(self, value):
                return getattr(self, value)
            return []
            
#    return {
#        'list' : {
#            'Software/ProductName':['string'],
#            'Hardware/ProcessorType':['string'],
#            'Hardware/OperatingSystem':['string'],
#            'Drive/TotalSpace':['int']
#        },
#        'double' : {
#            'Software/Products': [
#                ['Software/ProductName', 'string'],
#                ['Software/ProductVersion', 'int']
#            ]
#        },
#        'doubledetail' : {
#            'Software/ProductVersion' : 'int'
#        },
#        'halfstatic' : {
#            'Registry/Value' : ['string', 'Path', 'DisplayName']
#        }
#    }
    
