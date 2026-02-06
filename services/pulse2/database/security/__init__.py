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
    # Exclusion filtering helper
    # =========================================================================
    def _build_exclusion_filters(self, excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                                   excluded_machines_ids=None, excluded_groups_ids=None,
                                   include_group_machines=False):
        """
        Build SQL WHERE clauses for exclusions.

        Args:
            excluded_vendors: List of vendor names to exclude
            excluded_names: List of software names to exclude
            excluded_cve_ids: List of CVE IDs to exclude
            excluded_machines_ids: List of machine IDs (GLPI id) to exclude
            excluded_groups_ids: List of group IDs to exclude
            include_group_machines: If True, also exclude machines belonging to excluded groups
                                   (used only in Results by Group view)

        Returns:
            tuple: (name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion) SQL strings
        """
        def sql_escape(val):
            return val.replace("'", "''") if val else val

        name_exclusion = ""
        if excluded_names:
            names_escaped = ','.join(f"'{sql_escape(n)}'" for n in excluded_names)
            name_exclusion = f"AND sc.software_name NOT IN ({names_escaped})"

        cve_exclusion = ""
        if excluded_cve_ids:
            cve_ids_escaped = ','.join(f"'{sql_escape(c)}'" for c in excluded_cve_ids)
            cve_exclusion = f"AND c.cve_id NOT IN ({cve_ids_escaped})"

        # Vendor exclusion requires join with GLPI tables
        vendor_exclusion = ""
        if excluded_vendors:
            vendors_escaped = ','.join(f"'{sql_escape(v)}'" for v in excluded_vendors)
            vendor_exclusion = f"""AND sc.glpi_software_name COLLATE utf8mb4_general_ci NOT IN (
                SELECT gs.name COLLATE utf8mb4_general_ci FROM glpi.glpi_softwares gs
                LEFT JOIN glpi.glpi_manufacturers gm ON gm.id = gs.manufacturers_id
                WHERE gm.name IN ({vendors_escaped})
            )"""

        # Machine exclusion - exclude specific machines by GLPI id (individual exclusions only)
        machine_exclusion = ""
        if excluded_machines_ids:
            machine_ids_str = ','.join(str(int(mid)) for mid in excluded_machines_ids)
            machine_exclusion = f"AND m.id NOT IN ({machine_ids_str})"

        # Group exclusion - exclude machines that belong to excluded groups
        # Only applied when include_group_machines=True (for Results by Group view)
        # Results table links groups (FK_groups) to machines (FK_machines)
        # Machines table has uuid like 'UUID123' which corresponds to GLPI machine id
        if include_group_machines and excluded_groups_ids:
            group_ids_str = ','.join(str(int(gid)) for gid in excluded_groups_ids)
            group_exclusion = f"""AND m.id NOT IN (
                SELECT CAST(REPLACE(dm.uuid, 'UUID', '') AS UNSIGNED)
                FROM dyngroup.Results r
                JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                WHERE r.FK_groups IN ({group_ids_str})
            )"""
            machine_exclusion = machine_exclusion + " " + group_exclusion if machine_exclusion else group_exclusion

        return name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion

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
    def get_dashboard_summary(self, session, location='', min_cvss=0.0, min_severity='None',
                              excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                              excluded_machines_ids=None, excluded_groups_ids=None):
        """Get summary for dashboard: counts by severity, machines affected
        Filtered by entity if location is provided.
        Filtered by min_cvss if > 0.
        Filtered by min_severity if not 'None'.
        Filtered by exclusions.
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        # Build min_cvss filter
        cvss_filter = ""
        if min_cvss > 0:
            cvss_filter = f"AND c.cvss_score >= {min_cvss}"

        # Build min_severity filter
        severity_filter = ""
        if min_sev_index > 0:
            allowed_severities = severity_order[min_sev_index:]
            severity_list = ','.join(f"'{s}'" for s in allowed_severities)
            severity_filter = f"AND c.severity IN ({severity_list})"

        # Build entity filter clause for machines
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        # Build exclusion filters
        name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion = self._build_exclusion_filters(
            excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
        )

        # Count CVEs by severity (only CVEs affecting machines in selected entities)
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
                WHERE 1=1 {entity_filter} {cvss_filter} {severity_filter}
                {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
                GROUP BY c.severity
            """))
            for row in result:
                if row[0] in counts:
                    counts[row[0]] = row[1]
        except Exception as e:
            logger.error(f"Error counting CVEs by severity: {e}")

        # Count affected machines
        # Join using glpi_software_name
        machines_affected = 0
        try:
            result = session.execute(text(f"""
                SELECT COUNT(DISTINCT m.id) as count
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                JOIN xmppmaster.local_glpi_softwares s ON s.name = sc.glpi_software_name
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                WHERE 1=1 {entity_filter} {cvss_filter} {severity_filter}
                {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
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
                 severity=None, location='', sort_by='cvss_score', sort_order='desc',
                 min_cvss=0.0, excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                 excluded_machines_ids=None, excluded_groups_ids=None):
        """Get paginated list of CVEs with affected machine count
        Filtered by entity if location is provided.
        Filtered by min_cvss if > 0.
        Filtered by exclusions.
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Build entity filter clause for machines
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        # Build exclusion filters
        name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion = self._build_exclusion_filters(
            excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
        )

        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']

        # Build filter clauses
        cve_filters = []
        if min_cvss > 0:
            cve_filters.append(f"c.cvss_score >= {min_cvss}")
        if severity and severity in severity_order:
            # Filter by minimum severity (>= requested level)
            min_sev_index = severity_order.index(severity)
            if min_sev_index > 0:
                allowed_severities = severity_order[min_sev_index:]
                severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                cve_filters.append(f"c.severity IN ({severity_list})")
        if filter_str:
            escaped_filter = filter_str.replace("'", "''")
            cve_filters.append(f"(c.cve_id LIKE '%{escaped_filter}%' OR c.description LIKE '%{escaped_filter}%')")

        # Build complete WHERE clause
        cve_where_clause = ""
        if cve_filters:
            cve_where_clause = "AND " + " AND ".join(cve_filters)

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
                WHERE 1=1 {entity_filter}
                {cve_where_clause}
                {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
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
                WHERE 1=1 {entity_filter}
                {cve_where_clause}
                {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
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
                    'cvss_score': str(round(float(row.cvss_score), 1)) if row.cvss_score else '0.0',
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

        # Get affected machines using glpi_software_name for accurate matching
        # Filtered by entity if location is provided
        machines = []
        if sw_cves:
            try:
                # Get glpi_software_names linked to this CVE
                glpi_names = [sc.glpi_software_name for sc in sw_cves if sc.glpi_software_name]
                if glpi_names:
                    # Build conditions using glpi_software_name
                    conditions = []
                    for glpi_name in glpi_names:
                        escaped_name = glpi_name.replace("'", "''")
                        conditions.append(f"s.name = '{escaped_name}'")

                    where_clause = " OR ".join(conditions)
                    result = session.execute(text(f"""
                        SELECT DISTINCT m.id as machine_id, m.name as hostname,
                               sc.software_name, sc.software_version
                        FROM xmppmaster.local_glpi_items_softwareversions isv
                        JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                        JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                        JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                        JOIN security.software_cves sc ON sc.glpi_software_name = s.name AND sc.cve_id = {cve.id}
                        WHERE ({where_clause}) {entity_filter}
                        ORDER BY m.name, sc.software_name
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

        # Parse sources string to list
        sources = cve.sources.split(',') if cve.sources else []

        # Parse source_urls JSON to dict
        import json
        source_urls = {}
        if cve.source_urls:
            try:
                source_urls = json.loads(cve.source_urls)
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            'id': cve.id,
            'cve_id': cve.cve_id,
            'cvss_score': str(round(float(cve.cvss_score), 1)) if cve.cvss_score else '0.0',
            'severity': cve.severity,
            'description': cve.description,
            'published_at': cve.published_at.isoformat() if cve.published_at else None,
            'last_modified': cve.last_modified.isoformat() if cve.last_modified else None,
            'fetched_at': cve.fetched_at.isoformat() if cve.fetched_at else None,
            'sources': sources,
            'source_urls': source_urls,
            'softwares': softwares,
            'machines': machines
        }

    # =========================================================================
    # Machine-centric view
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_machines_summary(self, session, start=0, limit=50, filter_str='', location='',
                             min_cvss=0.0, min_severity='None',
                             excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                             excluded_machines_ids=None, excluded_groups_ids=None):
        """Get list of ALL machines from GLPI with vulnerability counts (only latest software versions)
        Filtered by entity if location is provided.
        Filtered by min_cvss if > 0.
        Filtered by min_severity if not 'None'.
        Filtered by exclusions.
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

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

        # Build min_cvss filter for inner query
        cvss_filter = ""
        if min_cvss > 0:
            cvss_filter = f"AND c.cvss_score >= {min_cvss}"

        # Build min_severity filter for inner query
        severity_filter = ""
        if min_sev_index > 0:
            allowed_severities = severity_order[min_sev_index:]
            severity_list = ','.join(f"'{s}'" for s in allowed_severities)
            severity_filter = f"AND c.severity IN ({severity_list})"

        # Build exclusion filters
        name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion = self._build_exclusion_filters(
            excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
        )

        # Add machine exclusion to WHERE clauses for the main query
        # machine_exclusion starts with "AND m.id NOT IN..." so we need to handle it properly
        machine_filter_clause = filter_clause
        if machine_exclusion:
            if machine_filter_clause:
                machine_filter_clause += " " + machine_exclusion
            else:
                # Convert "AND m.id NOT IN..." to "WHERE m.id NOT IN..."
                machine_filter_clause = "WHERE " + machine_exclusion[4:]  # Remove leading "AND "

        # Count query
        count_sql = text(f"""
            SELECT COUNT(*) as total
            FROM xmppmaster.local_glpi_machines m
            {machine_filter_clause}
        """)

        # Main query with vulnerability counts
        # Join using glpi_software_name (original GLPI name) for accurate matching
        main_sql = text(f"""
            SELECT
                m.id as id_glpi,
                m.name as hostname,
                COALESCE(v.total_cves, 0) as total_cves,
                COALESCE(v.critical, 0) as critical,
                COALESCE(v.high, 0) as high,
                COALESCE(v.medium, 0) as medium,
                COALESCE(v.low, 0) as low,
                COALESCE(v.max_cvss, 0) as risk_score
            FROM xmppmaster.local_glpi_machines m
            LEFT JOIN (
                SELECT
                    isv.items_id as machine_id,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                    MAX(c.cvss_score) as max_cvss
                FROM xmppmaster.local_glpi_items_softwareversions isv
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE 1=1 {cvss_filter} {severity_filter}
                {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
                GROUP BY isv.items_id
            ) v ON m.id = v.machine_id
            {machine_filter_clause}
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
                    'low': int(row.low),
                    'risk_score': str(round(float(row.risk_score), 1)) if row.risk_score else '0.0'
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting machines summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_machine_cves(self, session, id_glpi, start=0, limit=50, filter_str='', severity=None,
                         min_cvss=0.0, excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                         excluded_machines_ids=None, excluded_groups_ids=None):
        """Get all CVEs affecting a specific machine (only latest software versions)

        Args:
            id_glpi: GLPI machine ID
            start: Pagination offset
            limit: Max results per page
            filter_str: Search filter for CVE ID or description
            severity: Filter by severity (Critical, High, Medium, Low)
            min_cvss: Minimum CVSS score to display
            excluded_vendors: List of vendor names to exclude
            excluded_names: List of software names to exclude
            excluded_cve_ids: List of CVE IDs to exclude

        Returns:
            dict with 'total' count and 'data' list
        """
        try:
            # Build WHERE clause for filters
            where_clauses = []
            params = {'id_glpi': id_glpi, 'start': start, 'limit': limit}

            if min_cvss > 0:
                where_clauses.append(f"c.cvss_score >= {min_cvss}")

            if filter_str:
                where_clauses.append("(c.cve_id LIKE :filter OR c.description LIKE :filter)")
                params['filter'] = f"%{filter_str}%"

            if severity:
                where_clauses.append("c.severity = :severity")
                params['severity'] = severity

            where_sql = ""
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)

            # Build exclusion filters (machine_exclusion not used here since we're already filtering by specific machine)
            name_exclusion, cve_exclusion, vendor_exclusion, _ = self._build_exclusion_filters(
                excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
            )

            # Count query - use glpi_software_name for accurate matching
            count_sql = text(f"""
                SELECT COUNT(DISTINCT c.id) as total
                FROM xmppmaster.local_glpi_items_softwareversions isv
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE isv.items_id = :id_glpi
                {where_sql.replace('WHERE', 'AND') if where_sql else ''}
                {name_exclusion} {cve_exclusion} {vendor_exclusion}
            """)

            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query with pagination - use glpi_software_name for accurate matching
            # Display normalized software_name from software_cves for clarity
            main_sql = text(f"""
                SELECT
                    c.cve_id,
                    c.cvss_score,
                    c.severity,
                    c.description,
                    c.published_at,
                    c.last_modified,
                    GROUP_CONCAT(DISTINCT sc.software_name ORDER BY sc.software_name SEPARATOR ', ') as software_name,
                    GROUP_CONCAT(DISTINCT sc.software_version ORDER BY sc.software_name SEPARATOR ', ') as software_version
                FROM xmppmaster.local_glpi_items_softwareversions isv
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE isv.items_id = :id_glpi
                {where_sql.replace('WHERE', 'AND') if where_sql else ''}
                {name_exclusion} {cve_exclusion} {vendor_exclusion}
                GROUP BY c.id, c.cve_id, c.cvss_score, c.severity, c.description, c.published_at, c.last_modified
                ORDER BY c.cvss_score DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)

            cves = []
            for row in result:
                cves.append({
                    'cve_id': row.cve_id,
                    'cvss_score': str(round(float(row.cvss_score), 1)) if row.cvss_score else '0.0',
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
    def get_machine_softwares_summary(self, session, id_glpi, start=0, limit=50, filter_str='',
                                      min_cvss=0.0, excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                                      excluded_machines_ids=None, excluded_groups_ids=None):
        """Get vulnerable software summary for a specific machine, grouped by software.

        Args:
            id_glpi: GLPI machine ID
            start: Pagination offset
            limit: Max results per page
            filter_str: Search filter for software name
            min_cvss: Minimum CVSS score to display
            excluded_vendors: List of vendor names to exclude
            excluded_names: List of software names to exclude
            excluded_cve_ids: List of CVE IDs to exclude

        Returns:
            dict with 'total' count and 'data' list (grouped by software)
        """
        try:
            params = {'id_glpi': id_glpi, 'start': start, 'limit': limit}

            # Filter on normalized software_name for user convenience
            filter_clause = ""
            if filter_str:
                filter_clause = "AND sc.software_name LIKE :filter"
                params['filter'] = f"%{filter_str}%"

            # Build min_cvss filter
            cvss_filter = ""
            if min_cvss > 0:
                cvss_filter = f"AND c.cvss_score >= {min_cvss}"

            # Build exclusion filters (machine_exclusion not used here since we're already filtering by specific machine)
            name_exclusion, cve_exclusion, vendor_exclusion, _ = self._build_exclusion_filters(
                excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
            )

            # Count query - use glpi_software_name for accurate matching
            count_sql = text(f"""
                SELECT COUNT(DISTINCT CONCAT(sc.software_name, ':', sc.software_version)) as total
                FROM xmppmaster.local_glpi_items_softwareversions isv
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE isv.items_id = :id_glpi {filter_clause} {cvss_filter}
                {name_exclusion} {cve_exclusion} {vendor_exclusion}
            """)

            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query - use glpi_software_name for join, display normalized names
            main_sql = text(f"""
                SELECT
                    sc.software_name,
                    sc.software_version,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                    MAX(c.cvss_score) as max_cvss
                FROM xmppmaster.local_glpi_items_softwareversions isv
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE isv.items_id = :id_glpi {filter_clause} {cvss_filter}
                {name_exclusion} {cve_exclusion} {vendor_exclusion}
                GROUP BY sc.software_name, sc.software_version
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
                    'max_cvss': str(round(float(row.max_cvss), 1)) if row.max_cvss else '0.0'
                })

            return {'total': total, 'data': data}
        except Exception as e:
            logger.error(f"Error getting software summary for machine {id_glpi}: {e}")
            return {'total': 0, 'data': []}

    # =========================================================================
    # CVE Management (add/update from scanner)
    # =========================================================================
    @DatabaseHelper._sessionm
    def add_cve(self, session, cve_id, cvss_score, severity, description, published_at=None, last_modified=None, sources=None, source_urls=None):
        """Add or update a CVE in local cache

        Args:
            sources: List of source names (e.g., ['circl', 'nvd']) or None
            source_urls: Dict of source URLs (e.g., {'nvd': 'https://...', 'circl': 'https://...'}) or None
        """
        import json

        # Convert sources list to comma-separated string
        sources_str = ','.join(sources) if sources else None

        # Convert source_urls dict to JSON string
        source_urls_str = json.dumps(source_urls) if source_urls else None

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
            if sources_str:
                cve.sources = sources_str
            if source_urls_str:
                cve.source_urls = source_urls_str
            cve.fetched_at = datetime.utcnow()
        else:
            # Create new
            cve = Cve(
                cve_id=cve_id,
                cvss_score=cvss_score,
                severity=severity,
                description=description,
                published_at=published_at,
                last_modified=last_modified,
                sources=sources_str,
                source_urls=source_urls_str
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
    def get_softwares_summary(self, session, start=0, limit=50, filter_str='', location='',
                              min_cvss=0.0, min_severity='None',
                              excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                              excluded_machines_ids=None, excluded_groups_ids=None):
        """Get list of softwares with CVE counts, grouped by software name+version.
        Filtered by entity if location is provided.
        Filtered by min_cvss if > 0.
        Filtered by min_severity if not 'None'.
        Excludes vendors, names and CVE IDs based on exclusion policies.

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

        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        # Build entity filter clause for machines
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        # Build min_cvss filter
        cvss_filter = ""
        if min_cvss > 0:
            cvss_filter = f"AND c.cvss_score >= {min_cvss}"

        # Build min_severity filter
        severity_filter = ""
        if min_sev_index > 0:
            allowed_severities = severity_order[min_sev_index:]
            severity_list = ','.join(f"'{s}'" for s in allowed_severities)
            severity_filter = f"AND c.severity IN ({severity_list})"

        # Build exclusion filters
        name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion = self._build_exclusion_filters(
            excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
        )

        # Build filter clause (search on normalized name for user convenience)
        filter_clause = ""
        params = {'start': start, 'limit': limit}
        if filter_str:
            filter_clause = "AND (sc.software_name LIKE :filter OR sc.software_version LIKE :filter)"
            params['filter'] = f"%{filter_str}%"

        try:
            # Count total distinct software+version with CVEs
            # Software is shown if it exists in GLPI (any entity), CVE/name/vendor exclusions apply
            # Machine exclusions only affect the machines_affected count, not visibility
            count_sql = text(f"""
                SELECT COUNT(DISTINCT CONCAT(sc.software_name, '|', sc.software_version)) as total
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE EXISTS (
                    SELECT 1 FROM xmppmaster.local_glpi_softwares s
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.softwares_id = s.id
                    JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                    JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                    WHERE s.name = COALESCE(sc.glpi_software_name, sc.software_name)
                    {entity_filter}
                )
                AND 1=1 {filter_clause} {cvss_filter} {severity_filter} {name_exclusion} {cve_exclusion} {vendor_exclusion}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query: software grouped with CVE counts
            # Shows all software with CVEs that exist in GLPI
            # machines_affected counts only non-excluded machines
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
                    (
                        SELECT COUNT(DISTINCT m2.id)
                        FROM xmppmaster.local_glpi_softwares s2
                        JOIN xmppmaster.local_glpi_softwareversions sv2 ON sv2.softwares_id = s2.id
                        JOIN xmppmaster.local_glpi_items_softwareversions isv2 ON isv2.softwareversions_id = sv2.id
                        JOIN xmppmaster.local_glpi_machines m2 ON m2.id = isv2.items_id
                        WHERE s2.name = COALESCE(sc.glpi_software_name, sc.software_name)
                        {entity_filter.replace('m.', 'm2.')}
                        {machine_exclusion.replace('m.', 'm2.')}
                    ) as machines_affected
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE EXISTS (
                    SELECT 1 FROM xmppmaster.local_glpi_softwares s
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.softwares_id = s.id
                    JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                    JOIN xmppmaster.local_glpi_machines m ON m.id = isv.items_id
                    WHERE s.name = COALESCE(sc.glpi_software_name, sc.software_name)
                    {entity_filter}
                )
                AND 1=1 {filter_clause} {cvss_filter} {severity_filter} {name_exclusion} {cve_exclusion} {vendor_exclusion}
                GROUP BY sc.software_name, sc.software_version, sc.glpi_software_name
                ORDER BY max_cvss DESC, total_cves DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            results = []
            for row in result:
                software_data = {
                    'software_name': row.software_name,
                    'software_version': row.software_version,
                    'total_cves': int(row.total_cves),
                    'critical': int(row.critical),
                    'high': int(row.high),
                    'medium': int(row.medium),
                    'low': int(row.low),
                    'max_cvss': str(round(float(row.max_cvss), 1)) if row.max_cvss else '0.0',
                    'machines_affected': int(row.machines_affected),
                    # Store info (will be populated below)
                    'store_version': None,
                    'store_has_update': False,
                    'store_package_uuid': None
                }
                results.append(software_data)

            # Enrich with store info for each software
            if results:
                self._enrich_with_store_info(session, results)

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting softwares summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_entities_summary(self, session, start=0, limit=50, filter_str='', user_entities='',
                             min_cvss=0.0, min_severity='None',
                             excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                             excluded_machines_ids=None, excluded_groups_ids=None):
        """Get list of entities with CVE counts.
        Filtered by user's accessible entities if user_entities is provided.
        Filtered by min_cvss if > 0.
        Filtered by min_severity if not 'None'.
        Filtered by exclusions.

        Returns:
            dict with 'total' count and 'data' list containing:
            - entity_id, entity_name
            - total_cves, critical, high, medium, low
            - max_cvss, machines_count
        """
        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        # Build CVE filters
        cve_filter = ""
        if min_cvss > 0:
            cve_filter += f" AND c.cvss_score >= {min_cvss}"
        if min_sev_index > 0:
            allowed_severities = severity_order[min_sev_index:]
            severity_list = ','.join(f"'{s}'" for s in allowed_severities)
            cve_filter += f" AND c.severity IN ({severity_list})"

        # Build exclusion filters
        name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion = self._build_exclusion_filters(
            excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
        )

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
            # Entity is always shown, machine exclusions only affect counts
            # Use subqueries for counts to properly apply machine exclusions
            main_sql = text(f"""
                SELECT
                    e.id as entity_id,
                    e.name as entity_name,
                    e.completename as entity_fullname,
                    (
                        SELECT COUNT(DISTINCT m2.id)
                        FROM xmppmaster.local_glpi_machines m2
                        WHERE m2.entities_id = e.id
                        {machine_exclusion.replace('m.', 'm2.')}
                    ) as machines_count,
                    COALESCE(cve_stats.total_cves, 0) as total_cves,
                    COALESCE(cve_stats.critical, 0) as critical,
                    COALESCE(cve_stats.high, 0) as high,
                    COALESCE(cve_stats.medium, 0) as medium,
                    COALESCE(cve_stats.low, 0) as low,
                    COALESCE(cve_stats.max_cvss, 0) as max_cvss
                FROM xmppmaster.local_glpi_entities e
                LEFT JOIN (
                    SELECT
                        m.entities_id,
                        COUNT(DISTINCT c.id) as total_cves,
                        COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                        COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                        COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                        COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                        MAX(c.cvss_score) as max_cvss
                    FROM xmppmaster.local_glpi_machines m
                    JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.items_id = m.id
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                    JOIN security.cves c ON c.id = sc.cve_id
                    WHERE 1=1 {cve_filter}
                    {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
                    GROUP BY m.entities_id
                ) cve_stats ON cve_stats.entities_id = e.id
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
                    'max_cvss': str(round(float(row.max_cvss), 1)) if row.max_cvss else '0.0'
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting entities summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_groups_summary(self, session, start=0, limit=50, filter_str='', user_login='',
                           min_cvss=0.0, min_severity='None',
                           excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                           excluded_machines_ids=None, excluded_groups_ids=None):
        """Get list of groups with CVE counts.
        Filtered by ShareGroup - only show groups shared with this user.
        Filtered by min_cvss if > 0.
        Filtered by min_severity if not 'None'.
        Filtered by exclusions.

        Returns:
            dict with 'total' count and 'data' list containing:
            - group_id, group_name, group_type
            - total_cves, critical, high, medium, low
            - max_cvss, machines_count
        """
        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        # Build CVE filters
        cve_filter = ""
        if min_cvss > 0:
            cve_filter += f" AND c.cvss_score >= {min_cvss}"
        if min_sev_index > 0:
            allowed_severities = severity_order[min_sev_index:]
            severity_list = ','.join(f"'{s}'" for s in allowed_severities)
            cve_filter += f" AND c.severity IN ({severity_list})"

        # Build exclusion filters - for groups view, also exclude machines from excluded groups
        name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion = self._build_exclusion_filters(
            excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids,
            include_group_machines=True
        )

        try:
            # Build filter clause - exclude internal PULSE groups and excluded groups
            filter_clause = "AND g.name NOT LIKE 'PULSE_INTERNAL%'"
            params = {'start': start, 'limit': limit}
            if filter_str:
                filter_clause += " AND g.name LIKE :filter"
                params['filter'] = f"%{filter_str}%"

            # Exclude groups that are in the exclusion list
            if excluded_groups_ids:
                group_ids_str = ','.join(str(int(gid)) for gid in excluded_groups_ids)
                filter_clause += f" AND g.id NOT IN ({group_ids_str})"

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
            # Group is always shown, machine exclusions only affect counts
            # is_dynamic: 1 if query is not null and not empty, 0 otherwise
            main_sql = text(f"""
                SELECT
                    g.id as group_id,
                    g.name as group_name,
                    CASE WHEN g.query IS NOT NULL AND LENGTH(g.query) > 0 THEN 1 ELSE 0 END as is_dynamic,
                    (
                        SELECT COUNT(DISTINCT m2.id)
                        FROM dyngroup.Results r2
                        JOIN dyngroup.Machines dm2 ON dm2.id = r2.FK_machines
                        JOIN xmppmaster.local_glpi_machines m2 ON CONCAT('UUID', m2.id) = dm2.uuid
                        WHERE r2.FK_groups = g.id
                        {machine_exclusion.replace('m.', 'm2.')}
                    ) as machines_count,
                    COALESCE(cve_stats.total_cves, 0) as total_cves,
                    COALESCE(cve_stats.critical, 0) as critical,
                    COALESCE(cve_stats.high, 0) as high,
                    COALESCE(cve_stats.medium, 0) as medium,
                    COALESCE(cve_stats.low, 0) as low,
                    COALESCE(cve_stats.max_cvss, 0) as max_cvss
                FROM dyngroup.Groups g
                LEFT JOIN (
                    SELECT
                        r.FK_groups as group_id,
                        COUNT(DISTINCT c.id) as total_cves,
                        COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                        COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                        COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                        COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                        MAX(c.cvss_score) as max_cvss
                    FROM dyngroup.Results r
                    JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                    JOIN xmppmaster.local_glpi_machines m ON CONCAT('UUID', m.id) = dm.uuid
                    JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.items_id = m.id
                    JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                    JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                    JOIN security.cves c ON c.id = sc.cve_id
                    WHERE 1=1 {cve_filter}
                    {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
                    GROUP BY r.FK_groups
                ) cve_stats ON cve_stats.group_id = g.id
                WHERE 1=1 {filter_clause} {share_filter}
                GROUP BY g.id, g.name
                ORDER BY max_cvss DESC, total_cves DESC
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            results = []
            for row in result:
                # is_dynamic is computed in SQL: 1 = dynamic, 0 = static
                group_type_label = 'Dynamic' if int(row.is_dynamic) == 1 else 'Static'
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
                    'max_cvss': str(round(float(row.max_cvss), 1)) if row.max_cvss else '0.0'
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting groups summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_group_machines(self, session, group_id, start=0, limit=50, filter_str='',
                           min_cvss=0.0, min_severity='None',
                           excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                           excluded_machines_ids=None, excluded_groups_ids=None):
        """Get machines in a group with their CVE counts.
        Filtered by min_cvss if > 0.
        Filtered by min_severity if not 'None'.
        Filtered by exclusions.

        Returns:
            dict with 'total' count and 'data' list
        """
        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        # Build CVE filters
        cve_filter = ""
        if min_cvss > 0:
            cve_filter += f" AND c.cvss_score >= {min_cvss}"
        if min_sev_index > 0:
            allowed_severities = severity_order[min_sev_index:]
            severity_list = ','.join(f"'{s}'" for s in allowed_severities)
            cve_filter += f" AND c.severity IN ({severity_list})"

        # Build exclusion filters
        name_exclusion, cve_exclusion, vendor_exclusion, machine_exclusion = self._build_exclusion_filters(
            excluded_vendors, excluded_names, excluded_cve_ids, excluded_machines_ids, excluded_groups_ids
        )

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
                {machine_exclusion}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Main query: machines with CVE counts
            # Use glpi_software_name for accurate matching
            main_sql = text(f"""
                SELECT
                    m.id as id_glpi,
                    m.name as hostname,
                    COUNT(DISTINCT c.id) as total_cves,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Critical' THEN c.id END) as critical,
                    COUNT(DISTINCT CASE WHEN c.severity = 'High' THEN c.id END) as high,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Medium' THEN c.id END) as medium,
                    COUNT(DISTINCT CASE WHEN c.severity = 'Low' THEN c.id END) as low,
                    COALESCE(MAX(c.cvss_score), 0) as risk_score
                FROM dyngroup.Results r
                JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                JOIN xmppmaster.local_glpi_machines m ON CONCAT('UUID', m.id) = dm.uuid
                LEFT JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.items_id = m.id
                LEFT JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                LEFT JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                LEFT JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                LEFT JOIN security.cves c ON c.id = sc.cve_id
                WHERE r.FK_groups = :group_id {filter_clause} {cve_filter}
                {name_exclusion} {cve_exclusion} {vendor_exclusion} {machine_exclusion}
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
                    'low': int(row.low),
                    'risk_score': str(round(float(row.risk_score), 1)) if row.risk_score else '0.0'
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting group machines: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_software_cves(self, session, software_name, software_version, start=0, limit=50,
                          filter_str='', severity=None, min_cvss=0.0):
        """Get all CVEs affecting a specific software version.

        Args:
            software_name: Software name
            software_version: Software version
            start: Pagination offset
            limit: Max results per page
            filter_str: Search filter for CVE ID or description
            severity: Filter by severity (Critical, High, Medium, Low)
            min_cvss: Minimum CVSS score to display

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

            if min_cvss > 0:
                where_clauses.append(f"c.cvss_score >= {min_cvss}")

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
                    'cvss_score': str(round(float(row.cvss_score), 1)) if row.cvss_score else '0.0',
                    'severity': row.severity,
                    'description': row.description,
                    'published_at': row.published_at.isoformat() if row.published_at else None,
                    'last_modified': row.last_modified.isoformat() if row.last_modified else None
                })

            return {'total': total, 'data': cves}
        except Exception as e:
            logger.error(f"Error getting CVEs for software {software_name} {software_version}: {e}")
            return {'total': 0, 'data': []}

    # =========================================================================
    # Group creation helpers
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_machines_by_severity(self, session, severity, location=''):
        """Get list of machines affected by CVEs of a given severity.

        Args:
            severity: CVE severity level (Critical, High, Medium, Low)
            location: Entity filter (optional)

        Returns:
            List of dicts with 'uuid' and 'hostname' for each machine
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Build entity filter
        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        try:
            # Get distinct machines with CVEs of given severity
            # Use glpi_software_name for accurate matching
            result = session.execute(text(f"""
                SELECT DISTINCT m.id, m.name
                FROM xmppmaster.local_glpi_machines m
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.items_id = m.id
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                JOIN security.software_cves sc ON sc.glpi_software_name = s.name
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE c.severity = :severity {entity_filter}
                ORDER BY m.name
            """), {'severity': severity})

            machines = [{'uuid': f"UUID{row[0]}", 'hostname': row[1]} for row in result]
            return machines
        except Exception as e:
            logger.error(f"Error getting machines by severity {severity}: {e}")
            return []

    # =========================================================================
    # Policies Management (stored in DB for UI editing)
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_all_policies(self, session):
        """Get all policies from database, grouped by category.

        Returns:
            dict: {'display': {...}, 'policy': {...}, 'exclusions': {...}}
        """
        import json
        try:
            result = session.execute(text("""
                SELECT category, `key`, value FROM policies
            """))

            policies = {}
            for row in result:
                category, key, value = row
                if category not in policies:
                    policies[category] = {}

                # Try to parse JSON for list values
                try:
                    parsed = json.loads(value) if value else value
                    policies[category][key] = parsed
                except (json.JSONDecodeError, TypeError):
                    policies[category][key] = value

            return policies
        except Exception as e:
            logger.debug(f"Could not get policies from DB: {e}")
            return {}

    @DatabaseHelper._sessionm
    def get_policy(self, session, category, key):
        """Get a single policy value.

        Args:
            category: display, policy, or exclusions
            key: the policy key

        Returns:
            The value (parsed from JSON if applicable) or None
        """
        import json
        try:
            result = session.execute(text("""
                SELECT value FROM policies WHERE category = :category AND `key` = :key
            """), {'category': category, 'key': key})
            row = result.fetchone()
            if row and row[0]:
                try:
                    return json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    return row[0]
            return None
        except Exception as e:
            logger.error(f"Error getting policy {category}.{key}: {e}")
            return None

    @DatabaseHelper._sessionm
    def set_policy(self, session, category, key, value, user=None):
        """Set a policy value.

        Args:
            category: display, policy, or exclusions
            key: the policy key
            value: the value (will be JSON encoded if list/dict)
            user: username making the change

        Returns:
            bool: True on success
        """
        import json

        # Validate category
        if category not in ('display', 'policy', 'exclusions'):
            raise ValueError(f"Invalid category: {category}")

        # JSON encode lists and dicts
        if isinstance(value, (list, dict)):
            value_str = json.dumps(value)
        elif isinstance(value, bool):
            value_str = 'true' if value else 'false'
        else:
            value_str = str(value) if value is not None else ''

        try:
            # Use INSERT ... ON DUPLICATE KEY UPDATE for upsert
            session.execute(text("""
                INSERT INTO policies (category, `key`, value, updated_by, updated_at)
                VALUES (:category, :key, :value, :user, NOW())
                ON DUPLICATE KEY UPDATE
                    value = :value,
                    updated_by = :user,
                    updated_at = NOW()
            """), {
                'category': category,
                'key': key,
                'value': value_str,
                'user': user
            })
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting policy {category}.{key}: {e}")
            return False

    @DatabaseHelper._sessionm
    def set_policies_bulk(self, session, policies, user=None):
        """Set multiple policies at once.

        Args:
            policies: dict like {'display': {'min_cvss': 4.0}, 'exclusions': {'cve_ids': [...]}}
            user: username making the change

        Returns:
            bool: True on success
        """
        import json

        try:
            for category, settings in policies.items():
                if category not in ('display', 'policy', 'exclusions'):
                    continue
                for key, value in settings.items():
                    # JSON encode lists and dicts
                    if isinstance(value, (list, dict)):
                        value_str = json.dumps(value)
                    elif isinstance(value, bool):
                        value_str = 'true' if value else 'false'
                    else:
                        value_str = str(value) if value is not None else ''

                    session.execute(text("""
                        INSERT INTO policies (category, `key`, value, updated_by, updated_at)
                        VALUES (:category, :key, :value, :user, NOW())
                        ON DUPLICATE KEY UPDATE
                            value = :value,
                            updated_by = :user,
                            updated_at = NOW()
                    """), {
                        'category': category,
                        'key': key,
                        'value': value_str,
                        'user': user
                    })

            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting policies bulk: {e}")
            return False

    @DatabaseHelper._sessionm
    def delete_policy(self, session, category, key):
        """Delete a policy (reverts to ini file default).

        Args:
            category: display, policy, or exclusions
            key: the policy key

        Returns:
            bool: True on success
        """
        try:
            session.execute(text("""
                DELETE FROM policies WHERE category = :category AND `key` = :key
            """), {'category': category, 'key': key})
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting policy {category}.{key}: {e}")
            return False

    @DatabaseHelper._sessionm
    def reset_display_policies(self, session, user=None):
        """Reset only display policies to default values, keeping exclusions intact.

        Reads defaults from policies_defaults table.

        Args:
            user: username making the change (default: 'system')

        Returns:
            bool: True on success
        """
        if user is None:
            user = 'system'

        try:
            # Delete only display policies
            session.execute(text("DELETE FROM policies WHERE category = 'display'"))

            # Reinsert from policies_defaults table
            session.execute(text("""
                INSERT INTO policies (category, `key`, value, updated_by, updated_at)
                SELECT category, `key`, value, :user, NOW()
                FROM policies_defaults
                WHERE category = 'display'
            """), {'user': user})

            session.commit()
            logger.info(f"Display policies reset to defaults by user '{user}'")
            return True
        except Exception as e:
            logger.error(f"Error resetting display policies: {e}")
            return False

    @DatabaseHelper._sessionm
    def reset_all_policies(self, session, user=None):
        """Reset all policies to default values.

        Reads defaults from policies_defaults table.

        Args:
            user: username making the change (default: 'system')

        Returns:
            bool: True on success
        """
        if user is None:
            user = 'system'

        try:
            # Delete all existing policies
            session.execute(text("DELETE FROM policies"))

            # Reinsert all from policies_defaults table
            session.execute(text("""
                INSERT INTO policies (category, `key`, value, updated_by, updated_at)
                SELECT category, `key`, value, :user, NOW()
                FROM policies_defaults
            """), {'user': user})

            session.commit()
            logger.info(f"All policies reset to defaults by user '{user}'")
            return True
        except Exception as e:
            logger.error(f"Error resetting policies: {e}")
            return False

    # =========================================================================
    # Store integration methods
    # =========================================================================

    def _enrich_with_store_info(self, session, results):
        """Enrich software results with store update information.

        For each software in results, checks if a newer version exists in the store.
        Uses partial matching: GLPI software name often includes version (e.g., "7-Zip 23.01 (x64)")
        while store name is clean (e.g., "7-Zip"). We match if GLPI name starts with store name.

        Updates results in-place with store_version, store_has_update, store_package_uuid.

        Args:
            session: SQLAlchemy session
            results: List of software dicts to enrich
        """
        if not results:
            return

        try:
            # Get all active store software with their versions
            store_sql = text("""
                SELECT
                    s.name,
                    s.version as store_version,
                    sd.package_uuid
                FROM store.software s
                LEFT JOIN store.software_downloads sd ON sd.software_id = s.id
                    AND sd.status = 'success'
                WHERE s.active = 1
                AND s.version IS NOT NULL
                AND s.version != ''
            """)

            store_result = session.execute(store_sql)
            store_info = {}
            for row in store_result:
                # Store by lowercase name for case-insensitive matching
                store_info[row.name.lower()] = {
                    'name': row.name,
                    'store_version': row.store_version,
                    'store_package_uuid': row.package_uuid
                }

            # Enrich results - match if GLPI name starts with store name
            for software in results:
                glpi_name = software['software_name'].lower()

                # Find matching store software
                matched_store = None
                for store_name, store_data in store_info.items():
                    # Match if GLPI name starts with store name
                    # e.g., "7-zip 23.01 (x64)" starts with "7-zip"
                    if glpi_name.startswith(store_name):
                        # Prefer longer matches (more specific)
                        if matched_store is None or len(store_name) > len(matched_store[0]):
                            matched_store = (store_name, store_data)

                if matched_store:
                    store_data = matched_store[1]
                    software['store_version'] = store_data['store_version']
                    software['store_package_uuid'] = store_data['store_package_uuid']
                    software['store_name'] = store_data['name']  # Original store name for display
                    # Compare versions to determine if update available
                    software['store_has_update'] = self._is_version_newer(
                        store_data['store_version'],
                        software['software_version']
                    )

        except Exception as e:
            logger.warning(f"Could not enrich with store info: {e}")
            # Don't fail - just leave store fields as None/False

    def _is_version_newer(self, store_version, vulnerable_version):
        """Compare two version strings to determine if store version is newer.

        Args:
            store_version: Version in the store (e.g., "3.14.2")
            vulnerable_version: Vulnerable version (e.g., "3.11.9")

        Returns:
            bool: True if store_version > vulnerable_version
        """
        if not store_version or not vulnerable_version:
            return False

        try:
            # Parse version strings into comparable tuples
            def parse_version(v):
                # Remove common suffixes like 'esr', 'lts', etc.
                v = v.lower().replace('esr', '').replace('lts', '').strip('.')
                # Split and convert to integers where possible
                parts = []
                for part in v.split('.'):
                    try:
                        parts.append(int(part))
                    except ValueError:
                        # Handle non-numeric parts (e.g., "1.0.0a1")
                        parts.append(part)
                return tuple(parts)

            store_parts = parse_version(store_version)
            vuln_parts = parse_version(vulnerable_version)

            return store_parts > vuln_parts
        except Exception:
            # If comparison fails, assume no update (safe default)
            return False

    @DatabaseHelper._sessionm
    def get_store_software_info(self, session, software_name):
        """Get store information for a specific software.

        Uses partial matching: the software_name might be a GLPI name like "7-Zip 23.01 (x64)"
        while store has clean name "7-Zip". We find store software where GLPI name starts with store name.

        Args:
            software_name: Name of the software (GLPI name or clean name)

        Returns:
            dict with store info or None if not found:
            - name, version, vendor, short_desc
            - package_uuid, download_url
            - has_package (bool)
        """
        try:
            # First try exact match
            sql = text("""
                SELECT
                    s.id,
                    s.name,
                    s.version,
                    s.vendor,
                    s.short_desc,
                    s.os,
                    s.arch,
                    sd.package_uuid,
                    sd.filename,
                    sd.medulla_path
                FROM store.software s
                LEFT JOIN store.software_downloads sd ON sd.software_id = s.id
                    AND sd.status = 'success'
                WHERE s.name = :name
                AND s.active = 1
                LIMIT 1
            """)

            result = session.execute(sql, {'name': software_name})
            row = result.fetchone()

            # If no exact match, try partial match (GLPI name starts with store name)
            if not row:
                sql_partial = text("""
                    SELECT
                        s.id,
                        s.name,
                        s.version,
                        s.vendor,
                        s.short_desc,
                        s.os,
                        s.arch,
                        sd.package_uuid,
                        sd.filename,
                        sd.medulla_path,
                        LENGTH(s.name) as name_len
                    FROM store.software s
                    LEFT JOIN store.software_downloads sd ON sd.software_id = s.id
                        AND sd.status = 'success'
                    WHERE LOWER(:glpi_name) LIKE CONCAT(LOWER(s.name), '%')
                    AND s.active = 1
                    ORDER BY name_len DESC
                    LIMIT 1
                """)
                result = session.execute(sql_partial, {'glpi_name': software_name})
                row = result.fetchone()

            if not row:
                return None

            return {
                'id': row.id,
                'name': row.name,
                'version': row.version,
                'vendor': row.vendor,
                'short_desc': row.short_desc,
                'os': row.os,
                'arch': row.arch,
                'package_uuid': row.package_uuid,
                'filename': row.filename,
                'medulla_path': row.medulla_path,
                'has_package': row.package_uuid is not None
            }
        except Exception as e:
            logger.error(f"Error getting store software info for '{software_name}': {e}")
            return None

    @DatabaseHelper._sessionm
    def get_machines_for_vulnerable_software(self, session, software_name, software_version,
                                              location='', start=0, limit=100, filter_str=''):
        """Get machines that have a specific vulnerable software installed.

        Args:
            software_name: Normalized software name (e.g., "Python")
            software_version: Vulnerable version (e.g., "3.11.9")
            location: Entity filter (comma-separated entity IDs)
            start: Pagination offset
            limit: Pagination limit
            filter_str: Search filter on hostname

        Returns:
            dict with 'total' count and 'data' list containing:
            - id (GLPI machine ID)
            - uuid (format "UUID<id>")
            - hostname
            - entity_id, entity_name
            - glpi_software_name (original name in GLPI)
        """
        entity_ids = self._parse_entity_ids(session, location)

        entity_filter = ""
        if entity_ids:
            entity_ids_str = ','.join(str(e) for e in entity_ids)
            entity_filter = f"AND m.entities_id IN ({entity_ids_str})"

        filter_clause = ""
        params = {'software_name': software_name, 'start': start, 'limit': limit}
        if filter_str:
            filter_clause = "AND m.name LIKE :filter"
            params['filter'] = f"%{filter_str}%"

        try:
            # First get the glpi_software_name from software_cves
            glpi_name_sql = text("""
                SELECT COALESCE(glpi_software_name, software_name) as glpi_name
                FROM security.software_cves
                WHERE software_name = :software_name
                LIMIT 1
            """)
            glpi_result = session.execute(glpi_name_sql, {'software_name': software_name})
            glpi_row = glpi_result.fetchone()
            glpi_software_name = glpi_row.glpi_name if glpi_row else software_name
            params['glpi_software_name'] = glpi_software_name

            # Count total
            count_sql = text(f"""
                SELECT COUNT(DISTINCT m.id) as total
                FROM xmppmaster.local_glpi_machines m
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.items_id = m.id
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                WHERE s.name = :glpi_software_name
                {entity_filter}
                {filter_clause}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Get machines
            main_sql = text(f"""
                SELECT DISTINCT
                    m.id,
                    CONCAT('UUID', m.id) as uuid,
                    m.name as hostname,
                    m.entities_id as entity_id,
                    e.name as entity_name,
                    s.name as glpi_software_name,
                    sv.name as installed_version
                FROM xmppmaster.local_glpi_machines m
                JOIN xmppmaster.local_glpi_items_softwareversions isv ON isv.items_id = m.id
                JOIN xmppmaster.local_glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                JOIN xmppmaster.local_glpi_softwares s ON s.id = sv.softwares_id
                LEFT JOIN xmppmaster.local_glpi_entities e ON e.id = m.entities_id
                WHERE s.name = :glpi_software_name
                {entity_filter}
                {filter_clause}
                ORDER BY m.name
                LIMIT :limit OFFSET :start
            """)

            result = session.execute(main_sql, params)
            machines = []
            for row in result:
                machines.append({
                    'id': row.id,
                    'uuid': row.uuid,
                    'hostname': row.hostname,
                    'entity_id': row.entity_id,
                    'entity_name': row.entity_name or 'Root',
                    'glpi_software_name': row.glpi_software_name,
                    'installed_version': row.installed_version
                })

            return {'total': total, 'data': machines}
        except Exception as e:
            logger.error(f"Error getting machines for vulnerable software '{software_name}': {e}")
            return {'total': 0, 'data': []}
