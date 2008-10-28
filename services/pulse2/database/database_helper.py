from pulse2.utils import Singleton
from pulse2.database.sqlalchemy_tests import checkSqlalchemy
import logging

class DatabaseHelper(Singleton):
    is_activated = False
    config = None
    def db_check(self):
        if not checkSqlalchemy():
            self.logger.error("Sqlalchemy version error : is not %s.%s.* version" % (SA_MAJOR, SA_MINOR))
            return False

        conn = self.connected()
        if conn:
            self.logger.error("Can't connect to database (s=%s, p=%s, b=%s, l=%s, p=******). Please check inventory.ini." % (self.config.dbhost, self.config.dbport, self.config.dbbase, self.config.dbuser))
            return False
        
        return True
    
    def connected(self):
        try:
            if (self.db != None) and (session != None):
                return True
            return False
        except:
            return False

    def makeConnectionPath(self):
        """
        Build and return the db connection path according to the plugin configuration

        @rtype: str
        """
        if self.config == None:
            raise Exception("Object must have a config attribute")
        if self.config.dbport:
            port = ":" + str(self.config.dbport)
        else:
            port = ""
        url = "%s://%s:%s@%s%s/%s" % (self.config.dbdriver, self.config.dbuser, self.config.dbpasswd, self.config.dbhost, port, self.config.dbname)
        if self.config.dbsslenable:
            url = url + "?ssl_ca=%s&ssl_key=%s&ssl_cert=%s" % (self.config.dbsslca, self.config.dbsslkey, self.config.dbsslcert)
        return url
    
    def enableLogging(self, level = None):
        """
        Enable log for sqlalchemy.engine module using the level configured by the db_debug option of the plugin configuration file.
        The SQL queries will be loggued.
        """
        if not level:
            level = logging.INFO
        logging.getLogger("sqlalchemy.engine").setLevel(level)

    def disableLogging(self):
        """
        Disable log for sqlalchemy.engine module
        """
        logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

