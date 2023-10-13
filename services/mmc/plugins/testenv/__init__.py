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
# Au cas où on souhaite appeler des configs d'autres modules
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.testenv.config import TestenvConfig

# import pour la database
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


## JENKINS BUILD ##
def buildJenkinsUrl(username, token, url):
    """
    Cette fonction permet de créer une VM en envoyant une requête POST à l'URL.
    Parameters:
        url (str): URL de la requête
        username (str): Nom d'utilisateur Jenkins
        token (str): Mot de passe Jenkins

    Return (bool): True si la requête POST a été envoyée, False sinon
    """
    # Construire l'URL du crumb issu de Jenkins
    parsed_url = six.moves.urllib.parse.urlparse(url)
    crumb_issuer = six.moves.urllib.parse.urlunparse((parsed_url.scheme,
                                                      parsed_url.netloc,
                                                      'crumbIssuer/api/json',
                                                      '',
                                                      '',
                                                      ''))

    # Création d'une session pour les requêtes
    session = requests.session()

    # Récupérer le crumb de Jenkins
    auth = requests.auth.HTTPBasicAuth(username, token)

    # Je récupère le crumb(ma miette)
    result = session.get(crumb_issuer, auth=auth)

    # Vérifier le contenu de la réponse
    if result.status_code == 200 and result.text:
        try:
            # Convertir la réponse JSON en un dictionnaire Python et récupérer la valeur du crumb
            json_data = result.json()
            crumb = {json_data['crumbRequestField']: json_data['crumb']}

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            headers.update(crumb)
            result = session.post(url, headers=headers, auth=auth)

            return True

        except Exception as e:
            logger.error("Response content is not valid JSON: %s", result.text)
            return False
    else:
        return False

def checkStatusJobPending(job_name):
    """
    Cette fonction permet de vérifier le statut d'un job Jenkins s'il est en cours ou non.
    Parameters:
        job_name (str): Nom du job Jenkins
    Return (bool, str): Un tuple (en_cours, console_output), avec en_cours=True si le job est en cours d'exécution, False sinon, et console_output la sortie de la console du dernier build si celui-ci est terminé.
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url

    jenkins = Jenkins(jenkins_url, username=username, password=token)

    # Récupérer le job Jenkins
    job = jenkins[job_name]

    # Récupérer le dernier build du job
    # Temporisation pour laisser le temps à Jenkins de créer le build
    time.sleep(15)
    last_build = job.get_last_build()

    # Vérifier si le build est en cours d'exécution
    if last_build.is_running():
        console_output = last_build.get_console()
        return True, console_output
    else:
        console_output = last_build.get_console()
        return False, console_output

def getLastBuildOutput(job_name):
    """
    Cette fonction permet de récupérer la sortie de la console de la dernière exécution d'un job Jenkins.
    Parameters:
        job_name (str): Nom du job Jenkins
    Return (str): La sortie de la console du dernier build
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url

    jenkins = Jenkins(jenkins_url, username=username, password=token)

    # Récupérer le job Jenkins
    job = jenkins[job_name]

    # Récupérer le dernier build du job
    last_build = job.get_last_build()
    console_output = last_build.get_console()

    result = {}

    # Parcourir chaque ligne de la sortie de la console
    for ligne in console_output.split("\n"):
        # Vérifier si la ligne contient une clé et une valeur
        if ":" in ligne:
            # Séparer la clé et la valeur en utilisant le premier ":" trouvé
            cle, valeur = ligne.split(":", 1)
            # Ajouter la clé et la valeur à result
            result[cle.strip()] = valeur.strip()

    return result, True
## ./JENKINS BUILD ##


## Utilisation API LIBVIRT ##
def get_status_description(status_code):
    """
        Récupérer la description d'un code de status
        :param status_code: Code de status
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
    Récupérer la liste des machines virtuelles
    return: id, name, status
    """
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.listAllDomains(0)
        logger.info("Connexion à l'hyperviseur réussie !")

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
        logger.error("Échec de la connexion à l'hyperviseur ! %s", e)
        return False

