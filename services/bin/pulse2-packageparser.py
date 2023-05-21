#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""This package parse the packages and generate a rapport with errors found"""

import logging
import json
import os


class Package:
    """Data structure for the parsed packages"""

    logger = logging.getLogger("PackageParser")

    def __init__(self, path="", uuid="", files=[]):
        """
        Initialize a Package class. This class is used by PackageParser.
        Params:
            path: string of the absolute path to the package root dir
            uuid: string of the uuid name of the package
            files: list of the files name contained into the package
        """

        self.path = path
        self.uuid = uuid
        self.files = files
        self.summary = {}
        self.info = {}
        self.metaparameter = {}
        self.sequence = {}
        self.name = ""

    def test_files_list(self):
        """The files list of each package is tested by this method.
        Returns:
            True if the package is not empty and the main files are present
            else returns False
        """
        self.logger.info("\n")
        self.logger.info("Test if the package %s contains the main files", self.uuid)
        flag = True
        if not self.files:
            self.logger.error("The package %s is empty", self.uuid)
            self.to_summary("error", "The package is empty")
            return False
        # Check if the main files of the package are here
        if "conf.json" not in self.files:
            self.logger.error("The file conf.json is missing")
            self.to_summary("error", "The file conf.json is missing")
            flag = False
        if "xmppdeploy.json" not in self.files:
            self.logger.error("The file xmppdeploy.json is missing")
            self.to_summary("error", "The file xmppdeploy.json is missing")
            flag = False
        return flag

    def test_json_files(self):
        """Launch the tests for a uniq package.
        Returns :
            True if the package is valid or False if the package in wrong."""

        for file in self.files:
            if file.endswith(".json"):
                self.logger.info("Test if %s / %s is a valid json", self.uuid, file)
                with open(os.path.join(self.path, file), "r") as filestream:
                    content = filestream.read()
                    filestream.close()
                    try:
                        json_content = json.loads(content)
                        if file == "xmppdeploy.json":
                            self.info = json_content["info"]
                            self.metaparameter = json_content["metaparameter"]
                            self.name = self.info["name"]

                            # self.sequence = json_content[self.metaparameter['os'][0]]

                    except ValueError:
                        self.to_summary(
                            "error",
                            "The json file {0} contains an invalid json".format(file),
                        )
                        self.logger.error(
                            "The json file % contains an invalid json", file
                        )
                        return False
        return True

    def to_summary(self, message_type, message):
        """Store what append in the summary dict
        Params:
            package: string of the uuid
            message_type: string of the type of message (error, warning, info ...)
            message : string of what happens"""

        if self.uuid in self.summary:
            if message_type in self.summary[self.uuid]:
                self.summary[self.uuid][message_type].append(message)
            else:
                self.summary[self.uuid][message_type] = [message]
        else:
            self.summary[self.uuid] = {message_type: [message]}


class PackageParser:
    """PackageParser manage the tests for the packages"""

    excluded_list = [".stfolder", "sharing", ".stignore"]

    def __init__(self):
        index = 0
        log_file = os.path.join("/", "var", "log", "mmc", "packageparser.log")
        self.log_file = log_file
        logfile_exists = os.path.isfile(self.log_file)
        if logfile_exists is True:
            while logfile_exists:
                index += 1
                self.log_file = "%s.%s" % (log_file, index)
                logfile_exists = os.path.isfile(self.log_file)

        self.package_folder = ["/", "var", "lib", "pulse2", "packages"]
        self.packages_list = []
        self.summary = {"valids": [], "invalids": []}
        self.counts = {"valids": 0, "invalids": 0, "total": 0}

        self.logger = logging.getLogger("PackageParser")
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG)

    def get_package_folder(self):
        """Format the packages folder
        Returns :
            string of the packages folder"""
        tmp = ""
        for element in self.package_folder:
            tmp = os.path.join(tmp, element)
        return tmp

    def test_dependencies(self, package):
        """The dependencies of a package can be corrupted, this method prevent
        for this case.
        Param:
            package: Package object which will be tested
        Returns:
            True if the specified package has no corrupted dependencies"""
        dependencies_list = package.info["Dependency"]
        uuids_list = [package.uuid for package in self.packages_list]
        flag = True

        if not dependencies_list:
            flag = True
        else:
            for dependency in dependencies_list:
                if not dependency in uuids_list:
                    self.logger.error(
                        "The dependency %s for the package %s (%s) is not existing",
                        dependency,
                        package.uuid,
                        package.name,
                    )
                    package.to_summary(
                        "error", "The dependency {0} is not existing".format(dependency)
                    )
                    flag = False
        return flag

    def run(self):
        """The run function is the start point of the program."""

        # Reset the log file
        with open(self.log_file, "w") as file_log:
            file_log.write("")
            file_log.close()

        self.logger.info("=== Test the packages directory ===")

        if os.path.isdir(self.get_package_folder()) is True:
            self.logger.info(
                "The package directory %s is existing", self.get_package_folder()
            )
            exists = True
        else:
            self.logger.error(
                "The directory %s is not existing", self.get_package_folder()
            )
            exists = False

        if exists:
            self.logger.info("Get the packages list")
            plist = os.listdir(self.get_package_folder())

            for package in plist:
                # Blacklist some names
                if package not in PackageParser.excluded_list:
                    files_list = os.listdir(
                        os.path.join(self.get_package_folder(), package)
                    )
                    tmp = Package(
                        path=os.path.join(self.get_package_folder(), package),
                        uuid=package,
                        files=files_list,
                    )

                    self.packages_list.append(tmp)
                    self.logger.info("\t %s", package)

            self.logger.info("\n=== Test the packages ===")
            # At this point of the program the packages list is generated
            for package in self.packages_list:
                self.counts["total"] += 1
                if package.test_files_list():
                    self.logger.info(
                        "The main files of the package %s are present", package.uuid
                    )
                    if package.test_json_files():
                        self.logger.info(
                            "The files of the package %s (%s) seems to be ok",
                            package.uuid,
                            package.name,
                        )
                        self.test_dependencies(package)
                        self.counts["valids"] += 1
                        self.summary["valids"].append({"uuid": package.uuid})
                    else:
                        self.summary["invalids"].append(
                            {"uuid": package.uuid, "msg": "json file not ok"}
                        )
                        self.counts["invalids"] += 1
                else:
                    self.summary["invalids"].append(
                        {"uuid": package.uuid, "msg": "missing json files"}
                    )
                    self.counts["invalids"] += 1
            self.logger.info("\n")
            self.logger.info("====== Counts ======")
            self.logger.info("Total : %s" % self.counts["total"])
            self.logger.info("Valids : %s" % self.counts["valids"])
            self.logger.info("Invalids : %s" % self.counts["invalids"])

            self.logger.info("\n")
            self.logger.info("====== Invalids ======")
            for element in self.summary["invalids"]:
                self.logger.info("%s : %s" % (element["uuid"], element["msg"]))

            self.logger.info("\n")
            self.logger.info("====== Valids ======")
            for element in self.summary["valids"]:
                self.logger.info("%s" % (element["uuid"]))


if __name__ == "__main__":
    checker = PackageParser()
    checker.run()
    # To use the package report into script.
    # All the information are sent to /var/log/mmc/package/packageparser.log
    print("A report is generated into the %s file." % checker.log_file)
