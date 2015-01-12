# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
"""
Declare Update database
"""

import logging

#to parse html file
from lxml.html import parse
import urllib2
import cssselect

from sqlalchemy import create_engine, MetaData, func, distinct

from mmc.support.mmctools import SecurityContext
from mmc.database.database_helper import DatabaseHelper
from pulse2.managers.group import ComputerGroupManager
from mmc.plugins.dyngroup.database import DyngroupDatabase

from mmc.plugins.update.schema import OsClass, UpdateType, Update, Target, Groups,\
    STATUS_NEUTRAL, STATUS_ENABLED, STATUS_DISABLED


logger = logging.getLogger()


class updateDatabase(DatabaseHelper):

    """
    Singleton Class to query the update database.
    """
    is_activated = False

    def db_check(self):
        self.my_name = "update"
        self.configfile = "update.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        if self.is_activated:
            return None

        logger.info("UpdateMgr database is connecting")
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        # Uncomment this line to connect to mysql and parse tables
        self.is_activated = True
        logger.debug("UpdateMgr database connected")
        return self.db_check()

    def initMappers(self):
        """
        This Method is nomore need, all tables are mapped on schema.py
        """
        return

    # ========================================================================
    # >>>>>>> OS CLASSES AND UPDATE TYPES FUNCTIONS <<<<<<<<<<<<<<<<<<<<<<<<<
    # ========================================================================

    @DatabaseHelper._listinfo
    @DatabaseHelper._session
    def get_os_classes(self, session, params):
        """
        Get all os classes
        """
        return session.query(OsClass)

    @DatabaseHelper._session
    def enable_only_os_classes(self, session, os_classes_ids):
        """
        Enable spacified os_classes and disble others
        """
        try:
            session.query(OsClass)\
                .filter(OsClass.id.in_(os_classes_ids))\
                .update({'enabled': 1}, synchronize_session=False)
            session.query(OsClass)\
                .filter(~OsClass.id.in_(os_classes_ids))\
                .update({'enabled': 0}, synchronize_session=False)
            session.commit()
            return True
        except Exception as e:
            logger.error("DB Error: %s" % str(e))
            return False

    @DatabaseHelper._listinfo
    @DatabaseHelper._session
    def get_update_types(self, session, params):
        """
        Get all update types
        """
        return session.query(UpdateType)

    @DatabaseHelper._session
    def set_update_type_status(self, session, update_type_id, status):
        """
        Set the update type status
        """
        try:
            session.query(UpdateType).get(update_type_id).status = status
            session.commit()
            return True

        except Exception as e:
            logger.error("DB Error: %s" % str(e))
            return False

    # ========================================================================
    # >>>>>>> GENERAL UPDATE FUNCTIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # ========================================================================

    @DatabaseHelper._session
    def push_updates(self, session, uuid, updates):
        """
        This function Adds updates in updates table
        and link them to the specified uuid
        updates: list of {
            name: , guid : , os_class_id , type_id , status [optional]
        }
        """
        try:
            for upd in updates:
                update = session.query(Update).filter_by(*upd).all()

                if len(update) > 1:
                    logger.warning(
                        'Duplicate enties found, please check that you havent updates with same name AND guid')

                # if no same update found in db, we create it
                if len(update) == 0:
                    update = Update()
                    update.fromDict(upd)
                    session.add(update)
                    session.flush()
                else:
                    update = update[0]  # else we take the existing one

                # Adding current target
                update.targets.append(Target(uuid=uuid))

            session.commit()
            # session.flush()
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    @DatabaseHelper._session
    def add_update_description(self,session):
        """
        Add update descriptions from windows kb base.
        """
        logger.debug("get updates description from windows kb base...")
        try:
            query = session.query(Update.kb_number).filter(Update.description=="").all()
            kb_numbers = [r for r, in query]
            for kb_number in kb_numbers:
                link = "http://support.microsoft.com/kb/"+kb_number
                doc = parse(link).getroot()
                if doc is not None :
                    try:
                       title=doc.cssselect('#mt_title')[0]
                    except Exception as e:
                        title=None
                if title is not None:
                    description=unicode(title.text_content())
                    for update in session.query(Update).filter(Update.kb_number==kb_number).all():
                        update.description=description
                    session.commit()
            logger.debug("updates description added.")
            return True
        except Exception as e:
            logger.debug("failed to add update descriptions.")
            logger.error(str(e))
            return False

    @DatabaseHelper._session
    def get_machines(self, session):
        """
        Get list of id of machines who send informations to update databases
        """
        query = session.query(distinct(Target.uuid))
        result = [r for r, in query]
        return result

    @DatabaseHelper._listinfo
    @DatabaseHelper._session
    def get_updates(self, session, params):
        """
        Get all updates by the specified filters
        Status filter is specially treaten
        in this order of priority: Update -> Update Type
        """
        try:
            # Defining subqueries
            installed_targets = session.query(
                Target.update_id, func.sum(
                    Target.is_installed).label('total_installed')).group_by(
                Target.update_id).subquery()
            all_targets = session.query(Target.update_id, func.count(
                '*').label('total_targets')).group_by(Target.update_id).subquery()

            # Main query
            query = session.query(Update, func.ifnull(installed_targets.c.total_installed, 0).label('total_installed'), func.ifnull(all_targets.c.total_targets, 0).label('total_targets'))\
                .join(Update.update_type)\
                .outerjoin(installed_targets, Update.id == installed_targets.c.update_id)\
                .outerjoin(all_targets, Update.id == all_targets.c.update_id)

            # ==== STATUS FILTERING ======================
            if 'filters' in params and 'status' in params['filters']:
                # Special filter treatment for status
                Status = int(params['filters']['status'])
                del params['filters']['status']

                # other non-confusing filters
                # are automatically treaten by @DatabaseHelper._listinfo
                if 'hide_installed_update' in params :
                    if  params['hide_installed_update']:
                        query=query.filter(installed_targets.c.total_installed == 0)

                if Status == STATUS_NEUTRAL:
                    # Neutral status
                    query = query.filter(
                        (Update.status == Status) &
                        (UpdateType.status == Status)
                    )
                else:
                    # Dominant status
                    query = query.filter(
                        (Update.status == Status) |
                        (
                            (Update.status == STATUS_NEUTRAL) &
                            (UpdateType.status == Status)
                        )
                    )
            #
            # ==== END STATUS FILTERING ==================

            return query
        except Exception as e:
            logger.error("DB Error: %s" % str(e))
            return False

    @DatabaseHelper._session
    def set_update_status(self, session, update_id, status):
        """
        Set the global update status
        """
        if not isinstance(update_id, list):
            update_id = [update_id]
        try:
            session.query(Update).filter(Update.id.in_(update_id)).update(
                {'status': status}, synchronize_session=False)
            session.commit()
            return True

        except Exception as e:
            logger.error("DB Error: %s" % str(e))
            return False

    # ========================================================================
    # >>>>>>> UPDATE FOR HOSTS FUNCTIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # ========================================================================

    @DatabaseHelper._listinfo
    @DatabaseHelper._session
    def get_updates_for_group(self, session, params):
        """
        Get all updates for a group of hosts by the specified filters,
        like get_updates function.
        Status filter is specially treaten.
        in this order of priority:
        Groups -> Update -> Update Type
        """
        if 'gid' in params:
            gid = params['gid']

        if 'uuids' in params:
            uuids = params['uuids']
        else:
            uuids = []

        if 'is_install' in params:
            is_installed = params['is_installed']
        else:
            is_installed = None

        if 'filters' in params and 'status' in params['filters']:
            dStatus = int(params['filters']['status'])
            del params['filters']['status']
        else:
            dStatus = STATUS_NEUTRAL

        try:
            # Defining subqueries

            installed_targets = session.query(
                Target.update_id,
                func.sum(Target.is_installed).label('total_installed')
            )
            # count only group machines
            installed_targets = installed_targets.filter(
                Target.uuid.in_(uuids))
            installed_targets = installed_targets.group_by(Target.update_id)
            installed_targets = installed_targets.subquery()

            all_targets = session.query(
                Target.update_id,
                func.count('*').label('total_targets')
            )
            # count only group machines
            all_targets = all_targets.filter(Target.uuid.in_(uuids))
            all_targets = all_targets.group_by(Target.update_id).subquery()

            group = session.query(Groups).filter(Groups.gid == gid).subquery()

            query = session.query(
                Update,
                func.ifnull(
                    installed_targets.c.total_installed,
                    0).label('total_installed'),
                func.ifnull(
                    all_targets.c.total_targets,
                    0).label('total_targets'),
                func.ifnull(
                    group.c.gid,
                    gid).label('gid'),
                func.ifnull(
                    group.c.status,
                    0).label('group_status'),
            )
            query = query.join(Target)
            query = query.join(UpdateType)
            # filter on the group of hosts
            query = query.filter(Target.uuid.in_(uuids))
            # add subqueries
            query = query.outerjoin(
                installed_targets,
                Update.id == installed_targets.c.update_id)
            query = query.outerjoin(
                all_targets,
                Update.id == all_targets.c.update_id)
            query = query.outerjoin(
                group,
                Update.id == group.c.update_id)

            if is_installed is not None:
                query = query.filter(Target.is_installed == is_installed)

            # ============================================
            # ==== STATUS FILTERING ======================
            # ============================================
            if 'hide_installed_update' in params :
                if  params['hide_installed_update']:
                    query=query.filter(installed_targets.c.total_installed == 0)

            if dStatus ==  STATUS_NEUTRAL:
                query = query.filter((group.c.status == None) |
                                     (group.c.status == STATUS_NEUTRAL))
                query = query.filter(Update.status == STATUS_NEUTRAL)
                query = query.filter(UpdateType.status == STATUS_NEUTRAL)
            else:
                query = query.filter(
                    # 1st level filtering : Group status
                    (group.c.status == dStatus) |
                    (
                        (
                            (group.c.status == None) |
                            (group.c.status == STATUS_NEUTRAL)
                        ) &
                        (
                            # 2nd level filtering : Update status
                            (Update.status == dStatus) |
                            (
                                (Update.status == STATUS_NEUTRAL) &
                                (UpdateType.status == dStatus)
                            )
                        )
                    )
                )
            # ============================================
            # ==== END STATUS FILTERING ==================
            # ============================================
            return query
        except Exception as e:
            logger.error("DB Error: %s" % str(e))
            return False

    @DatabaseHelper._session
    def get_updates_for_host_by_dominant_status(
            self,
            session,
            uuid,
            dStatus,
            is_installed=None):
        """
        Get all update to install for host,
        this function return all updates for the host
        if the update have the Status (STATUS_ENABLED or STATUS_DISABLED, STATUS_NEUTRAL)
        in this order of priority:
        Target -> Groups -> Update -> Update Type
        """

        if dStatus == STATUS_NEUTRAL:
            logger.error(
                "Neutral status is not accepted, use get_neutral_updates function instead")
            return False
        # Get group list
        gid = self._get_machine_groups(uuid)
        try:
            # Defining group subquery
            group = session.query(
                Groups.update_id,
                # we choose the max because STATUS_DISABLED>STATUS_ENABLED
                # and STATUS_ENABLED>STATUS_NEUTRAL
                # So if disable and enable at the same time, disable win
                func.max(Groups.status).label('status')
            )
            if gid:
                group = group.filter(Groups.gid.in_(gid))
            # if no group, we need an empty list
            else:
                group = group.filter(Groups.gid == None)
            group = group.group_by(Groups.update_id)
            group = group.subquery()
            # Main query
            query = session.query(
                Target)
            query = query.add_entity(Update).join(Update).join(UpdateType)
            query = query.filter(Target.uuid == uuid)
            query = query.outerjoin(
                group,
                Update.id == group.c.update_id)

            if is_installed is not None:
                query = query.filter(Target.is_installed == is_installed)

            # ============================================
            # ==== STATUS FILTERING ======================
            # ============================================
            query = query.filter(
                # 1st level filtering : Target status
                (Target.status == dStatus) |
                (
                    (Target.status == STATUS_NEUTRAL) &
                    (
                        # 2nd level filtering : Group status
                        (group.c.status == dStatus) |
                        (
                            (
                                (group.c.status == None) |
                                (group.c.status == STATUS_NEUTRAL)
                            ) &
                            (
                                # 3rd level filtering : Update status
                                (Update.status == dStatus) |
                                (
                                    (Update.status == STATUS_NEUTRAL) &
                                    (UpdateType.status == dStatus)
                                )
                            )
                        )
                    )
                )
            )
            # ============================================
            # ==== END STATUS FILTERING ==================
            # ============================================

            result = []

            for (target, update) in query:
                result.append(update.toDict())
            return result
        except Exception as e:
            logger.error("DB Error: %s" % str(e))
            return False

    def printquery(self, statement, bind=None):
        """
        print a query, with values filled in
        for debugging purposes *only*
        for security, you should always separate queries from their values
        please also note that this function is quite slow
        """
        import sqlalchemy.orm
        if isinstance(statement, sqlalchemy.orm.Query):
            if bind is None:
                bind = statement.session.get_bind(
                    statement._mapper_zero_or_none()
                )
            statement = statement.statement
        elif bind is None:
            bind = statement.bind

        dialect = bind.dialect
        compiler = statement._compiler(dialect)

        class LiteralCompiler(compiler.__class__):

            def visit_bindparam(
                    self, bindparam, within_columns_clause=False,
                    literal_binds=False, **kwargs
            ):
                return super(LiteralCompiler, self).render_literal_bindparam(
                    bindparam, within_columns_clause=within_columns_clause,
                    literal_binds=literal_binds, **kwargs
                )

        compiler = LiteralCompiler(dialect, statement)
        print compiler.process(statement)

    @DatabaseHelper._session
    def get_eligible_updates_for_host(self, session, uuid):
        """
        Get all update to install for host,
        this function return all eligible updates for the host
        in this order of priority: Target -> Groups -> Update -> Update Type
        """
        return self.get_updates_for_host_by_dominant_status(
            uuid,
            STATUS_ENABLED,
            0)

    @DatabaseHelper._session
    def get_disabled_updates_for_host(self, session, uuid):
        """
        Get all update to install for host,
        this function return all eligible updates for the host
        in this order of priority: Target -> Groups -> Update -> Update Type
        """
        return self.get_updates_for_host_by_dominant_status(
            uuid,
            STATUS_DISABLED)

    @DatabaseHelper._session
    def get_neutral_updates_for_host(self, session, uuid):
        """
        Get all update to install for host,
        this function return all neutral upd
        in this order of priority: Target -> Groups -> Update -> Update Type
        """
        # Update is neutral (for host), if all levels status
        # are neutral

        # Get group list
        gid = self._get_machine_groups(uuid)
        try:
            # Defining group subquery
            group = session.query(
                Groups.update_id,
                # we choose the max because STATUS_DISABLED>STATUS_ENABLED
                # and STATUS_ENABLED>STATUS_NEUTRAL
                # So if disable and enable at the same time, disable win
                func.max(Groups.status).label('status')
            )
            if gid:
                group = group.filter(Groups.gid.in_(gid))
            # if no group, we need an empty list
            else:
                group = group.filter(Groups.gid == None)
            group = group.group_by(Groups.update_id)
            group = group.subquery()

            query = session.query(Target)\
                .add_entity(Update).join(Update)\
                .join(UpdateType)\
                .outerjoin(group, Update.id == group.c.update_id)\
                .filter((group.c.status == None) | (group.c.status == STATUS_NEUTRAL))\
                .filter(Target.uuid == uuid)\
                .filter(Target.status == STATUS_NEUTRAL)\
                .filter(Update.status == STATUS_NEUTRAL)\
                .filter(UpdateType.status == STATUS_NEUTRAL)

            result = []

            for (target, update) in query:
                result.append(update.toDict())

            return result

        except Exception as e:
            logger.error("DB Error: %s" % str(e))
            return False

    @DatabaseHelper._session
    def set_update_status_for_group(self, session, gid, update_id, status):
        """
        Set the update status for the group only
        (global update status and target status remain unchanged)
        """
        try:
            query = session.query(Groups)\
                .filter(Groups.gid == gid, Groups.update_id == update_id)
            update = query.all()
            # if this update not available,add it
            if len(update) == 0:
                update = Groups(update_id=update_id, gid=gid, status=status)
                session.add(update)
                session.flush()
            # else update it
            else:
                query.update({'status': status}, synchronize_session=False)
            session.commit()
            return True

        except Exception as e:
            logger.error(str(e))
            return False

    def _get_machine_groups(self, uuid):
        """
        Get groups of one machine with is uuid as number"
        """
        # Creating root context
        ctx = SecurityContext()
        ctx.userid = 'root'
        group_list = []
        groups = DyngroupDatabase().getallgroups(ctx, {})
        groups = map(lambda g: g.toH(), groups)
        for group in groups:
            if 'id' in group:
                result = ComputerGroupManager().get_group_results(
                    ctx, group['id'], 0, -1, {})
                if "UUID" + str(uuid) in result:
                    group_list.append(group['id'])
        return group_list

    @DatabaseHelper._session
    def get_update_conflicts_for_host(self, session, uuid):
        groups = self._get_machine_groups(uuid)
        logger.info(groups)
        try:
            updates = session.query(Groups.update_id)
            updates = updates.filter(Groups.gid.in_(groups))

            activated_update = updates.filter(Groups.status == STATUS_ENABLED)
            activated_update = activated_update.subquery()

            disabled_update = updates.filter(Groups.status == STATUS_DISABLED)
            disabled_update = disabled_update.subquery()

            query = session.query(Groups).filter(
                Groups.update_id.in_(activated_update))
            query = query.filter(Groups.gid.in_(groups))
            query = query.filter(Groups.update_id.in_(disabled_update))

            result = []
            for (update) in query:
                result.append(update.toDict())
            return result
        except Exception as e:
            logger.error(str(e))
            return False
