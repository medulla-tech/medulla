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

import re
import os
import logging
import time
import shutil
import stat

import pulse2.utils
import pulse2.package_server.imaging.api.functions
from pulse2.package_server.config import P2PServerCP as PackageServerConfig


def isMenuStructure(menu):
    """
    @return: True if the given object is a menu structure
    @rtype: bool
    """
    ret = True
    logger = logging.getLogger('imaging')
    if type(menu) == dict:
        for k in ['message',
                  'default_item',
                  'default_item_WOL',
                  'timeout',
                  'background_uri',
                  'bootservices',
                  'images',
                  'bootcli',
                  'disklesscli',
                  'hidden_menu',
                  'dont_check_disk_size',
                  'ethercard']:

            if not k in menu:
                logger.error("Menu is missing %s" % (k))
                ret = False
                break
    else:
        logger.error("Menu is not a dict")
        ret = False
    return ret


class ImagingDefaultMenuBuilder:

    """
    Class that builds an imaging menu according to its dict structure.
    """

    def __init__(self, config, menu):
        """
        The object builder

        @param config : the imaging server config
        @param menu : the menu dict

        @return the object
        """
        self.logger = logging.getLogger('imaging')
        if not isMenuStructure(menu):
            raise TypeError('Bad menu structure')
        self.menu = menu
        self.config = config
        if 'target' in self.menu:
            self.cacheHostname(self.menu['target']['uuid'],self.menu['target']['name'])

    def cacheHostname(self, uuid, name):
        if uuid:
            target_folder = os.path.join(PackageServerConfig().imaging_api['base_folder'], PackageServerConfig().imaging_api['computers_folder'],uuid)
            if os.path.isdir(target_folder):
                self.logger.debug('Imaging menu : folder %s for client %s : It already exists !' % (target_folder, uuid))
                return True
            if os.path.exists(target_folder):
                self.logger.warn('Imaging menu : folder %s for client %s : It already exists, but is not a folder !' % (target_folder, uuid))
                return False
            try:
                os.mkdir(target_folder)
                self.logger.debug('Imaging menu : folder %s for client %s was created' % (target_folder,uuid))
            except Exception, e:
                self.logger.error('Imaging menu : I was not able to create folder %s for client %s : %s' % (target_folder, uuid, e))
                return False
            if name:
                target_folder = os.path.join(target_folder,'hostname')
                fichier = open(target_folder, "w")
                fichier.write(name)
                fichier.close()
        return True

    def make(self, macaddress = None):
        """
        @return: an ImagingMenu object
        @rtype: ImagingMenu
        """
        if 'target' in self.menu:
            m = ImagingMenu(self.config, macaddress,self.menu['target']['name'],self.menu['target']['uuid'])
        else:
            m = ImagingMenu(self.config, macaddress)
        m.setSplashImage(self.menu['background_uri'])
        m.setMessage(self.menu['message'])
        m.setTimeout(self.menu['timeout'])
        m.setDefaultItem(self.menu['default_item'])
        self.logger.debug('bootcli: %s' % self.menu['bootcli'])
        m.setBootCLI(self.menu['bootcli'])
        m.hide(self.menu['hidden_menu'])
        if 'update_nt_boot' in self.menu:
            m.setNTBLFix(self.menu['update_nt_boot'])
        self.logger.debug('disklesscli: %s' % self.menu['disklesscli'])
        m.setDisklessCLI(self.menu['disklesscli'])
        self.logger.debug('dont_check_disk_size: %s' % self.menu['dont_check_disk_size'])
        m.setDiskSizeCheck(self.menu['dont_check_disk_size'])
        self.logger.debug('ethercard: %s' % self.menu['ethercard'])
        m.setEtherCard(int(self.menu['ethercard']))
        if 'language' in self.menu:
            m.setLanguage(int(self.menu['language']))
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
        computerMenu = ImagingDefaultMenuBuilder.make(self, self.macaddress)
        if 'raw_mode' in self.menu['target']:
            computerMenu.setRawMode(self.menu['target']['raw_mode'])
        return computerMenu


