# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/pulse2/itsmlocal_sync/server.py

"""Standalone server loop for itsmlocal synchronisation."""

import argparse
import configparser
import logging
import signal
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

import pulse2.itsmlocal_sync.glpi_adapter  # noqa: F401 - registers GLPI adapter
from pulse2.itsmlocal_sync.adapters import adapter_names, get_adapter

LOGGER = logging.getLogger("itsmlocal-sync")
STOP_REQUESTED = False


def _request_stop(signum, frame):
    """Ask the foreground service loop to stop cleanly."""
    global STOP_REQUESTED
    STOP_REQUESTED = True
    LOGGER.info("Stop requested by signal %s", signum)


def parse_args(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="itsmlocal synchronisation service")
    parser.add_argument(
        "-f",
        "--config",
        default="/etc/mmc/plugins/admin.ini",
        help="admin plugin configuration file",
    )
    parser.add_argument(
        "--itsmlocal-config",
        default="/etc/mmc/plugins/itsmlocal.ini",
        help="itsmlocal plugin configuration file",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="scheduler polling interval in seconds",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="run one scheduler cycle and exit",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="maximum number of clients synchronized in parallel",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="console log level",
    )
    return parser.parse_args(argv)


def setup_logging(level):
    """Configure stdout logging for systemd/journald."""
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def read_database_config(config_file):
    """Read the admin database section without importing MMC runtime modules."""
    parser = configparser.ConfigParser()
    loaded = parser.read([config_file, f"{config_file}.local"])
    if not loaded:
        raise RuntimeError(f"unable to read configuration file: {config_file}")
    if not parser.has_section("database"):
        raise RuntimeError(f"missing [database] section in {config_file}")

    return {
        "driver": parser.get("database", "dbdriver", fallback="mysql"),
        "host": parser.get("database", "dbhost", fallback="localhost"),
        "port": parser.get("database", "dbport", fallback=""),
        "name": parser.get("database", "dbname", fallback="admin"),
        "user": parser.get("database", "dbuser", fallback="mmc"),
        "password": parser.get("database", "dbpasswd", fallback="mmc"),
        "pool_recycle": parser.getint("database", "dbpoolrecycle", fallback=60),
        "pool_size": parser.getint("database", "dbpoolsize", fallback=5),
    }


def make_database_url(config):
    """Build a SQLAlchemy URL for the admin database."""
    driver = str(config["driver"] or "mysql").lower()
    if driver in ("mysql", "mariadb"):
        host = config["host"] or "localhost"
        port = f":{config['port']}" if config.get("port") else ""
        user = quote_plus(str(config["user"] or ""))
        password = quote_plus(str(config["password"] or ""))
        database = quote_plus(str(config["name"] or "admin"))
        return f"mysql://{user}:{password}@{host}{port}/{database}?charset=utf8"
    raise RuntimeError(f"unsupported database driver for itsmlocal-sync: {driver}")


def activate_database(config_file):
    """Open a database directly from a Medulla INI database section."""
    config = read_database_config(config_file)
    return create_engine(
        make_database_url(config),
        pool_recycle=config["pool_recycle"],
        pool_size=config["pool_size"],
    )


def validate_target_database(database):
    """Check that the itsmlocal target database is reachable."""
    with database.connect() as connection:
        row = connection.execute(
            text(
                """
                SELECT DATABASE() AS database_name,
                       COUNT(*) AS table_count
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                """
            )
        ).mappings().first()
    return {
        "database_name": (row or {}).get("database_name") or "",
        "table_count": int((row or {}).get("table_count") or 0),
    }


def load_itsm_sync_clients(database):
    """Return ITSM client configurations stored in admin.saas_application."""
    with database.connect() as connection:
        rows = connection.execute(
            text(
                """
                SELECT setting_name, setting_value
                FROM saas_application
                WHERE setting_name LIKE 'itsm.%.%'
                ORDER BY setting_name
                """
            )
        ).fetchall()

    clients = defaultdict(dict)
    for setting_name, setting_value in rows:
        parts = str(setting_name or "").split(".", 2)
        if len(parts) != 3 or parts[0] != "itsm":
            continue
        clients[parts[1]][parts[2]] = setting_value

    return dict(clients)


def is_client_enabled(config):
    """Return True when a client configuration is enabled for scheduling."""
    return str(config.get("enabled", "0")).strip() == "1"


def prepare_client_adapter(client_id, config, target_database):
    """Prepare the source adapter for a client without writing any data."""
    adapter_name = config.get("itsm_type") or config.get("type") or "glpi"
    LOGGER.info(
        "Client %s scheduled: type=%s mode=%s cron=%s retry_delay=%s",
        client_id,
        adapter_name,
        config.get("conn_mode", config.get("conn.mode", "api")),
        config.get("sync.cron_expression", config.get("cron_expr", "*/10 * * * *")),
        config.get("sync.retry_delay_minutes", config.get("retry_delay_minutes", "")),
    )

    adapter_class = get_adapter(adapter_name)
    adapter = adapter_class(client_id=client_id, config=config, logger=LOGGER)
    LOGGER.debug(
        "Client %s adapter %s ready (%s)",
        client_id,
        adapter_name,
        adapter.__class__.__name__,
    )
    # The target connection is passed now so reconciliation can write to
    # itsmlocal later without changing the scheduler contract.
    if target_database is None:
        raise RuntimeError("missing itsmlocal target database")
    return client_id


def run_cycle(admin_database, target_database, max_workers=4):
    """Run one non-destructive scheduler cycle."""
    clients = load_itsm_sync_clients(admin_database)
    active_clients = {
        client_id: config
        for client_id, config in clients.items()
        if is_client_enabled(config)
    }

    LOGGER.info(
        "Loaded %d ITSM client configuration(s), %d active",
        len(clients),
        len(active_clients),
    )

    worker_count = max(1, min(int(max_workers or 1), len(active_clients) or 1))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(
                prepare_client_adapter,
                client_id,
                config,
                target_database,
            ): client_id
            for client_id, config in sorted(active_clients.items())
        }
        for future in as_completed(futures):
            client_id = futures[future]
            try:
                future.result()
            except ValueError as exc:
                LOGGER.error(
                    "Client %s ignored: %s (available: %s)",
                    client_id,
                    exc,
                    ", ".join(adapter_names()),
                )
            except Exception:
                LOGGER.exception("Client %s scheduling failed", client_id)

    return len(active_clients)


def main(argv=None):
    """Run the foreground service."""
    args = parse_args(argv or sys.argv[1:])
    setup_logging(args.log_level)

    signal.signal(signal.SIGTERM, _request_stop)
    signal.signal(signal.SIGINT, _request_stop)

    if args.interval < 1:
        raise ValueError("--interval must be greater than zero")
    if args.workers < 1:
        raise ValueError("--workers must be greater than zero")

    admin_database = activate_database(args.config)
    target_database = activate_database(args.itsmlocal_config)
    target_info = validate_target_database(target_database)
    LOGGER.info("itsmlocal-sync service started")
    LOGGER.info(
        "itsmlocal target database ready: name=%s tables=%s",
        target_info["database_name"],
        target_info["table_count"],
    )

    while not STOP_REQUESTED:
        try:
            run_cycle(admin_database, target_database, max_workers=args.workers)
        except Exception:
            LOGGER.exception("itsmlocal-sync cycle failed")
            if args.once:
                return 1

        if args.once:
            break

        deadline = time.time() + args.interval
        while not STOP_REQUESTED and time.time() < deadline:
            time.sleep(min(1, max(0, deadline - time.time())))

    LOGGER.info("itsmlocal-sync service stopped")
    return 0
