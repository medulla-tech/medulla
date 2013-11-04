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
import logging
import time

from sqlalchemy.orm import create_session
from sqlalchemy import not_, or_ 


from pulse2.database.msc import MscDatabase

from pulse2.database.msc.orm.commands import Commands
from pulse2.database.msc.orm.commands_on_host import CommandsOnHost
from pulse2.database.msc.orm.commands_on_host_phase import CommandsOnHostPhase
from pulse2.database.msc.orm.target import Target



log = logging.getLogger()

class MscQuerySession :
    """

    """

    def __init__(self, cls, id):
        """
        @param cls: Queried table
        @type cls: SqlAlchemy table

        @param id: table id
        @type id: int
        """
        self._cls = cls
        self._id = id

    def __enter__(self):
        self._session = create_session()
        self._session.expire_on_commit = False

        self.query = self._session.query(self._cls).get(self._id)
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._session.close()

#TODO - these classes are simply 'object' instances 
#       instead of Table SqlAlchemy object
MSC_TABLES = [CommandsOnHost, Commands, Target]

class Refresh (object):
    """
    A common extender to add refresh() method to SqlAlchemy Table object.

    This class must be instantiated as first before SqlAlchemy table class.
   
    """
    _id = None

    def __init__(self, id):
        """
        Common constructor to initialize both classes.

        @param id: table id
        @type id: int
        """
        self._id = id

        # a little hack to avoid initialize of each table instance :
        # - get the sqlalchemy table subclass by method resolution order
        # - initialize it
        self._cls = self.__class__.__mro__[2]

        # TODO (see MSC_TABLES declaration)
        # because all msc tables are simply 'object' instance,
        # we don't approve a true orgin of class
        for table in MSC_TABLES :
            if issubclass(self._cls, table):
                break
        else :
            raise TypeError("Not a msc table")

        self._cls.__init__(self)


    def refresh(self):
        """ my-self overriding by actualised query object """
        self = self.get()

    def get(self):
        """
        Querying of inherited table object.

        @return: fetched-one SqlAlchemy Table record
        @rtype: object
        """
        with MscQuerySession(self._cls, self._id) as q:
            result = q.query
            setattr(result, "refresh", self.refresh)
            return result


def get_cohs(cmd_id, scheduler):
    database = MscDatabase()
    session = create_session()
    cohs = session.query(CommandsOnHost)
    cohs = cohs.filter(database.commands_on_host.c.fk_commands == cmd_id)
    cohs = cohs.filter(database.commands_on_host.c.scheduler == scheduler)
    
    session.close()
    return [q.id for q in cohs.all()]

def get_phases(id):
    database = MscDatabase()
    session = create_session()
    cohs = session.query(CommandsOnHostPhase)
    cohs = cohs.filter(database.commands_on_host_phase.c.fk_commands_on_host == id)
    
    session.close()
    return cohs.all()


def is_command_in_valid_time(cmd_id):
    session = create_session()
    cmd = session.query(Commands).get(cmd_id)
    session.close()
    if isinstance(cmd, Commands):
        return cmd.in_valid_time()
    return False


class RefreshedCommandsOnHost(Refresh, CommandsOnHost): pass
class RefreshedCommands(Refresh, Commands): pass
class RefreshedTarget(Refresh, Target): pass


