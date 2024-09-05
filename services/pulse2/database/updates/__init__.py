# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later

# SqlAlchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    select,
    func,
    and_,
    desc,
    or_,
    distinct,
    Table,
)
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base


# On importe la base de xmpp
# from pulse2.database.xmppmaster import XmppMasterDatabase

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.updates.schema import Tests

# Imported last
import logging
import json
import time

# Session = sessionmaker()

logger = logging.getLogger()


class UpdatesDatabase(DatabaseHelper):
    """
    Singleton Class to query the update database.

    """

    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "updates"
        self.configfile = "updates.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        # Base = automap_base()
        if self.is_activated:
            return None
        self.config = config

        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
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

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM updates.version limit 1;")
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
            except DBAPIError as e:
                logging.getLogger().error(e)
            except Exception as e:
                logging.getLogger().error(e)
            if ret:
                break
        if not ret:
            raise "Database updates connection error"
        return ret

    # =====================================================================
    # updates FUNCTIONS
    # =====================================================================
    @DatabaseHelper._sessionm
    def tests(self, session):
        # Tests c'est la table dans schema.py dans le module updates
        ret = session.query(Tests).all()
        lines = []
        for row in ret:
            lines.append(row.toDict())

        return lines

    @DatabaseHelper._sessionm
    def test_xmppmaster(self, session):
        sql = """SELECT update_data.product,
                        update_data.title
        FROM xmppmaster.update_data
        WHERE revisionid = '32268448';"""

        result = session.execute(sql)
        session.commit()
        session.flush()

        resultat = [x for x in result]
        print(resultat)
        if len(resultat) == 0:
            return -1
        else:
            return [x for x in result]
            # return resultat[0][1]

    @DatabaseHelper._sessionm
    def get_black_list(self, session, start, limit, filter=""):
        try:
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1

        try:
            black_list = {
                "nb_element_total": 0,
                "id": [],
                "updateid_or_kb": [],
                "title": [],
                "severity": [],
            }

            sql = """SELECT SQL_CALC_FOUND_ROWS
                        xmppmaster.up_black_list.updateid_or_kb,
                        xmppmaster.update_data.title,
                        xmppmaster.up_black_list.id,
                        coalesce(NULLIF(xmppmaster.update_data.msrcseverity, ""), "Corrective") as msrcseverity
                    FROM
                        xmppmaster.up_black_list
                    INNER JOIN
                        xmppmaster.update_data
                    ON
                        up_black_list.updateid_or_kb = update_data.kb
                    OR
                        up_black_list.updateid_or_kb = update_data.updateid """

            filterlimit = ""
            if limit != -1 and start != -1:
                filterlimit = "LIMIT %s, %s" % (start, limit)

            if filter:
                ffilterwhere = """WHERE
                    (update_data.title LIKE '%%%s%%' OR
                    concat("KB", update_data.kb) LIKE '%%%s%%' OR
                    update_data.description LIKE '%%%s%%' OR
                    update_data.updateid LIKE '%%%s%%' OR
                    coalesce(NULLIF(xmppmaster.update_data.msrcseverity, ""), "Corrective") LIKE '%%%s%%') """ % (
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                )
                sql += filterwhere

            sql += ' ORDER BY FIELD(msrcseverity, "Critical", "Important", "") '
            sql += filterlimit
            sql += ";"

            result = session.execute(sql)

            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]

            black_list["nb_element_total"] = nb_element_total

            session.commit()
            session.flush()

            if result is not None:
                for list_b in result:
                    black_list["updateid_or_kb"].append(list_b.updateid_or_kb)
                    black_list["title"].append(list_b.title)
                    black_list["id"].append(list_b.id)
                    black_list["severity"].append(list_b.msrcseverity)

        except Exception as e:
            logger.error("error function get_black_list : %s" % e)
        return black_list

    @DatabaseHelper._sessionm
    def get_grey_list(self, session, start, limit, filter=""):
        try:
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1

        try:
            grey_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "valided": [],
                "severity": [],
            }

            sql = """SELECT SQL_CALC_FOUND_ROWS
                        xmppmaster.up_gray_list.*,
                        coalesce(NULLIF(xmppmaster.update_data.msrcseverity, ""), "Corrective") as msrcseverity
                    FROM
                        xmppmaster.up_gray_list
                    JOIN xmppmaster.update_data on xmppmaster.update_data.updateid = xmppmaster.up_gray_list.updateid """

            filterlimit = ""
            if start != -1 and limit != -1:
                filterlimit = "LIMIT %s, %s" % (start, limit)
            if filter != "":
                filterwhere = """WHERE
                    (update_data.title LIKE '%%%s%%' OR
                    concat("KB", update_data.kb) LIKE '%%%s%%' OR
                    update_data.description LIKE '%%%s%%' OR
                    update_data.updateid LIKE '%%%s%%' OR
                    coalesce(NULLIF(xmppmaster.update_data.msrcseverity, ""), "Corrective") LIKE '%%%s%%') """ % (
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                )
                sql += filterwhere

            sql += ' ORDER BY FIELD(msrcseverity, "Critical", "Important", "") '
            sql += filterlimit
            sql += ";"

            result = session.execute(sql)

            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]

            grey_list["nb_element_total"] = nb_element_total

            session.commit()
            session.flush()

            if result:
                for list_b in result:
                    grey_list["updateid"].append(list_b.updateid)
                    grey_list["title"].append(list_b.title)
                    grey_list["kb"].append(list_b.kb)
                    grey_list["valided"].append(list_b.valided)
                    grey_list["severity"].append(list_b.msrcseverity)

        except Exception as e:
            logger.error("error function get_grey_list")

        return grey_list

    @DatabaseHelper._sessionm
    def get_white_list(self, session, start=0, limit=-1, filter=""):
        try:
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1

        try:
            white_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "severity": [],
            }

            sql = """SELECT SQL_CALC_FOUND_ROWS
                        xmppmaster.up_white_list.*,
                        coalesce(NULLIF(xmppmaster.update_data.msrcseverity, ""), "Corrective") as msrcseverity
                    FROM xmppmaster.up_white_list
                    JOIN xmppmaster.update_data on xmppmaster.update_data.updateid = xmppmaster.up_white_list.updateid """

            if filter:
                filterwhere = """WHERE
                    (update_data.title LIKE '%%%s%%' OR
                    concat("KB", update_data.kb) LIKE '%%%s%%' OR
                    update_data.description LIKE '%%%s%%' OR
                    update_data.updateid LIKE '%%%s%%' OR
                    coalesce(NULLIF(xmppmaster.update_data.msrcseverity, ""), "Corrective") LIKE '%%%s%%') """ % (
                    filter,
                    filter,
                    filter,
                    filter,
                    filter,
                )
                sql += filterwhere

            sql += ' ORDER BY FIELD(msrcseverity, "Critical", "Important", "") '
            filterlimit = ""
            if start != -1 and limit != -1:
                filterlimit = "LIMIT %s, %s" % (start, limit)
            sql += filterlimit
            sql += ";"
            result = session.execute(sql)

            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]

            white_list["nb_element_total"] = nb_element_total

            if result:
                for list_w in result:
                    white_list["updateid"].append(list_w.updateid)
                    white_list["title"].append(list_w.title)
                    white_list["kb"].append(list_w.kb)
                    white_list["severity"].append(list_w.msrcseverity)

        except Exception as e:
            logger.error("error function get_white_list")

        return white_list

    @DatabaseHelper._sessionm
    def get_enabled_updates_list(
        self, session, entity, upd_list="gray", start=0, limit=-1, filter="", config=None
    ):
        try:
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1
        filter_on = ""
        if config.filter_on is not None:
            for key in config.filter_on:
                if key == "state":
                    filter_on = "%s AND lgf.states_id in (%s)"%(filter_on, ",".join(config.filter_on[key]))
                if key == "type":
                    filter_on = "%s AND lgf.computertypes_id in (%s)"%(filter_on, ",".join(config.filter_on[key]))
                if key == "entity":
                    filter_on = "%s AND lgf.entities_id in (%s)"%(filter_on, ",".join(config.filter_on[key]))

        try:
            enabled_updates_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "missing": [],
                "installed": [],
                "history_list" : []
            }

            sql = """SELECT SQL_CALC_FOUND_ROWS
            uma.update_id as updateid,
    ud.kb AS kb,
    ud.title AS title,
    ud.description AS description,
    ud.creationdate AS creationdate,
    ud.title_short AS title_short,
    count(uma.update_id) as missing
FROM
    xmppmaster.up_machine_activated uma
    JOIN xmppmaster.update_data ud ON uma.update_id = ud.updateid
    JOIN xmppmaster.local_glpi_machines lgm on lgm.id = uma.glpi_id
    join xmppmaster.local_glpi_filters lgf on lgf.id = lgm.id
WHERE
    uma.entities_id = %s
    and list = "%s"
    %s""" % (
                entity.replace("UUID", ""),
                upd_list,
                filter_on
            )

            if filter != "":
                filterwhere = """AND
                        (ud.title LIKE '%%%s%%'
                        OR ud.updateid LIKE '%%%s%%'
                        OR ud.kb LIKE '%%%s%%'
                        OR ud.description LIKE '%%%s%%'
                        OR ud.creationdate LIKE '%%%s%%'
                        OR ud.title_short LIKE '%%%s%%')""" % tuple(
                    filter for x in range(0, 6)
                )
                sql += filterwhere

            sql += "group by uma.update_id "
            filterlimit = ""
            if start != -1 and limit != -1:
                filterlimit = "LIMIT %s, %s" % (start, limit)
            sql += filterlimit
            sql += ";"

            result = session.execute(sql)

            sql_count = "SELECT FOUND_ROWS();"
            try:
                ret_count = session.execute(sql_count)
            except Exception as e:
                logging.getLogger().error(e)
            nb_element_total = ret_count.first()[0]

            enabled_updates_list["nb_element_total"] = nb_element_total

            session.commit()
            session.flush()

            if result:
                for list_b in result:
                    sql2 = """select 
                    count(ma.id) as count,
                    coalesce(group_concat(lgm.id), NULL, "") as list
        from xmppmaster.machines ma
        join xmppmaster.local_glpi_machines lgm on concat("UUID",lgm.id) = ma.uuid_inventorymachine
        join xmppmaster.up_history uh on uh.id_machine = ma.id
        join xmppmaster.local_glpi_entities lge on lgm.entities_id = lge.id
    where uh.update_id='%s' and lge.id=%s and uh.delete_date is not NULL
    %s""" % (list_b.updateid, entity.replace("UUID", ""), filter_on )
                    try:
                        res = session.execute(sql2)
                    except Exception as e:
                        logger.error(e)
                    installed = 0
                    history_list=""
                    if res is not None:
                        for _res in res:
                            installed = _res.count
                            history_list = _res.list
                    enabled_updates_list["updateid"].append(list_b.updateid)
                    enabled_updates_list["title"].append(list_b.title)
                    enabled_updates_list["kb"].append(list_b.kb)
                    enabled_updates_list["missing"].append(list_b.missing)
                    enabled_updates_list["installed"].append(installed)

        except Exception as e:
            logger.error("error function get_enabled_updates_list %s" % e)

        return enabled_updates_list

    @DatabaseHelper._sessionm
    def approve_update(self, session, updateid):
        try:
            sql = """SELECT updateid,
                        kb,
                        title,
                        description
                    FROM xmppmaster.up_gray_list
                    WHERE updateid = '%s' or kb='%s' LIMIT 1;""" % (
                updateid,
                updateid,
            )
            result = session.execute(sql)
            selected = {"updateid": "", "kb": "", "title": "", "description": ""}

            if result is not None:
                selected = [
                    {
                        "updateid": elem.updateid,
                        "kb": elem.kb,
                        "title": elem.title,
                        "description": elem.description,
                    }
                    for elem in result
                ]
            selected = selected[0]

            sql2 = """INSERT INTO 
                        xmppmaster.up_white_list (updateid, kb, title, description, valided) 
                        VALUES("%s", "%s", "%s", "%s", %s)""" % (
                selected["updateid"],
                selected["kb"],
                selected["title"],
                selected["description"],
                1,
            )
            session.execute(sql2)

            session.commit()
            session.flush()
            return True
        except Exception as e:
            return False

    @DatabaseHelper._sessionm
    def grey_update(self, session, updateid, enabled=0):
        try:
            sql = """UPDATE `xmppmaster`.`up_gray_list`
                    SET
                        valided = %s
                    WHERE
                        (updateid = '%s');""" % (
                enabled,
                updateid,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logging.getLogger().error(str(e))
        return False

    @DatabaseHelper._sessionm
    def exclude_update(self, session, updateid):
        try:
            sql = """INSERT IGNORE INTO xmppmaster.up_black_list (updateid_or_kb, userjid_regexp, enable_rule, type_rule)
                VALUES ('%s', '.*', '1', 'id');""" % (
                updateid
            )

            result = session.execute(sql)
            session.commit()

            session.flush()
            return True
        except Exception as e:
            logging.getLogger().error(str(e))
        return False

    @DatabaseHelper._sessionm
    def delete_rule(self, session, id):
        try:
            sql_add = """INSERT INTO xmppmaster.up_gray_list (updateid, kb, revisionid, title, updateid_package, payloadfiles)
        SELECT xmppmaster.up_packages.updateid, xmppmaster.up_packages.kb, xmppmaster.up_packages.revisionid, xmppmaster.up_packages.title, xmppmaster.up_packages.updateid_package, xmppmaster.up_packages.payloadfiles FROM xmppmaster.up_packages
JOIN xmppmaster.up_black_list ON xmppmaster.up_packages.updateid = xmppmaster.up_black_list.updateid_or_kb or xmppmaster.up_packages.kb = xmppmaster.up_black_list.updateid_or_kb WHERE xmppmaster.up_black_list.id=%s;""" % (
                id
            )

            sql = (
                """DELETE FROM `xmppmaster`.`up_black_list` WHERE (`id` = '%s');"""
                % (id)
            )

            result = session.execute(sql_add)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True

        except Exception as e:
            logging.getLogger().error(str(e))
        return False

    @DatabaseHelper._sessionm
    def get_family_list(self, session, start, end, filter=""):
        try:
            family_list = {"nb_element_total": 0, "name_procedure": []}

            sql = """SELECT SQL_CALC_FOUND_ROWS
                        *
                    FROM
                        xmppmaster.up_list_produit 
                    WHERE
                        enable = 1 """

            if filter:
                filterwhere = (
                    """AND
                        name_procedure LIKE '%%%s%%'
                    LIMIT 5 OFFSET 5"""
                    % filter
                )
                sql = sql + filterwhere

            sql += ";"

            result = session.execute(sql)

            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]

            family_list["nb_element_total"] = nb_element_total

            session.commit()
            session.flush()

            if result:
                for list_f in result:
                    family_list["name_procedure"].append(list_f.name_procedure)

        except Exception as e:
            logger.error("error function get_family_list")

        return family_list

    @DatabaseHelper._sessionm
    def get_count_machine_as_not_upd(self, session, updateid):
        """
        This function returns the the update already done and update enable
        """
        sql = """SELECT COUNT(*) AS nb_machine_missing_update
                FROM
                    xmppmaster.up_machine_windows
                WHERE
                    (update_id = '%s');""" % (
            updateid
        )

        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [
            {column: value for column, value in rowproxy.items()}
            for rowproxy in resultquery
        ]
        return result

    @DatabaseHelper._sessionm
    def get_machines_needing_update(self, session, updateid, uuid, config, start=0, limit=-1, filter=""):
        """
        This function returns the list of machines needing a specific update
        """
        slimit = "limit %s"%start
        try:
            limit = int(limit)
        except:
            limit = -1

        if limit != -1:
            slimit = "%s,%s"%(slimit, limit)

        filter_on = ""

        sfilter = ""
        if filter != "":
            sfilter = """AND
    (lgm.name LIKE '%%%s%%'
    OR uma.update_id LIKE '%%%s%%'
    OR m.platform LIKE '%%%s%%'
    OR uma.kb LIKE '%%%s%%')""" % tuple(
                    filter for x in range(0, 4)
                )

        if config.filter_on is not None:
            for key in config.filter_on:
                if key not in ["state", "entity", "type"]:
                    continue
                if key == "state":
                    filter_on = "%s AND lgf.states_id in (%s)"%(filter_on, ",".join(config.filter_on[key]))
                if key == "type":
                    filter_on = "%s AND lgf.computertypes_id in (%s)"%(filter_on, ",".join(config.filter_on[key]))
                if key == "entity":
                    filter_on = "%s AND lgf.entities_id in (%s)"%(filter_on, ",".join(config.filter_on[key]))

        sql = """select
    SQL_CALC_FOUND_ROWS
    lgm.id,
    lgm.name,
    m.platform,
    concat("KB", uma.kb) as kb
from xmppmaster.up_machine_activated uma
join xmppmaster.machines m on uma.id_machine = m.id
join xmppmaster.local_glpi_machines lgm on concat("UUID", lgm.id) = m.uuid_inventorymachine
join xmppmaster.local_glpi_filters lgf on lgf.id = lgm.id
where uma.update_id = "%s"
and lgm.is_deleted = 0
and lgm.is_template = 0
and lgm.entities_id = %s
%s
%s
%s;
"""%(updateid,uuid.replace("UUID",""), sfilter, filter_on,slimit)
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        count = session.execute("SELECT FOUND_ROWS();")
        count = [elem[0] for elem in count][0]

        result = {
            "datas": {
                "id": [],
                "name": [],
                "platform" : [],
                "kb" : []
            },
            "total": count
        }

        if resultquery:
            for row in resultquery:
                result["datas"]["id"].append(row.id)
                result["datas"]["name"].append(row.name)
                result["datas"]["platform"].append(row.platform)
                result["datas"]["kb"].append(row.kb)
        return result

    @DatabaseHelper._sessionm
    def white_unlist_update(self, session, updateid):
        sql = (
            """DELETE FROM xmppmaster.up_white_list WHERE updateid = '%s' or kb='%s'"""
            % (updateid, updateid)
        )
        try:
            session.execute(sql)
            session.commit()
            session.flush()
            return True
        except:
            return False
