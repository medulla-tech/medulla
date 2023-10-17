# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
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

# File : mmc/plugins/testenv/__init__.py

import base64
from pulse2.version import getVersion, getRevision # pyflakes.ignore
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.testenv.config import TestenvConfig

from pulse2.database.testenv import TestenvDatabase

import six
from six.moves.urllib.parse import urlparse, urlencode
from jenkinsapi.jenkins import Jenkins
import xml.etree.ElementTree as ET
from guacapy import Guacamole
import subprocess
import xmltodict
import binascii
import requests
import logging
import time
import json
import os

import libvirt

VERSION = "1.0.0"
APIVERSION = "1:0:0"

logger = logging.getLogger()
config = TestenvConfig("testenv")

# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################
def getApiVersion():
    return APIVERSION

def activate():
    logger = logging.getLogger()
    config = TestenvConfig("testenv")

    if config.disable:
        logger.warning("Plugin testenv: disabled by configuration.")
        return False


    if not TestenvDatabase().activate(config):
        logger.warning("Plugin testenv: an error occurred during the database initialization")
        return False
    return True

def tests():
    return TestenvDatabase().tests()

def buildJenkinsUrl(username, token, url):
    """
    This function allows you to create a VM by sending a post request to the URL.
    Args:
        URL (string): URL of the request
        Username (string): Jenkins username
        Token (string): Jenkins password
    Returns:
        bool: True If the post request has been sent, false otherwise
    """
    # Build the Crumb URL from Jenkins
    parsed_url = six.moves.urllib.parse.urlparse(url)
    crumb_issuer = six.moves.urllib.parse.urlunparse((parsed_url.scheme,
                                                      parsed_url.netloc,
                                                      'crumbIssuer/api/json',
                                                      '',
                                                      '',
                                                      ''))

    session = requests.session()

    # Recover Jenkins Crumb
    auth = requests.auth.HTTPBasicAuth(username, token)

    # I get the Crumb (my crumb)
    result = session.get(crumb_issuer, auth=auth)

    if result.status_code == 200 and result.text:
        try:
            # Convert the JSON answer to a Python dictionary and recover the value of the Crumb
            json_data = result.json()
            crumb = {json_data['crumbRequestField']: json_data['crumb']}

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            headers.update(crumb)
            result = session.post(url, headers=headers, auth=auth)

            return True

        except Exception as e:
            logger.error("Response content is not valid JSON: '%s' Error message: '%s'", result.text, e)
            return False
    else:
        return False

def checkStatusJobPending(job_name):
    """
    This function makes it possible to check the status of a Jenkins job if it is in progress or not.
    Args:
        job_name (string): Job Job name
    Returns:
        bool: True if the job is running, False otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url

    jenkins = Jenkins(jenkins_url, username=username, password=token)

    job = jenkins[job_name]

    # Delay to give Jenkins time to create the build
    time.sleep(15)
    last_build = job.get_last_build()

    # Check if the build is running
    if last_build.is_running():
        console_output = last_build.get_console()
        return True, console_output
    else:
        console_output = last_build.get_console()
        return False, console_output

def getLastBuildOutput(job_name):
    """
    This function allows you to recover the output of the console from the last execution of a Jenkins job.
    Args:
        job_name (string): Job name
    Returns:
        string: Output of the console
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url

    jenkins = Jenkins(jenkins_url, username=username, password=token)

    job = jenkins[job_name]

    last_build = job.get_last_build()
    console_output = last_build.get_console()

    result = {}

    # Browse each line of the console exit
    for ligne in console_output.split("\n"):
        # Check if the line contains a key and a value
        if ":" in ligne:
            # Separate the key and the value using the first ":" found
            cle, valeur = ligne.split(":", 1)
            # Add the key and value to Result
            result[cle.strip()] = valeur.strip()

    return result, True


