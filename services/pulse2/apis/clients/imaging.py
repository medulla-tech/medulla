# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from pulse2.apis.clients import Pulse2Api

# need to get a ImagingApiManager, it will manage a Imaging api for each mirror
# defined in the conf file.
class Imaging(Pulse2Api):
    def __init__(self, *attr):
        self.name = "Imaging"
        Pulse2Api.__init__(self, *attr)

    
    # Computer registration
    def computerRegister(self, computerName, MACAddress):
        """
        Called by pulse2-imaging-server to tell the Package Server to register a new computer.
        The computer name may contain a profile and an entity path (self, like profile:/entityA/entityB/computer)
        """
        d = self.callRemote("computerRegister", computerName, MACAddress)
        d.addErrback(self.onErrorRaise, "Imaging:computerRegister", [computerName, MACAddress])
        return d
    def computerPrepareImagingDirectory(self, uuid, imagingData = None):
        """
        Asks the Package Server to create the file system structure for the given computer uuid thanks to imagingData content. 
        If imagingData is None, the package server queries the MMC agent for the imaging data.
        """
        d = self.callRemote("computerPrepareImagingDirectory", uuid, imagingData)
        d.addErrback(self.onErrorRaise, "Imaging:computerPrepareImagingDirectory", [uuid, imagingData])
        return d
    def computerUnregister(self, uuid, archive = True):
        """
        Remove computer data from the Imaging Server.
        The computer must be registered again to use imaging. 
        If archive is True, the computer imaging data are stored in an archive directory, else it is wiped out.
        """
        d = self.callRemote("computerUnregister", uuid, archive)
        d.addErrback(self.onErrorRaise, "Imaging:computerUnregister", [uuid, archive])
        return d
    # Computer Menu management
    def computerMenuGet(self, uuid): # imagingMenu
        """
        Returns the boot menu of a computer.
        Called by the MMC agent.
        """
        d = self.callRemote("computerMenuGet", uuid)
        d.addErrback(self.onErrorRaise, "Imaging:computerMenuGet", uuid)
        return d
    def computerMenuSet(self, uuid, imagingMenu):
        """
        Sets the boot menu of a computer.
        Called by the MMC agent.
        """
        d = self.callRemote("computerMenuSet", uuid, imagingMenu)
        d.addErrback(self.onErrorRaise, "Imaging:computerMenuSet", [uuid, imagingMenu])
        return d
    # Computer log management
    def computerLogGet(self, uuid): # str
        """Get the imaging log of a computer."""
        d = self.callRemote("computerLogGet", uuid)
        d.addErrback(self.onErrorRaise, "Imaging:computerLogGet", uuid)
        return d
    # Computer images management
    def computerBackupImagesGet(self, uuid): # list of imageData
        """
        Returns the data about the backup images for the given computer.
        Called by the MMC agent.
        """
        d = self.callRemote("computerBackupImagesGet", uuid)
        d.addErrback(self.onErrorRaise, "Imaging:computerBackupImagesGet", uuid)
        return d
    def computerBackupImageLogGet(self, uuid, imageId):
        """
        Get the imaging log of a computer backup image.
        Called by the MMC agent.
        """
        d = self.callRemote("computerBackupImageLogGet", uuid, imageId)
        d.addErrback(self.onErrorRaise, "Imaging:computerBackupImageLogGet", [uuid, imageId])
        return d
    def computerImageIsoBuild(self, uuid, imageId):
        """
        Build the auto restoration ISO CDROM of an image.
        Called by the MMC agent.
        """
        d = self.callRemote("computerImageIsoBuild", uuid, imageId)
        d.addErrback(self.onErrorRaise, "Imaging:computerImageIsoBuild", [uuid, imageId])
        return d
    def computerBackupImagesSetInformations(self, imageId, informations):
        """
        Set backup image informations, informations is a dict containing image label, description, and a post installation script name.
        Called by the MMC agent.
        """
        d = self.callRemote("computerBackupImagesSetInformations", imageId, informations)
        d.addErrback(self.onErrorRaise, "Imaging:computerBackupImagesSetInformations", [imageId, informations])
        return d
    # Imaging server images management
    def ImagingServerStatus(self):
        """
        Returns a dict containing the status of the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerStatus")
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerStatus")
        return d
    def ImagingServerMastersGet(self): # list of imageData
        """
        Returns the list of available master on the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerMastersGet")
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerMastersGet")
        return d
    def ImagingServerMasterSetInformations(self, imageId, informations):
        """
        Set master image informations, informations is a dict containing image label, description, and a post installation script name.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerMasterSetInformations", imageId, informations)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerMasterSetInformations", [imageId, informations])
        return d
    def ImagingServerBootServicesGet(self): # list of bootServiceData
        """
        Returns the list of available boot services on the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerBootServicesGet")
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerBootServicesGet")
        return d
    def ImagingServerBootServiceSetInformations(self, imageId, informations):
        """
        Set boot service informations, informations is a dict containing image label, description, and a post installation script name.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerBootServiceSetInformations", imageId, informations)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerBootServiceSetInformations", [imageId, informations])
        return d
    def ImagingServerDefaultMenuGet(self): # imagingMenu
        """
        Returns the default boot menu of the imaging server.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerDefaultMenuGet")
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerDefaultMenuGet")
        return d
    def ImagingServerDefaultMenuSet(self, imagingMenu):
        """
        Set the default boot menu on this imaging server for new computer without a profile.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerDefaultMenuSet", imagingMenu)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerDefaultMenuSet", imagingMenu)
        return d
    def ImagingServerMasterIsoBuild(self, imageId):
        """
        Build the auto restoration ISO CDROM of a master.
        Called by the MMC agent.
        """
        d = self.callRemote("ImagingServerMasterIsoBuild", imageId)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerMasterIsoBuild", imageId)
        return d
    def ImagingServerBackupToMaster(self, imageId):
        """Convert a backup image to a master."""
        d = self.callRemote("ImagingServerBackupToMaster", imageId)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerBackupToMaster", imageId)
        return d
    def ImagingServerMasterDisable(self, imageId):
        """Disable a master."""
        d = self.callRemote("ImagingServerMasterDisable", imageId)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerMasterDisable", imageId)
        return d
    def ImagingServerMasterDelete(self, imageId, archive = True):
        """Delete a master. Maybe archive it."""
        d = self.callRemote("ImagingServerMasterDelete", imageId, archive)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerMasterDelete", [imageId, archive])
        return d
    def ImagingServerConfigurationSet(self, configuration):
        """Set the imaging server configuration (dict)."""
        d = self.callRemote("ImagingServerConfigurationSet", configuration)
        d.addErrback(self.onErrorRaise, "Imaging:ImagingServerConfigurationSet", configuration)
        return d

