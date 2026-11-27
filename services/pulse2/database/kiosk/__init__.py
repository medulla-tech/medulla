# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

"""
kiosk database handler
"""
import logging
from datetime import datetime

from sqlalchemy import create_engine, MetaData, or_, text

from mmc.database.database_helper import DatabaseHelper
from pulse2.database.kiosk.schema import (
    Profiles,
    Profile_has_package,
    Profile_has_ou,
)

logger = logging.getLogger()

# Restriction of a profile inside its entity
PROFILE_SOURCES = ("entity", "ou_user", "ou_machine", "group", "ldap")
PACKAGE_STATUS = "allowed"

# Separator of GLPI complete names, and the one of the profiles stored before
# the entity_id column
ENTITY_SEPARATOR = " > "
LEGACY_ENTITY_SEPARATOR = ">>"


class KioskDatabase(DatabaseHelper):
    """
    Singleton Class to query the kiosk database.
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
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        return True

    def initMappers(self):
        return

    # =====================================================================
    # kiosk FUNCTIONS
    # =====================================================================

    @staticmethod
    def _profile_dict(profile):
        created = profile.creation_date
        return {
            "id": profile.id,
            "name": profile.name,
            "entity_id": profile.entity_id,
            "source": profile.source,
            "active": 1 if profile.active else 0,
            "creation_date": created.strftime("%Y-%m-%d %H:%M:%S") if created else "",
            "owner": profile.owner,
        }

    @DatabaseHelper._sessionm
    def get_profiles_list(self, session, entity_ids, start=0, limit=-1, filter=""):
        """Profiles of the GLPI entities; entity_ids None: every profile, the
        ones without entity included.

        Returns {"total": n, "datas": [profile]}."""
        query = session.query(Profiles)
        if entity_ids is not None:
            if not entity_ids:
                return {"total": 0, "datas": []}
            query = query.filter(Profiles.entity_id.in_(entity_ids))
        if filter:
            query = query.filter(
                or_(
                    Profiles.name.contains(str(filter), autoescape=True),
                    Profiles.creation_date.contains(str(filter), autoescape=True),
                )
            )
        total = query.count()
        query = query.order_by(Profiles.name, Profiles.id)
        try:
            start = max(int(start), 0)
            limit = int(limit)
        except (TypeError, ValueError):
            start, limit = 0, -1
        if limit > 0:
            query = query.offset(start).limit(limit)
        return {"total": total, "datas": [self._profile_dict(row) for row in query]}

    @DatabaseHelper._sessionm
    def get_profile_entities(self, session, ids):
        """{profile id: GLPI entity id or None} of the existing profiles among ids."""
        if not ids:
            return {}
        query = session.query(Profiles.id, Profiles.entity_id).filter(Profiles.id.in_(ids))
        return {row.id: row.entity_id for row in query}

    @DatabaseHelper._sessionm
    def get_profile_by_id(self, session, profile_id):
        """The profile with "ous": [str] and "packages": [{"uuid", "name"}], None
        when it does not exist."""
        profile = session.query(Profiles).filter(Profiles.id == profile_id).first()
        if profile is None:
            return None
        result = self._profile_dict(profile)
        result["ous"] = [
            row.ou
            for row in session.query(Profile_has_ou.ou)
            .filter(Profile_has_ou.profile_id == profile_id)
            .order_by(Profile_has_ou.id)
        ]
        result["packages"] = [
            {"uuid": row.uuid, "name": row.label}
            for row in session.execute(
                text("""
                    SELECT DISTINCT p.uuid, p.label
                      FROM package_has_profil php
                      JOIN pkgs.packages p ON p.uuid = php.package_uuid
                     WHERE php.profil_id = :profile_id
                     ORDER BY p.label
                    """),
                {"profile_id": profile_id},
            )
        ]
        return result

    @DatabaseHelper._sessionm
    def profile_name_exists(self, session, name, entity_id, exclude_id=None):
        """True when another profile of the entity has this name."""
        query = session.query(Profiles.id).filter(
            Profiles.name == name, Profiles.entity_id == entity_id
        )
        if exclude_id is not None:
            query = query.filter(Profiles.id != exclude_id)
        return query.first() is not None

    @staticmethod
    def _package_uuids(session, profile_id):
        query = session.query(Profile_has_package.package_uuid).filter(
            Profile_has_package.profil_id == profile_id
        )
        return list(dict.fromkeys(row.package_uuid for row in query))

    @staticmethod
    def _set_packages(session, profile_id, packages):
        session.query(Profile_has_package).filter(
            Profile_has_package.profil_id == profile_id
        ).delete(synchronize_session=False)
        for uuid in dict.fromkeys(packages):
            session.add(Profile_has_package(
                profil_id=profile_id, package_uuid=uuid, package_status=PACKAGE_STATUS
            ))

    @staticmethod
    def _set_ous(session, profile_id, ous):
        session.query(Profile_has_ou).filter(
            Profile_has_ou.profile_id == profile_id
        ).delete(synchronize_session=False)
        for ou in dict.fromkeys(ous):
            session.add(Profile_has_ou(profile_id=profile_id, ou=ou))

    @DatabaseHelper._sessionm
    def create_profile(self, session, name, entity_id, source, ous, active, packages, owner):
        """Returns the id of the new profile, False on error.

        ous: values of the source, none for "entity". packages: package uuids."""
        try:
            profile = Profiles(
                name=name,
                owner=owner,
                entity_id=entity_id,
                source=source,
                active=active,
                creation_date=datetime.now(),
            )
            session.add(profile)
            session.flush()
            self._set_packages(session, profile.id, packages)
            self._set_ous(session, profile.id, ous)
            session.commit()
            return profile.id
        except Exception as e:
            session.rollback()
            logger.error(f"kiosk: profile {name!r} not created: {e}")
            return False

    @DatabaseHelper._sessionm
    def update_profile(self, session, profile_id, name, entity_id, source, ous, active,
                       packages, visible_packages):
        """packages replaces the packages of the profile among visible_packages;
        the others are kept. Returns True when the profile is updated."""
        try:
            profile = session.query(Profiles).filter(Profiles.id == profile_id).first()
            if profile is None:
                return False
            profile.name = name
            profile.entity_id = entity_id
            profile.source = source
            profile.active = active
            kept = [uuid for uuid in self._package_uuids(session, profile_id)
                    if uuid not in visible_packages]
            self._set_packages(session, profile_id, kept + list(packages))
            self._set_ous(session, profile_id, ous)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"kiosk: profile {profile_id} not updated: {e}")
            return False

    @DatabaseHelper._sessionm
    def delete_profiles(self, session, ids):
        """Deletes the profiles with their packages and OUs; returns the ids
        actually deleted."""
        if not ids:
            return []
        try:
            deleted = [row.id for row in session.query(Profiles.id).filter(Profiles.id.in_(ids))]
            if deleted:
                session.query(Profile_has_package).filter(
                    Profile_has_package.profil_id.in_(deleted)
                ).delete(synchronize_session=False)
                session.query(Profile_has_ou).filter(
                    Profile_has_ou.profile_id.in_(deleted)
                ).delete(synchronize_session=False)
                session.query(Profiles).filter(Profiles.id.in_(deleted)).delete(
                    synchronize_session=False
                )
                session.commit()
            return deleted
        except Exception as e:
            session.rollback()
            logger.error(f"kiosk: profiles {ids} not deleted: {e}")
            return []

    @staticmethod
    def _legacy_entity_ids(profile, ous, names):
        """GLPI ids of the entities named by the OUs of a profile of source
        "entity", without those lying under another one of the list."""
        by_name = {
            name.replace(ENTITY_SEPARATOR, LEGACY_ENTITY_SEPARATOR): entity_id
            for entity_id, name in names.items()
        }
        ids = []
        for ou in ous:
            entity_id = by_name.get((ou or "").strip())
            if entity_id is None:
                logger.warning(
                    f"kiosk: profile {profile.id} ({profile.name!r}): unknown entity {ou!r}"
                )
            elif entity_id not in ids:
                ids.append(entity_id)
        return [
            entity_id for entity_id in ids
            if not any(
                names[entity_id].startswith(names[other] + ENTITY_SEPARATOR)
                for other in ids if other != entity_id
            )
        ]

    @DatabaseHelper._sessionm
    def adopt_profiles(self, session, owner_entities):
        """Gives a GLPI entity to the profiles that have none.

        Source "entity": the entities named by its OUs, one copy of the profile
        per entity after the first. Other sources: the highest entity of the
        owner, owner_entities(login) giving the GLPI ids of a user.

        Returns the number of profiles left without entity."""
        profiles = (
            session.query(Profiles)
            .filter(Profiles.entity_id.is_(None))
            .order_by(Profiles.id)
            .all()
        )
        if not profiles:
            return 0
        names = {
            int(row.id): row.completename or ""
            for row in session.execute(
                text("SELECT id, completename FROM xmppmaster.local_glpi_entities")
            )
        }
        owners = {}
        left = 0
        for profile in profiles:
            try:
                if profile.source == "entity":
                    ous = [
                        row.ou
                        for row in session.query(Profile_has_ou.ou)
                        .filter(Profile_has_ou.profile_id == profile.id)
                        .order_by(Profile_has_ou.id)
                    ]
                    entity_ids = self._legacy_entity_ids(profile, ous, names)
                else:
                    if profile.owner not in owners:
                        owners[profile.owner] = [
                            entity_id for entity_id in owner_entities(profile.owner)
                            if entity_id in names
                        ]
                    entity_ids = sorted(
                        owners[profile.owner],
                        key=lambda entity_id: (names[entity_id].count(ENTITY_SEPARATOR),
                                               entity_id),
                    )[:1]
                if not entity_ids:
                    left += 1
                    logger.warning(
                        f"kiosk: profile {profile.id} ({profile.name!r}, source "
                        f"{profile.source!r}, owner {profile.owner!r}) left without entity"
                    )
                    continue
                profile.entity_id = entity_ids[0]
                if profile.source == "entity":
                    packages = self._package_uuids(session, profile.id)
                    for entity_id in entity_ids[1:]:
                        copy = Profiles(
                            name=profile.name,
                            owner=profile.owner,
                            entity_id=entity_id,
                            source=profile.source,
                            active=profile.active,
                            creation_date=profile.creation_date,
                        )
                        session.add(copy)
                        session.flush()
                        self._set_packages(session, copy.id, packages)
                    self._set_ous(session, profile.id, [])
                session.commit()
            except Exception as e:
                session.rollback()
                left += 1
                logger.error(f"kiosk: profile {profile.id} not given an entity: {e}")
        return left
