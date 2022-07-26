#!/usr/bin/python3
# -*- coding: utf-8; -*-
#
# (c) 2016-2022 siveo, http://www.siveo.net
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


import json, os, sys
from datetime import datetime
import traceback

datenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def readjsonfile(namefile):

    with open(namefile) as json_data:
        data_dict = json.load(json_data)
    return data_dict

def writejsonfile(namefile, data):
    with open(namefile, 'w') as json_data:
        json.dump(data, json_data, indent=4)

def sharing_list():
    exclude_name_package = ["sharing", ".stfolder", ".stignore"]
    folderpackages = os.path.join("/", "var", "lib", "pulse2", "packages", "sharing")
    return  [os.path.join(folderpackages, x) for x in os.listdir(folderpackages) \
                if os.path.isdir(os.path.join(folderpackages, x)) \
                    and x not in exclude_name_package]

def packages_list():
    total_packages=[]
    list_of_sharing = sharing_list()
    exclude_name_package = ["sharing", ".stfolder", ".stignore" ]
    folderpackages = os.path.join("/", "var", "lib", "pulse2", "packages", "sharing")

    for share in list_of_sharing:
        total_packages.extend(
            [ os.path.join(share, x) for x in os.listdir(share) \
                if os.path.isdir(os.path.join(share, x)) \
                    and x not in exclude_name_package])
    return total_packages

def main():
    for path_packagename in packages_list():
        jsonfile_name = os.path.join(path_packagename, "conf.json")
        print("We are looking for file %s" % jsonfile_name)
        try:
            jsondata = readjsonfile(jsonfile_name)
            modif = False
            name_of_share = os.path.basename(os.path.dirname(path_packagename))
            if "localisation_server" not in jsondata:
                jsondata['localisation_server'] = name_of_share
                print("The localisation_server key is missing")
                modif = True
            else:
                if jsondata['localisation_server'].strip() == "":
                    jsondata['localisation_server'] = name_of_share
                    print("The localisation_server key is available but empty")
                    modif = True
                elif jsondata['localisation_server'].strip() != name_of_share:
                    print("The localisation_server key is available but with an error. The wrong value is %s" % jsondata['localisation_server'])
                    jsondata['localisation_server'] = name_of_share
                    modif = True
            if "previous_localisation_server" not in jsondata:
                jsondata['previous_localisation_server'] = name_of_share
                print("The previous_localisation_server key is missing")
                modif = True
            if "creation_date" not in jsondata:
                jsondata['creation_date'] = datenow
                print("The creation_date key is missing")
                modif = True
            if "creator" not in jsondata:
                jsondata['creator'] = "oldtonewpackagescript"
                print("The creator key is missing")
                modif = True
            if "metagenerator" not in jsondata:
                print("The metagenerator key is missing")
                jsondata['metagenerator'] = "expert"
            if modif:
                print("save file %s" % jsonfile_name)
                writejsonfile(jsonfile_name, jsondata)
                print("new file \n %s" % json.dumps(jsondata, indent=4))
            else:
                print("Correct values pour ce packages")
            print("The package is now fixed")
        except:
            print("VERIFY JSON FILE %s" % jsonfile_name)
            print("%s" % traceback.format_exc())
    return 0
if __name__ == '__main__':
    sys.exit(main())
