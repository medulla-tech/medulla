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
from sqlalchemy import create_engine, MetaData, select, func, and_
from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
from sqlalchemy.exc import DBAPIError

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.xmppmaster.schema import Network, Machines, RelayServer, Users, Regles, Has_machinesusers,Has_relayserverrules,Has_guacamole, Base, UserLog, Deploy,Has_login_command,Logs
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
    def logtext(self, session, text, sessionname='' , type = "noset",priority = 0, who = ''):
        try:
            new_log = Logs()
            new_log.text = text
            new_log.sessionname = sessionname
            new_log.type = type
            new_log.priority = priority
            new_log.who = who
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))


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
    def addPresenceMachine(self, session, jid, platform, hostname, archi,
                           uuid_inventorymachine, ip_xmpp, subnetxmpp, macaddress, agenttype, classutil='private', urlguacamole ="", groupdeploy =""):
        #print "%s %s %s %s %s %s %s %s %s %s"%(jid, platform, hostname, archi, uuid_inventorymachine, ip_xmpp, subnetxmpp, macaddress, agenttype, classutil)
        try:
            new_machine = Machines()
            new_machine.jid = jid
            new_machine.platform = platform
            new_machine.hostname = hostname
            new_machine.archi = archi
            new_machine.uuid_inventorymachine = uuid_inventorymachine
            new_machine.ip_xmpp = ip_xmpp
            new_machine.subnetxmpp = subnetxmpp
            new_machine.macaddress = macaddress
            new_machine.agenttype = agenttype
            new_machine.classutil = classutil
            new_machine.urlguacamole = urlguacamole
            new_machine.groupdeploy = groupdeploy
            session.add(new_machine)
            session.commit()
            session.flush()
            if agenttype == "relayserver":
                sql = "UPDATE `xmppmaster`.`relayserver` SET `enabled`='1' WHERE `xmppmaster`.`relayserver`.`nameserver`='%s'"%hostname;
                session.execute(sql)
                session.commit()
                session.flush()
        except Exception, e:
            #logging.getLogger().error("addPresenceMachine %s" % jid)
            logging.getLogger().error(str(e))
            return -1
        return new_machine.id
    
    @DatabaseHelper._session
    def loginbycommand(self, session,idcommand):
        sql = """SELECT 
                    login
                FROM
                    xmppmaster.has_login_command
                WHERE
                    command = %s
                    LIMIT 1 ;"""%idcommand
        result = session.execute(sql)
        session.commit()
        session.flush()
        result = [x for x in result][0]
        print result
        return result

    @DatabaseHelper._session
    def adddeploy(self, session, idcommand,  jidmachine, jidrelay,  host, inventoryuuid,
                           uuidpackage, state, sessionid, user="", deploycol=""):
        #print "%s %s %s %s %s %s %s %s %s %s"%(jid, platform, hostname, archi, uuid_inventorymachine, ip_xmpp, subnetxmpp, macaddress, agenttype, classutil)
        #recupere login command
        login = self.loginbycommand(idcommand)
        try:
            new_deploy = Deploy()
            new_deploy.jidmachine = jidmachine
            new_deploy.jid_relay = jidrelay
            new_deploy.host = host
            new_deploy.inventoryuuid = inventoryuuid
            new_deploy.pathpackage =uuidpackage
            new_deploy.state = state
            new_deploy.sessionid = sessionid
            new_deploy.user = user
            new_deploy.deploycol = deploycol
            new_deploy.command = idcommand
            new_deploy.login = login
            session.add(new_deploy)
            session.commit()
            session.flush()
        except Exception, e:
            print str(e)
            logging.getLogger().error(str(e))
        return new_deploy.id

    @DatabaseHelper._session
    def getdeployfromcommandid(self, session, command_id, uuid):
        if (uuid == "UUID_NONE"):
            relayserver = session.query(Deploy).filter(and_(Deploy.command == command_id,Deploy.result.isnot(None)))
        else:
            relayserver = session.query(Deploy).filter(and_( Deploy.inventoryuuid == uuid ,Deploy.command == command_id, Deploy.result.isnot(None)))
        print relayserver 
        relayserver = relayserver.all()
        session.commit()
        session.flush()
        ret={}
        ret['len']= len(relayserver)
        arraylist=[]
        for t in relayserver:
            obj={}
            obj['pathpackage']=t.pathpackage
            obj['jid_relay']=t.jid_relay
            obj['inventoryuuid']=t.inventoryuuid
            obj['jidmachine']=t.jidmachine
            obj['state']=t.state
            obj['sessionid']=t.sessionid
            obj['start']=t.start
            if t.result is None:
                obj['result']=""
            else:
                obj['result']=t.result
            obj['host']=t.host
            obj['user']=t.user
            obj['deploycol']=t.deploycol
            obj['login']=str(t.login)
            obj['command']=t.command
            arraylist.append(obj)
        ret['objectdeploy']= arraylist
        return ret

    @DatabaseHelper._session
    def getlinelogssession(self, session, sessionnamexmpp):
        log = session.query(Logs).filter(and_( Logs.sessionname == sessionnamexmpp, Logs.type == 'deploy')).order_by(Logs.id).all()
        session.commit()
        session.flush()
        ret={}
        ret['len']= len(log)
        arraylist=[]
        for t in log:
            obj={}
            obj['type']=t.type
            obj['date']=t.date
            obj['text']=t.text
            obj['sessionname']=t.sessionname
            obj['priority']=t.priority
            obj['who']=t.who
            arraylist.append(obj)
        ret['log']= arraylist
        return ret

    @DatabaseHelper._session
    def addlogincommand(self, session, login, commandid):
        try:
            new_logincommand = Has_login_command()
            new_logincommand.login = login
            new_logincommand.command = commandid
            session.add(new_logincommand)
            session.commit()
            session.flush()
        except Exception, e:
            print str(e)
            logging.getLogger().error(str(e))
        return new_logincommand.id

    @DatabaseHelper._session
    def deploylog(self,session,nblastline):
        """ return les machines en fonction du RS """
        sql = """SELECT 
                    *
                FROM
                    xmppmaster.deploy
                ORDER BY id DESC
                LIMIT %s;"""%nblastline
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def updatedeploystate(self, session, sessionid, state):
        try:
            session.query(Deploy).filter(Deploy.sessionid == sessionid).\
                    update({Deploy.state: state})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._session
    def addPresenceNetwork(self, session, macaddress, ipaddress, broadcast, gateway, mask, mac, id_machine):
        try:
            new_network = Network()
            new_network.macaddress=macaddress
            new_network.ipaddress=ipaddress
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
    def addServerRelay(self, session,
                        urlguacamole,
                        subnet,
                        nameserver,
                        groupdeploy,
                        ipserver,
                        ipconnection,
                        portconnection,
                        port, mask, jid, longitude="", latitude="", enabled=False, classutil="private"):
        sql = "SELECT count(*) as nb FROM xmppmaster.relayserver where `relayserver`.`nameserver`='%s';"%nameserver
        nb = session.execute(sql)
        session.commit()
        session.flush()
        result=[x for x in nb][0][0]
        if result == 0 :
            try:
                new_relayserver = RelayServer()
                new_relayserver.urlguacamole = urlguacamole
                new_relayserver.subnet = subnet
                new_relayserver.nameserver = nameserver
                new_relayserver.groupdeploy = groupdeploy
                new_relayserver.ipserver = ipserver
                new_relayserver.port = port
                new_relayserver.mask = mask
                new_relayserver.jid = jid
                new_relayserver.ipconnection = ipconnection
                new_relayserver.portconnection = portconnection
                new_relayserver.longitude = longitude
                new_relayserver.latitude = latitude
                new_relayserver.enabled = enabled
                new_relayserver.classutil = classutil
                session.add(new_relayserver)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))
        else:
            try:
                sql = "UPDATE `xmppmaster`.`relayserver` SET `enabled`=%s, `classutil`='%s' WHERE `xmppmaster`.`relayserver`.`nameserver`='%s';"%(enabled,classutil,nameserver)
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
        if result == 0 :
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
                session.query(Users).filter(Users.hostname == hostname).\
                    update({Users.city: city,
                            Users.region_name:region_name,
                            Users.time_zone:time_zone,
                            Users.longitude:longitude,
                            Users.latitude:latitude,
                            Users.postal_code:postal_code,
                            Users.country_code:country_code,
                            Users.country_name:country_name
                            })
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
    def showmachinegrouprelayserver(self,session):
        """ return les machines en fonction du RS """
        sql = """SELECT 
                `jid`, `agenttype`, `platform`, `groupdeploy`, `hostname`, `uuid_inventorymachine`, `ip_xmpp`, `subnetxmpp`
            FROM
                xmppmaster.machines
            order BY `groupdeploy` ASC, `agenttype` DESC;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def listjidRSdeploy(self,session):
        """ return les RS pour le deploiement """
        sql = """SELECT 
                    groupdeploy
                FROM
                    xmppmaster.machines
                WHERE
                    machines.agenttype = 'relayserver';"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def listmachinesfromRSdeploy( self, session, groupdeploy ):
        """ return les machine suivie par un RS """
        sql = """SELECT 
                    *
                FROM
                    xmppmaster.machines
                WHERE
                    machines.agenttype = 'machine'
                        AND machines.groupdeploy = '%s';"""%groupdeploy
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def listmachinesfromdeploy( self, session, groupdeploy ):
        """ return toutes les machines pour un deploy """
        sql = """SELECT 
                        *
                    FROM
                        xmppmaster.machines
                    WHERE
                    machines.groupdeploy = '%s'
                    order BY  `agenttype` DESC;"""%groupdeploy
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def ipfromjid(self, session, jid):
        """ return ip xmpp for JID """
        sql = """SELECT 
                    ip_xmpp
                FROM
                    xmppmaster.machines
                WHERE
                    jid LIKE ('%s%%')
                                LIMIT 1;"""%jid
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except:
            return -1

    @DatabaseHelper._session
    def algoruleuser(self, session, username, classutilMachine = "private", rule = 1, enabled=1):
        #-- type user rules_id` = 1
        #select `relayserver`.`id` from `relayserver` inner join `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id` 
        #where
        #`has_relayserverrules`.`rules_id` = 1 and -- type user rules_id` = 1
        #`has_relayserverrules`.`subject` = users_machine and -- user de la machine
        #`relayserver`.`enabled` = 1 and
        #`relayserver`.`classutil` = classutildela machine; -- seulement si classutil dela machine est private
        if classutilMachine == "private":
            sql = """select `relayserver`.`id` 
            from `relayserver` 
                inner join 
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id` 
            where
                `has_relayserverrules`.`rules_id` = %d 
                    AND `has_relayserverrules`.`subject` = '%s' 
                    AND `relayserver`.`enabled` = %d 
                    AND `relayserver`.`classutil` = '%s' 
            limit 1;"""%(rule, username, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id` 
            from `relayserver` 
                inner join 
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id` 
            where
                `has_relayserverrules`.`rules_id` = %d 
                    AND `has_relayserverrules`.`subject` = '%s' 
                    AND `relayserver`.`enabled` = %d 
            limit 1;"""%(rule, username, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def algorulehostname(self, session, hostname, classutilMachine = "private", rule = 2, enabled=1):
        """Recherche server relay impose pour un hostname"""
        if classutilMachine == "private":
            sql = """select `relayserver`.`id` 
            from `relayserver` 
                inner join 
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id` 
            where
                `has_relayserverrules`.`rules_id` = %d 
                    AND `has_relayserverrules`.`subject` = '%s' 
                    AND `relayserver`.`enabled` = %d 
                    AND `relayserver`.`classutil` = '%s'
            limit 1;"""%(rule, hostname, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id` 
            from `relayserver` 
                inner join 
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id` 
            where
                `has_relayserverrules`.`rules_id` = %d 
                    AND `has_relayserverrules`.`subject` = '%s' 
                    AND `relayserver`.`enabled` = %d 
            limit 1;"""%(rule, hostname, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def algorulesubnet(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
        """recherche server relay avec meme reseau"""
        if classutilMachine == "private":
            sql = """select `relayserver`.`id` 
            from `relayserver`
            where
                        `relayserver`.`enabled` = %d 
                    AND `relayserver`.`subnet` ='%s'
                    AND `relayserver`.`classutil` = '%s'
            limit 1;"""%(enabled, subnetmachine, classutilMachine)
        else:
            sql = """select `relayserver`.`id` 
            from `relayserver`
            where
                        `relayserver`.`enabled` = %d 
                    AND `relayserver`.`subnet` ='%s'
            limit 1;"""%(enabled, subnetmachine)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def IpAndPortConnectionFromServerRelay(self, session, id):
        """ return ip et port server relay for connection"""
        sql = """SELECT 
                    ipconnection, port, jid, urlguacamole
                 FROM
                    xmppmaster.relayserver
                 WHERE
                    id = %s;"""%id;
        result = session.execute(sql)
        session.commit()
        session.flush()
        return list( [x for x in result][0])

    @DatabaseHelper._session
    def jidrelayserverforip(self, session, ip ):
        """ return jid server relay for connection"""
        sql ="""SELECT 
                    jid
                FROM
                    xmppmaster.relayserver
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
    def IdlonglatServerRelay(self, session, classutilMachine = "private",  enabled=1):
        """ return long and lat server relay"""
        if classutilMachine == "private":
            sql = """SELECT 
                        id, longitude, latitude
                    FROM
                        xmppmaster.relayserver
                    WHERE
                            `relayserver`.`enabled` = %d 
                        AND `relayserver`.`classutil` = '%s';"""%(enabled, classutilMachine)
        else:
            sql = """SELECT 
                        id,longitude,latitude
                    FROM
                        xmppmaster.relayserver
                    WHERE
                            `relayserver`.`enabled` = %d;"""%(enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]


    #@DatabaseHelper._session
    #def algoruledefault(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
        #pass

    #@DatabaseHelper._session
    #def algorulegeo(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
        #pass

    @DatabaseHelper._session
    def Orderrules(self, session):
        sql = """SELECT 
                    *
                FROM
                    xmppmaster.rules
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
    def addguacamoleidforiventoryid(self, session, idinventory, idguacamole):
        try:
            hasguacamole = Has_guacamole()
            hasguacamole.idguacamole=idguacamole
            hasguacamole.idinventory=idinventory
            session.add(hasguacamole)
            session.commit()
            session.flush()
        except Exception, e:
            #logging.getLogger().error("addPresenceNetwork : %s " % new_network)
            logging.getLogger().error(str(e))

    @DatabaseHelper._session
    def addlistguacamoleidforiventoryid(self, session, idinventory, connection):
        # objet connection: {u'VNC': 60, u'RDP': 58, u'SSH': 59}}
        sql  = """DELETE FROM `xmppmaster`.`has_guacamole`
                    WHERE
                        `xmppmaster`.`has_guacamole`.`idinventory` = '%s';"""%idinventory
        result = session.execute(sql)
        session.commit()
        session.flush()

        for idguacamole in connection:
            try:
                hasguacamole = Has_guacamole()
                hasguacamole.idguacamole=connection[idguacamole]
                hasguacamole.idinventory=idinventory
                hasguacamole.protocol=idguacamole
                session.add(hasguacamole)
                session.commit()
                session.flush()
            except Exception, e:
                #logging.getLogger().error("addPresenceNetwork : %s " % new_network)
                logging.getLogger().error(str(e))

    @DatabaseHelper._session
    def listserverrelay(self, session):
        sql = """SELECT 
                    jid
                FROM
                    xmppmaster.relayserver;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._session
    def listmachines(self, session):
        sql = """SELECT 
                    jid
                FROM
                    xmppmaster.machines;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

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
    def getstepdeployinsession(self, session, sessiondeploy):
        sql = """
                SELECT 
            date, text
        FROM
            xmppmaster.logs
        WHERE
            type = 'deploy'
                AND sessionname = '%s'
        ORDER BY id;"""%(sessiondeploy)
       
    
        step = session.execute(sql)
        session.commit()
        session.flush()
        step
        #return [x for x in step]
        try:
            a=[]
            for t in step:
                a.append ({'date':t[0],'text':t[1] })
            return a
        except:
            return []

    @DatabaseHelper._session
    def getListPresenceMachine(self, session):
        sql = """SELECT 
                    jid, agenttype, hostname
                 FROM
                    xmppmaster.machines;"""
        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append({'jid':t[0],'type': t[1], 'hostname':t[2]})
                logging.getLogger().debug("t %s"%t)
            #a = {"jid": x, for x, y ,z in presencelist}
            logging.getLogger().debug("a %s"%a)
            return a
        except:
            return -1

    @DatabaseHelper._session
    def delPresenceMachine(self, session, jid):
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
            if result[2] == "relayserver":
                sql2 = """UPDATE `xmppmaster`.`relayserver` 
                            SET 
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""%result[1]
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
    def getGuacamoleRelayServerMachineUuid(self, session, uuid):
        relayserver = session.query(Machines).filter(Machines.uuid_inventorymachine == uuid)
        session.commit()
        session.flush()
        ret=[m for m in relayserver]
        print ret[0]
        return ret[0]

    @DatabaseHelper._session
    def getGuacamoleidforUuid(self, session, uuid):
        ret=session.query(Has_guacamole.idguacamole,Has_guacamole.protocol).filter(Has_guacamole.idinventory == uuid.replace('UUID','')).all()
        session.commit()
        session.flush()
        if ret:
            return [(m[1],m[0]) for m in ret]
        else:
            return []
    

    @DatabaseHelper._session
    def getPresencejid(self, session, jid):
        sql = """SELECT COUNT(jid) AS nb
            FROM
                 xmppmaster.machines
             WHERE
              jid LIKE ('%s%%');"""%(jid)
        presencejid = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in presencejid]
        if ret[0] == 0 :
            return False
        return True
