# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import logging, re
try :
    import cPickle as pickle
except ImportError :
    import pickle # pyflakes.ignore
from StringIO import StringIO

import MySQLdb

from twisted.internet.protocol import Factory, ProcessProtocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred

from pulse2.scheduler.config import SchedulerConfig, SchedulerDatabaseConfig
from pulse2.scheduler.network import chooseClientIP
from pulse2.scheduler.checks import getCheck

def sqladdslashes(s):
    return re.sub("(\\\\|'|\")", lambda o: "\\" + o.group(1), s)

def stripbrokenchars(s):
    bad_map = {
        u"\u2019":  u"'",
        u"\u2013":  u"-",
    }
    utf_map = dict([(ord(k), ord(v)) for k,v in bad_map.items()])
    return s.translate(utf_map)

class PackUtils :
    @classmethod
    def pack(cls, data):
        return pickle.dumps(data)

    @classmethod
    def unpack(cls, packet):
        try :
            ret = pickle.loads(packet)
            return ret
        except EOFError, e:
            logging.getLogger().debug("EOF: Losing a packet from scheduler-proxy: %s" % str(e))
            return None
        except Exception, e:
            logging.getLogger().warn("Losing a packet from scheduler-proxy: %s" % str(e))
            return None

def getClientCheck(target):
    return getCheck(SchedulerConfig().client_check, {
        'uuid': target.getUUID(),
        'shortname': target.getShortName(),
        'ips': target.getIps(),
        'macs': target.getMacs()
    })

def getServerCheck(target):
    return getCheck(SchedulerConfig().server_check, {
        'uuid': target.getUUID(),
        'shortname': target.getShortName(),
        'ips': target.getIps(),
        'macs': target.getMacs()
    })

def chooseClientInfo(target):
    host_dict = {'uuid': target.getUUID(),
                 'fqdn': target.getFQDN(),
                 'shortname': target.getShortName(),
                 'ips': target.getIps(),
                 'macs': target.getMacs(),
                 'netmasks': target.getNetmasks()
                }

    return chooseClientIP(host_dict)


class UnixProtocol (object, LineReceiver):

    __data = None

    def dataReceived(self, data):
        try :
            if not self.__data :
                self.__data = StringIO()

            self.__data.write(data)
            packet = pickle.loads(self.__data.getvalue())
        except EOFError:
            logging.getLogger().debug("EOF:completing the packet len=%d" % len(self.__data.getvalue()))
            return
        except pickle.UnpicklingError:
            logging.getLogger().debug("Unpickle:completing the packet len=%d" % len(self.__data.getvalue()))
            return
        except Exception, e:
            logging.getLogger().debug("Another:completing the packet len=%d" % len(self.__data.getvalue()))
            logging.getLogger().debug("Another exception when completing packet %s"  % str(e))
            return


        if isinstance(packet, list) and len(packet) == 2:
            name, args = packet
            method = self._lookup_procedure(name)
        else :
            logging.getLogger().warn("Response unpacking failed")
            d = maybeDeferred(self._send_response, "NOK")
            d.addErrback(self._eb_call_failed, "response:failed")
            return

        self.__data = None

        d = maybeDeferred(method, self, *args)
        d.addCallback(self._send_response)
        d.addErrback(self._eb_call_failed, name)


    def _send_response(self, response):
        logging.getLogger().debug("response: %s" % str(response))
        try:
            packet = PackUtils.pack(response)
            self.sendLine(packet)
        except Exception, e:
            logging.getLogger().error("UX response sending failed: %s"  % str(e))


    def _eb_call_failed(self, failure, method_name):
        logging.getLogger().error("Method calling %s failed: %s" % (method_name, failure))

    def _lookup_procedure(self, name):
        this_class_dict = self.__class__.__mro__[0].__dict__
        method_matches = [f for (k, f) in this_class_dict.items()
                                      if k == name and callable(f)]
        if len(method_matches)==1 :
            return method_matches[0]


class UNIXFactory(Factory):
    protocol = UnixProtocol

