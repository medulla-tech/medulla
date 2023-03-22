# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
dlp API v1
"""

import os
import cherrypy
from cherrypy.lib.static import serve_file
import logging
import tempfile
import shutil
import time
import urllib2
from base64 import b64decode

from pulse2.utils import isMACAddress
from pulse2.dlp.tools import HOSTNAME_KEY, MAC_KEY, UUID_KEY, COMMANDS_KEY
from pulse2.dlp.utils import download_file, make_zipfile, log


class Root(object):
    pass


class Auth(object):
    exposed = True
    _cp_config = {'tools.json_out.on': True,
                  'tools.xmlrpc_client.on': True}

    def POST(self, authkey, mac_list, hostname):
        log("Authenticate computer %s with authkey %s" % (hostname, authkey))
        if not authkey == cherrypy.config.get("dlp.authkey"):
            log("Failed to authenticate computer %s, authkey missmatch." % hostname, severity=logging.ERROR)
            raise cherrypy.HTTPError(401, "Not authorized")

        if isinstance(mac_list, basestring):
            mac_list = [mac_list]

        # Validate input values
        for mac in mac_list:
            if not isMACAddress(mac):
                raise cherrypy.HTTPError(400, "MAC address is not correct")

        try:
            uuid = cherrypy.request.xmlrpc_client.pull_target_awake(hostname, mac_list)
            if uuid is not None and uuid:
                cherrypy.session[HOSTNAME_KEY] = hostname
                cherrypy.session[MAC_KEY] = mac_list
                cherrypy.session[UUID_KEY] = uuid
                cherrypy.session.save()
                log("Result: %s" % uuid)
                return "OK"
            else:
                log("Not recognized machine, hostname=%s, mac_list=%s" % (hostname, mac_list), severity=logging.WARNING, traceback=True)
                raise cherrypy.HTTPError(404, "Not found")
        except cherrypy.HTTPError:
            raise
        except:
            log("pull_target_awake failed\n", severity=logging.ERROR, traceback=True)
            raise cherrypy.HTTPError(503, "Service unavailable")


class Commands(object):
    exposed = True
    _cp_config = {'tools.is_authorized.on': True,
                  'tools.json_out.on': True,
                  'tools.xmlrpc_client.on': True}

    def check_cache(self, package_uuid, package_path):
        if os.path.exists(package_path):
            stat_info = os.stat(package_path)
            current_time = int(time.time())
            # package cache is too old
            if current_time - cherrypy.config.get('dlp.cache_expire') > stat_info.st_ctime:
                return False
            else:
                return True
        return False

    def create_package(self, package_uuid, package_path, command):
        lock_file = package_path + '.lock'
        if not os.path.exists(lock_file):
            try:
                with file(lock_file, 'a'):
                    os.utime(lock_file, None)
                log("Creating package %s..." % package_path)
                if os.path.exists(package_path):
                    os.unlink(package_path)
                tmp_dir = tempfile.mkdtemp(suffix=package_uuid)
                # FIXME use first mirror for now
                url = command['urls'][0]
                if url.startswith('http'):
                    url += "_files"
                for package_file in command.get('files', []):
                    log("Download %s" % url + package_file)
                    download_file(url + package_file, tmp_dir, 0)
                make_zipfile(package_path, tmp_dir)
                shutil.rmtree(tmp_dir)
                log("Package %s created" % package_path)
                result = True
            except:
                log("Failed to create the package %s" % package_uuid, logging.ERROR, True)
                result = False
            # Cleanup before releasing...
            os.unlink(lock_file)
            return result
        # Another thread is creating the package
        # wait for it....
        else:
            time.sleep(0.5)
            return self.create_package(package_uuid, package_path, command)
        # We should not get here
        return False

    def GET(self):
        try:
            log("Get commands")
            commands = cherrypy.request.xmlrpc_client.get_available_commands(cherrypy.session[UUID_KEY])
            # Get package files
            for index, command in enumerate(list(commands)):
                package_uuid = command.get('package_uuid', False)
                if package_uuid:
                    packages_cache = cherrypy.config.get("dlp.cache_dir")
                    if not os.path.exists(packages_cache):
                        os.mkdir(packages_cache)
                    package_path = os.path.join(packages_cache, "%s.zip" % package_uuid)

                    if self.check_cache(package_uuid, package_path):
                        log("Using cached package at %s" % package_path)
                    else:
                        if not self.create_package(package_uuid, package_path, command):
                            del commands[index]
                            log("Command %d removed from list" % command['id'], logging.ERROR)
                            continue
                    # Remove not used infos on the client side
                    del command['files']
                    del command['urls']
            log("Result: %s" % commands)
            cherrypy.session[COMMANDS_KEY] = commands
            cherrypy.session.save()
            return commands
        except:
            log("get_available_commands failed:\n", logging.ERROR, True)
            raise cherrypy.HTTPError(503, "Service Unavailable")


class File(object):
    exposed = True
    _cp_config = {'tools.is_authorized.on': True}

    @cherrypy.popargs('filename')
    def GET(self, filename):
        path = os.path.join(cherrypy.config.get("dlp.cache_dir"), filename)
        log("Wants to download %s" % filename)
        if not path or not os.path.exists(path):
            raise cherrypy.HTTPError(404, "Not found")

        # Don't let the client download all packages
        # lookup his commands to get the packages he can download
        commands = cherrypy.session.get(COMMANDS_KEY, [])
        allowed_packages = ["%s.zip" % c['package_uuid'] for c in commands if 'package_uuid' in c]
        log("Allowed packages are: %s" % ", ".join(allowed_packages))
        if not filename in allowed_packages:
            raise cherrypy.HTTPError(401, "Not authorized")

        log("Serving package: %s" % path)
        return serve_file(path, "application/x-download", "attachment")


class Step(object):
    exposed = True
    _cp_config = {'tools.is_authorized.on': True,
                  'tools.json_out.on': True,
                  'tools.xmlrpc_client.on': True}

    @cherrypy.popargs('coh_id', 'step_id')
    def POST(self, coh_id, step_id, stdout, stderr, return_code):
        #commands = cherrypy.session.get(COMMANDS_KEY, [])

        try:
            coh_id = int(coh_id)
        except ValueError:
            raise cherrypy.HTTPError(400, "Bad command id")

        try:
            return_code = int(return_code)
        except ValueError:
            raise cherrypy.HTTPError(400, "Bad return code")

        #if not coh_id in [c['id'] for c in commands]:
            #raise cherrypy.HTTPError(401, "Not authorized")

        #for command in commands:
            #if coh_id == command['id']:
                #break

        #if step_id not in command['steps']:
            #raise cherrypy.HTTPError(401, "Not a valid step")

        try:
            log("Saving result (%d) for step %s of command %s" % (return_code, step_id, coh_id))
            if not cherrypy.request.xmlrpc_client.completed_step(coh_id, step_id, stdout, stderr, return_code):
                raise cherrypy.HTTPError(503, "Failed to save the result")
            cherrypy.response.status = 201
            return "Created"
        except cherrypy.HTTPError:
            raise
        except:
            log("Saving step result failed.", logging.ERROR, True)
            raise cherrypy.HTTPError(503, "Service Unavailable")


class Inventory(object):
    exposed = True
    _cp_config = {'tools.is_authorized.on': True}

    def POST(self, inventory):
        inventory_uri = cherrypy.config.get("inventory.uri")
        data = b64decode(inventory)
        try:
            request = urllib2.Request(inventory_uri,
                                      data,
                                      headers={'User-Agent': 'DLP service',
                                               'Content-Type': 'application/x-www-form-urlencoded',
                                               'Content-Length': len(data)})
            opener = urllib2.build_opener()
            urllib2.install_opener(opener)
            response = opener.open(request)
            if response.code == 200:
                cherrypy.response.status = 201
            else:
                raise cherrypy.HTTPError(response.code, "Inventory server returned an error.")
        except (urllib2.URLError, urllib2.HTTPError):
            log("Failed to send the inventory to the inventory server", logging.ERROR, True)
            raise cherrypy.HTTPError(503, "Service Unavailable")


rootV1 = Root()
rootV1.auth = Auth()
rootV1.commands = Commands()
rootV1.step = Step()
rootV1.file = File()
rootV1.inventory = Inventory()
