# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This module define the package get API.
It provides methods to get informations on packages.
"""
import logging
import time

from mmc.plugins.msc import MscConfig
from mmc.plugins.msc.database import MscDatabase
import medulla.apis.clients.package_get_api


def cmp(a, b):
    return (a > b) - (a < b)


class PackageGetA(medulla.apis.clients.package_get_api.PackageGetA):
    def __init__(self, server, port=None, mountpoint=None, proto="http", login=""):
        self.logger = logging.getLogger()
        bind = server
        credentials = ""
        if isinstance(server, dict):
            mountpoint = server["mountpoint"]
            port = server["port"]
            proto = server["protocol"]
            bind = server["server"]
            if (
                "username" in server
                and "password" in server
                and server["username"] != ""
            ):
                login = "%s:%s@" % (server["username"], server["password"])
                credentials = "%s:%s" % (server["username"], server["password"])

        self.server_addr = "%s://%s%s:%s%s" % (
            proto,
            login,
            bind,
            str(port),
            mountpoint,
        )
        self.config = MscConfig()
        if self.config.ma_verifypeer:
            medulla.apis.clients.package_get_api.PackageGetA.__init__(
                self,
                credentials,
                self.server_addr,
                self.config.ma_verifypeer,
                self.config.ma_cacert,
                self.config.ma_localcert,
            )
        else:
            medulla.apis.clients.package_get_api.PackageGetA.__init__(
                self, credentials, self.server_addr
            )


def prepareCommand(pinfos, params):
    """
    @param pinfos: getPackageDetail dict content
    @param params: command parameters
    @returns: dict with parameters needed to create the command in database
    @rtype: dict
    """
    ret = {}
    ret["start_file"] = pinfos["command"]["command"]
    ret["do_reboot"] = params["do_reboot"]
    ret["do_reboot"] = (
        (ret["do_reboot"] == "enable" or ret["do_reboot"] == "on")
        and "enable"
        or "disable"
    )
    # TODO : check that params has needed values, else put default one
    # as long as this method is called from the MSC php, the fields should be
    # set, but, if someone wants to call it from somewhere else...
    ret["start_script"] = params["start_script"] == "on" and "enable" or "disable"
    ret["clean_on_success"] = (
        params["clean_on_success"] == "on" and "enable" or "disable"
    )
    ret["do_wol"] = params["do_wol"] == "on" and "enable" or "disable"
    ret["do_wol_on_imaging"] = "disable"
    ret["next_connection_delay"] = params["next_connection_delay"]
    ret["max_connection_attempt"] = params["max_connection_attempt"]
    ret["do_inventory"] = params["do_inventory"] == "on" and "enable" or "disable"
    ret["issue_halt_to"] = params["issue_halt_to"] == ["done"] and "enable" or "disable"
    ret["maxbw"] = params["maxbw"]
    if "state" not in params:
        ret["state"] = "active"
    else:
        ret["state"] = params["state"]

    if "proxy_mode" in params:
        ret["proxy_mode"] = params["proxy_mode"]
    else:
        ret["proxy_mode"] = "none"

    if "deployment_intervals" in params:
        ret["deployment_intervals"] = params["deployment_intervals"]
    else:
        ret["deployment_intervals"] = ""

    if "parameters" in params:
        ret["parameters"] = params["parameters"]
    else:
        ret["parameters"] = ""

    try:
        ret["start_date"] = convert_date(params["start_date"])
    except:
        ret["start_date"] = "0000-00-00 00:00:00"  # ie. "now"

    try:
        ret["end_date"] = convert_date(params["end_date"])
    except:
        ret["end_date"] = "0000-00-00 00:00:00"  # ie. "no end date"

    if "ltitle" in params:
        ret["title"] = params["ltitle"]
    else:
        ret["title"] = ""

    if ret["title"] == None or ret["title"] == "":
        localtime = time.localtime()
        ret["title"] = "%s (%s) - %04d/%02d/%02d %02d:%02d:%02d" % (
            pinfos["label"],
            pinfos["version"],
            localtime[0],
            localtime[1],
            localtime[2],
            localtime[3],
            localtime[4],
            localtime[5],
        )

    if pinfos["files"] != None:
        ret["files"] = [
            hm["id"] + "##" + hm["path"] + "/" + hm["name"] for hm in pinfos["files"]
        ]
    else:
        ret["files"] = ""
    return ret


class SendPackageCommand:
    def __init__(
        self,
        ctx,
        pid,
        targets,
        params,
        mode,
        gid=None,
        bundle_id=None,
        order_in_bundle=None,
        proxies=[],
        cmd_type=0,
    ):
        self.ctx = ctx
        self.pid = pid
        self.targets = targets
        self.params = params.copy()
        self.mode = mode
        self.gid = gid
        self.bundle_id = bundle_id
        self.order_in_bundle = order_in_bundle
        self.proxies = proxies
        self.cmd_type = cmd_type

    def send(self):
        from mmc.plugins.xmppmaster.master.lib.managepackage import apimanagepackagemsc

        self.pinfos = apimanagepackagemsc.getPackageDetail(self.pid)
        return self.setRoot("/var/lib/medulla/packages")

    def setRoot(self, root):
        logging.getLogger().debug(root)
        if self.pid != None and self.pid != "" and not root:
            return self.onError("Can't get path for package %s" % self.pid)
        self.root = root
        # If is an empty Package, avoid file uploading
        if "size" in self.pinfos:
            if self.pinfos["size"] == 0:
                self.pinfos["files"] = None
        # Prepare command parameters for database insertion
        cmd = prepareCommand(self.pinfos, self.params)
        # cmd['maxbw'] is in kbits, set in bits
        cmd["maxbw"] = int(cmd["maxbw"]) * 1024
        cmd["do_wol_with_imaging"] = "disable"
        cmd["do_windows_update"] = "disable"
        _patterns = {
            "do_reboot": cmd["do_reboot"],
            "do_halt": cmd["issue_halt_to"],
            "do_wol": cmd["do_wol"],
            "do_wol_with_imaging": cmd["do_wol_with_imaging"],
            "do_windows_update": cmd["do_windows_update"],
            "do_inventory": cmd["do_inventory"],
        }
        cmd["start_file"], patternActions = MscDatabase().applyCmdPatterns(
            cmd["start_file"], _patterns
        )
        addCmd = MscDatabase().addCommand(  # TODO: refactor to get less args
            self.ctx,
            self.pid,
            cmd["start_file"],
            cmd["parameters"],
            cmd["files"],
            self.targets,  # TODO : need to convert array into something that we can get back ...
            self.mode,
            self.gid,
            cmd["start_script"],
            cmd["clean_on_success"],
            cmd["start_date"],
            cmd["end_date"],
            "root",  # TODO: may use another login name
            cmd["title"],
            patternActions["do_halt"],
            patternActions["do_reboot"],
            patternActions["do_wol"],
            patternActions["do_wol_with_imaging"],
            patternActions["do_windows_update"],
            cmd["next_connection_delay"],
            cmd["max_connection_attempt"],
            patternActions["do_inventory"],
            cmd["maxbw"],
            self.root,
            cmd["deployment_intervals"],
            self.bundle_id,
            self.order_in_bundle,
            cmd["proxy_mode"],
            self.proxies,
            cmd["state"],
            cmd_type=self.cmd_type,
        )
        return addCmd


def convert_date(date="0000-00-00 00:00:00"):
    try:
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.strptime(date, "%Y-%m-%d %H:%M:%S")
        )
    except ValueError:
        try:
            timestamp = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.strptime(date, "%Y/%m/%d %H:%M:%S")
            )
        except ValueError:
            timestamp = "0000-00-00 00:00:00"
    return timestamp
