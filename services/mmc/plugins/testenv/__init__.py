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
import libvirt
import time
import json
import os


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
    This function allows creating a VM by sending a POST request to the URL
        :param username: Jenkins username
        :param token: Jenkins token
        :param url: Jenkins URL
        :return: True if the VM has been created, False otherwise
    """
    parsed_url = six.moves.urllib.parse.urlparse(url)
    crumb_issuer = six.moves.urllib.parse.urlunparse((parsed_url.scheme,
                                                      parsed_url.netloc,
                                                      'crumbIssuer/api/json',
                                                      '',
                                                      '',
                                                      ''))

    session = requests.session()

    auth = requests.auth.HTTPBasicAuth(username, token)

    result = session.get(crumb_issuer, auth=auth)

    if result.status_code == 200 and result.text:
        try:
            json_data = result.json()
            crumb = {json_data['crumbRequestField']: json_data['crumb']}

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            headers.update(crumb)
            result = session.post(url, headers=headers, auth=auth)

            return True

        except Exception as e:
            logger.error("Response content is not valid JSON: '%s'", result.text)
            return False
    else:
        return False

def checkStatusJobPending(job_name):
    """
    This function checks the status of a Jenkins job to see if it's currently running or not
        :param job_name: Name of the Jenkins job
        :return: True if the job is running, False otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url

    jenkins = Jenkins(jenkins_url, username=username, password=token)

    job = jenkins[job_name]

    time.sleep(15)
    last_build = job.get_last_build()

    if last_build.is_running():
        console_output = last_build.get_console()
        return True, console_output
    else:
        console_output = last_build.get_console()
        return False, console_output

def getLastBuildOutput(job_name):
    """
    This function retrieves the console output from the last execution of a Jenkins job
        :param job_name: Name of the Jenkins job
        :return: Dictionary containing the console output
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url

    jenkins = Jenkins(jenkins_url, username=username, password=token)

    job = jenkins[job_name]

    last_build = job.get_last_build()
    console_output = last_build.get_console()

    result = {}

    for ligne in console_output.split("\n"):
        if ":" in ligne:
            cle, valeur = ligne.split(":", 1)
            result[cle.strip()] = valeur.strip()

    return result, True

def get_status_description(status_code):
    """
    Recover the description of a status code
        :param status_code: Status code
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
        :return: List of virtual machines
    """
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.listAllDomains(0)

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
        logger.error("Failure to connect to the hypervisor! '%s'", e)
        return False

def getVMInfo(vm_name):
    """
    Get information about a virtual machine
        :param vm_name: Name of the virtual machine
        :return: Dictionary containing the information
    """
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
            "id": root.get("id", "No ID"),
            "name": root.findtext("name", "No name"),
            "uuid": root.findtext("uuid", "No uuid"),
            "plateform": root.findtext("os/type", "No OS type"),
            "architecture": root.find("os/type").attrib.get("arch", "No architecture"),
            "currentCpu": info[3],
            "maxCpu": root.findtext("vcpu", "No CPU"),
            "maxMemory": int(root.findtext("memory", "No memory")) / 1024,
            "currentMemory": root.findtext("currentMemory", "No data"),
            "model": root.find("os/type").attrib.get("machine", "No model"),
            "mac_address": root.find("devices/interface/mac").attrib.get("address", "No mac address"),
            "state": get_status_description(domain.state()[0]),
            "persistent": root.findtext("on_poweroff", "No data"),
            "port_vnc": root.find("devices/graphics").get("port", "No VNC port")
        }

        return domain_info

    except Exception as e:
        logger.error("Failure to connect to the hypervisor!")
        return False

def editNameVM(old_name, new_name):
    """
    Rename a virtual machine
        : param old_name: old machine name
        : Param New_Name: New name of the machine
        : Return: True if the machine has been renamed, false otherwise
    """
    infoVM = getVMInfo(old_name)
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(old_name)

        if domain is None:
            logger.error("Area '%s' not found", old_name)
            return False

        if domain.isActive():
            try:
                domain.destroy()
            except Exception as e:
                logger.error("Domain failure failure '%s'", old_name)
                return False

        try:
            domain.rename(new_name)

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

            xml = ET.tostring(root).decode("utf-8")
            conn.defineXML(xml)

            image_path = "/var/lib/libvirt/images/{}.qcow2".format(old_name)
            new_image_path = "/var/lib/libvirt/images/{}.qcow2".format(new_name)
            if not os.path.exists(image_path):
                logger.error("The '%s' file does not exist", image_path)
                return False
            else:
                os.rename(image_path, new_image_path)
                logger.debug("The '%s' file was renamed in '%s'", image_path, new_image_path)

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

            if not start_vm(new_name):
                logger.error("Machine starting failure '%s'", new_name)
                return False
            else:
                logger.debug("The machine '%s' was successfully started", new_name)

            logger.debug("The machine '%s' was renamed in'%s'", old_name, new_name)
            return True

        except Exception as e:
            logger.error("Domaine renamed failure '%s'\nError message: '%s'", old_name, e)
            return False

    except Exception as e:
        logger.error("Connection to hypervisor connection !")
        return False


def create_vm(name, desc, ram, cpu, disk_size, os):
    """
    This function allows you to create a VM by sending a post request to the URL.
        :param name: Name of the VM
        :param desc: Description of the VM
        :param ram: Amount of RAM (in MB)
        :param cpu: Number of CPUs
        :param disk_size: Size of the disk (in GB)
        :param os: Operating system
        :return: True if the VM has been created, False otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'create-vm'

    try:
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={token}&NAME={name}&DESC={desc}&RAM={ram}&CPUS={cpu}&DISK_SIZE={disk_size}&OS={os}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=name, desc=desc, ram=ram, cpu=cpu, disk_size=disk_size, os=os)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("The virtual machine '%s' was successfully created !", name)

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
                logger.error("The job '%s' is not running.", job_name)
                return False
        else:
            logger.error("Failure to create the job '%s'.", job_name)
            return False

    except Exception as e:
        logger.error("Failure to build the Jenkins URL: '%s'", e)
        return False