class ImagingMenu:

    """
    hold an imaging menu
    """

    DEFAULT_MENU_FILE = 'default'
    LANG_CODE = {
        1 : 'C',
        2 : 'fr_FR',
        3 : 'pt_BR',
        4 : 'de_DE',
                }
    KEYB_CODE = {
        1 : None,
        2 : 'fr',
        3 : 'pt',
        4 : 'de',
    }

    def __init__(self, config, macaddress = None, hostname = None,uuid = None):
        """
        Initialize this object.

        @param config: a ImagingConfig object
        @param macaddress: the client MAC Address
        """
        self.logger = logging.getLogger('imaging')
        self.config = config  # the server configuration
        if macaddress:
            assert pulse2.utils.isMACAddress(macaddress)
        self.mac = macaddress  # the client MAC Address
        if hostname:
            self.hostname = hostname
        else:
            self.hostname = ""
        if uuid:
            self.uuid=uuid
        else:
            self.uuid=None
        # menu items
        self.menuitems = {}
        self.timeout = 0  # the menu timeout
        self.default_item = 0  # the menu default entry
        self.default_item_WOL = 0  # the menu default entry on WOL
        self.splashimage = None  # the menu splashimage
        self.message = None
        self.keyboard = None  # the menu keymap, None is C
        self.hidden = False  # do we hide the menu ?
        self.language = 'C'  # Menu language
        self.bootcli = False  # command line access at boot time ?
        self.disklesscli = False  # command line access at diskless time ?
        self.ntblfix = False  # NT Bootloader fix
        self.ethercard = 0  # use this ethernet iface to backup / restore stuff
        self.dont_check_disk_size = False  # check that the target disk is large enough

        self.diskless_opts = list()  # revo* options put on diskless command line

        # kernel options put on diskless command line
        # Check if Davos or revo
        if self.config.imaging_api['diskless_folder'] == "davos":
            self.kernel_opts = ['boot=live',
                'config',
                'noswap',
                'edd=on',
                'nomodeset',
                'nosplash',
                'noprompt',
                'vga=788',
                'fetch=tftp://%s/%s/fs.squashfs' % (PackageServerConfig().public_ip, self.config.imaging_api['diskless_folder'])]

            # If we have a mac, we put it in kernel params
            if macaddress is not None:
                self.kernel_opts.append('mac='+ macaddress)
        else:
            self.kernel_opts = list(['quiet'])  # kernel options put on diskless command line

        self.rawmode = ''  # raw mode backup

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
        # list of replacements to perform
        # a replacement is using the following structure :
        # key 'from' : the PCRE to look for
        # key 'to' : the replacement to perform
        # key 'when' : when to perform the replacement (only 'global' for now)
        replacements = [
            ('##PULSE2_LANG##', PackageServerConfig().pxe_keymap, 'global'),
            ('##PULSE2_PUBLIC_IP##', PackageServerConfig().public_ip, 'global'),
            ('##PULSE2_BOOTLOADER_DIR##', self.config.imaging_api['bootloader_folder'], 'global'),
            ('##PULSE2_TOOLS_DIR##', self.config.imaging_api['tools_folder'], 'global'),
            ('##PULSE2_BOOTSPLASH_FILE##', self.config.imaging_api['bootsplash_file'], 'global'),
            ('##PULSE2_DISKLESS_DIR##', self.config.imaging_api['diskless_folder'], 'global'),
            ('##PULSE2_DAVOS_OPTS##', self.config.imaging_api['davos_options'], 'global'),
            ('##PULSE2_DISKLESS_KERNEL##', self.config.imaging_api['diskless_kernel'], 'global'),
            ('##PULSE2_DISKLESS_INITRD##', self.config.imaging_api['diskless_initrd'], 'global'),
            ('##PULSE2_DISKLESS_OPTS##', ' '.join(self.diskless_opts), 'global'),
            ('##PULSE2_KERNEL_OPTS##', ' '.join(self.kernel_opts), 'global'),
            ('##PULSE2_MASTERS_DIR##', self.config.imaging_api['masters_folder'], 'global'),
            ('##PULSE2_POSTINST_DIR##', self.config.imaging_api['postinst_folder'], 'global'),
            ('##PULSE2_COMPUTERS_DIR##', self.config.imaging_api['computers_folder'], 'global'),
            ('##PULSE2_INVENTORIES_DIR##', self.config.imaging_api['inventories_folder'], 'global'),
            ('##PULSE2_PXE_MASK##', self.config.imaging_api['pxe_mask'], 'global'),
            ('##PULSE2_PXE_TFTP_IP##', self.config.imaging_api['pxe_tftp_ip'], 'global'),
            ('##PULSE2_PXE_SUBNET##', self.config.imaging_api['pxe_subnet'], 'global'),
            ('##PULSE2_PXE_GATEWAY##', self.config.imaging_api['pxe_gateway'], 'global'),
            ('##PULSE2_PXE_DEBUG##', self.config.imaging_api['pxe_debug'], 'global'),
            ('##PULSE2_PXE_TIME_REBOOT##', self.config.imaging_api['pxe_time'], 'global'),
            ('##PULSE2_PXE_XML##', self.config.imaging_api['pxe_xml'], 'global'),
            ('##PULSE2_BASE_DIR##', self.config.imaging_api['base_folder'], 'global'),
            ('##PULSE2_REVO_RAW##', self.rawmode, 'global')
            ]
        if self.mac:
            replacements.append(
                ('##MAC##',
                 pulse2.utils.reduceMACAddress(self.mac),
                 'global'))

        output = string
        for replacement in replacements:
            f, t, w = replacement
            if w == condition:
                output = re.sub(f, t, output)
        return output

    def _fill_reptable(self):
        """
         this function create array to remove accent who are not
         compatible with MS-DOS encoding
        """
        _reptable = {}
        _corresp = [
            (u"a",  [0x00E3]),
            ]
        for repchar,codes in _corresp :
            for code in codes :
                _reptable[code] = repchar

        return _reptable

    def delete_diacritics(self, s) :
        """
        Delete accent marks.

        @param s: string to clean
        @type s: unicode
        @return: cleaned string
        @rtype: unicode
        """
        _reptable = self._fill_reptable()
        if isinstance(s, str):
            s = unicode(s, "utf8", "replace")
        ret = []
        for c in s:
            ret.append(_reptable.get(ord(c) ,c))
        return u"".join(ret)

    def buildMenu(self):
        """
        @return: the SYSLINUX boot menu as a string encoded using CP-437
        @rtype: str
        """

        # takes global items, one by one
        buf = '# Auto-generated by Pulse 2 Imaging Server on %s \n\n' % time.asctime()
        buf += 'UI vesamenu.c32\n'
        buf += 'PROMPT 0\n'

        # the key mapping
        buf += 'KBDMAP %s.ktl\n' % PackageServerConfig().pxe_keymap

        # PXE Password entry if pxe_password is set
        if PackageServerConfig().pxe_password != '':
            buf += 'MENU MASTER PASSWD %s\n' % PackageServerConfig().pxe_password

        # the menu timeout : warning, 0 means "do not wait !"
        if self.timeout == '0':
            buf += 'TIMEOUT 1\n'
        else:
            buf += 'TIMEOUT %d\n' % (int(self.timeout) * 10)

        # the menu default item
        buf += 'DEFAULT %s\n' % self.default_item

        # the menu splash image
        if self.splashimage:
            buf += self._applyReplacement('MENU BACKGROUND %s\n' % self.splashimage)

        # the menu setup
        buf += 'MENU WIDTH 78\n'
        buf += 'MENU MARGIN 4\n'
        buf += 'MENU ROWS 10\n'
        buf += 'MENU VSHIFT 10\n'
        buf += 'MENU TIMEOUTROW 18\n'
        buf += 'MENU TABMSGROW 16\n'
        buf += 'MENU CMDLINEROW 16\n'
        buf += 'MENU HELPMSGROW 21\n'
        buf += 'MENU HELPMSGENDROW 29\n'
        buf += 'MENU TITLE %s\n' % self.hostname
        # do we hide the menu ? Splash screen will still be displayed
        if self.hidden:
            buf += 'MENU HIDDEN\n'

        # then write items
        indices = self.menuitems.keys()
        indices.sort()
        for i in indices:
            output = self._applyReplacement(self.menuitems[i].getEntry())
            buf += '\n'
            buf += output
            if PackageServerConfig().pxe_password != '' and not 'continue' in self.menuitems[i].getEntry():
                buf += 'MENU PASSWD\n'

        assert(type(buf) == unicode)

        # Clean brazilian characters who are not compatible
        # with MS-DOS encoding by delete accent marks
        buf = self.delete_diacritics(buf)

        # Encode menu using code page 437 (MS-DOS) encoding
        buf = buf.encode('cp437')
        return buf

    def write(self):
        """
        Write the boot menu to disk
        """
        if self.mac:
            filename = os.path.join(self.config.imaging_api['base_folder'], self.config.imaging_api['bootmenus_folder'], pulse2.utils.normalizeMACAddressForPXELINUX(self.mac))
            self.logger.debug('Preparing to write boot menu for computer MAC %s into file %s' % (self.mac, filename))
        else:
            filename = os.path.join(self.config.imaging_api['base_folder'], self.config.imaging_api['bootmenus_folder'], self.DEFAULT_MENU_FILE)
            self.logger.debug('Preparing to write the default boot menu for unregistered computers into file %s' % filename)


        def _write(self):
            try:
                buf = self.buildMenu()
            except Exception, e:
                logging.getLogger().error(str(e))

            backupname = "%s.backup" % filename
            if os.path.exists(filename):
                try:
                    os.rename(filename, backupname)
                except Exception, e:  # can make a backup : give up !
                    self.logger.error("While backuping boot menu %s as %s : %s" % (filename, backupname, e))
                    return False

            try:
                fid = open(filename, 'w+b')
                fid.write(buf)
                fid.close()
                for item in self.menuitems.values():
                    try:
                        item.write(self.config)
                    except Exception, e:
                        self.logger.error('An error occurred while writing boot menu entry "%s": %s' % (str(item), str(e)))
                if self.mac:
                    self.logger.debug('Successfully wrote boot menu for computer MAC %s into file %s' % (self.mac, filename))
                else:
                    self.logger.debug('Successfully wrote boot menu for unregistered computers into file %s' % filename)
            except Exception, e:
                if self.mac:
                    self.logger.error("While writing boot menu for %s : %s" % (self.mac, e))
                else:
                    self.logger.error("While writing default boot menu : %s" % e)
                return False

            if os.path.exists(backupname):
                try:
                    os.unlink(backupname)
                except Exception, e:
                    self.logger.warn("While removing backup %s of %s : %s" % (backupname, filename, e))
        # Retreive PXE Params
        pulse2.package_server.imaging.api.functions.Imaging().refreshPXEParams(_write, self)

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
        self.default_item = value.replace(" ","-")

    def addImageEntry(self, position, entry):
        """
        Add the ImagingEntry entry to our menu
        """
        assert(type(position) == int and position >= 0)
        if position in self.menuitems:
            raise ValueError('Position %d in menu already taken' % position)
        item = ImagingImageItem(entry)
        self.menuitems[position] = item

    def addBootServiceEntry(self, position, entry):
        """
        Add the ImagingEntry entry to our menu
        """
        assert(type(position) == int and position >= 0)
        if position in self.menuitems:
            raise ValueError('Position %d in menu already taken' % position)
        self.menuitems[position] = ImagingBootServiceItem(entry)

    def setKeyboard(self, mapping = None):
        """
        set keyboard map
        if mapping is none, do not set keymap
        """
        if mapping in ['fr', 'pt', 'de']:
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

    def setBootCLI(self, value):
        """
        set CLI access on boot (key "E")
        """
        value = bool(value)
        self.bootcli = value

    def setNTBLFix(self, value):
        """
        set NT Boot Loader fix
        """
        value = bool(value)
        self.ntblfix = value

    def setDisklessCLI(self, value):
        """
        do not drop to a shell when mastering
        """
        value = bool(value)
        self.disklesscli = value

    def setDiskSizeCheck(self, value):
        """
        do check disk size when restoring
        """
        value = bool(value)
        self.dont_check_disk_size = value

    def setEtherCard(self, value):
        """
        Set the ethernet restoration interface
        @param value : the iface number, between 0 (default) and 9
        """
        assert(type(value) == int)
        assert(value >= 0)
        assert(value <= 9)
        self.ethercard = value

    def setSplashImage(self, value):
        """
        Set the background image
        """
        if type(value) == str:
            value = value.decode('utf-8')
        assert(type(value) == unicode)
        self.splashimage = value

    def setMessage(self, value):
        """
        Set the warn message
        """
        if type(value) == str:
            value = value.decode('utf-8')
        assert(type(value) == unicode)
        self.message = value

    def setLanguage(self, value):
        """
        Set menu language, and keyboard map to use
        """
        try:
            self.language = self.LANG_CODE[value]
            if not self.keyboard:
                self.keyboard = self.KEYB_CODE[value]
        except KeyError:
            self.language = self.LANG_CODE[1]
            self.keyboard = self.KEYB_CODE[1]

    def setRawMode(self, value):
        """
        Set raw backup mode
        """
        value = bool(value)
        if value:
            self.rawmode = 'revoraw'

    def hide(self, flag):
        """
        Hide or display menu
        """
        flag = bool(flag)
        self.hidden = flag


