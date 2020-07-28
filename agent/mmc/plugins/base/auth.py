# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import os
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
from mmc.support.mmctools import Singleton
from mmc.support.config import MMCConfigParser


class AuthenticationManager(Singleton):
    """
    Classes that are able to authenticate users by implementing the
    AuthenticatorI interface must register to this class.
    """

    components = []

    def __init__(self):
        Singleton.__init__(self)
        self.logger = logging.getLogger()

    def register(self, name, klass):
        """
        @param name: the name of the authenticator
        @param klass: the class name of the authenticator
        """
        self.logger.debug("Registering authenticator %s / %s" % (name, str(klass)))
        self.components.append((name, klass))

    def validate(self):
        ret = True
        tmp = []
        for name, klass in self.components:
            mandatory = True
            try:
                instance = klass()
                mandatory = instance.config.mandatory
                valid = instance.validate()
            except Exception, e:
                self.logger.exception(e)
                valid = False
            if valid:
                self.logger.info("Authenticator %s successfully validated" % name)
                tmp.append((name, klass))
            else:
                self.logger.info("Authenticator %s failed to validate" % name)
                if mandatory:
                    self.logger.error("Authenticator %s is configured as mandatory, exiting" % name)
                    ret = False
                else:
                    self.logger.info("Authenticator %s is not configured as mandatory, so going on" % name)
        self.components = tmp
        return ret

    def select(self, names):
        tmp = []
        if names:
            for name in names.split():
                for n, k in self.components:
                    if n == name:
                        self.logger.info("Selecting authenticator %s / %s" % (n, str(k)))
                        tmp.append((n, k))
        self.components = tmp

    def authenticate(self, user, password, session):
        """
        Loops on the authenticator chains until one successfully authenticates
        the user.

        @return: AuthenticationToken object
        @rtype: AuthenticationToken
        """
        token = AuthenticationToken()
        for name, klass in self.components:
            instance = klass()
            self.logger.debug("Try to authenticate user with %s / %s" % (name, str(klass)))
            if instance.config.authonly:
                if user.lower() not in instance.config.authonly:
                    self.logger.debug("User %s is not in the authonly list of this authenticator, so we skip it" % user)
                    continue
            if instance.config.exclude:
                if user.lower() in instance.config.exclude:
                    self.logger.debug("User %s is in the exclude list of this authenticator, so we skip it" % user)
            try:
                token = instance.authenticate(user, password)
            except Exception, e:
                self.logger.exception(e)
                raise AuthenticationError
            self.logger.debug("Authentication result: " + str(token.authenticated) + str(token.infos))
            if token.authenticated:
                # the authentication succeeded
                break
        token.session = session
        return token


class AuthenticatorConfig(MMCConfigParser):
    """
    Class to handle Authenticator object configuration
    """

    def __init__(self, conffile, section):
        ConfigParser.__init__(self)
        self.conffile = conffile
        self.section = section
        self.setDefault()
        fp = file(self.conffile, "r")
        self.readfp(fp, self.conffile)
        if os.path.isfile(self.conffile + '.local'):
            self.readfp(open(self.conffile + '.local','r'))
        self.readConf()
        fp.close()

    def readConf(self):
        for option in ["authonly", "exclude"]:
            try:
                self.__dict__[option] = self.get(self.section, option).lower().split()
            except NoSectionError:
                pass
            except NoOptionError:
                pass
        for option in ["mandatory"]:
            try:
                self.__dict__[option] = self.getboolean(self.section, option)
            except NoSectionError:
                pass
            except NoOptionError:
                pass

    def setDefault(self):
        self.authonly = None
        self.mandatory = True
        self.exclude = None


class AuthenticatorI:
    """
    Class for authenticator object.

    Instance of this object is able to authenticate a user with a login and
    password couple.
    """

    def __init__(self, conffile, name, klass = AuthenticatorConfig):
        """
        @param conffile: authenticator configuration file
        @param name: the authenticator name
        """
        self.logger = logging.getLogger()
        self.config = klass(conffile, "authentication_" + name)

    def authenticate(self, user, password):
        """
        @return: AuthenticationToken object
        @rtype: AuthenticationToken
        """
        raise "Must be implemented by the subclass"

    def validate(self):
        """
        Should be implemented by the subclass, as this default method always
        returns False.
        The method should check that the authenticator will work.

        @return: True if the authenticator can be used, else False
        """
        return False


class AuthenticationToken:
    """
    Store an authentication result

    @ivar authenticated: True if the authenticated succeeded, else False
    @ivar login: the user login
    @ivar infos: User informations (e.g. user LDAP entry)
    @ivar session: User session information (may be used during provisioning)
    """
    def __init__(self, authenticated = False, login = None, password = None, infos = None, session = None):
        self.authenticated = authenticated
        self.login = login
        self.infos = infos
        self.password = password
        self.session = None

    def isAuthenticated(self):
        return self.authenticated

    def getInfos(self):
        return self.infos

    def getLogin(self):
        return self.login

    def getPassword(self):
        return self.password

    def getSession(self):
        return self.session

class AuthenticationError(Exception):
    """
    Raised by the AuthenticationManager if the authentication process failed
    """
    pass
