# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
XML-RPC server implementation of the MMC agent.
"""

from resource import RLIMIT_NOFILE, RLIM_INFINITY, getrlimit
import signal
import multiprocessing as mp
from inspect import getfullargspec, currentframe, getframeinfo
import base64
import zlib
import string
import yaml
from collections import OrderedDict
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import xmltodict

import twisted.internet.error
import twisted.copyright
from twisted.web import xmlrpc, server
from twisted.web.xmlrpc import XMLRPC, Handler
from twisted.internet import reactor, defer
from twisted.python import failure
import json
from mmc.utils import convert

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http  # pyflakes.ignore

from mmc.site import localstatedir
from mmc.ssl import makeSSLContext
from mmc.support.mmctools import Singleton
from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory
from mmc.core.log import ColoredFormatter

# from mmc.plugins.xmppmaster.master.lib import convert

from decimal import Decimal
import importlib
import logging
import logging.config
import xmlrpc.client
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import configparser
import glob
import time
import pwd
import grp
import threading
import re
import zipfile
import traceback
import time
import sys

import random

# import posix_ipc
import socket
import ssl
import gzip

from pulse2.database.xmppmaster import XmppMasterDatabase
from datetime import datetime, timedelta

logger = logging.getLogger()

sys.path.append("plugins")

Fault = xmlrpc.client.Fault
ctx = None
VERSION = "5.4.6"

PYTHON_VERSION = sys.version_info.major

class xmppbrowsing:
    """ """

    def __init__(self, defaultdir=None, rootfilesystem=None):
        """
        :param type: Uses this parameter to give a path abs
        :type defaultdir: string
        :type rootfilesystem :string
        :return: Function init has no return
        """
        self.defaultdir = None
        self.rootfilesystem = None
        self.dirinfos = {}

        if defaultdir is not None:
            self.defaultdir = defaultdir
        if rootfilesystem is not None:
            self.rootfilesystem = rootfilesystem
        self.listfileindir()

    def listfileindir1(self, path_abs_current=None):
        if path_abs_current is None or path_abs_current == "":
            if self.defaultdir is None:
                pathabs = os.getcwd()
            else:
                pathabs = self.defaultdir
        else:
            if self.rootfilesystem in path_abs_current:
                pathabs = os.path.abspath(path_abs_current)
            else:
                pathabs = self.rootfilesystem
        # TODO: Remove MIGRATION3
        self.dirinfos = {
            "path_abs_current": pathabs,
            "list_dirs_current": (
                os.walk(pathabs).next()[1]
                if PYTHON_VERSION == 2
                else next(os.walk(pathabs))[1]
            ),
            "list_files_current": (
                os.walk(pathabs).next()[2]
                if PYTHON_VERSION == 2
                else next(os.walk(pathabs))[2]
            ),
            "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
            "rootfilesystem": self.rootfilesystem,
            "defaultdir": self.defaultdir,
        }
        return self.dirinfos

    def listfileindir(self, path_abs_current=None):
        if path_abs_current is None or path_abs_current == "":
            if self.defaultdir is None:
                pathabs = os.getcwd()
            else:
                pathabs = self.defaultdir
        else:
            if self.rootfilesystem in path_abs_current:
                pathabs = os.path.abspath(path_abs_current)
            else:
                pathabs = self.rootfilesystem
        # TODO: Remove MIGRATION3
        list_files_current = (
            os.walk(pathabs).next()[2]
            if PYTHON_VERSION == 2
            else next(os.walk(pathabs))[2]
        )
        ff = []
        for t in list_files_current:
            fii = os.path.join(pathabs, t)
            ff.append((t, os.path.getsize(fii)))
        # TODO: Remove MIGRATION3
        self.dirinfos = {
            "path_abs_current": pathabs,
            "list_dirs_current": (
                os.walk(pathabs).next()[1]
                if PYTHON_VERSION == 2
                else next(os.walk(pathabs))[1]
            ),
            "list_files_current": ff,
            "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
            "rootfilesystem": self.rootfilesystem,
            "defaultdir": self.defaultdir,
        }
        return self.dirinfos


# decorateur mesure temps d'une fonction
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Temps d'exécution de {func.__name__}: {execution_time} secondes")
        return result

    return wrapper


def log_params(func):
    def wrapper(*args, **kwargs):
        print(f"Paramètres positionnels : {args}")
        print(f"Paramètres nommés : {kwargs}")
        result = func(*args, **kwargs)
        return result

    return wrapper


def log_details(func):
    def wrapper(*args, **kwargs):
        frame = currentframe().f_back
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
        function_name = func.__name__
        print(f"Nom de la fonction : {function_name}")
        print(f"Fichier : {filename}, ligne : {line_number}")
        print(f"Paramètres positionnels : {args}")
        print(f"Paramètres nommés : {kwargs}")
        result = func(*args, **kwargs)
        return result

    return wrapper


def log_details_debug_info(func):
    def wrapper(*args, **kwargs):
        frame = currentframe().f_back
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
        function_name = func.__name__
        # Configuration du logger
        logger = logging.getLogger(function_name)
        logger.setLevel(logging.INFO)
        # Configuration du format de log
        log_format = f"{function_name} - Ligne {line_number} - %(message)s"
        formatter = logging.Formatter(log_format)
        # Configuration du handler de log vers la console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        # Log des paramètres passés à la fonction
        logger.info(f"Paramètres positionnels : {args}")
        logger.info(f"Paramètres nommés : {kwargs}")
        result = func(*args, **kwargs)
        return result

    return wrapper


def generate_log_line(message):
    frame = currentframe().f_back
    file_name = getframeinfo(frame).filename
    line_number = frame.f_lineno
    log_line = f"[{file_name}:{line_number}] - {message}"
    return log_line


def display_message(message):
    frame = currentframe().f_back
    file_name = getframeinfo(frame).filename
    line_number = frame.f_lineno
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.INFO)
    # Configuration du handler de stream (affichage console)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    log_line = generate_log_line(message)
    logger.info(log_line)


def generer_mot_de_passe(taille):
    """
    Cette fonction permet de generer 1 mot de passe aléatoire
    le parametre taille precise le nombre de caractere du mot de passe
    renvoi le mot de passe

    eg : mot_de_passe = generer_mot_de_passe(32)
    """
    caracteres = string.ascii_letters + string.digits + string.punctuation
    mot_de_passe = "".join(random.choice(caracteres) for _ in range(taille))
    return mot_de_passe


class MotDePasse:
    def __init__(
        self,
        taille,
        temps_validation=60,
        caracteres_interdits=""""()[],%:|`.{}'><\\/^""",
    ):
        self.taille = taille
        self.caracteres_interdits = [x for x in caracteres_interdits]
        self.temps_validation = temps_validation
        self.mot_de_passe = self.generer_mot_de_passe()
        self.date_expiration = self.calculer_date_expiration()

    def generer_mot_de_passe(self):
        caracteres = string.ascii_letters + string.digits + string.punctuation
        for caractere_interdit in self.caracteres_interdits:
            caracteres = caracteres.replace(caractere_interdit, "")
        mot_de_passe = "".join(random.choice(caracteres) for _ in range(self.taille))
        return mot_de_passe

    def calculer_date_expiration(self):
        return datetime.now() + timedelta(seconds=self.temps_validation)

    def verifier_validite(self):
        temps_restant = (self.date_expiration - datetime.now()).total_seconds()
        return temps_restant

    def est_valide(self):
        return datetime.now() < self.date_expiration

    # def generer_qr_code(self, nom_fichier):
    # qr = qrcode.QRCode(version=1, box_size=10, border=4)
    # qr.add_data(self.mot_de_passe)
    # qr.make(fit=True)
    # qr_img = qr.make_image(fill="black", back_color="white")
    # qr_img.save(nom_fichier)
    # print(f"QR code généré et sauvegardé dans {nom_fichier}.")


