#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id: improve.py 90 2008-04-8 09:24:56Z neisen $
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

'''
This is the module to add information to OCS XML
for the Windows platforms
'''

import wmi
import _winreg
import os
import xml.dom.minidom

from pulse2.proxyssl.config import Pulse2InventoryProxyConfig

if Pulse2InventoryProxyConfig().addicon:
    import win32ui
    import win32gui
    import win32con
    import win32api
    import cStringIO
    import Image    # need install PIL package http://www.pythonware.com/products/pil/
    import base64
    import tempfile
    
    #system icon size 
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    
    #tempory file
    tmpfile = tempfile.mkstemp()
    dirTmpFile = tmpfile[1] 
    #close the opened temp file (SaveBitmapFile Error)   
    file = os.fdopen(tmpfile[0])
    file.close()

'''    
Get the icon of file
@param path: the path of the file
@param nIcon: position of the icon in the file
@param exeOrDll=True: set False if is a icon file 
@return string bit of icon in Jpeg Format encoded in base64, else Error : None
'''    
def windowsIconGetter(path, nIcon = 0 , exeOrDll = True):  #It's can be exe, dll, or already ico
    
    if os.path.isfile(path):
        dst = cStringIO.StringIO()
        if exeOrDll:
            large, small = win32gui.ExtractIconEx(path,nIcon)
            win32gui.DestroyIcon(small[0])
            #creating a destination memory DC 
            hdc = win32ui.CreateDCFromHandle( win32gui.GetDC(0) )
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject( hbmp )
            #set the background in white
            hdc.FillSolidRect( (0,0,ico_x,ico_x), 0xffffff )
            #draw a icon in it
            hdc.DrawIcon( (0,0), large[0] )
            win32gui.DestroyIcon(large[0])
            #convert picture in JPEG
            hbmp.SaveBitmapFile( hdc, dirTmpFile)
            im = Image.open(dirTmpFile)
        else:
            im = Image.open(path)
        
        try:
            im.save(dst, "JPEG")
        except IOError:
            return None
                
        dst.seek(0)
        return base64.b64encode( dst.read() )   
    
    else:    
        return None 
 
'''
Convert the Registry Date in Humain format date DD/MM/YYYY HH:MM:SS
@param date: date in registry format to convert
@param displayHour=True: if the registry date have no reached hour, set False to doesn't get 00:00:00
@return: convert date
'''
def windowsDateConversion(date, displayHour = True):

    if (len(date)==8 or len(date)==25):     # check if it's good windows date system
        finaldate = date[6:8]+"/"+date[4:6]+"/"+date[0:4]
        if displayHour:
            finaldate = finaldate +" "+date[8:10]+":"+date[10:12]+":"+date[12:14]
    else:   # if the date is not in registry format
        finaldate = date
    
    return finaldate

'''
Calculate the size of folder
@param folder: the path of the folder to calculate
@return: the size of the folder in Ko 
'''
def sizeFolder(folder):
    size = 0
    for (current, subFolder, files) in os.walk(folder):
        size = size + sum( os.path.getsize( os.path.join(current, file) ) for file in files )
    return size/1024 #Ko

