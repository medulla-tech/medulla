#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
    Pulse2 package parser module
"""
import logging
import os
from xml.dom import minidom
import json
from pulse2.package_server.types import Package


class PackageParser:
    def init(self, config):
        self.logger = logging.getLogger()
        if 1:  # config.parser == None or config.parser == 'XML':
            self.parser = PackageParserJSON()
        else:
            self.logger.error(
                "don't know how to parse this kind of package configuration %s"
                % (config.parser)
            )
            raise Exception("UKNPKGCNF")

    def parse(self, file):
        if isinstance(file, str):
            return self.parser.parse_str(file)
        else:
            raise Exception("UKNPARSEMETHOD")

    def concat(self, package):
        return self.parser.to_json(package)

    def concat_xmppdeploy(self, package):
        return self.parser.to_json_xmppdeploy(package)


class PackageParserXML:
    def parse_str(self, file):
        xml = None
        try:
            if os.path.exists(file):
                xml = minidom.parse(file)
            else:
                xml = minidom.parseString(file)

            # parsing routines
            self.logger = logging.getLogger()
            root = xml.getElementsByTagName("package")
            if len(root) != 1:
                raise Exception("CANTPARSE")
            root = root[0]
            pid = root.getAttribute("id")

            tmp = root.getElementsByTagName("name")[0]
            name = tmp.firstChild.wholeText.strip()
            version = root.getElementsByTagName("version")[0]
            tmp = version.getElementsByTagName("numeric")[0]
            tmp = version.getElementsByTagName("label")[0]
            if tmp.firstChild is not None:
                v_txt = tmp.firstChild.wholeText.strip()
            else:
                v_txt = "0"
            tmp = root.getElementsByTagName("description")
            if len(tmp) == 1 and tmp[0].firstChild is not None:
                tmp = tmp[0]
                desc = tmp.firstChild.wholeText.strip()
            else:
                desc = ""

            licenses = ""
            tmp = root.getElementsByTagName("licenses")
            if len(tmp) == 1 and tmp[0].firstChild is not None:
                tmp = tmp[0]
                licenses = tmp.firstChild.wholeText.strip()

            cmd = root.getElementsByTagName("commands")[0]
            reboot = 0
            if cmd.hasAttribute("reboot"):
                reboot = cmd.getAttribute("reboot")

            cmds = {}
            for c in [
                "installInit",
                "preCommand",
                "command",
                "postCommandSuccess",
                "postCommandFailure",
            ]:
                tmp = cmd.getElementsByTagName(c)
                if len(tmp) == 1 and tmp[0].firstChild is not None:
                    command = tmp[0].firstChild.wholeText.strip()
                    if tmp[0].hasAttribute("name"):
                        ncmd = tmp[0].getAttribute("name")
                    else:
                        ncmd = ""
                    cmds[c] = {"command": command, "name": ncmd}
                else:
                    cmds[c] = ""

            associateinventory = 0
            tmp = root.getElementsByTagName("associateinventory")
            if len(tmp) == 1 and tmp[0].firstChild is not None:
                tmp = tmp[0]
                associateinventory = tmp.firstChild.wholeText.strip()

            query = root.getElementsByTagName("query")
            queries = {"Qvendor": "", "Qsoftware": "", "Qversion": "", "boolcnd": ""}
            if query.length >= 1 and query[0].firstChild:
                for k in queries:
                    tmp = query[0].getElementsByTagName(k)
                    if tmp.length >= 1 and tmp[0].firstChild:
                        queries[k] = tmp[0].firstChild.wholeText.strip()

            p = Package()
            p.init(
                pid,
                name,
                v_txt,
                0,
                desc,
                cmds["command"],
                cmds["installInit"],
                cmds["preCommand"],
                cmds["postCommandSuccess"],
                cmds["postCommandFailure"],
                reboot,
                0,
                queries["Qvendor"],
                queries["Qsoftware"],
                queries["Qversion"],
                queries["boolcnd"],
                licenses,
                [],
                associateinventory,
            )
        except Exception as e:
            logging.getLogger().error("parse_str failed")
            logging.getLogger().error(e)
            p = None

        return p

    def to_xml(self, package):
        """
        create XML document for the package
        """

        imp = minidom.getDOMImplementation("")
        # Create document type
        dt = imp.createDocumentType("package", "", "")
        dt.internalSubset = self.doctype()

        # Create XML document with this document type
        doc = imp.createDocument("", "package", dt)

        docr = doc.documentElement
        pid = doc.createAttribute("id")
        pid.value = package.id
        docr.setAttributeNode(pid)

        name = doc.createElement("name")
        name.appendChild(doc.createTextNode(package.label))
        docr.appendChild(name)

        version = doc.createElement("version")
        numeric = doc.createElement("numeric")
        numeric.appendChild(doc.createTextNode(str(package.version)))
        label = doc.createElement("label")
        label.appendChild(doc.createTextNode(str(package.version)))
        version.appendChild(numeric)
        version.appendChild(label)
        docr.appendChild(version)

        description = doc.createElement("description")
        description.appendChild(doc.createTextNode(package.description))
        docr.appendChild(description)

        licenses = doc.createElement("licenses")
        licenses.appendChild(doc.createTextNode(package.licenses))
        docr.appendChild(licenses)

        commands = doc.createElement("commands")
        reboot = doc.createAttribute("reboot")
        reboot.value = str(package.reboot)
        commands.setAttributeNode(reboot)

        precommand = doc.createElement("preCommand")
        precommandname = doc.createAttribute("name")
        precommandname.value = package.precmd.name
        precommand.setAttributeNode(precommandname)
        precommand.appendChild(doc.createTextNode(package.precmd.command))

        installinit = doc.createElement("installInit")
        installinitname = doc.createAttribute("name")
        installinitname.value = package.initcmd.name
        installinit.setAttributeNode(installinitname)
        installinit.appendChild(doc.createTextNode(package.initcmd.command))

        command = doc.createElement("command")
        commandname = doc.createAttribute("name")
        commandname.value = package.cmd.name
        command.setAttributeNode(commandname)
        command.appendChild(doc.createTextNode(package.cmd.command))

        postsuccess = doc.createElement("postCommandSuccess")
        postsuccessname = doc.createAttribute("name")
        postsuccessname.value = package.postcmd_ok.name
        postsuccess.setAttributeNode(postsuccessname)
        postsuccess.appendChild(doc.createTextNode(package.postcmd_ok.command))

        postfailure = doc.createElement("postCommandFailure")
        postfailurename = doc.createAttribute("name")
        postfailurename.value = package.postcmd_ko.name
        postfailure.setAttributeNode(postfailurename)
        postfailure.appendChild(doc.createTextNode(package.postcmd_ko.command))

        commands.appendChild(precommand)
        commands.appendChild(installinit)
        commands.appendChild(command)
        commands.appendChild(postsuccess)
        commands.appendChild(postfailure)

        docr.appendChild(commands)

        associateinventory = doc.createElement("associateinventory")
        appenchild = doc.createTextNode(str(package.associateinventory))
        associateinventory.appendChild(appenchild)
        docr.appendChild(associateinventory)

        query = doc.createElement("query")
        Qvendor = doc.createElement("Qvendor")
        Qvendor.appendChild(doc.createTextNode(package.Qvendor))
        query.appendChild(Qvendor)
        Qsoftware = doc.createElement("Qsoftware")
        Qsoftware.appendChild(doc.createTextNode(package.Qsoftware))
        query.appendChild(Qsoftware)
        Qversion = doc.createElement("Qversion")
        Qversion.appendChild(doc.createTextNode(package.Qversion))
        query.appendChild(Qversion)
        boolcnd = doc.createElement("boolcnd")
        boolcnd.appendChild(doc.createTextNode(package.boolcnd))
        query.appendChild(boolcnd)

        docr.appendChild(query)

        return doc.toprettyxml(encoding="utf-8")

    def doctype(self):
        return """
    <!ELEMENT package (name,\
                       version,\
                       description?,\
                       commands,\
                       files?,\
                       associateinventory,\
                       query?,\
                       licenses?)>
    <!ATTLIST package id ID #REQUIRED>

    <!ELEMENT name (#PCDATA)>
    <!ELEMENT version (numeric,label)>
    <!ELEMENT numeric (#PCDATA)>
    <!ELEMENT label (#PCDATA)>
    <!ELEMENT description (#PCDATA)>
    <!ELEMENT licenses (#PCDATA)>

    <!ELEMENT commands (preCommand?,installInit?,command,postCommandSuccess?,postCommandFailure?)>
    <!ATTLIST commands reboot (0|1) "0">
    <!ELEMENT preCommand (#PCDATA)>
    <!ATTLIST preCommand name CDATA "">
    <!ELEMENT installInit (#PCDATA)>
    <!ATTLIST installInit name CDATA "">
    <!ELEMENT command (#PCDATA)>
    <!ATTLIST command name CDATA "">
    <!ELEMENT postCommandSuccess (#PCDATA)>
    <!ATTLIST postCommandSuccess name CDATA "">
    <!ELEMENT postCommandFailure (#PCDATA)>
    <!ATTLIST postCommandFailure name CDATA "">

    <!ELEMENT files (file*)>
    <!ELEMENT file (#PCDATA)>
    <!ATTLIST file fid ID #IMPLIED>
    <!ATTLIST file md5sum CDATA "">
    <!ATTLIST file size CDATA "">
    <!ELEMENT associateinventory (#PCDATA)>
    <!ELEMENT query (Qvendor, Qsoftware, Qversion, boolnd)>
    <!ELEMENT Qvendor (#PCDATA)>
    <!ELEMENT Qsoftware (#PCDATA)>
    <!ELEMENT Qversion (#PCDATA)>
    <!ELEMENT boolcnd (#PCDATA)>
"""


class PackageParserJSON:
    def parse_str(self, file):
        try:
            # Nonesense: we don't know if file is a path or content ??!! wtf
            if os.path.exists(file):
                try:
                    data = json.loads(open(file).read())
                except IOError:
                    pass
                except BaseException:
                    pass
            else:
                data = json.loads(file)

            # parsing routines
            self.logger = logging.getLogger()
            try:
                pid = data["id"]

                name = data["name"].strip()

                v_txt = data["version"] or "0"
                desc = data["description"]
                cmds = data["commands"]
                reboot = data["reboot"] or 0
                try:
                    targetos = data["targetos"]
                except KeyError:
                    targetos = "win"

                try:
                    sub_packages = data["sub_packages"]
                except KeyError:
                    sub_packages = []

                try:
                    entity_id = data["entity_id"]
                except KeyError:
                    entity_id = 0

                try:
                    metagenerator = data["metagenerator"]
                except KeyError:
                    metagenerator = "standard"

                # Inventory section
                licenses = data["inventory"]["licenses"]
                associateinventory = data["inventory"]["associateinventory"]
                queries = data["inventory"]["queries"]

            except KeyError:
                raise Exception("CANTPARSE")

            p = Package()
            p.init(
                pid,
                name,
                v_txt,
                0,
                desc,
                cmds["command"],
                cmds["installInit"],
                cmds["preCommand"],
                cmds["postCommandSuccess"],
                cmds["postCommandFailure"],
                reboot,
                targetos,
                entity_id,
                queries["Qvendor"],
                queries["Qsoftware"],
                queries["Qversion"],
                queries["boolcnd"],
                licenses,
                sub_packages,
                associateinventory,
                metagenerator,
            )
        except Exception as e:
            logging.getLogger().error("parse_str failed")
            logging.getLogger().error(e)
            p = None

        return p

    def to_json(self, package):
        """
        create JSON document for the package
        """

        data = {}
        data["id"] = package.id
        data["name"] = package.label
        data["version"] = str(package.version)
        data["description"] = package.description
        data["reboot"] = package.reboot
        data["targetos"] = package.targetos
        data["metagenerator"] = package.metagenerator

        # Sub packages if exists
        data["sub_packages"] = package.sub_packages

        # Entity info if exist
        data["entity_id"] = package.entity_id

        # Inventory section
        data["inventory"] = {}
        data["inventory"]["licenses"] = package.licenses
        data["inventory"]["associateinventory"] = str(package.associateinventory)
        data["inventory"]["queries"] = {
            "Qvendor": package.Qvendor,
            "Qsoftware": package.Qsoftware,
            "Qversion": package.Qversion,
            "boolcnd": package.boolcnd,
        }

        # Commands section
        data["commands"] = {}
        data["commands"]["preCommand"] = {
            "name": package.precmd.name,
            "command": package.precmd.command,
        }
        data["commands"]["installInit"] = {
            "name": package.initcmd.name,
            "command": package.initcmd.command,
        }
        data["commands"]["command"] = {
            "name": package.cmd.name,
            "command": package.cmd.command,
        }
        data["commands"]["postCommandSuccess"] = {
            "name": package.postcmd_ok.name,
            "command": package.postcmd_ok.command,
        }
        data["commands"]["postCommandFailure"] = {
            "name": package.postcmd_ko.name,
            "command": package.postcmd_ko.command,
        }

        return json.dumps(data, sort_keys=True, indent=4, separators=(",", ": "))

    def to_json_xmppdeploy(self, package):
        """
        create JSON xmppdeploy descriptor
        """

        data = {}

        data["metaparameter"] = {}
        data["metaparameter"][package.targetos] = {}
        data["metaparameter"][package.targetos]["label"] = {}

        data["info"] = {}
        data["info"]["name"] = str(
            package.label + " " + package.version + " (" + package.id + ")"
        )
        data["info"]["software"] = package.label
        data["info"]["version"] = str(package.version)
        data["info"]["description"] = package.description
        data["info"]["transferfile"] = True
        data["info"]["methodetransfert"] = "pushrsync"
        data["info"]["Dependency"] = []
        data["info"]["metagenerator"] = package.metagenerator

        data[package.targetos] = {}
        data[package.targetos]["sequence"] = []
        seq_count = 0

        sequence = {}
        sequence["step"] = seq_count
        sequence["action"] = "actionprocessscriptfile"
        sequence["script"] = package.cmd.command
        sequence["actionlabel"] = "EXECUTE_SCRIPT"
        sequence["typescript"] = "Batch"
        sequence["codereturn"] = ""
        sequence["@resultcommand"] = "@resultcommand"
        sequence["success"] = seq_count + 1
        if package.reboot:
            sequence["error"] = seq_count + 3
        else:
            sequence["error"] = seq_count + 2
        data[package.targetos]["sequence"].append(sequence)
        data["metaparameter"][package.targetos]["label"]["EXECUTE_SCRIPT"] = seq_count
        seq_count += 1

        if package.reboot:
            sequence = {}
            sequence["step"] = seq_count
            sequence["action"] = "actionrestart"
            sequence["actionlabel"] = "REBOOT"
            data[package.targetos]["sequence"].append(sequence)
            data["metaparameter"][package.targetos]["label"]["REBOOT"] = seq_count
            seq_count += 1

        sequence = {}
        sequence["step"] = seq_count
        sequence["action"] = "actionsuccescompletedend"
        sequence["actionlabel"] = "END_SUCCESS"
        data[package.targetos]["sequence"].append(sequence)
        data["metaparameter"][package.targetos]["label"]["END_SUCCESS"] = seq_count
        seq_count += 1

        sequence = {}
        sequence["step"] = seq_count
        sequence["action"] = "actionerrorcompletedend"
        sequence["actionlabel"] = "END_ERROR"
        data[package.targetos]["sequence"].append(sequence)
        data["metaparameter"][package.targetos]["label"]["END_ERROR"] = seq_count

        data["metaparameter"]["os"] = []
        data["metaparameter"]["os"].append(package.targetos)

        return json.dumps(data, sort_keys=True, indent=4, separators=(",", ": "))
