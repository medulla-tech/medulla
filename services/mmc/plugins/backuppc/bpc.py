#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import os.path
import os
from pyquery import PyQuery as pq
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.parse
import re, string
import logging
import tempfile
import time
import subprocess
from shutil import rmtree
import fnmatch
from random import randint

# Twisted
from twisted.python import threadable

threadable.init(1)
from twisted.internet.threads import deferToThread

deferred = deferToThread.__get__  # Create an alias for deferred functions

# BackupPC DB
from pulse2.database.backuppc import BackuppcDatabase

# BackupPC Config
from mmc.plugins.backuppc.config import BackuppcConfig

# Machine info
from mmc.plugins.glpi.database import Glpi

logger = logging.getLogger()

# Error consts
_FORMAT_ERROR = {
    "err": 14,
    "errtext": "Incorrect format, check if the version of BackupPC is supported",
}
_CONNECTION_ERROR = {"err": 10, "errtext": "Unable to connect to BackupPC server."}
_ENCODING_ERROR = {"err": 19, "errtext": "Encoding error."}
_UNKNOWN_ERROR = {
    "err": 20,
    "errtext": "Unable to perform selected action, unknown error occured.",
}

# Global vars
download_status = {}
file_index = {}

# ==========================================================================
# BACKUP SERVER I/O FUNCTIONS
# ==========================================================================


def getBackupServerByUUID(uuid):
    """
    @param uuid: Machine uuid
    @type uuid: str

    @returns: the Backup Server URL for the specified UUID
    @rtype: str
    """
    # return 'localhost/backuppc/index.cgi'
    from pulse2.managers.location import ComputerLocationManager

    try:
        entity_uuid = ComputerLocationManager().getMachinesLocations([uuid])[uuid][
            "uuid"
        ]
        parent_entities = [
            entity_uuid
        ] + ComputerLocationManager().getLocationParentPath(entity_uuid)
    except:
        logger.error("Cannot get Entity for this UUID (%s)" % uuid)
        return ""
    url = ""
    for _uuid in parent_entities:
        url = BackuppcDatabase().get_backupserver_by_entity(_uuid)
        if url:
            return url
    # If we're here, Backup host not mapped
    logger.error(
        "Cannot get BackupServer for this UUID (%s), please check Entity <> BackupServer mappings."
        % uuid
    )
    return ""


def dictToURL(params):
    s = ""
    for k in list(params.keys()):
        if isinstance(params[k], type([])):
            for val in params[k]:
                if val is None:
                    s += "&%s=" % k
                else:
                    s += "&%s=%s" % (k, val)
            del params[k]
    return urllib.parse.urlencode(params) + s


def send_request(params, url=""):
    """Send a request to BackupPC web interface.
    params [dict]: params to be transmitten.
    url : (Default empty) BackupPC Server url, if not specified
    get the default server for the host entity.
    If success, returns HTML response.
    """
    # Getting BackupServer URL
    url = url or getBackupServerByUUID(params["host"].upper())
    if not url:
        return
    # Host to lower case
    if "host" in params:
        params["host"] = params["host"].lower()
    # Converting params dict to an http query string
    params_str = dictToURL(params)
    # Sending a POST request
    try:
        response = urllib.request.urlopen(url, params_str)
        return str(response.read(), "utf8").encode("ascii", "xmlcharrefreplace")
    except:
        logger.error("Unable to connect to BackupPC server : %s" % url)
        return ""


# ==========================================================================
# GLOBAL PARSING FUNCTIONS
# ==========================================================================


def getTableByTitle(html, title):
    d = pq(html)
    # Searching for the right title
    titles = d("div.h2")
    div = []
    for i in range(len(title)):
        if titles.eq(i).text() == title:
            div = titles.eq(i)
            break
    if div:
        return div.nextAll().filter("table").eq(0)
    else:
        return []


def getTableHeader(table):
    header = table.find(".tableheader").find("td")
    hd = []
    for i in range(len(header)):
        hd += [header.eq(i).text()]
    return hd


def getTableContent(table):
    count = len(table.find("tr"))
    # Init filecount var and files dictionnary
    lines = []
    for i in range(count):
        if table.find("tr").eq(i).attr("class") == "tableheader":
            continue
        cols = table.find("tr").eq(i).find("td")
        line = []
        for i in range(len(cols)):
            line += [cols.eq(i).text()]
        lines += [line]
    return [list(i) for i in zip(*lines)]


