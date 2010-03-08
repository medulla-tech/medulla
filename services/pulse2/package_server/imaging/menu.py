# -*- coding: utf-8; -*-
#
# (c) 2009-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
    client menu handling classes
"""

import pulse2.utils
import re
import os.path
import os
import logging
import time


def isMenuStructure(menu):
    """
    @return: True if the given object is a menu structure
    @rtype: bool
    """
    ret = True
    logger = logging.getLogger()
    if type(menu) == dict:
        for k in ['message', 'protocol', 'default_item', 'default_item_WOL',
                  'timeout', 'background_uri', 'bootservices', 'images']:
            if not k in menu:
                logger.debug("your menu is missing %s" % (k))
                ret = False
                break
    else:
        logger.debug("your menu is not a dict")
        ret = False
    return ret


class ImagingDefaultMenuBuilder:

    """
    Class that builds an imaging menu according to its dict structure.
    """

    def __init__(self, config, menu):
        self.logger = logging.getLogger()
        if not isMenuStructure(menu):
            raise TypeError('Bad menu structure')
        self.menu = menu
        self.config = config

    def make(self, macaddress = None):
        """
        @return: an ImagingMenu object
        @rtype: ImagingMenu
        """
        m = ImagingMenu(self.config, macaddress)
        m.setSplashScreen(self.menu['background_uri'])
        m.setMessage(self.menu['message'])
        m.setTimeout(self.menu['timeout'])
        m.setDefaultItem(self.menu['default_item'])
        m.setProtocol(self.menu['protocol'])
        for pos, entry in self.menu['bootservices'].items():
            m.addBootServiceEntry(int(pos), entry)
        for pos, entry in self.menu['images'].items():
            m.addImageEntry(int(pos), entry)
        self.logger.debug('Menu structure built successfully')
        return m


class ImagingComputerMenuBuilder(ImagingDefaultMenuBuilder):

    """
    Class that builds an imaging menu for a computer according to its dict
    structure.
    """

    def __init__(self, config, macaddress, menu):
        ImagingDefaultMenuBuilder.__init__(self, config, menu)
        self.macaddress = macaddress

    def make(self):
        self.logger.debug('Building menu structure for computer mac %s' % self.macaddress)
        return ImagingDefaultMenuBuilder.make(self, self.macaddress)


class ImagingMenu:

    """
    hold an imaging menu
    """

    DEFAULT_MENU_FILE = 'default'

    def __init__(self, config, macaddress = None):
        """
        Initialize this object.

        @param config: a ImagingConfig object
        @param macaddress: the client MAC Address
        """
        self.logger = logging.getLogger()
        self.config = config # the server configuration
        if macaddress:
            assert pulse2.utils.isMACAddress(macaddress)
        self.mac = macaddress # the client MAC Address

        # menu items
        self.menuitems = {}
        self.timeout = 0 # the menu timeout
        self.default_item = 0 # the menu default entry
        self.default_item_wol = 0 # the menu default entry on WOL
        self.splashscreen = None # the menu splashscreen
        self.message = None
        self.colors = { # menu colors
            'normal': {'fg': 7, 'bg': 1},
            'highlight': {'fg': 15, 'bg': 3}}
        self.keyboard = None # the menu keymap, None is C
        self.hidden = False # do we hide the menu ?

        # list of replacements to perform
        # a replacement is using the following structure :
        # key 'from' : the PCRE to look for
        # key 'to' : the replacement to perform
        # key 'when' : when to perform the replacement (only 'global' for now)
        self.replacements = [
            ('##PULSE2_LANG##', 'C', 'global'),
            ('##PULSE2_D_BOOTLOADER##', self.config.imaging_api['bootloader_folder'], 'global'),
            ('##PULSE2_F_BOOTSPLASH##', self.config.imaging_api['bootsplash_file'], 'global'),
            ('##PULSE2_D_DISKLESS##', self.config.imaging_api['diskless_folder'], 'global'),
            ('##PULSE2_F_KERNEL##', self.config.imaging_api['diskless_kernel'], 'global'),
            ('##PULSE2_D_MASTERS##', self.config.imaging_api['masters_folder'], 'global'),
            ('##PULSE2_D_POSTINST##', self.config.imaging_api['postinst_folder'], 'global'),
            ('##PULSE2_D_COMPUTERS##', self.config.imaging_api['computers_folder'], 'global'),
            ('##PULSE2_D_BASE##', self.config.imaging_api['base_folder'], 'global'),
            ('##PULSE2_F_INITRD#', self.config.imaging_api['diskless_initrd'], 'global'),
            ('##PULSE2_F_MEMTEST##', self.config.imaging_api['diskless_memtest'], 'global')]
        if self.mac:
            self.replacements.append(
                ('##MAC##',
                 pulse2.utils.reduceMACAddress(self.mac),
                 'global'))

    def _applyReplacement(self, string, condition = 'global'):
        """
        Private func, to apply a replacement into a given string

        Some examples :
        ##MAC:fmt## replaced by the client MAC address; ATM fmt can be:
          - short (pure MAC addr)
          - cisco (cisco-fmt MAC addr)
          - linux (linux-fmt MAC addr)
          - win (win-fmt MAC addr)
        """
        output = string
        for replacement in self.replacements:
            f, t, w = replacement
            if w == condition:
                output = re.sub(f, t, output)
        return output

    def buildMenu(self):
        """
        @return: the GRUB boot menu as a string encoded using CP-437
        @rtype: str
        """
        # takes global items, one by one
        buf = '# Auto-generated by Pulse 2 Imaging Server on %s \n\n' % time.asctime()

        if self.timeout:
            buf += 'timeout %s\n' % self.timeout
        buf += 'default %s\n' % self.default_item
        if self.splashscreen:
            buf += self._applyReplacement('splashscreen %s\n' % self.splashscreen)
        buf += 'color %d/%d %d/%d\n' % (
            self.colors['normal']['fg'],
            self.colors['normal']['bg'],
            self.colors['highlight']['fg'],
            self.colors['highlight']['bg'])
        if self.keyboard == 'fr':
            buf += 'keybfr\n'

        if self.hidden:
            buf += 'hide\n'

        # then write items
        indices = self.menuitems.keys()
        indices.sort()
        for i in indices:
            output = self._applyReplacement(self.menuitems[i].getEntry(self.protocol))
            buf += '\n'
            buf += output

        assert(type(buf) == unicode)
        # Encode menu using code page 437 (MS-DOS) encoding
        buf = buf.encode('cp437')
        return buf

    def write(self):
        """
        Write the boot menu to disk
        """
        if self.mac:
            filename = os.path.join(self.config.imaging_api['base_folder'], self.config.imaging_api['bootmenus_folder'], pulse2.utils.reduceMACAddress(self.mac))
            self.logger.debug('Preparing to write boot menu for computer MAC %s into file %s' % (self.mac, filename))
        else:
            filename = os.path.join(self.config.imaging_api['base_folder'], self.config.imaging_api['bootmenus_folder'], self.DEFAULT_MENU_FILE)
            self.logger.debug('Preparing to write the default boot menu for unregistered computers into file %s' % filename)
        buf = self.buildMenu()

        backupname = "%s.backup" % filename
        if os.path.exists(filename):
            try:
                os.rename(filename, backupname)
            except Exception, e: # can make a backup : give up !
                logging.getLogger().error("While backuping boot menu %s as %s : %s" % (filename, backupname, e))
                return False

        try:
            fid = open(filename, 'w+b')
            fid.write(buf)
            fid.close()
            for item in self.menuitems.values():
                item.write(self.config)
            if self.mac:
                self.logger.debug('Successfully wrote boot menu for computer MAC %s into file %s' % (self.mac, filename))
            else:
                self.logger.debug('Successfully wrote boot menu for unregistered computers into file %s' % filename)
        except Exception, e:
            if self.mac:
                logging.getLogger().error("While writing boot menu for %s : %s" % (self.mac, e))
            else:
                logging.getLogger().error("While writing default boot menu : %s" % e)
            return False

        if os.path.exists(backupname):
            try:
                os.unlink(backupname)
            except Exception, e:
                logging.getLogger().warn("While removing backup %s of %s : %s" % (backupname, filename, e))
        return True

    def setTimeout(self, value):
        """
            set the default timeout
        """
        self.timeout = value

    def setDefaultItem(self, value):
        """
            set the default item number
        """
        assert(type(value) == int)
        self.default_item = value

    def addImageEntry(self, position, entry):
        """
        Add the ImagingEntry entry to our menu
        """
        assert(type(position) == int and position > 0)
        if position in self.menuitems:
            raise ValueError('Position %d in menu already taken' % position)
        item = ImagingImageItem(entry)
        self.menuitems[position] = item

    def addBootServiceEntry(self, position, entry):
        """
        Add the ImagingEntry entry to our menu
        """
        assert(type(position) == int and position > 0)
        if position in self.menuitems:
            raise ValueError('Position %d in menu already taken' % position)
        self.menuitems[position] = ImagingBootServiceItem(entry)

    def setKeyboard(self, mapping = None):
        """
        set keyboard map
        if mapping is none, do not set keymap
        """
        if mapping in ['fr']:
            self.keyboard = mapping

    def hideMenu(self):
        """
        Hide the menu
        """
        self.hidden = True

    def showMenu(self):
        """
        Show the menu
        """
        self.hidden = False

    def setProtocol(self, value):
        assert(value in ['nfs', 'tftp', 'mtftp'])
        self.protocol = value

    def setSplashScreen(self, value):
        if type(value == str):
            value = value.decode('utf-8')
        assert(type(value) == unicode)
        self.splashscreen = value

    def setMessage(self, value):
        if type(value == str):
            value = value.decode('utf-8')
        assert(type(value) == unicode)
        self.message = value


class ImagingItem:

    """
    Common class to hold an imaging menu item
    """

    def __init__(self, entry):
        """
        @param entry: menu item in dict format
        @type entry: dict
        """
        self.logger = logging.getLogger()
        self._convertEntry(entry)
        self.title = entry['name'] # the item title
        self.desc = entry['desc'] # the item desc
        assert(type(self.title) == unicode)
        assert(type(self.desc) == unicode)
        self.uuid = None

    def _applyReplacement(self, out, network = True):
        if network:
            device = '(nd)'
        else:
            # FIXME: Is it the right device name ?
            device = '(cdrom)'
        out = re.sub('##PULSE2_NETDEVICE##', device, out)
        if self.uuid:
            out = re.sub('##PULSE2_F_IMAGE##', self.uuid, out)
        return out

    def _convertEntry(self, array):
        """
        Convert dictionary value of type str to unicode.
        """
        for key, value in array.items():
            if type(value) == str:
                value = value.decode('utf-8')
            array[key] = value

    def write(self, config):
        """
        Actions to do for this item
        """
        pass


class ImagingBootServiceItem(ImagingItem):

    """
    hold an imaging menu item for a boot service
    """

    def __init__(self, entry):
        ImagingItem.__init__(self, entry)
        self.value = entry['value'] # the GRUB command line
        assert(type(self.value) == unicode)

    def getEntry(self, protocol, network = True):
        """
        Return the entry, in a GRUB compatible format
        """
        buf = 'title %s\n' % self.title
        if self.desc:
            buf += 'desc %s\n' % self.desc
        if self.value:
            buf += self.value + '\n'
        return self._applyReplacement(buf, network)


class ImagingImageItem(ImagingItem):

    """
    Hold an imaging menu item for a image to restore
    """

    NFSRESTORE = u"kernel ##PULSE2_NETDEVICE##/##PULSE2_F_DISKLESS##/##PULSE2_K_DISKLESS## revosavedir=/##PULSE2_F_MASTERS##/##PULSE2_F_IMAGE## revobase=##PULSE2_F_BASE## revorestorenfs quiet revopost revomac=##MAC## \ninitrd ##PULSE2_NETDEVICE##/##PULSE2_F_DISKLESS##/##PULSE2_I_DISKLESS##\n"
    # FIXME ! TFTP/MTFTP to be implemented
    TFTPRESTORE = NFSRESTORE
    MTFTPRESTORE = NFSRESTORE

    POSTINST = 'initinst'

    def __init__(self, entry):
        """
        Initialize this object.
        """
        ImagingItem.__init__(self, entry)
        self.uuid = entry['uuid']
        assert(type(self.uuid) == unicode)
        if 'post_install_script' in entry:
            self.post_install_script = entry['post_install_script']['value']
        else:
            self.post_install_script = None

    def getEntry(self, protocol, network = True):
        """
        @param network: if True, build a menu for a network restoration , else
                        build a menu for a CD-ROM restoration

        @return: the entry, in a GRUB compatible format.
        """
        assert(protocol in ['nfs', 'tftp', 'mtftp'])
        buf = 'title %s\n' % self.title
        if self.desc:
            buf += 'desc %s\n' % self.desc
        if protocol == 'tftp':
            buf += self.TFTPRESTORE
        elif protocol == 'mtftp':
            buf += self.MTFTPRESTORE
        else:
            buf += self.NFSRESTORE
        return self._applyReplacement(buf, network)

    def write(self, config):
        """
        Write post-installation script if any.
        """
        initinst = os.path.join(config.imaging_api['base_folder'], config.imaging_api['masters_folder'], self.uuid, self.POSTINST)
        if self.post_install_script:
            try:
                f = file(initinst, 'w+')
                f.write(self.post_install_script)
                f.close()
            except OSError, e:
                self.logger.error("Can't update post-installation script %s: %s" % (initinst, e))
                raise
        else:
            if os.path.exists(initinst):
                self.logger.debug('Deleting previous post-installation script: %s' % initinst)
                try:
                    os.unlink(initinst)
                except OSError, e:
                    self.logger.error("Can't delete post-installation script %s: %s" % (initinst, e))
                    raise