def get_status_description(status_code):
    """
    Recover the description of a status code
    Args:
        status_code (int): Status code
    Returns:
        string: Description of the status code
    """
    if status_code == libvirt.VIR_DOMAIN_RUNNING:
        return "Running"
    elif status_code == libvirt.VIR_DOMAIN_PAUSED:
        return "Paused"
    elif status_code == libvirt.VIR_DOMAIN_SHUTDOWN:
        return "Shutdown"
    elif status_code == libvirt.VIR_DOMAIN_SHUTOFF:
        return "Shutoff"
    elif status_code == libvirt.VIR_DOMAIN_CRASHED:
        return "Crashed"
    elif status_code == libvirt.VIR_DOMAIN_NOSTATE:
        return "No State"
    elif status_code == libvirt.VIR_DOMAIN_PMSUSPENDED:
        return "PM Suspended"
    else:
        return "Unknown"

def getAllVMList():
    """
    Recover the list of virtual machines
    Returns:
        list: List of virtual machines
    """
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.listAllDomains(0)
        logger.debug("Connection to the successful hypervisor!")

        vm_list = []
        for i in domain:
            vm_info = {
                'id': i.ID(),
                'name': i.name(),
                'status': get_status_description(i.state()[0])
            }
            vm_list.append(vm_info)

        return vm_list

    except Exception as e:
        logger.error("Failure to connect to the hypervisor! Error message: '%s'", e)
        return False

def getVMInfo(vm_name):
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(vm_name)

        if domain is None:
            logger.error("Area '%s' not found", vm_name)
            return ""

        xml = domain.XMLDesc()
        info = domain.info()

        root = ET.fromstring(xml)
        domain_info = {
            "id": root.get("id", "No ID"),  # VM ID
            "name": root.findtext("name", "No name"),  # VM name
            "uuid": root.findtext("uuid", "No uuid"),  # Uuid of the VM
            "plateform": root.findtext("os/type", "No bone type"),  # OS of the VM
            "architecture": root.find("os/type").attrib.get("arch", "No architecture"), # VM architecture
            "currentCpu": info[3], # Number of CPU
            "maxCpu": root.findtext("vcpu", "No CPU"),  # Number of maximum CPUs
            "maxMemory": int(root.findtext("memory", "No memory")) / 1024,  # Total memory (MB)
            "currentMemory": root.findtext("currentMemory", "No data"),  # Memory used
            "model": root.find("os/type").attrib.get("machine", "No model"), # VM model
            "mac_address": root.find("devices/interface/mac").attrib.get("address", "No mac address"), # Mac address
            "state": get_status_description(domain.state()[0]),  # Recover the condition with the auxiliary function
            "persistent": root.findtext("on_poweroff", "No data"),  # Persistent
            "port_vnc": root.find("devices/graphics").get("port", "No VNC port")
        }

        return domain_info

    except Exception as e:
        logger.error("Failed to connect to the hypervisor! Error message: '%s'", e)
        return False