def chooseClientNetwork(target):
    return chooseClientIP({'uuid': target.getUUID(),
                           'fqdn': target.getFQDN(),
                           'shortname': target.getShortName(),
                           'ips': target.getIps(),
                           'macs': target.getMacs(),
                           'netmasks': target.getNetmasks()
                         })


def launcher_proxymethod(*options):
    """
    Decorator to share a decorated method with the scheduler-proxy
    which is processing the incoming requests from launcher.
    """
    try:

        if len(options) == 1 and callable(options[0]) :
            # if only one option, this is a decorator without a parameter
            # so first parameter is decorated function
            fn = options[0]
            name = fn.__name__
            aliased = False
        else :
            # first argument supposed as alias
            name = options[0]
            aliased = True


        def wrap(f, method_name=name):
            def inner(self, *args, **kwargs):
                # TODO - test if Phase instance
                if self._register_only :
                    if method_name not in self._proxy_methods :
                        self._proxy_methods[method_name] = f#(self, f)#(f, args, kwargs)

                else :
                    return f(self, *args, **kwargs)

            inner.is_proxy_fnc = True
            return inner

        if not aliased :
            return wrap(fn, name)
        else :
            return wrap
    except Exception, e :
        logging.getLogger().error("launcher_proxymethod: %s"  % str(e))


class ProxyProcessProtocol(ProcessProtocol):

     def processExited(self, reason):
         logging.getLogger().warn("XML Proxy: Process exited: %s" % (reason.value.exitCode))

     def errReceived(self, data):
         logging.getLogger().warn("XMLRPC Proxy: STDERR: %s" % repr(data))

     def outConnectionLost(self, reason):
         logging.getLogger().info("XMLRPC Proxy: Connection lost: %s" % (reason.value.exitCode))


class SpawnProxy :
    def __init__(self, path):
         self.protocol = ProxyProcessProtocol()
         if isinstance(path, str):
             self.path = [path]
         else:
             self.path = path

    def run(self):
         return reactor.spawnProcess(self.protocol,
                                     self.path[0],
                                     self.path,
                                     env=None,
                                     childFDs={0 :"w",
                                               1 :"r",
                                               2:'r'}
                                    )

