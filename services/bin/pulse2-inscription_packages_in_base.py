#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2021 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# file  : inscription_in_base.py
# ce programme permet d'inscrire less package base fichiers vers la base sql
# il doit etre utilise que pour les package en mode standanrd.
# il lit tous les packages dans /var/lib/pulse/packages et les inscrit en base.

import sys
import os
import logging
import subprocess
import json
import traceback
from optparse import OptionParser
import MySQLdb
import getpass
logger = logging.getLogger()

def simplecommand(cmd):
    obj = {}
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code'] = p.wait()
    obj['result'] = result
    return obj
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class managepackage:
    # variable de classe
    agenttype="relayserver"

    @staticmethod
    def packagedir():
        """
        This function provide the path of the package folder.

        @return: string: The path of the package folder.
        """
        if sys.platform.startswith('linux'):
            if managepackage.agenttype == "relayserver":
                return os.path.join("/", "var", "lib", "pulse2", "packages")
            else:
                return os.path.join(os.path.expanduser('~pulseuser'), 'packages')
        elif sys.platform.startswith('win'):
            return os.path.join(
                os.environ["ProgramFiles"], "Pulse", "var", "tmp", "packages")
        elif sys.platform.startswith('darwin'):
            return os.path.join(
                "/opt", "Pulse", "packages")
        else:
            return None

    @staticmethod
    def search_list_package(shared_dir=None):
        """
            This function searches packages in the global and
            local shares.
        """

        packagelist = []
        if shared_dir is None:
            dirpackage = managepackage.packagedir()
        else:
            shared_dir = os.path.abspath(os.path.realpath(shared_dir))
        dirglobal = os.path.join(dirpackage,"sharing", "global")
        packagelist = [os.path.join(dirglobal, f) for f in os.listdir(dirglobal) if len(f) == 36]
        dirlocal  = os.path.join(dirpackage, "sharing")
        share_pathname = [os.path.join(dirlocal, f) for f in os.listdir(dirlocal) if f != "global"]
        for part in share_pathname:
            filelist = [os.path.join(part, f) for f in os.listdir(part) if len(f) == 36]
            packagelist += filelist
        return packagelist

    @staticmethod
    def package_for_deploy_from_share(shared_dir=None, verbose=False):
        """
            This function creates symlinks in the packages directory
            to the target in the local/global share
        """

        if shared_dir is None:
            dirpackage = managepackage.packagedir()
        else:
            shared_dir = os.path.abspath(os.path.realpath(shared_dir))
        for x in  managepackage.search_list_package():
            if verbose:
                print "symbolic link %s to %s" %(x , os.path.join(dirpackage, os.path.basename(x)))
            try:
                os.symlink(x , os.path.join(dirpackage, os.path.basename(x)))
            except OSError:
                pass

    @staticmethod
    def remove_symlinks(dirpackage=None):
        """
        This function remove symlinks
        """
        if dirpackage is None:
            dirpackage = managepackage.packagedir()
        else:
            dirpackage = os.path.abspath(os.path.realpath(dirpackage))
        packagelist = [os.path.join(dirpackage, f) for f in os.listdir(dirpackage) if len(f) == 36]
        for fi in packagelist:
            if os.path.islink(fi) and not os.path.exists(fi):
                os.remove(fi)

    @staticmethod
    def listpackages():
        """
        This functions is used to list the packages
        Returns:
            It returns the list of the packages.
        """
        return [os.path.join(managepackage.packagedir(), x) for x in os.listdir(
            managepackage.packagedir()) if os.path.isdir(os.path.join(managepackage.packagedir(), x))]

    @staticmethod
    def loadjsonfile(filename):
        """
        This function is used to load a json file
        Args:
            filename: The filename of the json file to load
        Returns:
            It returns the content of the JSON file
        """

        if os.path.isfile(filename):
            with open(filename, 'r') as info:
                jsonFile = info.read()
            try:
                outputJSONFile = json.loads(jsonFile.decode('utf-8', 'ignore'))
                return outputJSONFile
            except Exception as e:
                logger.error("We failed to decode the file %s" % filename)
                logger.error("we encountered the error: %s" % str(e))
        return None

    @staticmethod
    def getdescriptorpackagename(packagename):
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(
                    os.path.join(package, "xmppdeploy.json"))
                if 'info' in outputJSONFile \
                        and ('software' in outputJSONFile['info'] and\
                            'version' in outputJSONFile['info']) \
                        and (outputJSONFile['info']['software'] == packagename or\
                            outputJSONFile['info']['name'] == packagename):
                    return outputJSONFile
            except Exception as e:
                logger.error("Please verify the format of the descriptor for"
                             "the package %s." % packagename)
                logger.error("we are encountering the error: %s" % str(e))
        return None

    @staticmethod
    def getversionpackagename(packagename):
        """
        This function is used to get the version of the package
        WARNING: If more one package share the same name,
                 this function will return the first one.
        Args:
            packagename: This is the name of the package
        Returns:
            It returns the version of the package
        """
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(os.path.join(package, "xmppdeploy.json"))
                if 'info' in outputJSONFile \
                        and ('software' in outputJSONFile['info'] and 'version' in outputJSONFile['info']) \
                        and (outputJSONFile['info']['software'] == packagename or outputJSONFile['info']['name'] == packagename):
                    return outputJSONFile['info']['version']
            except Exception as e:
                logger.error("Please verify the version for the package %s in the descriptor"
                             "in the xmppdeploy.json file." % package)
                logger.error("we are encountering the error: %s" % str(e))
        return None

    @staticmethod
    def getpathpackagename(packagename):
        """
        This function is used to get the name of the package
        Args:
            packagename: This is the name of the package
        Returns:
            It returns the name of the package
        """
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(
                    os.path.join(package, "xmppdeploy.json"))
                if 'info' in outputJSONFile \
                    and (('software' in outputJSONFile['info'] and outputJSONFile['info']['software'] == packagename)
                         or ('name' in outputJSONFile['info'] and outputJSONFile['info']['name'] == packagename)):
                    return package
            except Exception as e:
                logger.error("Please verify the name for the package %s in the descriptor"
                             "in the xmppdeploy.json file." % package)
                logger.error("we are encountering the error: %s" % str(e))
        return None

    @staticmethod
    def getpathpackagebyuuid(uuidpackage):
        """
        This function is used to find the package based on the uuid
        Args:
            uuidpackage: The uuid of the package we are searching
        Returns:
            We return the package, it returns None if any error or if
                the package is not found.
        """
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(
                    os.path.join(package, "conf.json"))
                if 'id' in outputJSONFile and outputJSONFile['id'] == uuidpackage:
                    return package
            except Exception as e:
                logger.error("The conf.json for the package %s is missing" % package)
                logger.error("we are encountering the error: %s" % str(e))
                return None
        logger.error("We did not find the package %s" % package)
        return None


    @staticmethod
    def getversionpackageuuid(packageuuid):
        """
        This function is used to find the version of the package based
            on the uuid
        Args:
            packageuuid: The uuid of the package we are searching
        Returns:
            We return the version of package, it returns None if
                any error or if the package is not found.
        """
        for package in managepackage.listpackages():
            try:
                outputJSONFile = managepackage.loadjsonfile(
                    os.path.join(package, "conf.json"))
                if 'id' in outputJSONFile and outputJSONFile['id'] == packageuuid \
                    and 'version' in outputJSONFile:
                    return outputJSONFile['version']
            except Exception as e:
                logger.error(
                    "package %s verify format descriptor conf.json [%s]" %
                    (packageuuid, str(e)))
        logger.error("package %s verify version" \
                        "in descriptor conf.json [%s]" %(packageuuid))
        return None

    @staticmethod
    def getpathpackagebyuuid(uuidpackage):
        for package in managepackage.listpackages():
            try:
                jr = managepackage.loadjsonfile(
                    os.path.join(package, "conf.json"))
                if 'id' in jr and jr['id'] == uuidpackage:

                    logger.error("getpathpackagebyuuid %s package is %s" % (uuidpackage,
                                                                            package))
                    return package
            except Exception as e:
                logger.error("package %s missing [%s]" % (package, str(e)))
        return None

    @staticmethod
    def getversionpackageuuid(packageuuid):
        for package in managepackage.listpackages():
            try:
                jr = managepackage.loadjsonfile(
                    os.path.join(package, "conf.json"))
                if 'id' in jr and jr['id'] == packageuuid \
                    and 'version' in jr:
                    return jr['version']
            except Exception as e:
                logger.error(
                    "package %s verify format descriptor conf.json [%s]" %
                    (packageuuid, str(e)))
        logger.error("package %s verify version " \
                        "in descriptor conf.json [%s]" %(packageuuid))
        return None

    @staticmethod
    def getnamepackagefromuuidpackage(uuidpackage):
        pathpackage = os.path.join(
            managepackage.packagedir(),
            uuidpackage,
            "xmppdeploy.json")
        if os.path.isfile(pathpackage):
            outputJSONFile = managepackage.loadjsonfile(pathpackage)
            return outputJSONFile['info']['name']
        return None

    @staticmethod
    def getdescriptorpackageuuid(packageuuid):
        jsonfile = os.path.join(
            managepackage.packagedir(),
            packageuuid,
            "xmppdeploy.json")
        if os.path.isfile(jsonfile):
            try:
                outputJSONFile = managepackage.loadjsonfile(jsonfile)
                return outputJSONFile
            except Exception:
                return None

    @staticmethod
    def getpathpackage(uuidpackage):
        return os.path.join(managepackage.packagedir(), uuidpackage)

