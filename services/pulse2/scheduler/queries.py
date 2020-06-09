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
from sqlalchemy import not_, or_, func


from pulse2.database.msc import MscDatabase

from pulse2.database.msc.orm.commands import Commands
from pulse2.database.msc.orm.commands_on_host import CommandsOnHost, CoHManager
from pulse2.database.msc.orm.commands_on_host_phase import CommandsOnHostPhase
from pulse2.database.msc.orm.target import Target
from pulse2.database.msc.orm.pull_targets import PullTargets
from pulse2.database.msc.orm.commands_history import CommandsHistory

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
    cohs = session.query(CommandsOnHost, Target, PullTargets)
    cohs = cohs.select_from(database.commands_on_host.join(database.target).
                            outerjoin(database.pull_targets,
            Target.target_uuid == database.pull_targets.c.target_uuid))
    cohs = cohs.filter(database.commands_on_host.c.fk_commands == cmd_id)
    cohs = cohs.filter(database.commands_on_host.c.scheduler == scheduler)
    cohs = cohs.filter(database.pull_targets.c.target_uuid is None)
    cohs = cohs.filter(not_(database.commands_on_host.c.current_state.in_(("failed",
                                                                            "over_timed",
                                                                            "done",
                                                                            "stopped"))))

    commands_to_perform = [coh.id for (coh, target, pt) in cohs.all()]

    session.close()
    return commands_to_perform

def get_commands(cohs):
    database = MscDatabase()
    session = create_session()
    query = session.query(CommandsOnHost)
    query = query.filter(database.commands_on_host.c.id.in_(cohs))

    session.close()

    cmd_ids = []
    [cmd_ids.append(q.fk_commands) for q in query.all() if q.fk_commands not in cmd_ids]

    return cmd_ids


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

def any_failed(id, non_fatal_steps=[]):
    # Mutable list non_fatal_steps used as default argument to a method or function
    for phase in get_all_phases(id):
        if phase.state == "failed" and not phase.name in non_fatal_steps :
            return True
    return False


def get_ids_to_start(scheduler_name, ids_to_exclude = [], top=None):
    # Mutable list ids_to_exclude used as default argument to a method or function
    database = MscDatabase()
    session = create_session()

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    soon = time.strftime("0000-00-00 00:00:00")

    commands_query = session.query(Commands, CommandsOnHost, Target, PullTargets).\
                select_from(database.commands_on_host.join(database.commands).join(database.target).
                    outerjoin(database.pull_targets, Target.target_uuid == database.pull_targets.c.target_uuid)
        ).filter(not_(database.commands_on_host.c.current_state.in_(("failed", "over_timed", "done", "stopped")))
        ).filter(database.commands_on_host.c.next_launch_date <= now
        ).filter(or_(database.commands.c.start_date == soon,
                     database.commands.c.start_date <= now)
        ).filter(or_(database.commands.c.end_date == soon,
                     database.commands.c.end_date > now)
        ).filter(or_(database.commands_on_host.c.scheduler == '',
                     database.commands_on_host.c.scheduler == scheduler_name,
                     database.commands_on_host.c.scheduler is None)
        ).filter(database.pull_targets.c.target_uuid == None
        ).filter(database.commands.c.ready == True)
    if len(ids_to_exclude) > 0 :
        commands_query = commands_query.filter(not_(database.commands_on_host.c.id.in_(ids_to_exclude)))
    commands_query = commands_query.order_by(database.commands.c.order_in_bundle.asc(),
                                             database.commands_on_host.c.current_state.desc())
    if top :
        commands_query = commands_query.limit(top)
        # IMPORTANT NOTE : This ordering is not alphabetical!
        # Field 'current_state' is ENUM type, so decisive condition
        # is order of element in the declaration of field.
        # Because this order of elements is suitable on workflow,
        # using of descending order allows to favouring the commands
        # which state is approaching to end of worklow.

    commands = commands_query.all()
    commands_to_perform = [coh.id for (cmd, coh, target, pt) in commands if cmd.inDeploymentInterval()]
    session.close()
    return commands_to_perform