# TO FIX
def editNameVM(old_name, new_name):
    """
    Rename a virtual machine
    Args:
        old_name (string): Old name of the virtual machine
        new_name (string): New name of the virtual machine
    Returns:
        bool: True if the virtual machine has been renamed, False otherwise
    """
    infoVM = getVMInfo(old_name)
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(old_name)

        if domain is None:
            logger.error("Area '%s' not found", old_name)
            return False

        # Check if the machine is lit and, in this case, turn it off
        if domain.isActive():
            try:
                domain.destroy()
                logger.debug("Domain stop '%s'", old_name)
            except Exception as e:
                logger.error("Domain failure failure '%s', Error message: '%s'", old_name, e)
                return False

        try:
            domain.rename(new_name)
            logger.debug("The domain '%s' was renamed in'%s' ", old_name, new_name)

            # Update the source path of the virtual disc
            xml = domain.XMLDesc()
            root = ET.fromstring(xml)
            disks = root.findall("devices/disk")
            for disk in disks:
                source = disk.find("source")
                if source is not None:
                    old_path = source.get("file")
                    if old_path.startswith("/var/lib/libvirt/images/{}.".format(old_name)):
                        new_path = old_path.replace("/var/lib/libvirt/images/{}.".format(old_name),
                                                    "/var/lib/libvirt/images/{}.".format(new_name))
                        source.set("file", new_path)
                        logger.debug("The source path of the disc has been updated to '%s'", new_path)

            xml = ET.tostring(root).decode("utf-8")
            conn.defineXML(xml)

            # Update the file
            image_path = "/var/lib/libvirt/images/{}.qcow2".format(old_name)
            new_image_path = "/var/lib/libvirt/images/{}.qcow2".format(new_name)
            if not os.path.exists(image_path):
                logger.error("The '%s' file does not exist", image_path)
                return False
            else:
                os.rename(image_path, new_image_path)
                logger.debug("The '%s' file was renamed in '%s' ", image_path, new_image_path)

            vm_dict = {
                "old_name": old_name,
                "new_name": new_name,
                "uuid": infoVM['uuid'],
                "plateform": infoVM['plateform'],
                "architecture": infoVM['architecture'],
                "vcpu": infoVM['currentCpu'],
                "memory": infoVM['maxMemory'],
                "state": infoVM['state'],
                "persistent": infoVM['persistent'],
            }

            if not TestenvDatabase().updateVM(vm_dict):
                logger.error("Failure of updating the name in the database")
                return False
            else:
                logger.debug("The machine name has been updated in the database")

            if not editNameGuac(old_name, new_name):
                logger.error("Failure to update the name in Guacamole")
                return False
            else:
                logger.debug("The name of the machine has been updated in Guacamole")

            # Start the machine with the new name
            if not start_vm(new_name):
                logger.error("Machine start -up failure '%s'", new_name)
                return False
            else:
                logger.debug("The machine '%s' was successfully started", new_name)

            logger.debug("The machine '%s' was renamed in '%s' ", old_name, new_name)
            return True

        except Exception as e:
            logger.error("Failure to rename the domain '%s'", old_name)
            logger.error("Failed to connect to the hypervisor! Error message: '%s'", e)
            return False

    except Exception as e:
        logger.error("Failed to connect to the hypervisor! Error message: '%s'", e)
        return False


def create_vm(name, desc, ram, cpu, disk_size, os):
    """
    This function allows you to create a VM by sending a post request to the URL
    Args:
        name (string): Name of the VM
        desc (string): Description of the VM
        ram (int): RAM of the VM
        cpu (int): CPU of the VM
        disk_size (int): Disk size of the VM
        os (string): OS of the VM
    Returns:
        bool: True If the post request has been sent, false otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'create-vm'

    try:
        # Build the URL to create a VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={token}&NAME={name}&DESC={desc}&RAM={ram}&CPUS={cpu}&DISK_SIZE={disk_size}&OS={os}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=name, desc=desc, ram=ram, cpu=cpu, disk_size=disk_size, os=os)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("The virtual machine '%s' was successfully created.", name)

                dict = getVMInfo(name)

                if createConnectionGuac(name):
                    logger.debug("Guacamole connection successfully created")

                    if TestenvDatabase().createVM(dict):
                        logger.debug("Successful database update")
                        dict_guac = dictGuac(name)

                        if TestenvDatabase().setInfoGuac(dict_guac):
                            logger.debug("Successful database update")
                            return True

                        else:
                            logger.error("Failure to update the Guac database")
                            return False
                    else:
                        logger.error("Failure of updating the machine database")
                        return False
                else:
                    logger.error("Failure to create the Guacamole connection")
                    return False
            else:
                logger.debug("The job '%s' is not running.", job_name)
                return False
        else:
            logger.error("Failure to create the job '%s'.", job_name)
            return False

    except Exception as e:
        logger.error("Failure during the construction of the URL Jenkins, Error message: '%s'", e)
        return False

def delete_vm(vm_name):
    """
    This function makes it possible to delete a VM by sending a post request to the URL
    Args:
        vm_name (string): Name of the VM
    Returns:
        bool: True If the post request has been sent, false otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'delete-vm'

    try:
        # Build the URL to delete a VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={token}&NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("La machine virtuelle '%s' est en cours de suppression.", vm_name)
                if TestenvDatabase().deleteVM(vm_name):
                    logger.debug("La machine virtuelle '%s' a été supprimée avec succès.", vm_name)
                    return True
                else:
                    logger.error("Échec de la suppression de la machine virtuelle '%s' dans la base de données.", vm_name)
                    return False
            else:
                logger.error("La machine virtuelle '%s' n'est pas en cours de suppression.", vm_name)
                return False
        else:
            logger.error("Échec de la création du job.")
            return False

    except Exception as e:
        logger.error("Échec de la construction de l'URL Jenkins : '%s'", e)
        return False

