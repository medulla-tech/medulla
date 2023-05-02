# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import netifaces
import json
import subprocess
import sys
import os
import fnmatch
import platform
import logging
import configparser
import random
import re
import traceback
import types
from pprint import pprint
import hashlib
from functools import wraps
import base64
from importlib import import_module
import threading
import socket
import urllib.request, urllib.parse, urllib.error
import uuid
import time
from datetime import datetime
import imp
import requests
from Cryptodome import Random
from Cryptodome.Cipher import AES
import urllib.request, urllib.error, urllib.parse
import tarfile
import zipfile
from functools import wraps
import zlib
import io

logger = logging.getLogger()

sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "pluginsmaster")
)

if sys.platform.startswith("win"):
    import wmi
    import pythoncom
    import winreg as wr
    import win32net
    import win32netcon


#### debug decorator #########
def minimum_runtime(t):
    """
    Function decorator constrains the minimum execution time of the function
    """

    def decorated(f):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            runtime = time.time() - start
            if runtime < t:
                time.sleep(t - runtime)
            return result

        return wrapper

    return decorated


def dump_parameter(para=True, out=True, timeprocess=True):
    """
    Function decorator logging in and out function.
    """

    def decorated(decorated_function):
        @wraps(decorated_function)
        def wrapper(*dec_fn_args, **dec_fn_kwargs):
            # Log function entry
            start = time.time()
            func_name = decorated_function.__name__
            log = logging.getLogger(func_name)

            filepath = os.path.basename(__file__)
            # get function params (args and kwargs)
            if para:
                arg_names = decorated_function.__code__.co_varnames
                params = dict(
                    args=dict(list(zip(arg_names, dec_fn_args))), kwargs=dec_fn_kwargs
                )
                result = ", ".join(
                    ["{}={}".format(str(k), repr(v)) for k, v in list(params.items())]
                )
                log.info(
                    "\n@@@ call func : {}({}) file {}".format(
                        func_name, result, filepath
                    )
                )
                log.info(
                    "\n@@@ call func : {}({}) file {}".format(
                        func_name, result, filepath
                    )
                )
            else:
                log.info("\n@@@ call func : {}() file {}".format(func_name, filepath))
            # Execute wrapped (decorated) function:
            outfunction = decorated_function(*dec_fn_args, **dec_fn_kwargs)
            timeruntime = time.time() - start
            if out:
                if timeprocess:
                    log.info(
                        "\n@@@ out func :{}() in {}s is -->{}".format(
                            func_name, timeruntime, outfunction
                        )
                    )
                else:
                    log.info(
                        "\n@@@ out func :{}() is -->{}".format(func_name, outfunction)
                    )
            else:
                if timeprocess:
                    log.info(
                        "\n@@@ out func :{}() in {}s".format(func_name, timeruntime)
                    )
                else:
                    log.info("\n@@@ out func :{}()".format(func_name))
            return outfunction

        return wrapper

    return decorated


###########################################


def file_get_contents(
    filename, use_include_path=0, context=None, offset=-1, maxlen=-1, bytes=False
):
    """
    load content file or simple url
    """
    if filename.find("://") > 0:
        ret = urllib.request.urlopen(filename).read()
        if offset > 0:
            ret = ret[offset:]
        if maxlen > 0:
            ret = ret[:maxlen]
        return ret
    else:
        if bytes == True:
            fp = open(filename, "rb")
        else:
            fp = open(filename, "r")
        try:
            if offset > 0:
                fp.seek(offset)
            ret = fp.read(maxlen)
            return ret
        finally:
            fp.close()


def file_put_contents(filename, data, bytes=False):
    """
    write content "data" to file "filename"
    """
    if bytes == True:
        f = open(filename, "wb")
    else:
        f = open(filename, "w")
    f.write(data)
    f.close()


def file_put_contents_w_a(filename, data, option="w"):
    if option == "a" or option == "w":
        f = open(filename, option)
        f.write(data)
        f.close()


def displayDataJson(jsondata):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(jsondata)


def loadModule(filename):
    if filename == "":
        raise RuntimeError("Empty filename cannot be loaded")
    searchPath, file = os.path.split(filename)
    if not searchPath in sys.path:
        sys.path.append(searchPath)
        sys.path.append(os.path.normpath(searchPath + "/../"))
    moduleName, ext = os.path.splitext(file)
    fp, pathName, description = imp.find_module(
        moduleName,
        [
            searchPath,
        ],
    )
    try:
        module = imp.load_module(moduleName, fp, pathName, description)
    finally:
        if fp:
            fp.close()
    return module