def get_pull_targets(scheduler_name, uuids):
    database = MscDatabase()
    session = create_session()

    query = session.query(PullTargets)
    query = query.select_from(database.pull_targets)
    query = query.filter(database.pull_targets.c.scheduler == scheduler_name)
    query = query.filter(database.pull_targets.c.target_uuid.in_(uuids))

    session.close()
    return query.all()

def in_pull_targets(scheduler_name, uuid):
    database = MscDatabase()
    session = create_session()

    query = session.query(PullTargets)
    query = query.select_from(database.pull_targets)
    query = query.filter(database.pull_targets.c.scheduler == scheduler_name)
    query = query.filter(database.pull_targets.c.target_uuid == uuid)

    session.close()
    if query.first() :
        return True
    else :
        return False


def __available_downloads_query(scheduler_name, uuid):
    database = MscDatabase()
    session = create_session()

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    soon = time.strftime("0000-00-00 00:00:00")

    commands_query = session.query(CommandsOnHost, Commands, Target, PullTargets).\
        select_from(database.commands_on_host.join(database.commands).join(database.target). \
                    outerjoin(database.pull_targets, Target.target_uuid == database.pull_targets.c.target_uuid)
        ).filter(not_(database.commands_on_host.c.current_state.in_(("failed", "over_timed", "done", "stopped")))
        ).filter(database.commands_on_host.c.next_launch_date <= now
        ).filter(or_(database.commands.c.start_date == soon,
                     database.commands.c.start_date <= now)
        ).filter(or_(database.commands.c.end_date == soon,
                     database.commands.c.end_date > now)
        ).filter(or_(database.commands_on_host.c.scheduler == '',
                     database.commands_on_host.c.scheduler == scheduler_name,
                     database.commands_on_host.c.scheduler is None)
        ).filter(database.target.c.target_uuid == uuid
        ).filter(database.pull_targets.c.target_uuid == uuid)
    session.close()
    return commands_query


def get_available_commands(scheduler_name, uuid):

    commands_query = __available_downloads_query(scheduler_name, uuid)

    for coh, cmd, target, pt in commands_query.all():
        if not cmd.inDeploymentInterval():
            continue
        phases = [p.name for p in get_all_phases(coh.id)]
        todo = [p.name for p in get_all_phases(coh.id) if p.state != "done"]

        yield (coh.id,
               target.mirrors,
               cmd.start_file,
               cmd.files,
               cmd.parameters,
               time.mktime(cmd.creation_date.timetuple()),
               time.mktime(cmd.start_date.timetuple()),
               time.mktime(cmd.end_date.timetuple()),
               (coh.attempts_total - coh.attempts_failed),
               phases,
               todo,
               cmd.package_id)

def pull_target_update(scheduler_name, uuid):
    database = MscDatabase()
    session = create_session()

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    query = session.query(PullTargets)
    query = query.select_from(database.pull_targets)
    query = query.filter(database.pull_targets.c.target_uuid == uuid)
    query = query.filter(database.pull_targets.c.scheduler == scheduler_name)
    pt = query.first()
    session.close()

    if not pt :
        pt = PullTargets()
        pt.target_uuid = uuid
        pt.scheduler = scheduler_name
    pt.last_seen_time = now
    pt.flush()


def machine_has_commands(scheduler_name, uuid):
    commands = __available_downloads_query(scheduler_name, uuid).all()
    return len([cmd for (coh, cmd, target) in commands if cmd.inDeploymentInterval()]) > 0

def verify_target(coh_id, hostname, mac):
    database = MscDatabase()
    session = create_session()

    query = session.query(CommandsOnHost, Target)
    query = query.select_from(database.commands_on_host.join(database.commands).join(database.target))
    query = query.filter(database.commands_on_host.c.id==coh_id)
    query = query.filter(database.target.c.target_name==hostname)
    query = query.filter(database.target.c.target_macaddr.like("%%%s%%" % mac))

    session.close()
    if query.first() :
        return True
    else :
        return False

