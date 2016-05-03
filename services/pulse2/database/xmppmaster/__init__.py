# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
xmppmaster database handler
"""

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func
from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
from sqlalchemy.exc import DBAPIError

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.xmppmaster.schema import Network, Machines, RelaisServer, Users, Regles, Has_machinesusers,Has_relaisserverregles, Base, UserLog
# Imported last
import logging



class XmppMasterDatabase(DatabaseHelper):
    """
    Singleton Class to query the xmppmaster database.

    """
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "xmppmaster"
        self.configfile = "xmppmaster.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):

        if self.is_activated:
            return None
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM xmppmaster.version limit 1;")
        re = [x.Number for x in result]
        #logging.getLogger().debug("xmppmaster database connected (version:%s)"%(re[0]))
        return True


    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the xmppmaster database
        """
        # No mapping is needed, all is done on schema file
        return


    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError, e:
                logging.getLogger().error(e)
            except Exception, e:
                logging.getLogger().error(e)
            if ret: break
        if not ret:
            raise "Database connection error"
        return ret

    # =====================================================================
    # xmppmaster FUNCTIONS
    # =====================================================================
    
    @DatabaseHelper._session
    def log(self, session, msg, type = "info"):
        try:
            new_log = UserLog()
            new_log.msg = msg
            new_log.type = type
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._session
    def addPresenceMachine(self, session, jid, plateform, hostname, archi, 
                           uuid_inventorymachine, ip_xmpp, subnetxmpp, macadress, agenttype, classutil='private'):
        print "%s %s %s %s %s %s %s %s %s %s"%(jid, plateform, hostname, archi, uuid_inventorymachine, ip_xmpp, subnetxmpp, macadress, agenttype, classutil)
        try:
            new_machine = Machines()
            new_machine.jid = jid
            new_machine.plateform = plateform
            new_machine.hostname = hostname
            new_machine.archi = archi
            new_machine.uuid_inventorymachine = uuid_inventorymachine
            new_machine.ip_xmpp = ip_xmpp
            new_machine.subnetxmpp = subnetxmpp
            new_machine.macadress = macadress
            new_machine.agenttype = agenttype
            new_machine.classutil = classutil
            session.add(new_machine)
            session.commit()
            session.flush()
            if agenttype == "relaisserver":
                sql = "UPDATE `xmppmaster`.`relaisserver` SET `actif`='1' WHERE `xmppmaster`.`relaisserver`.`nameserver`='%s'"%hostname;
                session.execute(sql)
                session.commit()
                session.flush()
        except Exception, e:
            #logging.getLogger().error("addPresenceMachine %s" % jid)
            logging.getLogger().error(str(e))
            return -1
        return new_machine.id

    @DatabaseHelper._session
    def addPresenceNetwork(self, session, macadress, ipadress, broadcast, gateway, mask, mac, id_machine):
        try:
            new_network = Network()
            new_network.macadress=macadress
            new_network.ipadress=ipadress
            new_network.broadcast=broadcast
            new_network.gateway=gateway
            new_network.mask=mask
            new_network.mac=mac
            new_network.machines_id=id_machine
            session.add(new_network)
            session.commit()
            session.flush()
        except Exception, e:
            #logging.getLogger().error("addPresenceNetwork : %s " % new_network)
            logging.getLogger().error(str(e))
        #return new_network.toDict()

    @DatabaseHelper._session
    def addServerRelais(self, session,
                        urlguacamole,
                        subnet,
                        nameserver,
                        groupedeploy,
                        ipserver,
                        ipconnection,
                        portconnection,
                        port, mask, jid, longitude="", latitude="", actif=False, classutil="private"):
        sql = "SELECT count(*) as nb FROM xmppmaster.relaisserver where `relaisserver`.`nameserver`='%s';"%nameserver
        nb = session.execute(sql)
        session.commit()
        session.flush()
        result=[x for x in nb][0][0]
        #logging.getLogger().info("nb %d"%result)
        if result == 0 :
            try:
                new_relaisserver = RelaisServer()
                new_relaisserver.urlguacamole = urlguacamole
                new_relaisserver.subnet = subnet
                new_relaisserver.nameserver = nameserver
                new_relaisserver.groupedeploy = groupedeploy
                new_relaisserver.ipserver = ipserver
                new_relaisserver.port = port
                new_relaisserver.mask = mask
                new_relaisserver.jid = jid
                new_relaisserver.ipconnection = ipconnection
                new_relaisserver.portconnection = portconnection
                new_relaisserver.longitude = longitude
                new_relaisserver.latitude = latitude
                new_relaisserver.actif = actif
                new_relaisserver.classutil = classutil
                session.add(new_relaisserver)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))
        else:
            try:
                sql = "UPDATE `xmppmaster`.`relaisserver` SET `actif`=%s, `classutil`='%s' WHERE `xmppmaster`.`relaisserver`.`nameserver`='%s';"%(actif,classutil,nameserver)
                session.execute(sql)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))


    @DatabaseHelper._session
    def adduser(self, session, 
                    namesession,
                    hostname,
                    city = "",
                    region_name = "",
                    time_zone = "",
                    longitude = "",
                    latitude = "",
                    postal_code = "",
                    country_code = "",
                    country_name = ""):
        sql = "SELECT count(*) as nb FROM xmppmaster.users where `users`.`namesession`='%s' and `users`.`hostname`='%s';"%(namesession,hostname)
        city = city.decode('iso-8859-1').encode('utf8')
        region_name = region_name.decode('iso-8859-1').encode('utf8')
        time_zone = time_zone.decode('iso-8859-1').encode('utf8')
        postal_code = postal_code.decode('iso-8859-1').encode('utf8')
        country_code = country_code.decode('iso-8859-1').encode('utf8')
        country_name = country_name.decode('iso-8859-1').encode('utf8')
        try:
            nb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        result=[x for x in nb][0][0]

        logging.getLogger().info("nb %d"%result)
        if result == 0 :
            print "creation nouvelle users"
            try:
                new_user = Users()
                new_user.namesession = namesession
                new_user.hostname = hostname
                new_user.city = city
                new_user.region_name = region_name
                new_user.time_zone = time_zone
                new_user.longitude = longitude
                new_user.latitude = latitude
                new_user.postal_code = postal_code
                new_user.country_code = country_code
                new_user.country_name = country_name
                session.add(new_user)
                session.commit()
                session.flush()
                return new_user.id
            except Exception, e:
                logging.getLogger().error(str(e))
                return -1
        else:
            try:
                sql = """UPDATE `xmppmaster`.`users` SET `city`='%s', `region_name`='%s',`time_zone`='%s',
                `longitude`='%s',`latitude`='%s', `postal_code`='%s',`country_code`='%s', `country_name`='%s'
                WHERE `xmppmaster`.`users`.`hostname`='%s';"""%(city,region_name,time_zone,longitude,latitude,postal_code,country_code,country_name,hostname)
                session.execute(sql)
                session.commit()
                session.flush()
                sql ="select id from `xmppmaster`.`users` WHERE `xmppmaster`.`users`.`hostname`='%s';"%hostname
                result = session.execute(sql)
                result = [x for x in result][0]
                session.commit()
                session.flush()
                return result
            except Exception, e:
                logging.getLogger().error(str(e))
        return -1


    @DatabaseHelper._session
    def algoregleuser(self, session, username, classutilMachine = "private", regle = 1, actif=1):
        #-- type user regles_id` = 1
        #select `relaisserver`.`id` from `relaisserver` inner join `has_relaisserverregles` ON  `relaisserver`.`id` = `has_relaisserverregles`.`relaisserver_id` 
        #where
        #`has_relaisserverregles`.`regles_id` = 1 and -- type user regles_id` = 1
        #`has_relaisserverregles`.`sujet` = users_machine and -- user de la machine
        #`relaisserver`.`actif` = 1 and
        #`relaisserver`.`classutil` = classutildela machine; -- seulement si classutil dela machine est private
        if classutilMachine == "private":
            sql = """select `relaisserver`.`id` 
            from `relaisserver` 
                inner join 
                    `has_relaisserverregles` ON  `relaisserver`.`id` = `has_relaisserverregles`.`relaisserver_id` 
            where
                `has_relaisserverregles`.`regles_id` = %d 
                    AND `has_relaisserverregles`.`sujet` = '%s' 
                    AND `relaisserver`.`actif` = %d 
                    AND `relaisserver`.`classutil` = '%s' 
            limit 1;"""%(regle, username, actif, classutilMachine)
        else:
            sql = """select `relaisserver`.`id` 
            from `relaisserver` 
                inner join 
                    `has_relaisserverregles` ON  `relaisserver`.`id` = `has_relaisserverregles`.`relaisserver_id` 
            where
                `has_relaisserverregles`.`regles_id` = %d 
                    AND `has_relaisserverregles`.`sujet` = '%s' 
                    AND `relaisserver`.`actif` = %d 
            limit 1;"""%(regle, username, actif)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def algoreglehostname(self, session, hostname, classutilMachine = "private", regle = 2, actif=1):
        """Recherche server relais impose pour un hostname"""
        if classutilMachine == "private":
            sql = """select `relaisserver`.`id` 
            from `relaisserver` 
                inner join 
                    `has_relaisserverregles` ON  `relaisserver`.`id` = `has_relaisserverregles`.`relaisserver_id` 
            where
                `has_relaisserverregles`.`regles_id` = %d 
                    AND `has_relaisserverregles`.`sujet` = '%s' 
                    AND `relaisserver`.`actif` = %d 
                    AND `relaisserver`.`classutil` = '%s'
            limit 1;"""%(regle, hostname, actif, classutilMachine)
        else:
            sql = """select `relaisserver`.`id` 
            from `relaisserver` 
                inner join 
                    `has_relaisserverregles` ON  `relaisserver`.`id` = `has_relaisserverregles`.`relaisserver_id` 
            where
                `has_relaisserverregles`.`regles_id` = %d 
                    AND `has_relaisserverregles`.`sujet` = '%s' 
                    AND `relaisserver`.`actif` = %d 
            limit 1;"""%(regle, hostname, actif)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def algoreglesubnet(self, session, subnetmachine, classutilMachine = "private",  actif=1):
        """recherche server relais avec meme reseau"""
        if classutilMachine == "private":
            sql = """select `relaisserver`.`id` 
            from `relaisserver`
            where
                        `relaisserver`.`actif` = %d 
                    AND `relaisserver`.`subnet` ='%s'
                    AND `relaisserver`.`classutil` = '%s'
            limit 1;"""%(actif, subnetmachine, classutilMachine)
        else:
            sql = """select `relaisserver`.`id` 
            from `relaisserver`
            where
                        `relaisserver`.`actif` = %d 
                    AND `relaisserver`.`subnet` ='%s'
            limit 1;"""%(actif, subnetmachine)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def IpAndPortConnectionFromServerRelais(self, session, id):
        """ return ip et port serveur relais pour la connection"""
        #sql = """SELECT 
                    #ipserver, port, jid
                 #FROM
                    #xmppmaster.relaisserver
                 #WHERE
                    #id = %s;"""%id;
        sql = """SELECT 
                    ipconnection, port, jid, urlguacamole
                 FROM
                    xmppmaster.relaisserver
                 WHERE
                    id = %s;"""%id;
        print sql
        result = session.execute(sql)
        session.commit()
        session.flush()
        return list( [x for x in result][0])

    @DatabaseHelper._session
    def jidserverrelaisforip(self, session, ip ):
        """ return ip et port serveur relais pour la connection"""
        #sql ="""SELECT 
                    #jid
                #FROM
                    #xmppmaster.relaisserver
                #WHERE
                    #ipserver = '%s';"""%ip;
        sql ="""SELECT 
                    jid
                FROM
                    xmppmaster.relaisserver
                WHERE
                    ipconnection = '%s';"""%ip;
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1
        

    @DatabaseHelper._session
    def IdlonglatServerRelais(self, session, classutilMachine = "private",  actif=1):
        """ return ip et long et lat serveurs relais"""
        if classutilMachine == "private":
            sql = """SELECT 
                        id, longitude, latitude
                    FROM
                        xmppmaster.relaisserver
                    WHERE
                            `relaisserver`.`actif` = %d 
                        AND `relaisserver`.`classutil` = '%s';"""%(actif, classutilMachine)
        else:
            sql = """SELECT 
                        id,longitude,latitude
                    FROM
                        xmppmaster.relaisserver
                    WHERE
                            `relaisserver`.`actif` = %d;"""%(actif)
        print sql
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]


    #@DatabaseHelper._session
    #def algoregledefault(self, session, subnetmachine, classutilMachine = "private",  actif=1):
        #pass

    #@DatabaseHelper._session
    #def algoreglegeo(self, session, subnetmachine, classutilMachine = "private",  actif=1):
        #pass

    @DatabaseHelper._session
    def Orderregles(self, session):
        sql = """SELECT 
                    *
                FROM
                    xmppmaster.regles
                ORDER BY level;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def hasmachineusers(self, session, useradd, idmachine):
        sql = """INSERT 
                INTO `xmppmaster`.`has_machinesusers` (`users_id`, `machines_id`) 
                VALUES ('%s', '%s');"""%(useradd,idmachine)
        session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._session
    def clearMachine(self, session):
        session.execute('TRUNCATE TABLE xmppmaster.machines;')
        session.execute('TRUNCATE TABLE xmppmaster.network;')
        session.execute('TRUNCATE TABLE xmppmaster.has_machinesusers;')
        session.commit()
        session.flush()

    @DatabaseHelper._session
    def listMacAdressforMachine(self, session, id_machine):
        try:
            #sql = "SELECT group_concat(concat('%s',mac,'%s')) as listmac FROM xmppmaster.network where machines_id = '%s'  limit 1;"%('"','"',id_machine)
            sql = """SELECT 
                        GROUP_CONCAT(CONCAT(mac)) AS listmac
                    FROM
                        xmppmaster.network
                    WHERE
                        machines_id = '%s'
                    LIMIT 1;"""%(id_machine)
            #logging.getLogger().info(" sql %s"%sql)
            listMacAdress = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        result=[x for x in listMacAdress][0]
        #logging.getLogger().info(" result %s"%result[0])
        return result

    @DatabaseHelper._session
    def updateMachineidinventory(self, session, id_machineinventory, idmachine):
        try:
            sql = """UPDATE `machines` 
                    SET 
                        `uuid_inventorymachine` = '%s'
                    WHERE
                        `id` = '%s';"""%(id_machineinventory,idmachine)
            #logging.getLogger().debug("sql %s"%sql)
            updatedb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return updatedb

    @DatabaseHelper._session
    def getPresenceuuid(self, session, uuid):
        sql = """SELECT 
                    COUNT(*) AS 'nb'
                FROM
                    `xmppmaster`.`machines`
                WHERE
                    `xmppmaster`.`machines`.`uuid_inventorymachine` = '%s';"""%(uuid)
        #logging.getLogger().debug("sql :%s"%(sql))
        presence = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in presence]
        if ret[0] == 0 :
            return False
        return True

    @DatabaseHelper._session
    def delPresenceMachine(self, session, jid):
        print "delPresenceMachine" 
        result = ['-1']
        try:
            sql = """SELECT 
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.jid = '%s';"""%jid
            #logging.getLogger().debug(" sql %s"%sql)
            id = session.execute(sql)
            session.commit()
            session.flush()
            result=[x for x in id][0]
            sql  = """DELETE FROM `xmppmaster`.`machines` 
                    WHERE
                        `xmppmaster`.`machines`.`id` = '%s';"""%result[0]

            sql1 = """DELETE FROM `xmppmaster`.`network` 
                    WHERE
                        `network`.`machines_id` = '%s';"""%result[0]

            sql3 = """DELETE FROM `xmppmaster`.`has_machinesusers` 
                    WHERE
                        `has_machinesusers`.`machines_id` = '%s';"""%result[0]
            print "*******************************"
            print "%s"%result
            if result[2] == "relaisserver":
                sql2 = """UPDATE `xmppmaster`.`relaisserver` 
                            SET 
                                `actif` = '0'
                            WHERE
                                `xmppmaster`.`relaisserver`.`nameserver` = '%s';"""%result[1]
                supp2 = session.execute(sql2)
            supp  = session.execute(sql)
            supp1 = session.execute(sql1)
            supp3 = session.execute(sql3)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return result

    @DatabaseHelper._session
    def getGuacamoleRelaisServerMachineUuid(self, session, uuid):
        sql = """SELECT 
                    *
                FROM
                    xmppmaster.machines
                        INNER JOIN
                    xmppmaster.relaisserver ON xmppmaster.relaisserver.subnet = xmppmaster.machines.subnetxmpp
                WHERE
                    xmppmaster.machines.uuid_inventorymachine = '%s';"""%uuid  ;
        serverrelais = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m for m in serverrelais]
        return ret
