from sqlalchemy import *

SA_MAYOR = 0
SA_MINOR = 3

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
        if len(a_version) > 2 and str(a_version[0]) == str(SA_MAYOR) and str(a_version[1]) == str(SA_MINOR):
            return True
    except:
        pass
    return False


