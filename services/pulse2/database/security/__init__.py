# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import Counter
from sqlalchemy import create_engine, MetaData, desc, text, bindparam
from sqlalchemy.exc import DBAPIError, IntegrityError
from datetime import datetime
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.security.schema import Cve, SoftwareCve, Scan
import logging
import re

logger = logging.getLogger()


SEVERITIES = ['None', 'Low', 'Medium', 'High', 'Critical']

# GLPI OS of computers `c`, shared with the scanner so that inventory and display match.
OS_JOINS = """
    LEFT JOIN glpi_items_operatingsystems ios
        ON ios.items_id = c.id AND ios.itemtype = 'Computer' AND ios.is_deleted = 0
    LEFT JOIN glpi_operatingsystems os ON os.id = ios.operatingsystems_id
    LEFT JOIN glpi_operatingsystemversions osv ON osv.id = ios.operatingsystemversions_id
    LEFT JOIN glpi_operatingsystemkernelversions osk ON osk.id = ios.operatingsystemkernelversions_id
    LEFT JOIN glpi_operatingsystemservicepacks ossp ON ossp.id = ios.operatingsystemservicepacks_id"""
OS_LABEL = "CONCAT_WS(' ', os.name, osv.name)"
# Full Windows 10/11 build ('10.0.19045' + '19045.6466' -> '10.0.19045.6466'), NULL otherwise.
OS_BUILD = ("CASE WHEN LEFT(osk.name, 5) = '10.0.' AND ossp.name REGEXP '^[0-9]+[.][0-9]+$' "
            "THEN CONCAT('10.0.', ossp.name) END")
PLATFORMS = {
    'windows': "os.name LIKE '%windows%'",
    'linux': ("os.name <> '' AND os.name NOT LIKE '%windows%' "
              "AND os.name NOT LIKE '%mac%' AND os.name NOT LIKE '%darwin%'"),
}


def _get_glpi_database():
    """GLPI database instance (glpi credentials), or None if not available."""
    try:
        from mmc.plugins.glpi.database import Glpi
        glpi = Glpi()
        if glpi.is_activated:
            return glpi.database
        return None
    except Exception as e:
        logger.warning(f"Could not get GLPI database connection: {e}")
        return None


def _run(conn, sql, **params):
    """Execute sql; list/set/tuple params are expanded (`IN :param`)."""
    params = {k: list(v) if isinstance(v, (set, tuple)) else v for k, v in params.items()}
    lists = [bindparam(k, expanding=True) for k, v in params.items() if isinstance(v, list)]
    return conn.execute(text(sql).bindparams(*lists), params)


def _glpi(sql, **params):
    glpi_db = _get_glpi_database()
    if not glpi_db:
        raise Exception("GLPI database not available")
    with glpi_db.db.connect() as conn:
        return _run(conn, sql, **params).fetchall()


def _glpi_names(sql, names, **params):
    return {r[0] for r in _glpi(sql, names=names, **params)} if names else set()


def _computers_where(entity_ids=None, machine_ids=None, excluded=None, hostname='', platform=''):
    """WHERE clause on active GLPI computers `c`; entity_ids/machine_ids: None = all, [] = none."""
    sql = "c.is_deleted = 0 AND c.is_template = 0"
    params = {}
    if machine_ids is not None:
        sql += " AND c.id IN :machine_ids"
        params['machine_ids'] = machine_ids
    if entity_ids is not None:
        sql += " AND c.entities_id IN :entity_ids"
        params['entity_ids'] = entity_ids
    if excluded:
        sql += " AND c.id NOT IN :excluded_machines"
        params['excluded_machines'] = [int(m) for m in excluded]
    if hostname:
        sql += " AND c.name LIKE :hostname"
        params['hostname'] = f"%{hostname}%"
    if platform in PLATFORMS:
        sql += f" AND c.id IN (SELECT c.id FROM glpi_computers c {OS_JOINS} WHERE {PLATFORMS[platform]})"
    return sql, params


def _scope(policy, entity_ids=None, platform='', **computers):
    """_computers_where arguments for the machines in scope of a read."""
    return {'entity_ids': entity_ids, 'excluded': (policy or {}).get('excluded_machines_ids'),
            'platform': platform, **computers}


def _groups_where(login):
    """Machine groups `g` visible to login (owned or shared), all when login is None.
    type 0 only: 1 = imaging profiles, 2 = deployment convergence (deploy-/done-)."""
    sql = "g.type = 0 AND g.name NOT LIKE 'PULSE_INTERNAL%'"
    if login is None:
        return sql, {}
    return sql + """ AND (g.FK_users IN (SELECT id FROM dyngroup.Users WHERE login = :login)
        OR g.id IN (SELECT sg.FK_groups FROM dyngroup.ShareGroup sg
                    JOIN dyngroup.Users u ON u.id = sg.FK_users WHERE u.login = :login))""", {'login': login}


def _uuid_to_id(uuid):
    try:
        return int(uuid[4:]) if uuid and uuid.startswith('UUID') else None
    except ValueError:
        return None


def _min_severities(min_severity):
    """Severities >= min_severity, None when there is no filter."""
    if min_severity in SEVERITIES[1:]:
        return SEVERITIES[SEVERITIES.index(min_severity):]
    return None


def _cvss(value):
    return str(round(float(value or 0), 1))


def _date(value):
    return value.isoformat() if value else None


