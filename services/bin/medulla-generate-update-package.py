#!/usr/bin/python3
# -*- coding:utf-8 -*-
# SPDX-FileCopyrightText: 2022-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later

# This script is used to generate update packages in /var/lib/pulse2/packages

from datetime import datetime

import requests
import subprocess
import sys, os
import signal
import logging
import traceback
import MySQLdb
import base64
import getpass
from optparse import OptionParser

# from  MySQLdb import IntegrityError
# Global Variables

logger = logging.getLogger()

# connection xmppmaster


class download_packages:
    def __init__(self, db, name_table_produit, outputdir):
        self.db = db
        self.name_table_produit = name_table_produit
        self.directory_output_package = outputdir

    def url_to_download(self):
        try:
            os.makedirs(self.directory_output_package)
            logger.debug(
                f"Directory '{self.directory_output_package}' created successfully"
            )
        except OSError as error:
            logger.debug(
                f"Directory '{self.directory_output_package}' can not be created"
            )

        sql = f""" SELECT title, payloadfiles,updateid, kb, description  FROM xmppmaster.{self.name_table_produit};"""

        cursor = self.db.cursor()
        record = cursor.execute(sql)
        for i in cursor.fetchall():
            dirpackage = os.path.join(self.directory_output_package, i[2])
            self.download_url(i[1], dirpackage, i[2], i[3], i[0], i[4])
        cursor.close()

    def download_url(self, urlpath, dirpackage, updateid, kb, title, description):
        logger.debug(f"download {urlpath}")
        start = datetime.now()
        # logger.debug ("download", urlpath, dirpackage )
        namefile = urlpath.split("/")[-1]
        path_file_download = os.path.join(dirpackage, namefile)
        # logger.debug("path_file_download %s " % path_file_download)
        if os.path.isfile(path_file_download):
            logger.debug(f"package existe {path_file_download}")
            end = datetime.now()
            return end - start
        try:
            os.makedirs(dirpackage)
            logger.debug(f"Directory '{dirpackage}' created successfully")
        except OSError as error:
            logger.debug(f"Directory {dirpackage} can not be created")
        try:
            data = requests.get(urlpath, stream=True)
        except Exception as e:
            logger.error(
                "Error trying to download update file %s: %s" % (urlpath, str(e))
            )
            try:
                # Try with proxy parameters as defined on the system
                proxy_url = (
                    os.environ.get("HTTP_PROXY")
                    or os.environ.get("HTTPS_PROXY")
                    or os.environ.get("http_proxy")
                    or os.environ.get("https_proxy")
                )
                if proxy_url:
                    proxies = {"http": proxy_url, "https": proxy_url}
                    data = requests.get(urlpath, stream=True, proxies=proxies)
                else:
                    logger.error("No proxies defined")
            except Exception as e:
                logger.error("Error downloading update file: %s" % str(e))
        if data.status_code == 200:
            logger.debug(f"Writing contents to {path_file_download}")
            with open(path_file_download, "wb") as f:
                for chunk in data.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        else:
            logger.error(f"Failed to download {urlpath}: Error {data.status_code}")
        typename = os.path.splitext(path_file_download)[1][1:]
        file_conf_json = os.path.join(os.path.dirname(path_file_download), "conf.json")
        file_xmppdeploy_json = os.path.join(
            os.path.dirname(path_file_download), "xmppdeploy.json"
        )
        nameexecution = os.path.basename(path_file_download)
        logger.debug(f"Generating {file_conf_json}")
        with open(file_conf_json, "w") as outfile:
            outfile.write(
                self.generate_conf_json(title, updateid, description, urlpath)
            )
        logger.debug(f"Generating {file_xmppdeploy_json}")
        with open(file_xmppdeploy_json, "w") as outfile:
            outfile.write(
                self.generate_xmppdeploy_json(
                    title, updateid, description, typename, nameexecution, urlpath
                )
            )

        # logger.debug (self.generate_xmppdeploy_json(title, updateid, title, typename, nameexecution, urlpath))
        # generation
        # Path(dirpackage).write_bytes(data)
        end = datetime.now()
        return end - start

    def generate_xmppdeploy_json(
        self, name, id, description, typename, namefile, urlpath
    ):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        if typename == "cab":
            cmd = (
                """dism /Online /Add-Package /PackagePath:"@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" /NoRestart"""
                % (namefile)
            )
        elif "kb890830" in namefile:
            cmd = (
                """copy /y "@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" C:\Windows\System32\MRT.exe"""
                % (namefile)
            )
        else:
            cmd = """Start /wait "@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" """ % (
                namefile
            )
        cmd64 = base64.b64encode(bytes(cmd, "utf-8"))
        return """{
        "info": {
            "urlpath" : "%s",
            "creator": "automate_medulla",
            "creation_date": "%s",
            "licenses": "1.0",
            "gotoreturncode": "3010",
            "gotolabel": "REBOOTREQUIRED",
            "packageUuid": "%s",
            "spooling": "ordinary",
            "limit_rate_ko": "",
            "version": "0.1",
            "editor": "automate_medulla",
            "metagenerator": "expert",
            "targetrestart": "MA",
            "inventory": "noforced",
            "localisation_server": "global",
            "typescript": "Batch",
            "description": "%s",
            "previous_localisation_server": "global",
            "Dependency": [],
            "name": "%s",
            "url": "",
            "edition_date": "%s",
            "transferfile": true,
            "methodetransfert": "pushrsync",
            "software": "templated",
            "type_section" : "update"
        },
        "win": {
            "sequence": [
                {
                    "action": "action_section_update", 
                    "step": 0, 
                    "actionlabel": "upd_70a70cc9"
                }, 
                {
                    "typescript": "Batch",
                    "script": "%s",
                    "30@lastlines": "30@lastlines",
                    "actionlabel": "02d57e96",
                    "codereturn": "",
                    "step": 1,
                    "error": 6,
                    "action": "actionprocessscriptfile",
                    "timeout": "3600",
                    "gotoreturncode@3010": "REBOOTREQUIRED"
                },
                {
                    "action": "actionwaitandgoto",
                    "step": 2,
                    "codereturn": "",
                    "actionlabel": "wait_cc66c870",
                    "waiting": "1",
                    "goto": "END_SUCCESS"
                },
                {
                    "step": 3,
                    "action": "action_comment",
                    "actionlabel": "REBOOTREQUIRED",
                    "comment": "The update has been installed but a reboot is required to apply it."
                },
                {
                    "action": "action_notification",
                    "step": 4,
                    "codereturn": "",
                    "actionlabel": "notif_ee9943f2",
                    "titlemessage": "V2luZG93cyBVcGRhdGUgLSBSZWJvb3Q=",
                    "sizeheader": "15",
                    "message": "QW4gdXBkYXRlIGhhcyBiZWVuIGluc3RhbGxlZCBvbiB5b3VyIGNvbXB1dGVyIGJ5IE1lZHVsbGEuIFBsZWFzZSByZWJvb3Qgd2hlbiBwb3NzaWJsZSB0byBhcHBseSB0aGUgdXBkYXRlLg0KDQpVbmUgbWlzZSDDoCBqb3VyIGEgw6l0w6kgaW5zdGFsbMOpZSBzdXIgdm90cmUgb3JkaW5hdGV1ciBwYXIgTWVkdWxsYS4gUGVuc2V6IMOgIHJlZMOpbWFycmVyIHF1YW5kIGMnZXN0IHBvc3NpYmxlIGFmaW4gcXVlIGxhIG1pc2Ugw6Agam91ciBzb2l0IGFwcGxpcXXDqWUu",
                    "sizemessage": "10",
                    "textbuttonyes": "OK",
                    "timeout": "800"
                },
                {
                    "action": "actionsuccescompletedend",
                    "step": 5,
                    "actionlabel": "END_SUCCESS",
                    "clear": "False",
                    "inventory": "noforced"
                },
                {
                    "action": "actionerrorcompletedend",
                    "step": 6,
                    "actionlabel": "END_ERROR"
                }
            ]
        },
        "metaparameter": {
            "win": {
                "label": {
                    "upd_70a70cc9": 0,
                    "02d57e96": 1,
                    "wait_cc66c870": 2,
                    "REBOOTREQUIRED": 3,
                    "notif_ee9943f2": 4,    
                    "END_SUCCESS": 5,
                    "END_ERROR": 6
                }
            },
            "os": [
                "win"
            ]
        }
    }""" % (
            urlpath,
            dt_string,
            id,
            description,
            name,
            dt_string,
            cmd64.decode("utf-8"),
        )

    def generate_conf_json(self, name, id, description, urlpath):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        return """{
            "urlpath" : "%s",
            "localisation_server": "global",
            "sub_packages": [],
            "metagenerator": "manual",
            "description": "%s",
            "creator": "root",
            "edition_date": "",
            "previous_localisation_server": "global",
            "entity_id": "0",
            "creation_date": "%s",
            "inventory": {
                "associateinventory": "0",
                "licenses": "",
                "queries": {
                    "Qsoftware": "",
                    "Qvendor": "",
                    "boolcnd": "",
                    "Qversion": ""
                }
            },
            "version": "0.1",
            "reboot": 0,
            "editor": "",
            "targetos": "win",
            "commands": {
                "postCommandSuccess": {
                    "command": "",
                    "name": ""
                },
                "command": {
                    "command": "",
                    "name": ""
                },
                "postCommandFailure": {
                    "command": "",
                    "name": ""
                },
                "installInit": {
                    "command": "",
                    "name": ""
                },
                "preCommand": {
                    "command": "",
                    "name": ""
                }
            },
            "id": "%s",
            "name": "%s"
        }""" % (
            urlpath,
            description,
            dt_string,
            id,
            name,
        )