def getHTMLerr(html):
    d = pq(html)
    page_title = d("title").text()
    if page_title == "BackupPC: Error":
        # Printing error text
        logger.warning(d(".h1").text())
        return {"err": 15, "errtext": d(".h1").text()}
    else:
        if len(d(".editError")):
            errors = []
            for i in range(len(d(".editError"))):
                errors.append(d(".editError").eq(i).text())
            error_text = "\n".join(errors)
            logger.warning(error_text)
            return {"err": 15, "errtext": error_text}


# ==========================================================================
# MAIN BACKUPPC FUNCTIONS
# ==========================================================================


def get_host_list(pattern=""):
    """Get all configured hosts on BackupPC server.
    pattern (optional): to specify if a search is done.
    """
    html = send_request({}, "localhost/backuppc/index.cgi")
    if not html:
        return _CONNECTION_ERROR
    d = pq(html)
    hosts = []
    options = d("select:first").find("option")
    if not options:
        return _FORMAT_ERROR
    for i in range(len(options)):
        if options.eq(i).attr("value") != "#" and pattern in options.eq(i).text():
            hosts += [options.eq(i).text()]
    return {"err": 0, "data": hosts}


def get_backup_list(host):
    """Get available restore point for the specified host.
    host: host name or UUID (depending on your config).
    """
    html = send_request({"host": host})
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    tb_bak_sum = getTableByTitle(html, "Backup Summary")
    if tb_bak_sum:
        bk_list = getTableContent(tb_bak_sum)
        return {"err": 0, "data": bk_list}
    else:
        return _FORMAT_ERROR


def get_share_names(host, backup_num):
    # Setting params
    params = {}
    params["action"] = "browse"
    params["host"] = host
    params["num"] = backup_num
    # Sending request
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    # Setting a pquery object on html
    d = pq(html)
    # isolating sharestable
    sharestable = d("table:first").find("table:first")
    if not sharestable:
        return _FORMAT_ERROR
    lines = sharestable.find("tr")
    # init share names array
    share_names = []
    for i in range(len(lines)):
        if lines.eq(i).text()[0] == "/":
            share_names = share_names + [lines.eq(i).text()]
    return {"err": 0, "data": share_names}


def list_files(host, backup_num, share_name, dir, filter, recursive=0):
    """Returns .
    pattern (optional): to specify if a search is done.
    """
    # Setting params
    params = {"action": "browse", "host": host, "num": backup_num, "share": share_name}
    params["dir"] = dir if recursive == 2 else dir.encode("utf8", "ignore")
    # Sending request
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    # Setting a pquery object on html response
    d = pq(html)
    # Isolating filetable
    filetable = d("table:first").find("table:last")
    if not filetable:
        return _FORMAT_ERROR
    # Init filecount var and files dictionnary
    linecount = len(filetable.find("tr"))
    result = [[], [], [], [], [], [], []]
    for i in range(1, linecount):
        cols = filetable.find("tr").eq(i).find("td")
        if len(cols) == 6:
            if filter in cols.eq(0).text():
                # Attributes
                result[0] += [cols.eq(0).text().replace("\xa0", " ")]  # filename
                result[1] += [cols.eq(0).find("input").val()]  # filepath
                result[2] += [cols.eq(3).text()]  # type (int)
                result[3] += [cols.eq(1).text()]  # type (str)
                result[4] += [cols.eq(2).text()]  # mode
                result[5] += [cols.eq(4).text()]  # size
                result[6] += [cols.eq(5).text()]  # last modification
            # if recursive is on, we add directories to dirs array to browse them
            if recursive and cols.eq(1).text() == "dir":
                subdir = urllib.parse.unquote(cols.eq(0).find("input").val())
                sub = list_files(host, backup_num, share_name, subdir, filter, 2)
                if not sub["err"]:
                    for i in range(len(sub["data"])):
                        result[i] += sub["data"][i]
    return {"err": 0, "data": result}


def get_file_versions(host, share_name, filepath):
    # Result array
    backup_nums = []
    datetimes = []
    ages = []
    # Getting available restore points for the host
    restore_points = get_backup_list(host)
    if restore_points["err"]:
        return restore_points
    # Define filename and file path
    filename = os.path.basename(filepath)
    dir = os.path.dirname(filepath)
    # Testing if file is available in that restore point
    for i in range(len(restore_points["data"][0])):
        point = restore_points["data"][0][i]
        datetime = restore_points["data"][4][i]
        age = restore_points["data"][6][i]
        list = list_files(host, point, share_name, dir, filename)
        if "data" in list(list.keys()) and filename in list["data"][0]:
            backup_nums += [point]
            datetimes += [datetime]
            ages += [age]
    return {
        "err": "0",
        "backup_nums": backup_nums,
        "datetimes": datetimes,
        "ages": ages,
    }


