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

#file : master/lib/utils.py

import netifaces
import json
import subprocess
import sys
import os
import fnmatch
import platform
import logging
import ConfigParser
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
import urllib
import uuid
import time
from datetime import datetime
import imp
import requests
from Crypto import Random
from Crypto.Cipher import AES
import urllib2
import tarfile
import zipfile
from functools import wraps

logger = logging.getLogger()

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "pluginsmaster"))

if sys.platform.startswith('win'):
    import wmi
    import pythoncom
    import _winreg as wr
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

def dump_parameter(para=True, out=True, timeprocess = True):
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
                    args=dict(zip(arg_names, dec_fn_args)),
                    kwargs=dec_fn_kwargs)
                result = ', '.join([
                        '{}={}'.format(str(k), repr(v)) for k, v in params.items()])
                log.info('\n@@@ call func : {}({}) file {}'.format(func_name,result, filepath))
                log.info('\n@@@ call func : {}({}) file {}'.format(func_name,result, filepath))
            else:
                log.info('\n@@@ call func : {}() file {}'.format(func_name, filepath))
            # Execute wrapped (decorated) function:
            outfunction = decorated_function(*dec_fn_args, **dec_fn_kwargs)
            timeruntime = time.time() - start
            if out:
                if timeprocess:
                    log.info('\n@@@ out func :{}() in {}s is -->{}'.format(func_name,
                                                                           timeruntime,
                                                                           outfunction))
                else:
                    log.info('\n@@@ out func :{}() is -->{}'.format(func_name,
                                                                    outfunction))
            else:
                if timeprocess:
                    log.info('\n@@@ out func :{}() in {}s'.format(func_name,
                                                                  timeruntime))
                else:
                    log.info('\n@@@ out func :{}()'.format(func_name))
            return outfunction
        return wrapper
    return decorated
###########################################

def file_get_contents(filename, use_include_path=0, context=None, offset=-1, maxlen=-1):
    """
        load content file or simple url
    """
    if (filename.find('://') > 0):
        ret = urllib2.urlopen(filename).read()
        if (offset > 0):
            ret = ret[offset:]
        if (maxlen > 0):
            ret = ret[:maxlen]
        return ret
    else:
        fp = open(filename, 'rb')
        try:
            if (offset > 0):
                fp.seek(offset)
            ret = fp.read(maxlen)
            return ret
        finally:
            fp.close()

def file_put_contents(filename,  data):
    """
    write content "data" to file "filename"
    """
    f = open(filename, 'w')
    f.write(data)
    f.close()

def file_put_contents_w_a(filename, data, option = "w"):
    if option == "a" or  option == "w":
        f = open( filename, option )
        f.write(data)
        f.close()

def displayDataJson(jsondata):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(jsondata)

def loadModule(filename):
    if filename == '':
        raise RuntimeError, 'Empty filename cannot be loaded'
    searchPath, file = os.path.split(filename)
    if not searchPath in sys.path:
        sys.path.append(searchPath)
        sys.path.append(os.path.normpath(searchPath+"/../"))
    moduleName, ext = os.path.splitext(file)
    fp, pathName, description = imp.find_module(moduleName, [searchPath,])
    try:
        module = imp.load_module(moduleName, fp, pathName, description)
    finally:
        if fp:
            fp.close()
    return module

def call_plugin(name, *args, **kwargs):
    nameplugin = os.path.join(args[0].modulepath, "plugin_%s"%name)
    objxmpp = args[0]
    #add compteur appel plugins
    count = 0
    try:
        count = getattr(args[0], "num_call%s"%name)
    except AttributeError:
        count = 0
        setattr(args[0], "num_call%s"%name, count)
    if objxmpp.config.executiontimeplugins:
        tmps1=time.clock()
        pluginaction = loadModule(nameplugin)
        pluginaction.action(*args, **kwargs)
        setattr(args[0], "num_call%s"%name, count + 1)
        tmps2=time.clock()-tmps1
        logger.info("_xmpp_ %s Execution time: [%s] %s"% (str(datetime.now()), name, tmps2 ) )
        cmd = "cat /proc/%s/status | grep Threads"%os.getpid()
        obj = simplecommandstr(cmd)
        file_put_contents_w_a("/tmp/Execution_time_plugin.txt",
                            "%s  [%s] Execution time: %s | %s \n" %(str(datetime.now()),
                                                                    name,
                                                                    tmps2,
                                                                    obj['result'] ) ,
                                                                    "a")
    else:
        pluginaction = loadModule(nameplugin)
        pluginaction.action(*args, **kwargs)
        setattr(args[0], "num_call%s"%name, count + 1)