def call_plugin(name, *args, **kwargs):
    nameplugin = os.path.join(args[0].modulepath, "plugin_%s" % name)
    objxmpp = args[0]
    # add compteur appel plugins
    count = 0
    try:
        count = getattr(args[0], "num_call%s" % name)
    except AttributeError:
        count = 0
        setattr(args[0], "num_call%s" % name, count)
    if objxmpp.config.executiontimeplugins:
        tmps1 = time.clock()
        pluginaction = loadModule(nameplugin)
        pluginaction.action(*args, **kwargs)
        setattr(args[0], "num_call%s" % name, count + 1)
        tmps2 = time.clock() - tmps1
        logger.info(
            "_xmpp_ %s Execution time: [%s] %s" % (str(datetime.now()), name, tmps2)
        )
        cmd = "cat /proc/%s/status | grep Threads" % os.getpid()
        obj = simplecommandstr(cmd)
        file_put_contents_w_a(
            "/tmp/Execution_time_plugin.txt",
            "%s  [%s] Execution time: %s | %s \n"
            % (str(datetime.now()), name, tmps2, obj["result"]),
            "a",
        )
    else:
        pluginaction = loadModule(nameplugin)
        pluginaction.action(*args, **kwargs)
        setattr(args[0], "num_call%s" % name, count + 1)


def utc2local(utc):
    """
    utc2local transform a utc datetime object to local object.

    Param:
        utc datetime which is not naive (the utc timezone must be precised)
    Returns:
        datetime in local timezone
    """
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset


def getRandomName(nb, pref=""):
    a = "abcdefghijklnmopqrstuvwxyz0123456789"
    d = pref
    for t in range(nb):
        d = d + a[random.randint(0, 35)]
    return d


def data_struct_message(action, data={}, ret=0, base64=False, sessionid=None):
    if sessionid == None or sessionid == "" or not isinstance(sessionid, str):
        sessionid = action.strip().replace(" ", "")
    return {
        "action": action,
        "data": data,
        "ret": 0,
        "base64": False,
        "sessionid": getRandomName(4, sessionid),
    }


def add_method(cls):
    """decorateur a utiliser pour ajouter une methode a un object"""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)

        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func  # returning func means func can still be used normally

    return decorator


def pathbase():
    return os.path.abspath(os.getcwd())


def pathscript():
    return os.path.abspath(os.path.join(pathbase(), "script"))


def pathplugins():
    return os.path.abspath(os.path.join(pathbase(), "plugins"))


def pathlib():
    return os.path.abspath(os.path.join(pathbase(), "lib"))


def pathscriptperl(name):
    return os.path.abspath(os.path.join(pathbase(), "script", "perl", name))


def leplusfrequent(L):
    """Returns the most frequent element from the list"""
    L.sort()  # To assemble indentical elements
    n0, e0 = 0, None  # To keep the most frequent
    ep = None  # Store the distinct element from the previous loop
    for e in L:
        if e != ep:  # If e has been seen previously, nothing is done
            n = L.count(e)
            if n > n0:
                n0, e0 = n, e  # Store the new most frequent element
            ep = e  # Store current element in next loop
    return e0, n0


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


# windows


def get_connection_name_from_guid(iface_guids):
    iface_names = ["(unknown)" for i in range(len(iface_guids))]
    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
    reg_key = wr.OpenKey(
        reg,
        r"SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}",
    )
    for i in range(len(iface_guids)):
        try:
            reg_subkey = wr.OpenKey(reg_key, iface_guids[i] + r"\Connection")
            iface_names[i] = wr.QueryValueEx(reg_subkey, "Name")[0]
        except:
            pass
    return iface_names


def create_Win_user(username, password, full_name=None, comment=None):
    """
    Create a system user account for Rattail.
    """
    try:
        d = win32net.NetUserGetInfo(None, username, 1)
        return
    except:
        pass
    if not full_name:
        full_name = "{0} User".format(username.capitalize())
    if not comment:
        comment = "System user account for Rattail applications"
    win32net.NetUserAdd(
        None,
        2,
        {
            "name": username,
            "password": password,
            "priv": win32netcon.USER_PRIV_USER,
            "comment": comment,
            "flags": (
                win32netcon.UF_NORMAL_ACCOUNT
                | win32netcon.UF_PASSWD_CANT_CHANGE
                | win32netcon.UF_DONT_EXPIRE_PASSWD
            ),
            "full_name": full_name,
            "acct_expires": win32netcon.TIMEQ_FOREVER,
        },
    )

    win32net.NetLocalGroupAddMembers(
        None,
        "Users",
        3,
        [{"domainandname": r"{0}\{1}".format(socket.gethostname(), username)}],
    )

    # hide_user_account(username)
    return True


def isWinUserAdmin():
    if os.name == "nt":
        import ctypes

        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            # print "Admin check failed, assuming not an admin."
            return False
    elif os.name == "posix":
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError(
            "Unsupported operating system for this module: %s" % (os.name,)
        )


# mac OS


def isMacOsUserAdmin():
    obj = simplecommand("cat /etc/master.passwd")  # For linux "cat /etc/shadow")
    if int(obj["code"]) == 0:
        return True
    else:
        return False


def name_random(nb, pref=""):
    a = "abcdefghijklnmopqrstuvwxyz0123456789"
    d = pref
    for t in range(nb):
        d = d + a[random.randint(0, 35)]
    return d