# ==========================================================================
# RESTORE FUNCTIONS
# ==========================================================================


@deferred
def download_file(filepath, params):
    url = getBackupServerByUUID(params["host"])
    # Host to lower case
    if "host" in params:
        params["host"] = params["host"].lower()
    # Converting params dict to an http get string
    try:
        params_str = urllib.parse.urlencode(params)
    except:
        return _ENCODING_ERROR
    #
    try:
        response = urllib.request.urlretrieve(url, filepath, None, params_str)
        # Testing HTTP headers and checking for errors
        regex = 'attachment; filename="(.+)"'
        if "content-disposition" in response[1].dict and re.match(
            regex, response[1].dict["content-disposition"]
        ):
            # IF ZIP, We proceed to unzip and rezip
            if os.path.splitext(filepath)[1] == ".zip":
                parentpath = os.path.dirname(filepath)
                # Making sub temp dir
                _tempdir = parentpath + "/temp"
                os.mkdir(_tempdir)
                _filepath = filepath + ".old"
                os.rename(filepath, _filepath)
                # Unzip
                proc = subprocess.Popen(
                    ["7z -o%s x %s" % (_tempdir, _filepath)],
                    stdout=subprocess.PIPE,
                    shell=True,
                )
                (out, err) = proc.communicate()
                # Output to debug
                logger.debug(out)
                logger.debug(err)
                # Switching to tempdir and rezip
                proc = subprocess.Popen(
                    ["7z a ../%s ." % os.path.basename(filepath)],
                    stdout=subprocess.PIPE,
                    shell=True,
                    cwd=_tempdir,
                )
                (out, err) = proc.communicate()
                # Output to debug
                logger.debug(out)
                logger.debug(err)
                # Deleting old zip file
                os.unlink(_filepath)
                # Remove temp dir
                rmtree(_tempdir, True)
            # Setting file mode to 777
            os.chmod(filepath, 511)
            return {"err": 0, "filepath": filepath}
        else:
            if response[1].type == "text/html":
                html = open(response[0], "r").read()
                return getHTMLerr(html) or _UNKNOWN_ERROR
            else:
                logger.warning("Unable to restore file, unkown error occured")
                return _UNKNOWN_ERROR
    except Exception as e:
        logger.warning(str(e))
        logger.warning("Unable to download file from BackupPC server")
        return {"err": 17, "errtext": "Unable to download file from BackupPC server"}


def get_download_status():
    global download_status
    # Purge the downloads that are older than 24 hours
    for k in list(download_status.keys()):
        if (
            download_status[k]["time"] == 1
            and int(time.time()) - download_status[k]["time"] > 24 * 60 * 60
        ):
            del download_status[k]
            # Delete files (if not a direct restore)
            if not ">DIRECT:" in k:
                os.unlink(k)
        elif ">DIRECT:" in k:
            # Check restore status
            status = get_host_status(download_status[k]["host"])["status"]
            if "restore done" in status:
                # We pass it to 1
                download_status[k].update({"status": 1, "err": 0})
            elif "restore failed" in status:
                download_status[k].update({"status": 1})
                download_status[k].update({"err": 34, "errtext": "Restore failed"})
    return download_status


def restore_file(host, backup_num, share_name, files):
    """
    @param host: Host uuid
    @type host: str
    @param backup_num: Backup Number
    @type backup_num: str
    @param share_name: Selected ShareName
    @type share_name: str
    @param files: Files to restore
    @type files: str,list

    Launch a Download thread of the specified file from the Backup Server.
    If <files> is a List, a ZIP archive is generated.

    @returns: Temporary Path to the restored file
    @rtype: str
    """

    # Define deferred callback and failure functions
    def _success(result):
        # Set download status to 1 (finished) for this download entry
        global download_status
        download_status[destination].update({"status": 1})
        download_status[destination].update(result)

    def _failure(failure):
        logger.error(str(failure))

    #
    # Generating temp filepath
    # If tempdir doesnt exist we create it
    if not os.path.exists(BackuppcConfig().tempdir):
        os.makedirs(BackuppcConfig().tempdir, 511)
        os.chmod(BackuppcConfig().tempdir, 511)
    tempfile.tempdir = BackuppcConfig().tempdir
    tempfiledir = tempfile.mkdtemp()
    os.chmod(tempfiledir, 511)
    if isinstance(files, list):
        destination = os.path.join(
            tempfiledir, "restore-%s.zip" % time.strftime("%Y-%m-%d-%H%M%S")
        )
        # Setting params
        params = {"action": "Restore", "host": host, "num": backup_num, "type": "2"}
        params.update({"share": share_name, "relative": "1", "compressLevel": "5"})
        # Files list
        params["fcbMax"] = len(files) + 1
        for i in range(len(files)):
            params["fcb" + str(i)] = urllib.parse.unquote(files[i])
    else:
        destination = os.path.join(tempfiledir, os.path.basename(files))
        # Setting params
        params = {
            "action": "RestoreFile",
            "host": host,
            "num": backup_num,
            "share": share_name,
        }
        params["dir"] = files.encode("utf-8")
    # Updating download_status (0 = running) dict
    global download_status
    download_status[destination] = {"status": 0, "host": host, "time": int(time.time())}
    # Setting a callback on download file functions
    download_file(destination, params).addCallback(_success).addErrback(_failure)
    return destination