def utc2local (utc):
    """
    utc2local transform a utc datetime object to local object.

    Param:
        utc datetime which is not naive (the utc timezone must be precised)
    Returns:
        datetime in local timezone
    """
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp (epoch)
    return utc + offset


def getRandomName(nb, pref=""):
    a = "abcdefghijklnmopqrstuvwxyz0123456789"
    d = pref
    for t in range(nb):
        d = d + a[random.randint(0, 35)]
    return d

def data_struct_message(action, data = {}, ret=0, base64 = False, sessionid = None):
    if sessionid == None or sessionid == "" or not isinstance(sessionid, basestring):
        sessionid = action.strip().replace(" ", "")
    return { 'action' : action,
             'data' : data,
             'ret' : 0,
             "base64" : False,
             "sessionid" : getRandomName(4,sessionid)}

def add_method(cls):
    """ decorateur a utiliser pour ajouter une methode a un object """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
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
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

# windows


def get_connection_name_from_guid(iface_guids):
    iface_names = ['(unknown)' for i in range(len(iface_guids))]
    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
    reg_key = wr.OpenKey(
        reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    for i in range(len(iface_guids)):
        try:
            reg_subkey = wr.OpenKey(reg_key, iface_guids[i] + r'\Connection')
            iface_names[i] = wr.QueryValueEx(reg_subkey, 'Name')[0]
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
    win32net.NetUserAdd(None, 2, {
        'name': username,
        'password': password,
        'priv': win32netcon.USER_PRIV_USER,
        'comment': comment,
        'flags': (win32netcon.UF_NORMAL_ACCOUNT
                  | win32netcon.UF_PASSWD_CANT_CHANGE
                  | win32netcon.UF_DONT_EXPIRE_PASSWD),
        'full_name': full_name,
        'acct_expires': win32netcon.TIMEQ_FOREVER,
    })

    win32net.NetLocalGroupAddMembers(None, 'Users', 3, [
        {'domainandname': r'{0}\{1}'.format(socket.gethostname(), username)}])

    # hide_user_account(username)
    return True


def isWinUserAdmin():
    if os.name == 'nt':
        import ctypes
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            # print "Admin check failed, assuming not an admin."
            return False
    elif os.name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError, "Unsupported operating system for this module: %s" % (os.name,)

# mac OS


def isMacOsUserAdmin():
    obj = simplecommand("cat /etc/master.passwd")  # For linux "cat /etc/shadow")
    if int(obj['code']) == 0:
        return True
    else:
        return False


def name_random(nb, pref=""):
    a = "abcdefghijklnmopqrstuvwxyz0123456789"
    d = pref
    for t in range(nb):
        d = d+a[random.randint(0, 35)]
    return d

def name_randomplus(nb, pref=""):
    a = "abcdefghijklnmopqrstuvwxyz0123456789"
    q = str(uuid.uuid4())
    q = pref + q.replace("-","")
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
            if_mac = shorten_mac(addrs[netifaces.AF_LINK][0]['addr'])
            if_ip = addrs[netifaces.AF_INET][0]['addr']
            address = int(if_mac, 16)
            if address != 0:
                listmacaddress[address] = if_mac
        except:
            pass
    return listmacaddress


def name_jid():
    dd = getShortenedIpList()
    cc = dd.keys()
    cc.sort()
    return dd[cc[0]]


def getIPAdressList():
    ip_list = []
    for interface in netifaces.interfaces():
        try:
            for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                if link['addr'] != '127.0.0.1':
                    ip_list.append(link['addr'])
        except:
            pass
    return ip_list


def shorten_mac(mac):
    mac = mac.lower()
    mac = mac.replace(":", "")
    mac = mac.replace("-", "")
    mac = mac.replace(" ", "")
    #mac = mac.replace("/","")
    return mac

# 3 functions used for subnet network


def ipV4toDecimal(ipv4):
    d = ipv4.split('.')
    return (int(d[0])*256*256*256) + (int(d[1])*256*256) + (int(d[2])*256) + int(d[3])


def decimaltoIpV4(ipdecimal):
    a = float(ipdecimal)/(256*256*256)
    b = (a - int(a))*256
    c = (b - int(b))*256
    d = (c - int(c))*256
    return "%s.%s.%s.%s" % (int(a), int(b), int(c), int(d))


def subnetnetwork(adressmachine, mask):
    adressmachine = adressmachine.split(":")[0]
    reseaumachine = ipV4toDecimal(adressmachine) & ipV4toDecimal(mask)
    return decimaltoIpV4(reseaumachine)


def is_valid_ipv4(ip):
    """Validates IPv4 addresses.
    """
    pattern = re.compile(r"""
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
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None


def is_valid_ipv6(ip):
    """Validates IPv6 addresses.
    """
    pattern = re.compile(r"""
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
    """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
    return pattern.match(ip) is not None

# linux systemd or init


def typelinux():
    p = subprocess.Popen('cat /proc/1/comm',
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    code_result = p.wait()
    system = result[0].rstrip('\n')
    """returns the list of ip gateway related to the interfaces"""
    return system


def isprogramme(name):
    obj = {}
    p = subprocess.Popen("which %s" % (name),
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code'] = p.wait()
    obj['result'] = result
    # print obj['code']
    # print obj['result']
    # print obj
    if obj['result'] != "":
        return True
    else:
        return False


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


def simplecommandstr(cmd):
    obj = {}
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code'] = p.wait()
    obj['result'] = "\n".join(result)
    return obj


def servicelinuxinit(name, action):
    obj = {}
    p = subprocess.Popen("/etc/init.d/%s %s" % (name, action),
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    result = p.stdout.readlines()
    obj['code'] = p.wait()
    obj['result'] = result
    return obj

# restart service


def service(name, action):  # start | stop | restart | reload
    obj = {}
    if sys.platform.startswith('linux'):
        system = ""
        p = subprocess.Popen('cat /proc/1/comm',
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        result = p.stdout.readlines()
        code_result = p.wait()
        system = result[0].rstrip('\n')
        if system == "init":
            p = subprocess.Popen("/etc/init.d/%s %s" % (name, action),
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            result = p.stdout.readlines()
            obj['code'] = p.wait()
            obj['result'] = result
        elif system == "systemd":
            p = subprocess.Popen("systemctl %s %s" % (action, name),
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            result = p.stdout.readlines()
            obj['code'] = p.wait()
            obj['result'] = result
    elif sys.platform.startswith('win'):
        pythoncom.CoInitialize()
        try:
            wmi_obj = wmi.WMI()
            wmi_sql = "select * from Win32_Service Where Name ='%s'" % name
            wmi_out = wmi_obj.query(wmi_sql)
        finally:
            pythoncom.CoUninitialize()
        for dev in wmi_out:
            print dev.Caption
        pass
    elif sys.platform.startswith('darwin'):
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
        print dev.Caption
        print dev.DisplayName


def joint_compteAD(domain, password, login, group):
    # https://msdn.microsoft.com/en-us/library/windows/desktop/aa392154%28v=vs.85%29.aspx
    pythoncom.CoInitialize()
    try:
        c = wmi.WMI()
        for computer in c.Win32_ComputerSystem():
            if computer.PartOfDomain:
                print computer.Domain  # DOMCD
                print computer.SystemStartupOptions
                computer.JoinDomainOrWorkGroup(domain, password, login, group, 3)
    finally:
        pythoncom.CoUninitialize()


def windowsservice(name, action):
    pythoncom.CoInitialize()
    try:
        wmi_obj = wmi.WMI()
        wmi_sql = "select * from Win32_Service Where Name ='%s'" % name
        print wmi_sql
        wmi_out = wmi_obj.query(wmi_sql)
    finally:
        pythoncom.CoUninitialize()
    print len(wmi_out)
    for dev in wmi_out:
        print dev.caption
        if action.lower() == "start":
            dev.StartService()
        elif action.lower() == "stop":
            print dev.Name
            dev.StopService()
        elif action.lower() == "restart":
            dev.StopService()
            dev.StartService()
        else:
            pass


#windowsservice("FusionInventory-Agent", "Stop")

def methodservice():
    import pythoncom
    import wmi
    pythoncom.CoInitialize()
    try:
        c = wmi.WMI()
        for method in c.Win32_Service._methods:
            print method
    finally:
        pythoncom.CoUninitialize()


def file_get_content(path):
    inputFile = open(path, 'r')  # Open test.txt file in read mode
    content = inputFile.read()
    inputFile.close()
    return content


def file_put_content(filename, contents, mode="w"):
    fh = open(filename, mode)
    fh.write(contents)
    fh.close()

# windows
# def listusergroup():
    #import wmi
    #c = wmi.WMI()
    # for group in c.Win32_Group():
    # print group.Caption
    # for user in group.associators("Win32_GroupUser"):
    # print "  ", user.Caption

# decorator to simplify the plugins


def pluginprocess(func):
    def wrapper(xmppobject, action, sessionid, data, message, dataerreur):
        resultaction = "result%s" % action
        result = {}
        result['action'] = resultaction
        result['ret'] = 0
        result['sessionid'] = sessionid
        result['base64'] = False
        result['data'] = {}
        dataerreur['action'] = resultaction
        dataerreur['data']['msg'] = "ERROR : %s" % action
        dataerreur['sessionid'] = sessionid
        try:
            response = func(xmppobject, action, sessionid, data, message, dataerreur, result)
            # encode  result['data'] if needed
            # print result
            if result['base64'] == True:
                result['data'] = base64.b64encode(json.dumps(result['data']))
            xmppobject.send_message(mto=message['from'],
                                    mbody=json.dumps(result),
                                    mtype='chat')
        except:
            xmppobject.send_message(mto=message['from'],
                                    mbody=json.dumps(dataerreur),
                                    mtype='chat')
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
        response = func(xmppobject, action, sessionid, data, message, ret, objsessiondata)
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
            response = func(xmppobject, action, sessionid, data,
                            message, ret, dataobj, objsessiondata)
            if sessionaction == "clear" and objsessiondata != None:
                xmppobject.session.clear(sessionid)
            elif sessionaction == "actualise":
                xmppobject.session.reactualisesession(sessionid, 10)
            return response
        return wrapper
    return decorator


def searchippublic(site=1):
    if site == 1:
        try:
            page = urllib.urlopen("http://ifconfig.co/json").read()
            objip = json.loads(page)
            if is_valid_ipv4(objip['ip']):
                return objip['ip']
            else:
                return searchippublic(3)
        except BaseException:
            return searchippublic(2)
    elif site == 2:
        try:
            page = urllib.urlopen("http://www.monip.org/").read()
            ip = page.split("IP : ")[1].split("<br>")[0]
            if is_valid_ipv4(ip):
                return ip
            else:
                return searchippublic(3)
        except Exception:
            return searchippublic(3)
    elif site == 3:
        try:
            ip = urllib.urlopen("http://ip.42.pl/raw").read()
            if is_valid_ipv4(ip):
                return ip
            else:
                return searchippublic(4)
        except Exception:
            searchippublic(4)
    elif site == 4:
        return find_ip()
    return None


def find_ip():
    candidates = []
    for test_ip in ['192.0.2.0', "192.51.100.0", "203.0.113.0"]:
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
        self.obj['timeout'] = timeout
        self.obj['cmd'] = cmd
        self.obj['result'] = "result undefined"
        self.obj['code'] = 255
        self.obj['separateurline'] = os.linesep

    def run(self):
        def target():
            # print 'Thread started'
            self.process = subprocess.Popen(self.obj['cmd'],
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT)
            self.obj['result'] = self.process.stdout.readlines()
            self.obj['code'] = self.process.wait()
            self.process.communicate()
            # print 'Thread finished'
        thread = threading.Thread(target=target)
        thread.start()

        thread.join(self.obj['timeout'])
        if thread.is_alive():
            print 'Terminating process'
            print "timeout %s" % self.obj['timeout']
            #self.codereturn = -255
            #self.result = "error tineour"
            self.process.terminate()
            thread.join()

        #self.result = self.process.stdout.readlines()
        self.obj['codereturn'] = self.process.returncode

        if self.obj['codereturn'] == -15:
            self.result = "error tineout"

        return self.obj


def ipfromdns(name_domaine_or_ip):
    """ This function converts a dns to ipv4
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
    """ This function check if socket valid for connection
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


unpad = lambda s : s[0:-ord(s[-1])]
class AESCipher:

    def __init__( self, key , BS = 32):
        self.key = key
        self.BS = BS

    def _pad(self, s):
        return s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)

    def encrypt( self, raw ):
        raw = self._pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))

def make_tarfile(output_file_gz_bz2, source_dir, compresstype="gz"):
    """
        creation archive tar.gz or tar.bz2
        compresstype "gz" or "bz2"
    """
    try:
        with tarfile.open(output_file_gz_bz2, "w:%s"%compresstype) as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        return True
    except Exception:
        logger.error("Error creating tar.%s archive : %s"%(compresstype, str(e)))
        return False

def extract_file(imput_file__gz_bz2, to_directory='.', compresstype="gz"):
    """
        extract archive tar.gz or tar.bz2
        compresstype "gz" or "bz2"
    """
    cwd = os.getcwd()
    absolutepath = os.path.abspath(imput_file__gz_bz2)
    try:
        os.chdir(to_directory)
        with tarfile.open(absolutepath, "r:%s"%compresstype) as tar:
            tar.extractall()
        return True
    except OSError as e:
        logger.error( "Error creating tar.%s archive : %s"%(str(e),compresstype))
        return False
    except Exception as e:
        logger.error( "Error creating tar.%s archive : %s"%(str(e),compresstype))
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
    listfile=[]
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if abspath:
                listfile.append(os.path.join(root, basename))
            else:
                listfile.append(os.path.join(basename))
    return listfile

def md5folder(directory):
    hash = hashlib.md5()
    strmdr=[]
    for root, dirs, files in os.walk(directory):
        for basename in files:
            hash.update(md5(os.path.join(root, basename)))
    return hash.hexdigest()


def Setdirectorytempinfo():
    """
    create directory
    """
    dirtempinfo = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "INFOSTMP")
    if not os.path.exists(dirtempinfo):
        os.makedirs(dirtempinfo, mode=0700)
    return dirtempinfo


class geolocalisation_agent:
    def __init__(self,
                 typeuser = "public",
                 geolocalisation=True,
                 ip_public=None,
                 strlistgeoserveur=""):
        self.determination = False
        self.geolocalisation = geolocalisation
        self.ip_public = ip_public
        self.typeuser = typeuser
        self.filegeolocalisation = os.path.join(Setdirectorytempinfo(),
                                          'filegeolocalisation')
        self.listgeoserver = ["http://%s/json"%x for x in re.split(r'[;,\[\(\]\)\{\}\:\=\+\*\\\?\/\#\+\&\-\$\|\s]',
                                              strlistgeoserveur)  if x.strip()!=""];
        self.localisation = None
        self.getgeolocalisation()
        if self.localisation is None:
            self.localisation=self.getdatafilegeolocalisation()

    def getgeolocalisationobject(self):
        if self.localisation is None:
            return {}
        return self.localisation

    def getdatafilegeolocalisation(self):
        if self.geoinfoexist():
            try:
                with open(self.filegeolocalisation) as json_data:
                    self.localisation=json.load(json_data)
                self.determination = False
                return self.localisation
            except Exception:
                pass
        return None

    def setdatafilegeolocalisation(self):
        if self.localisation is not None:
            try:
                with open(self.filegeolocalisation, 'w') as json_data:
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
            if self.typeuser in ["public", "nomade", "both"] or self.localisation is None:
                # on recherche a chaque fois les information
                self.localisation = geolocalisation_agent.searchgeolocalisation(self.listgeoserver)
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
                    self.localisation = geolocalisation_agent.searchgeolocalisation(self.listgeoserver)
                    self.setdatafilegeolocalisation()
                    self.determination = True
                    return self.localisation
            return None
        else:
            if not self.geoinfoexist():
                self.localisation = geolocalisation_agent.searchgeolocalisation(self.listgeoserver)
                self.setdatafilegeolocalisation()
                self.determination = True
                return self.localisation

        return self.localisation

    def get_ip_public(self):
        if self.geolocalisation:
            if self.localisation is  None:
                self.getgeolocalisation()
            if self.localisation is not None and is_valid_ipv4(self.localisation['ip']):
                if not self.determination:
                    logger.warning("Determination use file")
                self.ip_public = self.localisation['ip']
                return self.localisation['ip']
            else :
                return None
        else:
            if not self.determination:
                logger.warning("use old determination ip_public")
            if self.localisation is  None:
                if self.geoinfoexist():
                    dd=self.getdatafilegeolocalisation()
                    logger.warning("%s"%dd)
                    if  self.localisation is  not None:
                        return self.localisation['ip']
            else:
                return self.localisation['ip']
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
            objip = json.loads(urllib.urlopen(url).read())
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
                if  objip is None:
                    raise
                return objip
            except BaseException:
                pass
        return None
