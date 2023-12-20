# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later

"""
kiosk database handler
"""
# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from mmc.plugins.pkgs import get_xmpp_package, xmpp_packages_list, package_exists
from pulse2.database.kiosk.schema import (
    Profiles,
    Profile_has_package,
    Profile_has_ou,
    Acknowledgements,
)
from pulse2.database.pkgs.orm.pakages import Packages

# Imported last
import logging
import json
import time
from datetime import datetime


class KioskDatabase(DatabaseHelper):
    """
    Singleton Class to query the xmppmaster database.

    """

    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "kiosk"
        self.configfile = "kiosk.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        if self.is_activated:
            return None
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
        )
        print(self.makeConnectionPath())
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM kiosk.version limit 1;")
        re = [element.Number for element in result]
        # logging.getLogger().debug("xmppmaster database connected (version:%s)"%(re[0]))
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
            except DBAPIError as e:
                logging.getLogger().error(e)
            except Exception as e:
                logging.getLogger().error(e)
            if ret:
                break
        if not ret:
            raise "Database kiosk connection error"
        return ret

    # =====================================================================
    # kiosk FUNCTIONS
    # =====================================================================

    @DatabaseHelper._sessionm
    def get_profiles_list(self, session, start=0, limit=-1, filter=""):
        """
        Return a list of all the existing profiles.
        The list contains all the elements of the profile.

        Returns:
            A list of all the founded entities.
        """

        try:
            start = int(start)
        except:
            start = 0
        try:
            limit = int(limit)
        except:
            limit = -1

        ret = session.query(Profiles)
        if filter != "":
            ret = ret.filter(
                or_(
                    Profiles.name.contains(filter),
                    Profiles.active.contains(filter),
                    Profiles.creation_date.contains(filter),
                )
            )
        count = ret.count()
        if limit != -1:
            ret = ret.limit(limit).offset(start)
        ret = ret.all()
        lines = []
        for row in ret:
            lines.append(row.toDict())

        return {"total": count, "datas": lines}

    @DatabaseHelper._sessionm
    def get_profile_list_for_OUList(self, session, OU):
        if len(OU) == 0:
            # return le profils par default
            return
        listou = "('" + "','".join(OU) + "')"
        sql = (
            """
            SELECT
                distinct
                pkgs.packages.label as 'name_package',
                kiosk.profiles.name as 'name_profile',
                pkgs.packages.description,
                pkgs.packages.version version_package,
                pkgs.packages.Qsoftware as software,
                pkgs.packages.Qversion version_software,
                pkgs.packages.uuid as package_uuid,
                pkgs.packages.os,
                kiosk.package_has_profil.package_status,
                kiosk.package_has_profil.id as id_package_has_profil
            FROM
                pkgs.packages
                  inner join
                kiosk.package_has_profil on pkgs.packages.uuid = kiosk.package_has_profil.package_uuid
                  inner join
                kiosk.profiles on profiles.id = kiosk.package_has_profil.profil_id

            WHERE
                kiosk.profiles.id in
                        (SELECT DISTINCT
                                profile_id
                            FROM
                                kiosk.profile_has_ous
                            WHERE
                                ou IN %s)
                    AND kiosk.profiles.active = 1;
                    """
            % listou
        )
        try:
            result = session.execute(sql)
            session.commit()
            session.flush()
            l = [x for x in result]
            return l
        except Exception as e:
            logging.getLogger().error("get_profile_list_for_OUList")
            logging.getLogger().error(str(e))
            return ""

    @DatabaseHelper._sessionm
    def add_askacknowledge(self, session, OU, package_uuid, askuser):
        if len(OU) == 0:
            return False
        listou = "('" + "','".join(OU) + "')"
        sql = """SELECT
    distinct
    kiosk.profiles.id as profile_id,
    kiosk.profiles.name as 'name_profile',
    kiosk.package_has_profil.package_status,
    kiosk.package_has_profil.id as package_has_profil_id,
    kiosk.package_has_profil.package_uuid
FROM
    kiosk.package_has_profil
INNER JOIN
    kiosk.profiles on profiles.id = kiosk.package_has_profil.profil_id
WHERE
    kiosk.profiles.id in
        (SELECT DISTINCT
            profile_id
        FROM
            kiosk.profile_has_ous
        WHERE
            ou IN (%s)
        )
AND kiosk.package_has_profil.package_uuid = '%s'
AND
    kiosk.package_has_profil.id not in(
        (SELECT
            id_package_has_profil
        FROM
            kiosk.acknowledgements
        WHERE
            id_package_has_profil = kiosk.package_has_profil.id
        AND
            kiosk.acknowledgements.askuser = '%s'
            )
    )
AND kiosk.profiles.active = 1
;""" % (
            listou,
            package_uuid,
            askuser,
        )

        try:
            result = session.execute(sql)
            session.commit()
            session.flush()
            associations = [x for x in result]

            for element in associations:
                new_acknowledge = Acknowledgements()
                new_acknowledge.id_package_has_profil = element.package_has_profil_id
                new_acknowledge.askuser = askuser
                new_acknowledge.acknowledgedbyuser = ""
                session.add(new_acknowledge)
                session.commit()
                session.flush()

            return associations
        except Exception as e:
            logging.getLogger().error("add_askacknowledge")
            logging.getLogger().error(str(e))
            return ""

    @DatabaseHelper._sessionm
    def get_profiles_name_list(self, session):
        """
        Return a list of all the existing profiles.
        The list is a shortcut of the method get_profiles_list.

        Returns:
            A list of the names for all the founded entities.
        """
        ret = session.query(Profiles.name).all()
        lines = []
        for row in ret:
            lines.append(row[0])
        return lines

    @DatabaseHelper._sessionm
    def create_profile(self, session, name, login, ous, active, packages, source):
        """
        Create a new profile for kiosk with the elements send.

        name:
            String which contains the name of the new profile
        ous:
            List of the selected OUs for this profile
        active:
            Int indicates if the profile is active (active = 1) or inactive (active = 0)
        packages:
            Dict which contains the packages associated with the profile and has the following form.
            {
                'allowed': [
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    },
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    }
                ],
                'restricted': [
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    },
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    }
                ]
            }

        return:
            The value returned is the id of the new profile
        """

        # Creation of the new profile
        import time

        now = time.strftime("%Y-%m-%d %H:%M:%S")

        sql = """INSERT INTO `kiosk`.`profiles` VALUES('%s','%s','%s', '%s', '%s', '%s');""" % (
            "0",
            name,
            login,
            source,
            active,
            now,
        )

        session.execute(sql)
        session.commit()
        session.flush()

        # Search the id of this new profile
        result = session.query(Profiles.id).filter(Profiles.name == name)
        result = result.first()
        id = 0
        for row in result:
            id = str(row)

        # Remove all packages associations concerning this profile
        session.query(Profile_has_package).filter(
            Profile_has_package.profil_id == id
        ).delete()

        # The profile is now created, but the packages are not linked to it nor added into database.
        # If the package list is not empty, then firstly we get the status and
        # the uuid for each packages
        if len(packages) > 0:
            for status in list(packages.keys()):
                for uuid in packages[status]:
                    profile = Profile_has_package()
                    profile.profil_id = id
                    profile.package_uuid = uuid
                    profile.package_status = status

                    session.add(profile)
                    session.commit()
                    session.flush()
            # Finally we associate the OUs with the profile.
            if isinstance(ous, str) and ous == "":
                profile_ou = Profile_has_ou()
                profile_ou.profile_id = id
                profile_ou.ou = ous

                session.add(profile_ou)
                session.commit()
                session.flush()

            else:
                for ou in ous:
                    profile_ou = Profile_has_ou()
                    profile_ou.profile_id = id
                    profile_ou.ou = ou

                    session.add(profile_ou)
                    session.commit()
                    session.flush()
        return id

    @DatabaseHelper._sessionm
    def refresh_package_list(self, session):
        """
        Refresh the package table, to be sure to not link the profile with deprecated packages.
        """
        # deprecated
        return
        # Get the real list of packages
        package_list = xmpp_packages_list()

        # For each package in this list, add if not exists or update existing
        # packages rows
        for ref_pkg in package_list:
            result = (
                session.query(Packages.id)
                .filter(Packages.package_uuid == ref_pkg["uuid"])
                .all()
            )

            # Create a Package object to interact with the database
            package = get_xmpp_package(ref_pkg["uuid"])
            os = list(json.loads(package).keys())[1]

            # Prepare a package object for the transaction with the database
            pkg = Packages()
            pkg.name = ref_pkg["software"]
            pkg.version_package = ref_pkg["version"]
            pkg.software = ref_pkg["software"]
            pkg.description = ref_pkg["description"]
            pkg.version_software = 0
            pkg.package_uuid = ref_pkg["uuid"]
            pkg.os = os
            # If the package is not registered into database, it is added. Else
            # it is updated
            if len(result) == 0:
                session.add(pkg)
                session.commit()
                session.flush()
            else:
                sql = """UPDATE `package` set name='%s', version_package='%s', software='%s',\
                description='%s', package_uuid='%s', os='%s' WHERE package_uuid='%s';""" % (
                    ref_pkg["software"],
                    ref_pkg["version"],
                    ref_pkg["software"],
                    ref_pkg["description"],
                    ref_pkg["uuid"],
                    os,
                    ref_pkg["uuid"],
                )

                session.execute(sql)
                session.commit()
                session.flush()

        # Now we need to verify if all the registered packages are still
        # existing into the server
        sql = """SELECT id, package_uuid FROM package;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        packages_in_db = [element for element in result]

        for package in packages_in_db:
            if package_exists(package[1]):
                pass
            else:
                session.query(Packages).filter(Packages.id == package[0]).delete()
                session.commit()
                session.flush()

    @DatabaseHelper._sessionm
    def delete_profile(self, session, id):
        """
        Delete the named profile from the table profiles.
        This method delete the profiles which have the specified name.

        Args:
            id: the id of the profile

        Returns:
            Boolean: True if success, else False
        """
        try:
            session.query(Profile_has_package).filter(
                Profile_has_package.profil_id == id
            ).delete()
            session.query(Profile_has_ou).filter(
                Profile_has_ou.profile_id == id
            ).delete()

            session.query(Profiles).filter(Profiles.id == id).delete()
            session.commit()
            session.flush()
            return True

        except Exception as e:
            return False

    @DatabaseHelper._sessionm
    def get_profile_by_id(self, session, id):
        """
        Return the profile datas and it's associated packages. This function create a view of the profile.
        id:
            Int it is the id of the wanted package
        return:
             Dict which contains the datas of the profile. The dict has this structure :
             {
                'active': '1',
                'creation_date': '2018-04-10 14:13:19',
                'id': '16',
                'ous': ['root/son/grand_son1', 'root/son/grand_son2']
                'packages': [
                    {
                        'status': 'restricted',
                        'uuid': 'df98c684-25ff-11e8-a488-0800271cd5f6',
                        'name': 'Notepad++'
                    },
                    {
                        'status': 'restricted',
                        'uuid': 'd2d143fa-3792-11e8-8364-0800278d719b',
                        'name': 'myPackage'
                    },
                    {
                        'status': 'allowed',
                        'uuid': '82c5996e-25ff-11e8-a488-0800271cd5f6',
                        'name': 'vlc'
                    },
                    {
                        'status': 'allowed',
                        'uuid': 'a6e11f44-25ff-11e8-a488-0800271cd5f6',
                        'name': 'Firefox'
                    }
                ],
                'name': 'qq'
             }
        """
        self.refresh_package_list()

        # get the profile row

        profile = session.query(Profiles).filter(Profiles.id == id).first()

        sql = """select \
        pkgs.packages.label as package_name,
        pkgs.packages.uuid as package_uuid,
        package_status
        from pkgs.packages \
        left join package_has_profil on pkgs.packages.uuid = package_has_profil.package_uuid \
        left join profiles on profiles.id = package_has_profil.profil_id\
        WHERE profiles.id = '%s';""" % (
            id
        )

        sql_ou = """SELECT ou FROM profile_has_ous WHERE profile_id = %s""" % (id)

        response = session.execute(sql)
        result = [
            {
                "uuid": element.package_uuid,
                "name": element.package_name,
                "status": element.package_status,
            }
            for element in response
        ]

        response_ou = session.execute(sql_ou)
        dict = {}

        for column in profile.__table__.columns:
            dict[column.name] = str(getattr(profile, column.name))
        dict["packages"] = result
        # generate a list for the OUs and it's added to the returned result
        dict["ous"] = [element.ou for element in response_ou]
        return dict

    @DatabaseHelper._sessionm
    def update_profile(self, session, id, name, ous, active, packages):
        """
        Update the specified profile
        id:
            Int is the id of the profile which will be updated
        name:
            String which contains the name of updated profile
        ous:
            List of the selected ous
        active:
            Int indicates if the profile is active (active = 1) or inactive (active = 0)
        packages:
            Dict which contains the packages associated with the profile and has the following form.
            {
                'allowed': [
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    },
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    }
                ],
                'restricted': [
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    },
                    {
                        'uuid': 'the-package-uuid',
                        'name': 'the-package-name'
                    }
                ]
            }
        """

        # Update the profile
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        sql = """UPDATE profiles SET name='%s',active='%s' WHERE id='%s';""" % (
            name,
            active,
            id,
        )

        session.execute(sql)
        session.commit()
        session.flush()

        # Remove all packages associations concerning this profile
        session.query(Profile_has_package).filter(
            Profile_has_package.profil_id == id
        ).delete()
        session.query(Profile_has_ou).filter(Profile_has_ou.profile_id == id).delete()

        session.commit()
        session.flush()

        # Finally we associate the OUs with the profile.
        if isinstance(ous, str) and ous == "":
            profile_ou = Profile_has_ou()
            profile_ou.profile_id = id
            profile_ou.ou = ous

            session.add(profile_ou)
            session.commit()
            session.flush()

        else:
            for ou in ous:
                profile_ou = Profile_has_ou()
                profile_ou.profile_id = id
                profile_ou.ou = ou

                session.add(profile_ou)
                session.commit()
                session.flush()

        # The profile is now created, but the packages are not linked to it nor added into database.
        # If the package list is not empty, then firstly we get the status and
        # the uuid for each packages
        if len(packages) > 0:
            for status in list(packages.keys()):
                for uuid in packages[status]:
                    profile = Profile_has_package()
                    profile.profil_id = id
                    profile.package_uuid = uuid
                    profile.package_status = status

                    session.add(profile)
                    session.commit()
                    session.flush()

    @DatabaseHelper._sessionm
    def get_acknowledges_for_sharings(
        self, session, sharings, start=0, end=-1, filter=""
    ):
        try:
            start = int(start)
        except:
            start = 0
        try:
            limit = int(limit)
        except:
            limit = -1

        sqlfilter = ""
        if filter != "":
            sqlfilter = """ WHERE pkgs.packages.label like "%%%s%%"
                OR pkgs.packages.uuid like "%%%s%%"
                OR profiles.name like "%%%s%%"
                OR acknowledgements.askuser like "%%%s%%"
                OR acknowledgements.askdate like "%%%s%%"
                OR acknowledgements.acknowledgedbyuser like "%%%s%%"
                OR acknowledgements.startdate like "%%%s%%"
                OR acknowledgements.enddate like "%%%s%%"
                OR acknowledgements.status like "%%%s%%" """ % (
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

        sqllimit = ""
        if limit != -1:
            sqllimit = "LIMIT %s, %s" % (start, limit)

        sql = """SELECT SQL_CALC_FOUND_ROWS
            pkgs.packages.label,
            pkgs.packages.uuid,
            profiles.name,
            askuser,
            askdate,
            acknowledgedbyuser,
            startdate,
            enddate,
            status,
            acknowledgements.id
        FROM acknowledgements
        JOIN package_has_profil ON acknowledgements.id_package_has_profil = package_has_profil.id
        JOIN profiles ON profiles.id = package_has_profil.profil_id
        LEFT JOIN pkgs.packages ON pkgs.packages.uuid = package_has_profil.package_uuid
        %s
        %s
        ORDER BY askdate DESC; """ % (
            sqlfilter,
            sqllimit,
        )

        sql_count = "SELECT FOUND_ROWS();"
        query = session.execute(sql)
        ret_count = session.execute(sql_count)
        count = ret_count.first()[0]
        result = {"total": count, "datas": []}

        if query is not None:
            for element in query:
                askdate = ""
                startdate = ""
                enddate = ""
                if element[4] is not None:
                    askdate = element[4].strftime("%Y-%m-%d %H:%M:%S")
                if element[6] is not None:
                    startdate = element[6].strftime("%Y-%m-%d %H:%M:%S")
                if element[7] is not None:
                    enddate = element[7].strftime("%Y-%m-%d %H:%M:%S")

                result["datas"].append(
                    {
                        "package_name": element[0] if element[0] is not None else "",
                        "package_uuid": element[1] if element[1] is not None else "",
                        "profile_name": element[2] if element[2] is not None else "",
                        "askuser": element[3] if element[3] is not None else "",
                        "askdate": askdate,
                        "acknowledgedbyuser": element[5]
                        if element[5] is not None
                        else "",
                        "startdate": startdate,
                        "enddate": enddate,
                        "status": element[8] if element[8] is not None else "",
                        "id": element[9] if element[8] is not None else "",
                    }
                )

        return result

    @DatabaseHelper._sessionm
    def get_acknowledges_for_package_profile(
        self, session, id_package_profil, uuid_package, user
    ):
        today = datetime.now()
        query = (
            session.query(Acknowledgements)
            .add_column(Profile_has_package.package_uuid)
            .filter(
                and_(
                    Acknowledgements.id_package_has_profil == id_package_profil,
                    Acknowledgements.askuser == user,
                ),
                Acknowledgements.startdate <= today.strftime("%Y-%m-%d %H:%M:%S"),
                or_(
                    Acknowledgements.enddate > today.strftime("%Y-%m-%d %H:%M:%S"),
                    Acknowledgements.enddate == None,
                    Acknowledgements.enddate == "",
                ),
            )
            .join(
                Profile_has_package,
                Profile_has_package.id == Acknowledgements.id_package_has_profil,
            )
            .all()
        )

        result = []

        if query is not None:
            for element, package_uuid in query:
                askdate = ""
                startdate = ""
                enddate = ""
                if element.askdate is not None:
                    askdate = element.askdate.strftime("%Y-%m-%d %H:%M:%S")
                if element.startdate is not None:
                    startdate = element.startdate.strftime("%Y-%m-%d %H:%M:%S")
                if element.enddate is not None:
                    enddate = element.enddate.strftime("%Y-%m-%d %H:%M:%S")

                result.append(
                    {
                        "askuser": element.askuser
                        if element.askuser is not None
                        else "",
                        "askdate": askdate,
                        "acknowledgedbyuser": element.acknowledgedbyuser
                        if element.acknowledgedbyuser is not None
                        else "",
                        "startdate": startdate,
                        "enddate": enddate,
                        "status": element.status if element.status is not None else "",
                        "id": element.id if element.id is not None else "",
                        "id_package_has_profil": element.id_package_has_profil,
                        "package_uuid": package_uuid,
                    }
                )
        return result

    @DatabaseHelper._sessionm
    def update_acknowledgement(
        self, session, id, acknowledgedbyuser, startdate, enddate, status
    ):
        query = session.query(Acknowledgements).filter(Acknowledgements.id == id)

        try:
            query = query.one()
        except:
            return False

        query.acknowledgedbyuser = acknowledgedbyuser
        query.startdate = startdate
        query.enddate = enddate
        query.status = status
        session.commit()
        session.flush()

        return True