def delete_vm(vm_name):
    """
    This function makes it possible to delete a VM by sending a post request to the URL.
        :param vm_name: Name of the VM
        :return: True if the VM has been deleted, False otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'delete-vm'

    try:
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={token}&NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("The virtual machine '%s' is being removed.", vm_name)
                if TestenvDatabase().deleteVM(vm_name):
                    logger.debug("The virtual machine '%s' has been successfully removed.", vm_name)
                    return True
                else:
                    logger.error("Failure to remove the virtual machine '%s' in the database.", vm_name)
                    return False
            else:
                logger.error("The virtual machine '%s' is not being suppressed.", vm_name)
                return False
        else:
            logger.error("Failure to create the job.")
            return False

    except Exception as e:
        logger.error("Failure to build the Jenkins URL: '%s' ", e)
        return False

def start_vm(vm_name):
    """
    This function allows you to turn on a VM by sending a Post request to the URL
        :param vm_name: Name of the VM
        :return: True if the VM has been turned on, False otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'start-vm'

    try:
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={job_name}&VM_NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("The virtual machine '%s' is being switched on.", vm_name)

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
        logger.error("Failure to build the Jenkins URL: '%s' ", e)
        return False

def forceshutdown_vm(vm_name):
    """
    This function allows you to force the extinction of a VM by sending a post request to the URL.
        :param vm_name: Name of the VM
        :return: True if the VM has been turned off, False otherwise
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'forceshut-vm'

    try:
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={job_name}&VM_NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.debug("The virtual machine '%s' is being extinction.", vm_name)
                try:
                    logger.debug("Database update: 'Shutoff' status for the virtual machine '%s'.", vm_name)
                    if TestenvDatabase().updateStatutVM(vm_name, "Shutoff"):
                        logger.debug("Updating the database successfully performed for the virtual machine '%s'.", vm_name)
                        return True
                    else:
                        logger.error("Failure to update the database for the virtual machine '%s'.", vm_name)
                        return False
                except Exception as e:
                    logger.error("Error when updating the database: '%s'", e)
                    return False
            else:
                logger.error("The virtual machine '%s' is not being extinction.", vm_name)
                return False
        else:
            logger.error("Failure to create the job.")
            return False

    except Exception as e:
        logger.error("Failure to build the Jenkins URL: '%s'", e)
        return False

def shutdown_vm(url):
    """
    This function makes it possible to extinguish a VM to envoanr a post post to the url
        :param url: URL of the VM
        :return: True if the VM has been turned off, False otherwise
    """
    try:
        username = config.jenkins_username
        token = config.jenkins_token
        jenkins_url = config.jenkins_url + url
        job_name = 'forceshut-vm'

        buildJenkinsUrl(username, token, jenkins_url)
        logger.debug("Successful virtual machine with the URL: '%s'", url)
        return True

    except requests.exceptions.RequestException as e:
        logger.error("An error occurred during the extinction of the virtual machine: '%s'", e)
        return False


def createConnectionGuac(name):
    """
    This function allows you to create a Guacamole connection.
        :param name: Name of the VM
        :return: True if the connection has been created, False otherwise
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')
    try:
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
        logger.error("Failure to create the Guacamole connection: '%s'", e)
        return False