def getVMInfo(vm_name):
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(vm_name)

        if domain is None:
            logger.error("Domaine '%s' non trouvé", vm_name)
            return ""

        xml = domain.XMLDesc()
        info = domain.info()

        root = ET.fromstring(xml)
        domain_info = {
            "id": root.get("id", "Pas d'ID"),  # ID de la VM
            "name": root.findtext("name", "Pas de nom"),  # Nom de la VM
            "uuid": root.findtext("uuid", "Pas d'UUID"),  # UUID de la VM
            "plateform": root.findtext("os/type", "Pas de type d'OS"),  # Type d'OS
            "architecture": root.find("os/type").attrib.get("arch", "Pas d'architecture"), # Architecture de la VM
            "currentCpu": info[3], # Nombre de CPU actuel
            "maxCpu": root.findtext("vcpu", "Pas de CPU"),  # Nombre de CPU Maximum
            "maxMemory": int(root.findtext("memory", "Pas de mémoire")) / 1024,  # Mémoire totale (en MB)
            "currentMemory": root.findtext("currentMemory", "Pas de donnée"),  # Mémoire utilisée
            "model": root.find("os/type").attrib.get("machine", "Pas de modèle"), # Modèle de la VM
            "mac_address": root.find("devices/interface/mac").attrib.get("address", "Pas d'adresse MAC"), # Adresse MAC
            "state": get_status_description(domain.state()[0]),  # Récupérer l'état avec la fonction auxiliaire
            "persistent": root.findtext("on_poweroff", "Pas de donnée"),  # Persistant
            "port_vnc": root.find("devices/graphics").get("port", "Pas de port VNC")
        }

        # logger.info("===== Informations de la VM =====")
        # logger.info(domain_info)

        return domain_info

    except Exception as e:
        logger.error("Échec de la connexion à l'hyperviseur")
        return False

# TO DO
def editNameVM(old_name, new_name):
    """
    Renommer une machine virtuelle
    :param old_name: Ancien nom de la machine
    :param new_name: Nouveau nom de la machine
    :return: True si la machine a été renommée, False sinon
    """
    infoVM = getVMInfo(old_name)
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(old_name)

        if domain is None:
            logger.error("Domaine '%s' non trouvé", old_name)
            return False

        # Vérifier si la machine est allumée et, dans ce cas, l'éteindre
        if domain.isActive():
            try:
                domain.destroy()
                logger.info("Arrêt du domaine '%s'", old_name)
            except Exception as e:
                logger.error("Échec de l'arrêt du domaine '%s'", old_name)
                return False

        # Renommer la machine
        try:
            domain.rename(new_name)
            logger.info("Le domaine '%s' a été renommé en '%s'", old_name, new_name)

            # Mettre à jour le chemin source du disque virtuel
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
                        logger.info("Le chemin source du disque a été mis à jour vers '%s'", new_path)

            xml = ET.tostring(root).decode("utf-8")
            conn.defineXML(xml)

            # Mettre à jour le fichier
            image_path = "/var/lib/libvirt/images/{}.qcow2".format(old_name)
            new_image_path = "/var/lib/libvirt/images/{}.qcow2".format(new_name)
            if not os.path.exists(image_path):
                logger.error("Le fichier '%s' n'existe pas", image_path)
                return False
            else:
                os.rename(image_path, new_image_path)
                logger.info("Le fichier '%s' a été renommé en '%s'", image_path, new_image_path)


            # Mettre à jour la RAM si nécessaire
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

            # Mettre à jour le nom dans la base de données
            if not TestenvDatabase().updateVM(vm_dict):
                logger.error("Échec de la mise à jour du nom dans la base de données")
                return False
            else:
                logger.info("Le nom de la machine a été mis à jour dans la base de données")

            # Mettre à jour le nom dans Guacamole
            if not editNameGuac(old_name, new_name):
                logger.error("Échec de la mise à jour du nom dans Guacamole")
                return False
            else:
                logger.info("Le nom de la machine a été mis à jour dans Guacamole")

            # Démarrer la machine avec le nouveau nom
            if not start_vm(new_name):
                logger.error("Échec du démarrage de la machine '%s'", new_name)
                return False
            else:
                logger.info("La machine '%s' a été démarrée avec succès", new_name)

            logger.info("La machine '%s' a été renommée en '%s'", old_name, new_name)
            return True

        except Exception as e:
            logger.error("Échec du renommage du domaine '%s'\nMessage d'erreur: %s", old_name, e)
            logger.error("Échec de la connexion à l'hyperviseur")
            return False

    except Exception as e:
        logger.error("Échec de la connexion à l'hyperviseur")
        return False

# ./TO DO
## ./Utilisation API LIBVIRT ##