'''
Search the information to add
@return: Dictonary with information asked
'''
def informationSearch():            # Found any information for the computer.
    result = {}                     # Software infomration will be reached in next time
    
    #With WMI
    wmiObject = wmi.WMI()
    
    #Company Register
    try:
        companyRegister = wmiObject.Win32_OperatingSystem(["Organization"])[0].Organization
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        companyRegister = "N/A"
        
    result['companyRegister']=companyRegister
    
    #Os Architecture (32-64 bit) only for Vista and superior
    try:
        osArchitecture = wmiObject.Win32_OperatingSystem(["OSArchitecture"])[0].OSArchitecture
    except WindowsError: # pyflakes.ignore
        osArchitecture = "N/A"
    except wmi.x_wmi :    # If os is XP, 2003, 2000, 98, 95, ...
        osArchitecture = "32-bit"
        
    result['osArchitecture']=osArchitecture
    
    # First boot
    try:
        dateFirst = wmiObject.Win32_BIOS(["ReleaseDate"])[0].ReleaseDate
        dateFirst = windowsDateConversion(dateFirst,False)
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        dateFirst = "N/A"
        
    result['dateFirst']=dateFirst
    
    # Last boot
    try:    
        dateLastBoot = wmiObject.Win32_OperatingSystem(["LastBootUpTime"])[0].LastBootUpTime
        dateLastBoot = windowsDateConversion(dateLastBoot)
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        dateLastBoot = "N/A"
        
    result['dateLastBoot'] = dateLastBoot
    
    # Serial Number
    try:  
        serialNumber = wmiObject.Win32_BIOS(["SerialNumber"])[0].SerialNumber
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        serialNumber = "N/A"
           
    result['serialNumber'] = serialNumber
    
    # Operating system installation date
    try:    
        dateInstall = wmiObject.Win32_OperatingSystem(["InstallDate"])[0].InstallDate
        dateInstall = windowsDateConversion(dateInstall)
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        dateInstall = "N/A"
        
    result['installDate'] = dateInstall
    
    # Default Gateway
    try:    
        interfacesAdapter = wmiObject.Win32_NetworkAdapterConfiguration(["DefaultIPGateway"])
        for interface in interfacesAdapter:
            if not (interface.DefaultIPGateway is None):
                defaultGateway = interface.DefaultIPGateway[0]
                break
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        defaultGateway = "N/A"
        
    result['defaultGateway'] = defaultGateway
        
        
    # Operating system folder
    try:
        # os.getenv("windir")
        result['OSfolder'] = wmiObject.Win32_OperatingSystem(["WindowsDirectory"])[0].WindowsDirectory     #by WMI. The installation can be anywhere
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        result['OSfolder'] = "N/A"    
        
    # last login date
    wmiObject = wmi.WMI(privileges=["Security"])
    try:
        lastLoginLog = wmiObject.Win32_NTLogEvent(["InsertionStrings","TimeGenerated"],EventCode=680)[0]    # For Win XP et 2k, EventCode = 680, but with Vista EventCode = 4624
        lastLogin = [lastLoginLog.InsertionStrings[1],lastLoginLog.TimeGenerated]
        # convert the date
        lastLogin[1] = windowsDateConversion(lastLogin[1])
        result['lastLogin']=lastLogin
    except (WindowsError, wmi.x_wmi, IndexError): # pyflakes.ignore
        result['lastLogin']=["N/A","N/A"]
    
    return result
    