def name_randomplus(nb, pref=""):
    a = "abcdefghijklnmopqrstuvwxyz0123456789"
    q = str(uuid.uuid4())
    q = pref + q.replace("-", "")
    for t in range(nb):
        d = a[random.randint(0, 35)]
    res = q + d
    return res[:nb]


def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


def getShortenedIpList():
    listmacaddress = {}
    for i in netifaces.interfaces():
        addrs = netifaces.ifaddresses(i)
        try:
            if_mac = shorten_mac(addrs[netifaces.AF_LINK][0]["addr"])
            if_ip = addrs[netifaces.AF_INET][0]["addr"]
            address = int(if_mac, 16)
            if address != 0:
                listmacaddress[address] = if_mac
        except:
            pass
    return listmacaddress


def name_jid():
    dd = getShortenedIpList()
    cc = sorted(dd.keys())
    return dd[cc[0]]


def getIPAdressList():
    ip_list = []
    for interface in netifaces.interfaces():
        try:
            for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                if link["addr"] != "127.0.0.1":
                    ip_list.append(link["addr"])
        except:
            pass
    return ip_list


def shorten_mac(mac):
    mac = mac.lower()
    mac = mac.replace(":", "")
    mac = mac.replace("-", "")
    mac = mac.replace(" ", "")
    # mac = mac.replace("/","")
    return mac


# 3 functions used for subnet network


def ipV4toDecimal(ipv4):
    d = ipv4.split(".")
    return (
        (int(d[0]) * 256 * 256 * 256)
        + (int(d[1]) * 256 * 256)
        + (int(d[2]) * 256)
        + int(d[3])
    )


def decimaltoIpV4(ipdecimal):
    a = float(ipdecimal) / (256 * 256 * 256)
    b = (a - int(a)) * 256
    c = (b - int(b)) * 256
    d = (c - int(c)) * 256
    return "%s.%s.%s.%s" % (int(a), int(b), int(c), int(d))


def subnetnetwork(adressmachine, mask):
    adressmachine = adressmachine.split(":")[0]
    reseaumachine = ipV4toDecimal(adressmachine) & ipV4toDecimal(mask)
    return decimaltoIpV4(reseaumachine)


def subnet_address(address, maskvalue):
    addr = [int(x) for x in adress.split(".")]
    mask = [int(x) for x in maskvalue.split(".")]
    subnet = [addr[i] & mask[i] for i in range(4)]
    broadcast = [(addr[i] & mask[i]) | (255 ^ mask[i]) for i in range(4)]
    return ".".join([str(x) for x in subnet]), ".".join([str(x) for x in broadcast])


