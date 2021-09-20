#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
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

# file  : pulse2-generation_package.py

import shutil
import sys,os
import logging
import platform
import subprocess
import base64
import time
import json
import re
import traceback
from datetime import datetime
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



def add_coloring_to_emit_windows(fn):
        # add methods we need to the class
    # def _out_handle(self):
        #import ctypes
        # return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    #out_handle = property(_out_handle)

    def _set_color(self, code):
        import ctypes
        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, '_set_color', _set_color)

    def new(*args):
        FOREGROUND_BLUE = 0x0001  # text color contains blue.
        FOREGROUND_GREEN = 0x0002  # text color contains green.
        FOREGROUND_RED = 0x0004  # text color contains red.
        FOREGROUND_INTENSITY = 0x0008  # text color is intensified.
        FOREGROUND_WHITE = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED
        # winbase.h
        #STD_INPUT_HANDLE = -10
        #STD_OUTPUT_HANDLE = -11
        #STD_ERROR_HANDLE = -12

        # wincon.h
        #FOREGROUND_BLACK     = 0x0000
        FOREGROUND_BLUE = 0x0001
        FOREGROUND_GREEN = 0x0002
        #FOREGROUND_CYAN      = 0x0003
        FOREGROUND_RED = 0x0004
        FOREGROUND_MAGENTA = 0x0005
        FOREGROUND_YELLOW = 0x0006
        #FOREGROUND_GREY      = 0x0007
        FOREGROUND_INTENSITY = 0x0008  # foreground color is intensified.

        #BACKGROUND_BLACK     = 0x0000
        #BACKGROUND_BLUE      = 0x0010
        #BACKGROUND_GREEN     = 0x0020
        #BACKGROUND_CYAN      = 0x0030
        #BACKGROUND_RED       = 0x0040
        #BACKGROUND_MAGENTA   = 0x0050
        BACKGROUND_YELLOW = 0x0060
        #BACKGROUND_GREY      = 0x0070
        BACKGROUND_INTENSITY = 0x0080  # background color is intensified.

        levelno = args[1].levelno
        if(levelno >= 50):
            color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY
        elif(levelno >= 40):
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif(levelno >= 30):
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif(levelno >= 20):
            color = FOREGROUND_GREEN
        elif(levelno >= 10):
            color = FOREGROUND_MAGENTA
        else:
            color = FOREGROUND_WHITE
        args[0]._set_color(color)

        ret = fn(*args)
        args[0]._set_color(FOREGROUND_WHITE)
        # print "after"
        return ret
    return new


