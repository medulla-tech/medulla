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
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct
from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
from sqlalchemy.exc import DBAPIError
from datetime import date, datetime, timedelta
# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.xmppmaster.schema import Network, Machines, RelayServer, Users, Regles, Has_machinesusers,\
    Has_relayserverrules, Has_guacamole, Base, UserLog, Deploy, Has_login_command, Logs, ParametersDeploy, \
    Organization, Packages_list, Qa_custom_command,\
    Cluster_ars, Has_cluster_ars,\
    Command_action, Command_qa,\
    Organization_ad, Cluster_resources
# Imported last
import logging
import json
import time
#topology
import os, pwd
import traceback
import sys
import re

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
        self.db = create_engine(self.makeConnectionPath(),
                                pool_recycle = self.config.dbpoolrecycle,
                                pool_size = self.config.dbpoolsize,
                                pool_timeout = self.config.dbpooltimeout)
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
    # xmppmaster FUNCTIONS synch syncthing
    # =====================================================================
    @DatabaseHelper._sessionm
    def get_List_jid_ServerRelay_enable(self, session, enabled=1):
        """ return list enable server relay id """
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.relayserver
                WHERE
                        `relayserver`.`enabled` = %d;"""%(enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def getRelayServer(self, session, enable = None ):
        listrelayserver = []
        if enable is not None:
            relayservers = session.query(RelayServer).filter(and_(RelayServer.enabled == enable)).all()
        else:
            relayservers = session.query(RelayServer).all()
        session.commit()
        session.flush()
        try:
            for relayserver in relayservers:
                res = { 'id' : relayserver.id,
                        'urlguacamole': relayserver.urlguacamole,
                        'subnet' : relayserver.subnet,
                        'nameserver' : relayserver.nameserver,
                        'ipserver' : relayserver.ipserver,
                        'ipconnection' : relayserver.ipconnection,
                        'port' : relayserver.port,
                        'portconnection' : relayserver.portconnection,
                        'mask' : relayserver.mask,
                        'jid' : relayserver.jid,
                        'longitude' : relayserver.longitude,
                        'latitude' : relayserver.latitude,
                        'enabled' : relayserver.enabled,
                        'classutil' : relayserver.classutil,
                        'groupdeploy' : relayserver.groupdeploy,
                        'package_server_ip' : relayserver.package_server_ip,
                        'package_server_port' : relayserver.package_server_port,
                        'moderelayserver' : relayserver.moderelayserver
                    }
                listrelayserver.append(res)
            return listrelayserver
        except Exception, e:
            logging.getLogger().error(str(e))
            traceback.print_exc(file=sys.stdout)
            return listrelayserver

    # =====================================================================
    # xmppmaster FUNCTIONS
    # =====================================================================

    @DatabaseHelper._sessionm
    def setlogxmpp( self,
                    session,
                    text,
                    type = "noset",
                    sessionname = '' ,
                    priority = 0,
                    who = '',
                    how = '',
                    why = '',
                    module = '',
                    action = '',
                    touser =  '',
                    fromuser = ''):
        """
            this functions addition a log line in table log xmpp.
        """
        try:
            new_log = Logs()
            new_log.text = text
            new_log.type = type
            new_log.sessionname = sessionname
            new_log.priority = priority
            new_log.who = who
            new_log.how = how
            new_log.why = why
            new_log.module = module
            new_log.action = action
            new_log.touser = touser
            new_log.fromuser = fromuser
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def getQAforMachine(self, session, cmd_id, uuidmachine):
        try:
            command_action = session.query(Command_action).filter(and_( Command_action.command_id == cmd_id, Command_action.target == uuidmachine))
            print command_action
            print cmd_id
            print uuidmachine
            command_action = command_action.all()
            listcommand = []
            for command in command_action:
                action = []
                action.append( command.command_id )
                action.append( str(command.date) )
                action.append( command.session_id )
                action.append( command.typemessage )
                action.append( command.command_result )
                listcommand.append(action)
            return listcommand
        except Exception, e:
            logging.getLogger().error(str(e))
            traceback.print_exc(file=sys.stdout)
            return []

    @DatabaseHelper._sessionm
    def getCommand_action_time(self, session, during_the_last_seconds, start, stop, filter = None):
        try:
            command_qa = session.query(distinct(Command_qa.id).label("id"),
                                       Command_qa.command_name.label("command_name"),
                                       Command_qa.command_login.label("command_login"),
                                       Command_qa.command_os.label("command_os"),
                                       Command_qa.command_start.label("command_start"),
                                       Command_qa.command_grp.label("command_grp"),
                                       Command_qa.command_machine.label("command_machine"),
                                       Command_action.target.label("target")).join(Command_action,
                                                                        Command_qa.id == Command_action.command_id)
            ##si on veut passer par les groupe avant d'aller sur les machine.
            ## command_qa = command_qa.group_by(Command_qa.id)
            command_qa = command_qa.order_by(desc(Command_qa.id))
            if during_the_last_seconds:
                command_qa = command_qa.filter( Command_qa.command_start >= (datetime.now() - timedelta(seconds=during_the_last_seconds)))
            #nb = self.get_count(deploylog)
        #lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]

            nbtotal = self.get_count(command_qa)
            if start != "" and stop != "":
                command_qa = command_qa.offset(int(start)).limit(int(stop)-int(start))
            command_qa = command_qa.all()
            session.commit()
            session.flush()
            ## creation des list pour affichage web organiser par colone
            result_list = []
            command_id_list = []
            command_name_list = []
            command_login_list = []
            command_os_list = []
            command_start_list = []
            command_grp_list = []
            command_machine_list = []
            command_target_list = []
            for command in command_qa:
                command_id_list.append(command.id)
                command_name_list.append(command.command_name)
                command_login_list.append(command.command_login)
                command_os_list.append(command.command_os)
                command_start_list.append(command.command_start)
                command_grp_list.append(command.command_grp)
                command_machine_list.append(command.command_machine)
                command_target_list.append(command.target)
            result_list.append(command_id_list)
            result_list.append(command_name_list)
            result_list.append(command_login_list)
            result_list.append(command_os_list)
            result_list.append(command_start_list)
            result_list.append(command_grp_list)
            result_list.append(command_machine_list)
            result_list.append(command_target_list)
            return {"nbtotal" :nbtotal ,"result" : result_list}
        except Exception, e:
            logging.getLogger().debug("getCommand_action_time error %s->"%str(e))
            traceback.print_exc(file=sys.stdout)
            return {"nbtotal" :0 ,"result" : result_list}


    @DatabaseHelper._sessionm
    def setCommand_qa(self, session, command_name, command_action, command_login, command_grp='', command_machine='', command_os=''):
        try:
            new_Command_qa = Command_qa()
            new_Command_qa.command_name = command_name
            new_Command_qa.command_action = command_action
            new_Command_qa.command_login = command_login
            new_Command_qa.command_grp = command_grp
            new_Command_qa.command_machine = command_machine
            new_Command_qa.command_os = command_os
            session.add(new_Command_qa)
            session.commit()
            session.flush()
            return new_Command_qa.id
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def getCommand_qa_by_cmdid(self, session, cmdid):
        try:
            command_qa = session.query(Command_qa).filter( Command_qa.id == cmdid)
            command_qa = command_qa.first()
            session.commit()
            session.flush()
            return { "id" :  command_qa.id,
                    "command_name": command_qa.command_name,
                    "command_action": command_qa.command_action,
                    "command_login": command_qa.command_login,
                    "command_os": command_qa.command_os,
                    "command_start": str(command_qa.command_start),
                    "command_grp" : command_qa.command_grp,
                    "command_machine" : command_qa.command_machine }
        except Exception, e:
            logging.getLogger().error("getCommand_qa_by_cmdid error %s->"%str(e))
            traceback.print_exc(file=sys.stdout)
            return { "id" :  "",
                    "command_name": "",
                    "command_action": "",
                    "command_login": "",
                    "command_os": "",
                    "command_start": "",
                    "command_grp" : "",
                    "command_machine" : "" }

    @DatabaseHelper._sessionm
    def setCommand_action(self, session, target, command_id, sessionid, command_result="", typemessage="log"):
        try:
            new_Command_action = Command_action()
            new_Command_action.session_id = sessionid
            new_Command_action.command_id = command_id
            new_Command_action.typemessage = typemessage
            new_Command_action.command_result = command_result
            new_Command_action.target = target
            session.add(new_Command_action)
            session.commit()
            session.flush()
            return new_Command_action.id
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
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


    @DatabaseHelper._sessionm
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

    #
    @DatabaseHelper._sessionm
    def getlistpackagefromorganization( self,
                                        session,
                                        organization_name = None,
                                        organization_id   = None):
        """
            return list package an organization
            eg call function example:
            XmppMasterDatabase().getlistpackagefromorganization( organization_id = 1)
            or
            XmppMasterDatabase().getlistpackagefromorganization( organization_name = "name")
        """
         # recupere id organization
        idorganization = -1
        try:
            if organization_id != None:
                try:
                    result_organization = session.query(Organization).filter(Organization.id == organization_id)
                    result_organization = result_organization.one()
                    session.commit()
                    session.flush()
                    idorganization = result_organization.id

                except Exception, e:
                    logging.getLogger().debug("organization id : %s is not exist"%organization_id)
                    return -1
            elif organization_name != None:
                idorganization = self.getIdOrganization(organization_name)
                if idorganization == -1:
                    return {"nb" : 0, "packageslist" : []}
            else:
                return {"nb" : 0, "packageslist" : []}
            result = session.query(Packages_list.id.label("id"),
                                Packages_list.packageuuid.label("packageuuid"),
                                Packages_list.organization_id.label("idorganization"),
                                Organization.name.label("name")).join(Organization,
                                                                        Packages_list.organization_id == Organization.id).\
                                                                filter(Organization.id == idorganization)
            nb = self.get_count(result)
            result = result.all()

            list_result = [{"id" : x.id ,
                            "packageuuid" : x.packageuuid,
                            "idorganization" : x.idorganization,
                            "name" :  x.name }  for x in result]
            return {"nb" : nb, "packageslist" : list_result}
        except Exception, e:
            logging.getLogger().debug("load packages for organization id : %s is error : %s"%(organization_id,str(e)))
            return {"nb" : 0, "packageslist" : []}

    #
    @DatabaseHelper._sessionm
    def getIdOrganization(  self,
                            session,
                            name_organization):
        """
            return id organization suivant le Name
            On error return -1
        """
        try:
            result_organization = session.query(Organization).filter(Organization.name == name_organization)
            result_organization=result_organization.one()
            session.commit()
            session.flush()
            return result_organization.id
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().debug("organization name : %s is not exist"%name_organization)
            return -1





    @DatabaseHelper._sessionm
    def addOrganization( self,
                          session,
                          name_organization):
        """
            creation d'une organization
        """
        id = self.getIdOrganization(name_organization)
        if id == -1:
            organization = Organization()
            organization.name = name_organization
            session.add(organization)
            session.commit()
            session.flush()
            return organization.id
        else :
            return id

    @DatabaseHelper._sessionm
    def delOrganization( self,
                          session,
                          name_organization):
        """
            del organization name
        """
        idorganization = self.getIdOrganization(name_organization)
        if idorganization != -1:
            session.query(Organization).filter(Organization.name == name_organization).delete()
            session.commit()
            session.flush()
            q = session.query(Packages_list).filter(Packages_list.organization_id == idorganization)
            q.delete()
            session.commit()
            session.flush()


    #################Custom Command Quick Action################################
    @DatabaseHelper._sessionm
    def create_Qa_custom_command( self,
                                  session,
                                  user,
                                  osname,
                                  namecmd,
                                  customcmd,
                                  description = ""):
        """
            create Qa_custom_command
        """
        try:
            qa_custom_command = Qa_custom_command()
            qa_custom_command.namecmd = namecmd
            qa_custom_command.user = user
            qa_custom_command.os = osname
            qa_custom_command.customcmd = customcmd
            qa_custom_command.description = description
            session.add(qa_custom_command)
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().debug("qa_custom_command error")
            return -1

    @DatabaseHelper._sessionm
    def updateName_Qa_custom_command( self,
                                     session,
                                     user,
                                     osname,
                                     namecmd,
                                     customcmd,
                                     description):
        """
            update updateName_Qa_custom_command
        """

        try:
            session.query(Qa_custom_command).filter( Qa_custom_command.namecmd == namecmd).\
                                            update( { Qa_custom_command.customcmd : customcmd ,
                                                        Qa_custom_command.description : description,
                                                        Qa_custom_command.os : osname })
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().debug("updateName_Qa_custom_command error %s->"%str(e))
            return -1


    @DatabaseHelper._sessionm
    def delQa_custom_command( self,
                              session,
                              user,
                              osname,
                              namecmd):
        """
            del Qa_custom_command
        """
        try:
            session.query(Qa_custom_command).filter(and_(Qa_custom_command.user == user,
                                                        Qa_custom_command.os == osname,
                                                        Qa_custom_command.namecmd == namecmd)
                                                        ).delete()
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().debug("delQa_custom_command error %s ->"%str(e))
            return -1


    @DatabaseHelper._sessionm
    def get_list_of_users_for_shared_qa(self, session, namecmd):
        """Return the list of users who are owning the specified QA.
        Param:
            str: namecmd the name of the quickaction
        Returns :
            list of users"""

        query = session.query(Qa_custom_command.user).filter( Qa_custom_command.namecmd == namecmd)

        if query is not None:
            user_list = [user[0] for user in query]
            return user_list
        else:
            return []


    @DatabaseHelper._sessionm
    def getlistcommandforuserbyos( self,
                                   session,
                                   user,
                                   osname  = None,
                                   min = None,
                                   max = None,
                                   filt = None,
                                   edit = None):
        ret={ 'len'     : 0,
              'nb'      : 0,
              'limit'   : 0,
              'max'     : 0,
              'min'     : 0,
              'filt'    : '',
              'command' : []}
        try:
            if edit is not None:
                # We are in the edition view
                result = session.query(Qa_custom_command).filter(and_(Qa_custom_command.user == user))
            elif osname is None:
                # We are displaying the list of QAs for use where OS is not defined (view list of QAs)
                result = session.query(Qa_custom_command).filter(or_(Qa_custom_command.user == user, Qa_custom_command.user == 'allusers'))
            else:
                # We are displaying the list of QAs for use where OS is defined (list QAs for specific machine)
                result = session.query(Qa_custom_command).filter(and_(or_(Qa_custom_command.user == user, Qa_custom_command.user == 'allusers'),
                                                                      Qa_custom_command.os == osname))

            total =  self.get_count(result)
            #todo filter
            if filt is not None:
                result = result.filter( or_(  result.namecmd.like('%%%s%%'%(filt)),
                                              result.os.like('%%%s%%'%(filt)),
                                              result.description.like('%%%s%%'%(filt))
                                        )
                        )

            nbfilter =  self.get_count(result)

            if min is not None and max is not None:
                result = result.offset(int(min)).limit(int(max)-int(min))
                ret['limit'] = int(max)-int(min)


            if min : ret['min'] = min
            if max : ret['max'] = max
            if filt : ret['filt'] = filt
            result = result.all()
            session.commit()
            session.flush()
            ret['len'] = total
            ret['nb'] = nbfilter

            arraylist = []
            for t in result:
                obj={}
                obj['user']=t.user
                obj['os']=t.os
                obj['namecmd']=t.namecmd
                obj['customcmd']=t.customcmd
                obj['description']=t.description
                arraylist.append(obj)
            ret['command']= arraylist
            return ret
        except Exception, e:
            logging.getLogger().debug("getlistcommandforuserbyos error %s->"%str(e))
            return ret
################################################

    @DatabaseHelper._sessionm
    def addPackageByOrganization( self,
                                  session,
                                  packageuuid,
                                  organization_name = None,
                                  organization_id   = None ):
        """
        addition reference package in packages table for organization id
            the organization input parameter is either organization name or either organization id
            return -1 if not created
        """
        # recupere id organization
        idorganization = -1
        try:
            if organization_id != None:
                try:
                    result_organization = session.query(Organization).filter(Organization.id == organization_id)
                    result_organization = result_organization.one()
                    session.commit()
                    session.flush()
                    idorganization = result_organization.id
                except Exception, e:
                    logging.getLogger().debug("organization id : %s is not exist"%organization_id)
                    return -1
            elif organization_name != None:
                idorganization = self.getIdOrganization(organization_name)
                if idorganization == -1:
                    return -1
            else:
                return -1

            # addition reference package in listpackages for attribut organization id.
            packageslist = Packages_list()
            packageslist.organization_id = idorganization
            packageslist.packageuuid = packageuuid
            session.add(packageslist)
            session.commit()
            session.flush()
            return packageslist.id
        except Exception, e:
            logging.getLogger().error(str(e))
            logging.getLogger().debug("add Package [%s] for Organization : %s%s is not exist"%( packageuuid,
                                                                                                self.__returntextisNone__(organization_name),
                                                                                                self.__returntextisNone__(organization_id)))
            return -1

    def __returntextisNone__(para, text = ""):
        if para == None:
            return text
        else:
            return para


    ##########gestion packages###############


    ################################
    @DatabaseHelper._sessionm
    def addPresenceMachine(self,
                           session,
                           jid,
                           platform,
                           hostname,
                           archi,
                           uuid_inventorymachine,
                           ip_xmpp,
                           subnetxmpp,
                           macaddress,
                           agenttype,
                           classutil='private',
                           urlguacamole ="",
                           groupdeploy ="",
                           objkeypublic = None,
                           ippublic = None,
                           ad_ou_user = "",
                           ad_ou_machine = "",
                           kiosk_presence = "False",
                           lastuser = ""):
        try:
            new_machine = Machines()
            new_machine.jid = jid
            new_machine.platform = platform
            new_machine.hostname = hostname
            new_machine.archi = archi
            new_machine.uuid_inventorymachine = uuid_inventorymachine
            new_machine.ippublic = ippublic
            new_machine.ip_xmpp = ip_xmpp
            new_machine.subnetxmpp = subnetxmpp
            new_machine.macaddress = macaddress
            new_machine.agenttype = agenttype
            new_machine.classutil = classutil
            new_machine.urlguacamole = urlguacamole
            new_machine.groupdeploy = groupdeploy
            new_machine.picklekeypublic = objkeypublic
            new_machine.ad_ou_user = ad_ou_user
            new_machine.ad_ou_machine = ad_ou_machine
            new_machine.kiosk_presence = kiosk_presence
            new_machine.lastuser = lastuser
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



    @DatabaseHelper._sessionm
    def is_jiduser_organization_ad(self, session, jiduser):
        """ if user exist return True"""
        sql = """SELECT COUNT(jiduser) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s');"""%(jiduser)
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in req]
        if ret[0] == 0 :
            return False
        return True

    def uuidtoid(self, uuid):
        if uuid.strip().lower().startswith("uuid"):
            return uuid[4:]
        else:
            return uuid

    @DatabaseHelper._sessionm
    def is_id_inventory_organization_ad(self, session, id_inventory):
        """ if id_inventory exist return True"""
        sql = """SELECT COUNT(id_inventory) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s');"""%(self.uuidtoid(id_inventory))
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in req]
        if ret[0] == 0 :
            return False
        return True

    @DatabaseHelper._sessionm
    def is_id_inventory_jiduser_organization_ad(self, session, id_inventory, jiduser):
        """ if id_inventory exist return True"""
        sql = """SELECT COUNT(id_inventory) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s')
              and
              id_inventory LIKE ('%s')
              ;"""%(jiduser, self.uuidtoid(id_inventory))
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in req]
        if ret[0] == 0 :
            return False
        return True

    @DatabaseHelper._sessionm
    def getAllOUuser(self, session, ctx, filt = ''):
        """
        @return: all ou defined in the xmpp database
        """
        query = session.query(Organization_ad)
        if filter != '':
            query = query.filter(Organization_ad.ouuser.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getAllOUmachine(self, session, ctx, filt = ''):
        """
        @return: all ou defined in the xmpp database
        """
        query = session.query(Organization_ad)
        if filter != '':
            query = query.filter(Organization_ad.oumachine.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def replace_Organization_ad_id_inventory(self,
                                session,
                                old_id_inventory,
                                new_id_inventory):
        try:
            session.query(Organization_ad).filter( Organization_ad.id_inventory ==  self.uuidtoid(old_id_inventory)).\
                    update({ Organization_ad.id_inventory : self.uuidtoid(new_id_inventory) })
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updateOrganization_ad_id_inventory(self,
                                session,
                                id_inventory,
                                jiduser,
                                ouuser="",
                                oumachine="",
                                hostname="",
                                username=""):
        """
            update Organization_ad table in base xmppmaster
        """
        try:
            session.query(Organization_ad).filter( Organization_ad.id_inventory ==  self.uuidtoid(id_inventory)).\
                    update({ Organization_ad.jiduser : jiduser,
                             Organization_ad.id_inventory : self.uuidtoid(id_inventory),
                             Organization_ad.ouuser : ouuser,
                             Organization_ad.oumachine : oumachine,
                             Organization_ad.hostname : hostname,
                             Organization_ad.username : username})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updateOrganization_ad_jiduser(self,
                                session,
                                id_inventory,
                                jiduser,
                                ouuser="",
                                oumachine="",
                                hostname="",
                                username=""):
        """
            update Organization_ad table in base xmppmaster
        """
        try:
            session.query(Organization_ad).filter( Organization_ad.jiduser ==  jiduser).\
                    update({ Organization_ad.jiduser : jiduser,
                             Organization_ad.id_inventory : self.uuidtoid(id_inventory),
                             Organization_ad.ouuser : ouuser,
                             Organization_ad.oumachine : oumachine,
                             Organization_ad.hostname : hostname,
                             Organization_ad.username : username})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def addOrganization_ad(self,
                           session,
                           id_inventory,
                           jiduser,
                           ouuser="",
                           oumachine="",
                           hostname="",
                           username=""):

        id = self.uuidtoid(id_inventory)
        new_Organization = Organization_ad()
        new_Organization.id_inventory = id
        new_Organization.jiduser = jiduser
        new_Organization.ouuser = ouuser
        new_Organization.oumachine = oumachine
        new_Organization.hostname = hostname
        new_Organization.username = username
        boolexistuserjid = self.is_jiduser_organization_ad(jiduser)
        if not boolexistuserjid:
            # creation de organization for machine jiduser
            if self.is_id_inventory_organization_ad(id):
                #delete for uuid
                self.delOrganization_ad(id_inventory = id)
            try:
                session.add(new_Organization)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error("creation Organisation_ad for jid user %s inventory uuid : %s"% (jiduser, id ))
                logging.getLogger().error("ouuser=%s\noumachine = %s\nhostname=%s\nusername=%s"% (ouuser, oumachine, hostname, username))
                logging.getLogger().error(str(e))
                return -1
            return new_Organization.id_inventory
        else:
            #update fiche
            self.updateOrganization_ad_jiduser(
                                                id_inventory,
                                                jiduser,
                                                ouuser=ouuser,
                                                oumachine=oumachine,
                                                hostname=hostname,
                                                username=username)
        return new_Organization.id_inventory

    @DatabaseHelper._sessionm
    def delOrganization_ad( self,
                            session,
                            id_inventory = None,
                            jiduser = None):
        """
            supp organization ad
        """
        req = session.query(Organization_ad)
        if id_inventory is not None and jiduser is not None:
            req=req.filter(and_(Organization_ad.id_inventory == id_inventory,
                                Organization_ad.jiduser == jiduser))
        elif id_inventory is not None and jiduser is None:
            req=req.filter(Organization_ad.id_inventory == id_inventory)
        elif jiduser is not None and id_inventory is None:
            req=req.filter(Organization_ad.jiduser == jiduser)
        else:
            return False
        try:
            req.delete()
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error("delOrganization_ad : %s "%str(e))
            return False

    @DatabaseHelper._sessionm
    def loginbycommand(self, session, idcommand):
        sql = """SELECT
                    login
                FROM
                    xmppmaster.has_login_command
                WHERE
                    command = %s
                    LIMIT 1 ;"""%idcommand
        try:
            result = session.execute(sql)
            session.commit()
            session.flush()
            #result = [x for x in result]
            ##print result.__dict__
            l = [x[0] for x in result][0]
            return l
        except Exception, e:
            #logging.getLogger().error("addPresenceMachine %s" % jid)
            logging.getLogger().error(str(e))
            return ""

    @DatabaseHelper._sessionm
    def updatedeployinfo(self, session, idcommand):
        """
        this function allows to update the counter of deployments in pause
        """
        try:
            session.query(Has_login_command).filter(and_(Has_login_command.command == idcommand)
                                  ).\
                    update({ Has_login_command.count_deploy_progress : Has_login_command.count_deploy_progress + 1})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            return -1

    def convertTimestampToSQLDateTime(self, value):
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(value))

    def convertSQLDateTimeToTimestamp(self, value):
        return time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S'))

    @DatabaseHelper._sessionm
    def checkstatusdeploy(self, session, idcommand):
        """
        this function is used to determine the state of the deployment when the deployemnet is scheduled and scheduler
        """
        nowtime = datetime.now()
        try:
            result = session.query(Has_login_command).filter(and_(Has_login_command.command == idcommand)).order_by(desc(Has_login_command.id)).limit(1).one()
            deployresult = session.query(Deploy).filter(and_(Deploy.command == idcommand)).order_by(desc(Deploy.id)).limit(1).one()
        except :
            # error case command supp base nunualy
            return 'abandonmentdeploy'
            pass
        if not (deployresult.startcmd <= nowtime and deployresult.endcmd >= nowtime):
            #we are more in the range of deployments.
            #abandonmentdeploy
            for id in  self.sessionidforidcommand(idcommand):
                self.updatedeploystate(id,"DEPLOYMENT ERROR")
            return 'abandonmentdeploy'

        if not (result.start_exec_on_time is None or str(result.start_exec_on_time) == '' or str(result.start_exec_on_time) == "None"):
            #time processing
            if nowtime > result.start_exec_on_time:
                return 'run'
        if not (result.start_exec_on_nb_deploy is None or result.start_exec_on_nb_deploy == ''):
            #nb of deploy processing
            if result.start_exec_on_nb_deploy <= result.count_deploy_progress:
                return 'run'
        for id in  self.sessionidforidcommand(idcommand):
                self.updatedeploystate(id,"DEPLOYMENT DIFFERED")
        return "pause"

    @DatabaseHelper._sessionm
    def update_status_deploy_end(self, session):
        """ this function schedued by xmppmaster """
        #session.query(Deploy).filter( and_( Deploy.endcmd < datenow,
                                            #Deploy.state == "DEPLOYMENT START")
        #).update({ Deploy.state : "DEPLOYMENT ERROR"})
        datenow = datetime.now()
        result = session.query(Deploy).filter( and_( Deploy.endcmd < datenow,
                                            Deploy.state.like('DEPLOYMENT START%%'))
        ).all()
        session.flush()
        session.close()
        for t in result:
            try:
                sql = """UPDATE `xmppmaster`.`deploy` SET `state`='DEPLOYMENT ERROR' WHERE `id`='%s';"""%t.id
                session.execute(sql)
                session.commit()
                session.flush()
            except Exception, e:
                logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def sessionidforidcommand(self, session, idcommand):
        result = session.query(Deploy.sessionid).filter(Deploy.command == idcommand).all()
        if result:
            a= [m[0] for m in result]
            return a
        else:
            return []

    @DatabaseHelper._sessionm
    def datacmddeploy(self, session, idcommand):
        try:
            result = session.query(Has_login_command).filter(and_(Has_login_command.command == idcommand)).order_by(desc(Has_login_command.id)).limit(1).one()
            session.commit()
            session.flush()
            obj={
                    'countnb': 0,
                    'exec' : True
                 }
            if result.login != '':
                obj['login'] = result.login
            obj['idcmd'] = result.command
            if not (result.start_exec_on_time is None or str(result.start_exec_on_time) == '' or str(result.start_exec_on_time) == "None"):
                obj['exectime'] = str(result.start_exec_on_time)
                obj['exec'] = False

            if result.grpid != '':
                obj['grp'] = result.grpid
            if result.nb_machine_for_deploy != '':
                obj['nbtotal'] = result.nb_machine_for_deploy
            if not (result.start_exec_on_nb_deploy is None or result.start_exec_on_nb_deploy == ''):
                obj['consignnb'] = result.start_exec_on_nb_deploy
                obj['exec'] = False
            obj['rebootrequired'] = result.rebootrequired
            obj['shutdownrequired'] = result.shutdownrequired
            obj['limit_rate_ko'] = result.bandwidth
            if result.params_json is not None:
                try:
                    params_json = json.loads(result.params_json)
                    if 'spooling' in params_json:
                        obj['spooling'] = params_json['spooling']
                except Exception, e:
                    logging.getLogger().error("[the avanced parameters from msc] : "+str(e))

            if result.parameters_deploy is not None:
                try:
                    params = str(result.parameters_deploy)
                    if params == '':
                        return obj
                    if not params.startswith('{'):
                        params = '{' + params
                    if not params.endswith('}'):
                        params = params + '}'
                    obj['paramdeploy'] = json.loads(params)
                except Exception, e:
                    logging.getLogger().error("[the avanced parameters must be declared in a json dictionary] : "+ str(e))
            return obj
        except Exception, e:
            logging.getLogger().error("[ obj commandid missing] : " + str(e))
            return {}

    @DatabaseHelper._sessionm
    def adddeploy(self,
                  session,
                  idcommand,
                  jidmachine,
                  jidrelay,
                  host,
                  inventoryuuid,
                  uuidpackage,
                  state,
                  sessionid,
                  user="",
                  login="",
                  title="",
                  group_uuid = None,
                  startcmd = None,
                  endcmd = None,
                  macadress = None
                  ):
        """
        parameters
        startcmd and endcmd  int(timestamp) either str(datetime)
        """
        createcommand = datetime.now()
        try:
            start=int(startcmd)
            end=int(endcmd)
            print start
            print end
            startcmd = datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S")
            endcmd = datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            #logger.error(str(e))
            pass

        #recupere login command
        if login == "":
            login = self.loginbycommand(idcommand)[0]
        try:
            new_deploy = Deploy()
            new_deploy.group_uuid = group_uuid
            new_deploy.jidmachine = jidmachine
            new_deploy.jid_relay = jidrelay
            new_deploy.host = host
            new_deploy.inventoryuuid = inventoryuuid
            new_deploy.pathpackage =uuidpackage
            new_deploy.state = state
            new_deploy.sessionid = sessionid
            new_deploy.user = user
            new_deploy.command = idcommand
            new_deploy.login = login
            new_deploy.startcmd =startcmd
            new_deploy.endcmd = endcmd
            new_deploy.start = createcommand
            new_deploy.macadress = macadress
            new_deploy.title = title
            session.add(new_deploy)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return new_deploy.id


    @DatabaseHelper._sessionm
    def addcluster_resources(self,
                             session,
                             jidmachine,
                             jidrelay,
                             hostname,
                             sessionid,
                             login="",
                             startcmd = None,
                             endcmd = None
                            ):
        """
            add ressource for cluster ressource
        """
        try:
            new_cluster_resources = Cluster_resources()
            new_cluster_resources.jidmachine = jidmachine
            new_cluster_resources.jidrelay = jidrelay
            new_cluster_resources.hostname = hostname
            new_cluster_resources.sessionid = sessionid
            new_cluster_resources.login = login
            new_cluster_resources.startcmd =startcmd
            new_cluster_resources.endcmd = endcmd
            session.add(new_cluster_resources)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return new_cluster_resources.id

    @DatabaseHelper._sessionm
    def getcluster_resources(self, session, jidmachine):
        clusterresources = session.query(Cluster_resources).filter( Cluster_resources.jidmachine == str(jidmachine)).all()
        session.commit()
        session.flush()
        ret = { 'len' : len(clusterresources) }
        arraylist=[]
        for t in clusterresources:
            obj = {}
            obj['jidmachine'] = t.jidmachine
            obj['jidrelay'] = t.jidrelay
            obj['hostname'] = t.hostname
            obj['sessionid'] = t.sessionid
            obj['login'] = t.login
            obj['startcmd'] = t.startcmd
            obj['endcmd'] = t.endcmd
            arraylist.append(obj)
        ret['resource']= arraylist
        self.clean_resources(jidmachine)
        return ret

    @DatabaseHelper._sessionm
    def clean_resources(self, session, jidmachine):
        session.query(Cluster_resources).filter( Cluster_resources.jidmachine == str(jidmachine) ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def delete_resources(self, session, sessionid):
        session.query(Cluster_resources).filter( Cluster_resources.sessionid == str(sessionid) ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def addcluster_resources(self,
                             session,
                             jidmachine,
                             jidrelay,
                             hostname,
                             sessionid,
                             login="",
                             startcmd = None,
                             endcmd = None
                            ):
        """
            add ressource for cluster ressource
        """
        self.clean_resources(jidmachine)
        try:
            new_cluster_resources = Cluster_resources()
            new_cluster_resources.jidmachine = jidmachine
            new_cluster_resources.jidrelay = jidrelay
            new_cluster_resources.hostname = hostname
            new_cluster_resources.sessionid = sessionid
            new_cluster_resources.login = login
            new_cluster_resources.startcmd =startcmd
            new_cluster_resources.endcmd = endcmd
            session.add(new_cluster_resources)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return new_cluster_resources.id

    @DatabaseHelper._sessionm
    def getcluster_resources(self, session, jidmachine):
        clusterresources = session.query(Cluster_resources).filter( Cluster_resources.jidmachine == str(jidmachine)).all()
        session.commit()
        session.flush()
        ret = { 'len' : len(clusterresources) }
        arraylist=[]
        for t in clusterresources:
            obj = {}
            obj['jidmachine'] = t.jidmachine
            obj['jidrelay'] = t.jidrelay
            obj['hostname'] = t.hostname
            obj['sessionid'] = t.sessionid
            obj['login'] = t.login
            obj['startcmd'] = str(t.startcmd)
            obj['endcmd'] = str(t.endcmd)
            arraylist.append(obj)
        ret['resource']= arraylist
        self.clean_resources(jidmachine)
        return ret

    @DatabaseHelper._sessionm
    def clean_resources(self, session, jidmachine):
        session.query(Cluster_resources).filter( Cluster_resources.jidmachine == str(jidmachine) ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def delete_resources(self, session, sessionid):
        session.query(Cluster_resources).filter( Cluster_resources.sessionid == str(sessionid) ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getlinelogswolcmd(self, session, idcommand, uuid):
        log = session.query(Logs).filter(and_( Logs.sessionname == str(idcommand) , Logs.type == 'wol', Logs.who == uuid)).order_by(Logs.id)
        log = log.all()
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

    #jfkjf
    @DatabaseHelper._sessionm
    def get_machine_stop_deploy(self, session, cmdid , inventoryuuid):
        """
            this function return the machines list for  1 command_id and 1 uuid
        """
        query = session.query(Deploy).filter(and_( Deploy.inventoryuuid == inventoryuuid, Deploy.command == cmdid))
        query = query.one()
        session.commit()
        session.flush()
        obj={}
        obj['len'] = 0
        try :
            obj['len'] = 1
            obj['pathpackage'] = query.pathpackage
            obj['jid_relay'] = query.jid_relay
            obj['inventoryuuid'] = query.inventoryuuid
            obj['jidmachine'] = query.jidmachine
            obj['state']= query.state
            obj['sessionid'] = query.sessionid
            obj['start'] = query.start
            obj['host'] = query.host
            obj['user'] = query.user
            obj['login'] = str(query.login)
            obj['command'] = query.command
        except Exception as e:
            logging.getLogger().error(str(e))
        return obj

    @DatabaseHelper._sessionm
    def get_group_stop_deploy(self, session, grpid, cmdid):
        """
            this function return the machines list for 1 group id and 1 command id
        """
        relayserver = session.query(Deploy).filter(and_( Deploy.group_uuid == grpid, Deploy.command == cmdid))
        relayserver = relayserver.all()
        session.commit()
        session.flush()
        ret={}
        ret['len']= len(relayserver)
        arraylist = []
        for t in relayserver:
            obj={}
            obj['pathpackage'] = t.pathpackage
            obj['jid_relay'] = t.jid_relay
            obj['inventoryuuid'] = t.inventoryuuid
            obj['jidmachine'] = t.jidmachine
            obj['state'] = t.state
            obj['sessionid']=t.sessionid
            obj['start'] = t.start
            obj['host'] = t.host
            obj['user'] = t.user
            obj['login'] = str(t.login)
            obj['command'] = t.command
            arraylist.append(obj)
        ret['objectdeploy'] = arraylist
        return ret


    @DatabaseHelper._sessionm
    def getstatdeployfromcommandidstartdate(self, session, command_id, datestart):
        try:
            machinedeploy =session.query(Deploy.state,
                                         func.count(Deploy.state)).\
                                             filter(and_( Deploy.command == command_id,

                                                            Deploy.startcmd == datestart
                                                        )
                                                ).group_by(Deploy.state)
            machinedeploy = machinedeploy.all()
            ret = { 'totalmachinedeploy' : 0,
                    'machinesuccessdeploy' : 0,
                    'machineerrordeploy' : 0,
                    'machineprocessdeploy' : 0,
                    'machineabortdeploy' : 0,
                    'autrestatus' : 0}

            liststatus = { x[0] : x[1] for x in machinedeploy}
            totalmachinedeploy = 0
            for t in liststatus:
                ret['totalmachinedeploy'] += liststatus[t]
                if t == 'DEPLOYMENT SUCCESS':
                    ret['machinesuccessdeploy'] = liststatus[t]
                elif t == 'DEPLOYMENT ERROR':
                    ret['machineerrordeploy'] = liststatus[t]
                elif t == 'DEPLOYMENT START':
                    ret['machineprocessdeploy'] = liststatus[t]
                elif t == 'DEPLOYMENT ABORT':
                    ret['machineabortdeploy'] = liststatus[t]
                else:
                    ret['autrestatus'] = liststatus[t]
            return ret
        except Exception:
            return ret

    @DatabaseHelper._sessionm
    def getdeployfromcommandid(self, session, command_id, uuid):
        if (uuid == "UUID_NONE"):
            relayserver = session.query(Deploy).filter(and_(Deploy.command == command_id))
            #,Deploy.result .isnot(None)
        else:
            relayserver = session.query(Deploy).filter(and_( Deploy.inventoryuuid == uuid, Deploy.command == command_id))
            #, Deploy.result .isnot(None)
        #print relayserver
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
            obj['login']=str(t.login)
            obj['command']=t.command
            arraylist.append(obj)
        ret['objectdeploy']= arraylist
        return ret


    @DatabaseHelper._sessionm
    def getlinelogssession(self, session, sessionnamexmpp):
        log = session.query(Logs).filter(and_( Logs.sessionname == sessionnamexmpp, Logs.type == 'deploy')).order_by(Logs.id)
        log = log.all()
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

    @DatabaseHelper._sessionm
    def addlogincommand(self,
                        session,
                        login,
                        commandid,
                        grpid,
                        nb_machine_in_grp,
                        instructions_nb_machine_for_exec,
                        instructions_datetime_for_exec,
                        parameterspackage,
                        rebootrequired,
                        shutdownrequired,
                        bandwidth,
                        params):
        try:
            new_logincommand = Has_login_command()
            new_logincommand.login = login
            new_logincommand.command = commandid
            new_logincommand.count_deploy_progress = 0
            new_logincommand.bandwidth = int(bandwidth)
            if grpid != "":
                new_logincommand.grpid = grpid
            if instructions_datetime_for_exec != "":
                new_logincommand.start_exec_on_time = instructions_datetime_for_exec
            if nb_machine_in_grp != "":
                new_logincommand.nb_machine_for_deploy = nb_machine_in_grp
            if instructions_nb_machine_for_exec != "":
                new_logincommand.start_exec_on_nb_deploy =instructions_nb_machine_for_exec
            if parameterspackage != "":
                new_logincommand.parameters_deploy = parameterspackage
            if rebootrequired == 0:
                new_logincommand.rebootrequired = False
            else:
                new_logincommand.rebootrequired = True
            if shutdownrequired == 0:
                new_logincommand.shutdownrequired = False
            else:
                new_logincommand.shutdownrequired = True
            if (type(params) is list or type(params) is dict) and len(params) != 0:
                new_logincommand.params_json = json.dumps(params)

            session.add(new_logincommand)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
        return new_logincommand.id

    @DatabaseHelper._sessionm
    def getListPresenceRelay(self, session):
        sql = """SELECT
                    jid, agenttype, hostname
                FROM
                    xmppmaster.machines
                WHERE
                    `machines`.`agenttype` = 'relayserver';"""
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

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def updatedeploystate1(self, session, sessionid, state):
        try:
            session.query(Deploy).filter(and_(Deploy.sessionid == sessionid,
                                              Deploy.state != "DEPLOYMENT SUCCESS",
                                              Deploy.state != "DEPLOYMENT ERROR")
                                  ).\
                    update({Deploy.state: state})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updatemachineAD(self, session, idmachine, lastuser, ou_machine, ou_user):
        """
            update Machine table in base xmppmaster
            data AD
        """
        try:
            session.query(Machines).filter( Machines.id ==  idmachine).\
                    update({ Machines.ad_ou_machine : ou_machine,
                             Machines.ad_ou_user : ou_user,
                             Machines.lastuser : lastuser})
            session.commit()
            session.flush()
            return 1
        except Exception, e:
            logging.getLogger().error(str(e))
            return -1

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def addServerRelay(self, session,
                        urlguacamole,
                        subnet,
                        nameserver,
                        groupdeploy,
                        ipserver,
                        ipconnection,
                        portconnection,
                        port,
                        mask,
                        jid,
                        longitude="",
                        latitude="",
                        enabled = False,
                        classutil="private",
                        packageserverip ="",
                        packageserverport = "",
                        moderelayserver = "static"):
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
                new_relayserver.package_server_ip = packageserverip
                new_relayserver.package_server_port = packageserverport
                new_relayserver.moderelayserver = moderelayserver
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

    @DatabaseHelper._sessionm
    def getCountPresenceMachine(self, session):
        return session.query(func.count(Machines.id)).scalar()

    @DatabaseHelper._sessionm
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

    def get_count(self, q):
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    def get_count1(self, q):
        return q.with_entities(func.count()).scalar()

    @DatabaseHelper._sessionm
    def getdeploybyuserlen(self, session, login = None):
        if login is not None:
            return self.get_count(session.query(Deploy).filter(Deploy.login == login))
            #lentotal = session.query(func.count(Deploy.id)).filter(Deploy.login == login).scalar()
        else:
            return self.get_count(session.query(Deploy))

    @DatabaseHelper._sessionm
    def getLogxmpp( self,
                    session,
                    start_date,
                    end_date,
                    typelog,
                    action,
                    module,
                    user,
                    how,
                    who,
                    why,
                    headercolumn):
        ##labelheader = [x.strip() for x in headercolumn.split("|") if x.strip() != "" and x is not "None"]
        logs = session.query(Logs)
        if headercolumn == "":
            headercolumn = "date@fromuser@who@text"

        if start_date != "":
            logs = logs.filter( Logs.date > start_date)
        if end_date != "":
            logs = logs.filter( Logs.date < end_date)
        if not (typelog == "None" or typelog == ""):
            logs = logs.filter( Logs.type == typelog)
        if not (action == "None" or action == ""):
            logs = logs.filter( Logs.action == action)
        if not (module == "None" or module == ""):
            #plusieurs criteres peuvent se trouver dans ce parametre.
            criterformodule = [x.strip() for x in module.split("|") if x.strip() != "" and x != "None"]
            for x in criterformodule:
                stringsearchinmodule = "%"+x+"%"
                logs = logs.filter( Logs.module.like(stringsearchinmodule))
        if not (user == "None" or user == ""):
            logs = logs.filter( func.lower(Logs.fromuser).like(func.lower(user)) )
        if not (how == "None" or how == ""):
            logs = logs.filter( Logs.how == how)
        if not (who == "None" or who == ""):
            logs = logs.filter( Logs.who == who)
        if not (why == "None" or why == ""):
            logs = logs.filter( Logs.why == why)
        logs = logs.order_by(desc(Logs.id)).limit(1000)
        result = logs.all()
        session.commit()
        session.flush()
        ret = {"data" : []}
        index = 0
        for linelogs in result:
            listchamp = []
            #listchamp.append(index)
            if headercolumn != "" and "date" in headercolumn:
                listchamp.append(str(linelogs.date))
            if headercolumn != "" and "fromuser" in headercolumn:
                listchamp.append(linelogs.fromuser)
            if headercolumn != "" and "type" in headercolumn:
                listchamp.append(linelogs.type)
            if headercolumn != "" and "action" in headercolumn:
                listchamp.append(linelogs.action)
            if headercolumn != "" and "module" in headercolumn:
                listchamp.append(linelogs.module)
            if headercolumn != "" and "how" in headercolumn:
                listchamp.append(linelogs.how)
            if headercolumn != "" and "who" in headercolumn:
                listchamp.append(linelogs.who)
            if headercolumn != "" and "why" in headercolumn:
                listchamp.append(linelogs.why)
            if headercolumn != "" and "priority" in headercolumn:
                listchamp.append(linelogs.priority)
            if headercolumn != "" and "touser" in headercolumn:
                listchamp.append(linelogs.touser)
            if headercolumn != "" and "sessionname" in headercolumn:
                listchamp.append(linelogs.sessionname)
            if headercolumn != "" and "text" in headercolumn:
                listchamp.append(linelogs.text)


            ##listchamp.append(linelogs.type)
            ##listchamp.append(linelogs.action)
            ##listchamp.append(linelogs.module)
            ##listchamp.append(linelogs.how)
            #listchamp.append(linelogs.who)
            ##listchamp.append(linelogs.why)
            ##listchamp.append(linelogs.priority)
            ##listchamp.append(linelogs.touser)
            #listchamp.append(linelogs.sessionname)
            #listchamp.append(linelogs.text)
            ret['data'].append(listchamp)
            #index = index + 1
        return ret

    @DatabaseHelper._sessionm
    def getdeploybymachinegrprecent(self, session, group_uuid, state, duree, min , max, filt):
        deploylog = session.query(Deploy)
        if group_uuid:
            deploylog = deploylog.filter( Deploy.group_uuid == group_uuid)
        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))
        if state:
            deploylog = deploylog.filter( Deploy.state == state)

        #todo filter
        #if filt:
            #deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                                #Deploy.pathpackage.like('%%%s%%'%(filt)),
                                                #Deploy.start.like('%%%s%%'%(filt)),
                                                #Deploy.login.like('%%%s%%'%(filt)),
                                                #Deploy.host.like('%%%s%%'%(filt))))
        nb = self.get_count(deploylog)
        lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]
        ##deploylog = deploylog.group_by(Deploy.title)
        deploylog = deploylog.order_by(desc(Deploy.id))

        nb = self.get_count(deploylog)
        if min and max:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))

        result = deploylog.all()
        session.commit()
        session.flush()
        ret = { 'lentotal' : 0,
               'lenquery' : 0,
                'tabdeploy' : { 'len' : [],
                                'state' : [],
                                'pathpackage' : [],
                                'sessionid' : [],
                                'start' : [],
                                'inventoryuuid' : [],
                                'command' : [],
                                'start' : [],
                                'login' : [],
                                'host' : [],
                                'macadress' : [],
                                'group_uuid' : [],
                                'startcmd' : [],
                                'endcmd' : [],
                                'jidmachine' : [],
                                'jid_relay' : [],
                                'title' : []
                }
        }
        ret['lentotal'] = lentaillerequette[0]
        ret['lenquery'] = nb
        for linedeploy in result:
            #ret['tabdeploy']['len'].append(linedeploy[1])
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(linedeploy.host.split("/")[-1])
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            if linedeploy.group_uuid == None:
                linedeploy.group_uuid = ""
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret

    @DatabaseHelper._sessionm
    def getdeploybymachinerecent(self, session, uuidinventory, state, duree, min , max, filt):
        deploylog = session.query(Deploy)
        if uuidinventory:
            deploylog = deploylog.filter( Deploy.inventoryuuid == uuidinventory)
        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))
        if state:
            deploylog = deploylog.filter( Deploy.state == state)
        #else:
            #deploylog = deploylog.filter( Deploy.state == "DEPLOYMENT START")

        #if filt:
    #deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                        #Deploy.pathpackage.like('%%%s%%'%(filt)),
                                        #Deploy.start.like('%%%s%%'%(filt)),
                                        #Deploy.login.like('%%%s%%'%(filt)),
                                        #Deploy.host.like('%%%s%%'%(filt))))

        nb = self.get_count(deploylog)

        lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]
        ##deploylog = deploylog.group_by(Deploy.title)
        #deploylog = deploylog.add_column(func.count(Deploy.title))
        deploylog = deploylog.order_by(desc(Deploy.id))

        nb = self.get_count(deploylog)
        if min and max:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))
        result = deploylog.all()
        session.commit()
        session.flush()
        ret = { 'lentotal' : 0,
               'lenquery' : 0,
                'tabdeploy' : { 'len' : [],
                                'state' : [],
                                'pathpackage' : [],
                                'sessionid' : [],
                                'start' : [],
                                'inventoryuuid' : [],
                                'command' : [],
                                'start' : [],
                                'login' : [],
                                'host' : [],
                                'macadress' : [],
                                'group_uuid' : [],
                                'startcmd' : [],
                                'endcmd' : [],
                                'jidmachine' : [],
                                'jid_relay' : [],
                                'title' : []
                }
        }
        ret['lentotal'] = lentaillerequette[0]
        ret['lenquery'] = nb
        for linedeploy in result:
            #ret['tabdeploy']['len'].append(linedeploy[1])
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(linedeploy.host.split("/")[-1])
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret

    @DatabaseHelper._sessionm
    def delDeploybygroup( self,
                          session,
                          numgrp):
        """
            creation d'une organization
        """
        session.query(Deploy).filter(Deploy.group_uuid == numgrp).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getdeploybyuserrecent(self, session, login , state, duree, min=None , max=None, filt=None):
        deploylog = session.query(Deploy)
        if login:
            deploylog = deploylog.filter( Deploy.login == login)
        if state:
            deploylog = deploylog.filter( Deploy.state == state)

        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))

        count = """select count(*) as nb from (
        select count(id) as nb
        from deploy
        where start >= DATE_SUB(NOW(),INTERVAL 24 HOUR)
        group by title
        ) as x;"""

        if filt is not None:
            deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                                Deploy.pathpackage.like('%%%s%%'%(filt)),
                                                Deploy.start.like('%%%s%%'%(filt)),
                                                Deploy.login.like('%%%s%%'%(filt)),
                                                Deploy.host.like('%%%s%%'%(filt))))
            count = """select count(*) as nb from (
              select count(id) as nb
              from deploy
              where start >= DATE_SUB(NOW(),INTERVAL 24 HOUR)
              AND (state LIKE "%%%s%%"
              or pathpackage LIKE "%%%s%%"
              or start LIKE "%%%s%%"
              or login LIKE "%%%s%%"
              or host LIKE "%%%s%%"
              )
              group by title
              ) as x;"""%(filt,filt,filt,filt,filt,)


        lentaillerequette = self.get_count(deploylog)

        result = session.execute(count)
        session.commit()
        session.flush()
        lenrequest = [x for x in result]

        #lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]
        deploylog = deploylog.group_by(Deploy.title)

        deploylog = deploylog.order_by(desc(Deploy.id))

        ##deploylog = deploylog.add_column(func.count(Deploy.title))
        if min is not None and max is not None:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))
        result = deploylog.all()
        session.commit()
        session.flush()
        ret ={'total_of_rows' : 0,
              'lentotal' : 0,
              'tabdeploy' : {
                                'state' : [],
                                'pathpackage' : [],
                                'sessionid' : [],
                                'start' : [],
                                'inventoryuuid' : [],
                                'command' : [],
                                'start' : [],
                                'login' : [],
                                'host' : [],
                                'macadress' : [],
                                'group_uuid' : [],
                                'startcmd' : [],
                                'endcmd' : [],
                                'jidmachine' : [],
                                'jid_relay' : [],
                                'title' : []}}

        ret['lentotal'] = lentaillerequette#[0]
        ret['total_of_rows'] = lenrequest[0][0]
        for linedeploy in result:
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(linedeploy.host.split("/")[-1])
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret


    @DatabaseHelper._sessionm
    def getdeploybyuserpast(self, session, login , duree, min=None , max=None, filt=None):

        deploylog = session.query(Deploy)
        if login:
            deploylog = deploylog.filter( Deploy.login == login)

        if duree:
            deploylog = deploylog.filter( Deploy.start >= (datetime.now() - timedelta(seconds=duree)))

        if filt is not None:
            deploylog = deploylog.filter( or_(  Deploy.state.like('%%%s%%'%(filt)),
                                                Deploy.pathpackage.like('%%%s%%'%(filt)),
                                                Deploy.start.like('%%%s%%'%(filt)),
                                                Deploy.login.like('%%%s%%'%(filt)),
                                                Deploy.host.like('%%%s%%'%(filt))))

        deploylog = deploylog.filter( or_(  Deploy.state == 'DEPLOYMENT SUCCESS',
                                            Deploy.state == 'DEPLOYMENT ERROR',
                                            Deploy.state == 'DEPLOYMENT ABORT'))

        lentaillerequette = session.query(func.count(distinct(Deploy.title)))[0]

        # It is the same as deploylog, but for unknown reason, the count doesn't works with ORM
        count = """select count(*) as nb from (
          select count(id) as nb
          from deploy
          where start >= DATE_SUB(NOW(),INTERVAL 3 MONTH)
          AND (state LIKE "%%%s%%"
          or pathpackage LIKE "%%%s%%"
          or start LIKE "%%%s%%"
          or login LIKE "%%%s%%"
          or host LIKE "%%%s%%"
          )
          group by title
          ) as x;"""%(filt,filt,filt,filt,filt,)
        count = session.execute(count)
        count = [nbcount for nbcount in count]

        deploylog = deploylog.group_by(Deploy.title)

        deploylog = deploylog.order_by(desc(Deploy.id))

        #deploylog = deploylog.add_column(func.count(Deploy.title))

        nbfilter =  self.get_count(deploylog)

        if min is not None and max is not None:
            deploylog = deploylog.offset(int(min)).limit(int(max)-int(min))
        result = deploylog.all()
        session.commit()
        session.flush()
        ret ={'lentotal' : 0,
              'tabdeploy' : {   'len' : [],
                                'state' : [],
                                'pathpackage' : [],
                                'sessionid' : [],
                                'start' : [],
                                'inventoryuuid' : [],
                                'command' : [],
                                'start' : [],
                                'login' : [],
                                'host' : [],
                                'macadress' : [],
                                'group_uuid' : [],
                                'startcmd' : [],
                                'endcmd' : [],
                                'jidmachine' : [],
                                'jid_relay' : [],
                                'title' : []}}

        #ret['lentotal'] = nbfilter
        ret['lentotal'] = count[0][0]
        for linedeploy in result:
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            ret['tabdeploy']['start'].append(str(linedeploy.start))
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['host'].append(linedeploy.host.split("/")[-1])
            ret['tabdeploy']['macadress'].append(linedeploy.macadress)
            ret['tabdeploy']['group_uuid'].append(linedeploy.group_uuid)
            ret['tabdeploy']['startcmd'].append(linedeploy.startcmd)
            ret['tabdeploy']['endcmd'].append(linedeploy.endcmd)
            ret['tabdeploy']['jidmachine'].append(linedeploy.jidmachine)
            ret['tabdeploy']['jid_relay'].append(linedeploy.jid_relay)
            ret['tabdeploy']['title'].append(linedeploy.title)
        return ret


    @DatabaseHelper._sessionm
    def getdeploybyuser(self, session, login = None, numrow = None, offset=None):
        if login is not None:
            deploylog = session.query(Deploy).filter(Deploy.login == login).order_by(desc(Deploy.id))
        else:
            deploylog = session.query(Deploy).order_by(desc(Deploy.id))
        if numrow is not None:
            deploylog = deploylog.limit(numrow)
            if offset is not None:
                deploylog = deploylog.offset(offset)
        deploylog = deploylog.all()
        session.commit()
        session.flush()
        ret ={'len' : len(deploylog),'tabdeploy' : {'state' : [],'pathpackage' : [], 'sessionid' : [],'start' : [], 'inventoryuuid' : [], 'command' : [], 'start' : [], 'login' : [],  'host' : [] }}
        for linedeploy in deploylog:
            ret['tabdeploy']['state'].append(linedeploy.state)
            ret['tabdeploy']['pathpackage'].append(linedeploy.pathpackage.split("/")[-1])
            ret['tabdeploy']['sessionid'].append(linedeploy.sessionid)
            d= linedeploy.start.strftime('%Y-%m-%d %H:%M')
            dd = str(linedeploy.start.strftime('%Y-%m-%d %H:%M'))
            ret['tabdeploy']['start'].append(dd)
            ret['tabdeploy']['inventoryuuid'].append(linedeploy.inventoryuuid)
            ret['tabdeploy']['command'].append(linedeploy.command)
            ret['tabdeploy']['login'].append(linedeploy.login)
            ret['tabdeploy']['start'].append(linedeploy.start)
            ret['tabdeploy']['host'].append(linedeploy.host.split("/")[-1])
        return ret

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def get_qaction(self, session, namecmd, user, grp, completename):
        """
            return quick actions informations
        """
        if grp == 0:
            qa_custom_command = session.query(Qa_custom_command).filter(and_(Qa_custom_command.namecmd==namecmd, Qa_custom_command.user==user))
            qa_custom_command = qa_custom_command.first()
        else:
            osdetection = ""
            if completename != "":
                if completename.endswith('(windows)'):
                    osdetection = "windows"
                elif completename.endswith('(macos)'):
                    osdetection = "macos"
                elif completename.endswith('(linux)'):
                    osdetection = "linux"
            if osdetection == "":
                qa_custom_command = session.query(Qa_custom_command).\
                    filter(and_(Qa_custom_command.customcmd==namecmd,
                                or_(Qa_custom_command.user==user,
                                    Qa_custom_command.user=="allusers")))
            else:
                qa_custom_command = session.query(Qa_custom_command).\
                    filter(and_(Qa_custom_command.customcmd==namecmd,
                                Qa_custom_command.os== osdetection,
                                or_(Qa_custom_command.user==user,
                                    Qa_custom_command.user=="allusers")))
            qa_custom_command = qa_custom_command.first()
        if qa_custom_command:
            result = {  "user" : qa_custom_command.user,
                        "os" : qa_custom_command.os,
                        "namecmd" : qa_custom_command.namecmd,
                        "customcmd" : qa_custom_command.customcmd,
                        "description" : qa_custom_command.description
                        }
            return result
        else:
            result = {}

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def groupdeployfromjid(self, session, jid):
        """ return groupdeploy xmpp for JID """
        sql = """SELECT
                    groupdeploy
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

    @DatabaseHelper._sessionm
    def ippackageserver(self, session, jid):
        """ return ip xmpp for JID """
        sql = """SELECT
                    package_server_ip
                FROM
                    xmppmaster.relayserver
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

    @DatabaseHelper._sessionm
    def portpackageserver(self, session, jid):
        """ return ip xmpp for JID """
        sql = """SELECT
                    package_server_port
                FROM
                    xmppmaster.relayserver
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

    @DatabaseHelper._sessionm
    def ipserverARS(self, session, jid):
        """ return ip xmpp for JID """
        sql = """SELECT
                    ipserver
                FROM
                    xmppmaster.relayserver
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

    @DatabaseHelper._sessionm
    def getUuidFromJid(self, session, jid):
        """ return machine uuid for JID """
        uuid_inventorymachine = session.query(Machines).filter_by(jid=jid).first().uuid_inventorymachine
        if uuid_inventorymachine:
            return uuid_inventorymachine.strip('UUID')
        else:
            return False

    @DatabaseHelper._sessionm
    def algoruleadorganisedbyusers(self, session, userou, classutilMachine = "both", rule = 8, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 8 by organization users
            Field "subject" is used to define the organisation by user OU eg Computers/HeadQuarter/Locations
            Field "relayserver_id" is used to define the Relayserver associe a ce name user
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """

        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
            limit 1;"""%(rule, userou, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
            limit 1;"""%(rule, userou, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algoruleadorganisedbymachines(self, session, machineou, classutilMachine = "both", rule = 7, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 7 by organization machine
            Field "subject" is used to define the organisation by machine OU eg Computers/HeadQuarter/Locations
            Field "relayserver_id" is used to define the Relayserver associe a this organization
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
            limit 1;"""%(rule, machineou, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
            limit 1;"""%(rule, machineou, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]


    @DatabaseHelper._sessionm
    def algoruleuser(self, session, username, classutilMachine = "both", rule = 1, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 1 for user name
            Field "subject" is used to define the name of the user in this rule
            Field "relayserver_id" is used to define the Relayserver associe a ce name user
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
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
                    AND `relayserver`.`moderelayserver` = 'static'
            limit 1;"""%(rule, username, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulehostname(self, session, hostname, classutilMachine = "both", rule = 2, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 2 for hostname
            Field "subject" is used to define the hostname in this rule
            Field "relayserver_id" is used to define the Relayserver associated to this hostname
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        sql = """select `has_relayserverrules`.`id`,`has_relayserverrules`.`subject`
        from `has_relayserverrules`
        where `has_relayserverrules`.`rules_id` = %d
        order by `has_relayserverrules`.`order`;"""%(rule)
        result = session.execute(sql)
        session.commit()
        session.flush()
        listrules = [x for x in result]
        for relayserverrule in listrules:
            subject = relayserverrule[1].replace('*','.*')
            if re.match(subject, hostname, flags=0):
                has_relayserverrules_id = relayserverrule[0]
                if classutilMachine == "private":
                    sql = """select `relayserver`.`id`
                    from `relayserver`
                        inner join
                            `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
                    where
                        `has_relayserverrules`.`rules_id` = %d
                            AND `has_relayserverrules`.`id` = %d
                            AND `relayserver`.`enabled` = %d
                            AND `relayserver`.`moderelayserver` = 'static'
                            AND `relayserver`.`classutil` = '%s'
                    limit 1;"""%(rule, has_relayserverrules_id, enabled, classutilMachine)
                else:
                    sql = """select `relayserver`.`id`
                    from `relayserver`
                        inner join
                            `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
                    where
                        `has_relayserverrules`.`rules_id` = %d
                            AND `has_relayserverrules`.`id` = %d
                            AND `relayserver`.`enabled` = %d
                            AND `relayserver`.`moderelayserver` = 'static'
                    limit 1;"""%(rule, has_relayserverrules_id, enabled)
                result = session.execute(sql)
                session.commit()
                session.flush()
                return [y for y in result]
        return ""

    @DatabaseHelper._sessionm
    def algoruleloadbalancer(self, session):
        sql = """
            SELECT
                COUNT(*) AS nb, `machines`.`groupdeploy`, `relayserver`.`id`
            FROM
                xmppmaster.machines
                    INNER JOIN
                xmppmaster.`relayserver` ON `relayserver`.`groupdeploy` = `machines`.`groupdeploy`
            WHERE
                agenttype = 'machine'
            GROUP BY `machines`.`groupdeploy`
            ORDER BY nb DESC
            LIMIT 1;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulesubnet(self, session, subnetmachine, classutilMachine = "both",  enabled=1):
        """
            To associate relay server that is on same networks...
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
            where
                        `relayserver`.`enabled` = %d
                    AND `relayserver`.`subnet` ='%s'
                    AND `relayserver`.`classutil` = '%s'
                    AND `relayserver`.`moderelayserver` = 'static'
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

    @DatabaseHelper._sessionm
    def algorulebynetworkaddress(self, session, subnetmachine, classutilMachine = "both", rule = 9, enabled=1):
        """
            Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 9 by network address
            Field "subject" is used to define the subnet for association
            Field "relayserver_id" is used to define the Relayserver to be assigned to the machines matching that rule
            enabled = 1 Only on active relayserver.
            If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
            limit 1;"""%(rule, subnetmachine, enabled, classutilMachine)
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
            limit 1;"""%(rule, subnetmachine, enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def jidrelayserverforip(self, session, ip ):
        """ return jid server relay for connection"""
        sql ="""SELECT
                    ipconnection, port, jid, urlguacamole
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

    @DatabaseHelper._sessionm
    def IdlonglatServerRelay(self, session, classutilMachine = "both",  enabled=1):
        """ return long and lat server relay"""
        if classutilMachine == "private":
            sql = """SELECT
                        id, longitude, latitude
                    FROM
                        xmppmaster.relayserver
                    WHERE
                            `relayserver`.`enabled` = %d
                        AND `relayserver`.`classutil` = '%s'
                    AND `relayserver`.`moderelayserver` = 'static';"""%(enabled, classutilMachine)
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

    #@DatabaseHelper._sessionm
    #def algoruledefault(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
        #pass

    #@DatabaseHelper._sessionm
    #def algorulegeo(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
        #pass

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def hasmachineusers(self, session, useradd, idmachine):
        sql = """INSERT
                INTO `xmppmaster`.`has_machinesusers` (`users_id`, `machines_id`)
                VALUES ('%s', '%s');"""%(useradd,idmachine)
        session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def addlistguacamoleidforiventoryid(self, session, idinventory, connection):
        # objet connection: {u'VNC': 60, u'RDP': 58, u'SSH': 59}}
        sql  = """DELETE FROM `xmppmaster`.`has_guacamole`
                    WHERE
                        `xmppmaster`.`has_guacamole`.`idinventory` = '%s';"""%idinventory
        session.execute(sql)
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

    @DatabaseHelper._sessionm
    def listserverrelay(self, session, moderelayserver = "static"):
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.relayserver
                WHERE
                    `xmppmaster`.`relayserver`.`moderelayserver` = '%s'
                    ;"""%moderelayserver
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def listmachines(self, session):
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.machines;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def clearMachine(self, session):
        session.execute('TRUNCATE TABLE xmppmaster.machines;')
        session.execute('TRUNCATE TABLE xmppmaster.network;')
        session.execute('TRUNCATE TABLE xmppmaster.has_machinesusers;')
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def getjidMachinefromuuid(self, session, uuid):
        try:
            sql = """SELECT
                        jid
                    FROM
                        xmppmaster.machines
                    WHERE
                        uuid_inventorymachine = '%s'
                        LIMIT 1;"""%uuid
            jidmachine = session.execute(sql)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))
            return ""
        try :
            result=[x for x in jidmachine][0]
        except:
            return ""
        return result[0]

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def getPresenceuuid(self, session, uuid):
        machinespresente = session.query(Machines.uuid_inventorymachine).filter( Machines.uuid_inventorymachine == uuid ).first()
        session.commit()
        session.flush()
        if machinespresente :
            return True
        return False

    @DatabaseHelper._sessionm
    def getPresenceuuids(self, session, uuids):
        if isinstance(uuids, basestring):
            uuids=[uuids]
        result = { }
        for uuidmachine in uuids:
            result[uuidmachine] = False
        machinespresente = session.query(Machines.uuid_inventorymachine).filter(Machines.uuid_inventorymachine.in_(uuids)).all()
        session.commit()
        session.flush()
        for linemachine in machinespresente:
            result[linemachine.uuid_inventorymachine] = True
        return result

    #topology
    @DatabaseHelper._sessionm
    def listRS(self,session):
        """ return les RS pour le deploiement """
        sql = """SELECT DISTINCT
                    groupdeploy
                FROM
                    xmppmaster.machines;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        listrs = [x for x in result]
        return [ i[0] for i in listrs ]

    #topology
    @DatabaseHelper._sessionm
    def topologypulse(self, session):
        #listrs = self.listRS()
        ## select liste des RS
        #list des machines pour un relayserver

        sql = """SELECT groupdeploy,
                    GROUP_CONCAT(jid)
                FROM
                    xmppmaster.machines
                WHERE
                    xmppmaster.machines.agenttype = 'machine'
                GROUP BY
                    groupdeploy;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        listmachinebyRS = [x for x in result]
        resulttopologie = {}
        for i in listmachinebyRS:
            listmachines = i[1].split(',')
            resulttopologie[i[0]] = listmachines
        self.write_topologyfile(resulttopologie)
        return [ resulttopologie]

    #topology
    def write_topologyfile(self, topology):
        directoryjson = os.path.join("/","usr","share","mmc","datatopology")
        if not os.path.isdir(directoryjson):
            #creation repertoire de json topology
            os.makedirs(directoryjson)
            os.chmod(directoryjson, 0o777) # for example
            uid, gid =  pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_gid
            os.chown(directoryjson, uid, gid) # set user:group as root:www-data
        # creation topology file.
        filename = "topology.json"
        pathfile =  os.path.join(directoryjson, filename)
        builddatajson = { "name" : "Pulse", "type" : "AMR", "parent": None, "children": []}
        for i in topology:
            listmachines = topology[i]

            ARS = {}
            ARS['name'] = i
            ARS['display_name'] = i.split("/")[1]
            ARS['type'] = "ARS"
            ARS['parent'] = "Pulse"
            ARS['children'] = []

            listmachinesstring = []
            for mach in listmachines:
                ARS['children'].append({ "name" : mach,
                'display_name': mach.split("/")[1],
                "type" : "AM", "parent" : i })
            #builddatajson[i] = listmachinesstring
            #ARS['children'] = builddatajson
            #print listmachinesstring
            builddatajson['children'].append(ARS)
        #import pprint
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(builddatajson)

        with open(pathfile, 'w') as outfile:
            json.dump(builddatajson,  outfile, indent = 4)
        os.chmod(pathfile, 0o777)
        uid, gid =  pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_gid
        os.chown(pathfile, uid, gid)

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def getlistPresenceMachineid(self, session, format=False):
        sql = """SELECT
                    uuid_inventorymachine
                 FROM
                    xmppmaster.machines
                 WHERE
                    agenttype = 'machine' and uuid_inventorymachine IS NOT NULL;"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append(t[0])
            return a
        except:
            return a

    @DatabaseHelper._sessionm
    def getxmppmasterfilterforglpi(self, session, listqueryxmppmaster = None):
        fl = listqueryxmppmaster[3].replace('*',"%")
        if listqueryxmppmaster[2] == "OU user":
            machineid = session.query(Organization_ad.id_inventory)
            machineid = machineid.filter(Organization_ad.ouuser.like(fl))
        elif listqueryxmppmaster[2] == "OU machine":
            machineid = session.query(Organization_ad.id_inventory)
            machineid = machineid.filter(Organization_ad.oumachine.like(fl))
        elif listqueryxmppmaster[2] == "Online computer":
            d = XmppMasterDatabase().getlistPresenceMachineid()
            listid = [x.replace("UUID", "") for x in d]
            return listid
        machineid = machineid.all()
        session.commit()
        session.flush()
        ret = [str(m.id_inventory) for m in machineid]
        return ret


    @DatabaseHelper._sessionm
    def getListPresenceMachine(self, session):
        sql = """SELECT
                    jid, agenttype, hostname, uuid_inventorymachine
                 FROM
                    xmppmaster.machines
                 WHERE
                    agenttype='machine' and uuid_inventorymachine IS NOT NULL;"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append({'jid':t[0],'type': t[1], 'hostname':t[2], 'uuid_inventorymachine':t[3]})
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def getListPresenceMachineWithKiosk(self, session):
        sql = """SELECT
                    *
                 FROM
                    xmppmaster.machines
                 WHERE
                    agenttype='machine' and uuid_inventorymachine IS NOT NULL ;"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a=[]
            for t in presencelist:
                a.append({'id':t[0],'jid': t[1], 'platform':t[2], \
                    'hostname': t[4], 'uuid_inventorymachine':t[5], \
                    'agenttype':t[10], 'classutil': t[11]})
            return a
        except:
            return -1

    @DatabaseHelper._sessionm
    def delPresenceMachine(self, session, jid):
        result = ['-1']
        typemachine = "machine"
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
                typemachine = "relayserver"
                sql2 = """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""%result[1]
                session.execute(sql2)
            session.execute(sql)
            session.execute(sql1)
            session.execute(sql3)
            session.commit()
            session.flush()
        except IndexError:
            logging.getLogger().warning("Configuration agent machine jid [%s]. no jid in base for configuration"%jid)
            return {}
        except Exception, e:
            logging.getLogger().error(str(e))
            return {}
        resulttypemachine={"type" : typemachine }
        return resulttypemachine

    @DatabaseHelper._sessionm
    def getPresencejiduser(self, session, userjid):
        sql = """SELECT COUNT(jid) AS nb
            FROM
                 xmppmaster.machines
             WHERE
              jid LIKE ('%s%%');"""%(userjid)
        presencejid = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in presencejid]
        if ret[0] == 0 :
            return False
        return True

    @DatabaseHelper._sessionm
    def delPresenceMachinebyjiduser(self, session, jiduser):
        result = ['-1']
        typemachine = "machine"
        try:
            sql = """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.jid like('%s@%%');"""%jiduser
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
                typemachine = "relayserver"
                sql2 = """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""%result[1]
                session.execute(sql2)
            session.execute(sql)
            session.execute(sql1)
            session.execute(sql3)
            session.commit()
            session.flush()
        except IndexError:
            logging.getLogger().warning("Configuration agent machine jid [%s]. no jid in base for configuration"%jiduser)
            return {}
        except Exception, e:
            logging.getLogger().error(str(e))
            return {}
        resulttypemachine={"type" : typemachine }
        return resulttypemachine

    @DatabaseHelper._sessionm
    def getPresencejiduser(self, session, userjid):
        sql = """SELECT COUNT(jid) AS nb
            FROM
                 xmppmaster.machines
             WHERE
              jid LIKE ('%s%%');"""%(userjid)
        presencejid = session.execute(sql)
        session.commit()
        session.flush()
        ret=[m[0] for m in presencejid]
        if ret[0] == 0 :
            return False
        return True

    @DatabaseHelper._sessionm
    def delPresenceMachinebyjiduser(self, session, jiduser):
        result = ['-1']
        typemachine = "machine"
        try:
            sql = """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.jid like('%s@%%');"""%jiduser
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
                typemachine = "relayserver"
                sql2 = """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""%result[1]
                session.execute(sql2)
            session.execute(sql)
            session.execute(sql1)
            session.execute(sql3)
            session.commit()
            session.flush()
        except IndexError:
            logging.getLogger().warning("Configuration agent machine jid [%s]. no jid in base for configuration"%jiduser)
            return {}
        except Exception, e:
            logging.getLogger().error(str(e))
            return {}
        resulttypemachine={"type" : typemachine }
        return resulttypemachine

    @DatabaseHelper._sessionm
    def getGuacamoleRelayServerMachineUuid(self, session, uuid):
        relayserver = session.query(Machines).filter(Machines.uuid_inventorymachine == uuid).one()
        session.commit()
        session.flush()
        try:
            result = {
                        "uuid" : uuid,
                        "jid" : relayserver.jid,
                        "groupdeploy" : relayserver.groupdeploy,
                        "urlguacamole" : relayserver.urlguacamole,
                        "subnetxmpp" : relayserver.subnetxmpp,
                        "hostname" : relayserver.hostname,
                        "platform" : relayserver.platform,
                        "macaddress" : relayserver.macaddress,
                        "archi" : relayserver.archi,
                        "uuid_inventorymachine" : relayserver.uuid_inventorymachine,
                        "ip_xmpp" : relayserver.ip_xmpp,
                        "agenttype" : relayserver.agenttype
                        }
            for i in result:
                if result[i] == None:
                    result[i] = ""
        except Exception:
            result = {
                        "uuid" : uuid,
                        "jid" : "",
                        "groupdeploy" : "",
                        "urlguacamole" : "",
                        "subnetxmpp" : "",
                        "hostname" : "",
                        "platform" : "",
                        "macaddress" : "",
                        "archi" : "",
                        "uuid_inventorymachine" : "",
                        "ip_xmpp" : "",
                        "agenttype" : ""
                    }
        return result

    @DatabaseHelper._sessionm
    def getGuacamoleidforUuid(self, session, uuid):
        ret=session.query(Has_guacamole.idguacamole,Has_guacamole.protocol).filter(Has_guacamole.idinventory == uuid.replace('UUID','')).all()
        session.commit()
        session.flush()
        if ret:
            return [(m[1],m[0]) for m in ret]
        else:
            return []

    @DatabaseHelper._sessionm
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

    @DatabaseHelper._sessionm
    def getMachinefromjid(self, session, jid):
        """ information machine"""
        machine = session.query(Machines).filter(Machines.jid == jid).first()
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {  "id" : machine.id,
                        "jid" : machine.jid,
                        "platform" : machine.platform,
                        "archi" : machine.archi,
                        "hostname" : machine.hostname,
                        "uuid_inventorymachine" : machine.uuid_inventorymachine,
                        "ip_xmpp" : machine.ip_xmpp,
                        "ippublic" : machine.ippublic,
                        "macaddress" : machine.macaddress,
                        "subnetxmpp" : machine.subnetxmpp,
                        "agenttype" : machine.agenttype,
                        "classutil" : machine.classutil,
                        "groupdeploy" : machine.groupdeploy,
                        "urlguacamole" : machine.urlguacamole,
                        "picklekeypublic" : machine.picklekeypublic,
                        'ad_ou_user': machine.ad_ou_user,
                        'ad_ou_machine': machine.ad_ou_machine,
                        'kiosk_presence': machine.kiosk_presence,
                        'lastuser': machine.lastuser}
        return result

    @DatabaseHelper._sessionm
    def getMachinefromuuid(self, session, uuid):
        """ information machine"""
        machine = session.query(Machines).filter(Machines.uuid_inventorymachine == uuid).first()
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {  "id" : machine.id,
                        "jid" : machine.jid,
                        "platform" : machine.platform,
                        "archi" : machine.archi,
                        "hostname" : machine.hostname,
                        "uuid_inventorymachine" : machine.uuid_inventorymachine,
                        "ip_xmpp" : machine.ip_xmpp,
                        "ippublic" : machine.ippublic,
                        "macaddress" : machine.macaddress,
                        "subnetxmpp" : machine.subnetxmpp,
                        "agenttype" : machine.agenttype,
                        "classutil" : machine.classutil,
                        "groupdeploy" : machine.groupdeploy,
                        "urlguacamole" : machine.urlguacamole,
                        "picklekeypublic" : machine.picklekeypublic,
                        'ad_ou_user': machine.ad_ou_user,
                        'ad_ou_machine': machine.ad_ou_machine,
                        'kiosk_presence': machine.kiosk_presence,
                        'lastuser': machine.lastuser}
        return result

    @DatabaseHelper._sessionm
    def get_List_jid_ServerRelay_enable(self, session, enabled=1):
        """ return list enable server relay id """
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.relayserver
                WHERE
                        `relayserver`.`enabled` = %d;"""%(enabled)
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]
    
    @DatabaseHelper._sessionm
    def getRelayServerfromjid(self, session, jid):
        relayserver = session.query(RelayServer).filter(RelayServer.jid == jid)
        relayserver = relayserver.first()
        session.commit()
        session.flush()
        try:
            result = {  'id' :  relayserver.id,
                        'urlguacamole': relayserver.urlguacamole,
                        'subnet' : relayserver.subnet,
                        'nameserver' : relayserver.nameserver,
                        'ipserver' : relayserver.ipserver,
                        'ipconnection' : relayserver.ipconnection,
                        'port' : relayserver.port,
                        'portconnection' : relayserver.portconnection,
                        'mask' : relayserver.mask,
                        'jid' : relayserver.jid,
                        'longitude' : relayserver.longitude,
                        'latitude' : relayserver.latitude,
                        'enabled' : relayserver.enabled,
                        'classutil' : relayserver.classutil,
                        'groupdeploy' : relayserver.groupdeploy,
                        'package_server_ip' : relayserver.package_server_ip,
                        'package_server_port' : relayserver.package_server_port,
                        'moderelayserver' : relayserver.moderelayserver
            }
        except Exception:
            result = {}
        return result


    @DatabaseHelper._sessionm
    def getRelayServerForMachineUuid(self, session, uuid):
        relayserver = session.query(Machines).filter(Machines.uuid_inventorymachine == uuid).one()
        session.commit()
        session.flush()
        try:
            result = {
                        "uuid" : uuid,
                        "jid" : relayserver.groupdeploy
                        }
            for i in result:
                if result[i] == None:
                    result[i] = ""
        except Exception:
            result = {
                        "uuid" : uuid,
                        "jid" : ""
                    }
        return result

    @DatabaseHelper._sessionm
    def getCountOnlineMachine(self, session):
        return session.query(func.count(Machines.id)).filter(Machines.agenttype == "machine").scalar()

    @DatabaseHelper._sessionm
    def getRelayServerofclusterFromjidars(self, session, jid, moderelayserver = None):
        #determine ARS id from jid
        relayserver = session.query(RelayServer).filter(RelayServer.jid == jid)
        relayserver = relayserver.first()
        session.commit()
        session.flush()
        if relayserver:
            #object complete
            #result = [relayserver.id,
                      #relayserver.urlguacamole,
                      #relayserver.subnet,
                      #relayserver.nameserver,
                      #relayserver.ipserver,
                      #relayserver.ipconnection,
                      #relayserver.port,
                      #relayserver.portconnection,
                      #relayserver.mask,
                      #relayserver.jid,
                      #relayserver.longitude,
                      #relayserver.latitude,
                      #relayserver.enabled,
                      #relayserver.classutil,
                      #relayserver.groupdeploy,
                      #relayserver.package_server_ip,
                      #relayserver.package_server_port
            #]

            notconfars = { relayserver.jid :[relayserver.ipconnection, relayserver.port, relayserver.jid, relayserver.urlguacamole, 0 ]}
            # search for clusters where ARS is
            clustersid = session.query(Has_cluster_ars).filter(Has_cluster_ars.id_ars == relayserver.id)
            clustersid = clustersid.all()
            session.commit()
            session.flush()
            #search the ARS in the same cluster that ARS finds
            if clustersid:
                listcluster_id = [m.id_cluster for m in clustersid]
                ars = session.query(RelayServer).\
                    join(Has_cluster_ars, Has_cluster_ars.id_ars == RelayServer.id).\
                        join(Cluster_ars, Has_cluster_ars.id_cluster == Cluster_ars.id)
                if moderelayserver != None:
                    ars = ars.filter(and_(Has_cluster_ars.id_cluster.in_(listcluster_id),
                                          RelayServer.enabled == 1,
                                          RelayServer.moderelayserver == moderelayserver ) )
                else:
                    ars = ars.filter(and_(Has_cluster_ars.id_cluster.in_(listcluster_id),
                                          RelayServer.enabled == 1 ) )
                ars = ars.all()
                session.commit()
                session.flush()
                if ars:
                    #result1 = [(m.ipconnection,m.port,m.jid,m.urlguacamole)for m in ars]
                    result2 = { m.jid :[m.ipconnection, m.port, m.jid, m.urlguacamole, 0 ] for m in ars}
                    countarsclient = self.algoloadbalancerforcluster()
                    if len(countarsclient) != 0:
                        for i in countarsclient:
                            try:
                                if result2[i[1]]:
                                    result2[i[1]][4] = i[0]
                            except KeyError:
                                pass
                    return result2
            else:
                # there are no clusters configured for this ARS.
                logging.getLogger().warning("Cluster ARS [%s] no configured"%relayserver.jid)
                return notconfars
        else:
            logging.getLogger().warning("Relay server no present")
            logging.getLogger().warning("ARS not known for machine")
        return {}


    @DatabaseHelper._sessionm
    def algoloadbalancerforcluster(self, session):
        sql = """
            SELECT
                COUNT(*) AS nb, `machines`.`groupdeploy`
            FROM
                xmppmaster.machines
            WHERE
                agenttype = 'machine'
            GROUP BY `machines`.`groupdeploy`
            ORDER BY nb DESC;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def get_machine_ad_infos(self, session, uuid_inventory):
        """
        Select the founded OUs of the logged machine.
        Param:
            uuid_inventory: str. This param is the uuid of the inventory of the machine received by xmpp.

        Returns:
            List of tuple. The tuple contains all the ou_machine and ou_user founded.
        """

        sql = """
        SELECT
            ad_ou_machine, ad_ou_user
        FROM
            machines
        WHERE
            uuid_inventorymachine = '%s';"""%(uuid_inventory)

        result = session.execute(sql)
        session.commit()
        session.flush()
        return [element for element in result]

    @DatabaseHelper._sessionm
    def get_machines_with_kiosk(self, session):
        """
        Select the machines with the kiosk installed.
        Returns:
            List of tuple. The tuple contains all the machines founded.
        """

        sql = """
        SELECT
            *
        FROM
            machines
        WHERE
            kiosk_presence = 'True';"""
        result = session.execute(sql)
        session.commit()
        session.flush()

        return [element for element in result]

    @DatabaseHelper._sessionm
    def get_machines_online_for_dashboard(self, session):
        ret = session.query(Machines.uuid_inventorymachine, Machines.macaddress).filter(Machines.agenttype != "relayserver").all()

        if ret is None:
            ret = []
        else:
            ret = [{'uuid':machine[0], 'macaddress':machine[1]} for machine in ret]
        return ret