def restore_files_to_host(
    host, backup_num, share_name, files, hostDest="", shareDest="", pathHdr="/"
):
    # Setting params
    params = {"action": "Restore", "host": host.lower(), "num": backup_num, "type": "4"}
    params["share"] = share_name.encode("utf8", "ignore")
    if hostDest:
        params["hostDest"] = hostDest.encode("utf8", "ignore")
    else:
        params["hostDest"] = host.lower()
    params["shareDest"] = shareDest.encode("utf8", "ignore")
    params["pathHdr"] = pathHdr.encode("utf8", "ignore")
    # Files list
    params["fcbMax"] = len(files) + 1
    for i in range(len(files)):
        params["fcb" + str(i)] = files[i].encode("utf8", "ignore")
    # Converting params dict to an http get string
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    else:
        # Updating download status table
        global download_status
        download_status[">DIRECT:" + host] = {
            "status": 0,
            "host": host,
            "time": int(time.time()),
            "destdir": share_name + pathHdr,
        }
        return {"err": 0}


# ==========================================================================
# HOST CONFIG FUNCTIONS
# ==========================================================================


def get_host_config(host, backupserver=""):
    # Function to convert _zZ_ to dict
    def underscores_to_dict(cfg):
        for key in list(cfg.keys()):
            if "_zZ_" in key:
                keys = string.split(key, "_zZ_")
                root = cfg
                for i in range(len(keys) - 1):
                    nkey = keys[i]
                    if not nkey in root:
                        root[nkey] = {}
                    root = root[nkey]
                root[keys[-1]] = cfg[key]
                del cfg[key]

    host_config = {}
    general_config = {}
    overrides = {}
    params = {}
    params["action"] = "editConfig"
    params["host"] = host
    html = send_request(params, backupserver)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    d = pq(html)
    inputs = d("form[name=editForm]").find("input")
    if not inputs:
        return _FORMAT_ERROR
    for i in range(len(inputs)):
        key = inputs.eq(i).attr("name")
        value = inputs.eq(i).val()
        if value is None:
            continue
        # Isolating host config params
        if "v_zZ_" in key:
            host_config[key.replace("v_zZ_", "")] = value
        # Isolating general config params
        elif "orig_zZ_" in key:
            general_config[key.replace("orig_zZ_", "")] = value
        # Isolating overrides
        elif "override_" in key:
            overrides[key.replace("override_", "")] = value
    underscores_to_dict(host_config)
    underscores_to_dict(general_config)
    return {
        "err": "0",
        "host_config": host_config,
        "general_config": general_config,
        "overrides": overrides,
    }


def set_host_config(host, config, globalconfig=0, backupserver=""):
    # Function used to format params
    def dict_to_underscores(cfg):
        for z in list(cfg.keys()):
            if isinstance(cfg[z], type({})):
                for h in list(cfg[z].keys()):
                    cfg[z + "_zZ_" + h] = cfg[z][h]
                del cfg[z]
                dict_to_underscores(cfg)
                break
            if isinstance(cfg[z], type([])):
                for h in range(len(cfg[z])):
                    cfg[z + "_zZ_" + str(h)] = cfg[z][h]
                del cfg[z]
                dict_to_underscores(cfg)
                break

    if not host and not globalconfig:
        return
    params = {}
    params["host"] = host
    params["action"] = "editConfig"
    params["saveAction"] = "Save"
    _config = config.copy()
    __config = config.copy()
    # Setting overrides
    for p in list(__config.keys()):
        params["override_" + p] = "1"
    # Formatting config dict
    dict_to_underscores(__config)
    # Setting overrides and params
    for p in __config:
        params["v_zZ_" + p] = __config[p]
    # TODO : fix this for all params
    if "BackupFilesExclude" in _config:
        params["vflds.BackupFilesExclude"] = _config["RsyncShareName"]
    # Sending HTTP request
    html = send_request(params, backupserver)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    return {"err": 0}