class CleanMenu:
    def __init__(self, config, macaddress = None):
        """
        @param config: a ImagingConfig object
        @type config: object
        @param macaddress: the client MAC Address
        @type macaddress: obj
        """
        self.config = config  # the server configuration
        uuid =     macaddress['uuid']
        self.mac = set(macaddress['mac'][uuid])  # the client MAC Address


    def clear(self):
        for i in self.mac:
            if i == "": continue
            filename = os.path.join(self.config.imaging_api['base_folder'], self.config.imaging_api['bootmenus_folder'], pulse2.utils.normalizeMACAddressForPXELINUX(i))
            try:
                os.unlink(filename)
            except Exception, e:
                pass
            # clear hostnamebymac
            target_file = os.path.join(self.config.imaging_api['base_folder'],self.config.imaging_api['computers_folder'], "hostnamebymac",pulse2.utils.normalizeMACAddressForPXELINUX(i))
            try:
                os.unlink(target_file)
            except Exception, e:
                pass
        return True


class ImagingItem:

    """
    Common class to hold an imaging menu item
    """

    def __init__(self, entry):
        """
        @param entry: menu item in dict format
        @type entry: dict
        """
        self.logger = logging.getLogger('imaging')
        self._convertEntry(entry)
        self.label = entry['name'].replace(" ","-")  # the item label
        self.menulabel = entry['desc']  # the item menulabel
        assert(type(self.label) == unicode)
        assert(type(self.menulabel) == unicode)
        self.uuid = None

    def __str__(self):
        d = self.__dict__
        return str(d)

    def _applyReplacement(self, out, network = True):
        if network:
            device = '(nd)'
        else:
            # FIXME: Is it the right device name ?
            device = '(cdrom)'
        out = re.sub('##PULSE2_NETDEVICE##', device, out)
        if self.uuid:
            out = re.sub('##PULSE2_IMAGE_UUID##', self.uuid, out)
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

    def getLogger(self):
        """
        return internal logger
        """
        return self.logger