class DateTimebytesEncoderjson(json.JSONEncoder):
    """
    Used to handle datetime in json files.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        elif isinstance(obj, bytes):
            encoded_object = obj.decode("utf-8")
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object

class messagefilexmpp:
    """
    Cette class est charge de communique avec le substitut master.
    elle permet d'envoyer des messages et iq sur xmpp
    """

    # priority : 1 send message remote to
    # dataform jsonstring ({to,action,ret,base64,data,sessionid}

    # priority : 2 send message remote iq
    # dataform

    # priority 4 call plugin master
    # (dataform : json string { "action" : plugin, "ret": 0, "sessionid": sessionid, "data": data

    # priority 9 notification
    # (dataform : string )

    def name_random(self, nb, pref=""):
        a = "abcdefghijklnmopqrstuvwxyz0123456789"
        d = pref
        for t in range(nb):
            d = d + a[random.randint(0, 35)]
        return d

    def __init__(self, objmmc, config_mcc_agent, config_xmpp):
        # Lit configuration du fichier
        self.config_mcc_agent = config_mcc_agent
        self.config_xmpp = config_xmpp
        # self.config = config
        self.message_type = "json"
        self.config_bool_done = False
        self.objmmc = objmmc
        self.xmppbrowsingpath = xmppbrowsing(
            defaultdir=self.config_xmpp.defaultdir,
            rootfilesystem=self.config_xmpp.rootfilesystem,
        )

    def sendstr(self, msg, timeout=0, priority=9):
        """
        fonction de bas niveaux qui envoi 1 chaine au substitut master
        """
        # logger.error("sendstr %s" % msg)
        try:
            try:
                msg = convert.convert_bytes_datetime_to_string(msg)
            except ValueError as e:
                logger.error("messagefilexmpp send error: %s" % str(e))
                return None
            if self.config_mcc_agent.submaster_ip_format == "ipv6":
                client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Activation de l'option pour réutiliser l'adresse
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = self.config_mcc_agent.submaster_check_hostname
            context.verify_mode = ssl.CERT_NONE

            # test json
            client.connect(
                (
                    self.config_mcc_agent.submaster_host,
                    self.config_mcc_agent.submaster_port,
                )
            )
            ssock = context.wrap_socket(
                client, server_hostname=self.config_mcc_agent.submaster_host
            )
            response = None
            try:
                message = self.config_mcc_agent.submaster_allowed_token + msg
                ssock.sendall(convert.compress_data_to_bytes(message))
                response = convert.decompress_data_to_bytes(ssock.recv(2097152))
                response = convert.convert_bytes_datetime_to_string(response)
            finally:
                # Fermeture de la connexion SSL
                # Fermeture du socket principal
                ssock.close()
                if self.config_mcc_agent.submaster_allowed_token:
                    longueur = len(self.config_mcc_agent.submaster_allowed_token)
                    if longueur > 0 and len(response) > longueur:
                        return response[longueur:]
                return response
        except ConnectionRefusedError as e:
            self.config_bool_done = False
            logger.error(
                "Erreur connection verify substitut master %s:%s"
                % (
                    self.config_mcc_agent.submaster_host,
                    self.config_mcc_agent.submaster_port,
                )
            )
            logger.warning("Restart Substitut master")
        except Exception as e:
            logger.error("client mmc to submast : %s " % str(e))
            logger.error("%s" % (traceback.format_exc()))
            return None

    def send_message(self, mto, msg):
        logger.debug("---------------------------------------------------------")
        logger.debug("------------------- SEND MESSAGE-------------------------")
        logger.debug("---------------------------------------------------------")
        if not self.config_bool_done:
            if not self.objmmc.init_master_substitut():
                return None
        try:
            msg = convert.convert_json_to_dict(msg)
            logger.debug("send_message msg format json")
        except json.decoder.JSONDecodeError as e:
            # type n est pas 1 json.
            logger.debug("msg pas 1 json ")
            try:
                msg = convert.yaml_string_to_dict(msg)
                logger.debug("send_message msg format yam")
            except:
                logger.debug("msg pas 1 yam ")
                try:
                    msg = convert.xml_to_dict(msg)
                    logger.debug("send_message msg format xml")
                except:
                    logger.debug("msg pas 1 xml")
        if isinstance(msg, (dict)):
            # verification message format
            # verification keys minimuns
            if not convert.check_keys_in(msg, ["action", "data"]):
                # il manque des keys obligatoire dans le message
                return None
            if "sessionid" not in msg:
                msg["sessionid"] = self.name_random(10, pref="mmc_message")
            sessionid = msg["sessionid"]
            if "base64" not in msg:
                msg["base64"] = False
            if "ret" not in msg:
                msg["ret"] = 0
            if not isinstance(msg["data"], (list)):
                if not isinstance(msg["data"], (dict)):
                    if convert.is_base64(msg["data"]):
                        msg["base64"] = True
                    elif isinstance(msg["data"], (str)):
                        logger.warning(
                            "Message sessionid %s data est 1 simple string"
                            % msg["sessionid"]
                        )
                    else:
                        logger.error(
                            "Message data type error : type %s" % type(msg["data"])
                        )
                        return None

            # addition des metadatas de message.
            msg["metadatas"] = {"type": "msg", "to": mto, "timeout": 0}
            messagesend = json.dumps(msg, indent=4)
            self.sendstr(messagesend)
            return sessionid

        elif isinstance(msg, (str)):
            logger.error("Message does not have a valid format")
            return None
        else:
            logger.error("type msg pas compatible %s" % type(msg))
            return None

    def iqsendpulse(self, mto, msg, timeout):
        return self.send_iq(mto, msg, timeout)

    def send_iq(self, mto, msg, timeout):
        logger.debug("---------------------------------------------------------")
        logger.debug("----------------------- SEND IQ -------------------------")
        logger.debug("---------------------------------------------------------")
        if not self.config_bool_done:
            if not self.objmmc.init_master_substitut():
                return None
        try:
            msg = convert.convert_json_to_dict(msg)
            logger.debug("msg est 1 json")
        except json.decoder.JSONDecodeError as e:
            # type n est pas 1 json.
            logger.debug("msg pas 1 json ")
            try:
                msg = convert.yaml_string_to_dict(msg)
                logger.debug("msg est 1 yam")
            except:
                logger.debug("msg pas 1 yam ")
                try:
                    msg = convert.xml_to_dict(msg)
                    logger.debug("msg est 1 xml")
                except:
                    logger.debug("msg pas 1 xml")

        if isinstance(msg, (dict)):
            # verification message format
            # verification keys minimuns
            if not convert.check_keys_in(msg, ["action", "data"]):
                # il manque des keys obligatoire dans le message
                return None
            if "sessionid" not in msg:
                msg["sessionid"] = self.name_random(10, pref="mmc_message")
            sessionid = msg["sessionid"]
            if "base64" not in msg:
                msg["base64"] = False
            if "ret" not in msg:
                msg["ret"] = 0

            if not isinstance(msg["data"], (list)):
                if not isinstance(msg["data"], (dict)):
                    if convert.is_base64(msg["data"]):
                        msg["base64"] = True
                    elif isinstance(msg["data"], (str)):
                        logger.warning(
                            "Message sessionid %s data est 1 simple string"
                            % msg["sessionid"]
                        )
                    else:
                        logger.error(
                            "Message data type error : type %s" % type(msg["data"])
                        )
                        return None
            # addition des metadatas de message.
            msg["metadatas"] = {"type": "iq", "to": mto, "timeout": timeout}
            messagesend = json.dumps(msg, indent=4)
            return self.sendstr(messagesend, timeout)
            # return sessionid

        elif isinstance(msg, (str)):
            logger.error("Message does not have a valid format")
            return None
        else:
            logger.error("type msg pas compatible %s" % type(msg))
            return None

    def send_call_plugin(self, msg):
        logger.debug("---------------------------------------------------------")
        logger.debug("--------------------- CALL PLUGINS ----------------------")
        logger.debug("---------------------------------------------------------")
        if not isinstance(msg, (dict)):
            try:
                msg = convert.convert_json_to_dict(msg)
                logger.debug("msg est 1 json")
            except json.decoder.JSONDecodeError as e:
                # type n est pas 1 json.
                logger.debug("msg pas 1 json ")
                try:
                    msg = convert.yaml_string_to_dict(msg)
                    logger.debug("msg est 1 yam")
                except:
                    logger.debug("msg pas 1 yam ")
                    try:
                        msg = convert.xml_to_dict(msg)
                        logger.debug("msg est 1 xml")
                    except:
                        logger.debug("msg pas 1 xml")

        if isinstance(msg, (dict)):
            # verification message format
            # verification keys minimuns
            if not convert.check_keys_in(msg, ["action", "data"]):
                # il manque des keys obligatoire dans le message
                return None, None

            if "sessionid" not in msg:
                msg["sessionid"] = self.name_random(10, pref="mmc_message")
            sessionid = msg["sessionid"]
            if "base64" not in msg:
                msg["base64"] = False
            if "ret" not in msg:
                msg["ret"] = 0
            if not isinstance(msg["data"], (list)):
                if not isinstance(msg["data"], (dict)):
                    if convert.is_base64(msg["data"]):
                        msg["base64"] = True
                    elif isinstance(msg["data"], (str)):
                        logger.warning(
                            "Message sessionid %s data est 1 simple string"
                            % msg["sessionid"]
                        )
                    else:
                        logger.error(
                            "Message data type error : type %s" % type(msg["data"])
                        )
                        return None, None
            # addition des metadatas de message.
            msg["metadatas"] = {
                "type": "plugin",
                "to": "master@pulse/MASTER",
                "timeout": 0,
            }
            messagesend = json.dumps(msg, indent=4)
            res = self.sendstr(messagesend)
            if res != None:
                logger.debug("Plugin call executed %s on master " % msg["action"])
                return sessionid, res
            return None, "Error connection"

        elif isinstance(msg, (str)):
            logger.error("Message does not have a valid format")
            return None, None
        else:
            logger.error("type msg pas compatible %s" % type(msg))
            return None, None

    def callpluginmasterfrommmc(self, plugin, data, sessionid=None):
        if sessionid is None:
            sessionid = self.name_random(5, plugin)
        msg = {"action": plugin, "ret": 0, "sessionid": sessionid, "data": data}
        self.send_call_plugin(msg)

    def _call_remote_action(self, to, nameaction, sessionname):
        msg = {
            "action": nameaction,
            "sessionid": self.name_random(5, sessionname),
            "data": [],
            "ret": 255,
            "base64": False,
        }
        self.send_message(to, msg)

    def send_message_json(self, to, jsonstring):
        return self.send_message(to, jsonstring)
        # jsonstring["to"] = to
        # return self.sendstr(json.dumps(jsonstring), priority=1)

    def callrestartbymaster(self, to):
        return self._call_remote_action(to, "restarfrommaster", "restart")

    def callInstallKey(self, jidAM, jidARS):
        """
        Envoie une requête pour installer une clé SSH d'un ars sur 1 machine
        cette fonction est 1 client qui envoi le message XMPP en utilisant le serveur substitut master.
        substitut master fait la requette xmpp

        Cette méthode crée un message de requête pour l'installation d'une clé SSH,
        ARS qui recoit se message install sa clef sur la machine jidAM.

        Args:
            jidAM (str): L'adresse JID de l'agent de messagerie (jidAM) pour lequel
                        la clé SSH doit être installée.
            jidARS (str): L'adresse JID du destinataire (jidARS) du message XMPP
                        demandant l'installation de la clé SSH.

        Raises:
            Exception: Si l'envoi du message échoue pour une raison quelconque.

        """
        msg = {
            "action": "installkey",
            "sessionid": self.name_random(5, "installkey"),
            "data": {"jidAM": jidAM},
            "ret": 0,
            "base64": False,
        }
        self.send_message(jidARS, msg)

    def callinventory(self, to):
        return self._call_remote_action(to, "inventory", "inventory")

    def callrestartbotbymaster(self, to):
        return self._call_remote_action(to, "restartbot", "restartbot")

    def callshutdownbymaster(self, to, time=0, msg=""):
        shutdownmachine = {
            "action": "shutdownfrommaster",
            "sessionid": self.name_random(5, "shutdown"),
            "data": {"time": time, "msg": msg},
            "ret": 0,
            "base64": False,
        }
        return self.send_message(to, shutdownmachine)
        # self.sendstr(json.dumps(shutdownmachine), priority=1)
        # return True

    def callvncchangepermsbymaster(self, to, askpermission=1):
        vncchangepermsonmachine = {
            "action": "vncchangepermsfrommaster",
            "sessionid": self.name_random(5, "vncchangeperms"),
            "data": {"askpermission": askpermission},
            "ret": 0,
            "base64": False,
        }
        return self.send_message(to, vncchangepermsonmachine)
        # self.sendstr(json.dumps(vncchangepermsonmachine), priority=1)
        # return True


class TimedCompressedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Extended version of TimedRotatingFileHandler that compresses logs on rollover.

    This handler rotates logs based on a time interval and compresses the rotated
    log files into ZIP format. It manages the number of backup files to keep.

    Attributes:
        backupCountlocal (int): The number of backup files to keep.
    """

    def __init__(
        self,
        filename,
        when="h",
        interval=1,
        backupCount=0,
        encoding=None,
        delay=False,
        utc=False,
        compress="zip",
    ):
        """
        Initializes the TimedCompressedRotatingFileHandler with the specified parameters.

        Args:
            filename (str): The base filename for the log files.
            when (str): The time interval for rotation (default: "h" for hours).
            interval (int): The number of units for the rotation interval (default: 1).
            backupCount (int): The maximum number of backup files to keep (default: 0).
            encoding (str): The encoding used for the log files (default: None).
            delay (bool): If True, the log file will not be opened until the first write (default: False).
            utc (bool): If True, uses UTC time for rotations (default: False).
            compress (str): The compression format (default: "zip").
        """
        # Call the superclass initializer for basic log file handling
        super(TimedCompressedRotatingFileHandler, self).__init__(
            filename, when, interval, backupCount, encoding, delay, utc
        )
        self.backupCountlocal = backupCount  # Store the backup count locally

    def get_files_by_date(self):
        """
        Retrieves log files and their creation timestamps, sorting them into
        compressed and uncompressed lists. Deletes old compressed files
        beyond the backup count limit.

        Returns:
            str: The filename of the log file to keep after rotation.
        """
        dir_name, base_name = os.path.split(self.baseFilename)  # Split the path to get directory and base name
        file_names = os.listdir(dir_name)  # List all files in the directory
        result = []  # To hold uncompressed files
        result1 = []  # To hold compressed files
        prefix = "{}".format(base_name)  # Create a prefix based on the base name

        # Loop through files to categorize them as compressed or uncompressed
        for file_name in file_names:
            if file_name.startswith(prefix) and not file_name.endswith(".zip"):
                f = os.path.join(dir_name, file_name)
                result.append((os.stat(f).st_ctime, f))  # Store creation time and file path
            if file_name.startswith(prefix) and file_name.endswith(".zip"):
                f = os.path.join(dir_name, file_name)
                result1.append((os.stat(f).st_ctime, f))  # Store creation time and compressed file path

        result1.sort()  # Sort compressed files by creation time
        result.sort()  # Sort uncompressed files by creation time

        # Remove old compressed files beyond the defined backup count
        while result1 and len(result1) >= self.backupCountlocal:
            el = result1.pop(0)  # Get the oldest compressed file
            if os.path.exists(el[1]):
                os.remove(el[1])  # Remove it from the filesystem

        # Return the most recent uncompressed log file to keep
        return result[1][1]

    def doRollover(self):
        """
        Handles the log file rollover by calling the superclass's rollover method
        and compressing the old log file into a ZIP format.
        """
        super(TimedCompressedRotatingFileHandler, self).doRollover()  # Perform regular rollover
        try:
            dfn = self.get_files_by_date()  # Get the most recent log file to work with
        except:
            return  # If an error occurs, simply return

        # Prepare the name for the compressed ZIP file
        dfn_zipped = "{}.zip".format(dfn)
        if os.path.exists(dfn_zipped):
            os.remove(dfn_zipped)  # Remove the ZIP file if it exists

        # Create a new ZIP file and add the uncompressed log file to it
        with zipfile.ZipFile(dfn_zipped, "w") as f:
            f.write(dfn, os.path.basename(dfn), zipfile.ZIP_DEFLATED)

        os.remove(dfn)  # Remove the uncompressed log file after compression


