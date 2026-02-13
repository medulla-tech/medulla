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


def _get_glpi_database():
    """Get the GLPI database instance for direct queries.

    This allows querying GLPI tables using the glpi user credentials
    instead of the mmc user which doesn't have access to GLPI.

    Returns:
        Glpi database instance or None if not available
    """
    try:
        from mmc.plugins.glpi.database import Glpi
        glpi = Glpi()
        if glpi.is_activated:
            return glpi.database
        return None
    except Exception as e:
        logger.warning(f"Could not get GLPI database connection: {e}")
        return None


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
                SELECT gs.name COLLATE utf8mb4_general_ci FROM xmppmaster.local_glpi_softwares gs
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

        Uses separate database connections:
        - GLPI connection (glpi user) for GLPI tables
        - Security connection (mmc user) for security tables
        Then merges results in Python.
        """
        entity_ids = self._parse_entity_ids(session, location)

        # Severity order for filtering
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'None': 0}
        machines_affected = 0

        try:
            # Get GLPI database connection
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.error("GLPI database not available for dashboard summary")
                raise Exception("GLPI database not available")

            # Step 1: Get software names installed on machines from GLPI
            # Using GLPI connection (glpi user has access to glpi.*)
            entity_filter_glpi = ""
            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                entity_filter_glpi = f"AND c.entities_id IN ({entity_ids_str})"

            machine_exclusion_glpi = ""
            if excluded_machines_ids:
                machine_ids_str = ','.join(str(int(mid)) for mid in excluded_machines_ids)
                machine_exclusion_glpi = f"AND c.id NOT IN ({machine_ids_str})"

            # Query GLPI for machines and their software names
            glpi_sql = text(f"""
                SELECT DISTINCT s.name as software_name, c.id as machine_id
                FROM glpi_softwares s
                JOIN glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN glpi_computers c ON c.id = isv.items_id
                WHERE c.is_deleted = 0 AND c.is_template = 0
                {entity_filter_glpi} {machine_exclusion_glpi}
            """)

            with glpi_db.db.connect() as glpi_conn:
                glpi_result = glpi_conn.execute(glpi_sql)
                # Build set of software names and machine IDs from GLPI
                software_names = set()
                machine_ids = set()
                software_machine_map = {}  # software_name -> set of machine_ids

                for row in glpi_result:
                    sw_name = row[0]
                    m_id = row[1]
                    software_names.add(sw_name)
                    machine_ids.add(m_id)
                    if sw_name not in software_machine_map:
                        software_machine_map[sw_name] = set()
                    software_machine_map[sw_name].add(m_id)

            if not software_names:
                # No software found, return empty results
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
                    'total_cves': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0,
                    'machines_affected': 0, 'last_scan': last_scan_info
                }

            # Step 2: Get CVEs for these software names from Security database
            # Build exclusion filters for security query
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

            cvss_filter = ""
            if min_cvss > 0:
                cvss_filter = f"AND c.cvss_score >= {min_cvss}"

            severity_filter = ""
            if min_sev_index > 0:
                allowed_severities = severity_order[min_sev_index:]
                severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                severity_filter = f"AND c.severity IN ({severity_list})"

            # Query security database for CVEs matching the software names
            security_sql = text(f"""
                SELECT c.id, c.severity, sc.glpi_software_name
                FROM cves c
                JOIN software_cves sc ON sc.cve_id = c.id
                WHERE sc.glpi_software_name IS NOT NULL
                {cvss_filter} {severity_filter} {name_exclusion} {cve_exclusion}
            """)

            result = session.execute(security_sql)

            # Step 3: Match CVEs with software installed on machines
            affected_machines = set()
            cve_ids_by_severity = {'Critical': set(), 'High': set(), 'Medium': set(), 'Low': set(), 'None': set()}

            for row in result:
                cve_id = row[0]
                severity = row[1]
                glpi_sw_name = row[2]

                # Check if this software is installed on any machine
                if glpi_sw_name in software_machine_map:
                    # Vendor exclusion check (simplified - would need GLPI query for full implementation)
                    if excluded_vendors:
                        # Skip vendor exclusion for now - would require additional GLPI query
                        pass

                    if severity in cve_ids_by_severity:
                        cve_ids_by_severity[severity].add(cve_id)
                    affected_machines.update(software_machine_map[glpi_sw_name])

            # Count unique CVEs per severity
            for severity in counts:
                counts[severity] = len(cve_ids_by_severity[severity])

            machines_affected = len(affected_machines)

        except Exception as e:
            logger.error(f"Error in get_dashboard_summary: {e}")

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

        Uses separate database connections:
        - GLPI connection (glpi user) for GLPI tables
        - Security connection (mmc user) for security tables
        """
        entity_ids = self._parse_entity_ids(session, location)
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']

        try:
            # Get GLPI database connection
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.error("GLPI database not available for get_cves")
                return {'total': 0, 'data': []}

            # Step 1: Get software names installed on machines from GLPI
            entity_filter_glpi = ""
            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                entity_filter_glpi = f"AND c.entities_id IN ({entity_ids_str})"

            machine_exclusion_glpi = ""
            if excluded_machines_ids:
                machine_ids_str = ','.join(str(int(mid)) for mid in excluded_machines_ids)
                machine_exclusion_glpi = f"AND c.id NOT IN ({machine_ids_str})"

            glpi_sql = text(f"""
                SELECT DISTINCT s.name as software_name, c.id as machine_id
                FROM glpi_softwares s
                JOIN glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN glpi_computers c ON c.id = isv.items_id
                WHERE c.is_deleted = 0 AND c.is_template = 0
                {entity_filter_glpi} {machine_exclusion_glpi}
            """)

            with glpi_db.db.connect() as glpi_conn:
                glpi_result = glpi_conn.execute(glpi_sql)
                software_names = set()
                software_machine_map = {}

                for row in glpi_result:
                    sw_name = row[0]
                    m_id = row[1]
                    software_names.add(sw_name)
                    if sw_name not in software_machine_map:
                        software_machine_map[sw_name] = set()
                    software_machine_map[sw_name].add(m_id)

            if not software_names:
                return {'total': 0, 'data': []}

            # Step 2: Build security query filters
            def sql_escape(val):
                return val.replace("'", "''") if val else val

            cve_filters = []
            if min_cvss > 0:
                cve_filters.append(f"c.cvss_score >= {min_cvss}")
            if severity and severity in severity_order:
                min_sev_index = severity_order.index(severity)
                if min_sev_index > 0:
                    allowed_severities = severity_order[min_sev_index:]
                    severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                    cve_filters.append(f"c.severity IN ({severity_list})")
            if filter_str:
                escaped_filter = filter_str.replace("'", "''")
                cve_filters.append(f"(c.cve_id LIKE '%{escaped_filter}%' OR c.description LIKE '%{escaped_filter}%')")

            name_exclusion = ""
            if excluded_names:
                names_escaped = ','.join(f"'{sql_escape(n)}'" for n in excluded_names)
                name_exclusion = f"AND sc.software_name NOT IN ({names_escaped})"

            cve_exclusion = ""
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{sql_escape(c)}'" for c in excluded_cve_ids)
                cve_exclusion = f"AND c.cve_id NOT IN ({cve_ids_escaped})"

            cve_where_clause = ""
            if cve_filters:
                cve_where_clause = "AND " + " AND ".join(cve_filters)

            # Step 3: Get CVEs from security database
            security_sql = text(f"""
                SELECT c.id, c.cve_id, c.cvss_score, c.severity, c.description, c.published_at,
                       sc.glpi_software_name
                FROM cves c
                JOIN software_cves sc ON sc.cve_id = c.id
                WHERE sc.glpi_software_name IS NOT NULL
                {cve_where_clause} {name_exclusion} {cve_exclusion}
                ORDER BY c.cvss_score {'DESC' if sort_order == 'desc' else 'ASC'}
            """)

            result = session.execute(security_sql)

            # Step 4: Filter CVEs that match installed software and count machines
            cve_data = {}  # cve_id -> {data, machines}
            for row in result:
                glpi_sw_name = row[6]
                if glpi_sw_name in software_machine_map:
                    cve_id = row[1]
                    if cve_id not in cve_data:
                        cve_data[cve_id] = {
                            'id': row[0],
                            'cve_id': row[1],
                            'cvss_score': row[2],
                            'severity': row[3],
                            'description': row[4],
                            'published_at': row[5],
                            'machines': set()
                        }
                    cve_data[cve_id]['machines'].update(software_machine_map[glpi_sw_name])

            # Step 5: Apply pagination and format results
            total = len(cve_data)
            sorted_cves = sorted(cve_data.values(),
                               key=lambda x: float(x['cvss_score']) if x['cvss_score'] else 0,
                               reverse=(sort_order == 'desc'))
            paginated_cves = sorted_cves[start:start + limit]

            results = []
            for cve in paginated_cves:
                sw_cves = session.query(SoftwareCve).filter(
                    SoftwareCve.cve_id == cve['id']
                ).all()
                softwares = [{'name': sc.software_name, 'version': sc.software_version}
                            for sc in sw_cves]

                results.append({
                    'id': cve['id'],
                    'cve_id': cve['cve_id'],
                    'cvss_score': str(round(float(cve['cvss_score']), 1)) if cve['cvss_score'] else '0.0',
                    'severity': cve['severity'],
                    'description': cve['description'],
                    'published_at': cve['published_at'].isoformat() if cve['published_at'] else None,
                    'softwares': softwares,
                    'machines_affected': len(cve['machines'])
                })

            return {'total': total, 'data': results}
        except Exception as e:
            logger.error(f"Error getting CVEs: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_cve_details(self, session, cve_id_str, location=''):
        """Get details of a CVE including affected machines
        Filtered by entity if location is provided.

        Uses separate database connections:
        - GLPI connection (glpi user) for GLPI tables
        - Security connection (mmc user) for security tables
        """
        cve = session.query(Cve).filter(Cve.cve_id == cve_id_str).first()
        if not cve:
            return None

        # Parse entity filter
        entity_ids = self._parse_entity_ids(session, location)

        # Get software linked to this CVE
        sw_cves = session.query(SoftwareCve).filter(
            SoftwareCve.cve_id == cve.id
        ).all()

        softwares = [{'name': sc.software_name, 'version': sc.software_version}
                    for sc in sw_cves]

        # Get affected machines using GLPI connection
        machines = []
        if sw_cves:
            try:
                glpi_db = _get_glpi_database()
                if not glpi_db:
                    logger.error("GLPI database not available for get_cve_details")
                else:
                    # Get glpi_software_names linked to this CVE
                    glpi_names = [sc.glpi_software_name for sc in sw_cves if sc.glpi_software_name]
                    if glpi_names:
                        # Build conditions using glpi_software_name
                        conditions = []
                        for glpi_name in glpi_names:
                            escaped_name = glpi_name.replace("'", "''")
                            conditions.append(f"s.name = '{escaped_name}'")

                        where_clause = " OR ".join(conditions)

                        entity_filter_glpi = ""
                        if entity_ids:
                            entity_ids_str = ','.join(str(e) for e in entity_ids)
                            entity_filter_glpi = f"AND c.entities_id IN ({entity_ids_str})"

                        glpi_sql = text(f"""
                            SELECT DISTINCT c.id as machine_id, c.name as hostname, s.name as software_name
                            FROM glpi_items_softwareversions isv
                            JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                            JOIN glpi_softwares s ON s.id = sv.softwares_id
                            JOIN glpi_computers c ON c.id = isv.items_id
                            WHERE ({where_clause})
                            AND c.is_deleted = 0 AND c.is_template = 0
                            {entity_filter_glpi}
                            ORDER BY c.name, s.name
                        """)

                        with glpi_db.db.connect() as glpi_conn:
                            result = glpi_conn.execute(glpi_sql)

                            # Build a map of software_name -> software_cve info
                            sw_cve_map = {sc.glpi_software_name: sc for sc in sw_cves if sc.glpi_software_name}

                            for row in result:
                                sw_name = row[2]
                                sc = sw_cve_map.get(sw_name)
                                machines.append({
                                    'id_glpi': row[0],
                                    'hostname': row[1],
                                    'software_name': sc.software_name if sc else sw_name,
                                    'software_version': sc.software_version if sc else ''
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

        Uses separate database connections:
        - GLPI connection (glpi user) for GLPI tables
        - Security connection (mmc user) for security tables
        """
        entity_ids = self._parse_entity_ids(session, location)
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        try:
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.error("GLPI database not available for get_machines_summary")
                return {'total': 0, 'data': []}

            # Step 1: Get machines and their software from GLPI
            where_clauses = ["c.is_deleted = 0", "c.is_template = 0"]

            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                where_clauses.append(f"c.entities_id IN ({entity_ids_str})")

            if filter_str:
                escaped_filter = filter_str.replace("'", "''")
                where_clauses.append(f"c.name LIKE '%{escaped_filter}%'")

            if excluded_machines_ids:
                machine_ids_str = ','.join(str(int(mid)) for mid in excluded_machines_ids)
                where_clauses.append(f"c.id NOT IN ({machine_ids_str})")

            filter_clause = "WHERE " + " AND ".join(where_clauses)

            # Get machines with their software names
            glpi_sql = text(f"""
                SELECT c.id as machine_id, c.name as hostname, s.name as software_name
                FROM glpi_computers c
                LEFT JOIN glpi_items_softwareversions isv ON isv.items_id = c.id
                LEFT JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                LEFT JOIN glpi_softwares s ON s.id = sv.softwares_id
                {filter_clause}
            """)

            with glpi_db.db.connect() as glpi_conn:
                glpi_result = glpi_conn.execute(glpi_sql)

                # Build machine data with software lists
                machines = {}  # machine_id -> {hostname, software_names}
                for row in glpi_result:
                    m_id = row[0]
                    hostname = row[1]
                    sw_name = row[2]

                    if m_id not in machines:
                        machines[m_id] = {'hostname': hostname, 'software_names': set()}
                    if sw_name:
                        machines[m_id]['software_names'].add(sw_name)

            if not machines:
                return {'total': 0, 'data': []}

            # Step 2: Get CVEs from security database
            def sql_escape(val):
                return val.replace("'", "''") if val else val

            cve_filters = []
            if min_cvss > 0:
                cve_filters.append(f"c.cvss_score >= {min_cvss}")
            if min_sev_index > 0:
                allowed_severities = severity_order[min_sev_index:]
                severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                cve_filters.append(f"c.severity IN ({severity_list})")

            name_exclusion = ""
            if excluded_names:
                names_escaped = ','.join(f"'{sql_escape(n)}'" for n in excluded_names)
                name_exclusion = f"AND sc.software_name NOT IN ({names_escaped})"

            cve_exclusion = ""
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{sql_escape(c)}'" for c in excluded_cve_ids)
                cve_exclusion = f"AND c.cve_id NOT IN ({cve_ids_escaped})"

            cve_where = ""
            if cve_filters:
                cve_where = "AND " + " AND ".join(cve_filters)

            security_sql = text(f"""
                SELECT c.id, c.severity, c.cvss_score, sc.glpi_software_name
                FROM cves c
                JOIN software_cves sc ON sc.cve_id = c.id
                WHERE sc.glpi_software_name IS NOT NULL
                {cve_where} {name_exclusion} {cve_exclusion}
            """)

            result = session.execute(security_sql)

            # Build CVE map: glpi_software_name -> list of CVEs
            cve_by_software = {}
            for row in result:
                sw_name = row[3]
                if sw_name not in cve_by_software:
                    cve_by_software[sw_name] = []
                cve_by_software[sw_name].append({
                    'id': row[0],
                    'severity': row[1],
                    'cvss_score': float(row[2]) if row[2] else 0.0
                })

            # Step 3: Calculate CVE counts per machine
            machine_stats = []
            for m_id, m_data in machines.items():
                cve_ids = set()
                severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'None': 0}
                max_cvss = 0.0

                for sw_name in m_data['software_names']:
                    if sw_name in cve_by_software:
                        for cve in cve_by_software[sw_name]:
                            if cve['id'] not in cve_ids:
                                cve_ids.add(cve['id'])
                                if cve['severity'] in severity_counts:
                                    severity_counts[cve['severity']] += 1
                                if cve['cvss_score'] > max_cvss:
                                    max_cvss = cve['cvss_score']

                machine_stats.append({
                    'id_glpi': m_id,
                    'hostname': m_data['hostname'],
                    'total_cves': len(cve_ids),
                    'critical': severity_counts['Critical'],
                    'high': severity_counts['High'],
                    'medium': severity_counts['Medium'],
                    'low': severity_counts['Low'],
                    'risk_score': str(round(max_cvss, 1))
                })

            # Step 4: Sort and paginate
            machine_stats.sort(key=lambda x: (float(x['risk_score']), x['hostname']), reverse=True)
            total = len(machine_stats)
            paginated = machine_stats[start:start + limit]

            return {'total': total, 'data': paginated}
        except Exception as e:
            logger.error(f"Error getting machines summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_machine_cves(self, session, id_glpi, start=0, limit=50, filter_str='', severity=None,
                         min_cvss=0.0, excluded_vendors=None, excluded_names=None, excluded_cve_ids=None,
                         excluded_machines_ids=None, excluded_groups_ids=None):
        """Get all CVEs affecting a specific machine (only latest software versions)

        Uses separate database connections:
        - GLPI connection (glpi user) for GLPI tables
        - Security connection (mmc user) for security tables
        """
        try:
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.error("GLPI database not available for get_machine_cves")
                return {'total': 0, 'data': []}

            # Step 1: Get software names for this machine from GLPI
            glpi_sql = text("""
                SELECT DISTINCT s.name as software_name
                FROM glpi_softwares s
                JOIN glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                WHERE isv.items_id = :id_glpi
            """)

            with glpi_db.db.connect() as glpi_conn:
                glpi_result = glpi_conn.execute(glpi_sql, {'id_glpi': id_glpi})
                software_names = set(row[0] for row in glpi_result)

            if not software_names:
                return {'total': 0, 'data': []}

            # Step 2: Get CVEs from security database
            def sql_escape(val):
                return val.replace("'", "''") if val else val

            cve_filters = []
            if min_cvss > 0:
                cve_filters.append(f"c.cvss_score >= {min_cvss}")
            if severity:
                cve_filters.append(f"c.severity = '{sql_escape(severity)}'")
            if filter_str:
                escaped_filter = filter_str.replace("'", "''")
                cve_filters.append(f"(c.cve_id LIKE '%{escaped_filter}%' OR c.description LIKE '%{escaped_filter}%')")

            name_exclusion = ""
            if excluded_names:
                names_escaped = ','.join(f"'{sql_escape(n)}'" for n in excluded_names)
                name_exclusion = f"AND sc.software_name NOT IN ({names_escaped})"

            cve_exclusion = ""
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{sql_escape(c)}'" for c in excluded_cve_ids)
                cve_exclusion = f"AND c.cve_id NOT IN ({cve_ids_escaped})"

            cve_where = ""
            if cve_filters:
                cve_where = "AND " + " AND ".join(cve_filters)

            security_sql = text(f"""
                SELECT c.id, c.cve_id, c.cvss_score, c.severity, c.description,
                       c.published_at, c.last_modified,
                       sc.software_name, sc.software_version, sc.glpi_software_name
                FROM cves c
                JOIN software_cves sc ON sc.cve_id = c.id
                WHERE sc.glpi_software_name IS NOT NULL
                {cve_where} {name_exclusion} {cve_exclusion}
                ORDER BY c.cvss_score DESC
            """)

            result = session.execute(security_sql)

            # Step 3: Filter CVEs by installed software and aggregate
            cve_data = {}  # cve_id -> {data, software_names, software_versions}
            for row in result:
                glpi_sw_name = row[9]
                if glpi_sw_name not in software_names:
                    continue

                cve_id = row[1]
                if cve_id not in cve_data:
                    cve_data[cve_id] = {
                        'cve_id': row[1],
                        'cvss_score': float(row[2]) if row[2] else 0.0,
                        'severity': row[3],
                        'description': row[4],
                        'published_at': row[5],
                        'last_modified': row[6],
                        'software_names': set(),
                        'software_versions': set()
                    }
                cve_data[cve_id]['software_names'].add(row[7])
                cve_data[cve_id]['software_versions'].add(row[8])

            # Step 4: Format and paginate results
            cves_list = sorted(cve_data.values(), key=lambda x: x['cvss_score'], reverse=True)
            total = len(cves_list)
            paginated = cves_list[start:start + limit]

            cves = []
            for cve in paginated:
                cves.append({
                    'cve_id': cve['cve_id'],
                    'cvss_score': str(round(cve['cvss_score'], 1)),
                    'severity': cve['severity'],
                    'description': cve['description'],
                    'published_at': str(cve['published_at']) if cve['published_at'] else None,
                    'last_modified': str(cve['last_modified']) if cve['last_modified'] else None,
                    'software_name': ', '.join(sorted(cve['software_names'])),
                    'software_version': ', '.join(sorted(cve['software_versions']))
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

        Uses separate database connections:
        - GLPI connection (glpi user) for GLPI tables
        - Security connection (mmc user) for security tables
        """
        try:
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.error("GLPI database not available for get_machine_softwares_summary")
                return {'total': 0, 'data': []}

            # Step 1: Get software names for this machine from GLPI
            glpi_sql = text("""
                SELECT DISTINCT s.name as software_name
                FROM glpi_softwares s
                JOIN glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                WHERE isv.items_id = :id_glpi
            """)

            with glpi_db.db.connect() as glpi_conn:
                glpi_result = glpi_conn.execute(glpi_sql, {'id_glpi': id_glpi})
                software_names = set(row[0] for row in glpi_result)

            if not software_names:
                return {'total': 0, 'data': []}

            # Step 2: Get CVEs from security database
            def sql_escape(val):
                return val.replace("'", "''") if val else val

            cve_filters = []
            if min_cvss > 0:
                cve_filters.append(f"c.cvss_score >= {min_cvss}")
            if filter_str:
                escaped_filter = filter_str.replace("'", "''")
                cve_filters.append(f"sc.software_name LIKE '%{escaped_filter}%'")

            name_exclusion = ""
            if excluded_names:
                names_escaped = ','.join(f"'{sql_escape(n)}'" for n in excluded_names)
                name_exclusion = f"AND sc.software_name NOT IN ({names_escaped})"

            cve_exclusion = ""
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{sql_escape(c)}'" for c in excluded_cve_ids)
                cve_exclusion = f"AND c.cve_id NOT IN ({cve_ids_escaped})"

            cve_where = ""
            if cve_filters:
                cve_where = "AND " + " AND ".join(cve_filters)

            security_sql = text(f"""
                SELECT sc.software_name, sc.software_version, sc.glpi_software_name,
                       c.id as cve_id, c.severity, c.cvss_score
                FROM software_cves sc
                JOIN cves c ON c.id = sc.cve_id
                WHERE sc.glpi_software_name IS NOT NULL
                {cve_where} {name_exclusion} {cve_exclusion}
            """)

            result = session.execute(security_sql)

            # Step 3: Aggregate by software
            software_stats = {}  # (software_name, software_version) -> stats
            for row in result:
                glpi_sw_name = row[2]
                if glpi_sw_name not in software_names:
                    continue

                key = (row[0], row[1])
                if key not in software_stats:
                    software_stats[key] = {
                        'software_name': row[0],
                        'software_version': row[1],
                        'cve_ids': set(),
                        'severity_counts': {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'None': 0},
                        'max_cvss': 0.0
                    }

                cve_id = row[3]
                if cve_id not in software_stats[key]['cve_ids']:
                    software_stats[key]['cve_ids'].add(cve_id)
                    sev = row[4]
                    cvss = float(row[5]) if row[5] else 0.0
                    if sev in software_stats[key]['severity_counts']:
                        software_stats[key]['severity_counts'][sev] += 1
                    if cvss > software_stats[key]['max_cvss']:
                        software_stats[key]['max_cvss'] = cvss

            # Step 4: Format and paginate
            data_list = []
            for key, stats in software_stats.items():
                data_list.append({
                    'software_name': stats['software_name'],
                    'software_version': stats['software_version'],
                    'total_cves': len(stats['cve_ids']),
                    'critical': stats['severity_counts']['Critical'],
                    'high': stats['severity_counts']['High'],
                    'medium': stats['severity_counts']['Medium'],
                    'low': stats['severity_counts']['Low'],
                    'max_cvss': str(round(stats['max_cvss'], 1))
                })

            data_list.sort(key=lambda x: (float(x['max_cvss']), x['total_cves']), reverse=True)
            total = len(data_list)
            paginated = data_list[start:start + limit]

            return {'total': total, 'data': paginated}
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

        Uses separate database connections:
        - GLPI connection (glpi user) for GLPI tables
        - Security connection (mmc user) for security tables
        """
        entity_ids = self._parse_entity_ids(session, location)
        severity_order = ['None', 'Low', 'Medium', 'High', 'Critical']
        min_sev_index = severity_order.index(min_severity) if min_severity in severity_order else 0

        try:
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.error("GLPI database not available for get_softwares_summary")
                return {'total': 0, 'data': []}

            # Step 1: Get software names installed on machines from GLPI
            entity_filter_glpi = ""
            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                entity_filter_glpi = f"AND c.entities_id IN ({entity_ids_str})"

            machine_exclusion_glpi = ""
            if excluded_machines_ids:
                machine_ids_str = ','.join(str(int(mid)) for mid in excluded_machines_ids)
                machine_exclusion_glpi = f"AND c.id NOT IN ({machine_ids_str})"

            glpi_sql = text(f"""
                SELECT s.name as software_name, COUNT(DISTINCT c.id) as machine_count
                FROM glpi_softwares s
                JOIN glpi_softwareversions sv ON sv.softwares_id = s.id
                JOIN glpi_items_softwareversions isv ON isv.softwareversions_id = sv.id
                JOIN glpi_computers c ON c.id = isv.items_id
                WHERE c.is_deleted = 0 AND c.is_template = 0
                {entity_filter_glpi} {machine_exclusion_glpi}
                GROUP BY s.name
            """)

            with glpi_db.db.connect() as glpi_conn:
                glpi_result = glpi_conn.execute(glpi_sql)
                # Build map of software_name -> machine_count
                software_machine_counts = {}
                for row in glpi_result:
                    software_machine_counts[row[0]] = row[1]

            if not software_machine_counts:
                return {'total': 0, 'data': []}

            # Step 2: Get CVEs from security database with filters
            def sql_escape(val):
                return val.replace("'", "''") if val else val

            cve_filters = []
            if min_cvss > 0:
                cve_filters.append(f"c.cvss_score >= {min_cvss}")
            if min_sev_index > 0:
                allowed_severities = severity_order[min_sev_index:]
                severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                cve_filters.append(f"c.severity IN ({severity_list})")

            name_exclusion = ""
            if excluded_names:
                names_escaped = ','.join(f"'{sql_escape(n)}'" for n in excluded_names)
                name_exclusion = f"AND sc.software_name NOT IN ({names_escaped})"

            cve_exclusion = ""
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{sql_escape(c)}'" for c in excluded_cve_ids)
                cve_exclusion = f"AND c.cve_id NOT IN ({cve_ids_escaped})"

            filter_clause = ""
            if filter_str:
                escaped_filter = filter_str.replace("'", "''")
                filter_clause = f"AND (sc.software_name LIKE '%{escaped_filter}%' OR sc.software_version LIKE '%{escaped_filter}%')"

            cve_where = ""
            if cve_filters:
                cve_where = "AND " + " AND ".join(cve_filters)

            security_sql = text(f"""
                SELECT sc.software_name, sc.software_version, sc.glpi_software_name,
                       c.id as cve_id, c.severity, c.cvss_score
                FROM software_cves sc
                JOIN cves c ON c.id = sc.cve_id
                WHERE sc.glpi_software_name IS NOT NULL
                {cve_where} {name_exclusion} {cve_exclusion} {filter_clause}
            """)

            result = session.execute(security_sql)

            # Step 3: Aggregate CVEs by software, filtering by installed software
            software_stats = {}  # (software_name, software_version) -> stats
            for row in result:
                glpi_sw_name = row[2]
                if glpi_sw_name not in software_machine_counts:
                    continue  # Software not installed in GLPI

                key = (row[0], row[1])  # (software_name, software_version)
                if key not in software_stats:
                    software_stats[key] = {
                        'software_name': row[0],
                        'software_version': row[1],
                        'glpi_software_name': glpi_sw_name,
                        'cve_ids': set(),
                        'severity_counts': {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'None': 0},
                        'max_cvss': 0.0,
                        'machines_affected': software_machine_counts.get(glpi_sw_name, 0)
                    }

                cve_id = row[3]
                if cve_id not in software_stats[key]['cve_ids']:
                    software_stats[key]['cve_ids'].add(cve_id)
                    severity = row[4]
                    cvss = float(row[5]) if row[5] else 0.0
                    if severity in software_stats[key]['severity_counts']:
                        software_stats[key]['severity_counts'][severity] += 1
                    if cvss > software_stats[key]['max_cvss']:
                        software_stats[key]['max_cvss'] = cvss

            # Step 4: Format results and paginate
            results_list = []
            for key, stats in software_stats.items():
                results_list.append({
                    'software_name': stats['software_name'],
                    'software_version': stats['software_version'],
                    'total_cves': len(stats['cve_ids']),
                    'critical': stats['severity_counts']['Critical'],
                    'high': stats['severity_counts']['High'],
                    'medium': stats['severity_counts']['Medium'],
                    'low': stats['severity_counts']['Low'],
                    'max_cvss': str(round(stats['max_cvss'], 1)),
                    'machines_affected': stats['machines_affected'],
                    'store_version': None,
                    'store_has_update': False,
                    'store_package_uuid': None
                })

            # Sort by max_cvss DESC, total_cves DESC
            results_list.sort(key=lambda x: (float(x['max_cvss']), x['total_cves']), reverse=True)

            total = len(results_list)
            paginated = results_list[start:start + limit]

            # Enrich with store info for each software
            if paginated:
                self._enrich_with_store_info(session, paginated)

            return {'total': total, 'data': paginated}
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

        try:
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.warning("GLPI database not available for get_entities_summary")
                return {'total': 0, 'data': []}

            # Build filter clause for GLPI
            filter_clause = ""
            if filter_str:
                filter_str_escaped = filter_str.replace("'", "''")
                filter_clause = f"AND e.name LIKE '%{filter_str_escaped}%'"

            # Filter by user's accessible entities
            entity_ids = self._parse_entity_ids(session, user_entities)
            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                filter_clause += f" AND e.id IN ({entity_ids_str})"

            # Machine exclusion filter
            machine_filter = ""
            if excluded_machines_ids:
                machine_ids_str = ','.join(str(int(mid)) for mid in excluded_machines_ids)
                machine_filter = f"AND c.id NOT IN ({machine_ids_str})"

            with glpi_db.db.connect() as glpi_conn:
                # Step 1: Count total entities from GLPI
                count_sql = text(f"""
                    SELECT COUNT(DISTINCT e.id) as total
                    FROM glpi_entities e
                    WHERE 1=1 {filter_clause}
                """)
                count_result = glpi_conn.execute(count_sql)
                total = count_result.scalar() or 0

                # Step 2: Get entities with pagination from GLPI
                entities_sql = text(f"""
                    SELECT e.id as entity_id, e.name as entity_name, e.completename as entity_fullname
                    FROM glpi_entities e
                    WHERE 1=1 {filter_clause}
                    ORDER BY e.name
                    LIMIT {limit} OFFSET {start}
                """)
                entities_result = glpi_conn.execute(entities_sql)
                entities = {row.entity_id: {
                    'entity_id': row.entity_id,
                    'entity_name': row.entity_name,
                    'entity_fullname': row.entity_fullname or row.entity_name,
                    'machines_count': 0,
                    'total_cves': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0,
                    'max_cvss': 0.0
                } for row in entities_result}

                if not entities:
                    return {'total': total, 'data': []}

                entity_ids_str = ','.join(str(eid) for eid in entities.keys())

                # Step 3: Get machine counts per entity
                machines_count_sql = text(f"""
                    SELECT c.entities_id, COUNT(DISTINCT c.id) as cnt
                    FROM glpi_computers c
                    WHERE c.is_deleted = 0 AND c.is_template = 0
                    AND c.entities_id IN ({entity_ids_str})
                    {machine_filter}
                    GROUP BY c.entities_id
                """)
                machines_count_result = glpi_conn.execute(machines_count_sql)
                for row in machines_count_result:
                    if row.entities_id in entities:
                        entities[row.entities_id]['machines_count'] = row.cnt

                # Step 4: Get all (machine_id, entity_id, software_name) for these entities
                software_sql = text(f"""
                    SELECT DISTINCT c.id as machine_id, c.entities_id, s.name as software_name
                    FROM glpi_computers c
                    JOIN glpi_items_softwareversions isv ON isv.items_id = c.id AND isv.itemtype = 'Computer'
                    JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN glpi_softwares s ON s.id = sv.softwares_id
                    WHERE c.is_deleted = 0 AND c.is_template = 0
                    AND c.entities_id IN ({entity_ids_str})
                    {machine_filter}
                """)
                software_result = glpi_conn.execute(software_sql)

                # Build mapping: entity_id -> set of software_names
                entity_software = {eid: set() for eid in entities.keys()}
                for row in software_result:
                    if row.entities_id in entity_software:
                        entity_software[row.entities_id].add(row.software_name)

            # Step 5: Get CVEs from security DB
            # Build CVE filters
            cve_where = "WHERE 1=1"
            if min_cvss > 0:
                cve_where += f" AND c.cvss_score >= {min_cvss}"
            if min_sev_index > 0:
                allowed_severities = severity_order[min_sev_index:]
                severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                cve_where += f" AND c.severity IN ({severity_list})"
            if excluded_names:
                names_escaped = ','.join(f"'{n.replace(chr(39), chr(39)+chr(39))}'" for n in excluded_names)
                cve_where += f" AND sc.software_name NOT IN ({names_escaped})"
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{c.replace(chr(39), chr(39)+chr(39))}'" for c in excluded_cve_ids)
                cve_where += f" AND c.cve_id NOT IN ({cve_ids_escaped})"

            cves_sql = text(f"""
                SELECT sc.glpi_software_name, c.id as cve_id, c.severity, c.cvss_score
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                {cve_where}
                AND sc.glpi_software_name IS NOT NULL
            """)
            cves_result = session.execute(cves_sql)

            # Build mapping: software_name -> list of (cve_id, severity, cvss_score)
            software_cves = {}
            for row in cves_result:
                if row.glpi_software_name not in software_cves:
                    software_cves[row.glpi_software_name] = []
                software_cves[row.glpi_software_name].append({
                    'cve_id': row.cve_id,
                    'severity': row.severity,
                    'cvss_score': float(row.cvss_score) if row.cvss_score else 0.0
                })

            # Step 6: Calculate CVE stats per entity in Python
            for entity_id, entity_data in entities.items():
                cve_ids_seen = set()
                severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
                max_cvss = 0.0

                for sw_name in entity_software.get(entity_id, set()):
                    for cve in software_cves.get(sw_name, []):
                        if cve['cve_id'] not in cve_ids_seen:
                            cve_ids_seen.add(cve['cve_id'])
                            if cve['severity'] in severity_counts:
                                severity_counts[cve['severity']] += 1
                            if cve['cvss_score'] > max_cvss:
                                max_cvss = cve['cvss_score']

                entity_data['total_cves'] = len(cve_ids_seen)
                entity_data['critical'] = severity_counts['Critical']
                entity_data['high'] = severity_counts['High']
                entity_data['medium'] = severity_counts['Medium']
                entity_data['low'] = severity_counts['Low']
                entity_data['max_cvss'] = str(round(max_cvss, 1))

            # Sort by max_cvss DESC, total_cves DESC
            results = sorted(entities.values(),
                           key=lambda x: (float(x['max_cvss']), x['total_cves']),
                           reverse=True)

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

        try:
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.warning("GLPI database not available for get_groups_summary")
                return {'total': 0, 'data': []}

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
                escaped_login = user_login.replace("'", "''")
                share_filter = f"""AND g.id IN (
                    SELECT DISTINCT sg.FK_groups
                    FROM dyngroup.ShareGroup sg
                    JOIN dyngroup.Users u ON u.id = sg.FK_users
                    WHERE u.login = '{escaped_login}'
                )"""

            # Step 1: Count total groups from dyngroup (via session/mmc)
            count_sql = text(f"""
                SELECT COUNT(DISTINCT g.id) as total
                FROM dyngroup.Groups g
                WHERE 1=1 {filter_clause} {share_filter}
            """)
            count_result = session.execute(count_sql, params)
            total = count_result.scalar() or 0

            # Step 2: Get groups with pagination from dyngroup
            groups_sql = text(f"""
                SELECT g.id as group_id, g.name as group_name,
                       CASE WHEN g.query IS NOT NULL AND LENGTH(g.query) > 0 THEN 1 ELSE 0 END as is_dynamic
                FROM dyngroup.Groups g
                WHERE 1=1 {filter_clause} {share_filter}
                ORDER BY g.name
                LIMIT :limit OFFSET :start
            """)
            groups_result = session.execute(groups_sql, params)
            groups = {row.group_id: {
                'group_id': row.group_id,
                'group_name': row.group_name,
                'group_type': 'Dynamic' if int(row.is_dynamic) == 1 else 'Static',
                'machines_count': 0,
                'total_cves': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0,
                'max_cvss': 0.0
            } for row in groups_result}

            if not groups:
                return {'total': total, 'data': []}

            group_ids_str = ','.join(str(gid) for gid in groups.keys())

            # Machine exclusion filter
            machine_exclusion_ids = set()
            if excluded_machines_ids:
                machine_exclusion_ids.update(int(mid) for mid in excluded_machines_ids)

            # Step 3: Get machines per group from dyngroup (uuid format: UUID<glpi_id>)
            machines_sql = text(f"""
                SELECT r.FK_groups as group_id, dm.uuid
                FROM dyngroup.Results r
                JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                WHERE r.FK_groups IN ({group_ids_str})
            """)
            machines_result = session.execute(machines_sql)

            # Build mapping: group_id -> set of machine_ids (GLPI)
            group_machines = {gid: set() for gid in groups.keys()}
            all_machine_ids = set()
            for row in machines_result:
                if row.uuid and row.uuid.startswith('UUID'):
                    try:
                        machine_id = int(row.uuid[4:])
                        if machine_id not in machine_exclusion_ids:
                            group_machines[row.group_id].add(machine_id)
                            all_machine_ids.add(machine_id)
                    except ValueError:
                        pass

            # Update machines_count
            for group_id in groups:
                groups[group_id]['machines_count'] = len(group_machines[group_id])

            if not all_machine_ids:
                results = sorted(groups.values(),
                               key=lambda x: (float(x['max_cvss']), x['total_cves']),
                               reverse=True)
                return {'total': total, 'data': results}

            # Step 4: Get software_names per machine from GLPI
            machine_ids_str = ','.join(str(mid) for mid in all_machine_ids)
            with glpi_db.db.connect() as glpi_conn:
                software_sql = text(f"""
                    SELECT DISTINCT c.id as machine_id, s.name as software_name
                    FROM glpi_computers c
                    JOIN glpi_items_softwareversions isv ON isv.items_id = c.id AND isv.itemtype = 'Computer'
                    JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN glpi_softwares s ON s.id = sv.softwares_id
                    WHERE c.id IN ({machine_ids_str})
                    AND c.is_deleted = 0 AND c.is_template = 0
                """)
                software_result = glpi_conn.execute(software_sql)

                # Build mapping: machine_id -> set of software_names
                machine_software = {}
                for row in software_result:
                    if row.machine_id not in machine_software:
                        machine_software[row.machine_id] = set()
                    machine_software[row.machine_id].add(row.software_name)

            # Step 5: Get CVEs from security DB
            cve_where = "WHERE sc.glpi_software_name IS NOT NULL"
            if min_cvss > 0:
                cve_where += f" AND c.cvss_score >= {min_cvss}"
            if min_sev_index > 0:
                allowed_severities = severity_order[min_sev_index:]
                severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                cve_where += f" AND c.severity IN ({severity_list})"
            if excluded_names:
                names_escaped = ','.join(f"'{n.replace(chr(39), chr(39)+chr(39))}'" for n in excluded_names)
                cve_where += f" AND sc.software_name NOT IN ({names_escaped})"
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{c.replace(chr(39), chr(39)+chr(39))}'" for c in excluded_cve_ids)
                cve_where += f" AND c.cve_id NOT IN ({cve_ids_escaped})"

            cves_sql = text(f"""
                SELECT sc.glpi_software_name, c.id as cve_id, c.severity, c.cvss_score
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                {cve_where}
            """)
            cves_result = session.execute(cves_sql)

            # Build mapping: software_name -> list of (cve_id, severity, cvss_score)
            software_cves = {}
            for row in cves_result:
                if row.glpi_software_name not in software_cves:
                    software_cves[row.glpi_software_name] = []
                software_cves[row.glpi_software_name].append({
                    'cve_id': row.cve_id,
                    'severity': row.severity,
                    'cvss_score': float(row.cvss_score) if row.cvss_score else 0.0
                })

            # Step 6: Calculate CVE stats per group in Python
            for group_id, group_data in groups.items():
                cve_ids_seen = set()
                severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
                max_cvss = 0.0

                for machine_id in group_machines.get(group_id, set()):
                    for sw_name in machine_software.get(machine_id, set()):
                        for cve in software_cves.get(sw_name, []):
                            if cve['cve_id'] not in cve_ids_seen:
                                cve_ids_seen.add(cve['cve_id'])
                                if cve['severity'] in severity_counts:
                                    severity_counts[cve['severity']] += 1
                                if cve['cvss_score'] > max_cvss:
                                    max_cvss = cve['cvss_score']

                group_data['total_cves'] = len(cve_ids_seen)
                group_data['critical'] = severity_counts['Critical']
                group_data['high'] = severity_counts['High']
                group_data['medium'] = severity_counts['Medium']
                group_data['low'] = severity_counts['Low']
                group_data['max_cvss'] = str(round(max_cvss, 1))

            # Sort by max_cvss DESC, total_cves DESC
            results = sorted(groups.values(),
                           key=lambda x: (float(x['max_cvss']), x['total_cves']),
                           reverse=True)

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

        try:
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.warning("GLPI database not available for get_group_machines")
                return {'total': 0, 'data': []}

            # Machine exclusion filter
            machine_exclusion_ids = set()
            if excluded_machines_ids:
                machine_exclusion_ids.update(int(mid) for mid in excluded_machines_ids)

            # Step 1: Get machine UUIDs from this group via dyngroup
            machines_sql = text("""
                SELECT DISTINCT dm.uuid
                FROM dyngroup.Results r
                JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                WHERE r.FK_groups = :group_id
            """)
            machines_result = session.execute(machines_sql, {'group_id': group_id})

            # Extract GLPI machine IDs from UUIDs
            all_machine_ids = []
            for row in machines_result:
                if row.uuid and row.uuid.startswith('UUID'):
                    try:
                        machine_id = int(row.uuid[4:])
                        if machine_id not in machine_exclusion_ids:
                            all_machine_ids.append(machine_id)
                    except ValueError:
                        pass

            if not all_machine_ids:
                return {'total': 0, 'data': []}

            machine_ids_str = ','.join(str(mid) for mid in all_machine_ids)

            # Step 2: Get machine info from GLPI with filtering and pagination
            with glpi_db.db.connect() as glpi_conn:
                # Build filter clause
                filter_clause = ""
                if filter_str:
                    filter_str_escaped = filter_str.replace("'", "''")
                    filter_clause = f"AND c.name LIKE '%{filter_str_escaped}%'"

                # Count total
                count_sql = text(f"""
                    SELECT COUNT(*) as total
                    FROM glpi_computers c
                    WHERE c.id IN ({machine_ids_str})
                    AND c.is_deleted = 0 AND c.is_template = 0
                    {filter_clause}
                """)
                count_result = glpi_conn.execute(count_sql)
                total = count_result.scalar() or 0

                # Get machines with pagination
                machines_info_sql = text(f"""
                    SELECT c.id, c.name as hostname
                    FROM glpi_computers c
                    WHERE c.id IN ({machine_ids_str})
                    AND c.is_deleted = 0 AND c.is_template = 0
                    {filter_clause}
                    ORDER BY c.name
                    LIMIT {limit} OFFSET {start}
                """)
                machines_info_result = glpi_conn.execute(machines_info_sql)
                machines = {row.id: {
                    'id_glpi': row.id,
                    'hostname': row.hostname,
                    'total_cves': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0,
                    'risk_score': 0.0
                } for row in machines_info_result}

                if not machines:
                    return {'total': total, 'data': []}

                # Step 3: Get software per machine from GLPI
                machine_ids_page = ','.join(str(mid) for mid in machines.keys())
                software_sql = text(f"""
                    SELECT DISTINCT c.id as machine_id, s.name as software_name
                    FROM glpi_computers c
                    JOIN glpi_items_softwareversions isv ON isv.items_id = c.id AND isv.itemtype = 'Computer'
                    JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN glpi_softwares s ON s.id = sv.softwares_id
                    WHERE c.id IN ({machine_ids_page})
                """)
                software_result = glpi_conn.execute(software_sql)

                # Build mapping: machine_id -> set of software_names
                machine_software = {mid: set() for mid in machines.keys()}
                for row in software_result:
                    if row.machine_id in machine_software:
                        machine_software[row.machine_id].add(row.software_name)

            # Step 4: Get CVEs from security DB
            cve_where = "WHERE sc.glpi_software_name IS NOT NULL"
            if min_cvss > 0:
                cve_where += f" AND c.cvss_score >= {min_cvss}"
            if min_sev_index > 0:
                allowed_severities = severity_order[min_sev_index:]
                severity_list = ','.join(f"'{s}'" for s in allowed_severities)
                cve_where += f" AND c.severity IN ({severity_list})"
            if excluded_names:
                names_escaped = ','.join(f"'{n.replace(chr(39), chr(39)+chr(39))}'" for n in excluded_names)
                cve_where += f" AND sc.software_name NOT IN ({names_escaped})"
            if excluded_cve_ids:
                cve_ids_escaped = ','.join(f"'{cv.replace(chr(39), chr(39)+chr(39))}'" for cv in excluded_cve_ids)
                cve_where += f" AND c.cve_id NOT IN ({cve_ids_escaped})"

            cves_sql = text(f"""
                SELECT sc.glpi_software_name, c.id as cve_id, c.severity, c.cvss_score
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                {cve_where}
            """)
            cves_result = session.execute(cves_sql)

            # Build mapping: software_name -> list of CVE info
            software_cves = {}
            for row in cves_result:
                if row.glpi_software_name not in software_cves:
                    software_cves[row.glpi_software_name] = []
                software_cves[row.glpi_software_name].append({
                    'cve_id': row.cve_id,
                    'severity': row.severity,
                    'cvss_score': float(row.cvss_score) if row.cvss_score else 0.0
                })

            # Step 5: Calculate CVE stats per machine in Python
            for machine_id, machine_data in machines.items():
                cve_ids_seen = set()
                severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
                max_cvss = 0.0

                for sw_name in machine_software.get(machine_id, set()):
                    for cve in software_cves.get(sw_name, []):
                        if cve['cve_id'] not in cve_ids_seen:
                            cve_ids_seen.add(cve['cve_id'])
                            if cve['severity'] in severity_counts:
                                severity_counts[cve['severity']] += 1
                            if cve['cvss_score'] > max_cvss:
                                max_cvss = cve['cvss_score']

                machine_data['total_cves'] = len(cve_ids_seen)
                machine_data['critical'] = severity_counts['Critical']
                machine_data['high'] = severity_counts['High']
                machine_data['medium'] = severity_counts['Medium']
                machine_data['low'] = severity_counts['Low']
                machine_data['risk_score'] = str(round(max_cvss, 1))

            # Sort by risk_score DESC, hostname ASC
            results = sorted(machines.values(),
                           key=lambda x: (-float(x['risk_score']), x['hostname']))

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

        try:
            # Step 1: Get software names with CVEs of given severity from security DB
            cve_result = session.execute(text("""
                SELECT DISTINCT sc.glpi_software_name
                FROM security.software_cves sc
                JOIN security.cves c ON c.id = sc.cve_id
                WHERE c.severity = :severity
                AND sc.glpi_software_name IS NOT NULL
            """), {'severity': severity})
            vulnerable_software_names = [row[0] for row in cve_result]

            if not vulnerable_software_names:
                return []

            # Step 2: Get machines with these software via GLPI connection
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.warning("GLPI database not available for get_machines_by_severity")
                return []

            # Build entity filter
            entity_filter = ""
            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                entity_filter = f"AND c.entities_id IN ({entity_ids_str})"

            # Build software names filter
            software_names_escaped = ','.join(f"'{n.replace(chr(39), chr(39)+chr(39))}'" for n in vulnerable_software_names)

            with glpi_db.db.connect() as glpi_conn:
                glpi_result = glpi_conn.execute(text(f"""
                    SELECT DISTINCT c.id, c.name
                    FROM glpi_computers c
                    JOIN glpi_items_softwareversions isv ON isv.items_id = c.id AND isv.itemtype = 'Computer'
                    JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN glpi_softwares s ON s.id = sv.softwares_id
                    WHERE c.is_deleted = 0 AND c.is_template = 0
                    AND s.name IN ({software_names_escaped})
                    {entity_filter}
                    ORDER BY c.name
                """))
                machines = [{'uuid': f"UUID{row[0]}", 'hostname': row[1]} for row in glpi_result]

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

        try:
            # Step 1: Get the glpi_software_name from software_cves (security DB)
            glpi_name_sql = text("""
                SELECT COALESCE(glpi_software_name, software_name) as glpi_name
                FROM security.software_cves
                WHERE software_name = :software_name
                LIMIT 1
            """)
            glpi_result = session.execute(glpi_name_sql, {'software_name': software_name})
            glpi_row = glpi_result.fetchone()
            glpi_software_name = glpi_row.glpi_name if glpi_row else software_name

            # Step 2: Query GLPI directly for machines with this software
            glpi_db = _get_glpi_database()
            if not glpi_db:
                logger.warning("GLPI database not available for get_machines_for_vulnerable_software")
                return {'total': 0, 'data': []}

            # Build entity filter for GLPI
            entity_filter = ""
            if entity_ids:
                entity_ids_str = ','.join(str(e) for e in entity_ids)
                entity_filter = f"AND c.entities_id IN ({entity_ids_str})"

            # Build filter clause
            filter_clause = ""
            if filter_str:
                filter_str_escaped = filter_str.replace("'", "''")
                filter_clause = f"AND c.name LIKE '%{filter_str_escaped}%'"

            # Escape software name for SQL
            glpi_software_name_escaped = glpi_software_name.replace("'", "''")

            with glpi_db.db.connect() as glpi_conn:
                # Count total
                count_sql = text(f"""
                    SELECT COUNT(DISTINCT c.id) as total
                    FROM glpi_computers c
                    JOIN glpi_items_softwareversions isv ON isv.items_id = c.id AND isv.itemtype = 'Computer'
                    JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN glpi_softwares s ON s.id = sv.softwares_id
                    WHERE c.is_deleted = 0 AND c.is_template = 0
                    AND s.name = '{glpi_software_name_escaped}'
                    {entity_filter}
                    {filter_clause}
                """)
                count_result = glpi_conn.execute(count_sql)
                total = count_result.scalar() or 0

                # Get machines with pagination
                main_sql = text(f"""
                    SELECT DISTINCT
                        c.id,
                        c.name as hostname,
                        c.entities_id as entity_id,
                        e.name as entity_name,
                        s.name as glpi_software_name,
                        sv.name as installed_version
                    FROM glpi_computers c
                    JOIN glpi_items_softwareversions isv ON isv.items_id = c.id AND isv.itemtype = 'Computer'
                    JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
                    JOIN glpi_softwares s ON s.id = sv.softwares_id
                    LEFT JOIN glpi_entities e ON e.id = c.entities_id
                    WHERE c.is_deleted = 0 AND c.is_template = 0
                    AND s.name = '{glpi_software_name_escaped}'
                    {entity_filter}
                    {filter_clause}
                    ORDER BY c.name
                    LIMIT {limit} OFFSET {start}
                """)

                result = glpi_conn.execute(main_sql)
                machines = []
                for row in result:
                    machines.append({
                        'id': row.id,
                        'uuid': f"UUID{row.id}",
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