'''
Improve the xml File with the Information and another research
@param xmlString: the xml String of the xml file to improve
@param lastInformation: some information to add in xml
@return: the improving xmlString 
'''
def xmlUpdate(xmlString, lastInformation):
    
    xmlFile = xml.dom.minidom.parseString(xmlString)
    
    # Check Serial number between Ocs and WMI
    ssn = xmlFile.getElementsByTagName("SSN")[0].childNodes[0].nodeValue
    if ( len(lastInformation['serialNumber']) > 0 and ssn != lastInformation['serialNumber'] ):
        ssn = lastInformation['serialNumber']
        
    # Operating system installation date
    newnode = xmlFile.createElement("INSTALLDATE")
    newtext = xmlFile.createTextNode(lastInformation['installDate'])
    refnode = xmlFile.getElementsByTagName("OSVERSION")[0]
    
    newnode.appendChild(newtext)
    refnode.parentNode.insertBefore(newnode,refnode.nextSibling)
    #Optionnal : help to the final xml File can be easy read
    newnode.parentNode.insertBefore(xmlFile.createTextNode("\n"),newnode)    
    
    
    # Company Register
    newnode = xmlFile.createElement("WINCOMPANY")
    newtext = xmlFile.createTextNode(lastInformation['companyRegister'])
    refnode = xmlFile.getElementsByTagName("WINOWNER")[0]
    
    newnode.appendChild(newtext)
    refnode.parentNode.insertBefore(newnode,refnode.nextSibling)
    newnode.parentNode.insertBefore(xmlFile.createTextNode("\n"),newnode) 
    
    
    # OS Architecture 
    newnode = xmlFile.createElement("OSARCHITECTURE")
    newtext = xmlFile.createTextNode(lastInformation['osArchitecture'])
    refnode = xmlFile.getElementsByTagName("OSNAME")[0]
    
    newnode.appendChild(newtext)
    refnode.parentNode.insertBefore(newnode,refnode.nextSibling)
    newnode.parentNode.insertBefore(xmlFile.createTextNode("\n"),newnode) 
	
	
    # Last login Date
    newnode = xmlFile.createElement("DATELASTLOGGEDUSER")
    newtext = xmlFile.createTextNode(lastInformation['lastLogin'][1])
    refnode = xmlFile.getElementsByTagName("LASTLOGGEDUSER")[0]
    
    newnode.appendChild(newtext)
    refnode.parentNode.insertBefore(newnode,refnode.nextSibling)
    newnode.parentNode.insertBefore(xmlFile.createTextNode("\n"),newnode)     
    
    
    # Default Gateway
    newnode = xmlFile.createElement("DEFAULTGATEWAY")
    newtext = xmlFile.createTextNode(lastInformation['defaultGateway'])
    refnode = xmlFile.getElementsByTagName("HARDWARE")[0]
    
    newnode.appendChild(newtext)
    refnode.appendChild(newnode)
    refnode.appendChild(xmlFile.createTextNode("\n"))
    
    
    # First boot date
    newnode = xmlFile.createElement("DATEFIRSTRUN")
    newtext = xmlFile.createTextNode(lastInformation['dateFirst'])
    refnode = xmlFile.getElementsByTagName("BIOS")[0]
    
    newnode.appendChild(newtext)
    refnode.appendChild(newnode)
    refnode.appendChild(xmlFile.createTextNode("\n"))
    
    
    # Last boot date
    newnode = xmlFile.createElement("DATELASTRUN")
    newtext = xmlFile.createTextNode(lastInformation['dateLastBoot'])
    refnode = xmlFile.getElementsByTagName("BIOS")[0]
    
    newnode.appendChild(newtext)
    refnode.appendChild(newnode)
    refnode.appendChild(xmlFile.createTextNode("\n"))
    
    # Who is Burner ?
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,"Software\Microsoft\Windows\CurrentVersion\Explorer\CD Burning\Drives")
    deviceKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"System\MountedDevices\\")
    #Search the tag of all burner
    burner = []
    try:
        i = 0
        while True:
            keyname = _winreg.EnumKey(key,i)
            subkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,"Software\Microsoft\Windows\CurrentVersion\Explorer\CD Burning\Drives\\"+keyname)
            if not ( _winreg.QueryValueEx(subkey,"Drive Type")[0] == 3 ):
                burner.append( _winreg.QueryValueEx(deviceKey,"\\??\\"+keyname)[0] )
            
            _winreg.CloseKey(subkey)
            i = i + 1
    except WindowsError: # pyflakes.ignore
        pass    
    _winreg.CloseKey(key)
    
    #Add if the drive is burner
    for device in xmlFile.getElementsByTagName("DRIVES"):
        if device.getElementsByTagName("TYPE")[0].firstChild.nodeValue == "CD-Rom Drive" :
            isBurner = False
            newnode = xmlFile.createElement("BURNER")
            i = 0
            while i < len(burner) and not isBurner :
                #Compare the tag with the tag of DosDevices to found the letter device of the burner
                isBurner = ( _winreg.QueryValueEx(deviceKey,"\\DosDevices\\"+ device.getElementsByTagName("LETTER")[0].firstChild.nodeValue[0]+":")[0] == burner[i] )
                if isBurner :
                    del burner[i]
                i += 1  
            
            if isBurner:
                newtext = xmlFile.createTextNode( "Burner" )
            else:
                newtext = xmlFile.createTextNode( "Only Reader" )
            
            newnode.appendChild(newtext)
            device.appendChild(newnode)
            device.appendChild(xmlFile.createTextNode("\n"))        
    
    _winreg.CloseKey(deviceKey)  
    
    # Initializing Variable 
    listSoftXML = xmlFile.getElementsByTagName("SOFTWARES")
    listSoftXMLDefault = xmlFile.getElementsByTagName("SOFTWARES")
    OSNAME = xmlFile.getElementsByTagName("OSNAME")[0].firstChild.nodeValue
    defaultNode = listSoftXMLDefault[0].cloneNode(1)  
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    updateDetection = Pulse2InventoryProxyConfig().updatedetection
    
    try:
        i = 0
        while True:         #For every software in Uninstall Registry          
            keyname = _winreg.EnumKey(key,i)
            subkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\\"+keyname)
            
            try:
                displayName = _winreg.QueryValueEx(subkey,"DisplayName")[0]
                nodeId = foundNodeInList(listSoftXML,"NAME",displayName)                 
                                
                if nodeId != -1:
                    selectnode = listSoftXML[nodeId]
				    #del(listSoftXML[nodeId])       # Warning : Both key Registry can be exist for the same software.
                                                    # Drop used software can acelerat the improving
                                                    # but it can lost some information in two places.
				    #Type Package
                    newnode = xmlFile.createElement("FROM")
                    newtext = xmlFile.createTextNode('win')
                    
                    newnode.appendChild(newtext)
                    selectnode.appendChild(newnode)
                    selectnode.appendChild(xmlFile.createTextNode("\n"))
					
					
                    #Software installation Date
                    try:
                        installDate = _winreg.QueryValueEx(subkey,"InstallDate")[0] 
                        installDate = windowsDateConversion(installDate,False)                       
                    except WindowsError: # pyflakes.ignore
                        installDate = "N/A"
                    
                    newnode = xmlFile.createElement("INSTALLDATE")
                    newtext = xmlFile.createTextNode(installDate)
                        
                    newnode.appendChild(newtext)
                    selectnode.appendChild(newnode)
                    selectnode.appendChild(xmlFile.createTextNode("\n"))
                                        
                    
                    # Version Check
                    try:
                        refnode = selectnode.getElementsByTagName("VERSION")[0].firstChild
                        if refnode.nodeValue == "N/A":
                            displayversion = _winreg.QueryValueEx(subkey,"DisplayVersion")[0]
                            refnode.nodeValue = displayversion                      
                    except WindowsError: # pyflakes.ignore
                        pass                   
                    
                    # Software size calculated on hardDisk
                    try:
                        folder = _winreg.QueryValueEx(subkey,"InstallLocation")[0]
                        if len(folder) > 0 :
                            foldersize = sizeFolder(folder)
                            if not (foldersize > 0):
                                foldersize = "N/A"
                                
                        else:
                            foldersize = "N/A"
                            newnode = xmlFile.createElement("FOLDER")
                            newtext = xmlFile.createTextNode("N/A")
                            refnode = selectnode.getElementsByTagName("VERSION")[0]
                            
                            newnode.appendChild(newtext)
                            refnode.parentNode.insertBefore(newnode,refnode.nextSibling)
                            newnode.parentNode.insertBefore(xmlFile.createTextNode("\n"),newnode)
                                                
                    except WindowsError: # pyflakes.ignore
                        foldersize = "N/A"
                        folder = "N/A"
                        
                    newnode = xmlFile.createElement("FOLDERSIZE")
                    newtext = xmlFile.createTextNode(str(foldersize))
                    refnode = selectnode.getElementsByTagName("FOLDER")[0]
        
                    newnode.appendChild(newtext)
                    refnode.parentNode.insertBefore(newnode,refnode.nextSibling)
                    newnode.parentNode.insertBefore(xmlFile.createTextNode("\n"),newnode)  
                    
                    # Software Size estimated by Operating System
                    try:
                        estimatedSize = _winreg.QueryValueEx(subkey,"EstimatedSize")[0]
                        if not (estimatedSize > 0):
                            estimatedSize = "N/A"
                    except WindowsError: # pyflakes.ignore
                        estimatedSize = "N/A"
                    
                    selectnode.getElementsByTagName("FILESIZE")[0].firstChild.nodeValue = estimatedSize
                    
                    #Uninstall command
                    try:
                        uninstallCommand = _winreg.QueryValueEx(subkey,"UninstallString")[0]
                    except WindowsError: # pyflakes.ignore
                        uninstallCommand = "N/A"
                    
                    if len(uninstallCommand)==0:
                        uninstallCommand = "N/A"
                    
                    newnode = xmlFile.createElement("UNINSTALL")
                    newtext = xmlFile.createTextNode(uninstallCommand)
        
                    newnode.appendChild(newtext)
                    selectnode.appendChild(newnode)
                    selectnode.appendChild(xmlFile.createTextNode("\n"))            
                    
                    # update detections
                    isUpdate = False
                    if updateDetection:
                        try:
                            parentKey = _winreg.QueryValueEx(subkey,"ParentKeyName")[0]
                            isUpdate = True
                            nodeParentId = -1
                            if len(parentKey)>0:
                                if parentKey =='OperatingSystem' :  #Update de l'OS
                                    nodeParentId = foundNodeInList(listSoftXMLDefault,"NAME",OSNAME)
                                    parentName = OSNAME
                                else :
                                    try:
                                        parentRegisterKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\\"+parentKey)
                                        parentName = _winreg.QueryValueEx(parentRegisterKey,"DisplayName")[0]
                                        _winreg.CloseKey(parentRegisterKey)
                                        nodeParentId = foundNodeInList(listSoftXMLDefault,"NAME",parentName)
                                    except WindowsError:    # if parent doesn't exist # pyflakes.ignore
                                        parentName = _winreg.QueryValueEx(subkey,"ParentDisplayName")[0]
                                        if len(parentName)>0:   # search parent with his name
                                            nodeParentId = foundNodeInList(listSoftXMLDefault,"NAME",parentName)
                                            if nodeParentId == -1:  # create the simulated parent
                                                newnode = defaultNode.cloneNode(1)
                                                nodeslist = newnode.childNodes
                                                for j in range(0,len(nodeslist)):
                                                    if j%2==1:
                                                        nodeslist[j].firstChild.nodeValue = "N/A"
                                                        
                                                newnode.getElementsByTagName("NAME")[0].firstChild.nodeValue = parentName
                                                xmlFile.getElementsByTagName("CONTENT")[0].insertBefore(newnode,listSoftXMLDefault[len(listSoftXMLDefault)-1])
                                                nodeParentId = foundNodeInList(listSoftXMLDefault,"NAME",parentName)
                                            
                                            listSoftXMLDefault = xmlFile.getElementsByTagName("SOFTWARES")
                                            nodeParentId = foundNodeInList(listSoftXMLDefault,"NAME",parentName)
                                
                                if nodeParentId > -1:
                                    '''
                                    selectnode.tagName = "UPDATE"                       #to transformed the select node (update) 
                                    del(listSoftXML[nodeId])                            #on child of his parent node (software updated)
                                    selectnode.parentNode.removeChild(selectnode.previousSibling)
                                    listSoftXMLDefault[nodeParentId].appendChild(selectnode)
                                    listSoftXMLDefault[nodeParentId].appendChild(xmlFile.createTextNode("\n"))
                                    '''
                                    
                                    selectnode.setAttribute("parent",parentName)    #only notified the dependance by attribute
                                    del(listSoftXML[nodeId])
                                      
                        except WindowsError: # pyflakes.ignore
                            isUpdate = False
                    
                    # if not update, we calculate this Rate Of Use and get icon
                    #log-on frequency    Only for WinXP et 2K (On Vista, it's doesn't exist)
                    if not updateDetection or ( updateDetection and not isUpdate ):
                        try:
                            arpKey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,"SOFTWARE\Microsoft\Windows\CurrentVersion\App Management\ARPCache\\"+keyname)
                            try:
                                rateOfUse = _winreg.QueryValueEx(arpKey,"SlowInfoCache")[0]
                                valueRateOfUse = ord(rateOfUse[24])
                                if valueRateOfUse == 255:
                                    valueRateOfUse = "N/A"
                                    
                            except WindowsError: # pyflakes.ignore
                                valueRateOfUse = "N/A"
                                
                            _winreg.CloseKey(arpKey)
                        except WindowsError: # pyflakes.ignore
                            valueRateOfUse = "N/A"
                            
                        refnode = selectnode.getElementsByTagName("RATEOFUSE") 
                        if len(refnode) == 0:
                            newnode = xmlFile.createElement("RATEOFUSE")
                            newtext = xmlFile.createTextNode(str(valueRateOfUse))
                                
                            newnode.appendChild(newtext)
                            selectnode.appendChild(newnode)
                            selectnode.appendChild(xmlFile.createTextNode("\n"))
                        else :
                            if valueRateOfUse != "N/A":
                                if refnode[0].firstChild.valueNode != "N/A":
                                    refnode[0].firstChild.valueNode = refnode[0].firstChild.valueNode + valueRateOfUse
                                else :
                                    refnode[0].firstChild.valueNode = valueRateOfUse
                        
                        
                        if Pulse2InventoryProxyConfig().addicon:
                            try:
                                iconpath = _winreg.QueryValueEx(subkey,"DisplayIcon")[0]
                                if iconpath[0] == '"':
                                    iconpath = iconpath[1:len(iconpath)-1]
                                
                                k = len(iconpath) -1    
                                while ( k > (len(iconpath) - 4) and iconpath[k] != ',' ):
                                    k -= 1
                                
                                nIcon = 0
                                if iconpath[k] == ',':
                                    try:    
                                        if (k < len(iconpath)):
                                            nIcon = int(iconpath[k+1])
                                    except ValueError :
                                        pass
                                    iconpath = iconpath[0:k] 
                                length = len(iconpath)
                                
                                if iconpath[length-3:] == 'ico':
                                    stringBit = windowsIconGetter(iconpath, nIcon, False)
                                else:
                                    stringBit = windowsIconGetter(iconpath, nIcon, True )
                                
                                if stringBit != None:
                                    newnode = xmlFile.createElement("ICON")
                                    newtext = xmlFile.createTextNode( stringBit )
                        
                                    newnode.appendChild(newtext)
                                    selectnode.appendChild(newnode)
                                    selectnode.appendChild(xmlFile.createTextNode("\n"))
                                
                            except WindowsError: # pyflakes.ignore
                                pass
                                
            except WindowsError: # pyflakes.ignore
                pass
            
            _winreg.CloseKey(subkey)
            i += 1
            
    except WindowsError: # pyflakes.ignore
        pass

    if Pulse2InventoryProxyConfig().addicon:
        # Do NOT FORGET !
        os.remove(dirTmpFile)
        
    _winreg.CloseKey(key)
    xmlString = xmlFile.toxml("utf-8")
    return xmlString