class ImagingBootServiceItem(ImagingItem):

    """
    hold an imaging menu item for a boot service
    """

    def __init__(self, entry):
        """
        @param entry : a ImagingItem
        """
        ImagingItem.__init__(self, entry)
        self.value = entry['value']  # the PXELINUX command line
        assert(type(self.value) == unicode)

    def getEntry(self, network = True):
        """
        Return the entry, in a SYSLINUX compatible format
        """
        buf = 'LABEL %s\n' % self.label
        if self.menulabel:
            buf += 'MENU LABEL %s\n' % self.menulabel
        if self.value:
            buf += self.value + '\n'
        return self._applyReplacement(buf, network)

    def writeShFile(self, script_file):
        """
        Create a sh file who contains commands of PostInstallScript
        """
        config = PackageServerConfig()
        postinst_scripts_folder = os.path.join(config.imaging_api['base_folder'],
                                config.imaging_api['postinst_folder'],
                                'scripts')
        if not os.path.exists(postinst_scripts_folder):
            self.logger.info("Postinst scripts directory %s doesn't exists, create it", postinst_scripts_folder)
            os.mkdir(postinst_scripts_folder)

        # Create and write sh file
        try:
            f = open(os.path.join(postinst_scripts_folder, script_file[0]), 'w')
            f.write('#!/bin/bash\n')
            f.write('\n')
            f.write('. /usr/lib/libpostinst.sh')
            f.write('\n')
            f.write('set -v\n')
            f.write('\n')
            f.write(script_file[1])
            f.close()
            self.logger.info('File %s successfully created', os.path.join(postinst_scripts_folder, script_file[0]))
        except Exception, e:
            self.logger.exception('Error while create sh file: %s', e)

        return True

    def unlinkShFile(self, bs_uuid):
        """
        Delete sh file created by post-install script
        """
        script_file = bs_uuid[0] + ".sh"

        config = PackageServerConfig()
        postinst_scripts_folder = os.path.join(config.imaging_api['base_folder'],
                                config.imaging_api['postinst_folder'],
                                'scripts')
        if not os.path.exists(postinst_scripts_folder):
            self.logger.exception("Error while delete sh file: Post-install script folder %s doesn't exists", postinst_scripts_folder)
            raise Exception ("Post-install script folder %s doesn't exists", postinst_scripts_folder)

        try:
            os.unlink(os.path.join(postinst_scripts_folder, script_file))
        except Exception, e:
            self.logger.exception("Error while delete sh file: %s", e)


