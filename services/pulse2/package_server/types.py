#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
    Pulse2 Package server types
"""

from pulse2.package_server.utilities import md5sum
import pulse2.package_server.common
import urllib.parse
import locale


class Mirror:
    def __init__(self, protocol=None, server=None, port=None, mountpoint=None):
        self.protocol = protocol
        self.server = server
        self.port = port
        self.mountpoint = mountpoint
        self.uuid = "UUID%s" % (mountpoint)

    def toH(self):
        return {
            "protocol": self.protocol,
            "server": self.server,
            "port": str(self.port),
            "mountpoint": self.mountpoint,
            "uuid": self.uuid,
        }

    def fromH(self, h):
        self.protocol = h["protocol"]
        self.server = h["server"]
        self.port = h["port"]
        self.mountpoint = h["mountpoint"]
        self.uuid = "UUID%s" % (self.mountpoint)

    def equal(self, a):
        if (
            self.protocol == a.protocol
            and self.server == a.server
            and self.port == a.port
            and self.mountpoint == a.mountpoint
        ):
            return True
        return False


class Command:
    def __init__(self, name="", command=""):
        self.name = name
        self.command = command

    def toH(self):
        return {"name": self.name, "command": self.command}

    def fromH(self, h):
        if isinstance(h, dict):
            self.name = h["name"]
            self.command = h["command"]
        elif isinstance(h, Command):
            self.name = h.name
            self.command = h.command
        elif isinstance(h, str):
            self.command = h
            self.name = ""

    def to_s(self):
        return self.command

    def equal(self, c):
        if self.name != c.name or self.command != c.command:
            return False
        return True


def getCommandFromH(h):
    cmd = Command()
    cmd.fromH(h)
    return cmd


class A_Packages:
    def __init__(self, a):
        self.packages = a


class Package:
    def __init__(self):
        self.files = AFiles()
        self.specifiedFiles = []

    def init(
        self,
        id,
        label,
        version,
        size,
        description,
        cmd,
        initcmd="",
        precmd="",
        postcmd_ok="",
        postcmd_ko="",
        reboot=0,
        targetos="win",
        entity_id=None,
        Qvendor="",
        Qsoftware="",
        Qversion="",
        boolcnd="",
        licenses="",
        sub_packages=None,
        associateinventory=0,
        metagenerator="standard",
    ):
        # Mutable list sub_packages used as default argument to a method or
        # function
        sub_packages = sub_packages or []
        self.label = label
        self.version = version
        self.size = size
        if self.size is None:
            self.size = 0
        self.description = description
        self.initcmd = getCommandFromH(initcmd)
        self.precmd = getCommandFromH(precmd)
        self.cmd = getCommandFromH(cmd)
        self.postcmd_ok = getCommandFromH(postcmd_ok)
        self.postcmd_ko = getCommandFromH(postcmd_ko)
        self.reboot = reboot
        self.targetos = targetos
        self.id = id
        self.root = ""
        self.Qvendor = Qvendor
        self.Qsoftware = Qsoftware
        self.Qversion = Qversion
        self.boolcnd = boolcnd
        self.licenses = licenses
        self.sub_packages = sub_packages
        self.entity_id = entity_id
        self.associateinventory = associateinventory
        self.metagenerator = metagenerator

    def addFile(self, file):
        self.files.append(file)

    def setFiles(self, files):
        self.files = files

    def hasFile(self):
        return not self.files.isEmpty()

    def setRoot(self, root):
        self.root = root

    def toH(self):
        ret = {
            "label": self.label,
            "version": self.version,
            "size": self.size,
            "id": self.id,
            "description": self.description,
            "installInit": self.initcmd.toH(),
            "preCommand": self.precmd.toH(),
            "command": self.cmd.toH(),
            "postCommandSuccess": self.postcmd_ok.toH(),
            "postCommandFailure": self.postcmd_ko.toH(),
            "reboot": self.reboot,
            "targetos": self.targetos,
            "files": self.files.toH(),
            "Qvendor": self.Qvendor,
            "Qsoftware": self.Qsoftware,
            "Qversion": self.Qversion,
            "boolcnd": self.boolcnd,
            "licenses": self.licenses,
            "sub_packages": self.sub_packages,
            "entity_id": self.entity_id,
            "associateinventory": self.associateinventory,
            "metagenerator": self.metagenerator,
        }
        if self.root != "":
            # The package root is decoded using the current encoding to get a Python
            # unicode string, so that non-ASCII characters can later be successfully
            # written into a XML-RPC stream
            try:
                root = self.root.decode(locale.getpreferredencoding())
            except BaseException:
                root = self.root
            ret["basepath"] = root
        return ret

    def to_h(self):
        return self.toH()

    def fromH(self, h):
        self.label = h["label"]
        self.version = h["version"]
        self.id = h["id"]
        if "size" in h and h["size"] != "":
            self.size = h["size"]
        else:
            self.size = "0"
        if "description" in h:
            self.description = h["description"]
        else:
            self.description = ""

        if "installInit" in h:
            self.initcmd = getCommandFromH(h["installInit"])
        else:
            self.initcmd = Command()
        if "preCommand" in h:
            self.precmd = getCommandFromH(h["preCommand"])
        else:
            self.precmd = Command()
        if "command" in h:
            self.cmd = getCommandFromH(h["command"])
        else:
            self.cmd = Command()
        if "postCommandSuccess" in h:
            self.postcmd_ok = getCommandFromH(h["postCommandSuccess"])
        else:
            self.postcmd_ok = Command()
        if "postCommandFailure" in h:
            self.postcmd_ko = getCommandFromH(h["postCommandFailure"])
        else:
            self.postcmd_ko = Command()
        self.entity_id = 0
        self.reboot = 0
        if "reboot" in h:
            self.reboot = h["reboot"]
        self.targetos = "win"
        if "targetos" in h:
            self.targetos = h["targetos"]
        self.root = ""
        if "basepath" in h:
            self.root = h["basepath"]
        if "Qvendor" in h:
            self.Qvendor = h["Qvendor"]
        if "Qsoftware" in h:
            self.Qsoftware = h["Qsoftware"]
        if "Qversion" in h:
            self.Qversion = h["Qversion"]
        if "boolcnd" in h:
            self.boolcnd = h["boolcnd"]
        if "licenses" in h:
            self.licenses = h["licenses"]
        if "sub_packages" in h:
            self.sub_packages = h["sub_packages"]
        if "entity_id" in h:
            self.entity_id = h["entity_id"]
        if "associateinventory" in h:
            self.associateinventory = h["associateinventory"]
        self.metagenerator = "standard"
        if "metagenerator" in h:
            self.metagenerator = h["metagenerator"]
        return self

    def equal(self, p):
        if (
            self.label != p.label
            or self.version != p.version
            or self.size != p.size
            or self.id != p.id
            or not (self.initcmd.equal(p.initcmd))
            or not (self.precmd.equal(p.precmd))
            or not (self.cmd.equal(p.cmd))
            or not (self.postcmd_ok.equal(p.postcmd_ok))
            or not (self.postcmd_ko.equal(p.postcmd_ko))
            or self.description != p.description
        ):
            return False
        # TODO check files
        return True


class AFiles:
    def __init__(self):
        self.internals = []

    def append(self, elt):
        self.internals.append(elt)

    def isEmpty(self):
        return len(self.internals) == 0

    def toH(self):
        return [x.toH() for x in self.internals]

    def to_h(self):
        return self.toH()

    def toURI(self, mp=None):
        if mp is None:
            return [x.toURI() for x in self.internals]
        else:
            d = pulse2.package_server.common.Common().h_desc(mp)
            if "mirror_url" in d and d["mirror_url"] != "":
                where = d["mirror_url"]
            elif "url" in d and d["url"] != "":
                where = "%s_files" % (d["url"])
            else:
                where = "%s://%s:%s%s_files" % (
                    d["proto"],
                    d["server"],
                    str(d["port"]),
                    d["mp"],
                )
            return [x.toURI(mp, where) for x in self.internals]


class File:
    def __init__(
        self, name=None, path="/", checksum=None, size=0, access=None, id=None
    ):
        if access is None:  # dont modify the default value!
            access = {}
        if "mirror" in access:
            self.where = access["mirror"]
        else:
            if "proto" not in access:
                access["proto"] = "http"
            if "file_access_uri" not in access:
                access["file_access_uri"] = "127.0.0.1"
            if "file_access_port" not in access:
                access["file_access_port"] = "80"
            if "file_access_path" not in access:
                access["file_access_path"] = ""
            self.where = "%s://%s:%s%s" % (
                access["proto"],
                access["file_access_uri"],
                str(access["file_access_port"]),
                access["file_access_path"],
            )

        self.name = name
        self.path = path
        self.checksum = checksum
        self.size = size
        if id is None:
            self.id = md5sum(
                "%s%s" % (self.toS().replace("\\", "/"), str(self.checksum))
            )
        else:
            self.id = id

    def toURI(self, mp=None, where=None):
        if mp is None:
            return (
                "%s%s/%s" % (self.where, self.path.replace("\\", "/"), self.name)
            ).replace(" ", "%20")
        else:
            if where is None:
                d = pulse2.package_server.common.Common().h_desc(mp)
                if "mirror_url".d and d["mirror_url"] != "":
                    where = d["mirror_url"]
                elif "mirror_mp".d and d["mirror_mp"] != "":
                    where = "%s://%s:%s%s" % (
                        d["proto"],
                        d["server"],
                        str(d["port"]),
                        d["mirror_mp"],
                    )
                else:
                    where = "%s://%s:%s%s_files" % (
                        d["proto"],
                        d["server"],
                        str(d["port"]),
                        d["mp"],
                    )
            ret = where + urllib.parse.quote(
                "%s/%s" % (self.path.replace("\\", "/"), self.name)
            )
            return ret

    def toS(self):
        return "%s/%s" % (self.path, self.name)

    def to_s(self):
        return self.toS()

    def toH(self):
        # The file name and path are decoded using the current encoding to get a
        # Python unicode string, so that non-ASCII characters can be later successfully
        # written into a XML-RPC stream
        try:
            name = self.name.decode(locale.getpreferredencoding())
        except BaseException:
            name = self.name
        try:
            path = self.path.decode(locale.getpreferredencoding())
        except BaseException:
            path = self.path
        return {"name": name, "path": path, "id": self.id}

    def to_h(self):
        return self.toH()


class Machine:
    def __init__(self, name=None, uuid=None):
        self.name = name
        self.uuid = uuid

    def uuid(self):
        return self.uuid

    def to_h(self):
        return {"name": self.name, "uuid": self.uuid}

    def from_h(self, h):
        if "name" in h:
            self.name = h["name"]
        else:
            self.name = ""
        try:
            self.uuid = h["uuid"]
        except Exception as e:
            raise Exception("machine must have an uuid: " + str(e))
        return self

    def equal(self, a):
        return self.name == a.name


class User:
    def __init__(self, name=None, uuid=None):
        self.name = name
        self.uuid = name

    def to_h(self):
        return {"name": self.name, "uuid": self.uuid}

    def from_h(self, h):
        if "name" in h:
            self.name = h["name"]
        else:
            self.name = ""
        try:
            self.uuid = h["uuid"]
        except Exception as e:
            raise Exception("user must have an uuid: " + str(e))
        return self

    def equal(self, a):
        return self.name == a.name and self.uuid == a.uuid