logger = logging.getLogger()

sys.path.append("plugins")

Fault = xmlrpc.client.Fault
ctx = None
VERSION = "5.4.6"


class IncludeStartsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter include ONLY the logs which starts by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is found (= print the record)
            or
            False if the criterion is not found (= don't print the record)
        """
        return record.getMessage().startswith(self.criterion)


# include log containing the criterions
class IncludeContainsFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter include ONLY the logs which contains the specified criterions"""

    def __init__(self, criterion=[]):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: list of the searched criterions"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is found (= print the record)
            or
            False if the criterion is not found (= don't print the record)
        """
        # if criterion == [] the filter let pass all messages
        flag = False
        for criterion in self.criterion:
            if re.search(criterion, record.getMessage(), re.I):
                flag = True
        return flag


# include log ending by the criterion
class IncludeEndsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter include ONLY the logs which ends by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is found (= print the record)
            or
            False if the criterion is not found (= don't print the record)
        """
        return record.getMessage().endswith(self.criterion)


# exclude all log starting by criterion
class ExcludeStartsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter excludes ALL the logs which starts by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is not found (= print the record)
            or
            False if the criterion is found (= don't print the record)
        """
        # if criterion == "" the filter exclude all messages
        return not record.getMessage().startswith(self.criterion)


# include log containing the criterion
class ExcludeContainsFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter excludes ALL the logs which contains the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is not found (= print the record)
            or
            False if the criterion is found (= don't print the record)
        """
        if re.search(self.criterion, record.getMessage(), re.I):
            return False
        else:
            return True


# include log ending by the criterion
class ExcludeEndsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter excludes ALL the logs which ends by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is not found (= print the record)
            or
            False if the criterion is found (= don't print the record)
        """
        return not record.getMessage().endswith(self.criterion)

def sanitize_for_xmlrpc(value):
    """
    Transforme récursivement les types non supportés par XML-RPC en types sérialisables.

    Types supportés nativement par XML-RPC:
        - int, float
        - bool
        - str
        - list, dict
        - None (si allow_none=True)

    Transformation appliquée:
        - None -> '' (pour compatibilité maximum avec tous les clients)
        - Decimal -> float
        - dict/list -> récursivement
        - Pour tout autre type exotique: ajouter un `elif` spécifique ici
          ou convertir en str pour la sérialisation.

    Exemple pour gérer un datetime:
        from datetime import datetime
        if isinstance(value, datetime):
            return xmlrpc.client.DateTime(value)

    Exemple pour gérer un UUID:
        import uuid
        if isinstance(value, uuid.UUID):
            return str(value)

    Parameters
    ----------
    value : any
        Valeur Python à transformer

    Returns
    -------
    value : any
        Valeur transformée, uniquement avec des types XML-RPC valides
    """
    if value is None:
        return ""
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, dict):
        return {k: sanitize_for_xmlrpc(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_for_xmlrpc(v) for v in value]
    # Exemple pour ajouter d'autres types:
    # elif isinstance(value, datetime):
    #     return xmlrpc.client.DateTime(value)
    # elif isinstance(value, uuid.UUID):
    #     return str(value)
    else:
        # Par défaut: laisser tel quel (doit être int, float, str, bool)
        return value


class MmcServer(XMLRPC, object):
    """
    Serveur MMC implémenté comme un serveur XML-RPC avec Twisted.
    Ce serveur permet de :
    - Charger des plugins depuis le répertoire "plugins/"
    - Gérer l'authentification des utilisateurs via HTTP Basic Auth
    - Gérer les sessions utilisateur (avec expiration)
    - Supporter l'exécution multithread des requêtes
    - Fournir des méthodes d'introspection XML-RPC standard
    - Permettre le rechargement des configurations des plugins
    Fichier de configuration : @sysconfdir@/agent/config.ini
    """

    # Ensemble pour suivre toutes les sessions actives
    sessions = set()

    def __init__(self, modules, config):
        """
        Initialise le serveur MMC.

        Args:
            modules (dict): Modules de plugins chargés.
            config (object): Objet de configuration du serveur.
        """
        XMLRPC.__init__(self)
        self.modules = modules
        self.config = config

    def _splitFunctionPath(self, functionPath):
        """
        Sépare un chemin de fonction en module et nom de fonction.

        Args:
            functionPath (str): Chemin de la fonction, par exemple "module.fonction".

        Returns:
            tuple: (module, function_name) ou (None, function_name) si pas de module.
        """
        if "." in functionPath:
            mod, func = functionPath.split(".", 1)
        else:
            mod = None
            func = functionPath
        return mod, func

    def _getFunction(self, functionPath, request=""):
        """
        Résout un chemin de fonction en un objet appelable.

        Args:
            functionPath (str): Chemin de la fonction, par exemple "module.fonction".
            request (Request): Objet de requête actuel.

        Returns:
            callable: Fonction à exécuter.

        Raises:
            Fault: Si la fonction n'existe pas.
        """
        mod, func = self._splitFunctionPath(functionPath)
        try:
            if mod and mod != "system":
                try:
                    # Récupère directement la fonction depuis le module
                    ret = getattr(self.modules[mod], func)
                except AttributeError:
                    # Si la fonction n'est pas trouvée, essaie le wrapper RpcProxy
                    rpcProxy = getattr(self.modules[mod], "RpcProxy")
                    ret = rpcProxy(request, mod).getFunction(func)
            else:
                # Fonctions appartenant au serveur lui-même
                ret = getattr(self, func)
        except AttributeError:
            logger.error(f"{functionPath} non trouvé")
            raise Fault("NO_SUCH_FUNCTION", f"No such function {functionPath}")
        return ret

    def _needAuth(self, functionPath):
        """
        Vérifie si une fonction nécessite une authentification.

        Args:
            functionPath (str): Chemin de la fonction.

        Returns:
            bool: True si une authentification est nécessaire.
        """
        mod, func = self._splitFunctionPath(functionPath)
        # Cas spécial : la fonction de rechargement ne nécessite pas d'authentification
        if (mod, func) == ("system", "reloadModulesConfiguration"):
            return False
        ret = True
        if mod:
            try:
                # Liste NOAUTHNEEDED est définie par le plugin
                nanl = self.modules[mod].NOAUTHNEEDED
                ret = func not in nanl
            except (KeyError, AttributeError):
                pass
        return ret

    def render_OPTIONS(self, request):
        """
        Gère les requêtes CORS preflight OPTIONS.
        """
        request.setHeader(
            "Access-Control-Allow-Origin",
            request.requestHeaders.getRawHeaders("Origin"),
        )
        request.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS")
        request.setHeader("Access-Control-Allow-Credentials", "true")
        request.setHeader("Access-Control-Allow-Headers", "content-type, authorization")
        request.setHeader("Access-Control-Max-Age", "1728000")
        request.setHeader("Content-Type", "text/plain")
        return ""

    def render_POST(self, request):
        """
        Surcharge de la méthode POST du framework XML-RPC Twisted.
        Gère l'authentification, les sessions, et l'exécution des fonctions RPC.

        Args:
            request: Requête XML-RPC brute.

        Returns:
            server.NOT_DONE_YET: Indique que la réponse sera envoyée plus tard.
        """
        # Gestion des headers CORS
        if request.requestHeaders.hasHeader("Origin"):
            request.setHeader(
                "Access-Control-Allow-Origin",
                request.requestHeaders.getRawHeaders("Origin"),
            )
        request.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS")
        request.setHeader("Access-Control-Allow-Credentials", "true")
        request.setHeader("Access-Control-Allow-Headers", "content-type,authorization")
        request.setHeader("Access-Control-Expose-Headers", "content-type,cookie")
        request.setHeader("Access-Control-Max-Age", "1728000")

        # Lecture de la requête XML
        requestxml = request.content.read()
        args, functionPath = xmlrpc.client.loads(requestxml)
        s = request.getSession()

        # Initialisation des attributs de session si absents
        if not hasattr(s, "loggedin"):
            s.loggedin = False
        if not hasattr(s, "lastModified"):
            s.lastModified = reactor.seconds()
        if not hasattr(s, "sessionTimeout"):
            s.sessionTimeout = self.config.sessiontimeout

        # Vérification de l'expiration de la session
        try:
            current_time = reactor.seconds()
            if (
                self.config.sessiontimeout
                and (current_time - s.lastModified) > self.config.sessiontimeout
            ):
                logger.debug("Session expirée !")
                s.loggedin = False
                request.setResponseCode(http.UNAUTHORIZED)
                request.setHeader(b"content-type", b"text/html")
                request.setHeader(b"content-length", b"0")
                request.finish()
                return server.NOT_DONE_YET
            s.lastModified = current_time
        except AttributeError as e:
            logger.error(f"Erreur d'attribut : {e}")
            s.loggedin = False
            s.sessionTimeout = self.config.sessiontimeout
            return server.NOT_DONE_YET

        # Authentification HTTP Basic
        cleartext_token = f"{self.config.login}:{self.config.password}"
        user = str(request.getUser(), "utf-8")
        password = str(request.getPassword(), "utf-8")
        token = f"{user}:{password}"
        if token != cleartext_token:
            logger.error("Identifiants invalides pour l'authentification HTTP Basic")
            request.setResponseCode(http.UNAUTHORIZED)
            self._cbRender(
                Fault(
                    http.UNAUTHORIZED,
                    "Non autorisé : identifiants invalides pour se connecter à l'agent MMC, authentification HTTP Basic requise",
                ),
                request,
            )
            return server.NOT_DONE_YET

        # Log des appels RPC
        if not s.loggedin:
            logger.debug(f"Appel RPC depuis un utilisateur non authentifié : {functionPath}{str(args)}")
            s.http_headers = request.requestHeaders.copy()
        else:
            logger.debug(f"Appel RPC depuis l'utilisateur {s.userid} : {functionPath}{str(args)}")

        # Vérification de l'authentification et exécution de la fonction
        try:
            if not s.loggedin and self._needAuth(functionPath):
                msg = f"Authentification nécessaire : {functionPath}"
                logger.debug(msg)
                raise Fault(8003, msg)
            else:
                if not s.loggedin and not self._needAuth(functionPath):
                    s.userid = "root"
                    try:
                        self._associateContext(request, s, s.userid)
                    except Exception as e:
                        s.loggedin = False
                        logger.exception(e)
                        f = Fault(8004, "L'agent MMC ne peut pas fournir de contexte de sécurité")
                        self._cbRender(f, request)
                        return server.NOT_DONE_YET
                function = self._getFunction(functionPath, request)
        except Fault as f:
            self._cbRender(f, request)
        else:
            if self.config.multithreading:
                oldargs = args
                args = (function, s,) + args
                defer.maybeDeferred(self._runInThread, *args).addErrback(
                    self._ebRender, functionPath, oldargs, request
                ).addCallback(self._cbRender, request, functionPath, oldargs)
            else:
                defer.maybeDeferred(function, *args).addErrback(
                    self._ebRender, functionPath, args, request
                ).addCallback(self._cbRender, request, functionPath, args)
        return server.NOT_DONE_YET

    def _runInThread(self, *args, **kwargs):
        """
        Exécute une fonction dans un thread séparé, en gérant les Deferred.
        Permet de ne pas bloquer le réacteur Twisted.
        """
        def _printExecutionTime(start):
            logger.debug(f"Temps d'exécution : {time.time() - start}")

        def _cbSuccess(result, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.callback, result)

        def _cbFailure(failure, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.errback, failure)

        def _putResult(deferred, f, session, args, kwargs):
            logger.debug(
                f"Utilisation du thread #{threading.currentThread().getName().split('-')[2]} pour {f.__name__}"
            )
            threading.currentThread().session = session
            start = time.time()
            try:
                result = f(*args, **kwargs)
            except:
                f = failure.Failure()
                reactor.callFromThread(deferred.errback, f)
            else:
                if isinstance(result, defer.Deferred):
                    result.addCallback(_cbSuccess, deferred, start)
                    result.addErrback(_cbFailure, deferred, start)
                else:
                    _printExecutionTime(start)
                    reactor.callFromThread(deferred.callback, result)

        function = args[0]
        context = args[1]
        args = args[2:]
        d = defer.Deferred()
        reactor.callInThread(_putResult, d, function, context, args, kwargs)
        return d


    def _cbRender(self, result, request, functionPath=None, args=None):
        """
        Callback pour rendre le résultat d'une requête XML-RPC.

        - Appelée automatiquement par Twisted après l'exécution d'une méthode
        XML-RPC exposée.
        - Sérialise le résultat Python en XML-RPC et écrit la réponse HTTP.

        🔹 Transformations appliquées avant sérialisation :
        -----------------------------------------------
        1. `result = sanitize_for_xmlrpc(result)` :
        - Remplace `None` par '' pour compatibilité maximale.
        - Convertit `decimal.Decimal` en `float`.
        - Transforme récursivement les dicts et listes.
        - Possibilité d'ajouter d'autres types exotiques (datetime, UUID, etc.).
        2. `xmlrpc.client.dumps((result,), methodresponse=True, allow_none=True)` :
        - Enveloppe le résultat dans un tuple comme l'exige xmlrpc.client.
        - `allow_none=True` permet de générer `<nil/>` pour les valeurs `None`.

        ⚠️ Points importants :
        ----------------------
        - XML-RPC standard ne supporte pas `None`. Sans `allow_none=True`, une
        exception "cannot marshal objects" est levée.
        - Les clients XML-RPC doivent accepter `<nil/>` pour que cela fonctionne
        correctement. Exemple en PHP : `$GLOBALS['xmlrpc_null_extension'] = true;`
        avec phpxmlrpc.
        - Tout type Python non supporté par XML-RPC (Decimal, datetime, UUID, etc.)
        doit être transformé avant le dump pour éviter une exception.

        Avantages :
        ----------
        - Permet d'envoyer des résultats contenant des `None` et d'autres types
        Python non-XML-RPC sans planter le serveur.

        Inconvénients :
        --------------
        - `<nil/>` n'est pas standard XML-RPC : certains clients stricts peuvent
        ne pas savoir le décoder. Dans ce cas, il faudra prévoir un fallback
        (ex : remplacer `None` par '').

        Parameters
        ----------
        result : any
            Résultat de la méthode XML-RPC (dict, list, etc.)
        request : twisted.web.http.Request
            Objet HTTP Twisted pour la réponse
        functionPath : str, optional
            Nom de la méthode appelée
        args : tuple, optional
            Arguments passés à la méthode
        """
        s = request.getSession()
        auth_funcs = ["base.ldapAuth", "base.tokenAuthenticate", "base.authenticate"]

        if functionPath in auth_funcs and not isinstance(result, Fault):
            if result:
                s.loggedin = True
                s.userid = args[0]
                try:
                    self._associateContext(request, s, s.userid)
                except Exception as e:
                    s.loggedin = False
                    logger.exception(e)
                    f = Fault(8004, "L'agent MMC ne peut pas fournir de contexte de sécurité pour ce compte")
                    self._cbRender(f, request)
                    return

        try:
            # 🔹 Fix: autoriser la sérialisation de None via <nil/>
            # Toujours envelopper le résultat dans un tuple
            result = sanitize_for_xmlrpc(result)
            # Log du résultat
            if s.loggedin:
                logger.debug(f"Résultat pour {s.userid}, {functionPath}: {result}")
            else:
                logger.debug(f"Résultat pour utilisateur non authentifié, {functionPath}: {result}")

            xml = xmlrpc.client.dumps((result,), methodresponse=True, allow_none=True)
        except Exception as e:
            logger.exception("Erreur de sérialisation XML-RPC: %s", e)
            fault = Fault(8005, f"Impossible de sérialiser la sortie : {e}")
            xml = xmlrpc.client.dumps((fault,), methodresponse=True, allow_none=True)
        request.setHeader(b"content-type", b"text/xml")
        request.write(xml.encode("utf-8"))
        request.finish()
    #
    # a supprimer apres test
    # def _cbRender(self, result, request, functionPath=None, args=None):
    #     """
    #     Callback pour rendre le résultat d'une requête RPC.
    #     Gère la sérialisation XML, les logs et les headers HTTP.
    #     """
    #     s = request.getSession()
    #     auth_funcs = ["base.ldapAuth", "base.tokenAuthenticate", "base.authenticate"]
    #     if functionPath in auth_funcs and not isinstance(result, Fault):
    #         if result:
    #             s = request.getSession()
    #             s.loggedin = True
    #             s.userid = args[0]
    #             try:
    #                 self._associateContext(request, s, s.userid)
    #             except Exception as e:
    #                 s.loggedin = False
    #                 logger.exception(e)
    #                 f = Fault(8004, "L'agent MMC ne peut pas fournir de contexte de sécurité pour ce compte")
    #                 self._cbRender(f, request)
    #                 return
    #
    #     if result is None:
    #         result = 0
    #     if isinstance(result, Handler):
    #         result = result.result
    #     if not isinstance(result, xmlrpc.client.Fault):
    #         result = (result,)
    #
    #     # Hack pour gérer les données binaires (ex: jpegPhoto)
    #     try:
    #         if isinstance(result[0], dict) and "jpegPhoto" in result[0]:
    #             result[0]["jpegPhoto"] = [xmlrpc.client.Binary(result[0]["jpegPhoto"][0])]
    #     except (IndexError, Exception):
    #         pass
    #
    #     # Log du résultat
    #     try:
    #         if s.loggedin:
    #             logger.debug(f"Résultat pour {s.userid}, {functionPath}: {result}")
    #         else:
    #             logger.debug(f"Résultat pour utilisateur non authentifié, {functionPath}: {result}")
    #         s = xmlrpc.client.dumps(result, methodresponse=1)
    #     except Exception as e:
    #         f = Fault(self.FAILURE, f"Impossible de sérialiser la sortie : {e}")
    #         s = xmlrpc.client.dumps(f, methodresponse=1)
    #
    #     s = bytes(s, encoding="utf-8")
    #     request.setHeader("content-length", str(len(s)))
    #     request.setHeader("content-type", "application/xml")
    #     request.write(s)
    #     request.finish()

    def _ebRender(self, failure, functionPath, args, request):
        """
        Callback en cas d'erreur lors du rendu d'une requête RPC.
        """
        logger.error(f"Erreur lors du rendu {functionPath} : {failure.getTraceback()}")
        result = {
            "faultString": f"{functionPath} {str(args)}",
            "faultCode": f"{failure.type}: {failure.value}",
            "faultTraceback": failure.getTraceback(),
        }
        return result

    def _associateContext(self, request, session, userid):
        """
        Demande à chaque plugin Python activé un contexte à attacher à la session utilisateur.

        Args:
            request: Requête XML-RPC actuelle.
            session: Objet de session actuel.
            userid: Identifiant de l'utilisateur.
        """
        session.contexts = {}
        for mod in self.modules:
            try:
                contextMaker = getattr(self.modules[mod], "ContextMaker")
            except AttributeError:
                continue
            cm = contextMaker(request, session, userid)
            context = cm.getContext()
            if context:
                logger.debug(f"Attachement du contexte du module '{mod}' à la session utilisateur")
                session.contexts[mod] = context
        if session not in self.sessions:
            self.sessions.add(session)

    # ===== Méthode de rechargement =====
    def reloadModulesConfiguration(self):
        """
        Recharge la configuration de tous les plugins.
        Expire toutes les sessions actives.
        """
        import gc
        from mmc.support.config import PluginConfig
        for obj in gc.get_objects():
            if isinstance(obj, PluginConfig):
                try:
                    with open(obj.conffile, "r") as fid:
                        obj.readfp(fid, obj.conffile)
                    if os.path.isfile(obj.conffile + ".local"):
                        with open(obj.conffile + ".local", "r") as fid:
                            obj.readfp(fid, obj.conffile + ".local")
                    obj.readConf()
                except Exception as e:
                    logger.error(f"Erreur lors du rechargement du fichier {obj.conffile}")
                    logger.error(str(e))
                    return "Failed"
        for session in self.sessions:
            session.expire()
        self.sessions = set()
        return "Done"

    # ===== Méthodes d'introspection XML-RPC standard =====
    def listMethods(self):
        """
        Liste toutes les méthodes RPC disponibles.
        """
        method_list = []
        for mod in self.modules:
            instance = self.modules[mod]
            for m in dir(instance):
                r = getattr(instance, m)
                if hasattr(r, "__call__"):
                    method_list.append(f"{mod}.{m}")
            if hasattr(instance, "RpcProxy"):
                for m in dir(instance.RpcProxy):
                    r = getattr(instance.RpcProxy, m)
                    if hasattr(r, "__call__"):
                        method_list.append(f"{mod}.{m}")
        return method_list

    def __getClassMethod(self, name):
        """
        Récupère une méthode de classe à partir de son nom.

        Args:
            name (str): Nom de la méthode.

        Returns:
            callable: Méthode ou None si non trouvée.
        """
        mod, func = self._splitFunctionPath(name)
        if mod not in self.modules:
            return None
        instance = self.modules[mod]
        if hasattr(instance, "RpcProxy"):
            if hasattr(instance.RpcProxy, func):
                return getattr(instance.RpcProxy, func)
            elif hasattr(instance, func):
                return getattr(instance, func)
        return None

    def methodSignature(self, name):
        """
        Retourne la signature d'une méthode RPC.

        Args:
            name (str): Nom de la méthode.

        Returns:
            list: Liste des arguments de la méthode.
        """
        method = self.__getClassMethod(name)
        if method is None:
            return []
        return getfullargspec(method)[0]

    def methodHelp(self, name):
        """
        Retourne la documentation d'une méthode RPC.

        Args:
            name (str): Nom de la méthode.

        Returns:
            str: Documentation de la méthode.
        """
        method = self.__getClassMethod(name)
        if method is None:
            return ""
        return method.__doc__

    # ===== Méthodes utilitaires =====
    def getRevision(self):
        """Retourne la révision SCM du serveur."""
        return scmRevision("$Rev$")

    def getVersion(self):
        """Retourne la version du serveur."""
        return VERSION

    def log(self, fileprefix, content):
        """
        Écrit un message dans un fichier de log.

        Args:
            fileprefix (str): Préfixe du fichier de log.
            content (str): Contenu à enregistrer.
        """
        with open(f"{localstatedir}/log/mmc/mmc-{fileprefix}.log", "a") as f:
            f.write(f"{time.asctime()}: {content}\n")


















class MMCApp(object):
    """Represent the MMCApp"""

    def __init__(self, config, options):
        self.config = readConfig(config)
        self.conffile = options.inifile
        self.daemon = options.daemonize
        self.daemonlog = options.daemonizenolog

        if hasattr(options, "exclude") and options.exclude is not None:
            self.exclude = options.exclude.split(",")

            for filter in self.exclude:
                logger.addFilter(ExcludeContainsFilter(filter))
                logging.getLogger("slixmpp.xmlstream.xmlstream").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.clientxmpp").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.plugins.base").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger(
                    "slixmpp.features.feature_starttls.starttls"
                ).addFilter(ExcludeContainsFilter(filter))
                logging.getLogger("slixmpp.thirdparty.statemachine").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger(
                    "slixmpp.features.feature_rosterver.rosterver"
                ).addFilter(ExcludeContainsFilter(filter))
                logging.getLogger("slixmpp.plugins.xep_0045").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.plugins.xep_0078.legacyauth").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.features.feature_bind.bind").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.features.feature_session.session").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.xmlstream.scheduler").addFilter(
                    ExcludeContainsFilter(filter)
                )

        if hasattr(options, "include") and options.include is not None:
            self.include = options.include.split(",")
            logger.addFilter(IncludeContainsFilter(self.include))
            logging.getLogger("slixmpp.xmlstream.xmlstream").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.clientxmpp").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.plugins.base").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_starttls.starttls").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.thirdparty.statemachine").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_rosterver.rosterver").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.plugins.xep_0045").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.plugins.xep_0078.legacyauth").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_bind.bind").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_session.session").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.xmlstream.scheduler").addFilter(
                IncludeContainsFilter(self.include)
            )

        if not self.daemonlog:
            self.daemon = False
        # Shared return state, so that father can know if children goes wrong
        if self.daemon:
            self._shared_state = mp.Value("i", 0)

        if self.daemon:
            self.lock = mp.Lock()

    def getState(self):
        if self.daemon:
            return self._shared_state.value

    def setState(self, s):
        if self.daemon:
            self._shared_state.value = s

    state = property(getState, setState)

    def daemonize(self):
        # Test if mmcagent has been already launched in daemon mode
        if os.path.isfile(self.config.pidfile):
            print(
                "%s already exist. Maybe mmc-agent is already running\n"
                % self.config.pidfile
            )
            sys.exit(0)

        # do the UNIX double-fork magic, see Stevens' "Advanced
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try:
            pid = os.fork()
            if pid > 0:
                # Wait for initialization before exiting
                self.lock.acquire()
                # exit first parent and return
                sys.exit(self.state)
        except OSError as e:
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            self.state = 1
            self.lock.release()
            sys.exit(1)

        maxfd = getrlimit(RLIMIT_NOFILE)[1]
        if maxfd == RLIM_INFINITY:
            maxfd = 1024

        for fd in range(0, maxfd):
            # Don't close twisted FDs
            # TODO: make a clean code to be sure nothing is opened before this function
            # ie: daemonize very early, then after import all stuff...
            if fd not in (3, 4, 5, 6, 7, 8):
                try:
                    os.close(fd)
                except OSError:
                    pass

        if hasattr(os, "devnull"):
            REDIRECT_TO = os.devnull
        else:
            REDIRECT_TO = "/dev/null"

        os.open(REDIRECT_TO, os.O_RDWR)
        os.dup2(0, 1)
        os.dup2(0, 2)

        # write pidfile
        self.writePid()

    def kill(self):
        pid = self.readPid()
        if pid is None:
            print("Can not find a running mmc-agent.")
            return 1

        try:
            os.kill(pid, signal.SIGTERM)
        except Exception as e:
            print("Can not terminate running mmc-agent: %s" % e)
            return 1

        return 0

    def reload(self):
        if self.config.enablessl:
            protocol = "https"
        else:
            protocol = "http"

        client = xmlrpc.client.ServerProxy(
            "%s://%s:%s@%s:%s/"
            % (
                protocol,
                self.config.login,
                self.config.password,
                self.config.host,
                self.config.port,
            )
        )
        try:
            client.system.reloadModulesConfiguration()
            return 0
        except Exception as e:
            print("Unable to reload configuration: %s" % str(e))
            return 1

    def readPid(self):
        """Try to read pid of running mmc-agent in pidfile
        Return the pid or None in case of failure
        """
        try:
            if os.path.exists(self.config.pidfile):
                f = open(self.config.pidfile, "r")
                try:
                    line = f.readline()
                    return int(line.strip())
                finally:
                    f.close()
        except:
            return None

    def writePid(self):
        pid = os.getpid()
        f = open(self.config.pidfile, "w")
        try:
            f.write("%s\n" % pid)
        finally:
            f.close()

    def cleanPid(self):
        if os.path.exists(self.config.pidfile):
            os.unlink(self.config.pidfile)

    def run(self):
        # If umask = 0077, created files will be rw for effective user only
        # If umask = 0007, they will be rw for effective user and group only
        os.umask(self.config.umask)
        os.setegid(self.config.egid)
        os.seteuid(self.config.euid)

        # Daemonize early
        if self.daemon:
            self.lock.acquire()
            self.daemonize()

        # Do all kind of initialization
        try:
            ret = self.initialize()
        finally:
            # Tell the father how to return, and let him return (release)
            if self.daemon:
                self.state = ret
                self.lock.release()

        if ret:
            return ret

        reactor.run()

    def initialize(self):
        # Initialize logging object
        print("Initialisation of the XMLRPC Server")
        try:
            logging.handlers.TimedCompressedRotatingFileHandler = (
                TimedCompressedRotatingFileHandler
            )
            logging.config.fileConfig(self.conffile)

            # In foreground mode, log to stderr
            if not self.daemon:
                if self.daemonlog:
                    hdlr2 = logging.StreamHandler()
                    hdlr2.setFormatter(ColoredFormatter("%(levelname)-18s %(message)s"))
                    logger.addHandler(hdlr2)

            # Create log dir if it doesn't exist
            try:
                os.mkdir(localstatedir + "/log/mmc")
            except OSError as xxx_todo_changeme:
                # Raise exception if error is not "File exists"
                (errno, strerror) = xxx_todo_changeme.args
                # Raise exception if error is not "File exists"
                if errno != 17:
                    raise
                else:
                    pass

            # Changing path to probe and load plugins
            os.chdir(os.path.dirname(globals()["__file__"]))

            logger.info("mmc-agent %s starting..." % VERSION)
            logger.info("Using Python %s" % sys.version.split("\n")[0])
            logger.info("Using Python Twisted %s" % twisted.copyright.version)

            logger.debug(
                "Running as euid = %d, egid = %d" % (os.geteuid(), os.getegid())
            )
            if self.config.multithreading:
                logger.info(
                    "Multi-threading enabled, max threads pool size is %d"
                    % self.config.maxthreads
                )
                reactor.suggestThreadPoolSize(self.config.maxthreads)

            # Export the MMC-AGENT variable in the environement so that
            # child process can know they were spawned by mmc-agent
            os.environ["MMC_AGENT"] = VERSION

            # Start audit system
            l = AuditFactory().log("MMC-AGENT", "MMC_AGENT_SERVICE_START")

            # Ask PluginManager to load MMC plugins
            pm = PluginManager()
            code = pm.loadPlugins()
            if code:
                logger.debug(
                    "The initialisation of the XMLRPC Server returned the code: %s "
                    % code
                )
                return code

            try:
                self.startService(pm.plugins)
            except Exception as e:
                # This is a catch all for all the exception that can happened
                logger.exception("Program exception: " + str(e))
                logger.debug("The initialisation of the XMLRPC Server returned 1")
                return 1

            l.commit()
        except Exception:
            logger.error("%s" % (traceback.format_exc()))
        logger.debug("The initialisation of the XMLRPC Server returned 0")
        return 0

    def startService(self, mod):
        # Starting XMLRPC server
        r = MmcServer(mod, self.config)
        if self.config.enablessl:
            sslContext = makeSSLContext(
                self.config.verifypeer, self.config.cacert, self.config.localcert
            )
            reactor.listenSSL(
                self.config.port,
                MMCSite(r),
                interface=self.config.host,
                contextFactory=sslContext,
            )
        else:
            logger.warning("SSL is disabled by configuration.")
            reactor.listenTCP(
                self.config.port, server.Site(r), interface=self.config.host
            )

        # Add event handler before shutdown
        reactor.addSystemEventTrigger("before", "shutdown", self.cleanUp)
        logger.info(
            "Listening to XML-RPC requests on %s:%s"
            % (self.config.host, self.config.port)
        )
        # Start client XMPP if module xmppmaster enable
        if PluginManager().isEnabled("xmppmaster"):
            configxmppmaster = XmppMasterDatabase().config
            # create file  message
            PluginManager().getEnabledPlugins()["xmppmaster"].modulemessagefilexmpp = (
                messagefilexmpp(self, self.config, configxmppmaster)
            )
            self.modulexmppmaster = (
                PluginManager().getEnabledPlugins()["xmppmaster"].modulemessagefilexmpp
            )
            # on a besoin de savoir les modules de mmc initialise
            XmppMasterDatabase().initialisation_module_list_mmc(
                PluginManager().getEnabledPluginNames()
            )
            # MASTER now is a substitute.
            self.config_bool_done = False
            logger.info("Start/restart MMC presence client substitut master")
            result = self.modulexmppmaster.sendstr("Start/restart MMC")
            if result is None:
                logger.info("INITIALISATION MMC (xmppmaster) ERREUR")
                logger.info("VERIFY SUBSTITUT MASTER START")
                logger.info("VERIFY PARAMETERS CONNECTION TO SUBSTITUT MASTER")
                logger.info("Restart SUBSTITUT MASTER")
                return
            self.init_master_substitut()

    def init_master_substitut(self):
        logger.debug("INITIALISATION SUBSTITUT")
        ree = None
        if (
            not PluginManager()
            .getEnabledPlugins()["xmppmaster"]
            .modulemessagefilexmpp.config_bool_done
        ):
            # important ici sont reunit en exemple mcanisme d'utilisation du serveur substiitut master.
            logger.info("initialise la liste des module MMC dans substitut master")
            # list_mmc_module est appeler au lancement de la mmc.
            # list_mmc_module n'est pas 1 plugin cet appel est traité dans le plugin
            # serveur /pluginsmastersubstitute/plugin___server_mmc_master.py
            # cette list permet de renseigner le substitut master des module active dans mmc.
            # remarque si mmc est lancer avant le substitut master. celui ci ne recevra pas cette list.
            result = {
                "action": "list_mmc_module",
                "data": PluginManager().getEnabledPluginNames(),
            }
            logger.info(
                "Start/restart MMC send module On on %s  MMC"
                % PluginManager().getEnabledPluginNames()
            )

            ree = self.modulexmppmaster.send_call_plugin(result)
            logger.info(
                "call plugin %s on master directement tcp/ip : sessionid  %s => %s"
                % (result["action"], ree[0], ree[1])
            )
            if ree[0] is None and ree[0] == "Error connection":
                PluginManager().getEnabledPlugins()[
                    "xmppmaster"
                ].modulemessagefilexmpp.config_bool_done = False
                return False

            PluginManager().getEnabledPlugins()[
                "xmppmaster"
            ].modulemessagefilexmpp.config_bool_done = True
            return True
            # appel plugin directement sur substitut master.
            # Cela remplace les plugins master. qui seront transferer sur le substitut master.
            # remarque on prefixera les plugin par mmc_ quand ceux ci seront uniquement appelable par mmc
            # exemple appel pluging mmc directement sur substitut master test_plugin_master
            # remarque on pas de parametre to c'est 1 plugin mmc type
            # la connection mmc substitut est client/serveur/ mmc est client du substitut.
            # celui -ci est en mesure de renvoyer 1 resultat ici ree
            # -----------------------------------------------------------------------------------
            # --------------------------------- call plugin mmc ---------------------------------
            # logger.info("MMC start plugin test_plugin_master on substitut master : sessionid  %s => %s" % ( ree[0],ree[1]))
            # ree = self.modulexmppmaster.send_call_plugin({"action": "test_plugin_master",
            # "data": { "text" : "message" }} )
            # logger.info("call plugin test_plugin_master on master : sessionid  %s => %s" % ( ree[0],ree[1]))
            # -----------------------------------------------------------------------------------
            # -----------------------------------------------------------------------------------

            # --------------------------------------------------------------------------------------------------
            # --------------------------------- call plugin sur 1 acteur en xmpp -------------------------------
            # test envoi mesage to  machine  dev-deb12-2.zb0@pulse/525400944ac7
            # logger.info("Start/restart MMC creation canal commande xmpp3")

            # ree = self.modulexmppmaster.send_message('dev-deb12-2.zb0@pulse/525400944ac7',
            # {"action": "ping",
            # "data": { "text" : "message" }} )
            # --------------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------------

            # --------------------------------------------------------------------------------------------------
            # --------------------------------- call iq synchrone sur sur 1 acteur en xmpp -------------------------------
            # test de machinessend_iq(mto, msg, timeout):
            # ree= self.modulexmppmaster.send_iq('dev-deb12-2.zb0@pulse/525400944ac7',
            # { "action": "test",
            # "data": {
            # "listinformation": ["get_ars_key_id_rsa", "keypub"],
            # "param": {},
            # },
            # }, 30)
            # logger.debug("RESULTAT is %s" % ree)

    def cleanUp(self):
        """
        function call before shutdown of reactor
        """
        if PluginManager().isEnabled("xmppmaster"):
            # self.modulexmppmaster
            if self.modulexmppmaster.isAlive():
                logger.info("mmc-agent xmppmaster stop...")
                self.modulexmppmaster.stop()
        logger.info("mmc-agent shutting down, cleaning up...")
        l = AuditFactory().log("MMC-AGENT", "MMC_AGENT_SERVICE_STOP")
        l.commit()

        self.cleanPid()


class MMCHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the MMC
    agent is in DEBUG mode, and to log connection errors.
    """

    def connectionMade(self):
        http.HTTPChannel.connectionMade(self)

    def connectionLost(self, reason):
        if not reason.check(twisted.internet.error.ConnectionDone):
            logger.debug(reason)
        http.HTTPChannel.connectionLost(self, reason)


class MMCSite(server.Site):
    protocol = MMCHTTPChannel


def readConfig(config):
    """
    Read and check the MMC agent configuration file

    @param config: a MMCConfigParser object reading the agent conf file
    @type config: MMCConfigParser

    @return: MMCConfigParser object with extra attributes set
    @rtype: MMCConfigParser
    """
    # TCP/IP stuff
    try:
        config.host = config.get("main", "host")
        config.port = config.getint("main", "port")
    except Exception as e:
        logger.error(e)
        return 1

    if config.has_section("daemon"):
        config.euid = pwd.getpwnam(config.get("daemon", "user"))[2]
        config.egid = grp.getgrnam(config.get("daemon", "group"))[2]
        config.umask = int(config.get("daemon", "umask"), 8)
    else:
        config.euid = 0
        config.egid = 0
        config.umask = 0o077

    # HTTP authentication login/password
    config.login = config.get("main", "login")
    config.password = config.getpassword("main", "password")

    # RPC session timeout
    try:
        config.sessiontimeout = config.getint("main", "sessiontimeout")
    except (configparser.NoSectionError, configparser.NoOptionError):
        # Use default session timeout
        config.sessiontimeout = server.Session.sessionTimeout

    # SSL stuff
    try:
        config.enablessl = config.getboolean("main", "enablessl")
    except (configparser.NoSectionError, configparser.NoOptionError):
        config.enablessl = False
    try:
        config.verifypeer = config.getboolean("main", "verifypeer")
    except (configparser.NoSectionError, configparser.NoOptionError):
        config.verifypeer = False

    if config.enablessl:
        # For old version compatibility, we try to get the old options name
        try:
            config.localcert = config.get("main", "localcert")
        except (configparser.NoSectionError, configparser.NoOptionError):
            config.localcert = config.get("main", "privkey")
        try:
            config.cacert = config.get("main", "cacert")
        except (configparser.NoSectionError, configparser.NoOptionError):
            config.cacert = config.get("main", "certfile")

    try:
        config.pidfile = config.get("daemon", "pidfile")
    except (configparser.NoSectionError, configparser.NoOptionError):
        # For compatibility with old version
        config.pidfile = config.get("log", "pidfile")

    # Multi-threading support
    config.multithreading = True
    config.maxthreads = 20
    try:
        config.multithreading = config.getboolean("main", "multithreading")
        config.maxthreads = config.getint("main", "maxthreads")
    except configparser.NoOptionError:
        pass

    # parametre client submaster
    config.submaster_host = "::1"
    config.submaster_check_hostname = False
    config.submaster_allowed_token = "4O&vHYKG3Cqq3RCUJu!vnQu+dBGwDkpZ"
    config.submaster_ip_format = "ipv6"
    config.submaster_port = "57041"

    if config.has_option("submaster", "host"):
        config.submaster_host = config.get("submaster", "host")

    if config.has_option("submaster", "port"):
        config.submaster_port = config.getint("submaster", "port")

    if config.has_option("submaster", "ip_format"):
        config.submaster_ip_format = config.get("submaster", "ip_format")

    if config.has_option("submaster", "allowed_token"):
        config.submaster_allowed_token = config.get("submaster", "allowed_token")

    # if config.has_option("submaster", "check_hostname"):
    # config.submaster_check_hostname = config.getboolean("submaster", "check_hostname")

    return config


class PluginManager(Singleton):
    """
    This singleton class imports available MMC plugins, activates them, and
    keeps track of all enabled plugins.
    """

    pluginDirectory = "plugins/"
    # Will contains the enabled plugins name and corresponding python
    # module objects
    plugins = {}

    def __init__(self):
        Singleton.__init__(self)

    def isEnabled(self, plugin):
        """
        @rtype: bool
        @return: Return True if the plugin has been enabled
        """
        return plugin in self.plugins

    def getEnabledPlugins(self):
        """
        @rtype: dict
        @return: the enabled plugins as a dict, key is the plugin name, value
                 is the python module object
        """
        return self.plugins

    def getEnabledPluginNames(self):
        """
        @rtype: list
        @return: the names of the enabled plugins
        """
        return list(self.getEnabledPlugins().keys())

    def getAvailablePlugins(self):
        """
        Fetch all available MMC plugin

        @return: list of all mmc plugins names
        @rtype: list
        """
        plugins = []
        for path in glob.glob(os.path.join(self.pluginDirectory, "*", "__init__.py*")):
            plugin = path.split("/")[1]
            if not plugin in plugins:
                plugins.append(plugin)
        return plugins

    def loadPlugin(self, name, force=False):
        """
        Load a plugin with the given name.

        To start one single module after the agent startup, use startPlugin()
        instead

        @returns: 4 on fatal error (mmc agent should not start without that
        plugin), 0 on non-fatal failure, and the module itself if
        the load was successful
        """
        sys.path.append(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins")
        )
        try:
            logger.debug("Trying to load module %s" % name)
            spec = importlib.util.find_spec(name)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            logger.debug("Module %s loaded" % name)
        except Exception as e:
            logger.exception(e)
            logger.error(
                "Module " + name + " raise an exception.\n" + name + " not loaded."
            )
            return 0

        # If module has no activate function
        try:
            # if not force:
            #     func = getattr(plugin, "activate")
            # else:
            # logger.debug('Forcing plugin startup')
            # try:
            # func = getattr(plugin, "activateForced")
            # except AttributeError:
            # logger.debug('Trying to force startup of plugin %s but no "activateForced" method found\nFalling back to the normale activate method' % (name,))

            version = "version: " + str(getattr(plugin, "getVersion")())
            logger.info("Plugin %s loaded, %s" % (name, version))

            func = getattr(plugin, "activate")

        except AttributeError as error:
            logger.error("%s is not a MMC plugin." % name)
            logger.error("We obtained the error \n %s." % error)
            plugin = None
            return 0

        # If is active
        try:
            if func():
                version = "version: " + str(getattr(plugin, "getVersion")())
                logger.info("Plugin %s loaded, %s" % (name, version))
            else:
                # If we can't activate it
                logger.warning("Plugin %s not loaded." % name)
                plugin = None
        except Exception as e:
            logger.error("Error while trying to load plugin " + name)
            logger.exception(e)
            plugin = None
            # We do no exit but go on when another plugin than base fail

        # Check that "base" plugin was loaded
        if name == "base" and not plugin:
            logger.error("MMC agent can't run without the base plugin. Exiting.")
            return 4
        return plugin

    def startPlugin(self, name):
        """
        Force a plugin load.
        Even if the configuration indicates the plugin is disabled,
        we load it and add it to the loaded list.

        Use it to start a plugin after the mmc agent startup, dynamically.

        This tries to call the activateForced method of the plugin (for example to
        ignore the disable = 1 configuration option)
        """
        if name in self.getEnabledPluginNames() or name in self.plugins:
            logger.warning("Trying to start an already loaded plugin: %s" % (name,))
            return 0
        res = self.loadPlugin(name, force=True)
        if res == 0:
            return 0
        elif res is not None and not isinstance(res, int):
            self.plugins[name] = res
            getattr(self.plugins["base"], "setModList")(
                [name for name in list(self.plugins.keys())]
            )
        elif res == 4:
            return 4
        return res

    def loadPlugins(self):
        """
        Find and load available MMC plugins

        @rtype: int
        @returns: exit code > 0 on error
        """
        # Find available plugins
        mod = {}
        sys.path.append("plugins")
        # self.modList = []
        plugins = self.getAvailablePlugins()
        if not "base" in plugins:
            logger.error("Plugin 'base' is not available. Please install it.")
            return 1
        else:
            # Set base plugin as the first plugin to load
            plugins.remove("base")
            plugins.insert(0, "base")

        # Put pulse2 plugins as the last to be imported, else we may get a mix
        # up with pulse2 module available in the main python path
        if "pulse2" in plugins:
            plugins.remove("pulse2")
            plugins.append("pulse2")

        # Load plugins
        logger.info("Importing available MMC plugins")
        for plugin in plugins:
            res = self.loadPlugin(plugin)
            if res == 0:
                continue
            elif res is not None and not isinstance(res, int):
                mod[plugin] = res
            elif res == 4:
                return 4

        # store enabled plugins
        self.plugins = mod

        logger.info("MMC plugins activation stage 2")
        for plugin in plugins:
            if self.isEnabled(plugin):
                try:
                    func = getattr(mod[plugin], "activate_2")
                except AttributeError:
                    func = None
                if func:
                    if not func():
                        logger.error(
                            "Error in activation stage 2 for plugin '%s'" % plugin
                        )
                        logger.error(
                            "Please check your MMC agent configuration and log"
                        )
                        return 4

        # Set module list
        getattr(self.plugins["base"], "setModList")(
            [name for name in list(self.plugins.keys())]
        )
        return 0

    def stopPlugin(self, name):
        """
        Stops a plugin.

        @rtype: boolean
        returns: True on success, False if the module is not loaded.
        """
        if not name in self.plugins:
            return False
        plugin = self.plugins[name]
        try:
            deactivate = getattr(plugin, "deactivate")
        except AttributeError:
            logger.info("Plugin %s has no deactivate function" % (name,))
        else:
            logger.info("Deactivating plugin %s" % (name,))
            deactivate()
        del self.plugins[name]
        getattr(self.plugins["base"], "setModList")(
            [name for name in list(self.plugins.keys())]
        )
        return True