def urlGuac(name):
    """
    This function allows you to recover the Guacamole URL from a connection
        :param name: Name of the VM
        :return: URL if the connection exists, False otherwise
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')
    try:
        identifier = guacapi.get_connection_by_name(name)['identifier']

        token_hex = binascii.hexlify(identifier) + '00' + binascii.hexlify('c') + '00' + binascii.hexlify('mysql')
        token = base64.b64encode(binascii.unhexlify(token_hex))

        url = config.guacamole_url_client + token + '?username=' + config.guacamole_username + '&password=' + config.guacamole_password

        return url

    except Exception as e:
        logger.error("Failed to recover the Guacamole URL: '%s'", e)
        return False

def deleteGuac(name):
    """
    This function allows you to delete a Guacamole connection
        :param name: Name of the VM
        :return: True if the connection has been deleted, False otherwise
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')
    try:
        identifier = guacapi.get_connection_by_name(name)['identifier']

        guacapi.delete_connection(identifier)
        return True

    except Exception as e:
        return False

def updateGuac(name, port):
    """
    Edit a VM information in Guacamole
        :param name: Name of the VM
        :param port: VNC port
        :return: True if the information has been edited, False otherwise
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')
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
        logger.error("An error occurred when modifying the Guacamole connection: '%s'", e)
        return False

def editNameGuac(old_name, new_name):
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')

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
        logger.error("An error occurred when modifying the Guacamole connection: '%s'", e)
        return False


def getVMs():
    """
    This function allows you to recover all VMS in the database
        :return: List of VMs
    """
    return TestenvDatabase().getVMs()

def getVMByName(vm_name):
    """
    This function allows you to recover a VM in the database
        :param vm_name: Name of the VM
        :return: VM
    """
    return TestenvDatabase().getVMByName(vm_name)

def checkExistVM(name):
    """
    This function allows you to check if a VM exists in the database
        :param name: Name of the VM
        :return: True if the VM exists, False otherwise
    """
    return TestenvDatabase().checkExistVM(name)

def dictGuac(name):
    """
    This function allows you to recover the information of a VM in Guacamole
        :param name: Name of the VM
        :return: Dictionary containing the information
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')

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
        :param vm_name: Name of the VM
        :param new_ram: New RAM (in MB)
        :param new_cpu: New CPU
        :return: True if the resources have been updated, False otherwise
    """
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(vm_name)

        if domain is None:
            logger.error("Area '%s' not found", vm_name)
            return False

        if domain.isActive():
            try:
                domain.destroy()
                logger.debug("Domain stop '%s'", vm_name)
            except Exception as e:
                logger.error("Domain failure failure '%s'", vm_name)
                return False

        try:
            xml = domain.XMLDesc()
            root = ET.fromstring(xml)
            memory_element = root.find(".//memory")
            memory_element.text = str(new_ram)

            new_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")

            domain.undefine()
            conn.defineXML(new_xml)

            logger.debug("The configuration of the virtual machine '%s' has been successfully redefined", vm_name)
        except Exception as e:
            logger.error("Failure to update the RAM of the virtual machine '%s'", vm_name)
            return False

        try:
            domain.setVcpusFlags(new_cpu, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            logger.debug("The number of CPUS of the virtual machine '%s' has been successfully updated", vm_name)

        except Exception as e:
            logger.error("Failure to update the CPU of the virtual machine '%s'", vm_name)
            return False

        logger.debug("The resources of the virtual machine '%s' have been successfully updated.RAM: %d Mo, CPU : %d", vm_name, new_ram, new_cpu)

        infoVM = getVMInfo(vm_name)
        vm_dict = {
            "name": infoVM['name'],
            "cpu": infoVM['currentCpu'],
            "memory": str(int(infoVM['maxMemory'])),
        }

        if not TestenvDatabase().updateRessourcesVM(vm_dict):
            logger.error("Failure of updating the resources of the virtual machine '%s' in the database", vm_name)
            return False
        else:
            logger.debug("The resources of the virtual machine '%s' have been successfully updated in the database", vm_name)

        if not start_vm(vm_name):
            logger.error("Machine start -up failure '%s'", vm_name)
            return False
        else:
            logger.debug("The machine '%s' was successfully started", vm_name)
        return True

    except Exception as e:
        logger.error("Failure to update the resources of the virtual machine '%s'. Error : '%s'", vm_name, str(e))
        return False
