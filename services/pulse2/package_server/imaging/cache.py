# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Caching related functions / objects
"""

import logging
import configparser
import os.path
import time

import pulse2.utils
import pulse2.package_server.config

# FIXME : shouldn't this cache be updated by the object itself ?


class UUIDCache(pulse2.utils.Singleton):
    """
    This is a object-cache for UUID/MAC conversion stuff.

    It work like this:
     - if info is in cache *and* less than memoryLifetime, serve it
     - if not, try to find it into the local cache (UUIDS.txt); it less than diskLifetime, serve it and update local cache, resetting lifetime
     - if not, try to find it asking the agent, updating both disk cache and local cache, resetting lifetime
    """

    log = logging.getLogger("imaging")
    config = configparser.RawConfigParser()

    def __init__(self):
        pulse2.utils.Singleton.__init__(self)
        self.cachePath = pulse2.package_server.config.P2PServerCP().imaging_api[
            "uuid_cache_file"
        ]
        self.cacheLifetime = pulse2.package_server.config.P2PServerCP().imaging_api[
            "uuid_cache_lifetime"
        ]

        self.log.info("Using %s as UUID Cache File" % self.cachePath)
        if not os.path.isfile(self.cachePath):
            try:
                self.log.info("Creating my UUID Cache File %s" % (self.cachePath))
                fp = open(self.cachePath, "w")
                self.config.write(fp)
                fp.close()
            except Exception as e:
                self.log.warn(
                    "Can't create my UUID Cache File %s : %s" % (self.cachePath, e)
                )
                return None
        if not self._fetch():
            return None

    def _flush(self):
        """
        Update cache file using our memory stucture
        """
        try:
            self.log.debug("Writing my UUID Cache File %s" % (self.cachePath))
            fp = open(self.cachePath, "w")
            self.config.write(fp)
            fp.close()
        except Exception as e:
            self.log.warn(
                "Can't write my UUID Cache File %s : %s" % (self.cachePath, e)
            )
            return False
        return True

    def _fetch(self):
        """
        Update memory stucture using our cache file
        """
        try:
            self.log.info("Reading my UUID Cache File %s" % (self.cachePath))
            fp = open(self.cachePath, "r")
            self.config.readfp(fp)
            fp.close()
        except Exception as e:
            self.log.warn("Can't read my UUID Cache File %s : %s" % (self.cachePath, e))
            return False
        return True

    def getByMac(self, mac):
        """
        Get a computer by its MAC from the cache.

        @param mac : the client mac address (mandatory)
        @type mac : str

        @return a dict(uuid, mac, shortname, fqdn, entity) or False
        @rtype dict
        """

        uuid = ""
        shortname = ""
        fqdn = ""

        if not pulse2.utils.isMACAddress(mac):
            return False

        mac = pulse2.utils.normalizeMACAddress(mac)

        for section in self.config.sections():
            if self.config.has_option(section, "mac"):
                if self.config.get(section, "mac") == mac:
                    uuid = section
                    if self.config.has_option(section, "shortname"):
                        shortname = self.config.get(section, "shortname")
                    else:
                        shortname = ""
                    if self.config.has_option(section, "fullname"):
                        fqdn = self.config.get(section, "fullname")
                    else:
                        fqdn = ""
                    if self.config.has_option(section, "entity"):
                        entity = self.config.get(section, "entity")
                    else:
                        entity = ""
                    if self.config.has_option(section, "updated"):
                        updated = self.config.getint(section, "updated")
                    else:
                        updated = 0
                    if int(time.time()) - updated > self.cacheLifetime:
                        self.log.debug(
                            "Cachefault on %s/%s (expired), ignoring" % (uuid, mac)
                        )
                        self.delete(uuid)
                        # do not break the flow
                        return False
                    return {
                        "uuid": uuid,
                        "mac": mac,
                        "shortname": shortname,
                        "fqdn": fqdn,
                        "entity": entity,
                        "updated": updated,
                    }
        return False

    def getByShortName(self, name):
        """
        Get a computer by its shortname from the cache.

        @param name : the client name (mandatory)
        @type name : str

        @return a dict(uuid, mac, shortname, fqdn) or False
        @rtype dict
        """

        uuid = ""
        mac = ""
        fqdn = ""

        for section in self.config.sections:
            if self.config.has_option(section, "shortname"):
                if self.config.get(section, "shortname") == name:
                    shortname = self.config.get(section, "shortname")
                    uuid = section
                    if self.config.has_option(section, "mac"):
                        mac = self.config.get(section, "mac")
                    else:
                        mac = ""
                    if self.config.has_option(section, "fullname"):
                        fqdn = self.config.get(section, "fullname")
                    else:
                        fqdn = ""
                    if self.config.has_option(section, "updated"):
                        updated = self.config.getint(section, "updated")
                    else:
                        updated = 0
                    if int(time.time() - updated) > self.cacheLifetime:
                        self.log.debug(
                            "Cachefault on %s/%s (expired), ignoring" % (uuid, mac)
                        )
                        # do not break the flow
                        # return False
                    return {
                        "uuid": uuid,
                        "mac": mac,
                        "shortname": shortname,
                        "fqdn": fqdn,
                        "updated": updated,
                    }
        return False

    def getByUUID(self, uuid):
        """
        Get a computer by its UUID from the cache.

        @param uuid : the client UUID (mandatory)
        @type uuid : str

        @return a dict(uuid, mac, shortname, fqdn) or False
        @rtype dict
        """

        mac = ""
        shortname = ""
        fqdn = ""

        if not pulse2.utils.isUUID(uuid):
            return False

        if self.config.has_section(uuid):
            if self.config.has_option(uuid, "mac"):
                mac = self.config.get(uuid, "mac")
            else:
                mac = ""
            if self.config.has_option(uuid, "shortname"):
                shortname = self.config.get(uuid, "shortname")
            else:
                shortname = ""
            if self.config.has_option(uuid, "fullname"):
                fqdn = self.config.get(uuid, "fullname")
            else:
                fqdn = ""
            if self.config.has_option(uuid, "updated"):
                updated = self.config.getint(uuid, "updated")
            else:
                updated = 0
            if int(time.time()) - updated > self.cacheLifetime:
                self.log.debug("Cachefault on %s/%s (expired), ignoring" % (uuid, mac))
                # do not break the flow
                # return False
            return {
                "uuid": uuid,
                "mac": mac,
                "shortname": shortname,
                "fqdn": fqdn,
                "updated": updated,
            }
        return False

    def get(self, uuid):
        """ """
        return self.getByUUID(uuid)

    def set(self, uuid, mac, shortname="", domain="", entity=""):
        """
        Add a computer in cache.

        @param uuid : the client UUID (mandatory)
        @type uuid : str
        @param mac : the client MAC address(mandatory)
        @type mac : str
        @param shortname : the client host name (default : '')
        @type shortname : str
        @param domain : the client domain name (default: '')
        @type domain : str
        @param entity : the client entity name (default: '')
        @type entity : str

        @return: True on success
        @rtype: boolean
        """

        # sanity check
        if not pulse2.utils.isMACAddress(mac):
            return False
        if not pulse2.utils.isUUID(uuid):
            return False

        # normalization
        fqdn = shortname + "." + domain
        mac = pulse2.utils.normalizeMACAddress(mac)
        updated = int(time.time())

        # check that if the UUID is already known, it's MAC is the same as our
        answer = self.getByUUID(uuid)
        if answer and answer["mac"] != mac:
            self.log.warn(
                "Cachefault on %s/%s (mac already known : %s), updating"
                % (uuid, mac, answer["mac"])
            )
            self.delete(uuid)

        # check that if the MAC is already known, it's UUID is the same as our
        answer = self.getByMac(mac)
        if answer and answer["uuid"] != uuid:
            self.log.warn(
                "Cachefault on %s/%s (uuid already known : %s), updating"
                % (uuid, mac, answer["uuid"])
            )
            self.delete(answer["uuid"])

        if not self.config.has_section(uuid):
            self.config.add_section(uuid)
        self.config.set(uuid, "mac", mac)
        self.config.set(uuid, "shortname", shortname)
        self.config.set(uuid, "fqdn", fqdn)
        self.config.set(uuid, "entity", entity)
        self.config.set(uuid, "updated", updated)
        self._flush()
        return True

    def setByUuid(self, _id, uuid, shortname="", domain="", entity=""):
        """
        Add a computer in cache.

        @param id : the client glpi ID
        @type id : str
        @param uuid : the client uuuid
        @type uuid : str
        @param shortname : the client host name (default : '')
        @type shortname : str
        @param domain : the client domain name (default: '')
        @type domain : str
        @param entity : the client entity name (default: '')
        @type entity : str

        @return: True on success
        @rtype: boolean
        """
        # normalization
        fqdn = shortname + "." + domain
        updated = int(time.time())

        # check that if the UUID is already known, it's MAC is the same as our
        answer = self.getByUuid(uuid)
        if answer and answer["uuid"] != uuid:
            self.log.warn(
                "Cachefault on %s/%s (uuid already known : %s), updating"
                % (_id, uuid, answer["uuid"])
            )
            self.delete(uuid)

        # check that if the MAC is already known, it's UUID is the same as our
        answer = self.getByUuid(uuid)
        if answer and answer["id"] != _id:
            self.log.warn(
                "Cachefault on %s/%s (id already known : %s), updating"
                % (id, uuid, answer["uuid"])
            )
            self.delete(answer["uuid"])

        if not self.config.has_section(uuid):
            self.config.add_section(uuid)
        self.config.set(uuid, "id", _id)
        self.config.set(uuid, "uuid", uuid)
        self.config.set(uuid, "shortname", shortname)
        self.config.set(uuid, "fqdn", fqdn)
        self.config.set(uuid, "entity", entity)
        self.config.set(uuid, "updated", updated)
        self._flush()

        return True

    def getByUuid(self, uuid):
        """
        Get a computer by its real UUID from the cache.

        @param uuid : the client real UUID (mandatory)
        @type uuid : str

        @return a dict(uuid, mac, shortname, fqdn) or False
        @rtype dict
        """

        shortname = ""
        fqdn = ""

        if self.config.has_section(uuid):
            # Everywhere uuid correspond to glpi_id, not the computer id
            _id = ""  # don't use id name because of the built-in function called id
            if self.config.has_option(uuid, "uuid"):
                _id = self.config.get(uuid, "uuid")

            shortname = ""
            if self.config.has_option(uuid, "shortname"):
                shortname = self.config.get(uuid, "shortname")

            mac = ""
            if self.config.has_option(uuid, "mac"):
                mac = self.config.get(uuid, "mac")

            fqdn = ""
            if self.config.has_option(uuid, "fullname"):
                fqdn = self.config.get(uuid, "fullname")

            updated = 0
            if self.config.has_option(uuid, "updated"):
                updated = self.config.getint(uuid, "updated")

            entity = ""
            if self.config.has_option(uuid, "entity"):
                entity = self.config.get(uuid, "entity")

            id = ""
            if self.config.has_option(uuid, "id"):
                id = self.config.get(uuid, "id")

            if int(time.time()) - updated > self.cacheLifetime:
                self.log.debug("Cachefault on %s/%s (expired), ignoring" % (uuid, mac))
                # do not break the flow
                # return False
            return {
                "uuid": uuid,
                "id": id,
                "mac": mac,
                "shortname": shortname,
                "fqdn": fqdn,
                "updated": updated,
                "entity": entity,
            }
        return False

    def delete(self, uuid):
        """
        Delete a computer from the cache.

        @param uuid: the client UUID (mandatory)
        @type uuid: str
        """
        if not pulse2.utils.isUUID(uuid):
            ret = False
        else:
            try:
                self.config.remove_section(uuid)
                self._flush()
                ret = True
            except Exception as e:
                self.log.error("Can't delete computer UUID %s from the cache: %s" % e)
                ret = False
        return ret