def start_vm(vm_name):
    """
    This function allows you to turn on a VM by sending a Post request to the URL
    Args:
        vm_name (string): Name of the VM
    Returns:
        bool: True If the post request has been sent, false otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'start-vm'

    try:
        # Build the URL to start a VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={job_name}&VM_NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("The virtual machine '%s' is under ignition.", vm_name)

                dict_guac = dictGuac(vm_name)

                if TestenvDatabase().updateStatutVM(vm_name, "Running") and TestenvDatabase().updateInfoGuac(dict_guac):
                    logger.debug("The virtual machine '%s' is updated with 'Running' status in the database.", vm_name)

                    if updateGuac(dict_guac['machine_name'], dict_guac['port']):
                        logger.debug("The virtual machine '%s' is updated with 'Running' status in the database.", vm_name)
                        return True
                    else:
                        logger.error("Failure to update the virtual machine '%s' in Guacamole.", vm_name)
                        return False
                else:
                    logger.error("Failure to update the status of the virtual machine '%s' in the database.", vm_name)
                    return False
            else:
                logger.error("The virtual machine '%s' is not in the process of ignition.", vm_name)
                return False
        else:
            logger.error("Failure to create the job.")
            return False

    except Exception as e:
        logger.error("Failure to build the Jenkins URL, Error message: '%s'", e)
        return False

def forceshutdown_vm(vm_name):
    """
    This function allows you to force the extinction of a VM by sending a post request to the URL
    Args:
        vm_name (string): Name of the VM
    Returns:
        bool: True If the post request has been sent, false otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'forceshut-vm'

    try:
        # Build the URL to force the extinction of a VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={job_name}&VM_NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("The virtual machine '%s' is being extinction.", vm_name)
                try:
                    logger.debug("Database update: 'Shutoff' status for the virtual machine '%s'.", vm_name)
                    if TestenvDatabase().updateStatutVM(vm_name, "Shutoff"):
                        logger.debug("Successful database update for the virtual machine '%s'.", vm_name)
                        return True
                    else:
                        logger.error("Failure of updating the database for the virtual machine '%s'.", vm_name)
                        return False
                except Exception as e:
                    logger.error("Error when updating the database, Error message: '%s'", e)
                    return False
            else:
                logger.error("The virtual machine '%s' is not being extinction.", vm_name)
                return False
        else:
            logger.error("Failure to create the job.")
            return False

    except Exception as e:
        logger.error("Failure to build the Jenkins URL, Error message: '%s'", e)
        return False

# TO DO
def shutdown_vm(url):
    """
    This function makes it possible to extinguish a VM to envoanr a post post to the url
    Args:
        url (string): URL of the request
    Returns:
        bool: True If the post request has been sent, false otherwise
    """
    try:
        username = config.jenkins_username
        token = config.jenkins_token
        url2 = config.jenkins_url + url

        buildJenkinsUrl(username, token, url2)

        logger.debug("Successful virtual machine with the URL: '%s'", url)
        return True

    except requests.exceptions.RequestException as e:
        logger.error("An error occurred during the extinction of the virtual machine, Error message: '%s'", e)
        return False


