#!/usr/bin/python3
# -*- coding:utf-8 -*-
# SPDX-FileCopyrightText: 2022-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-2.0-or-later

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

#from  MySQLdb import IntegrityError
# Global Variables

logger = logging.getLogger()

# connection xmppmaster

class download_packages:
    def __init__(self, db, name_table_produit, outputdir):
        self.db = db
        self.name_table_produit = name_table_produit
        self.directory_output_package  = outputdir

    def  url_to_download(self):
        try:
            os.makedirs(self.directory_output_package)
            logger.debug("Directory '%s' created successfully" %self.directory_output_package)
        except OSError as error:
            logger.debug("Directory '%s' can not be created" % self.directory_output_package)

        sql=""" SELECT title, payloadfiles,updateid, kb, description  FROM xmppmaster.%s;""" % self.name_table_produit

        cursor = self.db.cursor()
        record = cursor.execute(sql)
        for i in cursor.fetchall():
            dirpackage = os.path.join(self.directory_output_package, i[2])
            self.download_url(i[1], dirpackage, i[2] , i[3], i[0], i[4])
        cursor.close()

    def download_url(self, urlpath, dirpackage, updateid, kb, title, description):
        logger.debug("download %s" % urlpath)
        start = datetime.now()
        #logger.debug ("download", urlpath, dirpackage )
        namefile = urlpath.split("/")[-1]
        path_file_download = os.path.join(dirpackage, namefile)
        #logger.debug("path_file_download %s " % path_file_download)
        if os.path.isfile(path_file_download):
            logger.debug("package existe %s" % path_file_download)
            end = datetime.now()
            total_elapsed_time = end - start
            return total_elapsed_time
        try:
            os.makedirs(dirpackage)
            logger.debug("Directory '%s' created successfully" % path_file_download)
        except OSError as error:
            logger.debug("Directory %s can not be created" % path_file_download)
        data = requests.get(urlpath, stream=True)
        with  open(path_file_download, 'wb') as f:
            for chunk in data.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        typename = os.path.splitext(path_file_download)[1][1:]
        file_conf_json = os.path.join(os.path.dirname(path_file_download), "conf.json")
        file_xmppdeploy_json = os.path.join(os.path.dirname(path_file_download), "xmppdeploy.json")
        nameexecution = os.path.basename(path_file_download)
        #logger.debug(file_conf_json)
        #logger.debug(file_xmppdeploy_json)
        #logger.debug (generate_conf_json(title, updateid, title))

        with open(file_conf_json, 'w') as outfile:
            outfile.write(self.generate_conf_json(title, updateid, description,urlpath))

        with open(file_xmppdeploy_json, 'w') as outfile:
            outfile.write(self.generate_xmppdeploy_json(title, updateid, description, typename, nameexecution, urlpath))

        # logger.debug (self.generate_xmppdeploy_json(title, updateid, title, typename, nameexecution, urlpath))
        # generation
        #Path(dirpackage).write_bytes(data)
        end = datetime.now()
        total_elapsed_time = end - start
        return total_elapsed_time


    def generate_xmppdeploy_json(self, name, id, description, typename, namefile, urlpath):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        if typename == "cab":
            cmd="""dism /Online /Add-Package /PackagePath:"@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" /NoRestart"""%(namefile)
        elif "kb890830" in namefile:
            cmd="""copy /y "@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" C:\Windows\System32\MRT.exe"""%(namefile)
        else:
            cmd="""Start /wait "@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" """%(namefile)
        cmd64=base64.b64encode(bytes(cmd,"utf-8"))
        template="""{
        "info": {
            "urlpath" : "%s",
            "creator": "automate_medulla",
            "creation_date": "%s",
            "licenses": "1.0",
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
                    "error": 3,
                    "action": "actionprocessscriptfile",
                    "timeout": "3600"
                },
                {
                    "action": "actionsuccescompletedend",
                    "step": 2,
                    "actionlabel": "END_SUCCESS",
                    "clear": "False",
                    "inventory": "noforced"
                },
                {
                    "action": "actionerrorcompletedend",
                    "step": 3,
                    "actionlabel": "END_ERROR"
                }
            ]
        },
        "metaparameter": {
            "win": {
                "label": {
                    "END_SUCCESS": 2,
                    "END_ERROR": 3,
                    "upd_70a70cc9": 0,
                    "02d57e96": 1
                }
            },
            "os": [
                "win"
            ]
        }
    }"""%(urlpath, dt_string,id,  description, name, dt_string, cmd64.decode("utf-8") )
        return template


    def generate_conf_json(self, name, id, description, urlpath):
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        template="""{
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
        }"""%(urlpath, description,dt_string,id, name)
        return template


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