## Gestions des VMs ##
def create_vm(name, desc, ram, cpu, disk_size, os):
    """
    Cette fonction permet de créer une VM en envoyant une requête POST à l'URL.
    Parameters:
        name (str): Nom de la VM
        desc (str): Description de la VM
        ram (str): RAM de la VM
        cpu (str): Nombre de CPU de la VM
        disk_size (str): Taille du disque de la VM
        os (str): Système d'exploitation de la VM
    Return (bool): True si la VM a été créée, False sinon
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'create-vm'

    try:
        # Construire l'URL pour créer une VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={token}&NAME={name}&DESC={desc}&RAM={ram}&CPUS={cpu}&DISK_SIZE={disk_size}&OS={os}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=name, desc=desc, ram=ram, cpu=cpu, disk_size=disk_size, os=os)

        logger.info("===== URL Job Create VM =====")
        logger.info(url)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.info("La Machine Virtuelle %s a été créée avec succès.", name)

                dict = getVMInfo(name)

                if createConnectionGuac(name):
                    logger.info("Connexion Guacamole créée avec succès")

                    if TestenvDatabase().createVM(dict):
                        logger.info("Mise à jour de la base de données réussie")
                        dict_guac = dictGuac(name)

                        if TestenvDatabase().setInfoGuac(dict_guac):
                            logger.info("Mise à jour de la base de données réussie")
                            return True

                        else:
                            logger.error("Échec de la mise à jour de la base de données Guac")
                            return False
                    else:
                        logger.error("Échec de la mise à jour de la base de données Machines")
                        return False
                else:
                    logger.error("Échec de la création de la connexion Guacamole")
                    return False
            else:
                logger.info("Le job %s n'est pas en cours d'exécution.", job_name)
                return False
        else:
            logger.error("Échec de la création du job %s.", job_name)
            return False

    except Exception as e:
        logger.error("Échec de la construction de l'URL Jenkins : %s", e)
        return False

def delete_vm(vm_name):
    """
    Cette fonction permet de supprimer une VM en envoyant une requête POST à l'URL.
    Parameters:
        vm_name (str): Nom de la VM
    Return (bool): True si la VM a été supprimée, False sinon
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'delete-vm'

    try:
        # Construire l'URL pour supprimer une VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={token}&NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        logger.info("URL : %s", url)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.info("La machine virtuelle %s est en cours de suppression.", vm_name)
                if TestenvDatabase().deleteVM(vm_name):
                    logger.info("La machine virtuelle %s a été supprimée avec succès.", vm_name)
                    return True
                else:
                    logger.error("Échec de la suppression de la machine virtuelle %s dans la base de données.", vm_name)
                    return False
            else:
                logger.error("La machine virtuelle %s n'est pas en cours de suppression.", vm_name)
                return False
        else:
            logger.error("Échec de la création du job.")
            return False

    except Exception as e:
        logger.error("Échec de la construction de l'URL Jenkins : %s", e)
        return False

