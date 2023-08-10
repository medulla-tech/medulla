#!/usr/bin/python3
# -*- coding:utf-8 -*-
# SPDX-FileCopyrightText: 2022-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

# This script is used to generate update packages in /var/lib/pulse2/packages

from datetime import datetime
import re
import requests
import subprocess
import sys, os
import signal
import logging
import traceback
import MySQLdb
import base64
import getpass
import json
from optparse import OptionParser
import shutil
#from  MySQLdb import IntegrityError
# Global Variables

logger = logging.getLogger()

class synch_packages:
    def __init__(self, db, opts ):
        self.db = db
        self.param=opts
        #logger.info("File parmetre %s" % self.param)
        self.update_file_windows={}
        self.path_base = os.path.join("/", "var", "lib", "pulse2",
                                             "base_update_package")
        if not os.path.exists(self.path_base):
            try:
                os.makedirs(self.path_base)
            except OSError as e:
                logger.error("%s create directory share'%s'" %(str(e),
                                                            self.path_base))

        self.sharing=  os.path.join("/", "var", "lib", "pulse2",
                                             "packages","sharing")
        self.dirpartageupdate = os.path.join(self.sharing, self.param['partage'] )
        self.path_in_partage=os.path.join(self.dirpartageupdate,self.param['uidpackage'])
        self.path_in_base=os.path.join(self.path_base, self.param['uidpackage'])
        self.packagelist=self.search_list_package()
        if self.param['uidpackage'] in self.packagelist:
            package_install=True
        else:
            package_install=False

        if self.param['forcedelpackage']:
            logger.info("completely remove the package %s" % self.param['uidpackage'])
            self.uninstall_full_package()

        elif self.param['delpackage']:
            logger.info("uninstall package %s but don't remove it" % self.param['uidpackage'])
            self.mv_partage_to_base()
            # supprime le package de la base
            self.del_package_pkgs()
            return
        elif self.param['forcecreatepackage']:
            logger.info("create or completely create the package and install it %s" % self.param['uidpackage'])
            self.uninstall_full_package()
            self.install_full_package()
        elif self.param['createpackage']:
            logger.info("install package if not install %s" % self.param['uidpackage'])
            self.install_full_package()

    def install_full_package(self):
        if self.create_package_file():
            self.mv_base_to_partage()
            self.install_package()
        self.verify_packages_install()

    def uninstall_full_package(self):
         # supprime de la base fichier
        self.del_package()
        # suprime le lien symbolique
        #self.mv_partage_to_base()
        # supprime le package de la base
        self.del_package_pkgs()
        self.verify_packages_uninstall()

    def create_directory_in_partage(self):
        logger.debug("function create_directory_in_partage")
        logger.debug("package create directory '%s'" %(self.path_in_partage))
        if not os.path.exists(self.path_in_partage):
            try:
                os.makedirs(self.path_in_partage)
            except OSError as e:
                logger.error("%s : create_directory '%s'" %(str(e),
                                                            self.path_in_partage))

    def create_directory_in_base(self):
        logger.debug("function create_directory_in_base")
        logger.debug("package create directory '%s'" %(self.path_in_base))
        if not os.path.exists(self.path_in_base):
            try:
                os.makedirs(self.path_in_base)
            except OSError as e:
                logger.error("%s : create_directory '%s'" %(str(e),
                                                            self.path_in_base))
    def mv_base_to_partage(self):
        # mv base vers partages
        logger.debug("function mv_base_to_partage")
        if os.path.isdir(self.path_in_base):
            logger.debug("function make transfert %s to %s"%(self.path_in_base ,self.path_in_partage))
            file_names = os.listdir(self.path_in_base)
            self.create_directory_in_partage()
            for file_name in file_names:
                shutil.move(os.path.join(self.path_in_base, file_name), self.path_in_partage)
                logger.debug("move %s to %s"%(os.path.join(self.path_in_base, file_name),
                                              self.path_in_partage))
            logger.debug("del  %s"%self.path_in_base)
            shutil.rmtree(self.path_in_base)

    def mv_partage_to_base(self):
        # mv de partages vers base
        # mv_partage_to_base
        logger.debug("function mv_partage_to_base")
        if os.path.isdir(self.path_in_partage):
            logger.debug("function make transfert %s to %s"%(self.path_in_partage, self.path_in_base))
            file_names = os.listdir(self.path_in_partage)
            self.create_directory_in_base()
            for file_name in file_names:
                shutil.move(os.path.join(self.path_in_partage, file_name), self.path_in_base)
            shutil.rmtree(self.path_in_partage)

    def del_package(self):
        """
            supprime completement les fichiers du package de la base fichier
        """
        logger.debug("function del_package")
        logger.debug("del package '%s'" %( self.path_in_base))
        if os.path.isdir(self.path_in_base):
            try:
                shutil.rmtree(self.path_in_base)
                logger.debug("delete directory '%s'" % self.path_in_base)
            except Exception as e:
                logger.error("%s : del_package '%s'" %(str(e), self.path_in_base))
        else:
            logger.debug("directory '%s' is not exit" % self.path_in_base)


        if os.path.isdir(self.path_in_partage):
            try:
                shutil.rmtree(self.path_in_partage)
                logger.debug("delete directory '%s'" % self.path_in_partage)
            except Exception as e:
                logger.error("%s : del_package '%s'" %(str(e), self.path_in_partage))
        else:
            logger.debug("directory '%s' is not exit" % self.path_in_partage)

    def del_package_pkgs(self):
        """
            supprime completement les fichiers du package de la base
        """
        logger.debug("function del_package_pkgs")
        try:
            sql="""DELETE
                        FROM `pkgs`.`packages`
                    WHERE
                        (`uuid` = '%s');""" % self.param['uidpackage']
            logger.debug("sql %s"%(sql))
            cursor = self.db.cursor()
            result=cursor.execute(sql)
            self.db.commit()
            if result:
                logger.debug("the package [%s] is uninstalled"%self.param['uidpackage'])
            else:
                logger.debug("the package [%s] is not installed"%self.param['uidpackage'])
        except Exception as e:
            logger.error("%s : del_package_pkgs '%s'" %(str(e), self.param['uidpackage']))

    def verify_packages_install(self):
        logger.debug("verify packages install %s" % (self.path_in_partage))
        if os.path.isdir(self.path_in_partage):
            ff = os.listdir(self.path_in_partage)
            if len(ff) >= 3:
                logger.debug("the package %s was successfully created" % (self.param['uidpackage']))
            else:
                logger.error("package %s exists but is incomplete" % (self.param['uidpackage']))
                return False
        else:
            logger.error("package file %s does not exist" % (self.param['uidpackage']))
            return False

        if self.check_in_base():
            logger.debug("package %s is installed in pkgs" % (self.param['uidpackage']))
        else:
            logger.error("the package %s is not installed in pkgs" % (self.param['uidpackage']))
            return False
        logger.info("package %s is successfully installed" % (self.param['uidpackage']))
        return True

    def verify_packages_uninstall(self):
        logger.debug("verify packages uninstall %s" % (self.path_in_partage))
        if os.path.isdir(self.path_in_base):
            logger.error("the %s package files still exist" % (self.param['uidpackage']))
            return False
        else:
            logger.debug("package %s no longer exists" % (self.param['uidpackage']))

        if os.path.isdir(self.path_in_base):
            logger.error("the %s package files still exist" % (self.param['uidpackage']))
            return False
        else:
            logger.debug("package %s no longer exists" % (self.param['uidpackage']))
        if self.check_in_base():
            logger.debug("package %s is still installed in pkgs" % (self.param['uidpackage']))
            return False
        else:
            logger.debug("uninstalled package %s in pkgs" % (self.param['uidpackage']))
        logger.info("correct uninstalled package %s" % (self.param['uidpackage']))
        return True