'''
Search in the list of xml node, the value in tagName
@param listnode: the list of node
@param tagName: the Tag Name to procedd reasearch
@param value: the value research
@return: the index in the list of the node, else -1
'''
def foundNodeInList (listnode, tagName, value):
    
    i = 0
    found = False
    
    while not found and len(listnode)>i:               
        found = ( listnode[i].getElementsByTagName(tagName)[0].firstChild.nodeValue == value )
        i += 1        
        
    if found:
        i -= 1
    else:
        i = -1
                
    return i

'''
Improve the xml File and eventuality, save it on local machine
@param xmlFileString: the xml String to improve
@return: the improving xml String
'''
def improveXML( xmlFileString ):
        
    xmlFileString = xmlUpdate(xmlFileString, informationSearch() )
    if Pulse2InventoryProxyConfig().savexmlmodified:
        filout = open('XmlOutput.xml','w')
        for i in xmlFileString:
            filout.write(i)    
        filout.close()
          
    return xmlFileString

'''
Add the last log of OCS in xml
@param xmlString: the xml String to modify
@return: the xml String with the log
'''
def getOcsDebugLog( xmlString ):
    
    xmlFile = xml.dom.minidom.parseString(xmlString)
    userDomaine = xmlFile.getElementsByTagName("USERDOMAIN")[0].firstChild.nodeValue
    ocsFolder = Pulse2InventoryProxyConfig().command_name
    i = len(ocsFolder)
    found = False
    while not found and i>0:
        found = ( ocsFolder[i-1] == '\\' )
        i -= 1 
    
    if found :
        logFile = open ( ocsFolder[0:i+1] + userDomaine + ".log" , "r")
        logFileString = logFile.read()
        logFile.close()
    else :
        logFileString = "Error : couldn't open Log File"
        
    newnode = xmlFile.createElement("OCSDEBUG")
    newsubnode = xmlFile.createElement("DEBUGLOG")
    newtext = xmlFile.createTextNode(logFileString)
    refnode = xmlFile.getElementsByTagName("CONTENT")[0]
    #Optional : help to the final xml File can be esay read
    newsubnode.appendChild(newtext)
    newnode.appendChild(xmlFile.createTextNode("\n"))
    newnode.appendChild(newsubnode)
    newnode.appendChild(xmlFile.createTextNode("\n"))
    refnode.appendChild(newnode)
    refnode.appendChild(xmlFile.createTextNode("\n"))
    
    xmlString = xmlFile.toxml("utf-8")  
    return xmlString
