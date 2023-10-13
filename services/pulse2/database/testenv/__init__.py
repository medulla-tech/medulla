# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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

from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct, Table
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta

from mmc.database.database_helper import DatabaseHelper
from pulse2.database.testenv.schema import Tests
from pulse2.database.testenv.schema import Tests, Machines, Has_guacamole

import logging
import json
import time

logger = logging.getLogger()

class TestenvDatabase(DatabaseHelper):
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "testenv"
        self.configfile = "testenv.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        if self.is_activated:
            return None
        self.config = config

        self.db = create_engine(self.makeConnectionPath(), 
                                pool_recycle = self.config.dbpoolrecycle, 
                                pool_size = self.config.dbpoolsize)
        print(self.makeConnectionPath())
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM testenv.version limit 1;")
        re = [element.Number for element in result]
        return True

    def initMappers(self):
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
            raise "Database testenv connection error"
        return ret

    # =====================================================================
    # testenv FUNCTIONS
    # =====================================================================
    @DatabaseHelper._sessionm
    def tests(self, session):
        ret = session.query(Tests).all()
        lines = []
        for row in ret:
            lines.append(row.toDict())

        return lines


    @DatabaseHelper._sessionm
    def createVM(self, session, dict):
        try:
            new_vm = Machines(
                uuid_machine=dict['uuid'],
                nom=dict['name'],
                plateform=dict['plateform'],
                architecture=dict['architecture'],
                cpu=int(dict['vcpu']),
                ram=int(dict['memory']),
                state=dict['state'],
                persistent=dict['persistent'])

            session.add(new_vm)
            session.commit()
            session.close()
            return True

        except Exception as e:
            logger.error(str(e))
            return False

    @DatabaseHelper._sessionm
    def getVMs(self, session):
        try:
            results = session.query(Machines).all()
            if results:
                vm_list = []
                for result in results:
                    vm_data = {
                        "id": result.id,
                        "uuid": result.uuid_machine,
                        "name": result.nom,
                        "plateform": result.plateform,
                        "architecture": result.architecture,
                        "cpu": result.cpu,
                        "ram": result.ram,
                        "state": result.state,
                        "persistent": result.persistent
                    }
                    vm_list.append(vm_data)
                logger.info(vm_list)
                return vm_list
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            return None

    @DatabaseHelper._sessionm
    def getVMByName(self, session, name):
        try:
            result = session.query(Machines).filter(Machines.nom == name).first()
            if result:
                vm_data = {
                    "id": result.id,
                    "uuid": result.uuid_machine,
                    "name": result.nom,
                    "plateform": result.plateform,
                    "architecture": result.architecture,
                    "cpu": result.cpu,
                    "ram": result.ram,
                    "state": result.state,
                    "persistent": result.persistent
                }
                return vm_data
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            return None

    @DatabaseHelper._sessionm
    def deleteVM(self, session, name):
        try:
            machine = session.query(Machines).filter(Machines.nom == name).first()
            if machine:
                session.delete(machine)
                session.commit()
                session.close()
                return True
            else:
                logger.error("La machine virtuelle '%s' n'existe pas.", name)
                return False

        except Exception as e:
            logger.error(str(e))
            session.rollback()
            return False


    @DatabaseHelper._sessionm
    def setInfoGuac(self, session, dict):
        try:
            new_vm = Has_guacamole(
                idguacamole=dict['idguacamole'],
                protocol=dict['protocol'],
                port=dict['port'],
                machine_name=dict['machine_name'],
                id_machines=dict['id_machines'])

            session.add(new_vm)
            session.commit()
            session.close()
            return True

        except Exception as e:
            logger.error(str(e))
            session.rollback()
            return False

    @DatabaseHelper._sessionm
    def updateInfoGuac(self, session, dict):
        try:
            session.query(Has_guacamole).filter(Has_guacamole.id_machines == dict['id_machines']).update({
                Has_guacamole.idguacamole: dict['idguacamole'],
                Has_guacamole.protocol: dict['protocol'],
                Has_guacamole.port: dict['port'],
                Has_guacamole.machine_name: dict['machine_name']})
            session.commit()
            session.close()
            return True

        except Exception as e:
            logger.error(str(e))
            session.rollback()
            return False


    @DatabaseHelper._sessionm
    def checkExistVM(self, session, name):
        try:
            result = session.query(Machines).filter(Machines.nom == name).first()
            if result:
                return True
            else:
                return False

        except Exception as e:
            logger.error(str(e))
            return False

    @DatabaseHelper._sessionm
    def updateStatutVM(self, session, name, statut):
        try:
            session.query(Machines).filter(Machines.nom == name).update({Machines.state: statut})
            session.commit()
            session.close()
            return True

        except Exception as e:
            logger.error(str(e))
            session.rollback()
            return False

    @DatabaseHelper._sessionm
    def updateVM(self, session, dict):
        try:
            session.query(Machines).filter(Machines.nom == dict['old_name']).update({
                Machines.nom: dict['new_name'],
                Machines.uuid_machine: dict['uuid'],
                Machines.plateform: dict['plateform'],
                Machines.architecture: dict['architecture'],
                Machines.cpu: dict['vcpu'],
                Machines.ram: dict['memory'],
                Machines.state: dict['state'],
                Machines.persistent: dict['persistent']})
            session.commit()
            session.close()
            return True

        except Exception as e:
            logger.error(str(e))
            session.rollback()

    @DatabaseHelper._sessionm
    def updateRessourcesVM(self, session, dict):
        try:
            session.query(Machines).filter(Machines.nom == dict['name']).update({
                Machines.cpu: dict['cpu'],
                Machines.ram: dict['memory']})
            session.commit()
            session.close()
            return True

        except Exception as e:
            logger.error(str(e))
            session.rollback()
