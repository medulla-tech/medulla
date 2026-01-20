# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import create_engine, MetaData, func, desc, and_, or_, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.security.schema import (
    Tests, Cve, SoftwareCve, Scan, CveExclusion
)
import logging

logger = logging.getLogger()


class SecurityDatabase(DatabaseHelper):
    """
    Singleton Class to query the security database.
    """
    is_activated = False
    session = None
    _instance = None
    _db = None
    _config = None
    _metadata = None

    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern - return same instance"""
        if cls._instance is None:
            cls._instance = super(SecurityDatabase, cls).__new__(cls)
        return cls._instance

    def db_check(self):
        self.my_name = "security"
        self.configfile = "security.ini"
        return DatabaseHelper.db_check(self)

    @property
    def db(self):
        return SecurityDatabase._db

    @db.setter
    def db(self, value):
        SecurityDatabase._db = value

    @property
    def config(self):
        return SecurityDatabase._config

    @config.setter
    def config(self, value):
        SecurityDatabase._config = value

    @property
    def metadata(self):
        return SecurityDatabase._metadata

    @metadata.setter
    def metadata(self, value):
        SecurityDatabase._metadata = value

    def activate(self, config):
        if SecurityDatabase.is_activated:
            return None
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize
        )
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)

        # Import schema Base and bind it to the engine
        from pulse2.database.security.schema import Base as SchemaBase
        SchemaBase.metadata.bind = self.db

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        SecurityDatabase.is_activated = True
        return True

    def initMappers(self):
        """Initialize all SQLalchemy mappers needed for the database"""
        return

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError as e:
                logger.error(e)
            except Exception as e:
                logger.error(e)
            if ret:
                break
        if not ret:
            raise Exception("Database security connection error")
        return ret

    # =========================================================================
    # Entity filtering helper
    # =========================================================================
    def _parse_entity_ids(self, session, location):
        """
        Parse location parameter and return list of entity IDs for filtering.
        Location can be:
        - Empty string: no filter (all entities)
        - Single UUID: one entity
        - Comma-separated UUIDs: multiple entities

        Returns list of entity_id integers, or None if no filter.
        """
        if not location or location.strip() == '':
            return None

        try:
            # Split by comma if multiple UUIDs
            uuids = [u.strip() for u in location.split(',') if u.strip()]
            if not uuids:
                return None

            # Convert UUIDs to entity IDs
            # UUID format is typically "UUID<number>" - extract the number
            entity_ids = []
            for uuid in uuids:
                if uuid.startswith('UUID'):
                    try:
                        entity_id = int(uuid[4:])
                        entity_ids.append(entity_id)
                    except ValueError:
                        logger.warning(f"Invalid entity UUID format: {uuid}")
                else:
                    # Try direct integer
                    try:
                        entity_ids.append(int(uuid))
                    except ValueError:
                        logger.warning(f"Invalid entity ID format: {uuid}")

            return entity_ids if entity_ids else None
        except Exception as e:
            logger.error(f"Error parsing entity location: {e}")
            return None

    # =========================================================================
    # Tests (legacy)
    # =========================================================================
    @DatabaseHelper._sessionm
    def tests(self, session):
        ret = session.query(Tests).all()
        return [row.toDict() for row in ret]

    # =========================================================================
    # Dashboard / Summary
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_dashboard_summary(self, session, location=''):
        """Get summary for dashboard: counts by severity, machines affected
        Filtered by entity if location is provided.
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Build entity filter clause for machines
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        # Count CVEs by severity (only CVEs affecting machines in selected entities)
        # Platform filter: exclude CVEs targeting mobile (android, ios) or macos for Windows/Linux machines
        # target_platform values from CPE: android, macos, ios, iphone_os, etc.
        # Join using glpi_software_name which is the original GLPI software name
        counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'None': 0}
        try:
            result = session.execute(text(f"""
                SELECT c.severity, COUNT(DISTINCT c.id) as cnt
                FROM security.cves c
                JOIN security.software_cves sc ON sc.cve_id = c.id
                JOIN xmppmaster.local_glpi_softwares s ON s.name = sc.glpi_software_name
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                LEFT JOIN xmppmaster.machines xm ON xm.id_glpi = m.id
                WHERE 1=1 {entity_filter}
                AND (
                    sc.target_platform IS NULL
                    OR sc.target_platform = ''
                    OR (
                        -- Windows machine: exclude macos, android, ios CVEs
                        xm.platform LIKE '%Windows%'
                        AND sc.target_platform NOT IN ('macos', 'android', 'ios', 'iphone_os')
                    )
                    OR (
                        -- Linux machine: exclude macos, android, ios, windows CVEs
                        (xm.platform LIKE '%Linux%' OR xm.platform LIKE '%Debian%' OR xm.platform LIKE '%Ubuntu%')
                        AND sc.target_platform NOT IN ('macos', 'android', 'ios', 'iphone_os', 'windows')
                    )
                    OR (
                        -- macOS machine: exclude android, ios, windows CVEs
                        (xm.platform LIKE '%macOS%' OR xm.platform LIKE '%Mac%')
                        AND sc.target_platform NOT IN ('android', 'ios', 'iphone_os', 'windows')
                    )
                )
                GROUP BY c.severity
            """))
            for row in result:
                if row[0] in counts:
                    counts[row[0]] = row[1]
        except Exception as e:
            logger.error(f"Error counting CVEs by severity: {e}")

        # Count affected machines
        # With platform filtering to exclude CVEs that don't match machine OS
        # Join using glpi_software_name
        machines_affected = 0
        try:
            result = session.execute(text(f"""
                SELECT COUNT(DISTINCT m.id) as count
                FROM security.software_cves sc
                JOIN xmppmaster.local_glpi_softwares s ON s.name = sc.glpi_software_name
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                LEFT JOIN xmppmaster.machines xm ON xm.id_glpi = m.id
                WHERE 1=1 {entity_filter}
                AND (
                    sc.target_platform IS NULL
                    OR sc.target_platform = ''
                    OR (
                        xm.platform LIKE '%Windows%'
                        AND sc.target_platform NOT IN ('macos', 'android', 'ios', 'iphone_os')
                    )
                    OR (
                        (xm.platform LIKE '%Linux%' OR xm.platform LIKE '%Debian%' OR xm.platform LIKE '%Ubuntu%')
                        AND sc.target_platform NOT IN ('macos', 'android', 'ios', 'iphone_os', 'windows')
                    )
                    OR (
                        (xm.platform LIKE '%macOS%' OR xm.platform LIKE '%Mac%')
                        AND sc.target_platform NOT IN ('android', 'ios', 'iphone_os', 'windows')
                    )
                )
            """))
            row = result.fetchone()
            if row:
                machines_affected = row[0]
        except Exception as e:
            logger.error(f"Error counting affected machines: {e}")

        # Last scan info
        last_scan = session.query(Scan).order_by(desc(Scan.started_at)).first()
        last_scan_info = None
        if last_scan:
            last_scan_info = {
                'id': last_scan.id,
                'started_at': last_scan.started_at.isoformat() if last_scan.started_at else None,
                'finished_at': last_scan.finished_at.isoformat() if last_scan.finished_at else None,
                'status': last_scan.status,
                'softwares_sent': last_scan.softwares_sent,
                'cves_received': last_scan.cves_received,
                'machines_affected': last_scan.machines_affected
            }

        return {
            'total_cves': sum(counts.values()),
            'critical': counts['Critical'],
            'high': counts['High'],
            'medium': counts['Medium'],
            'low': counts['Low'],
            'machines_affected': machines_affected,
            'last_scan': last_scan_info
        }

    # =========================================================================
    # CVE List (toutes les CVEs connues pour les logiciels du parc)
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_cves(self, session, start=0, limit=50, filter_str='',
                 severity=None, location='', sort_by='cvss_score', sort_order='desc'):
        """Get paginated list of CVEs with affected machine count
        Filtered by entity if location is provided.
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Build entity filter clause for machines
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        # Build filter clauses
        cve_filters = []
        if severity:
            cve_filters.append(f"c.severity = '{severity}'")
        if filter_str:
            escaped_filter = filter_str.replace("'", "''")
            cve_filters.append(f"(c.cve_id LIKE '%{escaped_filter}%' OR c.description LIKE '%{escaped_filter}%')")

        # Platform filter condition (exclude CVEs targeting wrong platform)
        platform_filter = """(
            sc.target_platform IS NULL
            OR sc.target_platform = ''
            OR (
                xm.platform LIKE '%Windows%'
                AND sc.target_platform NOT IN ('macos', 'android', 'ios', 'iphone_os')
            )
            OR (
                (xm.platform LIKE '%Linux%' OR xm.platform LIKE '%Debian%' OR xm.platform LIKE '%Ubuntu%')
                AND sc.target_platform NOT IN ('macos', 'android', 'ios', 'iphone_os', 'windows')
            )
            OR (
                (xm.platform LIKE '%macOS%' OR xm.platform LIKE '%Mac%')
                AND sc.target_platform NOT IN ('android', 'ios', 'iphone_os', 'windows')
            )
        )"""

        # Build complete WHERE clause
        where_conditions = [platform_filter]
        if cve_filters:
            where_conditions.extend(cve_filters)
        cve_where_clause = "AND " + " AND ".join(where_conditions)

        # Get CVEs that affect machines in selected entities
        # Join using glpi_software_name
        try:
            # Count total matching CVEs
            count_sql = text(f"""
                SELECT COUNT(DISTINCT c.id) as total
                FROM security.cves c
                JOIN security.software_cves sc ON sc.cve_id = c.id
                JOIN xmppmaster.local_glpi_softwares s ON s.name = sc.glpi_software_name
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                LEFT JOIN xmppmaster.machines xm ON xm.id_glpi = m.id
                WHERE 1=1 {entity_filter}
                {cve_where_clause}
            """)
            count_result = session.execute(count_sql)
            total = count_result.scalar() or 0

            # Get paginated CVE list with machine counts
            sort_dir = "DESC" if sort_order == 'desc' else "ASC"
            main_sql = text(f"""
                SELECT
                    c.id, c.cve_id, c.cvss_score, c.severity, c.description, c.published_at,
                    COUNT(DISTINCT m.id) as machines_affected
                FROM security.cves c
                JOIN security.software_cves sc ON sc.cve_id = c.id
                JOIN xmppmaster.local_glpi_softwares s ON s.name = sc.glpi_software_name
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                LEFT JOIN xmppmaster.machines xm ON xm.id_glpi = m.id
                WHERE 1=1 {entity_filter}
                {cve_where_clause}
                GROUP BY c.id, c.cve_id, c.cvss_score, c.severity, c.description, c.published_at
                ORDER BY c.cvss_score {sort_dir}
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, {'start': start, 'limit': limit})
            results = []
            for row in result:
                # Get affected software for this CVE
                sw_cves = session.query(SoftwareCve).filter(
                    SoftwareCve.cve_id == row.id
                ).all()
                softwares = [{'name': sc.software_name, 'version': sc.software_version}
                            for sc in sw_cves]

                results.append({
                    'id': row.id,
                    'cve_id': row.cve_id,
                    'cvss_score': float(row.cvss_score) if row.cvss_score else 0.0,
                    'severity': row.severity,
                    'description': row.description,
                    'published_at': row.published_at.isoformat() if row.published_at else None,
                    'softwares': softwares,
                    'machines_affected': row.machines_affected
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting CVEs: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_cve_details(self, session, cve_id_str, location=''):
        """Get details of a CVE including affected machines
        Filtered by entity if location is provided.
        """
        cve = session.query(Cve).filter(Cve.cve_id == cve_id_str).first()
        if not cve:
            return None

        # Parse entity filter
        entity_ids = self._parse_entity_ids(session, location)
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        # Get software linked to this CVE
        sw_cves = session.query(SoftwareCve).filter(
            SoftwareCve.cve_id == cve.id
        ).all()

        softwares = [{'name': sc.software_name, 'version': sc.software_version}
                    for sc in sw_cves]

        # Get affected machines (unique, only latest software versions)
        # Filtered by entity if location is provided
        # Include software_name and software_version for each machine
        machines = []
        if softwares:
            try:
                conditions = []
                for sw in softwares:
                    sw_name = sw['name'].replace("'", "''")
                    sw_ver = sw['version'].replace("'", "''")
                    conditions.append(f"(latest_sw.software_name = '{sw_name}' AND latest_sw.software_version = '{sw_ver}')")

                if conditions:
                    where_clause = " OR ".join(conditions)
                    result = session.execute(text(f"""
                        SELECT latest_sw.machine_id, m.name as hostname,
                               latest_sw.software_name, latest_sw.software_version
                        FROM (
                            SELECT isv.items_id as machine_id, s.name as software_name,
                                   SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                            FROM xmppmaster.local_glpi_items_softwareversions isv
                            JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                            JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                            JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                            WHERE 1=1 {entity_filter}
                            GROUP BY isv.items_id, s.name
                        ) latest_sw
                        JOIN xmppmaster.local_glpi_machines m ON m.id = latest_sw.machine_id
                        WHERE ({where_clause}) {entity_filter}
                        ORDER BY m.name, latest_sw.software_name
                    """))
                    for row in result:
                        machines.append({
                            'id_glpi': row[0],
                            'hostname': row[1],
                            'software_name': row[2],
                            'software_version': row[3]
                        })
            except Exception as e:
                logger.error(f"Error getting machines for CVE {cve_id_str}: {e}")

        return {
            'id': cve.id,
            'cve_id': cve.cve_id,
            'cvss_score': float(cve.cvss_score) if cve.cvss_score else 0.0,
            'severity': cve.severity,
            'description': cve.description,
            'published_at': cve.published_at.isoformat() if cve.published_at else None,
            'last_modified': cve.last_modified.isoformat() if cve.last_modified else None,
            'fetched_at': cve.fetched_at.isoformat() if cve.fetched_at else None,
            'softwares': softwares,
            'machines': machines
        }

    # =========================================================================
    # Machine-centric view
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_machines_summary(self, session, start=0, limit=50, filter_str='', location=''):
        """Get list of ALL machines from GLPI with vulnerability counts (only latest software versions)
        Filtered by entity if location is provided.
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Build WHERE clauses
        where_clauses = []
        params = {'start': start, 'limit': limit}

        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            where_clauses.append(f"m.entities_id IN ({entity_ids_str})")

        if filter_str:
            where_clauses.append("m.name LIKE :filter")
            params['filter'] = f"%{filter_str}%"

        filter_clause = ""
        if where_clauses:
            filter_clause = "WHERE " + " AND ".join(where_clauses)

        # Count query
        count_sql = text(f"""
            SELECT COUNT(*) as total
            FROM xmppmaster.local_glpi_machines m
            {filter_clause}
        """)

        # Main query with vulnerability counts (only most recent version per software)
        main_sql = text(f"""
            SELECT
                m.id as id_glpi,
                m.name as hostname,
                COALESCE(v.total_cves, 0) as total_cves,
                COALESCE(v.critical, 0) as critical,
                COALESCE(v.high, 0) as high,
                COALESCE(v.medium, 0) as medium,
                COALESCE(v.max_cvss, 0) as risk_score
            FROM xmppmaster.local_glpi_machines m
            LEFT JOIN (
                SELECT
                    latest_sw.machine_id,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    MAX(c.cvss_score) as max_cvss
                FROM (
                    SELECT isv.items_id as machine_id, s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    GROUP BY isv.items_id, s.name
                ) latest_sw
                JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                AND sc.software_version = latest_sw.software_version
                JOIN security.cves c ON c.id = sc.cve_id
                GROUP BY latest_sw.machine_id
            ) v ON m.id = v.machine_id
            {filter_clause}
            ORDER BY v.max_cvss DESC, m.name ASC
            LIMIT :limit OFFSET :start
        """)

        try:
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            result = session.execute(main_sql, params)
            results = []
            for row in result:
                results.append({
                    'id_glpi': row.id_glpi,
                    'hostname': row.hostname,
                    'total_cves': int(row.total_cves),
                    'critical': int(row.critical),
                    'high': int(row.high),
                    'medium': int(row.medium),
                    'risk_score': float(row.risk_score) if row.risk_score else 0.0
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting machines summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_machine_cves(self, session, id_glpi, start=0, limit=50, filter_str='', severity=None):
        """Get all CVEs affecting a specific machine (only latest software versions)

        Args:
            id_glpi: GLPI machine ID
            start: Pagination offset
            limit: Max results per page
            filter_str: Search filter for CVE ID or description
            severity: Filter by severity (Critical, High, Medium, Low)

        Returns:
            dict with 'total' count and 'data' list
        """
        try:
            # Build WHERE clause for filters
            where_clauses = []
            params = {'id_glpi': id_glpi, 'start': start, 'limit': limit}

            if filter_str:
                where_clauses.append("(c.cve_id LIKE :filter OR c.description LIKE :filter)")
                params['filter'] = f"%{filter_str}%"

            if severity:
                where_clauses.append("c.severity = :severity")
                params['severity'] = severity

            where_sql = ""
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)

            # Count query
            count_sql = text(f"""
                SELECT COUNT(DISTINCT c.id) as total
                FROM (
                    SELECT s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    WHERE isv.items_id = :id_glpi
                    GROUP BY s.name
                ) latest_sw
                JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                AND sc.software_version = latest_sw.software_version
                JOIN security.cves c ON c.id = sc.cve_id
                {where_sql}
            """)

            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query with pagination - group by CVE to avoid duplicates
            main_sql = text(f"""
                SELECT
                    c.cve_id,
                    c.cvss_score,
                    c.severity,
                    c.description,
                    c.published_at,
                    c.last_modified,
                    GROUP_CONCAT(DISTINCT latest_sw.software_name ORDER BY latest_sw.software_name SEPARATOR ', ') as software_name,
                    GROUP_CONCAT(DISTINCT latest_sw.software_version ORDER BY latest_sw.software_name SEPARATOR ', ') as software_version
                FROM (
                    SELECT s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    WHERE isv.items_id = :id_glpi
                    GROUP BY s.name
                ) latest_sw
                JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                AND sc.software_version = latest_sw.software_version
                JOIN security.cves c ON c.id = sc.cve_id
                {where_sql}
                GROUP BY c.id, c.cve_id, c.cvss_score, c.severity, c.description, c.published_at, c.last_modified
                ORDER BY c.cvss_score DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)

            cves = []
            for row in result:
                cves.append({
                    'cve_id': row.cve_id,
                    'cvss_score': float(row.cvss_score) if row.cvss_score else 0.0,
                    'severity': row.severity,
                    'description': row.description,
                    'published_at': str(row.published_at) if row.published_at else None,
                    'last_modified': str(row.last_modified) if row.last_modified else None,
                    'software_name': row.software_name,
                    'software_version': row.software_version
                })

            return {'total': total, 'data': cves}
        except Exception as e:
            logger.error(f"Error getting CVEs for machine {id_glpi}: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_machine_softwares_summary(self, session, id_glpi, start=0, limit=50, filter_str=''):
        """Get vulnerable software summary for a specific machine, grouped by software.

        Args:
            id_glpi: GLPI machine ID
            start: Pagination offset
            limit: Max results per page
            filter_str: Search filter for software name

        Returns:
            dict with 'total' count and 'data' list (grouped by software)
        """
        try:
            params = {'id_glpi': id_glpi, 'start': start, 'limit': limit}

            filter_clause = ""
            if filter_str:
                filter_clause = "AND latest_sw.software_name LIKE :filter"
                params['filter'] = f"%{filter_str}%"

            # Count query - number of distinct vulnerable software
            count_sql = text(f"""
                SELECT COUNT(DISTINCT CONCAT(latest_sw.software_name, ':', latest_sw.software_version)) as total
                FROM (
                    SELECT s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    WHERE isv.items_id = :id_glpi
                    GROUP BY s.name
                ) latest_sw
                JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                AND sc.software_version = latest_sw.software_version
                WHERE 1=1 {filter_clause}
            """)

            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query - group by software with CVE counts
            main_sql = text(f"""
                SELECT
                    latest_sw.software_name,
                    latest_sw.software_version,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                    MAX(c.cvss_score) as max_cvss
                FROM (
                    SELECT s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    WHERE isv.items_id = :id_glpi
                    GROUP BY s.name
                ) latest_sw
                JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                AND sc.software_version = latest_sw.software_version
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE 1=1 {filter_clause}
                GROUP BY latest_sw.software_name, latest_sw.software_version
                ORDER BY max_cvss DESC, total_cves DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)

            data = []
            for row in result:
                data.append({
                    'software_name': row.software_name,
                    'software_version': row.software_version,
                    'total_cves': int(row.total_cves),
                    'critical': int(row.critical),
                    'high': int(row.high),
                    'medium': int(row.medium),
                    'low': int(row.low),
                    'max_cvss': float(row.max_cvss) if row.max_cvss else 0.0
                })

            return {'total': total, 'data': data}
        except Exception as e:
            logger.error(f"Error getting software summary for machine {id_glpi}: {e}")
            return {'total': 0, 'data': []}

    # =========================================================================
    # CVE Management (add/update from scanner)
    # =========================================================================
    @DatabaseHelper._sessionm
    def add_cve(self, session, cve_id, cvss_score, severity, description, published_at=None, last_modified=None):
        """Add or update a CVE in local cache"""
        cve = session.query(Cve).filter(Cve.cve_id == cve_id).first()

        if cve:
            # Update existing
            cve.cvss_score = cvss_score
            cve.severity = severity
            cve.description = description
            if published_at:
                cve.published_at = published_at
            if last_modified:
                cve.last_modified = last_modified
            cve.fetched_at = datetime.utcnow()
        else:
            # Create new
            cve = Cve(
                cve_id=cve_id,
                cvss_score=cvss_score,
                severity=severity,
                description=description,
                published_at=published_at,
                last_modified=last_modified
            )
            session.add(cve)

        session.commit()
        return cve.id

    @DatabaseHelper._sessionm
    def link_software_cve(self, session, software_name, software_version, cve_db_id,
                          glpi_software_name=None, target_platform=None):
        """Link a software to a CVE.

        Args:
            software_name: Normalized name (e.g., "Python")
            software_version: Normalized version (e.g., "3.11.9")
            cve_db_id: CVE database ID
            glpi_software_name: Original GLPI software name for joining with GLPI tables
            target_platform: Target platform from CPE (android, macos, ios, windows, etc.)
        """
        existing = session.query(SoftwareCve).filter(
            and_(
                SoftwareCve.software_name == software_name,
                SoftwareCve.software_version == software_version,
                SoftwareCve.cve_id == cve_db_id
            )
        ).first()

        if not existing:
            link = SoftwareCve(
                software_name=software_name,
                software_version=software_version,
                glpi_software_name=glpi_software_name,
                target_platform=target_platform,
                cve_id=cve_db_id
            )
            session.add(link)
            session.commit()
            return link.id
        else:
            # Update existing record with new fields if not set
            updated = False
            if glpi_software_name and not existing.glpi_software_name:
                existing.glpi_software_name = glpi_software_name
                updated = True
            if target_platform and not existing.target_platform:
                existing.target_platform = target_platform
                updated = True
            if updated:
                session.commit()
        return existing.id

    # =========================================================================
    # Scans history
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_scans(self, session, start=0, limit=20):
        """Get scan history"""
        # Count total
        count_result = session.execute(text("SELECT COUNT(*) FROM scans"))
        total = count_result.scalar() or 0

        # Get paginated data
        result = session.execute(
            text("""SELECT id, started_at, finished_at, status,
                    softwares_sent, cves_received, machines_affected, error_message
                    FROM scans ORDER BY started_at DESC
                    LIMIT :limit OFFSET :start"""),
            {'limit': limit, 'start': start}
        )

        data = []
        for row in result:
            data.append({
                'id': row[0],
                'started_at': str(row[1]) if row[1] else None,
                'finished_at': str(row[2]) if row[2] else None,
                'status': row[3],
                'softwares_sent': row[4] or 0,
                'cves_received': row[5] or 0,
                'machines_affected': row[6] or 0,
                'error_message': row[7]
            })

        return {'total': total, 'data': data}

    @DatabaseHelper._sessionm
    def create_scan(self, session):
        """Create a new scan entry"""
        result = session.execute(
            text("INSERT INTO scans (started_at, status) VALUES (NOW(), 'running')")
        )
        session.commit()
        # Get the last inserted ID - use lastrowid which is more reliable after TRUNCATE
        scan_id = result.lastrowid
        if not scan_id:
            # Fallback: query the max id
            id_result = session.execute(text("SELECT MAX(id) FROM scans"))
            scan_id = id_result.scalar() or 0
        return scan_id

    @DatabaseHelper._sessionm
    def complete_scan(self, session, scan_id, softwares_sent, cves_received,
                     machines_affected=0, error_message=None):
        """Complete a scan"""
        status = 'failed' if error_message else 'completed'
        session.execute(
            text("""UPDATE scans SET
                    finished_at = NOW(),
                    status = :status,
                    softwares_sent = :softwares_sent,
                    cves_received = :cves_received,
                    machines_affected = :machines_affected,
                    error_message = :error_message
                    WHERE id = :scan_id"""),
            {
                'status': status,
                'softwares_sent': softwares_sent,
                'cves_received': cves_received,
                'machines_affected': machines_affected,
                'error_message': error_message,
                'scan_id': scan_id
            }
        )
        session.commit()
        return True

    # =========================================================================
    # Configuration
    # =========================================================================
    # NOTE: Configuration is now read from /etc/mmc/plugins/security.ini and security.ini.local
    # Use mmc.plugins.security.get_config() instead of database methods

    # =========================================================================
    # Exclusions
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_exclusions(self, session):
        """Get list of excluded CVEs"""
        exclusions = session.query(CveExclusion).all()
        return [e.toDict() for e in exclusions]

    @DatabaseHelper._sessionm
    def add_exclusion(self, session, cve_id, reason, user, expires_at=None):
        """Add a CVE to exclusion list"""
        exclusion = CveExclusion(
            cve_id=cve_id,
            reason=reason,
            excluded_by=user,
            expires_at=expires_at
        )
        session.add(exclusion)
        session.commit()
        return exclusion.id

    @DatabaseHelper._sessionm
    def remove_exclusion(self, session, cve_id):
        """Remove a CVE from exclusion list"""
        session.query(CveExclusion).filter(CveExclusion.cve_id == cve_id).delete()
        session.commit()
        return True

    @DatabaseHelper._sessionm
    def is_excluded(self, session, cve_id):
        """Check if a CVE is excluded"""
        exclusion = session.query(CveExclusion).filter(
            and_(
                CveExclusion.cve_id == cve_id,
                or_(
                    CveExclusion.expires_at.is_(None),
                    CveExclusion.expires_at > datetime.utcnow()
                )
            )
        ).first()
        return exclusion is not None

    # =========================================================================
    # Software-centric view
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_softwares_summary(self, session, start=0, limit=50, filter_str='', location=''):
        """Get list of softwares with CVE counts, grouped by software name+version.
        Filtered by entity if location is provided.

        Returns:
            dict with 'total' count and 'data' list containing:
            - software_name, software_version (normalized names for display)
            - total_cves, critical, high, medium, low
            - max_cvss (highest CVSS score for this software)
            - machines_affected (count of machines with this software)

        Note: Uses glpi_software_name for joining with GLPI tables (original name),
        but displays normalized software_name for clarity (e.g., "Python" instead of
        "Python 3.11.9 (64-bit)").
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Build entity filter clause for machines
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        # Build filter clause (search on normalized name for user convenience)
        filter_clause = ""
        params = {'start': start, 'limit': limit}
        if filter_str:
            filter_clause = "AND (sc.software_name LIKE :filter OR sc.software_version LIKE :filter)"
            params['filter'] = f"%{filter_str}%"

        try:
            # Count total distinct software+version with CVEs
            # Use glpi_software_name for joining with GLPI, fallback to software_name if null
            count_sql = text(f"""
                SELECT COUNT(DISTINCT CONCAT(sc.software_name, '|', sc.software_version)) as total
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                JOIN (
                    SELECT DISTINCT s.name as glpi_software_name
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                    WHERE 1=1 {entity_filter}
                ) glpi_sw ON COALESCE(sc.glpi_software_name, sc.software_name) = glpi_sw.glpi_software_name
                WHERE 1=1 {filter_clause}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query: software grouped with CVE counts
            # Join using glpi_software_name but display normalized software_name
            main_sql = text(f"""
                SELECT
                    sc.software_name,
                    sc.software_version,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                    MAX(c.cvss_score) as max_cvss,
                    COUNT(DISTINCT glpi_sw.machine_id) as machines_affected
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                JOIN (
                    SELECT isv.items_id as machine_id, s.name as glpi_software_name
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                    WHERE 1=1 {entity_filter}
                ) glpi_sw ON COALESCE(sc.glpi_software_name, sc.software_name) = glpi_sw.glpi_software_name
                WHERE 1=1 {filter_clause}
                GROUP BY sc.software_name, sc.software_version
                ORDER BY max_cvss DESC, total_cves DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            results = []
            for row in result:
                results.append({
                    'software_name': row.software_name,
                    'software_version': row.software_version,
                    'total_cves': int(row.total_cves),
                    'critical': int(row.critical),
                    'high': int(row.high),
                    'medium': int(row.medium),
                    'low': int(row.low),
                    'max_cvss': float(row.max_cvss) if row.max_cvss else 0.0,
                    'machines_affected': int(row.machines_affected)
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting softwares summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_entities_summary(self, session, start=0, limit=50, filter_str='', user_entities=''):
        """Get list of entities with CVE counts.
        Filtered by user's accessible entities if user_entities is provided.

        Returns:
            dict with 'total' count and 'data' list containing:
            - entity_id, entity_name
            - total_cves, critical, high, medium, low
            - max_cvss, machines_count
        """
        try:
            # Build filter clause
            filter_clause = ""
            params = {'start': start, 'limit': limit}
            if filter_str:
                filter_clause = "AND e.name LIKE :filter"
                params['filter'] = f"%{filter_str}%"

            # Filter by user's accessible entities
            entity_ids = self._parse_entity_ids(session, user_entities)
            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                filter_clause += f" AND e.id IN ({entity_ids_str})"

            # Count total entities
            count_sql = text(f"""
                SELECT COUNT(DISTINCT e.id) as total
                FROM xmppmaster.local_glpi_entities e
                WHERE 1=1 {filter_clause}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query: entities with CVE counts
            main_sql = text(f"""
                SELECT
                    e.id as entity_id,
                    e.name as entity_name,
                    e.completename as entity_fullname,
                    COUNT(DISTINCT m.id) as machines_count,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                    COALESCE(MAX(c.cvss_score), 0) as max_cvss
                FROM xmppmaster.local_glpi_entities e
                LEFT JOIN xmppmaster.local_glpi_machines m ON m.entities_id = e.id
                LEFT JOIN (
                    SELECT isv.items_id as machine_id, s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    GROUP BY isv.items_id, s.name
                ) latest_sw ON latest_sw.machine_id = m.id
                LEFT JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                    AND sc.software_version = latest_sw.software_version
                LEFT JOIN security.cves c ON c.id = sc.cve_id
                WHERE 1=1 {filter_clause}
                GROUP BY e.id, e.name, e.completename
                ORDER BY max_cvss DESC, total_cves DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            results = []
            for row in result:
                results.append({
                    'entity_id': row.entity_id,
                    'entity_name': row.entity_name,
                    'entity_fullname': row.entity_fullname or row.entity_name,
                    'machines_count': int(row.machines_count),
                    'total_cves': int(row.total_cves),
                    'critical': int(row.critical),
                    'high': int(row.high),
                    'medium': int(row.medium),
                    'low': int(row.low),
                    'max_cvss': float(row.max_cvss) if row.max_cvss else 0.0
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting entities summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_groups_summary(self, session, start=0, limit=50, filter_str='', user_login=''):
        """Get list of groups with CVE counts.
        Filtered by ShareGroup - only show groups shared with this user.

        Returns:
            dict with 'total' count and 'data' list containing:
            - group_id, group_name, group_type
            - total_cves, critical, high, medium, low
            - max_cvss, machines_count
        """
        try:
            # Build filter clause - exclude internal PULSE groups
            filter_clause = "AND g.name NOT LIKE 'PULSE_INTERNAL%'"
            params = {'start': start, 'limit': limit}
            if filter_str:
                filter_clause += " AND g.name LIKE :filter"
                params['filter'] = f"%{filter_str}%"

            # Filter by ShareGroup - only show groups shared with this user
            share_filter = ""
            if user_login:
                # Escape the login for SQL
                escaped_login = user_login.replace("'", "''")
                share_filter = f"""AND g.id IN (
                    SELECT DISTINCT sg.FK_groups
                    FROM dyngroup.ShareGroup sg
                    JOIN dyngroup.Users u ON u.id = sg.FK_users
                    WHERE u.login = '{escaped_login}'
                )"""

            # Count total groups (excluding internal, filtered by share)
            count_sql = text(f"""
                SELECT COUNT(DISTINCT g.id) as total
                FROM dyngroup.Groups g
                WHERE 1=1 {filter_clause} {share_filter}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query: groups with CVE counts
            # Results table links groups (FK_groups) to machines (FK_machines)
            # Machines table has uuid that matches local_glpi_machines
            main_sql = text(f"""
                SELECT
                    g.id as group_id,
                    g.name as group_name,
                    g.type as group_type,
                    COUNT(DISTINCT m.id) as machines_count,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                    COALESCE(MAX(c.cvss_score), 0) as max_cvss
                FROM dyngroup.Groups g
                LEFT JOIN dyngroup.Results r ON r.FK_groups = g.id
                LEFT JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                LEFT JOIN xmppmaster.local_glpi_machines m ON CONCAT('UUID', m.id) = dm.uuid
                LEFT JOIN (
                    SELECT isv.items_id as machine_id, s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    GROUP BY isv.items_id, s.name
                ) latest_sw ON latest_sw.machine_id = m.id
                LEFT JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                    AND sc.software_version = latest_sw.software_version
                LEFT JOIN security.cves c ON c.id = sc.cve_id
                WHERE 1=1 {filter_clause} {share_filter}
                GROUP BY g.id, g.name, g.type
                ORDER BY max_cvss DESC, total_cves DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            results = []
            for row in result:
                group_type_label = 'Static' if row.group_type == 0 else 'Dynamic'
                results.append({
                    'group_id': row.group_id,
                    'group_name': row.group_name,
                    'group_type': group_type_label,
                    'machines_count': int(row.machines_count),
                    'total_cves': int(row.total_cves),
                    'critical': int(row.critical),
                    'high': int(row.high),
                    'medium': int(row.medium),
                    'low': int(row.low),
                    'max_cvss': float(row.max_cvss) if row.max_cvss else 0.0
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting groups summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_group_machines(self, session, group_id, start=0, limit=50, filter_str=''):
        """Get machines in a group with their CVE counts.

        Returns:
            dict with 'total' count and 'data' list
        """
        try:
            # Build filter clause
            filter_clause = ""
            params = {'group_id': group_id, 'start': start, 'limit': limit}
            if filter_str:
                filter_clause = "AND m.name LIKE :filter"
                params['filter'] = f"%{filter_str}%"

            # Count total machines in group
            # Results table links groups (FK_groups) to machines (FK_machines)
            count_sql = text(f"""
                SELECT COUNT(DISTINCT m.id) as total
                FROM dyngroup.Results r
                JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                JOIN xmppmaster.local_glpi_machines m ON CONCAT('UUID', m.id) = dm.uuid
                WHERE r.FK_groups = :group_id {filter_clause}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query: machines with CVE counts
            main_sql = text(f"""
                SELECT
                    m.id as id_glpi,
                    m.name as hostname,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COALESCE(MAX(c.cvss_score), 0) as risk_score
                FROM dyngroup.Results r
                JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                JOIN xmppmaster.local_glpi_machines m ON CONCAT('UUID', m.id) = dm.uuid
                LEFT JOIN (
                    SELECT isv.items_id as machine_id, s.name as software_name,
                           SUBSTRING_INDEX(GROUP_CONCAT(sv.name ORDER BY isv.id DESC), ',', 1) as software_version
                    FROM xmppmaster.local_glpi_items_softwareversions isv
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    GROUP BY isv.items_id, s.name
                ) latest_sw ON latest_sw.machine_id = m.id
                LEFT JOIN security.software_cves sc ON sc.software_name = latest_sw.software_name
                                                    AND sc.software_version = latest_sw.software_version
                LEFT JOIN security.cves c ON c.id = sc.cve_id
                WHERE r.FK_groups = :group_id {filter_clause}
                GROUP BY m.id, m.name
                ORDER BY risk_score DESC, m.name ASC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            results = []
            for row in result:
                results.append({
                    'id_glpi': row.id_glpi,
                    'hostname': row.hostname,
                    'total_cves': int(row.total_cves),
                    'critical': int(row.critical),
                    'high': int(row.high),
                    'medium': int(row.medium),
                    'risk_score': float(row.risk_score) if row.risk_score else 0.0
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting group machines: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_software_cves(self, session, software_name, software_version, start=0, limit=50,
                          filter_str='', severity=None):
        """Get all CVEs affecting a specific software version.

        Args:
            software_name: Software name
            software_version: Software version
            start: Pagination offset
            limit: Max results per page
            filter_str: Search filter for CVE ID or description
            severity: Filter by severity (Critical, High, Medium, Low)

        Returns:
            dict with 'total' count and 'data' list of CVEs
        """
        try:
            # Build WHERE clause for filters
            where_clauses = ["sc.software_name = :sw_name", "sc.software_version = :sw_version"]
            params = {
                'sw_name': software_name,
                'sw_version': software_version,
                'start': start,
                'limit': limit
            }

            if filter_str:
                where_clauses.append("(c.cve_id LIKE :filter OR c.description LIKE :filter)")
                params['filter'] = f"%{filter_str}%"

            if severity:
                where_clauses.append("c.severity = :severity")
                params['severity'] = severity

            where_sql = "WHERE " + " AND ".join(where_clauses)

            # Count query
            count_sql = text(f"""
                SELECT COUNT(DISTINCT c.id) as total
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                {where_sql}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query
            main_sql = text(f"""
                SELECT
                    c.id,
                    c.cve_id,
                    c.cvss_score,
                    c.severity,
                    c.description,
                    c.published_at,
                    c.last_modified
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                {where_sql}
                ORDER BY c.cvss_score DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            cves = []
            for row in result:
                cves.append({
                    'id': row.id,
                    'cve_id': row.cve_id,
                    'cvss_score': float(row.cvss_score) if row.cvss_score else 0.0,
                    'severity': row.severity,
                    'description': row.description,
                    'published_at': row.published_at.isoformat() if row.published_at else None,
                    'last_modified': row.last_modified.isoformat() if row.last_modified else None
                })

            return {'total': total, 'data': cves}
        except Exception as e:
            logger.error(f"Error getting CVEs for software {software_name} {software_version}: {e}")
            return {'total': 0, 'data': []}
