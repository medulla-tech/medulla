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
from pulse2.database.xmppmaster.schema import Network, Machines, RelaisServer, Base
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
    def addPresenceMachine(self, session, jid,plateform,hostname,archi,uuid_inventorymachine,ip_xmpp,subnetxmpp,macadress,agenttype):
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
            session.add(new_machine)
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
    def addServerRelais(self, session, urlguacamole, subnet, nameserver, ipserver, mask, jid):
        sql = "SELECT count(*) as nb FROM xmppmaster.relaisserver where `relaisserver`.`nameserver`='%s';"%nameserver
        #logging.getLogger().info(sql)
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
                new_relaisserver.ipserver = ipserver
                new_relaisserver.mask = mask
                new_relaisserver.jid = jid
                session.add(new_relaisserver)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))

    @DatabaseHelper._session
    def clearMachine(self, session):
        session.execute('TRUNCATE TABLE xmppmaster.machines;')
        session.execute('TRUNCATE TABLE xmppmaster.network;')
        session.commit()
        session.flush()

    @DatabaseHelper._session
    def listMacAdressforMachine(self, session, id_machine):
        try:
            #sql = "SELECT group_concat(concat('%s',mac,'%s')) as listmac FROM xmppmaster.network where machines_id = '%s'  limit 1;"%('"','"',id_machine)
            sql = "SELECT group_concat(concat(mac)) as listmac FROM xmppmaster.network where machines_id = '%s'  limit 1;"%(id_machine)
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
            sql = "UPDATE `machines` SET `uuid_inventorymachine`='%s' WHERE `id`='%s';"%(id_machineinventory,idmachine)
            #logging.getLogger().debug("sql %s"%sql)
            updatedb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))    
        return updatedb

    @DatabaseHelper._session
    def getPresenceuuid(self, session, uuid):
        sql = "SELECT COUNT(*) as 'nb' FROM `xmppmaster`.`machines` where `xmppmaster`.`machines`.`uuid_inventorymachine` = '%s';"%(uuid)
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
        result = ['-1']
        try:
            sql = "SELECT id FROM xmppmaster.machines where xmppmaster.machines.jid='%s';"%jid
            #logging.getLogger().debug(" sql %s"%sql)
            id = session.execute(sql)
            session.commit()
            session.flush()
            result=[x for x in id][0]
            #logging.getLogger().info(" result %s"%result[0])
            sql = "DELETE FROM `xmppmaster`.`machines` WHERE `xmppmaster`.`machines`.`id`='%s';"%result[0]
            sql1 = "DELETE FROM `xmppmaster`.`network` WHERE `network`.`machines_id`='%s';"%result[0]
            supp  = session.execute(sql)
            supp1 = session.execute(sql1)
            #logging.getLogger().debug(" sql %s"%sql)
            #logging.getLogger().debug(" sql %s"%sql1)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return result

    @DatabaseHelper._session
    def getGuacamoleRelaisServerMachineUuid(self, session, uuid):
        sql="SELECT * FROM xmppmaster.machines INNER JOIN xmppmaster.relaisserver ON xmppmaster.relaisserver.subnet = xmppmaster.machines.subnetxmpp where xmppmaster.machines.uuid_inventorymachine = '%s';"%uuid  ;
        serverrelais = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m for m in serverrelais]
        return ret