def createConnectionGuac(name):
    """
    This function allows you to create a Guacamole connection
    Args:
        name (string): Name of the VM
    Returns:
        bool: True if the Guacamole connection has been created, False otherwise
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole')
    try:
    # Automatic port when creating the VM of the blow once the VM creates we recover the port to put it in the connection
        port = getVMInfo(name)['port_vnc']

        payload = {
            "parentIdentifier": "ROOT",
            "protocol": "vnc",
            "name": name,
            "activeConnections": 0,
            "attributes":{"max-connections":"","max-connections-per-user":""},
            "parameters": {
                "port": port,
                "enable-menu-animations":"true",
                "enable-desktop-composition":"true",
                "hostname":"127.0.0.1",
                "color-depth":"32",
                "enable-font-smoothing":"true",
                "ignore-cert":"true",
                "enable-drive":"true",
                "enable-full-window-drag":"true",
                "security":"any",
                "password":"",
                "enable-wallpaper":"true",
                "create-drive-path":"true",
                "enable-theming":"true",
                "console":"true",
            }
        }

        guacapi.add_connection(payload)
        return True

    except Exception as e:
        logger.error("Failure to create the Guacamole connection, Error message: '%s'", e)
        return False

def urlGuac(name):
    """
    This function allows you to recover the Guacamole URL from a connection
    Args:
        name (string): Name of the VM
    Returns:
        string: Guacamole URL
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole')
    try:
        identifier = guacapi.get_connection_by_name(name)['identifier']

        token_hex = binascii.hexlify(identifier) + '00' + binascii.hexlify('c') + '00' + binascii.hexlify('mysql')
        token = base64.b64encode(binascii.unhexlify(token_hex))

        url = config.guacamole_url_client + token + '?username=' + config.guacamole_username + '&password=' + config.guacamole_password

        return url

    except Exception as e:
        logger.error("Failed to recover the Guacamole URL, Error message: '%s'", e)
        return False

def deleteGuac(name):
    """
    This function allows you to delete a Guacamole connection
    Args:
        name (string): Name of the VM
    Returns:
        bool: True if the Guacamole connection has been deleted, False otherwise
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole')
    try:
        identifier = guacapi.get_connection_by_name(name)['identifier']

        guacapi.delete_connection(identifier)
        return True

    except Exception as e:
        return False

def updateGuac(name, port):
    """
    Edit a VM information in Guacamole
    Args:
        name (string): Name of the VM
        port (int): Port of the VM
    Returns:
        bool: True if the Guacamole connection has been edited, False otherwise
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole')
    try:
        identifier = guacapi.get_connection_by_name(name)['identifier']
        port = getVMInfo(name)['port_vnc']

        payload = {
            "parentIdentifier": "ROOT",
            "protocol": "vnc",
            "name": name,
            "activeConnections": 0,
            "attributes":{"max-connections":"","max-connections-per-user":""},
            "parameters": {
                "port": port,
                "enable-menu-animations":"true",
                "enable-desktop-composition":"true",
                "hostname":"127.0.0.1",
                "color-depth":"32",
                "enable-font-smoothing":"true",
                "ignore-cert":"true",
                "enable-drive":"true",
                "enable-full-window-drag":"true",
                "security":"any",
                "password":"",
                "enable-wallpaper":"true",
                "create-drive-path":"true",
                "enable-theming":"true",
                "console":"true",
            }
        }

        guacapi.edit_connection(identifier, payload)

        return True

    except Exception as e:
        logger.error("An error occurred when modifying the Guacamole connection, Error message: '%s'", e)
        return False

def editNameGuac(old_name, new_name):
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole')

    try:
        identifier = guacapi.get_connection_by_name(old_name)['identifier']
        port = getVMInfo(new_name)['port_vnc']

        payload = {
            "parentIdentifier": "ROOT",
            "protocol": "vnc",
            "name": new_name,
            "activeConnections": 0,
            "attributes":{"max-connections":"","max-connections-per-user":""},
            "parameters": {
                "port": port,
                "enable-menu-animations":"true",
                "enable-desktop-composition":"true",
                "hostname":"127.0.0.1",
                "color-depth":"32",
                "enable-font-smoothing":"true",
                "ignore-cert":"true",
                "enable-drive":"true",
                "enable-full-window-drag":"true",
                "security":"any",
                "password":"",
                "enable-wallpaper":"true",
                "create-drive-path":"true",
                "enable-theming":"true",
                "console":"true",
            }
        }

        guacapi.edit_connection(identifier, payload)

        return True

    except Exception as e:
        logger.error("An error occurred when modifying the Guacamole connection, Error message: '%s'", e)
        return False