class ImagingImageItem(ImagingItem):

    """
    Hold an imaging menu item for a image to restore
    """

    # Important: This is a cmdline for a restore process
    # For "Create an image" it's a bootservice and its command line is in the DB
    # TODO: for clonezilla backend it will be useful to clean some of unused params

    # Grub cmdlines
    CMDLINE = u"kernel ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL## ##PULSE2_KERNEL_OPTS## ##PULSE2_DISKLESS_OPTS## revosavedir=##PULSE2_MASTERS_DIR## revoinfodir=##PULSE2_COMPUTERS_DIR## revooptdir=##PULSE2_POSTINST_DIR## revobase=##PULSE2_BASE_DIR## revopost revomac=##MAC## revoimage=##PULSE2_IMAGE_UUID## \ninitrd ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##\n"

    POSTINST = '%02d_postinst'
    POSTINSTDIR = 'postinst.d'

    def __init__(self, entry):
        """
        Initialize this object.
        """
        ImagingItem.__init__(self, entry)
        self.uuid = entry['uuid']
        assert(type(self.uuid) == unicode)
        if 'post_install_script' in entry:
            assert(type(entry['post_install_script']) == list)
            self.post_install_script = entry['post_install_script']
        else:
            self.post_install_script = None

        # Davos imaging client case
        if PackageServerConfig().imaging_api['diskless_folder'] == "davos":
            self.CMDLINE = u"kernel ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL## ##PULSE2_KERNEL_OPTS## ##PULSE2_DISKLESS_OPTS## image_uuid=##PULSE2_IMAGE_UUID## davos_action=RESTORE_IMAGE ##PULSE2_DAVOS_OPTS##\ninitrd ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##\n"
            self.CMDLINE = u"kernel ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL## ##PULSE2_KERNEL_OPTS## ##PULSE2_DISKLESS_OPTS## image_uuid=##PULSE2_IMAGE_UUID## davos_action=RESTORE_IMAGE ##PULSE2_DAVOS_OPTS##\ninitrd ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##\n"


    def getEntry(self, network = True):
        """
        @param network: if True, build a menu for a network restoration , else
                        build a menu for a CD-ROM restoration

        @return: the entry, in a SYSLINUX compatible format.
        """
        buf = 'LABEL %s\n' % self.label
        buf += 'MENU LABEL %s\n' % self.label
        buf += self.CMDLINE + '\n'
        return self._applyReplacement(buf, network)

    def write(self, config):
        """
        Write post-imaging scripts if any.
        """
        # First: remove old post-imaging directory if there is one
        postinstdir = os.path.join(config.imaging_api['base_folder'], config.imaging_api['masters_folder'], self.uuid, self.POSTINSTDIR)
        if os.path.exists(postinstdir):
            self.logger.debug('Deleting previous post-imaging directory: %s' % postinstdir)
            try:
                shutil.rmtree(postinstdir)
            except OSError, e:
                self.logger.error("Can't delete post-imaging directory %s: %s" % (postinstdir, e))
                raise
        # Then populate the post-imaging script directory if needed
        if self.post_install_script:
            try:
                os.mkdir(postinstdir)
                self.logger.debug('Directory successfully created: %s' % postinstdir)
            except OSError, e:
                self.logger.error("Can't create post-imaging script folder %s: %s" % (postinstdir, e))
                raise

            order = 1  # keep 0 for later use
            for script in self.post_install_script:
                postinst = os.path.join(postinstdir, self.POSTINST % order)
                try:
                    # write header
                    f = file(postinst, 'w+')
                    f.write('#!/bin/bash\n')
                    f.write('\n')
                    f.write('. /usr/lib/libpostinst.sh')
                    f.write('\n')
                    f.write('echo "==> postinstall script #%d : %s"\n' % (order, script['name'].encode('utf-8')))
                    f.write('set -v\n')
                    f.write('\n')
                    f.write(script['value'].encode('utf-8'))
                    f.close()
                    os.chmod(postinst, stat.S_IRUSR | stat.S_IXUSR)
                    self.logger.debug('Successfully wrote script: %s' % postinst)
                except OSError, e:
                    self.logger.error("Can't update post-imaging script %s: %s" % (postinst, e))
                    raise
                except Exception, e:
                    self.logger.error("Something wrong happened while writing post-imaging script %s: %s" % (postinst, e))
                order += 1
        else:
            self.logger.debug('No post-imaging script to write')