class WUInjectDB :
    """
    A shortcut to insert the Windows Updates into the 'update' database.
    """

    conn = None

    def __init__(self):
        self.config = SchedulerDatabaseConfig()

        self.logger = logging.getLogger()
        self.connect()


    def connect(self):
        try:
            self.conn = MySQLdb.connect(user=self.config.dbuser,
                                        passwd=self.config.dbpasswd,
                                        host=self.config.dbhost,
                                        port=self.config.dbport,
                                        db="update")
        except Exception, exc:
            self.logger.error("Can't connect to the database: %s" % str(exc))
            return False

        return True

    @property
    def cursor(self):
        """
        @return: dataset cursor
        @rtype: object
        """
        try:
            return self.conn.cursor()
        except Exception, exc:
            self.logger.error("Error while creating cursor: %s" % str(exc))


    def uuid_exists(self, uuid):
        query = "SELECT 1 FROM updates WHERE uuid = '%s';" % (uuid)

        c = self.cursor
        c.execute(query)
        if len(c.fetchall()) == 1:
            return True
        return False


    def get_update_id(self, uuid):
        query = "SELECT id FROM updates WHERE uuid = '%s';" % (uuid)

        c = self.cursor
        c.execute(query)

        result = c.fetchall()
        if len(result) > 0 :
            return result[0][0]
        return None


    def target_exists(self, target_uuid, update_id):
        query = "SELECT 1 FROM targets WHERE uuid = '%s' AND update_id = %d;" % (target_uuid, update_id)

        c = self.cursor
        c.execute(query)
        if len(c.fetchall()) == 1:
            return True
        return False


    def insert_target(self, update_id, uuid, is_installed):
        """
        Inserts the target with a update reference.
        """

        stat = "INSERT INTO targets (update_id, uuid, is_installed) "
        stat += "VALUES (%d, '%s', %d);" % (update_id, uuid, is_installed)

        self.logger.debug("\033[33m%s\033[0m" % stat)
        try:
            c = self.cursor
            c.execute(stat)
            self.conn.commit()
        except Exception, exc:
            self.conn.rollback()
            self.logger.error("Error while insert target into 'update' db: %s" % str(exc))


    def update_target(self, update_id, uuid, is_installed):
        """
        Update the target with a update reference.
        """

        stat = "UPDATE targets SET is_installed = %d " % is_installed
        stat += "WHERE update_id = %s AND uuid = %s;" % (update_id, uuid)

        self.logger.debug("\033[33m%s\033[0m" % stat)
        try:
            c = self.cursor
            c.execute(stat)
            self.conn.commit()
        except Exception, exc:
            self.conn.rollback()
            self.logger.error("Error while insert target into 'update' db: %s" % str(exc))

    def purge_obselete_updates(self, uuid, update_uuids):
        """
        Purge all target links if update are no more present
        in json
        """
        if not update_uuids:
            return

        stat = "DELETE FROM targets WHERE uuid = %s " % uuid
        stat += "AND update_id IN ("
        stat += "SELECT id FROM updates WHERE uuid IN('%s'))" % "', '".join(update_uuids)

        self.logger.debug("\033[33m%s\033[0m" % stat)

        try:
            c = self.cursor
            c.execute(stat)
            self.conn.commit()
        except Exception, exc:
            self.conn.rollback()
            self.logger.error("Error while insert target into 'update' db: %s" % str(exc))

    def insert_WU(self,
                  uuid,
                  title,
                  kb_number,
                  type_id,
                  need_reboot,
                  request_user_input,
                  os_class_id,
                  info_url):
        """ Windows Updates insert """

        stat = "INSERT INTO updates "
        stat += "(uuid, title, kb_number, type_id, os_class_id, need_reboot, "
        stat += "request_user_input, info_url) "
        stat += "VALUES ('%s', '%s', '%s', %d, %d, %d, %d, '%s');"

        try:
            title = sqladdslashes(stripbrokenchars(title.decode('utf-8', 'ignore')))
        except Exception, e:
            self.logger.warn("WU Unable to decode title: %s" % str(e))
        try:
            kb_number = sqladdslashes(stripbrokenchars(kb_number.decode('utf-8', 'ignore')))
        except Exception, e:
            self.logger.warn("WU Unable to decode KB number: %s" % str(e))
        try:
            info_url = sqladdslashes(stripbrokenchars(info_url.decode('utf-8', 'ignore')))
        except Exception, e:
            self.logger.warn("WU Unable to decode info URL: %s" % str(e))

        try:
            stat = stat % (uuid,
                       title,
                       kb_number,
                       type_id,
                       os_class_id,
                       need_reboot,
                       request_user_input,
                       info_url)
        except Exception, e:
            import sys
            self.logger.error('Unable to parse WU item, traceback was: '+str(sys.exc_info()))

        self.logger.debug("\033[33m%s\033[0m" % stat)


        try:
            c = self.cursor
            c.execute(stat)
            self.conn.commit()
        except Exception, exc:
            self.conn.rollback()
            self.logger.error("Error while insert an update record into 'update' db: %s" % str(exc))


    def inject(self,
               target_uuid,
               uuid,
               title,
               kb_number,
               type_id,
               need_reboot,
               request_user_input,
               os_class_id,
               info_url,
               is_installed):
        """
        Injects the parsed stdout content into 'update' database.
        """

        if not self.uuid_exists(uuid):
            self.insert_WU(uuid,
                           title,
                           kb_number,
                           type_id,
                           need_reboot,
                           request_user_input,
                           os_class_id,
                           info_url)

        update_id = self.get_update_id(uuid)

        if not self.target_exists(target_uuid, update_id):
            self.insert_target(update_id, target_uuid, is_installed)
        else:
            # Set the NEW is_installed field
            self.update_target(update_id, target_uuid, is_installed)