def set_host_backup_profile(uuid, newprofile):
    newprofile = int(newprofile)
    if BackuppcDatabase().set_host_backup_profile(uuid, newprofile) and newprofile:
        # Get profile data
        profile = BackuppcDatabase().edit_backup_profile(newprofile, {})
        # Define config dict
        config = {}
        config["RsyncShareName"] = profile["sharenames"].split("\n")
        config["ClientCharset"] = profile["encoding"]
        excludes = profile["excludes"].split("||")
        for i in range(len(excludes)):
            excludes[i] = excludes[i].split("\n")
        config["BackupFilesExclude"] = dict(
            list(zip(config["RsyncShareName"], excludes))
        )
        # Setting new host config
        set_host_config(uuid, config)


def set_host_period_profile(uuid, newprofile):
    newprofile = int(newprofile)
    if BackuppcDatabase().set_host_period_profile(uuid, newprofile) and newprofile:
        # Get profile data
        profile = BackuppcDatabase().edit_period_profile(newprofile, {})
        # Define config dict
        config = {}
        config["FullPeriod"] = profile["full"]
        config["IncrPeriod"] = profile["incr"]
        # Blackout periods
        periods = profile["exclude_periods"].split("\n")
        #
        config["BlackoutPeriods"] = []
        #
        for period in periods:
            m = re.search("([0-9.]+)=>([0-9.]+):([^:]+)", period)
            config["BlackoutPeriods"] += [
                {"hourBegin": m.group(1), "hourEnd": m.group(2), "weekDays": m.group(3)}
            ]
        # Setting host config
        set_host_config(uuid, config)


def host_exists(uuid):
    return BackuppcDatabase().host_exists(uuid)


def get_host_rsync_path(uuid):
    machine_info = Glpi().getLastMachineInventoryFull(uuid)
    machine = dict((key, value) for (key, value) in machine_info)
    if "Windows".lower() in machine["os"].lower():
        try:
            if "64" in machine["os_arch"]:
                return "C:\\Windows\\SysWOW64\\rsync.exe"
            else:
                return "C:\\Windows\\System32\\rsync.exe"
        except KeyError:
            return "C:\\Windows\\System32\\rsync.exe"
    elif "macOS".lower() in machine["os"].lower():
        return "rsync"
    else:
        return "/usr/bin/rsync"


def set_backup_for_host(uuid):
    rsync_path = get_host_rsync_path(uuid)
    server_url = getBackupServerByUUID(uuid)
    machine_info = Glpi().getLastMachineInventoryFull(uuid)
    machine = dict((key, value) for (key, value) in machine_info)
    if not server_url:
        return
    config = get_host_config("", server_url)["general_config"]
    try:
        newid = str(int(max(config["Hosts"].keys())) + 1)
        config["Hosts"][newid] = {
            "host": uuid,
            "dhcp": "0",
            "user": "root",
            "moreUsers": "0",
        }
    except:
        config["Hosts"] = [
            {"host": uuid, "dhcp": "0", "user": "root", "moreUsers": "0"}
        ]
    set_host_config("", config, 1, server_url)
    # if res['err']: return res
    # Checking if host has been added, then add it to DB
    config = get_host_config("", server_url)["general_config"]
    is_added = 0
    for i in config["Hosts"]:
        if config["Hosts"][i]["host"].lower() == uuid.lower():
            is_added = 1
            break
    if not is_added:
        logger.error("Unable to set host on BackupPC server")
        return {"err": 22, "errtext": "Unable to set host on BackupPC server"}
    # Setting nmblookup cmds and Rsync cmds in conf
    # TODO : read NmbLookupCmd from ini file
    config = {}
    port = randint(49152, 65535)
    config["RsyncClientPath"] = "%s" % rsync_path
    config["RsyncClientCmd"] = (
        "$sshPath -q -x -o StrictHostKeyChecking=no -l pulse -p %s $rsyncPath $argList+"
        % port
    )
    if machine["os"].lower() == "macos":
        config["RsyncClientRestoreCmd"] = (
            "$sshPath -q -x -o StrictHostKeyChecking=no -l pulse -p %s localhost sudo $rsyncPath $argList+"
            % port
        )
    else:
        config["RsyncClientRestoreCmd"] = (
            "$sshPath -q -x -o StrictHostKeyChecking=no -l pulse -p %s localhost $rsyncPath $argList+"
            % port
        )
    config[
        "DumpPreUserCmd"
    ] = "/usr/sbin/pulse2-connect-machine-backuppc -m %s -p %s" % (uuid, port)
    config[
        "DumpPostUserCmd"
    ] = "/usr/sbin/pulse2-disconnect-machine-backuppc -m %s -p %s" % (uuid, port)
    config[
        "RestorePreUserCmd"
    ] = "/usr/sbin/pulse2-connect-machine-backuppc -m %s -p %s" % (uuid, port)
    config[
        "RestorePostUserCmd"
    ] = "/usr/sbin/pulse2-disconnect-machine-backuppc -m %s -p %s" % (uuid, port)
    config["ClientNameAlias"] = "localhost"
    config["NmbLookupCmd"] = "/usr/bin/python /usr/bin/pulse2-uuid-resolver -A $host"
    config[
        "NmbLookupFindHostCmd"
    ] = "/usr/bin/python /usr/bin/pulse2-uuid-resolver $host"
    config["XferMethod"] = "rsync"
    config[
        "RsyncRestoreArgs"
    ] = "--numeric-ids --perms --owner --group -D --links --hard-links --times --block-size=2048 --relative --ignore-times --recursive --super".split(
        " "
    )
    config["PingCmd"] = "/bin/true"
    print("***", config, "****")
    set_host_config(uuid, config)
    # Adding host to the DB
    try:
        BackuppcDatabase().add_host(uuid, port)
    except:
        logger.error("Unable to add host to database")
        return {"err": 23, "errtext": "Unable to add host to database"}