def process_non_valid(scheduler_name, non_fatal_steps, ids_to_exclude = []):
    # Mutable list ids_to_exclude used as default argument to a method or function
    database = MscDatabase()
    session = create_session()

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    commands_query = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)
        ).filter(not_(database.commands_on_host.c.current_state.in_(("failed", "over_timed", "done")))
        ).filter(database.commands.c.end_date < now
        ).filter(or_(database.commands_on_host.c.scheduler == '',
                     database.commands_on_host.c.scheduler == scheduler_name,
                     database.commands_on_host.c.scheduler is None))

    #commands_query = commands_query.limit(top)
    if len(ids_to_exclude) > 0 :
        commands_query = commands_query.filter(not_(database.commands_on_host.c.id.in_(ids_to_exclude)))
    fls = []
    otd = []

    for q in commands_query.all():
        if any_failed(q.id, non_fatal_steps) or q.attempts_failed > 0 :
            fls.append(q.id)
        else :
            otd.append(q.id)

        #yield q.id

    session.close()

    if len(otd) > 0 :
        logging.getLogger().info("Switching %d circuits to overtimed" % len(otd))
        CoHManager.setCoHsStateOverTimed(otd)
    if len(fls) > 0 :
        logging.getLogger().info("Switching %d circuits to failed" % len(fls))
        CoHManager.setCoHsStateFailed(fls)


def get_cohs_with_failed_phase(id, phase_name):
    database = MscDatabase()
    session = create_session()

    query = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands).\
        join(database.commands_on_host_phase)
        ).filter(database.commands.c.id == id
        ).filter(database.commands_on_host_phase.c.name==phase_name
        ).filter(database.commands_on_host_phase.c.state=="failed")
    ret = [q.id for q in query.all()]
    session.close()
    return ret


def is_command_finished(scheduler_name, id):
    database = MscDatabase()
    session = create_session()

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    query = session.query(CommandsOnHost).\
        select_from(database.commands_on_host.join(database.commands)
        ).filter(not_(database.commands_on_host.c.current_state.in_(("failed", "over_timed", "done")))
        ).filter(database.commands.c.id == id
        ).filter(database.commands.c.end_date < now
        ).filter(or_(database.commands_on_host.c.scheduler == '',
                     database.commands_on_host.c.scheduler == scheduler_name,
                     database.commands_on_host.c.scheduler is None))
    nbr = query.count()
    session.close()
    if nbr > 1 :
        return False
    else :
        return True

def switch_commands_to_stop(cohs):
    CoHManager.setCoHsStateStopped(cohs)

def switch_commands_to_start(cohs):
    CoHManager.setCoHsStateScheduled(cohs)

def get_commands_stats(scheduler_name, cmd_id=None):
    database = MscDatabase()
    session = create_session()

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    query = session.query(CommandsOnHost.fk_commands,
                          CommandsOnHost.current_state,
                          func.count(CommandsOnHost.current_state))
    query = query.select_from(database.commands_on_host.join(database.commands))

    if cmd_id :
        query = query.filter(database.commands.c.id== cmd_id)
    else:
        query = query.filter(database.commands.c.end_date > now)
        query = query.filter(database.commands.c.start_date < now)

    query = query.filter(or_(database.commands_on_host.c.scheduler == '',
                     database.commands_on_host.c.scheduler == scheduler_name,
                     database.commands_on_host.c.scheduler is None))
    query = query.group_by(database.commands_on_host.c.fk_commands,
                           database.commands_on_host.c.current_state)

    ret = [q for q in query.all()]
    session.close()
    return ret

def update_commands_stats(cmd_id, stats):
    session = create_session()

    cmd = session.query(Commands).get(cmd_id)
    cmd.update_stats(session, **stats)

    session.add(cmd)
    session.flush()
    session.close()

def get_history_stdout(coh_id, phase):

    database = MscDatabase()
    session = create_session()

    query = session.query(CommandsHistory)
    query = query.select_from(database.commands_history)
    query = query.filter(database.commands_history.c.phase == phase)
    query = query.filter(database.commands_history.c.fk_commands_on_host == coh_id)

    stdout = ""
    for q in query.all():
        stdout += q.stdout

    session.close()
    return stdout