def _fix(values):
    """Fix status of a CVE over its links: False (one has no fix) > None (unknown) > True."""
    if 0 in values:
        return False
    return None if None in values else True


def _priority(row, cvss='max_cvss'):
    """Sort key of counter rows: exploited, then CVSS, critical, high, total (all DESC)."""
    return (row['exploited'], float(row[cvss]), row['critical'], row['high'], row['total_cves'])


def _stats(cve_pks, info):
    """Counters of a set of cves.id; info: cves.id -> (severity, cvss, exploited)."""
    severities = Counter(info[pk][0] for pk in cve_pks)
    return {
        'total_cves': len(cve_pks),
        'critical': severities['Critical'],
        'high': severities['High'],
        'medium': severities['Medium'],
        'low': severities['Low'],
        'exploited': sum(1 for pk in cve_pks if info[pk][2]),
        'max_cvss': _cvss(max((info[pk][1] for pk in cve_pks), default=0.0))
    }


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
    # CVE <-> GLPI matching on (GLPI name, version)
    # =========================================================================
    def _cve_rows(self, session, policy=None, severity=None, exploited_only=False, where='', **params):
        """software_cves joined to cves, filtered by the display policies.

        severity: exact severity, replaces policy min_severity.
        """
        policy = policy or {}
        sql = """
            SELECT c.id, c.cve_id, c.severity, c.cvss_score, c.exploited_since, sc.fix_available,
                   sc.software_name, sc.software_version, sc.glpi_software_name, sc.source_package
            FROM software_cves sc
            JOIN cves c ON c.id = sc.cve_id
            WHERE 1=1"""
        severities = [severity] if severity in SEVERITIES else _min_severities(policy.get('min_severity'))
        if severities:
            sql += " AND c.severity IN :severities"
            params['severities'] = severities
        if policy.get('excluded_names'):
            sql += " AND sc.software_name NOT IN :excluded_names"
            params['excluded_names'] = policy['excluded_names']
        if policy.get('excluded_cve_ids'):
            sql += " AND c.cve_id NOT IN :excluded_cve_ids"
            params['excluded_cve_ids'] = policy['excluded_cve_ids']
        if not policy.get('show_unfixed'):
            sql += " AND (sc.fix_available IS NULL OR sc.fix_available = 1)"
        if int(policy.get('max_age_days') or 0) > 0:
            sql += " AND c.published_at >= CURDATE() - INTERVAL :max_age_days DAY"
            params['max_age_days'] = int(policy['max_age_days'])
        if int(policy.get('min_published_year') or 0) > 0:
            sql += " AND c.published_at >= :min_published"
            params['min_published'] = f"{int(policy['min_published_year'])}-01-01"
        if exploited_only:
            sql += " AND c.exploited_since IS NOT NULL"
        return _run(session, f"{sql} {where}", **params).fetchall()

    @staticmethod
    def _index(rows):
        """(GLPI name, version) -> set(cves.id), and cves.id -> (severity, cvss, exploited)."""
        by_key, info = {}, {}
        for r in rows:
            by_key.setdefault((r.glpi_software_name, r.software_version), set()).add(r.id)
            info[r.id] = (r.severity, float(r.cvss_score or 0), r.exploited_since is not None)
        return by_key, info

    @staticmethod
    def _names(by_key):
        return sorted({name for name, _ in by_key})

    @staticmethod
    def _installs(names=None, **computers):
        """(GLPI name, version) -> set(machine id) of software and Windows builds on active computers.

        names restricts the remote GLPI query to software having CVEs (None = all).
        """
        if any(v is not None and not v for v in (names, computers.get('machine_ids'), computers.get('entity_ids'))):
            return {}
        where, params = _computers_where(**computers)
        if names is not None:
            params['names'] = names
        only = " AND {} IN :names" if names is not None else ""
        sql = f"""
            SELECT s.name, sv.name, c.id
            FROM glpi_items_softwareversions isv
            JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
            JOIN glpi_softwares s ON s.id = sv.softwares_id
            JOIN glpi_computers c ON c.id = isv.items_id
            WHERE isv.itemtype = 'Computer' AND isv.is_deleted = 0 AND {where}{only.format('s.name')}
            UNION
            SELECT os.name, {OS_BUILD}, c.id
            FROM glpi_computers c {OS_JOINS}
            WHERE {OS_BUILD} IS NOT NULL AND {where}{only.format('os.name')}"""
        installs = {}
        for name, version, machine_id in _glpi(sql, **params):
            installs.setdefault((name, version or ''), set()).add(machine_id)
        return installs

    @staticmethod
    def _keys_by_machine(installs):
        keys = {}
        for key, machine_ids in installs.items():
            for machine_id in machine_ids:
                keys.setdefault(machine_id, set()).add(key)
        return keys

    @staticmethod
    def _cves_of(keys, by_key):
        return set().union(*(by_key.get(key, ()) for key in keys))

    @staticmethod
    def _categorize(data, category_filter=''):
        """Flag software rows as browser extension / Windows OS, then keep the requested category."""
        names = sorted({r['software_name'] for r in data})
        extensions = _glpi_names("SELECT name FROM glpi_softwares WHERE comment LIKE :ext AND name IN :names",
                                 names, ext='%Extension Navigateur%')
        systems = _glpi_names("SELECT name FROM glpi_operatingsystems WHERE name LIKE :win AND name IN :names",
                              names, win='%windows%')
        for r in data:
            r['is_extension'] = r['software_name'] in extensions
            r['is_os'] = r['software_name'] in systems
        if category_filter == 'extension':
            return [r for r in data if r['is_extension']]
        if category_filter == 'software':
            return [r for r in data if not r['is_extension']]
        return data

    def _cve_details(self, session, pks):
        if not pks:
            return {}
        rows = _run(session, """
            SELECT id, cve_id, description, published_at, last_modified, exploited_since, euvd_id
            FROM cves WHERE id IN :pks""", pks=pks)
        return {r.id: r for r in rows}

    def _cve_list(self, session, rows, start, limit):
        """One entry per CVE of rows, highest CVSS first."""
        cves = {}
        for r in rows:
            cve = cves.setdefault(r.id, {'severity': r.severity, 'cvss': float(r.cvss_score or 0),
                                         'exploited': r.exploited_since is not None,
                                         'names': set(), 'versions': set(), 'fixes': set()})
            cve['names'].add(r.software_name)
            cve['versions'].add(r.software_version)
            cve['fixes'].add(r.fix_available)
        ordered = sorted(cves, key=lambda pk: (cves[pk]['exploited'], cves[pk]['cvss'], pk), reverse=True)
        page = ordered[start:start + limit]
        details = self._cve_details(session, page)
        data = [{
            'id': pk,
            'cve_id': details[pk].cve_id,
            'cvss_score': _cvss(cves[pk]['cvss']),
            'severity': cves[pk]['severity'],
            'description': details[pk].description,
            'published_at': _date(details[pk].published_at),
            'last_modified': _date(details[pk].last_modified),
            'exploited_since': _date(details[pk].exploited_since),
            'euvd_id': details[pk].euvd_id,
            'fix_available': _fix(cves[pk]['fixes']),
            'software_name': ', '.join(sorted(cves[pk]['names'])),
            'software_version': ', '.join(sorted(cves[pk]['versions']))
        } for pk in page]
        return {'total': len(ordered), 'data': data}

    @staticmethod
    def machine_name(id_glpi, entity_ids=None):
        """Hostname of an active computer within entity_ids, None otherwise."""
        if entity_ids is not None and not entity_ids:
            return None
        where, params = _computers_where(entity_ids=entity_ids, machine_ids=[id_glpi])
        rows = _glpi(f"SELECT c.name FROM glpi_computers c WHERE {where}", **params)
        return (rows[0][0] or f"ID:{id_glpi}") if rows else None

    # =========================================================================
    # Dashboard / Summary
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_dashboard_summary(self, session, entity_ids=None, policy=None, platform='', exploited_only=False):
        """Dashboard counters filtered by entity and display policies."""
        stats = _stats(set(), {})
        machines = set()
        try:
            by_key, info = self._index(self._cve_rows(session, policy, exploited_only=exploited_only))
            installs = self._installs(self._names(by_key), **_scope(policy, entity_ids, platform))
            cves = set()
            for key, machine_ids in installs.items():
                if key in by_key:
                    cves |= by_key[key]
                    machines |= machine_ids
            stats = _stats(cves, info)
        except Exception as e:
            logger.error(f"Error in get_dashboard_summary: {e}")

        last_scan = session.query(Scan).order_by(desc(Scan.started_at)).first()
        last_scan_info = None
        if last_scan:
            last_scan_info = {
                'id': last_scan.id,
                'started_at': _date(last_scan.started_at),
                'finished_at': _date(last_scan.finished_at),
                'status': last_scan.status,
                'softwares_sent': last_scan.softwares_sent,
                'cves_received': last_scan.cves_received
            }

        stats.pop('max_cvss')
        return {**stats, 'machines_affected': len(machines), 'last_scan': last_scan_info}

    # =========================================================================
    # CVE List (toutes les CVEs connues pour les logiciels du parc)
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_cves(self, session, start=0, limit=50, filter_str='', severity=None, entity_ids=None,
                 policy=None, platform='', exploited_only=False):
        """Paginated CVEs present in the park, with their affected machine count."""
        try:
            where, params = '', {}
            if filter_str:
                where = "AND (c.cve_id LIKE :search OR c.description LIKE :search)"
                params['search'] = f"%{filter_str}%"
            rows = self._cve_rows(session, policy, severity, exploited_only, where, **params)
            by_key, info = self._index(rows)
            installs = self._installs(self._names(by_key), **_scope(policy, entity_ids, platform))

            machines, softwares = {}, {}
            for r in rows:
                machine_ids = installs.get((r.glpi_software_name, r.software_version))
                if machine_ids:
                    machines.setdefault(r.id, set()).update(machine_ids)
                    softwares.setdefault(r.id, set()).add((r.software_name, r.software_version))

            ordered = sorted(machines, key=lambda pk: (info[pk][2], info[pk][1], pk), reverse=True)
            page = ordered[start:start + limit]
            details = self._cve_details(session, page)
            data = [{
                'id': pk,
                'cve_id': details[pk].cve_id,
                'cvss_score': _cvss(info[pk][1]),
                'severity': info[pk][0],
                'description': details[pk].description,
                'published_at': _date(details[pk].published_at),
                'exploited_since': _date(details[pk].exploited_since),
                'euvd_id': details[pk].euvd_id,
                'softwares': [{'name': n, 'version': v} for n, v in sorted(softwares[pk])],
                'machines_affected': len(machines[pk])
            } for pk in page]
            return {'total': len(ordered), 'data': data}
        except Exception as e:
            logger.error(f"Error getting CVEs: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_cve_details(self, session, cve_id_str, entity_ids=None, policy=None):
        """A CVE with its software links and the affected machines within entity_ids."""
        cve = session.query(Cve).filter(Cve.cve_id == cve_id_str).first()
        if not cve:
            return None

        links = session.query(SoftwareCve).filter(SoftwareCve.cve_id == cve.id).all()
        if not (policy or {}).get('show_unfixed'):
            links = [sc for sc in links if sc.fix_available is not False]
        softwares = [{'name': sc.software_name, 'version': sc.software_version,
                      'fix_available': sc.fix_available} for sc in links]

        machines = []
        by_key = {(sc.glpi_software_name, sc.software_version): sc.software_name or sc.glpi_software_name
                  for sc in links if sc.glpi_software_name}
        try:
            installs = self._installs(self._names(by_key), **_scope(policy, entity_ids))
            found = [(machine_id, key) for key, ids in installs.items() if key in by_key for machine_id in ids]
            if found:
                hosts = dict(_glpi("SELECT c.id, c.name FROM glpi_computers c WHERE c.id IN :ids",
                                   ids={machine_id for machine_id, _ in found}))
                machines = sorted(({'id_glpi': machine_id, 'hostname': hosts.get(machine_id),
                                    'software_name': by_key[key], 'software_version': key[1]}
                                   for machine_id, key in found),
                                  key=lambda m: (m['hostname'] or '', m['software_name'], m['software_version']))
        except Exception as e:
            logger.error(f"Error getting machines for CVE {cve_id_str}: {e}")

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
            'cvss_score': _cvss(cve.cvss_score),
            'severity': cve.severity,
            'description': cve.description,
            'published_at': _date(cve.published_at),
            'last_modified': _date(cve.last_modified),
            'exploited_since': _date(cve.exploited_since),
            'euvd_id': cve.euvd_id,
            'fetched_at': _date(cve.fetched_at),
            'sources': cve.sources.split(',') if cve.sources else [],
            'source_urls': source_urls,
            'softwares': softwares,
            'machines': machines
        }

    # =========================================================================
    # Machine-centric view
    # =========================================================================
    def _machine_rows(self, session, machines, policy, exploited_only=False, **computers):
        """CVE counters of machines [(id, hostname)], installs taken on computers."""
        by_key, info = self._index(self._cve_rows(session, policy, exploited_only=exploited_only))
        keys = self._keys_by_machine(self._installs(self._names(by_key), **computers))
        data = []
        for machine_id, hostname in machines:
            stats = _stats(self._cves_of(keys.get(machine_id, ()), by_key), info)
            stats['risk_score'] = stats.pop('max_cvss')
            data.append({'id_glpi': machine_id, 'hostname': hostname, **stats})
        return data

    @DatabaseHelper._sessionm
    def get_machines_summary(self, session, start=0, limit=50, filter_str='', entity_ids=None,
                             policy=None, platform='', exploited_only=False, group_id=None, login=None):
        """GLPI machines (of group_id if set) with their CVE counters, filtered by entity and display policies."""
        try:
            machine_ids = None if group_id is None else self._group_members(session, group_id, login)
            if (entity_ids is not None and not entity_ids) or machine_ids == set():
                return {'total': 0, 'data': []}
            computers = _scope(policy, entity_ids, platform, hostname=filter_str, machine_ids=machine_ids)
            where, params = _computers_where(**computers)
            machines = _glpi(f"SELECT c.id, c.name FROM glpi_computers c WHERE {where}", **params)
            if not machines:
                return {'total': 0, 'data': []}
            data = self._machine_rows(session, machines, policy, exploited_only, **computers)
            data.sort(key=lambda x: _priority(x, 'risk_score'), reverse=True)
            return {'total': len(data), 'data': data[start:start + limit]}
        except Exception as e:
            logger.error(f"Error getting machines summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_machine_cves(self, session, id_glpi, start=0, limit=50, filter_str='', severity=None,
                         entity_ids=None, policy=None):
        """CVEs of the software (name and version) installed on a machine."""
        try:
            keys = set(self._installs(machine_ids=[id_glpi], entity_ids=entity_ids))
            if not keys:
                return {'total': 0, 'data': []}
            where, params = '', {}
            if filter_str:
                where = "AND (c.cve_id LIKE :search OR c.description LIKE :search)"
                params['search'] = f"%{filter_str}%"
            rows = [r for r in self._cve_rows(session, policy, severity, False, where, **params)
                    if (r.glpi_software_name, r.software_version) in keys]
            return self._cve_list(session, rows, start, limit)
        except Exception as e:
            logger.error(f"Error getting CVEs for machine {id_glpi}: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_machine_softwares_summary(self, session, id_glpi, start=0, limit=50, filter_str='',
                                      category_filter='', entity_ids=None, policy=None):
        """Vulnerable software of a machine, Linux binaries grouped by source package."""
        try:
            keys = set(self._installs(machine_ids=[id_glpi], entity_ids=entity_ids))
            if not keys:
                return {'total': 0, 'data': []}
            where, params = '', {}
            if filter_str:
                where = "AND sc.software_name LIKE :search"
                params['search'] = f"%{filter_str}%"
            rows = self._cve_rows(session, policy, None, False, where, **params)
            _, info = self._index(rows)

            groups, linux = {}, set()
            for r in rows:
                if (r.glpi_software_name, r.software_version) in keys:
                    key = (r.source_package or r.glpi_software_name, r.software_version)
                    groups.setdefault(key, set()).add(r.id)
                    if r.source_package:
                        linux.add(key)
            data = self._categorize([{'software_name': name, 'software_version': version,
                                      'linux': (name, version) in linux, **_stats(cves, info)}
                                     for (name, version), cves in groups.items()], category_filter)
            data.sort(key=_priority, reverse=True)
            page = data[start:start + limit]
            self._enrich_with_store_info(session, page)
            return {'total': len(data), 'data': page}
        except Exception as e:
            logger.error(f"Error getting software summary for machine {id_glpi}: {e}")
            return {'total': 0, 'data': []}

    # =========================================================================
    # Software-centric view
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_softwares_summary(self, session, start=0, limit=50, filter_str='', entity_ids=None,
                              category_filter='', policy=None, platform='', exploited_only=False):
        """Vulnerable software of the park, Linux binaries grouped by source package."""
        try:
            where, params = '', {}
            if filter_str:
                where = "AND (sc.software_name LIKE :search OR sc.software_version LIKE :search)"
                params['search'] = f"%{filter_str}%"
            rows = self._cve_rows(session, policy, None, exploited_only, where, **params)
            by_key, info = self._index(rows)
            installs = self._installs(self._names(by_key), **_scope(policy, entity_ids, platform))

            groups, linux = {}, set()  # (display name, version) -> (cves, machines) ; paquets Linux
            for r in rows:
                machine_ids = installs.get((r.glpi_software_name, r.software_version))
                if machine_ids:
                    key = (r.source_package or r.glpi_software_name, r.software_version)
                    cves, machines = groups.setdefault(key, (set(), set()))
                    cves.add(r.id)
                    machines |= machine_ids
                    if r.source_package:
                        linux.add(key)

            data = self._categorize([{
                'software_name': name,
                'software_version': version,
                **_stats(cves, info),
                'machines_affected': len(machines),
                'linux': (name, version) in linux,
                'store_version': None,
                'store_has_update': False,
                'store_package_uuid': None
            } for (name, version), (cves, machines) in groups.items()], category_filter)
            data.sort(key=_priority, reverse=True)

            page = data[start:start + limit]
            self._enrich_with_store_info(session, page)
            return {'total': len(data), 'data': page}
        except Exception as e:
            logger.error(f"Error getting softwares summary: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_software_cves(self, session, software_name, software_version, start=0, limit=50,
                          filter_str='', severity=None, policy=None):
        """CVEs of a software version; software_name is COALESCE(source_package, GLPI name)."""
        try:
            where = ("AND COALESCE(sc.source_package, sc.glpi_software_name) = :sw_name "
                     "AND sc.software_version = :sw_version")
            params = {'sw_name': software_name, 'sw_version': software_version}
            if filter_str:
                where += " AND (c.cve_id LIKE :search OR c.description LIKE :search)"
                params['search'] = f"%{filter_str}%"
            rows = self._cve_rows(session, policy, severity, False, where, **params)
            return self._cve_list(session, rows, start, limit)
        except Exception as e:
            logger.error(f"Error getting CVEs for software {software_name} {software_version}: {e}")
            return {'total': 0, 'data': []}

    # =========================================================================
    # Entity / group views
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_entities_summary(self, session, start=0, limit=50, filter_str='', entity_ids=None,
                             policy=None, platform='', exploited_only=False):
        """Entities (restricted to entity_ids) with their CVE counters."""
        try:
            if entity_ids is not None and not entity_ids:
                return {'total': 0, 'data': []}
            where, params = "1=1", {'start': start, 'limit': limit}
            if filter_str:
                where += " AND e.name LIKE :search"
                params['search'] = f"%{filter_str}%"
            if entity_ids is not None:
                where += " AND e.id IN :entity_ids"
                params['entity_ids'] = entity_ids

            total = _glpi(f"SELECT COUNT(*) FROM glpi_entities e WHERE {where}", **params)[0][0]
            rows = _glpi(f"""
                SELECT e.id, e.name, e.completename FROM glpi_entities e
                WHERE {where} ORDER BY e.name LIMIT :limit OFFSET :start""", **params)
            if not rows:
                return {'total': total, 'data': []}

            computers = _scope(policy, [r.id for r in rows], platform)
            cwhere, cparams = _computers_where(**computers)
            entity_of = dict(_glpi(f"SELECT c.id, c.entities_id FROM glpi_computers c WHERE {cwhere}", **cparams))

            by_key, info = self._index(self._cve_rows(session, policy, exploited_only=exploited_only))
            entity_keys = {}
            for machine_id, keys in self._keys_by_machine(self._installs(self._names(by_key), **computers)).items():
                entity_keys.setdefault(entity_of.get(machine_id), set()).update(keys)

            machines_count = Counter(entity_of.values())
            data = [{
                'entity_id': r.id,
                'entity_name': r.name,
                'entity_fullname': r.completename or r.name,
                'machines_count': machines_count[r.id],
                **_stats(self._cves_of(entity_keys.get(r.id, ()), by_key), info)
            } for r in rows]
            data.sort(key=lambda x: (float(x['max_cvss']), x['total_cves']), reverse=True)
            return {'total': total, 'data': data}
        except Exception as e:
            logger.error(f"Error getting entities summary: {e}")
            return {'total': 0, 'data': []}

    def _visible(self, machine_ids, entity_ids=None, policy=None, platform=''):
        """Subset of machine_ids that are active computers in scope."""
        if not machine_ids or (entity_ids is not None and not entity_ids):
            return set()
        where, params = _computers_where(**_scope(policy, entity_ids, platform, machine_ids=machine_ids))
        return {r[0] for r in _glpi(f"SELECT c.id FROM glpi_computers c WHERE {where}", **params)}

    @DatabaseHelper._sessionm
    def get_groups_summary(self, session, start=0, limit=50, filter_str='', login=None, entity_ids=None,
                           policy=None, platform='', exploited_only=False):
        """Groups visible to login (None = all) with their CVE counters on the machines in scope."""
        try:
            where, params = _groups_where(login)
            params.update(start=start, limit=limit)
            if filter_str:
                where += " AND g.name LIKE :search"
                params['search'] = f"%{filter_str}%"
            excluded_groups = (policy or {}).get('excluded_groups_ids')
            if excluded_groups:
                where += " AND g.id NOT IN :excluded_groups"
                params['excluded_groups'] = [int(g) for g in excluded_groups]

            total = _run(session, f"SELECT COUNT(*) FROM dyngroup.Groups g WHERE {where}", **params).scalar() or 0
            rows = _run(session, f"""
                SELECT g.id, g.name, COALESCE(LENGTH(g.query), 0) > 0 AS is_dynamic
                FROM dyngroup.Groups g
                WHERE {where} ORDER BY g.name LIMIT :limit OFFSET :start""", **params).fetchall()
            if not rows:
                return {'total': total, 'data': []}

            group_machines = {r.id: set() for r in rows}
            for group_id, uuid in _run(session, """
                    SELECT r.FK_groups, dm.uuid FROM dyngroup.Results r
                    JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                    WHERE r.FK_groups IN :group_ids""", group_ids=list(group_machines)):
                group_machines[group_id].add(_uuid_to_id(uuid))
            visible = self._visible(set().union(*group_machines.values()) - {None}, entity_ids, policy, platform)

            by_key, info = self._index(self._cve_rows(session, policy, exploited_only=exploited_only))
            keys = self._keys_by_machine(self._installs(self._names(by_key), machine_ids=visible))

            data = []
            for r in rows:
                machines = group_machines[r.id] & visible
                data.append({
                    'group_id': r.id,
                    'group_name': r.name,
                    'group_type': 'Dynamic' if r.is_dynamic else 'Static',
                    'machines_count': len(machines),
                    **_stats(self._cves_of(set().union(*(keys.get(m, ()) for m in machines)), by_key), info)
                })
            data.sort(key=lambda x: (float(x['max_cvss']), x['total_cves']), reverse=True)
            return {'total': total, 'data': data}
        except Exception as e:
            logger.error(f"Error getting groups summary: {e}")
            return {'total': 0, 'data': []}

    def _group_members(self, session, group_id, login=None):
        """Machine ids of a group, empty when the group is not visible to login."""
        where, params = _groups_where(login)
        uuids = _run(session, f"""
            SELECT DISTINCT dm.uuid FROM dyngroup.Results r
            JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
            JOIN dyngroup.Groups g ON g.id = r.FK_groups
            WHERE r.FK_groups = :group_id AND {where}""", group_id=group_id, **params)
        return {_uuid_to_id(uuid) for (uuid,) in uuids} - {None}

    @DatabaseHelper._sessionm
    def get_groups_list(self, session, login=None, policy=None):
        """[{id, name}] of the groups visible to login, by name."""
        where, params = _groups_where(login)
        excluded = (policy or {}).get('excluded_groups_ids')
        if excluded:
            where += " AND g.id NOT IN :excluded_groups"
            params['excluded_groups'] = [int(g) for g in excluded]
        rows = _run(session, f"SELECT g.id, g.name FROM dyngroup.Groups g WHERE {where} ORDER BY g.name", **params)
        return [{'id': r.id, 'name': r.name} for r in rows]

    @DatabaseHelper._sessionm
    def get_group_machines(self, session, group_id, start=0, limit=50, filter_str='', login=None,
                           entity_ids=None, policy=None):
        """Machines in scope of a group visible to login, with their CVE counters."""
        try:
            machine_ids = self._group_members(session, group_id, login)
            if not machine_ids or (entity_ids is not None and not entity_ids):
                return {'total': 0, 'data': []}

            where, params = _computers_where(**_scope(policy, entity_ids, machine_ids=machine_ids,
                                                      hostname=filter_str))
            total = _glpi(f"SELECT COUNT(*) FROM glpi_computers c WHERE {where}", **params)[0][0]
            machines = _glpi(f"""
                SELECT c.id, c.name FROM glpi_computers c
                WHERE {where} ORDER BY c.name LIMIT :limit OFFSET :start""",
                             start=start, limit=limit, **params)
            if not machines:
                return {'total': total, 'data': []}
            data = self._machine_rows(session, machines, policy, machine_ids=[m.id for m in machines])
            data.sort(key=lambda x: (-float(x['risk_score']), x['hostname'] or ''))
            return {'total': total, 'data': data}
        except Exception as e:
            logger.error(f"Error getting group machines: {e}")
            return {'total': 0, 'data': []}

    # =========================================================================
    # Group creation helpers
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_machines_by_severity(self, session, severity, entity_ids=None, policy=None):
        """Machines having a software version with a CVE of the given severity."""
        try:
            by_key, _ = self._index(self._cve_rows(session, policy, severity))
            installs = self._installs(self._names(by_key), **_scope(policy, entity_ids))
            machine_ids = set().union(*(ids for key, ids in installs.items() if key in by_key))
            if not machine_ids:
                return []
            rows = _glpi("SELECT c.id, c.name FROM glpi_computers c WHERE c.id IN :ids ORDER BY c.name",
                         ids=machine_ids)
            return [{'uuid': f"UUID{machine_id}", 'hostname': hostname} for machine_id, hostname in rows]
        except Exception as e:
            logger.error(f"Error getting machines by severity {severity}: {e}")
            return []

    # =========================================================================
    # CVE Management (add/update from scanner)
    # =========================================================================
    @DatabaseHelper._sessionm
    def add_cve(self, session, cve_id, cvss_score, severity, description, published_at=None, last_modified=None,
                sources=None, source_urls=None, exploited_since=None, euvd_id=None):
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
            if exploited_since:
                cve.exploited_since = exploited_since
            if euvd_id:
                cve.euvd_id = euvd_id
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
                exploited_since=exploited_since,
                euvd_id=euvd_id,
                sources=sources_str,
                source_urls=source_urls_str
            )
            session.add(cve)

        try:
            session.commit()
            return cve.id
        except IntegrityError:
            # Course entre deux appels (CVE partagée par plusieurs logiciels) : le
            # check-then-insert ci-dessus n'est pas atomique, une CVE peut avoir ete
            # inseree entre-temps -> collision uk_cve_id. On repart proprement et on
            # renvoie l'id existant au lieu de perdre la CVE et son lien.
            session.rollback()
            existing = session.query(Cve).filter(Cve.cve_id == cve_id).first()
            return existing.id if existing else None

    @DatabaseHelper._sessionm
    def link_software_cve(self, session, software_name, software_version, cve_db_id,
                          glpi_software_name, target_platform=None, source_package=None, fix_available=None):
        """Upsert the link (glpi_software_name, software_version) -> CVE."""
        session.execute(text("""
            INSERT INTO software_cves (software_name, software_version, glpi_software_name,
                                       source_package, target_platform, fix_available, cve_id, created_at)
            VALUES (:name, :version, :glpi_name, :source_package, :target_platform, :fix_available, :cve_pk, NOW())
            ON DUPLICATE KEY UPDATE
                software_name = VALUES(software_name),
                source_package = COALESCE(VALUES(source_package), source_package),
                target_platform = COALESCE(VALUES(target_platform), target_platform),
                fix_available = VALUES(fix_available)
        """), {
            'name': software_name,
            'version': software_version,
            'glpi_name': glpi_software_name,
            'source_package': source_package,
            'target_platform': target_platform,
            'fix_available': fix_available,
            'cve_pk': cve_db_id
        })
        session.commit()

    @DatabaseHelper._sessionm
    def prune_stale_cves(self, session, scanned, confirmed):
        """Remove the links no longer confirmed by a successful scan, then the orphan CVEs.

        scanned: set of (glpi_software_name, software_version) sent in this scan.
        confirmed: {(glpi_software_name, software_version): set(cve_id)} received in this scan.
        Links of other versions are never touched.
        """
        if not scanned:
            return 0
        rows = _run(session, """
            SELECT sc.id, sc.glpi_software_name, sc.software_version, sc.cve_id AS cve_pk, c.cve_id
            FROM software_cves sc
            JOIN cves c ON c.id = sc.cve_id
            WHERE sc.glpi_software_name IN :names""", names={name for name, _ in scanned})
        stale, cve_pks = [], set()
        for r in rows:
            key = (r.glpi_software_name, r.software_version)
            if key in scanned and r.cve_id not in confirmed.get(key, ()):
                stale.append(r.id)
                cve_pks.add(r.cve_pk)
        for i in range(0, len(stale), 1000):
            _run(session, "DELETE FROM software_cves WHERE id IN :ids", ids=stale[i:i + 1000])
        if cve_pks:
            _run(session, """
                DELETE FROM cves WHERE id IN :pks
                AND NOT EXISTS (SELECT 1 FROM software_cves sc WHERE sc.cve_id = cves.id)""",
                 pks=cve_pks)
        session.commit()
        return len(stale)


    # =========================================================================
    # Scans history
    # =========================================================================
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
    def complete_scan(self, session, scan_id, softwares_sent, cves_received, error_message=None):
        """Close a scan: 'failed' when error_message is set, 'completed' otherwise."""
        session.execute(
            text("""UPDATE scans SET
                    finished_at = NOW(),
                    status = :status,
                    softwares_sent = :softwares_sent,
                    cves_received = :cves_received,
                    error_message = :error_message
                    WHERE id = :scan_id"""),
            {
                'status': 'failed' if error_message else 'completed',
                'softwares_sent': softwares_sent,
                'cves_received': cves_received,
                'error_message': error_message,
                'scan_id': scan_id
            }
        )
        session.commit()
        return True


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
    def set_policies_bulk(self, session, policies, user=None):
        """Set multiple policies at once.

        Args:
            policies: dict like {'display': {'min_severity': 'Medium'}, 'exclusions': {'cve_ids': [...]}}
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

    # =========================================================================
    # Store integration methods
    # =========================================================================

    def _enrich_with_store_info(self, session, results):
        """Store update of each Windows row: the Windows build of the same track, surely newer.

        The Store has one build per OS / arch / track (win/linux/mac, x64, stable/esr/lts). Linux rows are
        distro packages, fixed by the distribution (apt), never by the Store.
        """
        if not results:
            return
        try:
            from mmc.plugins.store import get_all_software, get_client_subscriptions
            subscribed = set(get_client_subscriptions() or [])
            builds = {}
            for soft in get_all_software().get('data', []):
                if soft.get('name') and soft.get('version'):
                    builds.setdefault((soft['name'].lower(), soft.get('os')), []).append(soft)

            for software in results:
                if software.get('linux'):
                    continue
                glpi_name = software['software_name'].lower()
                # Longest Store name contained in the GLPI name ("Mozilla Firefox (x64 fr)" -> "firefox")
                names = [n for n, o in builds if o == 'win' and n in glpi_name]
                if not names:
                    continue
                build = self._store_build(builds[max(names, key=len), 'win'], glpi_name, subscribed)
                software['store_name'] = build['name']
                software['store_version'] = build['version']
                software['store_package_uuid'] = (build.get('package_uuids') or '').split(',')[0] or None
                # Déployable seulement si abonné et sûrement plus récent : des numérotations différentes
                # (Teams : installeur 1.0 / application 25290) ressembleraient à un retour en arrière
                software['store_has_update'] = (build['id'] in subscribed
                                                and self._is_version_newer(build['version'], software['software_version']) is True)
        except Exception as e:
            logger.warning(f"Could not enrich with store info: {e}")

    @staticmethod
    def _store_build(candidates, glpi_name, subscribed):
        """Build of the same track (esr, lts… in the name, else stable), subscribed and x64 first."""
        track = next((t for t in ('esr', 'lts', 'beta') if t in glpi_name), 'stable')
        return max(candidates, key=lambda b: (b.get('track') == track, b['id'] in subscribed, b.get('arch') == 'x64'))

    @staticmethod
    def _is_version_newer(store_version, installed_version):
        """True if the Store version is newer, False if not, None when the numbering differs
        (Teams: installer 1.0.2508703 / application 25290.205): no way to tell."""
        def numbers(version):
            upstream = re.sub(r'^\d+:', '', version or '').split('-')[0]  # 2:4.17.12-1 -> 4.17.12
            return [int(n) for n in re.findall(r'\d+', upstream)]
        store, installed = numbers(store_version), numbers(installed_version)
        if not store or not installed:
            return False
        if max(store[0], installed[0]) > 10 * max(min(store[0], installed[0]), 1):
            return None
        return store > installed

    @DatabaseHelper._sessionm
    def get_machines_for_vulnerable_software(self, session, software_name, software_version,
                                              entity_ids=None, start=0, limit=100, filter_str=''):
        """Get machines that have a specific vulnerable software installed.

        Args:
            software_name: Normalized software name (e.g., "Python")
            software_version: Vulnerable version (e.g., "3.11.9")
            entity_ids: Entity ids in scope (None = all)
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
        try:
            # Step 1: Résoudre les noms GLPI (binaires) pour l'identité d'affichage
            # reçue. Sur Linux, un package source (freerdp2) regroupe plusieurs
            # binaires (libfreerdp2-2, libwinpr2-2, ...) : on veut toutes les machines
            # ayant l'un d'eux. COALESCE(source_package, glpi_software_name) = identité
            # affichée ; on retourne tous les glpi_software_name (binaires) du groupe.
            glpi_names_sql = text("""
                SELECT DISTINCT COALESCE(glpi_software_name, software_name) as glpi_name
                FROM security.software_cves
                WHERE COALESCE(source_package, glpi_software_name) = :software_name
            """)
            glpi_rows = session.execute(glpi_names_sql, {'software_name': software_name}).fetchall()
            glpi_software_names = [r.glpi_name for r in glpi_rows if r.glpi_name]
            if not glpi_software_names:
                glpi_software_names = [software_name]

            # Step 2: machines having one of these names at this version (software or OS)
            installs = self._installs(glpi_software_names, entity_ids=entity_ids, hostname=filter_str)
            names = {}
            for (name, version), ids in installs.items():
                if version == software_version:
                    for machine_id in ids:
                        names[machine_id] = min(name, names.get(machine_id, name))
            if not names:
                return {'total': 0, 'data': []}
            rows = _glpi("""
                SELECT c.id, c.name, c.entities_id, e.name
                FROM glpi_computers c
                LEFT JOIN glpi_entities e ON e.id = c.entities_id
                WHERE c.id IN :ids
                ORDER BY c.name
                LIMIT :limit OFFSET :start""", ids=set(names), limit=int(limit), start=int(start))
            data = [{'id': machine_id, 'uuid': f"UUID{machine_id}", 'hostname': hostname,
                     'entity_id': entity_id, 'entity_name': entity_name or 'Root',
                     'glpi_software_name': names[machine_id], 'installed_version': software_version}
                    for machine_id, hostname, entity_id, entity_name in rows]
            return {'total': len(names), 'data': data}
        except Exception as e:
            logger.error(f"Error getting machines for vulnerable software '{software_name}': {e}")
            return {'total': 0, 'data': []}