def start_vm(vm_name):
    """
    Cette fonction permet d'allumer une VM en envoyant une requête POST à l'URL.
    Parameters:
        vm_name (str): Nom de la VM
    Return (bool, bool): Un tuple (allumée, mise_à_jour) avec allumée=True si la VM est en cours d'allumage, False sinon,
                        et mise_à_jour=True si la mise à jour du statut dans la base de données est réussie, False sinon.
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'start-vm'

    try:
        # Construire l'URL pour allumer une VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={job_name}&VM_NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        logger.info("URL : %s", url)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.info("La machine virtuelle %s est en cours d'allumage.", vm_name)

                dict_guac = dictGuac(vm_name)
                logger.info("===== Dict Guac =====")
                logger.info(dict_guac)

                if TestenvDatabase().updateStatutVM(vm_name, "Running") and TestenvDatabase().updateInfoGuac(dict_guac):
                    logger.info("La machine virtuelle %s est mise à jour avec le statut 'Running' dans la base de données.", vm_name)

                    if updateGuac(dict_guac['machine_name'], dict_guac['port']):
                        logger.info("La machine virtuelle %s est mise à jour avec le statut 'Running' dans la base de données.", vm_name)
                        return True
                    else:
                        logger.error("Échec de la mise à jour de la machine virtuelle %s dans Guacamole.", vm_name)
                        return False
                else:
                    logger.error("Échec de la mise à jour du statut de la machine virtuelle %s dans la base de données.", vm_name)
                    return False
            else:
                logger.error("La machine virtuelle %s n'est pas en cours d'allumage.", vm_name)
                return False
        else:
            logger.error("Échec de la création du job.")
            return False

    except Exception as e:
        logger.error("Échec de la construction de l'URL Jenkins : %s", e)
        return False

def forceshutdown_vm(vm_name):
    """
    Cette fonction permet de forcer l'extinction d'une VM en envoyant une requête POST à l'URL.
    Parameters:
        vm_name (str): Nom de la VM
    Return (bool, bool): Un tuple (en_cours, mise_à_jour) avec en_cours=True si la VM est en cours d'extinction,
                        False sinon, et mise_à_jour=True si la mise à jour du statut dans la base de données
                        est réussie, False sinon.
    """
    username = config.jenkins_username
    token = config.jenkins_token
    jenkins_url = config.jenkins_url
    job_name = 'forceshut-vm'

    try:
        # Construire l'URL pour forcer l'extinction d'une VM
        url = "{jenkins_url}/job/{job_name}/buildWithParameters?token={job_name}&VM_NAME={name}".format(
            jenkins_url=jenkins_url, job_name=job_name, token=job_name, name=vm_name)

        logger.info("URL : %s", url)

        if buildJenkinsUrl(username, token, url):
            if checkStatusJobPending(job_name):
                logger.info("La machine virtuelle %s est en cours d'extinction.", vm_name)
                try:
                    logger.info("Mise à jour de la base de données : statut 'Shutoff' pour la machine virtuelle %s.", vm_name)
                    if TestenvDatabase().updateStatutVM(vm_name, "Shutoff"):
                        logger.info("Mise à jour de la base de données effectuée avec succès pour la machine virtuelle %s.", vm_name)
                        return True
                    else:
                        logger.error("Échec de la mise à jour de la base de données pour la machine virtuelle %s.", vm_name)
                        return False
                except Exception as e:
                    logger.error("Erreur lors de la mise à jour de la base de données : %s", e)
                    return False
            else:
                logger.error("La machine virtuelle %s n'est pas en cours d'extinction.", vm_name)
                return False
        else:
            logger.error("Échec de la création du job.")
            return False

    except Exception as e:
        logger.error("Échec de la construction de l'URL Jenkins : %s", e)
        return False

# TO DO
def shutdown_vm(url):
    """
        Cette fonction permet d'éteindre une VM à en envoyanr une requête POST à l'URL
    """
    try:
        # TO DO - A mettre dans un fichier de configuration
        username = 'Administrateur'
        password = '114adfa602a4ffedadc6248aef25b9d173'
        url2 = 'http://lma.siveo.net:8080/job/shutdown-vm/buildWithParameters?token=shutdown-vm&VM_NAME=' + url
        # Utilisation de la fonction buildJenkinsUrl pour créer la VM
        buildJenkinsUrl(username, password, url2)
        # L'URL de la VM créée est retournée
        logger.info("Machine virtuelle éteinte avec succès avec l'url : %s", url)
        return True

    except requests.exceptions.RequestException as e:
        # LOG de l'erreur s'il y a
        logger.error("Une erreur s'est produite lors de l'extinction de la machine virtuelle: %s", e)
        return False
## ./Gestion des VMs ##


## GUACAMOLE ##
def createConnectionGuac(name):
    """
    Cette fonction permet de créer une connexion Guacamole.
    Parameters:
        name (str): Nom de la connexion Guacamole
    Return (bool): True si la connexion a été créée, False sinon
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')
    try:
    # Port en automatique lors de la création de la VM du coup une fois la VM créee on récupère le port pour le mettre dans la connexion
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
        logger.error("Échec de la création de la connexion Guacamole : %s", e)
        return False

def urlGuac(name):
    """
    Cette fonction permet de récupérer l'URL Guacamole d'une connexion.
    """
    guacapi = Guacamole(config.guacamole_url, config.guacamole_username, config.guacamole_password, None, 'http', '/guacamole/')
    try:
        identifier = guacapi.get_connection_by_name(name)['identifier']

        token_hex = binascii.hexlify(identifier) + '00' + binascii.hexlify('c') + '00' + binascii.hexlify('mysql')
        token = base64.b64encode(binascii.unhexlify(token_hex))

        url = 'http://lma.siveo.net/guacamole/#/client/' + token + '?username=' + config.guacamole_username + '&password=' + config.guacamole_password

        return url

    except Exception as e:
        logger.error("Échec de la récupération de l'URL Guacamole : %s", e)
        return False