def unset_backup_for_host(uuid):
    if not host_exists(uuid):
        logger.warning("Backup is not set for the machine %s" % uuid)
        return
    #
    server_url = getBackupServerByUUID(uuid)
    if not server_url:
        return
    # Removing entry from hosts
    config = get_host_config("", server_url)["general_config"]
    try:
        for i in list(config["Hosts"].keys()):
            if config["Hosts"][i]["host"].lower() == uuid.lower():
                del config["Hosts"][i]
                set_host_config("", config, 1, server_url)
                # if res['err']: return res
                break
        else:
            logger.warning("Host is already removed from BackupPC")
    except:
        logger.warning("No host found, passing")
    # Checking if host has been removed, then remove it from DB
    config = get_host_config("", server_url)["general_config"]
    if "Hosts" in config:
        for i in config["Hosts"]:
            if config["Hosts"][i]["host"].lower() == uuid.lower():
                logger.error("Unable to remove host from BackupPC")
                return {"err": 37, "errtext": "Unable to remove host from BackupPC"}
    # Removing host from the DB
    try:
        BackuppcDatabase().remove_host(uuid)
    except:
        logger.error("Unable to remove host from database")
        return {"err": 23, "errtext": "Unable to remove host from database"}


# ==========================================================================
# SERVER, HOST INFO AND BACKUP LOGS
# ==========================================================================


def get_xfer_log(host, backupnum):
    params = {}
    params["host"] = host
    params["action"] = "view"
    params["type"] = "XferErr"
    params["num"] = backupnum
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    d = pq(html)
    if not d("pre:first"):
        return _FORMAT_ERROR
    else:
        return {"err": 0, "data": d("pre:first").text()}


def get_host_log(host):
    params = {"host": host, "action": "view", "type": "LOG"}
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    d = pq(html)
    if not d("pre:first"):
        return _FORMAT_ERROR
    else:
        return {"err": 0, "data": d("pre:first").text()}


def build_fileindex(host):
    res = get_backup_list(host)
    # If error is returned, we abort
    if res["err"]:
        return res
    # Retreiving Backup nums array
    if not res["data"]:
        return {"err": 33, "errtext": "No backup point found"}
    backups = res["data"][0]
    #
    global file_index
    # If file_index doesnt contain host, we add it
    if not host in file_index:
        file_index[host] = {}
    # Building file index for all Backup points
    for backupnum in backups:
        # Setting params for XferLog page
        params = {}
        params["host"] = host
        params["action"] = "view"
        params["type"] = "XferLOG"
        params["num"] = backupnum
        # Sending request
        html = send_request(params)
        # Error treatment
        if not html:
            return _CONNECTION_ERROR
        #
        if getHTMLerr(html):
            return getHTMLerr(html)
        #
        d = pq(html)
        #
        if not d("pre:first"):
            return _FORMAT_ERROR
        #
        log = d("pre:first").text()
        lines = log.split("\n")
        #
        current_share = ""
        file_index[host][backupnum] = {}
        for line in lines:
            if len(line) < 3:
                continue
            if line[0:2] != "  ":
                if "backup started" in line:
                    r1 = re.search(
                        "for directory ([^(^)]+) \(baseline backup.+\)", line
                    )
                    r2 = re.search("for directory ([^(^)]+)", line)
                    r = r1 or r2
                    if r:
                        current_share = r.group(1)
                    file_index[host][backupnum][current_share] = {
                        "actions": [],
                        "types": [],
                        "modes": [],
                        "pts": [],
                        "sizes": [],
                        "paths": [],
                    }
                continue
            # If filename is . or .. , we pass
            if line[37:].strip() in [".", ".."]:
                continue
            # XferLog can be malformed, so this bullshit code below can fail
            if "4294967295" in line:
                continue
            # extracting info
            file_index[host][backupnum][current_share]["actions"].append(
                line[2:8].strip()
            )
            file_index[host][backupnum][current_share]["types"].append(line[9])
            # file_index[host][backupnum][current_share]['modes'].append(line[11:14])
            # file_index[host][backupnum][current_share]['pts'].append(line[17:24])
            file_index[host][backupnum][current_share]["sizes"].append(int(line[25:36]))
            file_index[host][backupnum][current_share]["paths"].append(line[37:])
    return {"err": 0}


