# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Contains classes to read MMC agent plugin configuration files.
"""

from . import mmctools

import ldap
import re
import os
import logging
import MySQLdb
from os.path import isfile
from configparser import ConfigParser, NoOptionError, NoSectionError, InterpolationError

logger = logging.getLogger()


class ConfigException(Exception):
    """
    Exception raised when there is a configuration error.
    """

    pass


class DatabaseConfigBackend:
    """
    Backend pour lire la configuration depuis une base de données MySQL.
    Les paramètres de connexion sont lus depuis les variables d'environnement.
    """

    def __init__(self, table_name):
        """
        Args:
            table_name: Nom de la table de configuration (ex: 'xmpp_conf')
        """
        self.table_name = table_name
        self._cache = {}  # Cache des valeurs lues
        self._connection = None
        
        # Configuration depuis variables d'environnement avec defaults
        self.db_config = {
            'host': os.getenv('MMC_DB_HOST', 'localhost'),
            'port': int(os.getenv('MMC_DB_PORT', '3306')),
            'user': os.getenv('MMC_DB_USER', 'mmc'),
            'password': os.getenv('MMC_DB_PASSWORD', 'pBWfpjErqtsU'),
            'database': os.getenv('MMC_DB_NAME', 'admin')
        }

    def _get_connection(self):
        """Retourne une connexion DB (lazy loading)"""
        if self._connection is None:
            try:
                logger.info(f"[DatabaseConfigBackend] Connexion à MySQL: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
                self._connection = MySQLdb.connect(
                    host=self.db_config['host'],
                    port=self.db_config['port'],
                    user=self.db_config['user'],
                    passwd=self.db_config['password'],
                    db=self.db_config['database'],
                    charset='utf8'
                )
                logger.info(f"[DatabaseConfigBackend] ✅ Connecté avec succès")
            except ImportError:
                raise ConfigException(
                    "MySQLdb not installed. Install python3-mysqldb to use database backend."
                )
            except Exception as e:
                logger.error(f"[DatabaseConfigBackend] ❌ Erreur de connexion: {e}")
                raise ConfigException(f"Cannot connect to database: {e}")
        return self._connection

    def get(self, section, option):
        """
        Récupère une valeur depuis la base de données.
        Retourne None si la clé n'existe pas.
        """
        cache_key = f"{section}.{option}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"""
                SELECT valeur, valeur_defaut FROM {self.table_name}
                WHERE section = %s AND nom = %s AND activer = 1
            """
            cursor.execute(query, (section, option))
            result = cursor.fetchone()
            
            if result:
                # Priorité à 'valeur', sinon 'valeur_defaut'
                value = result[0] if result[0] is not None else result[1]
                self._cache[cache_key] = value
                logger.debug(f"[DatabaseConfigBackend] Lue: {section}.{option} = {value}")
                return value
            logger.debug(f"[DatabaseConfigBackend] Non trouvé: {section}.{option}")
            return None
        finally:
            cursor.close()

    def has_option(self, section, option):
        """Vérifie si une option existe"""
        return self.get(section, option) is not None

    def has_section(self, section):
        """Vérifie si une section existe"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE section = %s AND activer = 1"
            cursor.execute(query, (section,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            cursor.close()

    def options(self, section):
        """Retourne la liste des options d'une section"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"SELECT nom FROM {self.table_name} WHERE section = %s AND activer = 1"
            cursor.execute(query, (section,))
            return [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()

    def reload_cache(self):
        """Vide le cache pour forcer le rechargement"""
        self._cache = {}


class MMCConfigParser(ConfigParser):
    """
    Class to read and parse a MMC agent plugin configuration file.
    """

    def __init__(self):
        ConfigParser.__init__(self)

    def get(self, section, option, **kwargs):
        try:
            value = ConfigParser.get(self, section, option, **kwargs)
        except InterpolationError as exc:
            kwargs["raw"] = True
            value = ConfigParser.get(self, section, option, **kwargs)
            if "%(baseDN)s" not in value:
                raise InterpolationError
            from mmc.plugins.base import BasePluginConfig

            config = PluginConfigFactory.new(BasePluginConfig, "base")
            value = value.replace("%(baseDN)s", config.baseDN)
        return value

    def safe_get(self, section, option, default=None):
        """
        Returns a default value if the option does not exist
        """
        try:
            return self.get(section, option)
        except (NoOptionError, NoSectionError):
            return default

    def getdn(self, section, option):
        """
        Like get, but interpret the value as a LDAP DN, and sanitize it by
        removing the extra spaces.

        If the value is not a valid DN, a ldap.LDAPError exception will be
        raised.
        """
        return ",".join(ldap.explode_dn(self.get(section, option)))

    def getpassword(self, section, option):
        """
        Like get, but interpret the value as a obfuscated password if a
        password scheme is specified.

        For example: passwd = {base64}bWFuL2RyaXZhMjAwOA==
        """
        value = self.get(section, option)
        if not (match := re.search("^{(\w+)}(.+)$", value)):
            return value
        scheme = match[1]
        obfuscated = match[2]
        return obfuscated.decode(scheme)


class PluginConfig(MMCConfigParser):
    """
    Class to hold a MMC agent plugin configuration
    """

    USERDEFAULT = "userdefault"
    HOOKS = "hooks"
    SERVICE = "service"

    def __init__(self, name, conffile=None, backend="ini", db_table=None):
        """
        Args:
            name: Nom du plugin
            conffile: Chemin du fichier de config (optionnel)
            backend: "ini" (défaut) ou "database"
            db_table: Nom de la table DB (ex: 'xmpp_conf') si backend="database"
        """
        MMCConfigParser.__init__(self)
        self.name = name
        self.userDefault = {}
        self.hooks = {}
        self.service = {}
        self.backend_type = backend
        
        if backend == "database":
            if not db_table:
                raise ConfigException(f"db_table required when using database backend for {name}")
            self.backend = DatabaseConfigBackend(db_table)
            self.conffile = None  # Pas de fichier si on lit la BDD
        else:
            # Mode INI classique
            self.backend = None
            self.conffile = mmctools.getConfigFile(name) if not conffile else conffile
            self.setDefault()
            fid = open(self.conffile, "r")
            self.readfp(fid, self.conffile)
            if isfile(f"{self.conffile}.local"):
                fid = open(f"{self.conffile}.local", "r")
                self.readfp(fid, self.conffile)
        
        self.setDefault()
        self.readConf()

    def get(self, section, option, **kwargs):
        """Override get pour router vers le bon backend"""
        if self.backend_type == "database":
            value = self.backend.get(section, option)
            if value is None:
                raise NoOptionError(option, section)
            return value
        else:
            return MMCConfigParser.get(self, section, option, **kwargs)

    def has_option(self, section, option):
        """Override has_option pour router vers le bon backend"""
        if self.backend_type == "database":
            return self.backend.has_option(section, option)
        else:
            return ConfigParser.has_option(self, section, option)

    def has_section(self, section):
        """Override has_section pour router vers le bon backend"""
        if self.backend_type == "database":
            return self.backend.has_section(section)
        else:
            return ConfigParser.has_section(self, section)

    def options(self, section):
        """Override options pour router vers le bon backend"""
        if self.backend_type == "database":
            return self.backend.options(section)
        else:
            return ConfigParser.options(self, section)

    def readConf(self):
        """Read the configuration file"""
        try:
            self.disabled = self.getboolean("main", "disable")
        except (NoSectionError, NoOptionError):
            pass
        if self.has_section(self.USERDEFAULT):
            for option in self.options(self.USERDEFAULT):
                self.userDefault[option] = self.get(self.USERDEFAULT, option)
        if self.has_section(self.HOOKS):
            for option in self.options(self.HOOKS):
                self.hooks[f"{self.name}.{option}"] = self.get(self.HOOKS, option)
        if self.has_section(self.SERVICE):
            for option in self.options(self.SERVICE):
                self.service[option] = self.get(self.SERVICE, option)

    def setDefault(self):
        """Set reasonable default"""
        self.disabled = True

    def check(self):
        """
        Check the values set in the configuration file.

        Must be implemented by the subclass.
        ConfigException is raised with a corresponding error string if a check
        fails.
        """
        pass


class PluginConfigFactory(object):
    """
    For each plugin, we need to have only ONE config instance.
    This is useful, for example so that the Admin-Configuration plugin
    can change the config at run time, and every classes using the a PluginConfig will get the new values without restarting.
    So, every PluginConfig (or a derivated) instance should be created this way
    """

    instances = {}

    @staticmethod
    def new(cls, name, *args, **kwargs):
        """
        If no instance of a class (with this name) has not already
        been created, create it and keep it in the dict.
        If one already exist, just return it.
        """
        if name not in PluginConfigFactory.instances:
            PluginConfigFactory.instances[name] = cls(name, *args, **kwargs)
        return PluginConfigFactory.instances[name]

    @staticmethod
    def get(name):
        """
        Returns the PluginConfig instance that was
        created with this name.
        If it doesn't exist, raise an error because that should never
        happen.
        """
        return PluginConfigFactory.instances.get(name)