def changeDefaultMenuItem(macaddress, value):
    """
    Change the default menu item of a computer.

    This method directly changes the content of the boot menu file of a
    computer. It should be used only when the MMC-agent can't be reached.

    @param macaddress: computer MAC address
    @type macaddress: str

    @param value: defaut item value
    @type value: int

    @return: True if success, else False
    @rtype: bool
    """
    config = PackageServerConfig()
    logger = logging.getLogger('imaging')
    filename = os.path.join(config.imaging_api['base_folder'],
                            config.imaging_api['bootmenus_folder'],
                            pulse2.utils.normalizeMACAddressForPXELINUX(macaddress))
    logger.debug('Changing default boot menu item of computer MAC %s'
                 % macaddress)
    newlines = ''
    try:
        for line in file(filename):
            if line.startswith('default '):
                if line == 'default %d\n' % value:
                    logger.debug('Default item is already set to %d, nothing to do.' % value)
                    return True
                # Change default menu item
                newlines += 'default %d\n' % value
            else:
                newlines += line
    except OSError, e:
        logger.error('Error while reading computer bootmenu file %s: %s' %
                          (filename, str(e)))
        logger.error('This computer default menu item can\'t be changed')
        newlines = ''
    if newlines:
        backupname = "%s.backup" % filename
        try:
            os.rename(filename, backupname)
        except OSError, e:  # can make a backup : give up !
            logger.error("While backuping boot menu %s as %s : %s"
                         % (filename, backupname, e))
            return False
        # Write new boot menu
        try:
            fid = file(filename, 'w+b')
            fid.write(newlines)
            fid.close()
            logger.debug('Successfully wrote boot menu for computer MAC %s into file %s' % (macaddress, filename))
        except IOError, e:
            logger.error("While writing boot menu for %s : %s"
                         % (macaddress, e))
            return False
        # Remove boot menu backup
        try:
            os.unlink(backupname)
        except OSError, e:
            logger.warn("While removing backup %s of %s : %s"
                        % (backupname, filename, e))
        return True
    return False