class CoHQuery :
    """
    Container keeping CommandsOnHost, Commands and Target records.

    Based on CommandsOnHost id, all related records are initialised 
    by constructor and still in memory.
    All records are accessibles as properties having a refresh() method
    to re-query...
    """
    def __init__(self, id):
        """
        @param id: CommandsOnHost id
        @type id: int
        """
        self._id = id

        # initial queries
        self._coh = RefreshedCommandsOnHost(self._id).get()
        self._cmd = RefreshedCommands(self._coh.getIdCommand()).get()
        self._target = RefreshedTarget(self._coh.getIdTarget()).get()

    def get_phase(self, name):
        database = MscDatabase()
        session = create_session()
        phase = session.query(CommandsOnHostPhase)
        phase = phase.filter(database.commands_on_host_phase.c.fk_commands_on_host == self._id)
        phase = phase.filter(database.commands_on_host_phase.c.name == name)
        #phase = phase.all()
        phase = phase.first()
        session.close()
        if isinstance(phase, list):
            return phase[0]
        else :
            return phase

    def get_phases(self):
        database = MscDatabase()
        session = create_session()
        phases = session.query(CommandsOnHostPhase)
        phases = phases.filter(database.commands_on_host_phase.c.fk_commands_on_host == self._id)
        phases = phases.filter(database.commands_on_host_phase.c.state != "done")
        session.close()
        return [q.name for q in phases.all()]

    def get_all_phases(self):
        database = MscDatabase()
        session = create_session()
        phases = session.query(CommandsOnHostPhase)
        phases = phases.filter(database.commands_on_host_phase.c.fk_commands_on_host == self._id)
        session.close()
        return phases.all()

    def get_starting_phase(self):
        database = MscDatabase()
        session = create_session()
        phases = session.query(CommandsOnHostPhase)
        phases = phases.filter(database.commands_on_host_phase.c.fk_commands_on_host == self._id)
        phases = phases.filter(database.commands_on_host_phase.c.state != "done")
        phases = phases.order_by(database.commands_on_host_phase.c.phase_order)
        session.close()
        for phase in phases.all():
            if phase.state in ("ready","running", "failed"):
                return phase.name
        else :
            return None


    @property
    def coh(self):
        """
        CommandsOnHost table record.

        @return: CommandsOnHost instance extended by refresh() method
        @rtype: SqlAlchemy qyery object
        """
        return self._coh

    @property
    def cmd(self):
        """
        Commands table record.

        @return: Commands instance extended by refresh() method
        @rtype: SqlAlchemy qyery object
        """
        return self._cmd

    @property
    def target(self):
        """
        Target record.

        @return: Target instance extended by refresh() method
        @rtype: SqlAlchemy qyery object
        """
        return self._target

def get_all_phases(id):
    database = MscDatabase()
    session = create_session()
    phases = session.query(CommandsOnHostPhase)
    phases = phases.filter(database.commands_on_host_phase.c.fk_commands_on_host == id)
    session.close()
    return phases.all()

def any_failed(id):
    for phase in get_all_phases(id):
        if phase.state == "failed":
            return True
    return False


def get_ids_to_start(scheduler_name, ids_to_exclude = [], top=None):
    database = MscDatabase()
    session = create_session()
  
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    soon = time.strftime("0000-00-00 00:00:00")

    commands_query = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)
        ).filter(not_(database.commands_on_host.c.current_state.in_(("failed", "over_timed", "done")))
        ).filter(database.commands_on_host.c.attempts_left > database.commands_on_host.c.attempts_failed
        ).filter(database.commands_on_host.c.next_launch_date <= now
        ).filter(or_(database.commands.c.start_date == soon,
                     database.commands.c.start_date <= now)
        ).filter(or_(database.commands.c.end_date == soon,
                     database.commands.c.end_date > now)
        ).filter(or_(database.commands_on_host.c.scheduler == '',
                     database.commands_on_host.c.scheduler == scheduler_name,
                     database.commands_on_host.c.scheduler == None))
    if len(ids_to_exclude) > 0 :
        commands_query = commands_query.filter(not_(database.commands_on_host.c.id.in_(ids_to_exclude)))
    commands_query = commands_query.order_by(database.commands_on_host.c.current_state.desc())
    if top :
        commands_query = commands_query.limit(top)
        # IMPORTANT NOTE : This ordering is not alphabetical!
        # Field 'current_state' is ENUM type, so decisive condition
        # is order of element in the declaration of field.
        # Because this order of elements is suitable on workflow, 
        # using of descending order allows to favouring the commands
        # which state is approaching to end of worklow.


    commands_to_perform = [q.id for q in commands_query.all()]

    session.close()
    return commands_to_perform

def process_non_valid(scheduler_name, ids_to_exclude = []):
    database = MscDatabase()
    session = create_session()
  
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    commands_query = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)
        ).filter(not_(database.commands_on_host.c.current_state.in_(("failed", "over_timed", "done")))
        ).filter(database.commands.c.end_date < now
        ).filter(or_(database.commands_on_host.c.scheduler == '',
                     database.commands_on_host.c.scheduler == scheduler_name,
                     database.commands_on_host.c.scheduler == None))
    if len(ids_to_exclude) > 0 :
        commands_query = commands_query.filter(not_(database.commands_on_host.c.id.in_(ids_to_exclude)))

    for q in commands_query.all():
        cohq = CoHQuery(q.id)
        if any_failed(q.id) or q.attempts_failed > 0 :
            logging.getLogger().info("Circuit #%s: Switched to failed" % q.id)
            cohq.coh.setStateFailed()
        else :
            logging.getLogger().info("Circuit #%s: Switched to overtimed" % q.id)
            cohq.coh.setStateOverTimed()
        yield q.id

    session.close()


