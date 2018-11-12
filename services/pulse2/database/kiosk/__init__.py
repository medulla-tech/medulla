# -*- coding: utf-8; -*-
#
# (c) 2018 siveo, http://www.siveo.net
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

"""
kiosk database handler
"""
# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct
from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta
# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from mmc.plugins.pkgs import get_xmpp_package, xmpp_packages_list, package_exists
from pulse2.database.kiosk.schema import Profiles, Packages, Profile_has_package, Profile_has_ou
# Imported last
import logging
import json
import time


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
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        print self.makeConnectionPath()
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
            raise "Database kiosk connection error"
        return ret

    # =====================================================================
    # kiosk FUNCTIONS
    # =====================================================================

    @DatabaseHelper._sessionm
    def get_profiles_list(self, session):
        """
        Return a list of all the existing profiles.
        The list contains all the elements of the profile.

        Returns:
            A list of all the founded entities.
        """
        ret = session.query(Profiles).all()
        lines = []
        for row in ret:
            lines.append(row.toDict())

        return lines

    @DatabaseHelper._sessionm
    def get_profile_list_for_OUList(self, session, OU):
        if len(OU) == 0:
            # return le profils par default
            return
        listou =  "('" + "','".join(OU) + "')"
        sql = """
            SELECT
                distinct
                kiosk.package.name as 'name_package',
                kiosk.profiles.name as 'name_profile',
                kiosk.package.description,
                kiosk.package.version_package,
                kiosk.package.software,
                kiosk.package.version_software,
                kiosk.package.package_uuid,
                kiosk.package.os,
                kiosk.package_has_profil.package_status
            FROM
                kiosk.package
                  inner join
                kiosk.package_has_profil on kiosk.package.id = kiosk.package_has_profil.package_id
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
                    """ % listou
        try:
            result = session.execute(sql)
            session.commit()
            session.flush()
            l = [x for x in result]
            return l
        except Exception, e:
            logging.getLogger().error("get_profile_list_for_OUList")
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
    def create_profile(self, session, name, ous, active, packages):
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

        # refresh the packages in the database
        self.refresh_package_list()

        # Creation of the new profile
        import time
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        sql = """INSERT INTO `kiosk`.`profiles` VALUES('%s','%s', '%s', '%s');""" % ('0', name, active, now)

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
        session.query(Profile_has_package).filter(Profile_has_package.profil_id == id).delete()

        # The profile is now created, but the packages are not linked to it nor added into database.
        # If the package list is not empty, then firstly we get the status and the uuid for each packages
        if len(packages) > 0 :
            for status in packages.keys():
                for uuid in packages[status]:

                    # get the package id and link it with the profile
                    result = session.query(Packages.id).filter(Packages.package_uuid == uuid)
                    result = result.first()
                    id_package = 0
                    for row in result:
                        id_package = str(row)

                    profile = Profile_has_package()
                    profile.profil_id = id
                    profile.package_id = id_package
                    profile.package_status = status

                    session.add(profile)
                    session.commit()
                    session.flush()
            # Finally we associate the OUs with the profile.
            if type(ous) == str and ous == "":
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

        # Get the real list of packages
        package_list = xmpp_packages_list()

        # For each package in this list, add if not exists or update existing packages rows
        for ref_pkg in package_list:
            result = session.query(Packages.id).filter(Packages.package_uuid == ref_pkg['uuid']).all()

            # Create a Package object to interact with the database
            package = get_xmpp_package(ref_pkg['uuid'])
            os = json.loads(package).keys()[1]

            # Prepare a package object for the transaction with the database
            pkg = Packages()
            pkg.name = ref_pkg['software']
            pkg.version_package = ref_pkg['version']
            pkg.software = ref_pkg['software']
            pkg.description = ref_pkg['description']
            pkg.version_software = 0
            pkg.package_uuid = ref_pkg['uuid']
            pkg.os = os
            # If the package is not registered into database, it is added. Else it is updated
            if len(result) == 0:
                session.add(pkg)
                session.commit()
                session.flush()
            else:
                sql = """UPDATE `package` set name='%s', version_package='%s', software='%s',\
                description='%s', package_uuid='%s', os='%s' WHERE package_uuid='%s';""" % (
                    ref_pkg['software'], ref_pkg['version'], ref_pkg['software'], ref_pkg['description'], ref_pkg['uuid'], os, ref_pkg['uuid'])

                session.execute(sql)
                session.commit()
                session.flush()

        # Now we need to verify if all the registered packages are still existing into the server
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
            session.query(Profile_has_package).filter(Profile_has_package.profil_id == id).delete()
            session.query(Profile_has_ou).filter(Profile_has_ou.profile_id == id).delete()

            session.query(Profiles).filter(Profiles.id == id).delete()
            session.commit()
            session.flush()
            return True

        except Exception, e:
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
        package.name as package_name,
        package.package_uuid,
        package_status
        from package \
        left join package_has_profil on package.id = package_has_profil.package_id \
        left join profiles on profiles.id = package_has_profil.profil_id\
        WHERE profiles.id = '%s';""" %(id)

        sql_ou = """SELECT ou FROM profile_has_ous WHERE profile_id = %s"""%(id)

        response = session.execute(sql)
        result = [{'uuid':element.package_uuid, 'name':element.package_name, 'status':element.package_status} for element in response]

        response_ou = session.execute(sql_ou)
        dict = {}

        for column in profile.__table__.columns:
            dict[column.name] = str(getattr(profile, column.name))
        dict['packages'] = result
        # generate a list for the OUs and it's added to the returned result
        dict['ous'] = [element.ou for element in response_ou]
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
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        sql = """UPDATE profiles SET name='%s',active='%s' WHERE id='%s';""" % (name, active, id)

        session.execute(sql)
        session.commit()
        session.flush()

        # Remove all packages associations concerning this profile
        session.query(Profile_has_package).filter(Profile_has_package.profil_id == id).delete()
        session.query(Profile_has_ou).filter(Profile_has_ou.profile_id == id).delete()

        session.commit()
        session.flush()

        # Finally we associate the OUs with the profile.
        if type(ous) == str and ous == "":
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
        # If the package list is not empty, then firstly we get the status and the uuid for each packages
        if len(packages) > 0:
            for status in packages.keys():
                for uuid in packages[status]:

                    # get the package id and link it with the profile
                    result = session.query(Packages.id).filter(Packages.package_uuid == uuid)
                    result = result.first()
                    id_package = 0
                    for row in result:
                        id_package = str(row)

                    profile = Profile_has_package()
                    profile.profil_id = id
                    profile.package_id = id_package
                    profile.package_status = status

                    session.add(profile)
                    session.commit()
                    session.flush()
