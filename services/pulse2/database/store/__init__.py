# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from datetime import date, datetime, timedelta
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.store.schema import Software, SoftwareDownload, SoftwareRequest, Version, Client, Subscription
import logging
import json
import os

class StoreDatabase(DatabaseHelper):
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "store"
        self.configfile = "store.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        if self.is_activated:
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
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM store.version limit 1;")
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
            raise Exception("Database store connection error")
        return ret

    def _serialize_dict(self, d):
        """Convert datetime to string for XMLRPC serialization"""
        result = {}
        for key, value in d.items():
            if isinstance(value, datetime):
                result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, date):
                result[key] = value.strftime('%Y-%m-%d')
            else:
                result[key] = value
        return result

    def _check_package_exists(self, package_uuid, packages_path="/var/lib/pulse2/packages"):
        """Check if a package directory exists locally"""
        if not package_uuid:
            return False
        package_dir = os.path.join(packages_path, package_uuid)
        return os.path.isdir(package_dir) or os.path.islink(package_dir)

    @DatabaseHelper._sessionm
    def get_all_software(self, session, active_only=True, packages_path="/var/lib/pulse2/packages", start=0, limit=0, sort="popular"):
        """Get all software with download info and local package existence check

        Args:
            active_only: Only return active software
            packages_path: Path to check for local packages
            start: Offset for pagination (0 = from beginning)
            limit: Max number of results (0 = no limit)
            sort: Sort order - 'popular', 'name', or 'recent'

        Returns:
            dict with 'total' count and 'data' list
        """
        try:
            # Ensure start and limit are integers
            start = int(start)
            limit = int(limit)

            query = session.query(Software)
            if active_only:
                query = query.filter(Software.active == 1)

            # Get total count before pagination
            total = query.count()

            # Apply sorting
            if sort == "popular":
                # Sort by subscribers count (how many Medulla clients use this software)
                query = query.order_by(
                    desc(func.coalesce(Software.subscribers_count, 0)),
                    Software.name
                )
            elif sort == "recent":
                # Sort by last_update descending
                query = query.order_by(desc(Software.last_update), Software.name)
            else:
                # Default: sort by name A-Z
                query = query.order_by(Software.name)

            # Apply pagination if limit > 0
            if limit > 0:
                query = query.offset(start).limit(limit)

            result = []
            for soft in query.all():
                download = session.query(SoftwareDownload).filter(
                    SoftwareDownload.software_id == soft.id
                ).order_by(desc(SoftwareDownload.downloaded_at)).first()

                item = self._serialize_dict(soft.toDict())
                if download:
                    item['download_version'] = download.version
                    item['download_status'] = download.status
                    item['downloaded_at'] = download.downloaded_at.strftime('%Y-%m-%d %H:%M:%S') if download.downloaded_at else None
                    item['package_uuid'] = download.package_uuid
                    item['deployed_at'] = download.deployed_at.strftime('%Y-%m-%d %H:%M:%S') if download.deployed_at else None
                    item['package_exists'] = self._check_package_exists(download.package_uuid, packages_path)
                else:
                    item['download_version'] = None
                    item['download_status'] = None
                    item['downloaded_at'] = None
                    item['package_uuid'] = None
                    item['deployed_at'] = None
                    item['package_exists'] = False
                result.append(item)
            return {'total': total, 'data': result}
        except Exception as e:
            logging.getLogger().error(f"get_all_software error: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_software_by_id(self, session, software_id):
        """Get software by ID with its downloads"""
        try:
            soft = session.query(Software).filter(
                Software.id == software_id,
                Software.active == 1
            ).first()
            
            if not soft:
                return None
            
            result = self._serialize_dict(soft.toDict())
            
            downloads = session.query(SoftwareDownload).filter(
                SoftwareDownload.software_id == software_id,
                SoftwareDownload.status == 'success'
            ).order_by(SoftwareDownload.lang).all()
            
            result['downloads'] = [self._serialize_dict(d.toDict()) for d in downloads]
            return result
        except Exception as e:
            logging.getLogger().error(f"get_software_by_id error: {e}")
            return None

    @DatabaseHelper._sessionm
    def get_filters(self, session):
        """Get distinct values for filters"""
        try:
            filters = {}
            
            os_query = session.query(distinct(Software.os)).filter(
                Software.active == 1,
                Software.os != None
            ).order_by(Software.os)
            filters['os'] = [r[0] for r in os_query.all() if r[0]]
            
            vendor_query = session.query(distinct(Software.vendor)).filter(
                Software.active == 1,
                Software.vendor != None,
                Software.vendor != ''
            ).order_by(Software.vendor)
            filters['vendor'] = [r[0] for r in vendor_query.all() if r[0]]
            
            track_query = session.query(distinct(Software.track)).filter(
                Software.active == 1,
                Software.track != None
            ).order_by(Software.track)
            filters['track'] = [r[0] for r in track_query.all() if r[0]]
            
            arch_query = session.query(distinct(Software.arch)).filter(
                Software.active == 1,
                Software.arch != None
            ).order_by(Software.arch)
            filters['arch'] = [r[0] for r in arch_query.all() if r[0]]
            
            return filters
        except Exception as e:
            logging.getLogger().error(f"get_filters error: {e}")
            return {'os': [], 'vendor': [], 'track': [], 'arch': []}

    @DatabaseHelper._sessionm
    def search_software(self, session, filters=None, packages_path="/var/lib/pulse2/packages", start=0, limit=0, sort="popular"):
        """Search software with filters and local package existence check

        Args:
            filters: dict with search, os, vendor, track, arch keys
            packages_path: Path to check for local packages
            start: Offset for pagination (0 = from beginning)
            limit: Max number of results (0 = no limit)
            sort: Sort order - 'popular', 'name', or 'recent'

        Returns:
            dict with 'total' count and 'data' list
        """
        try:
            # Ensure start and limit are integers
            start = int(start)
            limit = int(limit)

            if filters is None:
                filters = {}

            query = session.query(Software).filter(Software.active == 1)

            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                query = query.filter(or_(
                    Software.name.like(search_term),
                    Software.vendor.like(search_term),
                    Software.short_desc.like(search_term)
                ))

            if filters.get('os'):
                query = query.filter(Software.os == filters['os'])

            if filters.get('vendor'):
                query = query.filter(Software.vendor == filters['vendor'])

            if filters.get('track'):
                query = query.filter(Software.track == filters['track'])

            if filters.get('arch'):
                query = query.filter(Software.arch == filters['arch'])

            # Get total count before pagination
            total = query.count()

            # Apply sorting
            if sort == "popular":
                # Sort by subscribers count (how many Medulla clients use this software)
                query = query.order_by(
                    desc(func.coalesce(Software.subscribers_count, 0)),
                    Software.name
                )
            elif sort == "recent":
                # Sort by last_update descending
                query = query.order_by(desc(Software.last_update), Software.name)
            else:
                # Default: sort by name A-Z
                query = query.order_by(Software.name)

            # Apply pagination if limit > 0
            if limit > 0:
                query = query.offset(start).limit(limit)

            result = []
            for soft in query.all():
                download = session.query(SoftwareDownload).filter(
                    SoftwareDownload.software_id == soft.id
                ).order_by(desc(SoftwareDownload.downloaded_at)).first()

                item = self._serialize_dict(soft.toDict())
                if download:
                    item['download_version'] = download.version
                    item['download_status'] = download.status
                    item['downloaded_at'] = download.downloaded_at.strftime('%Y-%m-%d %H:%M:%S') if download.downloaded_at else None
                    item['package_uuid'] = download.package_uuid
                    item['deployed_at'] = download.deployed_at.strftime('%Y-%m-%d %H:%M:%S') if download.deployed_at else None
                    item['package_exists'] = self._check_package_exists(download.package_uuid, packages_path)
                else:
                    item['download_version'] = None
                    item['download_status'] = None
                    item['downloaded_at'] = None
                    item['package_uuid'] = None
                    item['deployed_at'] = None
                    item['package_exists'] = False
                result.append(item)
            return {'total': total, 'data': result}
        except Exception as e:
            logging.getLogger().error(f"search_software error: {e}")
            return {'total': 0, 'data': []}

    @DatabaseHelper._sessionm
    def get_pending_requests(self, session):
        """Get pending software requests"""
        try:
            requests = session.query(SoftwareRequest).filter(
                SoftwareRequest.status == 'pending'
            ).order_by(desc(SoftwareRequest.created_at)).all()
            return [self._serialize_dict(r.toDict()) for r in requests]
        except Exception as e:
            logging.getLogger().error(f"get_pending_requests error: {e}")
            return []

    @DatabaseHelper._sessionm
    def get_store_stats(self, session):
        """Get store statistics"""
        try:
            stats = {}
            stats['total_software'] = session.query(func.count(Software.id)).scalar()
            stats['active_software'] = session.query(func.count(Software.id)).filter(
                Software.active == 1
            ).scalar()
            stats['total_downloads'] = session.query(func.count(SoftwareDownload.id)).filter(
                SoftwareDownload.status == 'success'
            ).scalar()
            stats['pending_requests'] = session.query(func.count(SoftwareRequest.id)).filter(
                SoftwareRequest.status == 'pending'
            ).scalar()
            return stats
        except Exception as e:
            logging.getLogger().error(f"get_store_stats error: {e}")
            return {'total_software': 0, 'active_software': 0, 'total_downloads': 0, 'pending_requests': 0}

    # ============================================
    # Subscription methods
    # ============================================

    @DatabaseHelper._sessionm
    def get_client_by_uuid(self, session, uuid):
        """Get client by UUID"""
        try:
            client = session.query(Client).filter(
                Client.uuid == uuid,
                Client.active == 1
            ).first()
            if client:
                return self._serialize_dict(client.toDict())
            return None
        except Exception as e:
            logging.getLogger().error(f"get_client_by_uuid error: {e}")
            return None

    @DatabaseHelper._sessionm
    def get_client_subscriptions(self, session, client_uuid):
        """Get software IDs a client is subscribed to"""
        try:
            client = session.query(Client).filter(
                Client.uuid == client_uuid,
                Client.active == 1
            ).first()
            if not client:
                return []

            subscriptions = session.query(Subscription.software_id).filter(
                Subscription.client_id == client.id
            ).all()
            return [s[0] for s in subscriptions]
        except Exception as e:
            logging.getLogger().error(f"get_client_subscriptions error: {e}")
            return []

    @DatabaseHelper._sessionm
    def save_subscriptions(self, session, client_uuid, software_ids):
        """Save client subscriptions (replaces existing ones)"""
        try:
            client = session.query(Client).filter(
                Client.uuid == client_uuid,
                Client.active == 1
            ).first()
            if not client:
                return {'success': False, 'error': 'Client not found'}

            # Delete existing subscriptions
            session.query(Subscription).filter(
                Subscription.client_id == client.id
            ).delete()

            # Add new subscriptions
            for software_id in software_ids:
                # Check that software exists and is active
                software = session.query(Software).filter(
                    Software.id == software_id,
                    Software.active == 1
                ).first()
                if software:
                    subscription = Subscription(
                        client_id=client.id,
                        software_id=software_id
                    )
                    session.add(subscription)

            session.commit()

            # Update subscribers_count for all software
            self._update_all_subscribers_count(session)

            return {'success': True, 'count': len(software_ids)}
        except Exception as e:
            logging.getLogger().error(f"save_subscriptions error: {e}")
            session.rollback()
            return {'success': False, 'error': str(e)}

    def _update_all_subscribers_count(self, session):
        """Update subscribers_count for all software based on current subscriptions"""
        try:
            # Get count per software
            from sqlalchemy import text
            session.execute(text("""
                UPDATE software s
                SET subscribers_count = (
                    SELECT COUNT(*)
                    FROM subscriptions sub
                    WHERE sub.software_id = s.id
                ),
                popularity_updated_at = NOW()
            """))
            session.commit()
        except Exception as e:
            logging.getLogger().error(f"_update_all_subscribers_count error: {e}")

    @DatabaseHelper._sessionm
    def get_subscribers_for_software(self, session, software_id):
        """Get clients subscribed to a software (for Kestra)"""
        try:
            subscribers = session.query(Client).join(Subscription).filter(
                Subscription.software_id == software_id,
                Client.active == 1
            ).all()
            return [self._serialize_dict(c.toDict()) for c in subscribers]
        except Exception as e:
            logging.getLogger().error(f"get_subscribers_for_software error: {e}")
            return []

    @DatabaseHelper._sessionm
    def create_software_request(self, session, software_name, os, requester_name, requester_email, message=""):
        """Create a new software request"""
        try:
            request = SoftwareRequest(
                software_name=software_name,
                os=os if os else None,
                requester_name=requester_name,
                requester_email=requester_email,
                message=message if message else None,
                status='pending'
            )
            session.add(request)
            session.commit()
            return {'success': True, 'message': 'Request submitted successfully', 'id': request.id}
        except Exception as e:
            logging.getLogger().error(f"create_software_request error: {e}")
            session.rollback()
            return {'success': False, 'error': str(e)}