if __name__ == "__main__":

    # Quit the process if we don't want to continue
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    parser = OptionParser()
    parser.add_option("-H", "--host",
                    dest="hostname", default = "localhost",
                    help="hostname SGBD")

    parser.add_option("-P", "--port",
                    dest="port", default = 3306,
                    help="port_decreation")

    parser.add_option("-u", "--user",
                    dest="user", default = "root",
                    help="user compter")
    parser.add_option("-B", "--base",
                    dest="base", default = "xmppmaster",
                    help="base sql name")

    parser.add_option("-p", "--password",
                    dest="password", default = "",
                    help="password connection")

    parser.add_option("-t", "--testconnect", action="store_true",
                    dest="testconnect", default=False,
                    help="test connection et quitte")

    parser.add_option("-T", "--tablename", dest="table_name", default="",
                    help="name table des update")

    parser.add_option("-o", "--outputdir", dest="outputdir",
                      default="/var/lib/pulse2/packages/sharing/",
                      help="path directory generation package")

    parser.add_option("-l", "--logfile", dest="logfile",
                      default="/var/log/mmc/medulla-generate-update-package.log",
                      help="file de configuration")

    parser.add_option("-d", "--debug", dest="debugmode",action="store_true",
                      default=False,
                      help="ecrit reference in code")

    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")

    parser.add_option("-i", "--info_parametre",
                    action="store_true", dest="show_parametre", default=False,
                    help="display tout les parametres")

    (opts, args) = parser.parse_args()

    try:
        if not os.path.exists(opts.logfile):
            if not os.path.isdir(os.path.dirname(opts.logfile)):
                os.makedirs(os.path.abspath(os.path.dirname(opts.logfile)))
            open(opts.logfile,"w").close()
    except Exception as e:
        errorstr = "%s" % traceback.format_exc()
        print("\n%s" % (errorstr))
        sys.exit(1)

    if  not opts.testconnect and opts.table_name  == "":
        print("table parametre missing")
        if not opts.show_parametre:
            sys.exit(1)

    if opts.outputdir == "/var/lib/pulse2/packages/sharing/":
        opts.outputdir=os.path.join(opts.outputdir, opts.table_name)

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
        print ("command information\n")
        print ("\t affiche cette info")
        print ("\t\tpython3 ./medulla-generate-update-package.py -d  -q -i\n")
        print ("\n\t test connection\n")
        print ("\t\tpython3 ./medulla-generate-update-package.py -uroot -P 3306 -Hlocalhost -p siveo -q -t")
        print ("2022-10-19 14:20:54,179 - INFO - try Connecting with parameters")
        print ("\thost: localhost")
        print ("\tuser: root")
        print ("\tport: 3306")
        print ("\tdb: xmppmaster\n")
        print ("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS\n")
        print ("\t test connection format debug")
        print ("\t\tpython3 ./medulla-generate-update-package.py -uroot -P 3306 -Hlocalhost -p siveo -q -t -d")
        print ("[2022-10-19 14:21:23,587] {medulla-generate-update-package.py:444} INFO - try Connecting with parameters")
        print ("\thost: localhost")
        print ("\tuser: root")
        print ("\tport: 3306")
        print ("\tdb: xmppmaster\n")
        print ("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS\n")
        print ("\t Creation des packages depuis la table xmppmaster.up_packages_Win10_X64_21H2")
        print ("\t dans repertoire /var/lib/pulse2/packages/sharing/up_packages_Win10_X64_21H2")
        print ("\t\tpython3 ./medulla-generate-update-package.py -p siveo -Tup_packages_Win10_X64_21H2 -o/var/lib/pulse2/packages/sharing/packages_Win10_X64_21H2 -q -d" )
        sys.exit(1)

    format = "%(asctime)s - %(levelname)s - %(message)s"
    level = logging.INFO
    if opts.debugmode:
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format=format,
        handlers=handlers
    )

    logger = logging.getLogger()

    Passwordbase = ""
    if opts.password != "":
        Passwordbase = opts.password
    else:
        print("key password input ????")
        Passwordbase = getpass.getpass(prompt='Password for mysql://' \
                                       '%s:<password>@%s:%s/%s'%(opts.user,
                                                                 opts.hostname,
                                                                 opts.port,
                                                                 opts.base),
                                       stream=None)
    if Passwordbase == "":
        print("Connecting parameters password missing")
        sys.exit(1)

    if opts.testconnect:
        logger.info("try Connecting with parameters\n" \
                        "\thost: %s\n" \
                        "\tuser: %s\n" \
                        "\tport: %s\n" \
                        "\tdb: %s\n" %( opts.hostname,
                                        opts.user,
                                        int(opts.port),
                                        opts.base))
        try:
            db = MySQLdb.connect(host=opts.hostname,
                                user=opts.user,
                                passwd=Passwordbase,
                                port = int(opts.port),
                                db=opts.base)
            print("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS")
        except Exception as e:
            errorstr = "%s" % traceback.format_exc()
            print("\n%s" % (errorstr))
        finally:
            db.close()
            sys.exit(1)
    try:
        db = MySQLdb.connect(host=opts.hostname,
                            user=opts.user,
                            passwd=Passwordbase,
                            port = int(opts.port),
                            db=opts.base)
        logger.debug("CONNECT SUCCESS")

        logger.debug("Genere les packages")
        generateur = download_packages(db, opts.table_name, opts.outputdir ).url_to_download()

    except Exception as e:
        errorstr = "%s" % traceback.format_exc()
        print ("ERROR CONNECTION")
        print ("\n%s" % (errorstr))
        logger.error("\n%s" % (errorstr))
        sys.exit(1)
    finally:
        db.close()