def file_search(
    host,
    backupnum_0,
    sharename_0,
    filename_0,
    filesize_min=-1,
    filesize_max=-1,
    type_0="",
):
    global file_index
    # If no entry in file_index, we build host file index
    if not host in file_index:
        res = build_fileindex(host)
        # If error, we abort
        if res["err"]:
            return res
    # Adapting Params
    # filename_0 to lower, for case insensitive search
    filename_0 = filename_0.lower()
    # If sharename0_, backupnum_0 are strings, we convert them to lists
    if backupnum_0 and isinstance(backupnum_0, type("a")):
        backupnum_0 = [backupnum_0]
    if sharename_0 and isinstance(sharename_0, type("a")):
        sharename_0 = [sharename_0]
    filesize_min = int(filesize_min)
    filesize_max = int(filesize_max)
    # init result list
    result = []
    #
    for backupnum in file_index[host]:
        # If there is a backupnum filter, we apply it
        if backupnum_0 and not backupnum in backupnum_0:
            continue
        for sharename in file_index[host][backupnum]:
            # If there is a sharename filter, we apply it
            if sharename_0 and not sharename in sharename_0:
                continue
            for i in range(len(file_index[host][backupnum][sharename]["paths"])):
                # ========== TYPE FILTERING =============================
                _type = file_index[host][backupnum][sharename]["types"][i]
                # if symlink, we pass
                if _type == "l":
                    continue
                if type_0 and _type != type_0:
                    continue
                # ========== FILENAME FILTERING =============================
                filepath = file_index[host][backupnum][sharename]["paths"][i]
                filename = os.path.basename(filepath).lower()
                if filename_0 and not fnmatch.fnmatch(filename, filename_0):
                    continue
                # ========== FILESIZE FILTERING =============================
                size = file_index[host][backupnum][sharename]["sizes"][i]
                if filesize_max != -1 and size > filesize_max:
                    continue
                if filesize_min != -1 and size < filesize_min:
                    continue
                # =========== APPENDING RESULT ENTRY =================================
                result.append(
                    {
                        "backupnum": backupnum,
                        "sharename": sharename,
                        "filepath": "/" + filepath,
                        "filename": filename,
                        "filesize": size,
                        "type": _type,
                    }
                )
    return {"err": 0, "data": result}


def apply_backup_profile(profileid):
    # Hosts corresponding to selected profile
    hosts = BackuppcDatabase().get_hosts_by_backup_profile(profileid)
    # Getting profile settings
    profile = BackuppcDatabase().edit_backup_profile(profileid, {})
    # Define config dict
    config = {}
    config["RsyncShareName"] = profile["sharenames"].split("\n")
    config["ClientCharset"] = profile["encoding"]
    excludes = profile["excludes"].split("||")
    for i in range(len(excludes)):
        excludes[i] = excludes[i].split("\n")
    config["BackupFilesExclude"] = dict(list(zip(config["RsyncShareName"], excludes)))
    for host in hosts:
        set_host_config(host, config)
    # TODO : Error treatment
    return 0


def apply_period_profile(profileid):
    # Hosts corresponding to selected profile
    hosts = BackuppcDatabase().get_hosts_by_period_profile(profileid)
    # Getting profile settings
    profile = BackuppcDatabase().edit_period_profile(profileid, {})
    # Define config dict
    config = {}
    config["FullPeriod"] = profile["full"]
    config["IncrPeriod"] = profile["incr"]
    # Blackout periods
    periods = profile["exclude_periods"].split("\n")
    #
    config["BlackoutPeriods"] = []
    #
    for period in periods:
        m = re.search("([0-9.]+)=>([0-9.]+):([^:]+)", period)
        config["BlackoutPeriods"] += [
            {"hourBegin": m.group(1), "hourEnd": m.group(2), "weekDays": m.group(3)}
        ]
    #
    for host in hosts:
        set_host_config(host, config)
    # TODO : Error treatment
    return 0