def getVMs():
    """
    This function allows you to recover all VMS in the database
    """
    return TestenvDatabase().getVMs()

def getVMByName(vm_name):
    """
    This function allows you to recover a VM in the database
    """
    return TestenvDatabase().getVMByName(vm_name)

def checkExistVM(name):
    """
    This function allows you to check if a VM exists in the database
    """
    return TestenvDatabase().checkExistVM(name)

def dictGuac(name):
    """
    This function allows you to recover the information of a VM in Guacamole
    Args:
        name (string): Name of the VM
    Returns:
        dict: Dictionary containing the information of the VM
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole')

    identifier = guacapi.get_connection_by_name(name)['identifier']
    protocol = guacapi.get_connection_full(identifier)['protocol']
    port = getVMInfo(name)['port_vnc']
    machine_name = guacapi.get_connection_full(identifier)['name']
    id_machines = TestenvDatabase().getVMByName(machine_name)['id']

    dict = {
        "idguacamole": identifier,
        "protocol": protocol,
        "port": port,
        "machine_name": machine_name,
        "id_machines": id_machines
    }

    return dict

def updateVMResources(vm_name, new_ram, new_cpu):
    """
    Update the resources (RAM and CPU) of a virtual machine
    Args:
        vm_name (string): Name of the virtual machine
        new_ram (int): New RAM
        new_cpu (int): New CPU
    Returns:
        bool: True if the resources have been updated, False otherwise
    """
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(vm_name)

        if domain is None:
            logger.error("Area '%s' not found", vm_name)
            return False

        # Check if the machine is lit and, in this case, turn it off
        if domain.isActive():
            try:
                domain.destroy()
                logger.debug("Arrêt du domaine '%s'", vm_name)
            except Exception as e:
                logger.error("Échec de l'arrêt du domaine '%s'", vm_name)
                return False

        try:
            # Get the Virtual Machine XML
            xml = domain.XMLDesc()

            # Patrix the XML to update the value of the maxmemory
            root = ET.fromstring(xml)
            memory_element = root.find(".//memory")
            memory_element.text = str(new_ram)  # Turn into kilo-ocets

            # Update the XML with the new value of the Maxmemory
            new_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")

            # Redefine the configuration of the virtual machine with the new XML
            domain.undefine()
            conn.defineXML(new_xml)

            logger.debug("The configuration of the virtual machine '%s' has been successfully redefined", vm_name)
        except Exception as e:
            logger.error("Failure to update the RAM of the virtual machine '%s', Error message: '%s'", vm_name, e)
            return False

        try:
        # Update the CPU
            domain.setVcpusFlags(new_cpu, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            logger.debug("The number of CPUS of the virtual machine '%s' has been successfully updated", vm_name)

        except Exception as e:
            logger.error("Failure to update the CPU of the virtual machine '%s', Error message: '%s'", vm_name, e)
            return False

        logger.debug("The resources of the virtual machine '%s' have been successfully updated. RAM : %d Mo, CPU : %d", vm_name, new_ram, new_cpu)

        infoVM = getVMInfo(vm_name)
        vm_dict = {
            "name": infoVM['name'],
            "cpu": infoVM['currentCpu'],
            "memory": str(int(infoVM['maxMemory'])),
        }

        if not TestenvDatabase().updateRessourcesVM(vm_dict):
            logger.error("Failure to update the resources of the virtual machine '%s' in the database ", vm_name)
            return False
        else:
            logger.debug("The resources of the virtual machine '%s' have been successfully updated in the database", vm_name)

        # # On redémarre la machine
        if not start_vm(vm_name):
            logger.error("Machine start failure '%s'", vm_name)
            return False
        else:
            logger.debug("The machine '%s' was successfully started", vm_name)
        return True

    except Exception as e:
        logger.error("Failure to update the resources of the virtual machine '%s', Error message: '%s'", vm_name, e)
        return False