def deleteGuac(name):
    """
    Cette fonction permet de supprimer une connexion Guacamole.
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
    Modifier les informations d'une VM dans Guacamole
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
        logger.error("Une erreur s'est produite lors de la modification de la connexion Guacamole: %s", e)
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
        logger.error("Une erreur s'est produite lors de la modification de la connexion Guacamole: %s", e)
        return False

## ./GUACAMOLE ##


## BdD ##
def getVMs():
    """
    Cette fonction permet de récupérer toutes les VMs dans la base de données.
    """
    return TestenvDatabase().getVMs()

def getVMByName(vm_name):
    """
    Cette fonction permet de récupérer une VM dans la base de données.
    """
    return TestenvDatabase().getVMByName(vm_name)

def checkExistVM(name):
    """
    Cette fonction permet de vérifier si une VM existe dans la base de données.
    """
    return TestenvDatabase().checkExistVM(name)

def dictGuac(name):
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

    # return TestenvDatabase().setInfoGuac(dict)
    return dict
## ./BdD ##


## TESTS ##
def updateVMResources(vm_name, new_ram, new_cpu):
    """
    Mettre à jour les ressources (RAM et CPU) d'une machine virtuelle.
    :param vm_name: Nom de la machine virtuelle
    :param new_ram: Nouvelle quantité de RAM (en Mo)
    :param new_cpu: Nouveau nombre de CPUs
    :return: True si la mise à jour est réussie, False sinon
    """

    logger.info("===== Mise à jour des ressources de la machine virtuelle '%s' =====", vm_name)
    # logger.info("Nouvelle RAM : '%s' Mo", new_ram)
    # logger.info("Nouveau CPU : '%s'", new_cpu)
    try:
        conn = libvirt.open("qemu:///system")
        domain = conn.lookupByName(vm_name)

        if domain is None:
            logger.error("Domaine '%s' non trouvé", vm_name)
            return False

        # Vérifier si la machine est allumée et, dans ce cas, l'éteindre
        if domain.isActive():
            try:
                domain.destroy()
                logger.info("Arrêt du domaine '%s'", vm_name)
            except Exception as e:
                logger.error("Échec de l'arrêt du domaine '%s'", vm_name)
                return False

        try:
            # Obtenir le XML de la machine virtuelle
            xml = domain.XMLDesc()

            # Parser le XML pour mettre à jour la valeur du maxMemory
            root = ET.fromstring(xml)
            memory_element = root.find(".//memory")
            memory_element.text = str(new_ram)  # Convertir en kilo-octets

            # Mettre à jour le XML avec la nouvelle valeur du maxMemory
            new_xml = ET.tostring(root, encoding="utf-8").decode("utf-8")

            # Redéfinir la configuration de la machine virtuelle avec le nouveau XML
            domain.undefine()
            conn.defineXML(new_xml)

            logger.info("La configuration de la machine virtuelle '%s' a été redéfinie avec succès", vm_name)
        except Exception as e:
            logger.error("Échec de la mise à jour de la RAM de la machine virtuelle '%s'", vm_name)
            return False

        try:
        # Mettre à jour le CPU
            domain.setVcpusFlags(new_cpu, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
            logger.info("Le nombre de CPUs de la machine virtuelle '%s' a été mis à jour avec succès", vm_name)

        except Exception as e:
            logger.error("Échec de la mise à jour du CPU de la machine virtuelle '%s'", vm_name)
            return False

        logger.info("Les ressources de la machine virtuelle '%s' ont été mises à jour avec succès. RAM : %d Mo, CPU : %d", vm_name, new_ram, new_cpu)

        # Je met à jour la base de données
        infoVM = getVMInfo(vm_name)
        vm_dict = {
            "name": infoVM['name'],
            "cpu": infoVM['currentCpu'],
            "memory": str(int(infoVM['maxMemory'])),
        }

        if not TestenvDatabase().updateRessourcesVM(vm_dict):
            logger.error("Échec de la mise à jour des ressources de la machine virtuelle '%s' dans la base de données", vm_name)
            return False
        else:
            logger.info("Les ressources de la machine virtuelle '%s' ont été mises à jour avec succès dans la base de données", vm_name)

        # # On redémarre la machine
        if not start_vm(vm_name):
            logger.error("Échec du démarrage de la machine '%s'", vm_name)
            return False
        else:
            logger.info("La machine '%s' a été démarrée avec succès", vm_name)
        return True

    except Exception as e:
        logger.error("Échec de la mise à jour des ressources de la machine virtuelle '%s'. Erreur : %s", vm_name, str(e))
        return False