# ====================================================================
# BACKUP ACTIONS
# ====================================================================


def start_full_backup(host):
    params = {}
    params["host"] = host
    params["action"] = "Start_Full_Backup"
    params["doit"] = "1"
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    return {"err": 0}


def start_incr_backup(host):
    params = {}
    params["host"] = host
    params["action"] = "Start_Incr_Backup"
    params["doit"] = "1"
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    return {"err": 0}


def stop_backup(host, backoff=""):
    params = {}
    params["host"] = host
    params["action"] = "Stop_Dequeue_Backup"
    params["doit"] = "1"
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    return {"err": 0}


def get_host_status(host):
    params = {"host": host}
    html = send_request(params)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    result = {"err": 0, "status": []}
    d = pq(html)
    if d("ul:first").find("li"):
        statuslines = d("ul:first").find("li").text()
    else:
        statuslines = ""
    # Status strings
    if "no ping" in statuslines:
        result["status"] += ["no ping"]
    if "restore failed" in statuslines:
        result["status"] += ["restore failed"]
    if "backup failed" in statuslines:
        result["status"] += ["backup failed"]
    if "restore done" in statuslines:
        result["status"] += ["restore done"]
    elif "done" in statuslines:
        result["status"] += ["backup_done"]
    if "(idle)" in statuslines:
        result["status"] += ["idle"]
    if "in progress" in statuslines:
        result["status"] += ["in progress"]
    if "canceled by user" in statuslines:
        result["status"] += ["canceled"]
    if len(result["status"]) == 0:
        result["status"] += ["nothing"]
    try:
        tb_summary = getTableByTitle(html, "Backup Summary")
        xfer_summary = getTableByTitle(html, "Xfer Error Summary")
        size_summary = getTableByTitle(html, "File Size/Count Reuse Summary")
        if not (tb_summary and xfer_summary and size_summary):
            return _FORMAT_ERROR
        # Contents
        tb_summary = getTableContent(tb_summary)
        xfer_summary = getTableContent(xfer_summary)
        size_summary = getTableContent(size_summary)
        #
        result["data"] = {
            "backup_nums": tb_summary[0][::-1],
            "type": tb_summary[1][::-1],
            "start_dates": tb_summary[4][::-1],
            "durations": tb_summary[5][::-1],
            "ages": tb_summary[6][::-1],
            "xfer_errs": xfer_summary[3][::-1],
            "total_file_count": size_summary[2][::-1],
            "total_file_size": size_summary[3][::-1],
            "new_file_count": size_summary[7][::-1],
            "new_file_size": size_summary[8][::-1],
        }
    except:
        result["data"] = {}
    return result


def get_global_status(entity_uuid):
    params = {"action": "summary"}
    entities_parent = Glpi().get_ancestors(entity_uuid)
    url = BackuppcDatabase().get_backupserver_by_entity(entity_uuid)
    if url == "":
        for id in entities_parent:
            url = BackuppcDatabase().get_backupserver_by_entity("UUID%s" % id)
            if url != "":
                break

    if not url:
        return {"err": 0, "data": {}}
    html = send_request(params, url)
    if not html:
        return _CONNECTION_ERROR
    if getHTMLerr(html):
        return getHTMLerr(html)
    result = {"err": 0, "data": {}}
    try:
        tb_good = getTableByTitle(html, "Hosts with good Backups")
        tb_none = getTableByTitle(html, "Hosts with no Backups")
        # Contents
        if not (tb_good or tb_none):
            return result
        tb_good = getTableContent(tb_good)
        if not tb_good:
            tb_good = [[] for i in range(12)]
        tb_none = getTableContent(tb_none)
        if not tb_none:
            tb_none = [[] for i in range(12)]
        #
        result["data"] = {
            "hosts": tb_good[0] + tb_none[0],
            "full": tb_good[2] + tb_none[2],
            "full_size": tb_good[4] + tb_none[4],
            "incr": tb_good[6] + tb_none[6],
            "last_backup": tb_good[8] + tb_none[8],
            "state": tb_good[9] + tb_none[9],
            "last_attempt": tb_good[10] + tb_none[10],
        }
    except:
        result["data"] = {}
    return result
