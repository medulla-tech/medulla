def possibleQueries(): # TODO : need to put this in the conf file
    return {
        'list' : {
            'Software/ProductName':['string'],
            'Hardware/ProcessorType':['string'],
            'Hardware/OperatingSystem':['string'],
            'Drive/TotalSpace':['int']
        },
        'double' : {
            'Software/Products': [
                ['Software/ProductName', 'string'],
                ['Software/ProductVersion', 'int']
            ]
        },
        'doubledetail' : {
            'Software/ProductVersion' : 'int'
        },
        'halfstatic' : {
            'Registry/Value' : ['string', 'Path', 'DisplayName']
        }
        
    }
    