#dans /var/lib/pulse2/packages/sharing/winupdates
#ln -s /var/lib/pulse2/base_update_package/fcc60465-497b-4395-b714-4699cef797ca fcc60465-497b-4395-b714-4699cef797ca

    def search_list_package(self):
        """
            list tout les packages in le partages
        """
        logger.debug("function search_list_package")
        packagelist = [f for f in os.listdir(self.dirpartageupdate) if uuid_validate(f)]
        return packagelist

    def search_file_update(self):
        logger.debug("function search_file_update")
        self.update_file_windows={}
        sql="""SELECT
                    updateid, kb, revisionid, title, description
                FROM
                    xmppmaster.%s
                WHERE
                    updateid = '%s' limit 1;""" % (self.param['nametable'], self.param['uidpackage'])
        logger.debug("sql %s"%(sql))
        cursor = self.db.cursor()
        record = cursor.execute(sql)
        for i in cursor.fetchall():
            self.update_file_windows['updateid']=i[0]
            self.update_file_windows['kb']=i[1]
            self.update_file_windows['revisionid']=i[2]
            self.update_file_windows['title']=i[3]
            self.update_file_windows['description']=i[4]
        if self.update_file_windows:
            sql="""SELECT
                    updateid, payloadfiles, supersededby,creationdate,title_short
                FROM
                    xmppmaster.%s
                WHERE
                    payloadfiles NOT IN ('')
                        AND supersededby LIKE "%s" limit 1;"""  % (self.param['nametable'],self.update_file_windows['revisionid'])
            logger.debug("sql %s"%(sql))
            record = cursor.execute(sql)
            for i in cursor.fetchall():
                self.update_file_windows['updateid_payloadfiles']=i[0]
                self.update_file_windows['payloadfiles']=i[1]
                self.update_file_windows['supersededby']=i[2]
                self.update_file_windows['creationdate']=i[3]
                self.update_file_windows['title_short']=i[4]
            logger.debug("update_file_windows complet %s "%self.update_file_windows)
        return self.update_file_windows

    def create_package_file(self):
        """
            download file from url urlpath in directory
        """
        logger.debug("function create_package_file")
        logger.debug("function create_package_file %s" %self.path_in_base)
        if os.path.isdir(self.path_in_base):
            ff = os.listdir(self.path_in_base)
            if len(ff) >=3:
                logger.debug("package exists %s already" % (self.param['uidpackage']))
                return True
        elif os.path.isdir(self.path_in_partage):
            ff = os.listdir(self.path_in_partage)
            if len(ff) >=3:
                logger.debug("package exists %s already" % (self.param['uidpackage']))
                return True
        #logger.debug("download %s" % urlpath)
        #start = datetime.now()
        # search url file update
        if not self.search_file_update():
            logger.error("not find update file to download for %s" % (self.param['uidpackage']))
            return False

        # test si url exist
        if self.update_file_windows and \
            'payloadfiles' in  self.update_file_windows and \
                self.update_file_windows['payloadfiles'] != "":
            # 1 url trouver on fabrique le package
            logger.debug("url update file windows package %s is %s" % (self.param['uidpackage'],
                                                                self.update_file_windows['payloadfiles']))
            namefile = self.update_file_windows['payloadfiles'].split("/")[-1]
            path_file_download = os.path.join(self.path_in_base, namefile)
            # creation repertoire du package si non exist
            self.create_directory_in_base()
            data = requests.get(self.update_file_windows['payloadfiles'], stream=True)
            with  open(path_file_download, 'wb') as f:
                for chunk in data.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            typename = os.path.splitext(path_file_download)[1][1:]
            file_conf_json = os.path.join(self.path_in_base, "conf.json")
            file_xmppdeploy_json = os.path.join(self.path_in_base, "xmppdeploy.json")
            nameexecution = os.path.basename(path_file_download)


            with open(file_conf_json, 'w') as outfile:
                outfile.write(self.generate_conf_json(self.update_file_windows['title'],
                                                      self.update_file_windows['updateid'],
                                                      self.update_file_windows['description'],
                                                      self.update_file_windows['payloadfiles']))

            with open(file_xmppdeploy_json, 'w') as outfile:
                outfile.write(self.generate_xmppdeploy_json(self.update_file_windows['title'],
                                                            self.update_file_windows['updateid'],
                                                            self.update_file_windows['description'],
                                                            typename,
                                                            nameexecution,
                                                            self.update_file_windows['payloadfiles'],
                                                            self.update_file_windows['kb'],
                                                            self.update_file_windows['creationdate']))
        else:
            # terminer avec erreur
            logger.error("create package %s" % (self.param['uidpackage']))
        #end = datetime.now()
        #total_elapsed_time = end - start
        return True

    def loadjsonfile(self,filename):
        """
        This function is used to load a json file
        Args:
            filename: The filename of the json file to load
        Returns:
            It returns the content of the JSON file
        """

        if os.path.isfile(filename):
            try:
                with open(filename,'r') as info:
                    outputJSONFile=json.load(info)
                return outputJSONFile
            except Exception as e:
                logger.error("We failed to decode the file %s" % filename)
                logger.error("we encountered the error: %s" % str(e))
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
        return None



    def generate_xmppdeploy_json(self, name, id, description, typename, namefile, urlpath, kb, date_edition_windows_update):
        logger.debug("function generate_xmppdeploy_json")
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
            "meta_update_kb" : "%s",
            "meta_update_date_edition_windows_update" : "%s",
            "urlpath" : "%s",
            "creator": "automate_medulla",
            "edition": "automate_medulla",
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
            "localisation_server": "%s",
            "typescript": "Batch",
            "description": "%s",
            "previous_localisation_server": "%s",
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
    }"""%(kb, date_edition_windows_update, urlpath, dt_string,id, self.param['partage'],
          description, self.param['partage'],name, dt_string, cmd64.decode("utf-8"))
        return template


    def id_partage(self):
        logger.debug("function id_partage")
        self.partage_id=None
        sql="""SELECT
                id
            FROM
                pkgs.pkgs_shares
            WHERE
                name = '%s' limit 1;"""%self.param['partage']
        logger.debug("sql %s" % sql)
        cursor = self.db.cursor()
        record = cursor.execute(sql)
        for i in cursor.fetchall():
            self.partage_id=i[0]
        if self.partage_id:
            logger.debug("ID partage is  %s" % self.partage_id)
            return self.partage_id
        else:
            # creation partage
            sql="""INSERT INTO `pkgs`.`pkgs_shares` (`name`, `comments`,
                                                    `enabled`, `type`,
                                                    `uri`, `ars_name`,
                                                    `ars_id`, `share_path`,
                                                    `usedquotas`, `quotas`) VALUES ('%s', 'partage update', '1', 'update', 'pulse', 'pulse', '1', '%s', '0', '0');""" %(self.param['partage'], self.dirpartageupdate)
            logger.debug("sql %s" % sql)
            try:
                logger.debug("creation partage %s %s" % self.param['partage'])
                cursor = self.db.cursor()
                cursor.execute(sql)
                self.partage_id = cursor.lastrowid
                self.db.commit()
                logger.debug("ID partage is  %s" % self.partage_id)
                return self.partage_id
            except MySQLdb.Error as e:
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
                logger.error("%s : id_partage '%s'" %(str(e)))
                self.partage_id=None
            except Exception as e:
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
                self.partage_id=None
            finally:
                cursor.close()
        return None


    def check_in_base(self):
        logger.debug("function check_in_base")
        sql="""SELECT
                id
            FROM
                pkgs.packages
            WHERE
                uuid = '%s' limit 1;"""%self.param['uidpackage']
        logger.debug("sql %s" % sql)
        cursor = self.db.cursor()
        record = cursor.execute(sql)
        for i in cursor.fetchall():
            logger.debug("check_in_base TRUE")
            return True
        logger.debug("package non installer in pkgs")
        return False

    def install_package(self):
        try:
            logger.debug("function install_package")
            # search id_partage winupdates
            if self.check_in_base():
                return
            self.id_partage()
            if not self.partage_id:
                return
            if os.path.isdir(self.path_in_base):
                dirpackage = self.path_in_base
            else:
                dirpackage = self.path_in_partage


            logger.debug("1")
            file_xmppdeploy_json = os.path.join(dirpackage, "conf.json")
            contenuedejson = self.loadjsonfile(file_xmppdeploy_json)
            logger.debug("3")
            if contenuedejson is None:
                # erreur d'installation package
                logger.error("decodage json conf.json erreur")
                return False
            logger.debug("4")
            if not('localisation_server' in contenuedejson and contenuedejson['localisation_server'] != "") :
                contenuedejson['localisation_server'] = self.param['partage']
                contenuedejson['previous_localisation_server'] = self.param['partage']

            #if not ("creator" in contenuedejson and contenuedejson['creator'] != "") :
                #contenuedejson['creator'] = "root"

            #if not ("edition" in contenuedejson  and contenuedejson['edition'] != "") :
                #contenuedejson['edition'] = "root"

            if not "creation_date" in contenuedejson or\
                    contenuedejson['creation_date'] == "" :
                contenuedejson['creation_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not "edition_date" in contenuedejson or\
                    contenuedejson['edition_date'] == "" :
                contenuedejson['edition_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'metagenerator' not in contenuedejson:
                contenuedejson['metagenerator'] = "expert"

            edition_status = 1
            if contenuedejson['metagenerator'] == "manual":
                edition_status = 0

            ### print json.dumps(contenuedejson, indent=4)
            #du = simplecommand("du -Lsb")

            result = simplecommand("du -b %s" % dirpackage)
            taillebytefolder = int(result['result'][0].split()[0])

            fiche={ "size" : "%s" % taillebytefolder,
                    "label" :contenuedejson['name'],
                    "description" : contenuedejson['description'],
                    "version" : contenuedejson['version'],
                    "os" : contenuedejson['targetos'],
                    "metagenerator" : contenuedejson['metagenerator'],
                    "uuid" : contenuedejson['id'],
                    "entity_id": contenuedejson['entity_id'],
                    "sub_packages": json.dumps(contenuedejson['sub_packages']),
                    "reboot": contenuedejson['reboot'],
                    "inventory_associateinventory": contenuedejson['inventory']['associateinventory'],
                    "inventory_licenses": contenuedejson['inventory']['licenses'],
                    "Qversion": contenuedejson['inventory']['queries']['Qversion'],
                    "Qvendor": contenuedejson['inventory']['queries']['Qvendor'],
                    "Qsoftware": contenuedejson['inventory']['queries']['Qsoftware'],
                    "boolcnd": contenuedejson['inventory']['queries']['boolcnd'],
                    "postCommandSuccess_command": contenuedejson['commands']['postCommandSuccess']['command'],
                    "postCommandSuccess_name": contenuedejson['commands']['postCommandSuccess']['name'],
                    "installInit_command": contenuedejson['commands']['installInit']['command'],
                    "installInit_name": contenuedejson['commands']['installInit']['name'],
                    "postCommandFailure_command": contenuedejson['commands']['postCommandFailure']['command'],
                    "postCommandFailure_name": contenuedejson['commands']['postCommandFailure']['name'],
                    "command_command": contenuedejson['commands']['command']['command'],
                    "command_name": contenuedejson['commands']['command']['name'],
                    "preCommand_command": contenuedejson['commands']['preCommand']['command'],
                    "preCommand_name": contenuedejson['commands']['preCommand']['name'],
                    "pkgs_share_id": self.partage_id,
                    "edition_status": 1,
                    "conf_json": json.dumps(contenuedejson)}
            for p in fiche:
                #logger.debug("p %s" % p)
                if p in ['name', 'description','conf_json']:
                    fiche[p] = MySQLdb.escape_string(str(fiche[p])).decode('utf-8')


            sql="""INSERT IGNORE INTO `pkgs`.`packages` (
                                            `label`,
                                            `description`,
                                            `uuid`,
                                            `version`,
                                            `os`,
                                            `metagenerator`,
                                            `entity_id`,
                                            `sub_packages`,
                                            `reboot`,
                                            `inventory_associateinventory`,
                                            `inventory_licenses`,
                                            `Qversion`,
                                            `Qvendor`,
                                            `Qsoftware`,
                                            `boolcnd`,
                                            `postCommandSuccess_command`,
                                            `postCommandSuccess_name`,
                                            `installInit_command`,
                                            `installInit_name`,
                                            `postCommandFailure_command`,
                                            `postCommandFailure_name`,
                                            `command_command`,
                                            `command_name`,
                                            `preCommand_command`,
                                            `preCommand_name`,
                                            `pkgs_share_id`,
                                            `edition_status`,
                                            `conf_json`,
                                            `size`)
                                            VALUES ("%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s");"""%(
                                                    fiche['label'],
                                                    fiche['description'],
                                                    fiche['uuid'],
                                                    fiche['version'],
                                                    fiche['os'],
                                                    fiche['metagenerator'],
                                                    fiche['entity_id'],
                                                    fiche['sub_packages'],
                                                    fiche['reboot'],
                                                    fiche['inventory_associateinventory'],
                                                    fiche['inventory_licenses'],
                                                    fiche['Qversion'],
                                                    fiche['Qvendor'],
                                                    fiche['Qsoftware'],
                                                    fiche['boolcnd'],
                                                    fiche['postCommandSuccess_command'],
                                                    fiche['postCommandSuccess_name'],
                                                    fiche['installInit_command'],
                                                    fiche['installInit_name'],
                                                    fiche['postCommandFailure_command'],
                                                    fiche['postCommandFailure_name'],
                                                    fiche['command_command'],
                                                    fiche['command_name'],
                                                    fiche['preCommand_command'],
                                                    fiche['preCommand_name'],
                                                    fiche['pkgs_share_id'],
                                                    fiche['edition_status'],
                                                    fiche['conf_json'],
                                                    fiche['size'])
            logger.debug("sql %s" % sql)
            try:
                cursor = self.db.cursor()
                cursor.execute(sql)
                self.db.commit()
            except MySQLdb.Error as e:
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
            except Exception as e:
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
            finally:
                cursor.close()
        except Exception as e:
            errorstr = "%s" % traceback.format_exc()
            logger.error("\n%s" % (errorstr))

    def generate_conf_json(self, name, id, description, urlpath):
        logger.debug("function generate_conf_json")
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        template="""{
            "urlpath" : "%s",
            "localisation_server": "%s",
            "sub_packages": [],
            "metagenerator": "manual",
            "description": "%s",
            "creator": "automate_medulla",
            "edition": "automate_medulla",
            "edition_date": "%s",
            "previous_localisation_server": "%s",
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
        }"""%(urlpath,self.param['partage'], description,dt_string,self.param['partage'], dt_string,id, name)
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


def uuid_validate(uuid):
    if len(uuid) != 36:
        return False
    uuid_pattern = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
    result=re.match(uuid_pattern, uuid)
    if result is None:
        return False
    else:
        return True

## Extract number from a string
#uuid_extract_pattern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}"
#re.findall(uuid_extract_pattern, 'The UUID 123e4567-e89b-12d3-a456-426614174000 for node Node 01 is not unique.') # returns ['123e4567-e89b-12d3-a456-426614174000']


if __name__ == "__main__":

    # Quit the process if we don't want to continue
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    parser = OptionParser()
    parser.add_option("-H", "--host",
                    dest="hostname", default = "localhost",
                    help="hostname SGBD")

    parser.add_option("-P", "--port",
                    dest="port", default = 3306,
                    help="port SGBD")

    parser.add_option("-u", "--user",
                    dest="user", default = "root",
                    help="user account")

    parser.add_option("-B", "--base",
                    dest="base", default = "xmppmaster",
                    help="base sql name")

    parser.add_option("-p", "--password",
                    dest="password", default = "",
                    help="password connection")

    parser.add_option("-t", "--testconnect", action="store_true",
                    dest="testconnect", default=False,
                    help="test connection and quit")

    parser.add_option("-T", "--nametable", dest="nametable", default="update_data",
                    help="name table update")

    parser.add_option("-U", "--uidpackage", dest="uidpackage", default="",
                    help="name uid package windows")

    parser.add_option("-C", "--forcecreatepackage", action="store_true",
                      dest="forcecreatepackage", default=False,
                      help="installation du package avec creation ou recreation")

    parser.add_option("-c", "--createpackage", action="store_true",
                      dest="createpackage", default=False,
                      help="installation du package avec creation si necessaire")

    parser.add_option("-S", "--forcedelpackage", action="store_true",
                      dest="forcedelpackage",  default=False,
                      help="deinstallation du package et suppression complete")

    parser.add_option("-s", "--delpackage",action="store_true",
                      dest="delpackage", default=False,
                      help="deinstallation du package mais conserve package")

    parser.add_option("-o", "--outputdir", dest="outputdir",
                      default="/var/lib/pulse2/base_update_package",
                      help="path base directory generation package")

    parser.add_option("-M", "--share_dir_medulla ",
                      dest="partage", default="winupdates",
                      help="partage name")

    parser.add_option("-l", "--logfile", dest="logfile",
                      default="/var/log/mmc/medulla-mariadb-synchro-update-package.log",
                      help="file de configuration")

    parser.add_option("-d", "--debug", dest="debugmode",action="store_true",
                      default=False,
                      help="ecrit reference in code")

    parser.add_option("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages to stdout")

    parser.add_option("-i", "--info_parametre",
                    action="store_true", dest="show_parametre", default=False,
                    help="display tout les parametres and quit")

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

    file_handler = logging.FileHandler(filename=opts.logfile)

    if opts.verbose:
        handlers = [file_handler]
    else:
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]
    format = "%(asctime)s - %(levelname)s - %(message)s"
    level = logging.INFO
    if opts.debugmode:
        #format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
        #format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
        format='[%(asctime)s] {%(lineno)d} %(levelname)s - %(message)s'
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format=format,
        handlers=handlers
    )

    logger = logging.getLogger()
    commandline=  " ".join(sys.argv)
    logger.debug("comand line %s"%commandline)
    print ("comand line %s"% " ".join(sys.argv))

    parametre_display = vars(opts).copy()
    parametre_display['password']="xxxxx"
    parametre_dis=json.dumps(parametre_display,indent=4)
    if opts.debugmode:
        logger.debug(parametre_dis)
    if opts.show_parametre:
        print ("*************************************************************************************************************************")
        print ("*********************************************** utility usage information ***********************************************")
        print ("*************************************************************************************************************************")
        print("your command line : %s" % commandline)
        print("Current or default option")
        print(parametre_dis)
        print("exemples")
        print ("command information\n")
        print ("\t1) affiche cette info option -i")
        print ("\t\tpython3 ./%s -i\n" % os.path.basename(sys.argv[0]))
        print ("\n\t2) test connection option -t")
        print ("\t\tpython3 ./%s -t -uroot -P 3306 -Hlocalhost -p siveo\n" % os.path.basename(sys.argv[0]))
        print ("\tPARAMETRE CONNECION CORRECT: CONNECT SUCCESS")
        print ("\ttest connection format debug")
        print ("\t\tpython3 ./%s -t -uroot -P 3306 -Hlocalhost -p siveo -d"% os.path.basename(sys.argv[0]))
        print("try Connecting with parameters\n" \
                    "\thost: localhost\n" \
                    "\tuser: root\n" \
                    "\tport: 3306\n" \
                    "\tdb: 3306\n")
        print ("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS\n")
        print ("\n\t3) forces the complete creation of an update package and installs it in pkgs option -C")
        print ("\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -C" % os.path.basename(sys.argv[0]))
        print ("\t\tIf the package exists it is completely recreated")
        print ("\t\tIf the package is installed it reinstalls it")
        print ("package c9240667-c3d9-4ba0-8a4e-e258473f7b73 is successfully installed\n")

        print ("SELECT uuid FROM pkgs.packages where uuid='c9240667-c3d9-4ba0-8a4e-e258473f7b73';")
        print ("+--------------------------------------+")
        print ("| uuid                                 |")
        print ("+--------------------------------------+")
        print ("| c9240667-c3d9-4ba0-8a4e-e258473f7b73 |    <<--- package installer  ")
        print ("+--------------------------------------+")
        print ("ls -al  /var/lib/pulse2/packages/sharing/winupdates/")
        print ("c9240667-c3d9-4ba0-8a4e-e258473f7b73")

        print ("\n\t4 creation if no exist package and installs it in pkgs if is not installed option -c")
        print ("\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -c "%os.path.basename(sys.argv[0]))
        print ("\t\tpackage exists c9240667-c3d9-4ba0-8a4e-e258473f7b73 already")
        print ("\t\tpackage c9240667-c3d9-4ba0-8a4e-e258473f7b73 is installed in pkgs")

        print ("\n\t5 uninstall package option -s")
        print ("\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -s "%os.path.basename(sys.argv[0]))
        print ("\t\tpackage move to base update : the package still exists")
        print ("ls /var/lib/pulse2/base_update_package")
        print ("c9240667-c3d9-4ba0-8a4e-e258473f7b73     <---the package still exists")
        print ("ls  /var/lib/pulse2/packages/sharing/winupdates/    uninstall")
        print ("uninstall pkgs")
        print ("SELECT * FROM pkgs.packages where uuid='c9240667-c3d9-4ba0-8a4e-e258473f7b73';")
        print ("Empty set (0.000 sec)  package uninstall in pkgs")

        print ("\n\t6 complete uninstall package option -S")
        print ("\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -S "%os.path.basename(sys.argv[0]))
        print ("\t\tRemove package")
        print ("\t\tthe package no longer exists")
        print ("ls /var/lib/pulse2/base_update_package    <---  the package no longer exists")
        print ("ls  /var/lib/pulse2/packages/sharing/winupdates/    <---  the package no longer exists")
        print ("uninstall pkgs")
        print ("MariaDB [pkgs]> SELECT * FROM pkgs.packages where uuid='c9240667-c3d9-4ba0-8a4e-e258473f7b73';")
        print ("Empty set (0.000 sec)  package uninstall in pkgs")
        print ("*************************************************************************************************************************")
        sys.exit(1)

    if opts.partage == "":
        print("name partage missing")
    path_partage = os.path.join("/var/lib/pulse2/packages/sharing/", opts.partage)


    #if opts.outputdir == "/var/lib/pulse2/packages/base_update_package":
        #opts.outputdir=os.path.join(opts.outputdir, opts.table_name)

    #print ( "path_partage %s " % path_partage)


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
        print("try Connecting with parameters\n" \
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
            print("CORRECT CONNECTION PARAMETER: CONNECT SUCCESS")
            logger.debug("CONECTION SUCCES : TEST TERMINER OK")
        except Exception as e:
            errorstr = "%s" % traceback.format_exc()
            print("\n%s" % (errorstr))
        finally:
            db.close()
            sys.exit(1)

    nbtrue=  len ([x for x in [ opts.forcecreatepackage,opts.createpackage,opts.forcedelpackage,opts.delpackage ] if x])
    valquit=0
    if nbtrue != 1:
        print ( "at least 1 of the following options is required (sScC) -s or -S or -c or -C")
        valquit=1


    if opts.uidpackage == "":
        print ( "you must have the -U option to specify the update uuid")
        logger.debug( "you must have the -U option to specify the update uuid")
        sys.exit(1)

    if len(opts.uidpackage) != 36 or uuid_validate( opts.uidpackage) == None:
        print ( "uuid de l'option U n'est pas conforme")
        #obligatoirement ce parametre avec 1 uuid valable pour option -u")
        print (uuid_validate( opts.uidpackage))
        valquit=1

    if opts.nametable == "":
        print ( "l'option -T 'table produit' ne peut pas etre vide")
        valquit=1

    if  valquit:
        print ( "at least 1 of the following options is required (sScC) -s or -S or -c or -C")

        sys.exit(1)
    try:
        #db = MySQLdb.connect(host=opts.hostname,
                            #user=opts.user,
                            #passwd=Passwordbase,
                            #port = int(opts.port),
                            #db=opts.base)
        db = MySQLdb.connect(host=opts.hostname,
                            user=opts.user,
                            passwd=Passwordbase,
                            port = int(opts.port))
        logger.debug("CONNECT SUCCESS")

        logger.debug("Generate the packages")


        #if opts.forcecreatepackage or opts.createpackage or opts.forcedelpackage or opts.delpackage:
            # il y a au moin 1 demande
            #verification qu'il y ai 1 seule demande


        generateur = synch_packages(db,  vars(opts))
        #generateur = synch_packages(db, opts ).search_file_update()

    except Exception as e:
        errorstr = "%s" % traceback.format_exc()
        print ("ERROR CONNECTION")
        print ("\n%s" % (errorstr))
        logger.error("\n%s" % (errorstr))
        sys.exit(1)
    finally:
        db.close()