def simplecommand(cmd):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj = {"code": p.wait()}
    obj["result"] = result
    return obj


def simplecommandstr(cmd):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj = {"code": p.wait()}
    obj["result"] = "\n".join(result)
    return obj


if __name__ == "__main__":
    # Quit the process if we don't want to continue
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    parser = OptionParser()
    parser.add_option(
        "-H", "--host", dest="hostname", default="localhost", help="hostname SGBD"
    )

    parser.add_option("-P", "--port", dest="port", default=3306, help="port_decreation")

    parser.add_option("-u", "--user", dest="user", default="root", help="user compter")
    parser.add_option(
        "-B", "--base", dest="base", default="xmppmaster", help="base sql name"
    )

    parser.add_option(
        "-p", "--password", dest="password", default="", help="password connection"
    )

    parser.add_option(
        "-t",
        "--testconnect",
        action="store_true",
        dest="testconnect",
        default=False,
        help="test connection et quitte",
    )

    parser.add_option(
        "-T", "--tablename", dest="table_name", default="", help="name table des update"
    )

    parser.add_option(
        "-o",
        "--outputdir",
        dest="outputdir",
        default="/var/lib/pulse2/packages/sharing/",
        help="path directory generation package",
    )

    parser.add_option(
        "-l",
        "--logfile",
        dest="logfile",
        default="/var/log/mmc/medulla-generate-update-package.log",
        help="file de configuration",
    )

    parser.add_option(
        "-d",
        "--debug",
        dest="debugmode",
        action="store_true",
        default=False,
        help="ecrit reference in code",
    )

    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="don't print status messages to stdout",
    )

    parser.add_option(
        "-i",
        "--info_parametre",
        action="store_true",
        dest="show_parametre",
        default=False,
        help="display tout les parametres",
    )

    (opts, args) = parser.parse_args()

    try:
        if not os.path.exists(opts.logfile):
            if not os.path.isdir(os.path.dirname(opts.logfile)):
                os.makedirs(os.path.abspath(os.path.dirname(opts.logfile)))
            open(opts.logfile, "w").close()
    except Exception as e:
        errorstr = f"{traceback.format_exc()}"
        print("\n%s" % (errorstr))
        sys.exit(1)

    if not opts.testconnect and opts.table_name == "":
        print("table parametre missing")
        if not opts.show_parametre:
            sys.exit(1)

    if opts.outputdir == "/var/lib/pulse2/packages/sharing/":
        opts.outputdir = os.path.join(opts.outputdir, opts.table_name)

    file_handler = logging.FileHandler(filename=opts.logfile)

    if opts.verbose:
        handlers = [file_handler]
    else:
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]

    if opts.show_parametre:
        print("Option actuelle")
        print(opts)
        print("exemples")
        print("command information\n")
        print("\t affiche cette info")
        print("\t\tpython3 ./medulla-generate-update-package.py -d  -q -i\n")
        print("\n\t test connection\n")
        print(
            "\t\tpython3 ./medulla-generate-update-package.py -uroot -P 3306 -Hlocalhost -p siveo -q -t"
        )
        print("2022-10-19 14:20:54,179 - INFO - try Connecting with parameters")
        print("\thost: localhost")
        print("\tuser: root")
        print("\tport: 3306")
        print("\tdb: xmppmaster\n")
        print("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS\n")
        print("\t test connection format debug")
        print(
            "\t\tpython3 ./medulla-generate-update-package.py -uroot -P 3306 -Hlocalhost -p siveo -q -t -d"
        )
        print(
            "[2022-10-19 14:21:23,587] {medulla-generate-update-package.py:444} INFO - try Connecting with parameters"
        )
        print("\thost: localhost")
        print("\tuser: root")
        print("\tport: 3306")
        print("\tdb: xmppmaster\n")
        print("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS\n")
        print(
            "\t Creation des packages depuis la table xmppmaster.up_packages_Win10_X64_21H2"
        )
        print(
            "\t dans repertoire /var/lib/pulse2/packages/sharing/up_packages_Win10_X64_21H2"
        )
        print(
            "\t\tpython3 ./medulla-generate-update-package.py -p siveo -Tup_packages_Win10_X64_21H2 -o/var/lib/pulse2/packages/sharing/packages_Win10_X64_21H2 -q -d"
        )
        sys.exit(1)

    level = logging.INFO
    format = "%(asctime)s - %(levelname)s - %(message)s"
    if opts.debugmode:
        format = "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
        level = logging.DEBUG

    logging.basicConfig(level=level, format=format, handlers=handlers)

    logger = logging.getLogger()

    Passwordbase = ""
    if opts.password != "":
        Passwordbase = opts.password
    else:
        print("key password input ????")
        Passwordbase = getpass.getpass(
            prompt=f"Password for mysql://{opts.user}:<password>@{opts.hostname}:{opts.port}/{opts.base}",
            stream=None,
        )
    if Passwordbase == "":
        print("Connecting parameters password missing")
        sys.exit(1)

    if opts.testconnect:
        logger.info(
            "try Connecting with parameters\n"
            "\thost: %s\n"
            "\tuser: %s\n"
            "\tport: %s\n"
            "\tdb: %s\n" % (opts.hostname, opts.user, int(opts.port), opts.base)
        )
        try:
            db = MySQLdb.connect(
                host=opts.hostname,
                user=opts.user,
                passwd=Passwordbase,
                port=int(opts.port),
                db=opts.base,
            )
            print("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS")
        except Exception as e:
            errorstr = f"{traceback.format_exc()}"
            print("\n%s" % (errorstr))
        finally:
            db.close()
            sys.exit(1)
    try:
        db = MySQLdb.connect(
            host=opts.hostname,
            user=opts.user,
            passwd=Passwordbase,
            port=int(opts.port),
            db=opts.base,
        )
        logger.debug("CONNECT SUCCESS")

        logger.debug("Genere les packages")
        generateur = download_packages(
            db, opts.table_name, opts.outputdir
        ).url_to_download()

    except Exception as e:
        errorstr = f"{traceback.format_exc()}"
        print("ERROR CONNECTION")
        print("\n%s" % (errorstr))
        logger.error("\n%s" % (errorstr))
        sys.exit(1)
    finally:
        db.close()