class ImagingMulticastMenuBuilder:
    """
    Class that builds an imaging menu according to its dict structure.
    """

    def __init__(self,  menu):
        """
        The object builder Menu multicast
        @param config : the imaging server config
        @param menu : the menu dict

        @return the object
        """

        self.pathBootMenu = os.path.join(PackageServerConfig().imaging_api['base_folder'],
                            PackageServerConfig().imaging_api['bootmenus_folder'])
        self.logger = logging.getLogger('imaging')
        self.logger.debug('creation commande et menu [%s] '%(menu))
        self.menu = menu
        self.public_ip = PackageServerConfig().public_ip
        self.server_address = self.ipV4toDecimal(self.public_ip)
        self.public_mask = PackageServerConfig().public_mask
        self.mask_server = self.ipV4toDecimal(self.public_mask)
        self.networkserver = self.server_address & self.mask_server
        self.ipPart=self.public_ip.split(".")
        #self.listnameinterface=os.listdir("/sys/class/net/")
        #for interface in self.listnameinterface:
            #if pulse2.utils.get_ip_address(interface)==self.public_ip:
                #self.nameinterface=interface
                #break
        #self.logger.info('interface [%s] ip [%s]'%(self.nameinterface,self.public_ip))
        self.action = "startdisk"
        diskfile = os.path.join(self.menu['path'], "disk")
        #load disk restore
        fid = file(diskfile, 'r')
        lines = fid.readlines()
        fid.close()
        self.disk=[ x.strip(' \t\n\r"') for x in lines if x.strip(' \t\n\r"')!= ""]

        if 'maxwaittime' in self.menu:
            self.templatecmdline = """#!/bin/bash
echo -e "DO NOT DELETE" > /tmp/processmulticast
echo "" > /tmp/udp-sender.log
mastername="%s"
localisationmaster="%s"
masteruuid=%s
mastersize=%s
groupuuid=%s
waitting=%s
locationuuid=%s
maxtimetowait=%s
drbl-ocs -sc0 -b -g auto -e1 auto -e2 -x -j2 --clients-to-wait %s  --max-time-to-wait %s -l en_US.UTF-8 -h "127.0.0.1" %s multicast_restore %s %s &>> /tmp/%s.log"""%(
                                        self.menu['description'] ,
                                        self.menu['path'] ,
                                        self.menu['master'] ,
                                        self.menu['size'] ,
                                        self.menu['group'] ,
                                        self.menu['nbcomputer'],
                                        self.menu['location'],
                                        self.menu['maxwaittime'],
                                        self.menu['nbcomputer'],
                                        self.menu['maxwaittime'],
                                        self.action,
                                        self.menu['master'] ,
                                        self.disk[0],
                                        self.menu['master'])
        else:
            self.templatecmdline = """#!/bin/bash
echo -e "NE PAS EFFACER\nDO NOT DELETE" > /tmp/processmulticast
echo "" > /tmp/udp-sender.log
mastername="%s"
localisationmaster="%s"
masteruuid=%s
mastersize=%s
groupuuid=%s
waitting=%s
locationuuid=%s
drbl-ocs -sc0 -b -g auto -e1 auto -e2 -x -j2 --clients-to-wait %s -l en_US.UTF-8 -h "127.0.0.1" %s multicast_restore %s %s &>> /tmp/%s.log"""%(
                                        self.menu['description'] ,
                                        self.menu['path'] ,
                                        self.menu['master'] ,
                                        self.menu['size'] ,
                                        self.menu['group'] ,
                                        self.menu['nbcomputer'],
                                        self.menu['location'],
                                        self.menu['nbcomputer'],
                                        self.action,
                                        self.menu['master'] ,
                                        self.disk[0],
                                        self.menu['master'])
        self.template="""
UI vesamenu.c32
TIMEOUT 100
MENU BACKGROUND bootsplash.png
MENU WIDTH 78
MENU MARGIN 4
MENU ROWS 10
MENU VSHIFT 10
MENU TIMEOUTROW 18
MENU TABMSGROW 16
MENU CMDLINEROW 16
MENU HELPMSGROW 21
MENU HELPMSGENDROW 29

LABEL multicast
MENU LABEL Restore Multicast %s
KERNEL ../davos/vmlinuz
APPEND boot=live config noswap edd=on nomodeset nosplash noprompt vga=788 fetch=tftp://%s/davos/fs.squashfs mac=%s revorestorenfs image_uuid=%s davos_action=RESTORE_IMAGE_MULTICAST
INITRD ../davos/initrd.img
"""

    def ipV4toDecimal(self, ipv4):
        d = ipv4.split('.')
        return (int(d[0])*256*256*256) + (int(d[1])*256*256) + (int(d[2])*256) +int(d[3])

    def isValidIPv4Address(self, adressmachine):
        self.logger.info("controle of the machine address %s in network %s"%(adressmachine,self.networkserver))
        adressmachine = adressmachine.split(":")[0]
        reseaumachine = self.ipV4toDecimal(adressmachine) &  self.mask_server
        if self.networkserver == reseaumachine :
            self.logger.info("machine address %s in network %s"%(adressmachine,self.networkserver))
            return True
        else :
            self.logger.error("machine %s in not in network %s. Please check your public_mask setting."%(adressmachine,self.networkserver))
        return False

    def chooseMacAddress(self):
        rest = True
        for k, v in self.menu['computer'].iteritems():
            if self.isValidIPv4Address(v):
                mac = pulse2.utils.reduceMACAddress(k)
                filename = pulse2.utils.normalizeMACAddressForPXELINUX(mac)
                self.logger.debug("create bootMenu [%s] Computer ip [%s]"%(k,v))
                menuval= self.template%( self.menu['description'],
                                self.public_ip,
                                k, #mac
                                self.menu['master']
                                )
                self.logger.debug("bootMenu [%s]\n%s"%(mac, menuval))
                if self.writeMenuMulticast( filename, menuval) == False:
                    rest = False
            else:
                self.logger.debug("mac [%s] ip [%s] non selected"%(k,v))
        return rest

    def writeMenuMulticast(self,filename,content):
        backupname = os.path.join(self.pathBootMenu,"%s.backup" % filename)
        fichier = os.path.join(self.pathBootMenu,filename)
        try:
            os.rename(fichier, backupname)
        except OSError, e:  # can make a backup : give up !
            self.logger.error("While backuping boot menu %s as %s : %s"
                         % (fichier, backupname, e))

        # Write new boot menu
        try:
            fid = file(fichier, 'w+b')
            fid.write(content)
            fid.close()
            self.logger.debug('Successfully wrote boot menu for computer MAC %s into file %s' % (filename, fichier))
        except IOError, e:
            self.logger.error("While writing boot menu for %s : %s"
                         % (filename, e))
            return False
        # Remove boot menu backup
        try:
            os.unlink(backupname)
        except OSError, e:
            self.logger.warn("While removing backup %s of %s : %s"
                        % (backupname, filename, e))
        return True

    def make(self):
        """
        """
        ##generation bootmenu for multicast
        if not self.chooseMacAddress():
            return False
        ##generation command line in tmp
        fichier = os.path.join("/tmp","multicast.sh")
        try:
            fid = file(fichier, 'w+b')
            fid.write(self.templatecmdline)
            fid.close()
            os.chmod(fichier, stat.S_IXUSR| stat.S_IWUSR |stat.S_IRUSR)
            self.logger.debug('Successfully wrote multicast command into file %s' % ( fichier))
            return True
        except IOError, e:
            self.logger.error("While writing commande for multicast command"
                         % (fichier, e))
            return False
        return True
