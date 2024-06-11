# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Provides access to Pkgs database
"""
# standard modules
import traceback

# SqlAlchemy
from sqlalchemy import (
    and_,
    create_engine,
    MetaData,
    Table,
    asc,
    desc,
    func,
    distinct,
)
from sqlalchemy.orm import create_session, mapper
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.ext.automap import automap_base

import datetime
import magic
import base64

# ORM mappings
from pulse2.database.pkgs.orm.pakages import Packages
from pulse2.database.pkgs.orm.extensions import Extensions
from pulse2.database.pkgs.orm.dependencies import Dependencies
from pulse2.database.pkgs.orm.syncthingsync import Syncthingsync
from pulse2.database.pkgs.orm.package_pending_exclusions import (
    Package_pending_exclusions,
)

from pulse2.database.pkgs.orm.pkgs_rules_algos import Pkgs_rules_algos
from pulse2.database.pkgs.orm.pkgs_rules_global import Pkgs_rules_global
from pulse2.database.pkgs.orm.pkgs_rules_local import Pkgs_rules_local
from pulse2.database.pkgs.orm.pkgs_shares_ars import Pkgs_shares_ars
from pulse2.database.pkgs.orm.pkgs_shares_ars_web import Pkgs_shares_ars_web
from pulse2.database.pkgs.orm.pkgs_shares import Pkgs_shares


from mmc.database.database_helper import DatabaseHelper
from pulse2.database.xmppmaster import XmppMasterDatabase

# Pulse 2 stuff
# from pulse2.managers.location import ComputerLocationManager
# Imported last
import logging
import os
import json

logger = logging.getLogger()


NB_DB_CONN_TRY = 2

# TODO need to check for useless function (there should be many unused one...)


class PkgsDatabase(DatabaseHelper):
    """
    Singleton Class to query the Pkgs database.

    """

    def db_check(self):
        self.my_name = "pkgs"
        self.configfile = "pkgs.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None
        self.logger.info("Pkgs database is connecting")
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
            pool_timeout=self.config.dbpooltimeout,
            convert_unicode=True,
        )
        self.logger.info(
            "parameters connection pkgs from mmc :  pool_recycle  %s"
            " pool_size %s pool_timeout %s"
            % (
                self.config.dbpoolrecycle,
                self.config.dbpoolsize,
                self.config.dbpooltimeout,
            )
        )
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)

        Base = automap_base()
        Base.prepare(self.db, reflect=True)

        # Only federated tables (beginning by local_) are automatically mapped
        # If needed, excludes tables from this list
        exclude_table = []
        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in Base.classes.items():
            if table_name in exclude_table:
                continue
            if table_name.startswith("local"):
                setattr(self, table_name.capitalize(), mapped_class)

        if not self.initTables():
            return False
        if not self.initMappersCatchException():
            return False
        self.metadata.create_all()
        # FIXME: should be removed
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("Pkgs database connected")
        return True

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """
        try:
            # packages
            self.package = Table("packages", self.metadata, autoload=True)

            # extensions
            self.extensions = Table("extensions", self.metadata, autoload=True)

            # Dependencies
            self.dependencies = Table("dependencies", self.metadata, autoload=True)

            # Syncthingsync
            self.syncthingsync = Table("syncthingsync", self.metadata, autoload=True)
            # package_pending_exclusions
            self.package_pending_exclusions = Table(
                "package_pending_exclusions", self.metadata, autoload=True
            )
            # pkgs_shares_ars_web
            self.pkgs_shares_ars_web = Table(
                "pkgs_shares_ars_web", self.metadata, autoload=True
            )

            # pkgs_shares_ars
            self.pkgs_shares_ars = Table(
                "pkgs_shares_ars", self.metadata, autoload=True
            )

            # pkgs_shares
            self.pkgs_shares = Table("pkgs_shares", self.metadata, autoload=True)

            # pkgs_rules_algos
            self.pkgs_rules_algos = Table(
                "pkgs_rules_algos", self.metadata, autoload=True
            )

            # pkgs_rules_global
            self.pkgs_rules_global = Table(
                "pkgs_rules_global", self.metadata, autoload=True
            )

            # pkgs_rules_local
            self.pkgs_rules_local = Table(
                "pkgs_rules_local", self.metadata, autoload=True
            )
        except NoSuchTableError as e:
            self.logger.error(
                "Cant load the Pkgs database : table '%s' does not exists"
                % (str(e.args[0]))
            )
            return False
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the Pkgs database
        """
        mapper(Packages, self.package)
        mapper(Extensions, self.extensions)
        mapper(Dependencies, self.dependencies)
        mapper(Syncthingsync, self.syncthingsync)
        mapper(Package_pending_exclusions, self.package_pending_exclusions)
        mapper(Pkgs_shares, self.pkgs_shares)
        mapper(Pkgs_shares_ars, self.pkgs_shares_ars)
        mapper(Pkgs_shares_ars_web, self.pkgs_shares_ars_web)
        mapper(Pkgs_rules_algos, self.pkgs_rules_algos)
        mapper(Pkgs_rules_global, self.pkgs_rules_global)
        mapper(Pkgs_rules_local, self.pkgs_rules_local)

    ####################################

    @DatabaseHelper._sessionm
    def createPackage(self, session, package, pkgs_share_id=None, edition_status=1):
        """
        Insert the package config into database.
        Param:
            session: The SQLAlchemy session
            package : dict of the historical config of the package
            pkgs_share_id:
            edition_status:
        Returns:
            It returns the new package format
        """

        request = session.query(Packages).filter(Packages.uuid == package["id"]).first()

        if request is None:
            new_package = Packages()
        else:
            new_package = request

        new_package.label = package["name"]
        new_package.uuid = package["id"]
        new_package.description = package["description"]
        new_package.version = package["version"]
        new_package.os = package["targetos"]
        new_package.metagenerator = package["metagenerator"]
        new_package.entity_id = package["entity_id"]
        if isinstance(package["sub_packages"], str):
            new_package.sub_packages = package["sub_packages"]
        elif isinstance(package["sub_packages"], list):
            new_package.sub_packages = ",".join(package["sub_packages"])
        new_package.reboot = package["reboot"]
        new_package.inventory_associateinventory = package["inventory"][
            "associateinventory"
        ]
        new_package.inventory_licenses = package["inventory"]["licenses"]
        new_package.Qversion = package["inventory"]["queries"]["Qversion"]
        new_package.Qvendor = package["inventory"]["queries"]["Qvendor"]
        new_package.Qsoftware = package["inventory"]["queries"]["Qsoftware"]
        new_package.boolcnd = package["inventory"]["queries"]["boolcnd"]
        new_package.postCommandSuccess_command = package["commands"][
            "postCommandSuccess"
        ]["command"]
        new_package.postCommandSuccess_name = package["commands"]["postCommandSuccess"][
            "name"
        ]
        new_package.installInit_command = package["commands"]["installInit"]["command"]
        new_package.installInit_name = package["commands"]["installInit"]["name"]
        new_package.postCommandFailure_command = package["commands"][
            "postCommandFailure"
        ]["command"]
        new_package.postCommandFailure_name = package["commands"]["postCommandFailure"][
            "name"
        ]
        new_package.command_command = package["commands"]["command"]["command"]
        new_package.command_name = package["commands"]["command"]["name"]
        new_package.preCommand_command = package["commands"]["preCommand"]["command"]
        new_package.preCommand_name = package["commands"]["preCommand"]["name"]
        new_package.pkgs_share_id = pkgs_share_id
        new_package.edition_status = edition_status
        new_package.conf_json = json.dumps(package)
        if request is None:
            session.add(new_package)
        session.commit()
        session.flush()
        return new_package

    @DatabaseHelper._sessionm
    def remove_dependencies(self, session, package_uuid, status="delete"):
        """
        Remove the dependencies for the specified package.
        Params:
            package_uuid : string of the uuid of the package given as reference.
            status : string (default : delete) if the status is delete, then the
                function delete all in the dependencies table which refers to the package
        """
        session.query(Dependencies).filter(
            Dependencies.uuid_package == package_uuid
        ).delete()
        if status == "delete":
            session.query(Dependencies).filter(
                Dependencies.uuid_dependency == package_uuid
            ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def refresh_dependencies(self, session, package_uuid, uuid_list):
        """
        Refresh the list of the dependencies for a specified package.
        Params:
            package_uuid : string of the reference uuid
            uuid_list : list of the dependencies associated to the reference.
                One reference has many dependencies.
        """
        self.remove_dependencies(package_uuid, "refresh")
        for dependency in uuid_list:
            new_dependency = Dependencies()
            new_dependency.uuid_package = package_uuid
            new_dependency.uuid_dependency = dependency
            session.add(new_dependency)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_list_packages_deploy_view(
        self, session, objsearch, start=-1, end=-1, ctx={}
    ):
        """
        Get the list of all the packages uuid for deploy.
        Params:
            session: The SQLAlchemy session
            login: The user login. (str)
            sharing_activated: True, if the sharing system is activated
            start: int of the starting offset
            end: int of the limit
        Returns:
            It returns the list of the packages.
        """
        result = {"count": 0, "uuid": []}
        if "list_sharing" in objsearch and not objsearch["list_sharing"]:
            return result

        if "filter1" in ctx:
            filter1 = ctx["filter1"]
        else:
            filter1 = ""

        if "filter1" in ctx:
            filter1 = ctx["filter1"]
        else:
            filter1 = ""

        if "filter" in ctx:
            filter = ctx["filter"]
        else:
            filter = ""

        try:
            start = int(start)
        except BaseException:
            start = -1
        try:
            end = int(end)
        except BaseException:
            end = -1

        if filter == "":
            _filter = ""
        else:
            _filter = """AND ( pkgs_shares.name LIKE '%%%s%%'
            OR
                pkgs_shares.type LIKE '%%%s%%'
            OR
                packages.label LIKE '%%%s%%'
            OR
                packages.description LIKE '%%%s%%'
            OR
                packages.version LIKE '%%%s%%'
            OR
                packages.uuid LIKE '%%%s%%'
            OR
                packages.metagenerator LIKE '%%%s%%'
            OR
                packages.Qversion LIKE '%%%s%%'
            OR
                packages.Qvendor LIKE '%%%s%%'
            OR
                packages.Qsoftware LIKE '%%%s%%'
            )""" % (
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
            )

        if filter1 == "":
            _filter1 = ""
        else:
            _filter1 = """ AND
            packages.os LIKE '%%%s%%' """ % (
                filter1
            )

        if start >= 0:
            limit = "LIMIT %s" % start
        else:
            limit = " "

        if end > 0:
            offset = ", %s" % end
        else:
            offset = " "
        where_clause = ""
        if objsearch["list_sharing"]:
            strlist = ",".join([str(x) for x in objsearch["list_sharing"]])
            where_clause = (
                where_clause + " AND packages.`pkgs_share_id` IN (%s) " % strlist
            )

        where_clause = (
            where_clause
            + "AND pkgs_shares.enabled = 1  ORDER BY packages.pkgs_share_id ASC, packages.label ASC, packages.version ASC  "
        )

        sql = """SELECT SQL_CALC_FOUND_ROWS
                    packages.uuid
                FROM
                    packages
                        LEFT JOIN
                    pkgs_shares ON pkgs_shares.id = packages.pkgs_share_id
                WHERE
                    packages.uuid NOT IN (SELECT
                            syncthingsync.uuidpackage
                        FROM
                            pkgs.syncthingsync)
                %s %s %s %s %s
                    ;""" % (
            _filter,
            _filter1,
            where_clause,
            limit,
            offset,
        )
        ret = session.execute(sql)
        sql_count = "SELECT FOUND_ROWS();"
        ret_count = session.execute(sql_count)
        result["count"] = ret_count.first()[0]
        for package in ret:
            result["uuid"].append(package[0])
        return result

    @DatabaseHelper._sessionm
    def get_all_packages(
        self, session, login, sharing_activated=False, start=-1, end=-1, ctx={}
    ):
        """
        Get the list of all the packages stored in database.
        Params:
            session: The SQLAlchemy session
            login: The user login. (str)
            sharing_activated: True, if the sharing system is activated
            start: int of the starting offset
            end: int of the limit
        Returns:
            It returns the list of the packages.
        """

        result = {
            "total": 0,
            "datas": {
                "id": [],
                "name": [],
                "description": [],
                "version": [],
                "uuid": [],
                "conf_json": [],
                "share_id": [],
                "share_name": [],
                "share_type": [],
                "permission": [],
                "size": [],
            },
        }
        sharing = self.pkgs_search_share({"login": login})
        listidsharing = [
            [str(x["id_sharing"]), x["permission"]] for x in sharing["datas"]
        ]
        idsharestr = ",".join([x[0] for x in listidsharing])

        #  creation  dict
        dictpermission = {}
        for t in listidsharing:
            dictpermission[t[0]] = t[1]

        if "filter" in ctx:
            filter = ctx["filter"]
        else:
            filter = ""

        try:
            start = int(start)
        except BaseException:
            start = -1
        try:
            end = int(end)
        except BaseException:
            end = -1

        if sharing_activated is True:
            # No sharing found no need to continue, there
            if idsharestr == "":
                return result

            if filter == "":
                _filter = ""
            else:
                _filter = """AND ( pkgs_shares.name LIKE '%%%s%%'
            OR
                pkgs_shares.type LIKE '%%%s%%'
            OR
                packages.label LIKE '%%%s%%'
            OR
                packages.description LIKE '%%%s%%'
            OR
                packages.version LIKE '%%%s%%'
            OR
                packages.uuid LIKE '%%%s%%'
            OR
                packages.os LIKE '%%%s%%'
            OR
                packages.metagenerator LIKE '%%%s%%'
            OR
                packages.Qversion LIKE '%%%s%%'
            OR
                packages.Qvendor LIKE '%%%s%%'
            OR
                packages.Qsoftware LIKE '%%%s%%'
            )""" % (
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                )

            if start >= 0:
                limit = "LIMIT %s" % start
            else:
                limit = " "

            if end > 0:
                offset = ", %s" % end
            else:
                offset = " "

            sql = """SELECT SQL_CALC_FOUND_ROWS DISTINCT
                            packages.id AS package_id,
                            packages.label AS package_label,
                            packages.description AS package_description,
                            packages.version AS package_version,
                            packages.uuid,
                            packages.conf_json,
                            packages.pkgs_share_id AS share_id,
                            pkgs_shares.name AS share_name,
                            pkgs_shares.type AS share_type,
                            packages.size,
                            packages.inventory_licenses AS licenses,
                            packages.inventory_associateinventory AS associateinventory,
                            packages.Qversion AS qversion,
                            packages.Qvendor AS qvendor,
                            packages.Qsoftware AS qsoftware
                        FROM
                            packages
                                LEFT JOIN
                            pkgs_shares ON pkgs_shares.id = packages.pkgs_share_id
                        WHERE
                            packages.pkgs_share_id IN (%s) AND
                            packages.uuid NOT IN (SELECT
                                    syncthingsync.uuidpackage
                                FROM
                                    pkgs.syncthingsync)
                            %s
                        AND pkgs_shares.enabled = 1 ORDER BY packages.pkgs_share_id ASC, packages.label ASC, packages.version ASC
                        %s %s;""" % (
                idsharestr,
                _filter,
                limit,
                offset,
            )

            ret = session.execute(sql)
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            count = ret_count.first()[0]

        else:
            query = session.query(Packages).order_by(Packages.label)
            if filter != "":
                query = query.filter(Packages.conf_json.contains(filter))
            count = query.count()
            if start >= 0 and end > 0:
                query = query.offset(start).limit(end)
            ret = query.all()

        result["total"] = count

        if sharing_activated is True:
            result["datas"]["licence"] = []
            result["datas"]["associateinventory"] = []
            result["datas"]["qversion"] = []
            result["datas"]["qvendor"] = []
            result["datas"]["qsoftware"] = []
            for package in ret:
                try:
                    conf_json = json.loads(package[5])
                except BaseException:
                    conf_json = {}
                result["datas"]["id"].append(package[0])
                result["datas"]["uuid"].append(package[4])
                result["datas"]["name"].append(package[1])
                result["datas"]["description"].append(package[2])
                result["datas"]["version"].append(package[3])
                result["datas"]["conf_json"].append(conf_json)
                result["datas"]["share_id"].append(
                    package[6] if package[6] is not None else ""
                )
                result["datas"]["share_name"].append(
                    package[7] if package[7] is not None else ""
                )
                result["datas"]["share_type"].append(
                    package[8] if package[8] is not None else ""
                )
                result["datas"]["permission"].append(dictpermission[str(package[6])])
                result["datas"]["size"].append(
                    str(package[9]) if package[9] is not None else ""
                )
                result["datas"]["licence"].append(
                    package[10] if package[10] is not None else ""
                )
                result["datas"]["associateinventory"].append(
                    package[11] if package[11] is not None else ""
                )
                result["datas"]["qversion"].append(
                    package[12] if package[12] is not None else ""
                )
                result["datas"]["qvendor"].append(
                    package[13] if package[13] is not None else ""
                )
                result["datas"]["qsoftware"].append(
                    package[14] if package[14] is not None else ""
                )
        else:
            for package in ret:
                result["datas"]["id"].append(
                    package.id if package.id is not None else ""
                )
                result["datas"]["uuid"].append(
                    package.uuid if package.uuid is not None else ""
                )
                result["datas"]["name"].append(
                    package.label if package.label is not None else ""
                )
                result["datas"]["description"].append(
                    package.description if package.description is not None else ""
                )
                result["datas"]["version"].append(
                    package.version if package.version is not None else ""
                )
                try:
                    conf_json = json.loads(package.conf_json)
                except BaseException:
                    conf_json = {}
                result["datas"]["conf_json"].append(conf_json)
                result["datas"]["share_id"].append(
                    package.pkgs_share_id if package.pkgs_share_id is not None else ""
                )
                result["datas"]["size"].append(
                    package.size if package.size is not None else ""
                )
        return result

    @DatabaseHelper._sessionm
    def update_package_size(self, session, uuid, size):
        """
        This function update the size in package of the package.
        Args:
            session: the SQLAlchemy session
            uuid: The uuid of the package
            size: The new size of the package
        Returns:
            It returns the Quota for the shares.

        """
        result = {"size": size, "uuid": uuid, "error": 0}
        try:
            package = session.query(Packages).filter(Packages.uuid == uuid).first()
            if package:
                package.size = size
                result["label"] = package.label
                pkgs_share_id = package.pkgs_share_id
                result["pkgs_share_id"] = pkgs_share_id
                session.commit()
                session.flush()
                if pkgs_share_id is not None:
                    sql_request = (
                        session.query(func.sum(Packages.size).label("total_size"))
                        .filter(Packages.pkgs_share_id == pkgs_share_id)
                        .first()
                    )
                    resultquotas = self.update_sharing_usedquotas(
                        pkgs_share_id, sql_request.total_size
                    )
                    result.update(resultquotas)
        except BaseException:
            result["error"] = 1
        return result

    @DatabaseHelper._sessionm
    def update_sharing_usedquotas(self, session, rule_id, usesize):
        """
        Search quotas in the shares
        Args:
            session: the SQLAlchemy session
            usesize:
        """
        result = {"quotas": 0, "usedquotas": 0}
        re = session.query(Pkgs_shares).filter(Pkgs_shares.id == rule_id).first()
        if re:
            re.usedquotas = usesize
        session.commit()
        session.flush()
        return result

    @DatabaseHelper._sessionm
    def get_pkgs_share_from_uuid(self, session, uuid):
        """
        This function is used to obtain a package based on the uuid.
        Args:
            session: the SQLAlchemy session.
            uuid: string of the uuid of the specified package.

        Returns:
            It returns the package based on the uuid.
        """
        package = session.query(Packages).filter(Packages.uuid == uuid).first()
        if package:
            return package.to_array()
        return None

    @DatabaseHelper._sessionm
    def remove_package(self, session, uuid):
        """
        Delete the specified package from the DB and
        Updates the quotas used by the sharing in which the UUID package belongs.
        Param :
            session: the SQLAlchemy session
            uuid: string of the uuid of the specified package.
        """
        packagesdata = self.get_pkgs_share_from_uuid(uuid)
        session.query(Packages).filter(Packages.uuid == uuid).delete()
        session.commit()
        session.flush()
        if (
            packagesdata is not None
            and "pkgs_share_id" in packagesdata
            and packagesdata["pkgs_share_id"] is not None
        ):
            sql_request = (
                session.query(func.sum(Packages.size).label("total_size"))
                .filter(Packages.pkgs_share_id == packagesdata["pkgs_share_id"])
                .first()
            )
            return self.update_sharing_usedquotas(
                packagesdata["pkgs_share_id"], sql_request.total_size
            )
        return {"quotas": 0, "usedquotas": 0}

    ######## Extensions / Rules ##########
    @DatabaseHelper._sessionm
    def list_all_extensions(self, session):
        ret = session.query(Extensions).order_by(asc(Extensions.rule_order)).all()
        extensions = []
        for extension in ret:
            extensions.append(extension.to_array())
        return extensions

    @DatabaseHelper._sessionm
    def rule_test_extensions(
        self, session, nameexectutable, rule, bangtring=0, stringstring=0, stringfile=0
    ):
        extensions_dictlist = []
        try:
            sql = """SELECT
                    id,
                    REPLACE('%s', '"%%s"',  "%s"),
                    (IF(name IS NULL OR name = '', 0, 1) and  (SUBSTRING_INDEX("%s", '/', - 1) REGEXP name)) as rulename,
                    (IF(extension IS NULL OR extension = '', 0, 1) and SUBSTRING_INDEX("%s", '.', - 1) REGEXP extension ) as ruleextension,
                    (IF(bang IS NULL OR bang = '', 0, 1) and %s) as rulebang,
                    (IF(strings IS NULL OR strings = '', 0, 1) and %s) as rulestrings,
                    (IF(file IS NULL OR file = '', 0, 1) and %s) as rulefile
                FROM
                    pkgs.extensions
                WHERE
                id = %s and
                    ( name = '' or (SUBSTRING_INDEX("%s", '/', - 1) REGEXP name)) and
                    ( extension = ''  or SUBSTRING_INDEX("%s", '.', - 1) REGEXP extension ) and
                    ( strings = '' or %s) and
                    ( file = '' or %s) and
                    ( bang = '' or %s) ;""" % (
                rule["proposition"],
                nameexectutable,
                nameexectutable,
                nameexectutable,
                bangtring,
                stringstring,
                stringfile,
                rule["id"],
                nameexectutable,
                nameexectutable,
                stringstring,
                stringfile,
                bangtring,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            for extension in result:
                extensions_dict = {
                    "id": extension[0],
                    "proposition": extension[1],
                    "rulename": extension[2],
                    "ruleext": extension[3],
                    "rulestring": extension[4],
                    "rulefile": extension[5],
                    "rulesbang": extension[6],
                }
                extensions_dictlist.append(extensions_dict)
            logger.info(extensions_dictlist)
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))
        return extensions_dictlist

    @DatabaseHelper._sessionm
    def delete_extension(self, session, rule_id):
        try:
            session.query(Extensions).filter(Extensions.id == rule_id).delete()
            session.commit()
            session.flush()
            return True
        except BaseException:
            return False

    @DatabaseHelper._sessionm
    def raise_extension(self, session, rule_id):
        """
        Raise the selected rule
        Param:
            session: the SQLAlchemy session
            rule_id: int corresponding to the rule id we want to raise
        """
        rule_to_raise = session.query(Extensions).filter(Extensions.id == rule_id).one()
        rule_to_switch = (
            session.query(Extensions)
            .filter(Extensions.rule_order < rule_to_raise.rule_order)
            .order_by(desc(Extensions.rule_order))
            .first()
        )

        rule_to_raise.rule_order, rule_to_switch.rule_order = (
            rule_to_switch.getRule_order(),
            rule_to_raise.getRule_order(),
        )
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def lower_extension(self, session, rule_id):
        """
        Lower the selected rule
        Param:
            session: the SQLAlchemy session
            rule_id: int corresponding to the rule id we want to raise
        """
        rule_to_lower = session.query(Extensions).filter(Extensions.id == rule_id).one()
        rule_to_switch = (
            session.query(Extensions)
            .filter(Extensions.rule_order > rule_to_lower.rule_order)
            .order_by(asc(Extensions.rule_order))
            .first()
        )

        rule_to_lower.rule_order, rule_to_switch.rule_order = (
            rule_to_switch.getRule_order(),
            rule_to_lower.getRule_order(),
        )
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_last_extension_order(self, session):
        """Lower the selected rule
        Param:
            session: the SQLAlchemy session
            id: int corresponding to the rule id we want to raise
        """
        last_rule = (
            session.query(Extensions).order_by(desc(Extensions.rule_order)).first()
        )
        session.commit()
        session.flush()

        return last_rule.getRule_order()

    @DatabaseHelper._sessionm
    def add_extension(self, session, datas):
        """Lower the selected rule
        Param:
            session: the SQLAlchemy session
            id: int corresponding to the rule id we want to raise
        """
        if "id" in datas:
            request = (
                session.query(Extensions).filter(Extensions.id == datas["id"]).first()
            )
            rule = request
            if request is None:
                rule = Extensions()
        else:
            request = None
            rule = Extensions()

        if "rule_order" in datas:
            rule.rule_order = datas["rule_order"]

        if "rule_name" in datas:
            rule.rule_name = datas["rule_name"]

        if "name" in datas:
            rule.name = datas["name"]

        if "extension" in datas:
            rule.extension = datas["extension"]

        if "magic_command" in datas:
            rule.magic_command = datas["magic_command"]

        if "bang" in datas:
            rule.bang = datas["bang"]

        if "file" in datas:
            rule.file = datas["file"]

        if "strings" in datas:
            rule.strings = datas["strings"]

        if "proposition" in datas:
            rule.proposition = datas["proposition"]

        if "description" in datas:
            rule.description = datas["description"]

        if request is None:
            session.add(rule)

        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_extension(self, session, id):
        return session.query(Extensions).filter(Extensions.id == id).first().to_array()

    # =====================================================================
    # pkgs FUNCTIONS synch syncthing
    # =====================================================================

    @DatabaseHelper._sessionm
    def setSyncthingsync(
        self,
        session,
        uuidpackage,
        relayserver_jid,
        typesynchro="create",
        watching="yes",
    ):
        try:
            new_Syncthingsync = Syncthingsync()
            new_Syncthingsync.uuidpackage = uuidpackage
            new_Syncthingsync.typesynchro = typesynchro
            new_Syncthingsync.relayserver_jid = relayserver_jid
            new_Syncthingsync.watching = watching
            session.add(new_Syncthingsync)
            session.commit()
            session.flush()
        except Exception as e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def get_relayservers_no_sync_for_packageuuid(self, session, uuidpackage):
        result_list = []
        try:
            relayserversync = (
                session.query(Syncthingsync)
                .filter(and_(Syncthingsync.uuidpackage == uuidpackage))
                .all()
            )
            session.commit()
            session.flush()

            for relayserver in relayserversync:
                res = {}
                res["uuidpackage"] = relayserver.uuidpackage
                res["typesynchro"] = relayserver.typesynchro
                res["relayserver_jid"] = relayserver.relayserver_jid
                res["watching"] = relayserver.watching
                res["date"] = relayserver.date
                result_list.append(res)
            return result_list
        except Exception as e:
            logging.getLogger().error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return []

    @DatabaseHelper._sessionm
    def pkgs_register_synchro_package(self, session, uuidpackage, typesynchro):
        """
        This function allows to register the ARS that needs to tell the update of a package.
        This function is only used in the "not shared" mode of the packageserver.
        All the ARS are concerned.
        Args:
            session: the SQLAlchemy session
            uuidpackage: the UUID of the package.
            typesynchro: Tells if the package will be created or changed.
        """
        list_server_relay = XmppMasterDatabase().get_List_jid_ServerRelay_enable(
            enabled=1
        )
        for jid in list_server_relay:
            # Exclude the local package server
            if jid[0].startswith("rspulse@pulse/"):
                continue
            self.setSyncthingsync(uuidpackage, jid[0], typesynchro, watching="yes")

    @DatabaseHelper._sessionm
    def pkgs_register_synchro_package_multisharing(
        self, session, package, typesynchro="create"
    ):
        """
        This function allows to register the ARS that needs to tell the update of a package.
        This function is only used in the "shared" mode of the package server.
        Only the the ars in the share are concerned.

        Args:
            session: the SQLAlchemy session.
            package: The package to synchronize.
            typesynchro: Tells if the package will be created or changed.

        """
        list_idars = XmppMasterDatabase().get_List_Mutual_ARS_from_cluster_of_one_idars(
            package["shareobject"]["ars_id"]
        )
        list_server_relay = XmppMasterDatabase().getRelayServerfromid(list_idars[0])
        for relaydata in list_server_relay:
            if relaydata["jid"].startswith("rspulse@pulse/"):
                continue
            self.setSyncthingsync(
                package["id"], relaydata["jid"], typesynchro, watching="yes"
            )

    @DatabaseHelper._sessionm
    def pkgs_unregister_synchro_package(
        self, session, uuidpackage, typesynchro, jid_relayserver
    ):
        listdata = jid_relayserver.split("@")
        if len(listdata) > 0:
            datadata = "%s%%" % listdata[0]
            sql = """DELETE FROM `pkgs`.`syncthingsync`
                WHERE
                `syncthingsync`.`uuidpackage` like '%s' AND
                `syncthingsync`.`relayserver_jid`  like "%s" ;""" % (
                uuidpackage,
                datadata,
            )
            session.execute(sql)
            session.commit()
            session.flush()

    @DatabaseHelper._sessionm
    def pkgs_delete_synchro_package(self, session, uuidpackage):
        session.query(Syncthingsync).filter(
            Syncthingsync.uuidpackage == uuidpackage
        ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def list_pending_synchro_package(self, session):
        pendinglist = session.query(
            distinct(Syncthingsync.uuidpackage).label("uuidpackage")
        ).all()
        session.commit()
        session.flush()
        result_list = []
        for packageuid in pendinglist:
            result_list.append(packageuid.uuidpackage)
        return result_list

    @DatabaseHelper._sessionm
    def clear_old_pending_synchro_package(self, session, timeseconde=35):
        sql = (
            """DELETE FROM `pkgs`.`syncthingsync`
            WHERE
                `syncthingsync`.`date` < DATE_SUB(NOW(), INTERVAL %d SECOND);"""
            % timeseconde
        )
        session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_package_summary(self, session, package_id):
        path = os.path.join("/", "var", "lib", "pulse2", "packages", package_id)
        size = 0
        files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                size += os.path.getsize(os.path.join(root, file))

        diviser = 1000.0
        units = ["B", "Kb", "Mb", "Gb", "Tb"]

        count = 0
        next = True
        while next and count < len(units):
            if size / (diviser**count) > 1000:
                count += 1
            else:
                next = False

        query = (
            session.query(
                Packages.label,
                Packages.version,
                Packages.Qsoftware,
                Packages.Qversion,
                Packages.Qvendor,
                Packages.description,
            )
            .filter(Packages.uuid == package_id)
            .first()
        )
        session.commit()
        session.flush()
        result = {
            "name": "",
            "version": "",
            "Qsoftware": "",
            "Qversion": "",
            "Qvendor": "",
            "description": "",
            "files": files,
            "size": str(size),
            "Size": "%s %s" % (round(size / (diviser**count), 2), units[count]),
        }

        if query is not None:
            result["name"] = query.label
            result["version"] = query.version
            result["Qsoftware"] = query.Qsoftware
            result["Qversion"] = query.Qversion
            result["Qvendor"] = query.Qvendor
            result["description"] = query.description

        return result

    @DatabaseHelper._sessionm
    def delete_from_pending(self, session, pid="", jidrelay=[]):
        query = session.query(Syncthingsync)
        if pid != "":
            query = query.filter(Syncthingsync.uuidpackage == pid)
        if jidrelay != []:
            query = query.filter(Syncthingsync.relayserver_jid.in_(jidrelay))
        query = query.delete(synchronize_session="fetch")
        session.commit()
        session.flush()

    # =====================================================================
    # pkgs FUNCTIONS manage share
    # =====================================================================

    @DatabaseHelper._sessionm
    def SetPkgs_shares(
        self,
        session,
        name,
        comments,
        enabled,
        share_type,
        uri,
        ars_name,
        ars_id,
        share_path,
        usedquotas,
        quotas,
    ):
        try:
            new_Pkgs_shares = Pkgs_shares()
            new_Pkgs_shares.name = name
            new_Pkgs_shares.comments = comments
            new_Pkgs_shares.enabled = enabled
            new_Pkgs_shares.type = share_type
            new_Pkgs_shares.uri = uri
            new_Pkgs_shares.ars_name = ars_name
            new_Pkgs_shares.ars_id = ars_id
            new_Pkgs_shares.share_path = share_path
            new_Pkgs_shares.usedquotas = usedquotas
            new_Pkgs_shares.quotas = quotas
            session.add(new_Pkgs_shares)
            session.commit()
            session.flush()
            return new_Pkgs_shares.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def SetPkgs_shares_ars(self, session, shareId, hostname, jid, pkgs_shares_id):
        try:
            new_Pkgs_shares_ars = Pkgs_shares_ars()
            new_Pkgs_shares_ars.id = shareId
            new_Pkgs_shares_ars.hostname = hostname
            new_Pkgs_shares_ars.jid = jid
            new_Pkgs_shares_ars.pkgs_shares_id = pkgs_shares_id
            session.add(new_Pkgs_shares_ars)
            session.commit()
            session.flush()
            return new_Pkgs_shares_ars.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def SetPkgs_shares_ars_web(
        self,
        session,
        pkgs_share_id,
        ars_share_id,
        packages_id,
        status,
        finger_print,
        size,
        edition_date,
    ):
        try:
            new_Pkgs_shares_ars_web = Pkgs_shares_ars_web()
            new_Pkgs_shares_ars_web.ars_share_id = ars_share_id
            new_Pkgs_shares_ars_web.packages_id = packages_id
            new_Pkgs_shares_ars_web.status = status
            new_Pkgs_shares_ars_web.finger_print = finger_print
            new_Pkgs_shares_ars_web.size = size
            new_Pkgs_shares_ars_web.date_edition = date_edition
            session.add(new_Pkgs_shares_ars_web)
            session.commit()
            session.flush()
            return new_Pkgs_shares_ars_web.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def SetPkgs_rules_algos(self, session, name, description, level):
        try:
            new_Pkgs_rules_algos = Pkgs_rules_algos()
            session.add(new_Pkgs_rules_algos)
            new_Pkgs_rules_algos.name = name
            new_Pkgs_rules_algos.description = description
            new_Pkgs_rules_algos.level = level
            session.commit()
            session.flush()
            return new_Pkgs_rules_algos.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def SetPkgs_rules_global(
        self, session, pkgs_rules_algos_id, pkgs_cluster_ars_id, order, subject
    ):
        try:
            new_Pkgs_rules_global = Pkgs_rules_local()
            new_Pkgs_rules_global.pkgs_rules_algos_id = pkgs_rules_algos_id
            new_Pkgs_rules_global.pkgs_cluster_ars_id = pkgs_cluster_ars_id
            new_Pkgs_rules_global.order = order
            new_Pkgs_rules_global.subject = subject
            session.add(new_Pkgs_rules_global)
            session.commit()
            session.flush()
            return new_Pkgs_rules_global.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def SetPkgs_rules_local(
        self, session, pkgs_rules_algos_id, pkgs_shares_id, order, subject, permission
    ):
        try:
            new_Pkgs_rules_local.pkgs_rules_algos_id = pkgs_rules_algos_id
            new_Pkgs_rules_local.pkgs_shares_id = pkgs_shares_id
            new_Pkgs_rules_local.order = order
            new_Pkgs_rules_local.subject = subject
            new_Pkgs_rules_local.permission = permission
            session.add(new_Pkgs_rules_local)
            session.commit()
            session.flush()
            return new_Pkgs_rules_local.id
        except Exception as e:
            logging.getLogger().error(str(e))
            return None

    @DatabaseHelper._sessionm
    def pkgs_Orderrules(self, session):
        """
        This function is used to obtain the pkgs_rules_algos
        Args:
            session: The SQLAlchemy session
        Returns:
            It returns the pkgs_rules_algos ordered by level
        """
        sql = """SELECT
                    *
                FROM
                    pkgs.pkgs_rules_algos
                WHERE
                    pkgs_rules_algos.level < (SELECT
                            level
                        FROM
                            pkgs.pkgs_rules_algos
                        WHERE
                            name LIKE 'no_sharing')
                ORDER BY level;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    def _result_dict_sql_request(self, ret):
        """
        this function return dict result sqlalchimy
        """
        resultrecord = {}
        try:
            if ret:
                for keynameresult in list(ret.keys()):
                    if getattr(ret, keynameresult) is None:
                        resultrecord[keynameresult] = ""
                    else:
                        typestr = str(type(getattr(ret, keynameresult)))

                        if "class" in typestr:
                            try:
                                if "decimal.Decimal" in typestr:
                                    resultrecord[keynameresult] = float(
                                        getattr(ret, keynameresult)
                                    )
                                else:
                                    resultrecord[keynameresult] = str(
                                        getattr(ret, keynameresult)
                                    )
                            except BaseException:
                                self.logger.warning(
                                    "type class %s no used for key %s"
                                    % (typestr, keynameresult)
                                )
                                resultrecord[keynameresult] = ""
                        else:
                            if isinstance(
                                getattr(ret, keynameresult), datetime.datetime
                            ):
                                resultrecord[keynameresult] = getattr(
                                    ret, keynameresult
                                ).strftime("%m/%d/%Y %H:%M:%S")
                            else:
                                resultrecord[keynameresult] = getattr(
                                    ret, keynameresult
                                )
        except Exception:
            self.logger.error("\n%s" % (traceback.format_exc()))
        return resultrecord

    @DatabaseHelper._sessionm
    def pkgs_sharing_rule_search(
        self,
        session,
        user_information,
        algoid,
        enabled=1,
        share_type=None,
        permission=None,
    ):
        sql = """SELECT
                    pkgs.pkgs_shares.id AS id_sharing,
                    pkgs.pkgs_shares.name AS name,
                    pkgs.pkgs_shares.comments AS comments,
                    pkgs.pkgs_shares.enabled AS enabled,
                    pkgs.pkgs_shares.type AS type,
                    pkgs.pkgs_shares.uri AS uri,
                    pkgs.pkgs_shares.ars_name AS ars_name,
                    pkgs.pkgs_shares.ars_id AS ars_id,
                    pkgs.pkgs_shares.share_path AS share_path,
                    pkgs.pkgs_rules_local.id AS id_rule,
                    pkgs.pkgs_rules_local.pkgs_rules_algos_id AS algos_id,
                    pkgs.pkgs_rules_local.order AS order_rule,
                    pkgs.pkgs_rules_local.subject AS subject,
                    pkgs.pkgs_rules_local.permission AS permission,
                    pkgs.pkgs_shares.quotas AS quotas,
                    pkgs.pkgs_shares.usedquotas AS usedquotas
                FROM
                    pkgs.pkgs_shares
                        INNER JOIN
                    pkgs.pkgs_rules_local ON pkgs.pkgs_rules_local.pkgs_shares_id = pkgs.pkgs_shares.id
                WHERE"""

        whereclause = """'%s' REGEXP (pkgs.pkgs_rules_local.subject)
                        AND pkgs.pkgs_shares.enabled = %s
                        AND pkgs.pkgs_rules_local.pkgs_rules_algos_id = %s""" % (
            user_information,
            enabled,
            algoid,
        )
        typeclause = ""
        if share_type is not None:
            typeclause = """ AND pkgs.pkgs_shares.type = '%s' """ % (share_type)

        permitionclause = ""
        if permission is not None:
            permitionclause = (
                """ AND pkgs.pkgs_rules_local.permission like '%%%s%%' """
                % (permission)
            )
        sql = """ %s
                  %s %s %s
                  ORDER BY pkgs.pkgs_rules_local.order;""" % (
            sql,
            whereclause,
            typeclause,
            permitionclause,
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        ret = []
        if result:
            # create dict partage
            for y in result:
                resuldict = {}
                resuldict["id_sharing"] = y[0] if y[0] is not None else ""
                resuldict["name"] = y[1] if y[1] is not None else ""
                resuldict["comments"] = y[2] if y[2] is not None else ""
                resuldict["type"] = y[4] if y[4] is not None else ""
                resuldict["uri"] = y[5] if y[5] is not None else ""
                resuldict["ars_name"] = y[6] if y[6] is not None else ""
                resuldict["ars_id"] = y[7] if y[7] is not None else ""
                resuldict["share_path"] = y[8] if y[8] is not None else ""
                resuldict["id_rule"] = y[9] if y[9] is not None else ""
                resuldict["algos_id"] = y[10] if y[10] is not None else ""
                resuldict["order_rule"] = y[11] if y[11] is not None else ""
                resuldict["regexp"] = y[12] if y[12] is not None else ""
                resuldict["permission"] = y[13] if y[13] is not None else ""
                resuldict["quotas"] = str(y[14]) if y[14] is not None else ""
                resuldict["usedquotas"] = str(y[15]) if y[15] is not None else ""
                if resuldict["type"] == "global":
                    resuldict["nbpackage"] = self.nb_package_in_sharing(share_id=None)
                else:
                    resuldict["nbpackage"] = self.nb_package_in_sharing(
                        share_id=resuldict["id_sharing"]
                    )
                ret.append(resuldict)
        return ret

    @DatabaseHelper._sessionm
    def get_Cluster_list_rule(self, session, objsearch):
        if "login" in objsearch:
            sql = (
                """
                SELECT
                    pkgs_cluster_ars_id
                FROM
                    pkgs.pkgs_rules_global
                WHERE
                    '%s' REGEXP (pkgs.pkgs_rules_global.subject)
                         AND permission LIKE '%%r%%'
                         AND pkgs.pkgs_rules_global.pkgs_rules_algos_id = 3;"""
                % objsearch["login"]
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return [x for x in result]
        return []

    def pkgs_search_ars_list_from_cluster_rules(self, objsearch):
        """
        This function is used to retrieve the ars list for read permissions
            following the defined rules.
        Args:
            objsearch:
            # TODO: Fix documentation
        Results:
            It returns the the ars id followind the defined rules.

        """
        cluster_result = []
        extend_ars_list = []
        order_rules = self.pkgs_Orderrules()
        # global sharing
        if objsearch["login"] == "root":
            return []
        else:
            for algo in order_rules:
                if algo[0] == 3:
                    listcluster = self.get_Cluster_list_rule(objsearch)
                    extend_ars_list = (
                        XmppMasterDatabase().get_Arsid_list_from_clusterid_list(
                            listcluster
                        )
                    )
        return extend_ars_list

    def pkgs_search_share(self, objsearch):
        """
        This function is used to retrieve the shares and the permissions
            following the defined rules.
        Args:
            objsearch:
            # TODO: Fix documentation
        Results:
            It returns the the shares and the permissions following the defined rules.

        """
        sharing_result = []
        order_rules = self.pkgs_Orderrules()

        wrapper = {"config": {}, "datas": []}
        wrapper["config"][
            "centralizedmultiplesharing"
        ] = self.config.centralizedmultiplesharing
        wrapper["config"]["movepackage"] = self.config.movepackage

        permission = None
        if "permission" in objsearch:
            permission = objsearch["permission"]

        for algo in order_rules:
            id_algo = algo[0]
            # User Rule : 1 sharing on login user
            if id_algo == 1:
                if "login" in objsearch:
                    logger.debug(" algos id is %s [%s]" % (id_algo, algo[2]))
                    result = self.pkgs_sharing_rule_search(
                        objsearch["login"], algoid=id_algo, permission=permission
                    )
                    if result:
                        for t in result:
                            re = [x["name"] for x in sharing_result]
                            if t["name"] in re:
                                continue
                            sharing_result.append(t)
                    logger.debug("search sharing local %s" % (result))
            elif id_algo == 2:  # 1 sharing on profile userlogger.
                if "profil" in objsearch:
                    debug("algos id is %s [%s]" % (id_algo, algo[2]))
                    result = self.pkgs_sharing_rule_search(
                        objsearch["profil"], algoid=id_algo
                    )
                    if result:
                        for t in result:
                            re = [x["name"] for x in sharing_result]
                            if t["name"] in re:
                                continue
                            sharing_result.append(t)
                    logger.debug("search sharing local %s" % (result))

        wrapper["datas"] = sharing_result
        return wrapper

    @DatabaseHelper._sessionm
    def get_shares(self, session):
        """
        This function is used to obtain the list of the shares
        Args:
            session: The SQLAlchemy session

        Returns:
            It returns the list of the actual shares
        """
        query = session.query(Pkgs_shares).all()
        list_of_shares = [elem.toH() for elem in query]
        return list_of_shares

    @DatabaseHelper._sessionm
    def pkgs_sharing_admin_profil(self, session):
        """
            This function is used to obtain packages list
            from the admin profile
        Args:
            session: The SQLAlchemy session

        Returns:
            It returns the list of the actual shares for the admin profile.
        """
        sql = """SELECT
                    pkgs.pkgs_shares.id AS id_sharing,
                    pkgs.pkgs_shares.name AS name,
                    pkgs.pkgs_shares.comments AS comments,
                    pkgs.pkgs_shares.enabled AS enabled,
                    pkgs.pkgs_shares.type AS type,
                    pkgs.pkgs_shares.uri AS uri,
                    pkgs.pkgs_shares.ars_name AS ars_name,
                    pkgs.pkgs_shares.ars_id AS ars_id,
                    pkgs.pkgs_shares.share_path AS share_path,
                    pkgs.pkgs_shares.quotas AS quotas,
                    pkgs.pkgs_shares.usedquotas AS usedquotas
                FROM
                    pkgs.pkgs_shares
                WHERE
                     pkgs.pkgs_shares.enabled = 1;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        ret = []
        if result:
            # create dict partage
            for y in result:
                resuldict = {}
                resuldict["id_sharing"] = y[0] if y[0] is not None else ""
                resuldict["name"] = y[1] if y[1] is not None else ""
                resuldict["comments"] = y[2] if y[2] is not None else ""
                resuldict["type"] = y[4] if y[4] is not None else ""
                resuldict["uri"] = y[5] if y[5] is not None else ""
                resuldict["ars_name"] = y[6] if y[6] is not None else ""
                resuldict["ars_id"] = y[7] if y[7] is not None else ""
                resuldict["share_path"] = y[8] if y[8] is not None else ""
                resuldict["permission"] = "rw"
                resuldict["quotas"] = str(y[9]) if y[9] is not None else ""
                resuldict["usedquotas"] = str(y[10]) if y[10] is not None else ""
                ret.append(resuldict)
                if resuldict["type"] == "global":
                    resuldict["nbpackage"] = self.nb_package_in_sharing(share_id=None)
                else:
                    resuldict["nbpackage"] = self.nb_package_in_sharing(
                        share_id=resuldict["id_sharing"]
                    )
        return ret

    @DatabaseHelper._sessionm
    def nb_package_in_sharing(self, session, share_id=None):
        sql = """SELECT
                    COUNT(*)
                FROM
                    pkgs.packages
                WHERE
                    packages.pkgs_share_id is NULL;"""
        logging.getLogger().debug(str(sql))
        if share_id is not None:
            sql = """SELECT
                        COUNT(*)
                    FROM
                        pkgs.packages
                    WHERE
                        packages.pkgs_share_id = %s;""" % (
                share_id
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result][0][0]

    @DatabaseHelper._sessionm
    def pkgs_get_sharing_list_login(self, session, loginname):
        sql = """SELECT
                    distinct pkgs.pkgs_shares.id as id_sharing,
                    pkgs.pkgs_shares.name as name,
                    pkgs.pkgs_shares.comments as comments,
                    pkgs.pkgs_shares.enabled as enabled,
                    pkgs.pkgs_shares.type as type,
                    pkgs.pkgs_shares.uri as uri,
                    pkgs.pkgs_shares.ars_name as ars_name,
                    pkgs.pkgs_shares.ars_id as ars_id,
                    pkgs.pkgs_shares.share_path as share_path,
                    pkgs.pkgs_rules_local.id as id_rule,
                    pkgs.pkgs_rules_local.pkgs_rules_algos_id as algos_id,
                    pkgs.pkgs_rules_local.order as order_rule,
                    pkgs.pkgs_rules_local.subject as subject,
                    pkgs.pkgs_rules_local.permission as permission
                FROM
                    pkgs.pkgs_shares
                        INNER JOIN
                    pkgs.pkgs_rules_local
                        ON pkgs.pkgs_rules_local.pkgs_shares_id = pkgs.pkgs_shares.id
                WHERE
                        '%s' REGEXP (pkgs.pkgs_rules_local.subject)
                        AND pkgs.pkgs_shares.enabled = 1
                ORDER BY pkgs.pkgs_rules_local.order;""" % (
            loginname
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        ret = []
        if result:
            # create dict partage
            for y in result:
                resuldict = {}
                resuldict["id_sharing"] = y[0]
                resuldict["name"] = y[1]
                resuldict["comments"] = y[2]
                resuldict["type"] = y[4]
                resuldict["uri"] = y[5]
                resuldict["ars_name"] = y[6]
                resuldict["ars_id"] = y[7]
                resuldict["share_path"] = y[8]
                # information from table pkgs_rules_local or pkgs_rules_global
                resuldict["id_rule"] = y[9]
                resuldict["algos_id"] = y[10]
                resuldict["order_rule"] = y[11]
                resuldict["regexp"] = y[12]
                resuldict["permission"] = y[13]
                ret.append(resuldict)
        return ret

    @DatabaseHelper._sessionm
    def get_pkg_name_from_uuid(self, session, uuids):
        """
        Retrieve the name of the package based on the uuids
        Args:
            session: The SQL Alchemy session
            uuids: uuids of the packages
        Return:
            It returns the name of the package
        """
        query = session.query(Packages.label, Packages.uuid)
        if isinstance(uuids, list):
            query = query.filter(Packages.uuid.in_(uuids))
        elif isinstance(uuids, str):
            query = query.filter(Packages.uuid == uuids)

        result = query.all()
        pkg = {}
        if result is not None:
            for tmp in result:
                pkg[tmp.uuid] = tmp.label

        return pkg

    @DatabaseHelper._sessionm
    def get_pkg_creator_from_uuid(self, session, uuids):
        """
        Retrieve the creator of the package based on the uuids
        Args:
            session: The SQL Alchemy session
            uuids: uuids of the packages
        Return:
            It returns the name of the creator of the package
        """
        query = session.query(Packages.conf_json, Packages.uuid)
        if isinstance(uuids, list):
            query = query.filter(Packages.uuid.in_(uuids))
        elif isinstance(uuids, str):
            query = query.filter(Packages.uuid == uuids)
        result = query.all()

        pkg = {}
        if result is not None:
            for tmp in result:
                try:
                    conf_json = json.loads(tmp.conf_json)
                    if "creator" in conf_json:
                        pkg[tmp.uuid] = conf_json["creator"]
                    else:
                        pkg[tmp.uuid] = ""
                except BaseException:
                    pkg[tmp.uuid] = ""
        return pkg

    @DatabaseHelper._sessionm
    def get_files_infos(self, session, uuid, filename=""):
        """
        This is used to retrieve informations about a package.
        Args:
            session: The SQLAlchemy session
            uuid: uuid of the package
            filename: name of the file to analyze
        Return:
            Return informations about the package:
                - Name
                - Size
                - Mime
                - Fullpath
                - Content
        """
        query = (
            session.query(Pkgs_shares.share_path)
            .join(Packages, Pkgs_shares.id == Packages.pkgs_share_id)
            .filter(Packages.uuid == uuid)
            .first()
        )

        path = query[0] if query is not None else ""

        result = {"path": path, "files": []}

        if path is None:
            return result

        try:
            pkg_path = os.readlink(os.path.join(path, uuid))
        except BaseException:
            pkg_path = os.path.join(path, uuid)

        mime_reader = magic.open(magic.MAGIC_MIME)
        mime_reader.load()

        if os.path.isdir(pkg_path):
            result["valid_path"] = True
            if filename == "":
                # Get all files
                result["files"] = [
                    {
                        "fullpath": os.path.join(pkg_path, pkg_file),
                        "name": pkg_file,
                        "size": str(os.path.getsize(os.path.join(pkg_path, pkg_file))),
                        "mime": mime_reader.file(
                            os.path.join(pkg_path, pkg_file)
                        ).split("; charset="),
                    }
                    for pkg_file in os.listdir(pkg_path)
                    if os.path.isfile(os.path.join(pkg_path, pkg_file))
                ]
            else:
                # Get specific file
                if os.path.join(pkg_path, filename):
                    result = {
                        "name": filename,
                        "mime": mime_reader.file(
                            os.path.join(pkg_path, filename)
                        ).split("; charset="),
                        "content": "",
                    }
                    if result["mime"][0].startswith("text"):
                        fp = open(os.path.join(pkg_path, filename), "rb")
                        result["content"] = base64.b64encode(fp.read())
                        fp.close()
                else:
                    result = {"size": 0, "content": ""}
        else:
            result["valid_path"] = False
        return result
