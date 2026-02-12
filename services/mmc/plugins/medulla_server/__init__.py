# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Pulse2 mmc-agent plugin
give a central access to the Managers that can be needed by pulse2 modules
"""

# SqlAlchemy
from sqlalchemy.exc import DBAPIError
import sqlalchemy.orm.query
import os
import logging
from mmc.support.config import PluginConfig

from mmc.support.mmctools import (
    xmlrpcCleanup,
    RpcProxyI,
    ContextMakerI,
    SecurityContext,
    EnhancedSecurityContext
)
from mmc.plugins.base import (with_xmpp_context,
                              with_optional_xmpp_context,)


import subprocess


from mmc.agent import PluginManager
from pulse2.managers.group import ComputerGroupManager
from pulse2.managers.location import ComputerLocationManager
from pulse2.managers.imaging import ComputerImagingManager
from pulse2.database.pulse.config import Pulse2DatabaseConfig
from pulse2.database.pulse import Pulse2Database
from pulse2.managers.pulse import Pulse2Manager
from mmc.plugins.medulla_server.medulla_server import Pulse2Pulse2Manager

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

import logging
import subprocess
import json
import re
from time import time
from twisted.internet.threads import deferToThread

logger = logging.getLogger()
deferred = deferToThread.__get__  # Create an alias for deferred functions


last_update_check_ts = None
available_updates = []

APIVERSION = "0:0:0"

NOAUTHNEEDED = [
    "canDoInventory",
]


def getApiVersion():
    return APIVERSION


def activate():
    config = Pulse2Config("medulla_server", None, "database")
    logger = logging.getLogger()
    if config.disable:
        logger.warning("Plugin medulla_server: disabled by configuration.")
        return False
    if not Pulse2Database().activate(config):
        logger.warning(
            "Plugin medulla_server: an error occurred during the database initialization"
        )
        return False

    Pulse2Manager().register("medulla_server", Pulse2Pulse2Manager)
    updateQueryClass()
    return True


def activate_2():
    config = Pulse2Config("medulla_server", None, "database")
    try:
        ComputerLocationManager().select(config.location)
    except Exception as e:
        logging.getLogger().error(e)
        return False
    return True


def updateQueryClass():
    """
    Our fix for SQLAlchemy behaviour with MySQL
    Sometimes we lost the connection to the MySQL Server, even on a local
    server.
    """
    q = sqlalchemy.orm.query.Query
    for m in ["first", "count", "all", "__iter__"]:
        setattr(q, "_old_" + m, getattr(q, m))
        setattr(q, m, create_method(m))


def create_method(m):
    def method(self, already_in_loop=False):
        NB_DB_CONN_TRY = 2
        NORESULT = "__noresult__"
        ret = NORESULT
        try:
            old_m = getattr(self, "_old_" + m)
            ret = old_m()
        except DBAPIError as e:
            reconnect = False
            if (
                e.orig.args[0] == 2013 and not already_in_loop
            ):  # Lost connection to MySQL server during query error
                logging.getLogger().warn("DBAPIError Lost connection")
                reconnect = True
            elif (
                e.orig.args[0] == 2006 and not already_in_loop
            ):  # MySQL server has gone away
                logging.getLogger().warn("DBAPIError MySQL server has gone away")
                reconnect = True
            if reconnect:
                for i in range(0, NB_DB_CONN_TRY):
                    logging.getLogger().warn(
                        "Trying to recover the connection (try #%d on %d)"
                        % (i + 1, NB_DB_CONN_TRY + 1)
                    )
                    new_m = getattr(self, m)
                    try:
                        ret = new_m(True)
                        break
                    except Exception as e:
                        # Try again
                        continue
            if ret != NORESULT:
                return ret
            raise e
        return ret

    return method


class Pulse2Config(PluginConfig, Pulse2DatabaseConfig):
    location = None

    def __init__(self, name="medulla_server", conffile=None, backend="database"):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="medulla_server_conf")
            Pulse2DatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)
        self.disable = self.getboolean("main", "disable")
        if self.backend == "database":
            PluginConfig._load_db_settings_from_backend(self)
        elif self.conffile and self.backend == "ini":
            Pulse2DatabaseConfig.setup(self, self.conffile)

        if self.has_option("main", "location"):
            self.location = self.get("main", "location")



class ContextMaker(ContextMakerI):
    """
    Fabrique de contextes personnalisés pour XMPP, héritée de ContextMakerI.
    Sert à créer et initialiser un objet de type `EnhancedSecurityContext`.

    appeler sur chaque module a l'initialiasation'

    Méthodes
    --------
    getContext() :
        Crée et retourne un contexte sécurisé enrichi contenant les informations
        de l'utilisateur et de la requête courante.
    """

    def getContext(self):
        """
        Crée un contexte de type `EnhancedSecurityContext` pour l'utilisateur courant.

        Retourne
        --------
        EnhancedSecurityContext
            Contexte initialisé avec :
              - `userid` : l'identifiant de l'utilisateur courant
              - `request` : la requête associée
              - `session` : la session courante

        Effets de bord
        --------------
        - Écrit des logs de niveau `error` lors de la création du contexte.
        """
        s = EnhancedSecurityContext()
        s.userid = self.userid
        s.request = self.request
        s.session = self.session
        return s


def simplecommand(cmd):
    obj = {}
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj["code"] = p.wait()
    obj["result"] = result
    return obj


def simplecommandstr(cmd):
    obj = {}
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj["code"] = p.wait()
    obj["result"] = "\n".join(result)
    return obj


class RpcProxy(RpcProxyI):
    # groups
    def isdyn_group(self, gid):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerGroupManager().isdyn_group(ctx, gid))

    def isrequest_group(self, gid):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerGroupManager().isrequest_group(ctx, gid))

    def requestresult_group(self, gid, min, max, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(
            ComputerGroupManager().requestresult_group(ctx, gid, min, max, filter)
        )

    def result_group(self, gid, min, max, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(
            ComputerGroupManager().result_group(ctx, gid, min, max, filter)
        )

    # Locations
    def getUserLocations(self):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerLocationManager().getUserLocations(ctx.userid))

    def getLocationParentPath(self, uuid):
        return xmlrpcCleanup(ComputerLocationManager().getLocationParentPath(uuid))

    def getLocationName(self, uuid):
        return xmlrpcCleanup(ComputerLocationManager().getLocationName(uuid))

    # Profiles
    def isImagingInProfilePossible(self):
        """
        tell if the profiles can access imaging

        @returns: True if the profiles can access imaging
        @rtype: boolean
        """
        return ComputerImagingManager().isImagingInProfilePossible()

    def areProfilesPossible(self):
        """
        profiles are possible only if the imaging plugin is enable
        """
        # maybe we can add something in the configuration of dyngroup to say if we want or not profiles
        return PluginManager().isEnabled("imaging")

    @with_optional_xmpp_context
    def getAllImagingServersForProfiles(self, associated=False, ctx=None):
        """
        get all the imaging server that this user can access
        """
        return ComputerImagingManager().getAllImagingServers(ctx.userid, associated)

    def runinshell(self, cmd):
        process = subprocess.Popen(
            [cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        out, err = process.communicate()
        return out.decode('utf-8').strip(), err.decode('utf-8').strip(), process.returncode


    def getProductUpdates(self):
        mup_path = "/usr/share/medulla-update-manager/medulla-update-manager.py"
        install_command = f"{mup_path} --list --json"

        @deferred
        def _getProductUpdates():
            stdout, stderr, code = self.runinshell(install_command)

            logger.debug(f"Sortie standard du script enfant (stdout) :\n{stdout}")
            logger.debug(f"Sortie erreur du script enfant (stderr) :\n{stderr}")

            if code == 0:
                # JSON extraction between markers
                match = re.search(r"===JSON_BEGIN===(.*?)===JSON_END===", stdout, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        return {"success": True, "data": data}
                    except json.JSONDecodeError as e:
                        logger.error(f"Erreur lors du décodage JSON : {e}")
                        return {"success": False, "error": "invalid_json"}
                else:
                    logger.warning("Bloc JSON non trouvé dans la sortie")
                    return {"success": False, "error": "no_json_found"}
            else:
                logger.error(f"Échec de la commande (code {code})")
                return {"success": False, "code": code, "stderr": stderr}

        return _getProductUpdates()

    def installProductUpdates(self):
        mup_path = "/usr/share/medulla-update-manager/medulla-update-manager.py"
        install_command = f"{mup_path} -I" # Option -i to install everything

        @deferred
        def _runInstall():
            stdout, stderr, code = self.runinshell(install_command)

            if code == 0:
                logger.info("Commande exécutée avec succès")
                return {"success": True, "output": stdout}
            else:
                logger.error(f"Échec de la commande (code {code})")
                return {"success": False, "code": code, "stderr": stderr}

        return _runInstall()


def displayLocalisationBar():
    return xmlrpcCleanup(ComputerLocationManager().displayLocalisationBar())


def getSSHPublicKey():
    try:
        return open("/root/.ssh/id_rsa.pub").read()
    except IOError:
        logging.getLogger().error("Error while reading SSH public key")
        return ""


def updateDebianSourceList():
    try:
        installation_uuid = open("/etc/pulse-licensing/installation_id").read().strip()
    except IOError:
        logging.getLogger().error("Error while reading installation_id file")
    try:
        pulse_version = getVersion().split(".")[0]
        # Pulse repository line
        repo_line = (
            "deb http://%s:a0@pulse.mandriva.org/pub/pulse2/server/debian wheezy %s.0\n"
            % (installation_uuid, pulse_version)
        )

        lines = open("/etc/apt/sources.list", "r").readlines()
        for i in range(len(lines)):
            line = lines[i]
            # If there is already a pulse line, we overwrite it (skip comment line)
            if (
                "pulse.mandriva.org/pub/pulse2/server/debian" in line
                and not "#" in line
            ):
                lines[i] = repo_line
                break
        else:
            lines.append(repo_line)

        # Writing file
        f = open("/etc/apt/sources.list", "w")
        f.writelines(lines)
        f.close()
    except IOError:
        logging.getLogger().error("Error while writing source.list file")
    except Exception as e:
        logging.getLogger().exception(str(e))


def canDoInventory():
    try:
        from mmc.plugins.medulla_server.inventory import canDoInventory

        return canDoInventory()
    except ImportError:
        return True