if __name__ == '__main__':
    base="pkgs"
    db=None

    help_message="This program is use to add or readd in the database, the package already in /var/lib/pulse2/packages"

    optp = OptionParser(description=help_message)
    optp.add_option("-H", "--hostname",
                    dest="hostname", default = "localhost",
                    help="Hostname of the SQL Server")

    optp.add_option("-P", "--port",
                    dest="port", default = 3306,
                    help="port of the SQL Server")

    optp.add_option("-u", "--user",
                    dest="user", default = "root",
                    help="username in the SQL Server")
    password=""
    optp.add_option("-p", "--password",
                    dest="password", default = "",
                    help="Password of the user in the SQL Server")


    optp.add_option("-g", "--regeneratetable",action="store_true",
                    dest="regeneratetable", default=False,
                    help="reser the package list in the database")

    opts, args = optp.parse_args()

    if opts.password != "":
        Passwordbase = opts.password
    else:
        Passwordbase = getpass.getpass(prompt='Password for mysql://' \
                                       '%s:<password>@%s:%s/%s'%(opts.user,
                                                                 opts.hostname,
                                                                 opts.port,
                                                                 base) ,
                                       stream=None)


    try:
        db = MySQLdb.connect(host=opts.hostname,
                             user=opts.user,
                             passwd=Passwordbase,
                             port = int(opts.port),
                             db=base)
        if opts.regeneratetable:
            try:
                cursor = db.cursor()
                cursor.execute("DELETE FROM `pkgs`.`packages` WHERE 1;")
                db.commit()
            except MySQLdb.Error as e:
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
                print "%s" % (errorstr)
                sys.exit(255)
            except Exception as e:
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
                print "%s" % (errorstr)
                sys.exit(255)
            finally:
                cursor.close()

        packagedir = os.path.join("/", "var", "lib", "pulse2", "packages")
        sharing = os.path.join(packagedir,"sharing")
        list_package = [os.path.join(packagedir, x) for x in os.listdir(packagedir) \
            if len(x) == 36 and\
                os.path.isdir(os.path.join(packagedir, x))]

        for package in list_package:
            jsonfilepath = os.path.join(package, "conf.json")
            json_file = managepackage.loadjsonfile(jsonfilepath)

            result = simplecommand("du -b %s" % package)
            sizebytefolder = int(result['result'][0].split()[0])
            package_infos = {"size": "%s" % sizebytefolder,
                     "label":json_file['name'],
                     "description": json_file['description'],
                     "version": json_file['version'],
                     "os": json_file['targetos'],
                     "metagenerator": json_file['metagenerator'],
                     "uuid": json_file['id'],
                     "entity_id": json_file['entity_id'],
                     "sub_packages": json.dumps(json_file['sub_packages']),
                     "reboot": json_file['reboot'],
                     "inventory_associateinventory": json_file['inventory']['associateinventory'],
                     "inventory_licenses": json_file['inventory']['licenses'],
                     "Qversion": json_file['inventory']['queries']['Qversion'],
                     "Qvendor": json_file['inventory']['queries']['Qvendor'],
                     "Qsoftware": json_file['inventory']['queries']['Qsoftware'],
                     "boolcnd": json_file['inventory']['queries']['boolcnd'],
                     "postCommandSuccess_command": json_file['commands']['postCommandSuccess']['command'],
                     "postCommandSuccess_name": json_file['commands']['postCommandSuccess']['name'],
                     "installInit_command": json_file['commands']['installInit']['command'],
                     "installInit_name": json_file['commands']['installInit']['name'],
                     "postCommandFailure_command": json_file['commands']['postCommandFailure']['command'],
                     "postCommandFailure_name": json_file['commands']['postCommandFailure']['name'],
                     "command_command": json_file['commands']['command']['command'],
                     "command_name": json_file['commands']['command']['name'],
                     "preCommand_command": json_file['commands']['preCommand']['command'],
                     "preCommand_name": json_file['commands']['preCommand']['name'],
                     "pkgs_share_id": "NULL",
                     "edition_status": 1,
                     "conf_json": json.dumps(json_file)}

            for p in package_infos:
                package_infos[p] = MySQLdb.escape_string(str(package_infos[p]))


            sql="""INSERT INTO `pkgs`.`packages` (
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
                                                    %s,"%s","%s",%s);"""%(
                                                    package_infos['label'],
                                                    package_infos['description'],
                                                    package_infos['uuid'],
                                                    package_infos['version'],
                                                    package_infos['os'],
                                                    package_infos['metagenerator'],
                                                    package_infos['entity_id'],
                                                    package_infos['sub_packages'],
                                                    package_infos['reboot'],
                                                    package_infos['inventory_associateinventory'],
                                                    package_infos['inventory_licenses'],
                                                    package_infos['Qversion'],
                                                    package_infos['Qvendor'],
                                                    package_infos['Qsoftware'],
                                                    package_infos['boolcnd'],
                                                    package_infos['postCommandSuccess_command'],
                                                    package_infos['postCommandSuccess_name'],
                                                    package_infos['installInit_command'],
                                                    package_infos['installInit_name'],
                                                    package_infos['postCommandFailure_command'],
                                                    package_infos['postCommandFailure_name'],
                                                    package_infos['command_command'],
                                                    package_infos['command_name'],
                                                    package_infos['preCommand_command'],
                                                    package_infos['preCommand_name'],
                                                    package_infos['pkgs_share_id'],
                                                    package_infos['edition_status'],
                                                    package_infos['conf_json'],
                                                    package_infos['size'])

            print sql
            try:
                lastrowid = -1
                cursor = db.cursor()
                cursor.execute(sql)
                lastrowid = cursor.lastrowid
                print "create package id=%s" % lastrowid
                db.commit()
            except MySQLdb.Error as e:
                errorstr = "%s" % traceback.format_exc()
                print "%s" % (str(e))
            except Exception as e:
                errorstr = "%s" % traceback.format_exc()
                logger.error("\n%s" % (errorstr))
                print "%s" % (errorstr)
            finally:
                cursor.close()
    except Exception as e:
        errorstr = "%s" % traceback.format_exc()
        logger.error("\n%s" % (errorstr))
        print "%s" % (errorstr)
        sys.exit(1)
    finally:
        if db is not None:
            db.close()
    for package in list_package:
        print package