def is_valid_ipv4(ip):
    """Validates IPv4 addresses."""
    pattern = re.compile(
        r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """,
        re.VERBOSE | re.IGNORECASE,
    )
    return pattern.match(ip) is not None


def is_valid_ipv6(ip):
    """Validates IPv6 addresses."""
    pattern = re.compile(
        r"""
        ^
        \s*                         # Leading whitespace
        (?!.*::.*::)                # Only a single whildcard allowed
        (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
        (?:                         # Repeat 6 times:
            [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
        ){6}                        #
        (?:                         # Either
            [0-9a-f]{0,4}           #   Another group
            (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            [0-9a-f]{0,4}           #   Last group
            (?: (?<=::)             #   Colon iff preceeded by exacly one colon
             |  (?<!:)              #
             |  (?<=:) (?<!::) :    #
             )                      # OR
         |                          #   A v4 address with NO leading zeros
            (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            (?: \.
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
            ){3}
        )
        \s*                         # Trailing whitespace
        $
    """,
        re.VERBOSE | re.IGNORECASE | re.DOTALL,
    )
    return pattern.match(ip) is not None


# linux systemd or init


def typelinux():
    p = subprocess.Popen(
        "cat /proc/1/comm", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    code_result = p.wait()
    system = result[0].rstrip("\n")
    """returns the list of ip gateway related to the interfaces"""
    return system


def isprogramme(name):
    obj = {}
    p = subprocess.Popen(
        "which %s" % (name),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result = p.stdout.readlines()
    obj["code"] = p.wait()
    obj["result"] = result
    # print obj['code']
    # print obj['result']
    # print obj
    if obj["result"] != "":
        return True
    else:
        return False


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


def servicelinuxinit(name, action):
    obj = {}
    p = subprocess.Popen(
        "/etc/init.d/%s %s" % (name, action),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result = p.stdout.readlines()
    obj["code"] = p.wait()
    obj["result"] = result
    return obj


# restart service


def service(name, action):  # start | stop | restart | reload
    obj = {}
    if sys.platform.startswith("linux"):
        system = ""
        p = subprocess.Popen(
            "cat /proc/1/comm",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        result = p.stdout.readlines()
        code_result = p.wait()
        system = result[0].rstrip("\n")
        if system == "init":
            p = subprocess.Popen(
                "/etc/init.d/%s %s" % (name, action),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            result = p.stdout.readlines()
            obj["code"] = p.wait()
            obj["result"] = result
        elif system == "systemd":
            p = subprocess.Popen(
                "systemctl %s %s" % (action, name),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            result = p.stdout.readlines()
            obj["code"] = p.wait()
            obj["result"] = result
    elif sys.platform.startswith("win"):
        pythoncom.CoInitialize()
        try:
            wmi_obj = wmi.WMI()
            wmi_sql = "select * from Win32_Service Where Name ='%s'" % name
            wmi_out = wmi_obj.query(wmi_sql)
        finally:
            pythoncom.CoUninitialize()
        for dev in wmi_out:
            print(dev.Caption)
        pass
    elif sys.platform.startswith("darwin"):
        pass
    return obj


# listservice()
# FusionInventory Agent


def listservice():
    pythoncom.CoInitialize()
    try:
        wmi_obj = wmi.WMI()
        wmi_sql = "select * from Win32_Service"  # Where Name ='Alerter'"
        wmi_out = wmi_obj.query(wmi_sql)
    finally:
        pythoncom.CoUninitialize()
    for dev in wmi_out:
        print(dev.Caption)
        print(dev.DisplayName)


def joint_compteAD(domain, password, login, group):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa392154%28v=vs.85%29.aspx
    pythoncom.CoInitialize()
    try:
        c = wmi.WMI()
        for computer in c.Win32_ComputerSystem():
            if computer.PartOfDomain:
                print(computer.Domain)  # DOMCD
                print(computer.SystemStartupOptions)
                computer.JoinDomainOrWorkGroup(domain, password, login, group, 3)
    finally:
        pythoncom.CoUninitialize()


def windowsservice(name, action):
    pythoncom.CoInitialize()
    try:
        wmi_obj = wmi.WMI()
        wmi_sql = "select * from Win32_Service Where Name ='%s'" % name
        print(wmi_sql)
        wmi_out = wmi_obj.query(wmi_sql)
    finally:
        pythoncom.CoUninitialize()
    print(len(wmi_out))
    for dev in wmi_out:
        print(dev.caption)
        if action.lower() == "start":
            dev.StartService()
        elif action.lower() == "stop":
            print(dev.Name)
            dev.StopService()
        elif action.lower() == "restart":
            dev.StopService()
            dev.StartService()
        else:
            pass


# windowsservice("FusionInventory-Agent", "Stop")


def methodservice():
    import pythoncom
    import wmi

    pythoncom.CoInitialize()
    try:
        c = wmi.WMI()
        for method in c.Win32_Service._methods:
            print(method)
    finally:
        pythoncom.CoUninitialize()


def file_get_content(path):
    inputFile = open(path, "r")  # Open test.txt file in read mode
    content = inputFile.read()
    inputFile.close()
    return content


def file_put_content(filename, contents, mode="w"):
    fh = open(filename, mode)
    fh.write(contents)
    fh.close()


# windows
# def listusergroup():
# import wmi
# c = wmi.WMI()
# for group in c.Win32_Group():
# print group.Caption
# for user in group.associators("Win32_GroupUser"):
# print "  ", user.Caption

# decorator to simplify the plugins


def pluginprocess(func):
    def wrapper(xmppobject, action, sessionid, data, message, dataerreur):
        resultaction = "result%s" % action
        result = {}
        result["action"] = resultaction
        result["ret"] = 0
        result["sessionid"] = sessionid
        result["base64"] = False
        result["data"] = {}
        dataerreur["action"] = resultaction
        dataerreur["data"]["msg"] = "ERROR : %s" % action
        dataerreur["sessionid"] = sessionid
        try:
            response = func(
                xmppobject, action, sessionid, data, message, dataerreur, result
            )
            # encode  result['data'] if needed
            # print result
            if result["base64"] == True:
                result["data"] = base64.b64encode(json.dumps(result["data"]))
            xmppobject.send_message(
                mto=message["from"], mbody=json.dumps(result), mtype="chat"
            )
        except:
            xmppobject.send_message(
                mto=message["from"], mbody=json.dumps(dataerreur), mtype="chat"
            )
            return
        return response

    return wrapper


# decorator to simplify the plugins
# Check if session exists.
# No end of session


def pluginmaster(func):
    def wrapper(xmppobject, action, sessionid, data, message, ret):
        if action.startswith("result"):
            action = action[:6]
        if xmppobject.session.isexist(sessionid):
            objsessiondata = xmppobject.session.sessionfromsessiondata(sessionid)
        else:
            objsessiondata = None
        response = func(
            xmppobject, action, sessionid, data, message, ret, objsessiondata
        )
        return response

    return wrapper


def pluginmastersessionaction(sessionaction, timeminute=10):
    def decorator(func):
        def wrapper(xmppobject, action, sessionid, data, message, ret, dataobj):
            # avant
            if action.startswith("result"):
                action = action[6:]
            if xmppobject.session.isexist(sessionid):
                if sessionaction == "actualise":
                    xmppobject.session.reactualisesession(sessionid, 10)
                objsessiondata = xmppobject.session.sessionfromsessiondata(sessionid)
            else:
                objsessiondata = None
            response = func(
                xmppobject,
                action,
                sessionid,
                data,
                message,
                ret,
                dataobj,
                objsessiondata,
            )
            if sessionaction == "clear" and objsessiondata != None:
                xmppobject.session.clear(sessionid)
            elif sessionaction == "actualise":
                xmppobject.session.reactualisesession(sessionid, 10)
            return response

        return wrapper

    return decorator


def find_ip():
    candidates = []
    for test_ip in ["192.0.2.0", "192.51.100.0", "203.0.113.0"]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((test_ip, 80))
            ip_adrss = s.getsockname()[0]
            if ip_adrss in candidates:
                return ip_adrss
            candidates.append(ip_adrss)
        except Exception:
            pass
        finally:
            s.close()
    if len(candidates) >= 1:
        return candidates[0]
    return None


class shellcommandtimeout(object):
    def __init__(self, cmd, timeout=15):
        self.process = None
        self.obj = {}
        self.obj["timeout"] = timeout
        self.obj["cmd"] = cmd
        self.obj["result"] = "result undefined"
        self.obj["code"] = 255
        self.obj["separateurline"] = os.linesep

    def run(self):
        def target():
            # print 'Thread started'
            self.process = subprocess.Popen(
                self.obj["cmd"],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.obj["result"] = self.process.stdout.readlines()
            self.obj["code"] = self.process.wait()
            self.process.communicate()
            # print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(self.obj["timeout"])
        if thread.is_alive():
            print("Terminating process")
            print("timeout %s" % self.obj["timeout"])
            # self.codereturn = -255
            # self.result = "error tineour"
            self.process.terminate()
            thread.join()

        # self.result = self.process.stdout.readlines()
        self.obj["codereturn"] = self.process.returncode

        if self.obj["codereturn"] == -15:
            self.result = "error tineout"

        return self.obj


def ipfromdns(name_domaine_or_ip):
    """This function converts a dns to ipv4
    If not find return ""
    function tester on OS:
    MAcOs, linux (debian, redhat, ubuntu), windows
    eg : print ipfromdns("sfr.fr")
    80.125.163.172
    """
    if name_domaine_or_ip != "" and name_domaine_or_ip != None:
        if is_valid_ipv4(name_domaine_or_ip):
            return name_domaine_or_ip
        try:
            return socket.gethostbyname(name_domaine_or_ip)
        except socket.gaierror:
            return ""
        except Exception:
            return ""
    return ""


def check_exist_ip_port(name_domaine_or_ip, port):
    """This function check if socket valid for connection
    return True or False
    """
    ip = ipfromdns(name_domaine_or_ip)
    try:
        socket.getaddrinfo(ip, port)
        return True
    except socket.gaierror:
        return False
    except Exception:
        return False


unpad = lambda s: s[0 : -ord(s[-1])]


class AESCipher:
    def __init__(self, key, BS=32):
        self.key = key
        self.BS = BS

    def _pad(self, s):
        return s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))


def make_tarfile(output_file_gz_bz2, source_dir, compresstype="gz"):
    """
    creation archive tar.gz or tar.bz2
    compresstype "gz" or "bz2"
    """
    try:
        with tarfile.open(output_file_gz_bz2, "w:%s" % compresstype) as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        return True
    except Exception as e:
        logger.error("Error creating tar.%s archive : %s" % (compresstype, str(e)))
        return False


def extract_file(imput_file__gz_bz2, to_directory=".", compresstype="gz"):
    """
    extract archive tar.gz or tar.bz2
    compresstype "gz" or "bz2"
    """
    cwd = os.getcwd()
    absolutepath = os.path.abspath(imput_file__gz_bz2)
    try:
        os.chdir(to_directory)
        with tarfile.open(absolutepath, "r:%s" % compresstype) as tar:
            tar.extractall()
        return True
    except OSError as e:
        logger.error("Error creating tar.%s archive : %s" % (str(e), compresstype))
        return False
    except Exception as e:
        logger.error("Error creating tar.%s archive : %s" % (str(e), compresstype))
        return False
    finally:
        os.chdir(cwd)
    return True


def find_files(directory, pattern):
    """
    use f
    """
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = str(os.path.join(root, basename))
                yield filename


def listfile(directory, abspath=True):
    listfile = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if abspath:
                listfile.append(os.path.join(root, basename))
            else:
                listfile.append(os.path.join(basename))
    return listfile


def md5folder(directory):
    hash = hashlib.md5()
    strmdr = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            hash.update(md5(os.path.join(root, basename)))
    return hash.hexdigest()


def Setdirectorytempinfo():
    """
    create directory
    """
    dirtempinfo = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "INFOSTMP"
    )
    if not os.path.exists(dirtempinfo):
        os.makedirs(dirtempinfo, mode=0o700)
    return dirtempinfo


class geolocalisation_agent:
    def __init__(
        self,
        typeuser="public",
        geolocalisation=True,
        ip_public=None,
        strlistgeoserveur="",
    ):
        self.determination = False
        self.geolocalisation = geolocalisation
        self.ip_public = ip_public
        self.typeuser = typeuser
        self.filegeolocalisation = os.path.join(
            Setdirectorytempinfo(), "filegeolocalisation"
        )
        self.listgeoserver = [
            "http://%s/json" % x
            for x in re.split(
                r"[;,\[\(\]\)\{\}\:\=\+\*\\\?\/\#\+\&\-\$\|\s]", strlistgeoserveur
            )
            if x.strip() != ""
        ]
        self.localisation = None
        self.getgeolocalisation()
        if self.localisation is None:
            self.localisation = self.getdatafilegeolocalisation()

    def getgeolocalisationobject(self):
        if self.localisation is None:
            return {}
        return self.localisation

    def getdatafilegeolocalisation(self):
        if self.geoinfoexist():
            try:
                with open(self.filegeolocalisation) as json_data:
                    self.localisation = json.load(json_data)
                self.determination = False
                return self.localisation
            except Exception:
                pass
        return None

    def setdatafilegeolocalisation(self):
        if self.localisation is not None:
            try:
                with open(self.filegeolocalisation, "w") as json_data:
                    json.dump(self.localisation, json_data, indent=4)
                self.determination = True
            except Exception:
                pass

    def geoinfoexist(self):
        if os.path.exists(self.filegeolocalisation):
            return True
        return False

    def getgeolocalisation(self):
        if self.geolocalisation:
            if (
                self.typeuser in ["public", "nomade", "both"]
                or self.localisation is None
            ):
                # on recherche a chaque fois les information
                self.localisation = geolocalisation_agent.searchgeolocalisation(
                    self.listgeoserver
                )
                self.determination = True
                self.setdatafilegeolocalisation()
                return self.localisation
            else:
                if self.localisation is not None:
                    if not self.geoinfoexist():
                        self.setdatafilegeolocalisation()
                        self.determination = False
                    return self.localisation
                elif not self.geoinfoexist():
                    self.localisation = geolocalisation_agent.searchgeolocalisation(
                        self.listgeoserver
                    )
                    self.setdatafilegeolocalisation()
                    self.determination = True
                    return self.localisation
            return None
        else:
            if not self.geoinfoexist():
                self.localisation = geolocalisation_agent.searchgeolocalisation(
                    self.listgeoserver
                )
                self.setdatafilegeolocalisation()
                self.determination = True
                return self.localisation

        return self.localisation

    def get_ip_public(self):
        if self.geolocalisation:
            if self.localisation is None:
                self.getgeolocalisation()
            if self.localisation is not None and is_valid_ipv4(self.localisation["ip"]):
                if not self.determination:
                    logger.warning("Determination use file")
                self.ip_public = self.localisation["ip"]
                return self.localisation["ip"]
            else:
                return None
        else:
            if not self.determination:
                logger.warning("use old determination ip_public")
            if self.localisation is None:
                if self.geoinfoexist():
                    dd = self.getdatafilegeolocalisation()
                    logger.warning("%s" % dd)
                    if self.localisation is not None:
                        return self.localisation["ip"]
            else:
                return self.localisation["ip"]
        return self.ip_public

    @staticmethod
    def call_simple_page(url):
        try:
            r = requests.get(url)
            return r.json()
        except:
            return None

    @staticmethod
    def call_simple_page_urllib(url):
        try:
            objip = json.loads(urllib.request.urlopen(url).read())
            return objip
        except:
            return None

    @staticmethod
    def searchgeolocalisation(http_url_list_geo_server):
        """
        return objet
        """
        for url in http_url_list_geo_server:
            try:
                objip = geolocalisation_agent.call_simple_page(url)
                if objip is None:
                    raise
                return objip
            except BaseException:
                pass
        return None


class Converter:
    """Object to simplify convertions from objects to base64 string"""

    def __init__(self, data, **kwargs):
        """A new instance of Converter determines what to do with the datas.
        If the data is in base 64, it converts datas to bytes field or string,
        depending on _bytes option.
        In the other hand if the data is not in base 64 (str or bytes) it converts datas to
        base 64 bytes field or str, depending on _bytes option.
        In this conversion if the option compressed is set to True, the datas are compressed before base 64 conversion.

        Params:
            - data: mixed datas which will be converted
            - kwargs: dict of options

        kwargs Options:
            - bytes: bool (default=False) to specify if the output format is bytes field or str.
                False to convert the result into str
                True to convert the result into bytes field
            - compress: bool (default=False) to specify if the datas must be compressed before the conversion.
                False to keep the datas
                True to compress datas
            - b64: bool (default: determined by the converter) to force the converter to consider incoming data as b64.
                True: the incoming data is in base 64 format
                False: the incoming data isn't in base 64 format
            - loads: bool (default=False) to specify if the converter has to try to convert self.transform into dict/list object

        Returns:
            There is no return value because we are in the __init__ method.
            To prevent this, the attribute self.transform stores the result of the conversion.

        Attributes:
            self.data = stores the incoming datas
            self.transform = stores the output datas
            self.bytes = stores the _bytes flag
            self.compressed = stores the compressed flag
            self.loads = stores the loads flag
        """

        self.data = data
        self.transform = data
        self.bytes = False
        self.compressed = False
        self.loads = False

        # Set the options
        if "bytes" in kwargs and type(kwargs["bytes"]) is bool:
            self.bytes = kwargs["bytes"]
        if "compress" in kwargs and type(kwargs["compress"]) is bool:
            self.compressed = kwargs["compress"]

        if "loads" in kwargs and type(kwargs["loads"]) is bool:
            self.loads = kwargs["loads"]

        if "b64" in kwargs and type(kwargs["b64"]) is bool:
            is_base64 = kwargs["b64"]
        else:
            # Determines in which way the conversion must be done
            is_base64 = Converter.is_base64(data)

        # Obj to b64 conversion
        if is_base64 is False:
            is_compressed = Converter.is_compressed(self.transform)

            if is_compressed is False and self.compressed is True:
                self.transform = Converter.obj_to_bytes(self.transform)
                self.transform = Converter.bytes_to_compress(self.transform)
            elif is_compressed is True and self.compressed is False:
                # In this case self.transform is already bytes field
                self.transform = Converter.decompress_to_bytes(self.transform)
            else:
                self.transform = Converter.obj_to_bytes(self.transform)
            self.transform = Converter.bytes_to_b64(self.transform, self.bytes)
        else:
            # B64 to obj conversion
            self.transform = Converter.b64_to_bytes(self.transform)
            try:
                self.transform = Converter.decompress_to_bytes(self.transform)
            except:
                pass
            if self.bytes is False:
                try:
                    tmp = Converter.bytes_to_str(self.transform)
                    self.transform = tmp
                except:
                    pass
            if self.loads is True:
                try:
                    self.transform = json.loads(self.transform)
                except:
                    pass

    @staticmethod
    def obj_to_str(obj):
        """Transform conventionnals objects to string object
        Params:
            obj: the input object can be :
                - a list,
                - a dict,
                - a tuple,
                - a string
                - a ConfigParser object
                - a file object (keep the cursor position).
                    /!\ The file is NOT close at the end
                    of the conversion
        Returns:
            str if success or False if failure
        """
        if type(obj) is str:
            return obj
        if type(obj) in (list, dict, tuple):
            obj = json.dumps(obj)
            return obj
        elif isinstance(obj, configparser.ConfigParser):
            obj = obj.__dict__["_sections"].__repr__()
            return obj
        if isinstance(obj, io.IOBase):
            content = None
            if obj.closed or obj.readable() is False:
                with open(obj.name, "rb") as fp:
                    content = fp.read()
                    fp.close()
                # here the content is in bytes
                return bytes.decode(content, "utf-8")
            else:
                position = obj.tell()
                obj.seek(0, 0)
                content = obj.read()
                obj.seek(position, 0)
                if type(content) is str:
                    return content
                else:
                    return bytes.decode(content, "utf-8")
        else:
            return False

    @staticmethod
    def str_to_bytes(string):
        """Convert str object to bytes field
        Params:
            - string: the string we want to convert to bytes field
        Returns:
            A bytes field if success or False if failure
        """
        if type(string) is str:
            string = bytes(string, "utf-8")
            return string
        else:
            return False

    @staticmethod
    def obj_to_bytes(obj):
        """Convert conventionnals objects to bytes field
        Params:
            obj: the object we want to convert to bytes field. The object could be
                - a list
                - a dict
                - a string
                - a tuple
                - a configParserObject
                - a file object (keep the cursor position).
                    /!\ The file is NOT close at the end
                    of the conversion
        Returns:
            Field of bytes if success or False if failure
        """
        # obj is already bytes
        if type(obj) is bytes:
            return obj

        if isinstance(obj, io.IOBase):
            content = None
            if obj.closed or obj.readable() is False:
                with open(obj.name, "rb") as fp:
                    content = fp.read()
                    fp.close()
                # here the content is in bytes
                return content
            else:
                position = obj.tell()
                obj.seek(0, 0)
                content = obj.read()
                obj.seek(position, 0)
                if type(content) is bytes:
                    return content
                else:
                    return Converter.str_to_bytes(content)

        obj = Converter.obj_to_str(obj)
        return Converter.str_to_bytes(obj)

    @staticmethod
    def bytes_to_str(field):
        """Transform the specified bytes field to str
        Params:
            field: bytes field
        Returns: str
        """
        field = bytes.decode(field, "utf-8")
        return field

    @staticmethod
    def bytes_to_b64(field, _bytes=False):
        """Convert bytes field to base64
        Params:
            field: the bytes field we want to convert to base64
            _bytes (default = False) : a flag to specify if the result must be
                 a string (_bytes = False) or a bytes field (_bytes = True)
        Returns:
            base64 bytes field or str
        """
        if type(field) is bool:
            return False

        field = base64.b64encode(field)
        if _bytes is False:
            field = bytes.decode(field, "utf-8")
        return field

    @staticmethod
    def str_to_b64(string, _bytes=False):
        """Convert a string to base64
        Params:
            string : the string we want to convert to base64
            _bytes (default = False) : Specify if the result is bytes field or string
        Returns:
            base64 bytes field or str
        """
        string = Converter.str_to_bytes(field)
        string = base64.b64encode(field)
        if _bytes is False:
            string = bytes.decode(field, "utf-8")
        return string

    @staticmethod
    def obj_to_b64(obj, _bytes=False):
        """Convert a conventionnal object to base64.
        Params:
            - obj : can be
                - a string
                - a bytes field
                - a list
                - a dict
                - a tuple
                - a ConfigParser
            - _bytes (default = False) : Specify if the result is bytes field or string
        Returns:
            base64 bytes field or str
        """
        obj = Converter.obj_to_bytes(obj)
        if obj is False:
            return False
        obj = Converter.bytes_to_b64(obj, _bytes)
        return obj

    @staticmethod
    def b64_to_bytes(b64):
        """Convert base64 string or bytes field to bytes field
        Params:
            base64 : can be encoded string or encoded bytes field.
        Returns:
            decoded bytes field
        """
        if type(b64) not in (bytes, str):
            return False

        if type(b64) is str:
            # Convert b64-byte before converting b64
            b64 = bytes(b64, "utf-8")
        # convert
        try:
            b64 = base64.b64decode(b64, validate=True)
        except Exception as err:
            return False
        return b64

    @staticmethod
    def b64_to_str(b64):
        """Convert base64 string or bytes field to string
        Params:
            base64 : can be encoded string or encoded bytes field.
        Returns:
            decoded string
        """
        if type(b64) not in (bytes, str):
            return False

        if type(b64) is str:
            # Convert b64-byte before converting b64
            b64 = bytes(b64, "utf-8")
        # convert
        try:
            b64 = base64.b64decode(b64, validate=True)
        except Exception as err:
            return False
        b64 = bytes.decode(b64, "utf-8")
        return b64

    @staticmethod
    def is_base64(b64):
        """Test if the input is base64 bytes field or string
        Params:
            b64 : challeged bytes field or string
        Returns:
            Bool True if b64 is a valid base64, else False
        """
        if type(b64) not in (bytes, str):
            return False

        if type(b64) is str:
            # Convert b64-byte before converting b64
            b64 = bytes(b64, "utf-8")
        # convert
        try:
            b64 = base64.b64decode(b64, validate=True)
        except Exception as err:
            return False
        return True

    @staticmethod
    def bytes_to_compress(data):
        """Compress the specified incoming datas in gzip format.
        Params:
            data: bytes field which will be compressed
        Returns:
            Gzip compressed bytes field
        """
        compressed = zlib.compress(data, 9)
        return compressed

    @staticmethod
    def str_to_compress(string):
        """Compress incoming str value.
        Params:
            string: str which will be compressed
        Returns:
            Gzip comrpessed bytes field"""
        string = Converter.str_to_bytes(string)
        compressed = Converter.bytes_to_compress(string)
        return compressed

    @staticmethod
    def decompress_to_bytes(compressed):
        """Decompress Gzip bytes field to bytes field
        Params:
            compressed: Gzipped bytes field
        Returns:
            uncompressed bytes field"""
        data = zlib.decompress(compressed)
        return data

    @staticmethod
    def decompress_to_str(compressed):
        """Decompress Gzip bytes field to str
        Params:
            compressed: Gzipped bytes field
        Returns:
            uncompressed str"""
        data = zlib.decompress(compressed)
        data = Converter.bytes_to_str(data)
        return data

    @staticmethod
    def is_compressed(data):
        """Test if the specified bytes field is compressed
        Params:
            data : bytes field
        Returns:
            bool, True if the bytes field is compressed, False if not"""
        compressed = True
        try:
            zlib.decompress(data)
        except:
            compressed = False
        return compressed

    def __str__(self):
        """Gives a printable representation of the self.transform value.
        If self.transform is a base 64, split every 76 chars to corresponds to rfc4648

        Returns:
            str
        """
        content = self.transform
        if Converter.is_base64(self.transform):
            if type(self.transform) is str:
                return "\n".join(
                    self.transform[pos : pos + 76]
                    for pos in range(0, len(self.transform), 76)
                )
            else:
                return "%s" % self.transform
        else:
            return "%s" % self.transform

    def __repr__(self):
        """Gives an official representation value for the transformed value

        Returns :
            mixed values: may be dict, list, string, bytes, depending on the transformation
        """
        return self.transform
