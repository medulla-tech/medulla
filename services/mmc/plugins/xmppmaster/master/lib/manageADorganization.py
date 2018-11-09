#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import json
import logging

logger = logging.getLogger()


class manage_fqdn_window_activedirectory:

    @staticmethod
    def basedirmachineAD():
        bd = os.path.join("/", "var", "lib", "pulse2", "organizationADmachines")
        if not os.path.isdir(bd):
            os.makedirs(bd, mode=0700)
        return bd

    @staticmethod
    def basediruserAD():
        bd = os.path.join("/", "var", "lib", "pulse2", "organizationADusers")
        if not os.path.isdir(bd):
            os.makedirs(bd, mode=0700)
        return bd

    @staticmethod
    def organizationADmachinetofile(fqdnsinfomachine):
        bd = manage_fqdn_window_activedirectory.basedirmachineAD()
        list_cn_ou_dc = fqdnsinfomachine.split("@@")

        contenuefile = list_cn_ou_dc[2]
        pathfile = os.path.join(bd, list_cn_ou_dc[1])
        if not os.path.isdir(pathfile):
            os.makedirs(pathfile, mode=0700)
        namefile = os.path.join(pathfile, list_cn_ou_dc[0])
        f = open(namefile, 'w')
        f.write(contenuefile)
        f.close()

    @staticmethod
    def organizationADusertofile(fqdnsinfomachine):
        bd = manage_fqdn_window_activedirectory.basediruserAD()
        list_cn_ou_dc = fqdnsinfomachine.split("@@")
        contenuefile = list_cn_ou_dc[2]
        pathfile = os.path.join(bd, list_cn_ou_dc[1])
        if not os.path.isdir(pathfile):
            os.makedirs(pathfile, mode=0700)
        namefile = os.path.join(pathfile, list_cn_ou_dc[0])
        f = open(namefile, 'w')
        f.write(contenuefile)
        f.close()

    @staticmethod
    def getOrganizationADmachineCN(fqdnsinfomachine):
        """
            in cas organization by machine cn is name machine
        """
        list_cn_ou_dc = fqdnsinfomachine.split("@@")
        return list_cn_ou_dc[0]

    @staticmethod
    def getOrganizationADuserCN(fqdnsinfouser):
        """
            in cas organization by user cn is name user
        """
        list_cn_ou_dc = fqdnsinfouser.split("@@")
        return list_cn_ou_dc[0]

    @staticmethod
    def getOrganizationADmachineOU(fqdnsinfomachine):
        """
            in cas organizationby machine ou is entite for machine
        """
        return fqdnsinfomachine

    @staticmethod
    def getOrganizationADuserOU(fqdnsinfouser):
        """
            in cas organization by user ou is entite for user
        """
        return fqdnsinfouser

    @staticmethod
    def getOrganizationADmachineDC(fqdnsinfomachine):
        """
            in cas organization by machine cn is domaine machine
        """
        list_cn_ou_dc = fqdnsinfomachine.split("@@")
        return list_cn_ou_dc[2]

    @staticmethod
    def getOrganizationADuserDC(fqdnsinfouser):
        """
            in cas organization by user cn is domaine user
        """
        list_cn_ou_dc = fqdnsinfouser.split("@@")
        return list_cn_ou_dc[2]
