# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
BackupPC report database handler
"""

import logging
from datetime import timedelta

from pulse2.database.backuppc import BackuppcDatabase, Hosts, Backup_servers
from mmc.plugins.backuppc.bpc import get_global_status
from mmc.plugins.base import ComputerManager
from sqlalchemy import (create_engine, MetaData, Table, Integer, Column,
                        DateTime, and_, ForeignKey, String)
from sqlalchemy.orm import create_session, mapper, relationship

class ReportDatabase(BackuppcDatabase):
    """
    Singleton Class to query the report database.
    """
    is_activated = False

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("BackupPC Report database is connecting")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        # Uncomment this line to connect to mysql and parse tables
        #self.metadata.create_all()
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("BackupPC Report database connected")
        return True

    def initMappers(self):
        # ReportServerUsedDiscSpace
        self.report_server_used_disc_space = Table("report_server_used_disc_space", self.metadata,
                                Column('id', Integer, primary_key = True),
                                Column('timestamp', DateTime),
                                Column('used', Integer),
                                Column('free', Integer),
                                Column('backup_server_id', Integer, ForeignKey(Backup_servers.id)),
                                mysql_engine='InnoDB'
                                )
        mapper(ReportServerUsedDiscSpace, self.report_server_used_disc_space)

        # ReportUsedDiscSpacePerMachine
        self.report_used_disc_space_per_machine = Table("report_used_disc_space_per_machine", self.metadata,
                                Column('id', Integer, primary_key = True),
                                Column('timestamp', DateTime),
                                Column('used_disc_space', Integer),
                                Column('host_id', Integer, ForeignKey(Hosts.id)),
                                mysql_engine='InnoDB'
                                )
        mapper(ReportUsedDiscSpacePerMachine, self.report_used_disc_space_per_machine)#, properties={
        #    'hostss': relationship(Hosts),
        #})

    def feed_db(self):
        logging.getLogger().debug('Successfully feeded BackupPC report database')
        logging.getLogger().error(self.get_backup_profiles())
        return True

    #################
    ## Report Methods
    #################

    def get_backuppc_server_disc_space(self, from_timestamp, to_timestamp, splitter, entities):
        delta = to_timestamp - from_timestamp
        if delta.days < splitter:
            step = 1
        else:
            step = delta.days / splitter

        session = create_session()
        query = session.query(ReportServerUsedDiscSpace)
        query = query.filter(and_(
            ReportServerUsedDiscSpace.timestamp >= from_timestamp,
            ReportServerUsedDiscSpace.timestamp <= to_timestamp + timedelta(1),
            ReportServerUsedDiscSpace.backup_server_id.in_(entities),
        ))
        session.close()

        l = {}
        for x in query.all():
            if not x.backup_server_id in l:
                l[x.backup_server_id] = [(x.timestamp.strftime('%s'), x.used, x.free)]
            else:
                l[x.backup_server_id].append((x.timestamp.strftime('%s'), x.used, x.free))

        res = {}
        for entity in l:
            res[str(entity)] = {'titles': ['Used', 'Free']}
            for x in xrange(0, len(l[entity]), step):
                res[str(entity)][l[entity][x][0]] = [l[entity][x][1], l[entity][x][2]]

        return res

    def get_backuppc_used_disc_space_per_machine(self, from_timestamp, to_timestamp, splitter, entities, kargs):
        ctx = kargs['ctx']
        critical_limit = int(kargs['critical_limit'])
        critical_unit = kargs['critical_limit_unit']
        if critical_unit == 'Mo':
            critical_limit = critical_limit / 1000.0

        display_all_machines = kargs['display_all_machines']

        delta = to_timestamp - from_timestamp
        if delta.days < splitter:
            step = 1
        else:
            step = delta.days / splitter

        # get all hosts who are part of selected entities
        # hosts_per_entity = {
        #   entity_id: [list_of_hosts],
        # }

        hosts_per_entity = {}
        for entity in entities:
            # Get hosts of current entity
            hosts_per_entity[entity] = get_global_status('UUID' + str(entity))['data']['hosts']
            # Full size in BackupPC is in GB
            #full_size = get_global_status('UUID' + str(entity))['data']['full_size']

        # Get used disc space per machine
        all_hosts = sum([hosts_per_entity[x] for x in hosts_per_entity], [])

        session = create_session()
        query = session.query(
            ReportUsedDiscSpacePerMachine.timestamp,
            ReportUsedDiscSpacePerMachine.used_disc_space,
            Hosts.uuid
        ).join(Hosts)

        query = query.filter(and_(
            ReportUsedDiscSpacePerMachine.timestamp >= from_timestamp,
            ReportUsedDiscSpacePerMachine.timestamp <= to_timestamp + timedelta(1),
            Hosts.uuid.in_(all_hosts),
        ))
        session.close()

        qresult = {}
        dates = []
        uuids = []
        for timestamp, value, uuid in query.all():
            date = timestamp.strftime('%s')
            dates.append(date)
            if not uuid in uuids:
                if display_all_machines:
                    uuids.append(uuid)
                elif value > critical_limit:
                    uuids.append(uuid)

            if not date in qresult:
                qresult[date] = {}
            qresult[date][uuid] = value

        computers_list = ComputerManager().getComputersList(ctx, {'uuids': uuids})
        def get_computer_name(uuid):
            if uuid in computers_list:
                return computers_list[uuid][1]['cn'][0]
            else:
                self.logger.warn("BackupPC ReportDatabase: I can't find name of machine %s" % uuid)
                return uuid

        res = {}
        for entity in hosts_per_entity:
            res[str(entity)] = {'titles': [get_computer_name(uuid) for uuid in uuids]}
            entity = str(entity)
            for x in xrange(0, len(dates), step):
                values = []
                for uuid in uuids:
                    values.append(qresult[dates[x]][uuid])
                res[entity][dates[x]] = values

        return res

# Tables classes

class ReportServerUsedDiscSpace(object):
    pass

class ReportUsedDiscSpacePerMachine(object):
    pass
