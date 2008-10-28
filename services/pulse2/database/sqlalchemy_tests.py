from sqlalchemy import *
from sqlalchemy.orm import *
from pulse2.database.utilities import create_method

SA_MAJOR = 0
SA_MINOR = 4

for m in ['first', 'count', 'all']:
    try:
        getattr(Query, '_old_'+m)
    except AttributeError:
        setattr(Query, '_old_'+m, getattr(Query, m))
        setattr(Query, m, create_method(m))
        
def checkSqlalchemy():
    try:
        import sqlalchemy
        a_version = sqlalchemy.__version__.split('.')
        if len(a_version) > 2 and str(a_version[0]) == str(SA_MAJOR) and str(a_version[1]) == str(SA_MINOR):
            return True
    except:
        pass
    return False