def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if(levelno >= 50):
            color = '\x1b[31m'  # red
        elif(levelno >= 40):
            color = '\x1b[31m'  # red
        elif(levelno >= 30):
            color = '\x1b[33m'  # yellow
        elif(levelno >= 20):
            color = '\x1b[32m'  # green
        elif(levelno >= 10):
            color = '\x1b[35m'  # pink
        else:
            color = '\x1b[0m'  # normal
        args[1].msg = color + str(args[1].msg) + '\x1b[0m'  # normal
        # print "after"
        return fn(*args)
    return new

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
                return os.path.join(os.path.expanduser('~pulseuser'),
'packages')
        elif sys.platform.startswith('win'):
            return os.path.join(
                os.environ["ProgramFiles"], "Pulse", "var", "tmp", "packages")
        elif sys.platform.startswith('darwin'):
            return os.path.join(
                "/opt", "Pulse", "packages")
        else:
            return None

    @staticmethod
    def search_list_package(dirpartage = None):
        """
            list tout les packages in les partages
        """
        packagelist=[]
        if dirpartage is None:
            dirpackage = managepackage.packagedir()
        else:
            dirpartage = os.path.abspath(os.path.realpath(dirpartage))
        dirglobal = os.path.join(dirpackage,"sharing", "global")
        packagelist = [os.path.join(dirglobal, f) for f in os.listdir(dirglobal) if len(f) == 36]
        dirlocal  = os.path.join(dirpackage, "sharing")
        pathnamepartage = [os.path.join(dirlocal, f) for f in os.listdir(dirlocal) if f != "global"]
        for part in pathnamepartage:
            filelist = [os.path.join(part, f) for f in os.listdir(part) if len(f) == 36]
            packagelist += filelist
        return packagelist

    @staticmethod
    def package_for_deploy_from_partage(dirpartage = None, verbeux = False):
        """
            Cette fonction crée les liens symbolique pour les partages.
        """
        if dirpartage is None:
            dirpackage = managepackage.packagedir()
        else:
            dirpartage = os.path.abspath(os.path.realpath(dirpartage))
        for x in  managepackage.search_list_package():
            if verbeux:
                print "symbolic link %s to %s" %(x , os.path.join(dirpackage, os.path.basename(x)))
            try:
                os.symlink(x , os.path.join(dirpackage, os.path.basename(x)))
            except OSError:
                pass

    @staticmethod
    def del_link_symbolic(dirpackage = None):
        """
            Cette fonction suprime les liens symboliques cassés pour les partages.
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
            with open(filename,
'r') as info:
                jsonFile = info.read()
            try:
                outputJSONFile = json.loads(jsonFile.decode('utf-8',
'ignore'))
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
                             "the package %s." %s)
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
            # print os.path.join(package,"xmppdeploy.json")
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
    textprogramme="""
    Usage: generation_package.py [options]

    Ce Programme permet de migrer
        les packages de /var/lib/pulse/packages

        ├── packages
            ├── 74b2dffa-benjamin_uw9z8k3zu2c7v3tps0
            ├── 1369af6a-5cb6-11eb-a553-cb5f2e393da3
            └── 136a3b60-5cb6-11eb-9d70-87334546ed5a
        vers
        les partages /var/lib/pulse/packages/sharing

        ├── packages
            └── sharing
                ├── caisse1
                │   └── 74b2dffa-benjamin_uw9z8k3zu2c7v3tps0 <-package caisse1
                └── global
                    ├── 1369af6a-5cb6-11eb-a553-cb5f2e393da3 <-package global
                    └── 136a3b60-5cb6-11eb-9d70-87334546ed5a <-package global
        Vous devez deplacer les packages dans leurs differents partages.
        puis lancer le programme.

        exemple
        ./generation_package.py -ummc -P yslJl8EBUA -r -g -m -l

    Options:
    -h, --help            show this help message and exit
    -H HOSTNAME, --hostname=HOSTNAME
                            hostname SGBD
    -P PORT, --port=PORT  port_decreation
    -u USER, --user=USER  user compter
    -p PASSWORD, --password=PASSWORD
                            password connection
    -v, --verbeux         mode verbeux
    -t, --testconnect     teste la connexion et quitte
    -r, --report          print report messages to stdout
    -g, --regeneratetable
                            reinitialise des packages dans la bases
    -m, --move            deplace les packages avec erreur vers
                            /var/lib/pulse2/packageerror
    -l, --linkcreate      regenere les liens symbolique des package
    """
    textprogrammehelp="\nCe Programme permet de migrer\n" \
        "les packages de /var/lib/pulse/packages\n" \
        "\nvers\n" \
        "les partages /var/lib/pulse/packages/sharing\n"\
        "\nvoir pour information generation_package.py -i"


    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)
    logging.basicConfig(level = logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    optp = OptionParser(description=textprogrammehelp)
    optp.add_option("-H", "--host",
                    dest="hostname", default = "localhost",
                    help="hostname SGBD")

    optp.add_option("-P", "--port",
                    dest="port", default = 3306,
                    help="port_decreation")

    optp.add_option("-u", "--user",
                    dest="user", default = "root",
                    help="user compter")
    password=""
    optp.add_option("-p", "--password",
                    dest="password", default = "",
                    help="password connection")

    optp.add_option("-v", "--verbeux",action="store_true",
                    dest="verbeux", default=False,
                    help="mode verbeux")

    optp.add_option("-r", "--report",action="store_true",
                    dest="verbosereport", default=False,
                    help="print report messages to stdout")

    optp.add_option("-g", "--regeneratetable",action="store_true",
                    dest="regeneratetable", default=False,
                    help="reinitialise des packages dans la bases")

    optp.add_option("-m", "--move",action="store_true",
                    dest="movebadpackage", default=False,
                    help="deplace les packages avec erreur vers /var/lib/pulse2/packageerror")

    optp.add_option("-l", "--linkcreate",action="store_true",
                    dest="linkcreate", default=False,
                    help="regenere les liens symbolique des package")

    optp.add_option("-t", "--testconnect",action="store_true",
                    dest="testconnect", default=False,
                    help="test connection et quitte")

    optp.add_option("-i", "--info",action="store_true",
                    dest="info", default=False,
                    help="message information et quitte")

    opts, args = optp.parse_args()

    if opts.info:
        print textprogramme
        sys.exit(0)

    if not os.path.exists("/var/lib/pulse2/packageerror"):
        os.mkdir("/var/lib/pulse2/packageerror")

    if opts.verbeux:
        opts.verbosereport = 1

    if opts.password != "":
        Passwordbase = opts.password
    else:
        Passwordbase = getpass.getpass(prompt='Password for mysql://' \
                                       '%s:<password>@%s:%s/%s'%(opts.user,
                                                                 opts.hostname,
                                                                 opts.port,
                                                                 base) ,
                                       stream=None)
    if opts.verbeux or opts.testconnect:
            logger.debug("try Connecting with parameters\n" \
                            "\thost: %s\n" \
                            "\tuser: %s\n" \
                            "\tport: %s\n" \
                            "\tdb: %s\n" %( opts.hostname,
                                            opts.user,
                                            int(opts.port),
                                            base))

    try:
        db = MySQLdb.connect(host=opts.hostname,
                             user=opts.user,
                             passwd=Passwordbase,
                             port = int(opts.port),
                             db=base)

        if opts.verbeux:
            logger.debug("Connecting with parameters\n" \
                            "\thost: %s\n" \
                            "\tuser: %s\n" \
                            "\tdb: %s\n" %( opts.hostname,
                                        opts.user,
                                        base))

        if opts.testconnect:
            logger.debug("CONNECT SUCCESS")
            sys.exit(0)

        if opts.regeneratetable:
            if opts.verbosereport:
                print "truncate table package"
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

        cursor = db.cursor()
        sharingid={}
        try:
            cursor.execute("SELECT id,name FROM pkgs.pkgs_shares;")
            records = cursor.fetchall()

            for row in records:
                sharingid[row[1]] = row[0]
            if opts.verbosereport:
                print("\nPARTAGE LISTE")
                for part in sharingid:
                    print "%s %s" % (part, sharingid[part])
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



        packagename=[]
        partagename=set()
        partagename.add("global")

        package_partage={}
        bad_package=[]
        listpackage = managepackage.search_list_package()
        if opts.verbeux:
            print "LISTE DES PACKAGES"
        for t in listpackage:
            packagename.append(os.path.basename(t))
            partagename.add(os.path.basename(os.path.dirname(t)))

        for t in partagename:
            package_partage[t]=[]

        for t in listpackage:
            packagename.append(os.path.basename(t))
            partagename =  os.path.basename(os.path.dirname(t))
            package_partage[partagename].append(t)
        if opts.verbeux:
            print json.dumps(package_partage, indent=4)
        creationpackageinbase=[]
        errorcreationpackageinbase=[]
        for partage in package_partage:
            for path_package in package_partage[partage]:
                jsonfilepath = os.path.join(path_package, "conf.json")
                if opts.verbeux:
                    print "analyse package suivant %s" % jsonfilepath

                contenuedejson = managepackage.loadjsonfile(jsonfilepath)
                if contenuedejson is None:
                    #print "WARNING PACKAGE %s BAD"%path_package
                    bad_package.append(path_package)
                    continue

                if not('localisation_server' in contenuedejson and contenuedejson['localisation_server'] != "") :
                    contenuedejson['localisation_server'] = partage
                    contenuedejson['previous_localisation_server'] = partage

                if not ("creator" in contenuedejson and contenuedejson['creator'] != "") :
                    contenuedejson['creator'] = "root"

                if not ("edition" in contenuedejson  and contenuedejson['edition'] != "") :
                    contenuedejson['edition'] = "root"

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
                du = simplecommand("du -sb")
                result = simplecommand("du -b %s" % path_package)
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
                        "pkgs_share_id": sharingid[partage],
                        "edition_status": 1,
                        "conf_json": json.dumps(contenuedejson)}


                for p in fiche:
                    fiche[p] = MySQLdb.escape_string(str(fiche[p]))
                if opts.verbeux:
                    print "creation package %s(%s) dans partage %s" %(fiche['label'],
                                                                    fiche['uuid'],
                                                                    partage)

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
                #print sql
                try:
                    lastrowid = -1
                    cursor = db.cursor()
                    cursor.execute(sql)

                    lastrowid = cursor.lastrowid
                    db.commit()
                    creationpackageinbase.append({ "packagename" :  fiche['label'],
                                                "uuid" : fiche['uuid'],
                                                "id" : lastrowid,
                                                "sharing" : partage})

                except MySQLdb.Error as e:

                    errorstr = "%s" % traceback.format_exc()
                    if opts.verbeux:
                        logger.error("\n%s" % (errorstr))
                    if opts.verbeux:
                        print "%s" % (str(e))
                    errorcreationpackageinbase.append({ "packagename" : fiche['label'],
                                                        "uuid" : fiche['uuid'],
                                                        "sharing" : partage,
                                                        "error" : str(e)})

                except Exception as e:
                    errorstr = "%s" % traceback.format_exc()
                    logger.error("\n%s" % (errorstr))
                    print "%s" % (errorstr)
                finally:
                    cursor.close()
        if opts.verbosereport:
            if  creationpackageinbase:
                print "PACKAGE ADD IN BASE"
                print "+%6s+%15s+%36s+%40s+"%('------',
                                            '---------------',
                                            '------------------------------------',
                                            '----------------------------------------')
                print "|%6s|%15s|%36s|%40s|"%('ID',
                                        'sharing',
                                        'uuid package',
                                        'package name')
                for inscription in creationpackageinbase:
                    print "|%6s|%15s|%36s|%40s|"%(inscription['id'],
                                            inscription['sharing'],
                                            inscription['uuid'],
                                            inscription['packagename'])
                print "+%6s+%15s+%36s+%40s+"%('------',
                                            '---------------',
                                            '------------------------------------',
                                            '----------------------------------------')
            else:
                print "\n No packages have been injected in the database"
        print
        print
        if  errorcreationpackageinbase and opts.verbosereport:
            print "PACKAGE ERROR INJECTION"

            print "+%15s+%36s+%36s+%50s+"%('---------------',
                                            '------------------------------------',
                                            '------------------------------------',
                                            '--------------------------------------------------'\
                                                '------------------------------------')

            for inscription in errorcreationpackageinbase:
                print "|%15s|%36s|%36s|%50s|"%(inscription['sharing'],
                                                inscription['uuid'],
                                                inscription['packagename'],
                                                inscription['error'])
            print "+%15s+%36s+%36s+%50s+"%('---------------',
                                            '------------------------------------',
                                            '------------------------------------',
                                            '--------------------------------------------------'\
                                                '------------------------------------')

        if opts.verbosereport:
            if bad_package:
                print "List Package non conforme"
                for t in bad_package:
                    print t

        if opts.movebadpackage:
            for t in bad_package:
                if opts.verbosereport:
                    print "move %s to packageerror" % os.path.basename(t)
                re = simplecommand("mv %s /var/lib/pulse2/packageerror/"%t)
                if opts.verbeux:
                    if re['code'] != 0:
                        print re['result']

        if opts.linkcreate:
            if opts.verbosereport:
                print "update lien symbolique"
            managepackage.del_link_symbolic()
            managepackage.package_for_deploy_from_partage(verbeux = opts.verbosereport)


    except Exception as e:
        errorstr = "%s" % traceback.format_exc()
        logger.error("\n%s" % (errorstr))
        print "%s" % (errorstr)
        #raise GuacamoleError("MySQL connection error")
        sys.exit(1)
    finally:
        db.close()
