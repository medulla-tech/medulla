from sqlalchemy import *
from sqlalchemy.orm import *

SA_MAJOR = 0
SA_MINOR = 4

def checkSqlalchemy():
    try:
        import sqlalchemy
        a_version = sqlalchemy.__version__.split('.')
        if len(a_version) > 2 and str(a_version[0]) == str(SA_MAJOR) and str(a_version[1]) == str(SA_MINOR):
            return True
    except:
        pass
    return False


