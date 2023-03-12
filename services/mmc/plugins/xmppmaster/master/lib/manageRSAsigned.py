# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

from Crypto.PublicKey import RSA
import pickle
import os
import base64
from .utils import file_get_contents


class MsgsignedRSA:
    """
        Class use for verify from message xmpp.
        The message structure pulse xmpp has a session id.
        Session id is signed with the private key of the sender of the message.
        The receiver of the message can verify the origin of the message by comparing\
        the signature of the sessionid with the sessionid.

        Examples sender signed  data:
            master = MsgsignedRSA("master")
            sig = master.signedmsg(data)

            receiver verify data:
            client = MsgsignedRSA("client")
            key_public_server_String_base = "....................."
            object_key_public_server = client.Base64_To_ObjKeyRSA(key_public_server_String_base)
            client.verifymsg(object_key_public_server,data, sig)
    """

    def __init__(self, type):
        """
        :param type: Uses this parameter to give a name to the key
        :type b: string
        :return: Function init has no return
        """
        self.type = type
        self.filekeypublic = os.path.join(
            self.Setdirectorytempinfo(), "%s-public-RSA.key" % self.type
        )
        self.fileallkey = os.path.join(
            self.Setdirectorytempinfo(), "%s-all-RSA.key" % self.type
        )
        self.dirtempinfo = self.Setdirectorytempinfo()
        self.allkey = None
        self.publickey = None
        self.loadkey()

    def loadkey(self):
        """
        Function that loads the keys if it exists or creates\
        them in the case where it does not exist.
        """
        if self.allkey is None or self.publickey is None:
            if os.path.exists(self.filekeypublic) and os.path.exists(self.fileallkey):
                f = open(self.fileallkey, "r")
                self.allkey = pickle.load(f)
                f.close()
                f = open(self.filekeypublic, "r")
                self.publickey = pickle.load(f)
                f.close()
            else:
                # recherche keyfile si not exist then generate.
                self.generateRSAclefagent()

    def loadkeyall(self):
        """
        Function load from file the complete keys to object RSA key
        """
        if os.path.exists(self.fileallkey):
            f = open(self.fileallkey, "r")
            self.allkey = pickle.load(f)
            f.close()

    def loadkeypublic(self):
        """
        Function load from file the public key to object RSA key
        """
        if os.path.exists(self.filekeypublic):
            f = open(self.filekeypublic, "r")
            self.allkey = pickle.load(f)
            f.close()

    def loadkeyalltostr(self):
        """
        Function load from file the keys complete as a string
        """
        if os.path.exists(self.fileallkey):
            return file_get_contents(self.fileallkey)
        return ""

    def loadkeyalltobase64(self):
        """
        Function load from file the keys complete as a base64 string
        """
        if os.path.exists(self.fileallkey):
            return base64.b64encode(file_get_contents(self.fileallkey))
        return ""

    def loadkeypublictostr(self):
        """
        Function load from file the public keys as a string
        """
        if os.path.exists(self.filekeypublic):
            return file_get_contents(self.filekeypublic)
        return ""

    def loadkeypublictobase64(self):
        """
        Function load from file the public keys RSA as a base64 string
        """
        if os.path.exists(self.filekeypublic):
            return base64.b64encode(file_get_contents(self.filekeypublic))
        return ""

    def keypublictostr(self):
        """
        Function obj public key to string
        """
        return pickle.dumps(self.publickey)

    def strtokeypublic(self, str):
        """
        Function string public key to obj keyRSA
        """
        return pickle.loads(str)

    def strkeytokey(self, str):
        """
        Function string key to obj keyRSA
        """
        return pickle.loads(str)

    def Obj_KeyRSA_to_Base64(self, objectkey):
        """
        Function object keyRSA to stringbase64
        :param objectkey: key RSA all or public
        :type b:  key RSA
        :return: string encoded in base64

        """
        return base64.b64encode(pickle.dumps(objectkey))

    def Base64_To_ObjKeyRSA(self, strbase64):
        """
        Function stringbase64 to object keyRSA
        :param strbase64: string encoded in base64
        :type strbase64:  string
        :return: object
        """
        return pickle.loads(base64.b64decode(strbase64))

    def generateRSAclefagent(self):
        """
        Function generate clef RSA to file
        """
        # In real life, you use a *much* longer key
        self.allkey = RSA.generate(1024)
        self.publickey = self.allkey.publickey()
        pickle.dump(self.allkey, open(self.fileallkey, "w"))
        pickle.dump(self.publickey, open(self.filekeypublic, "w"))
        return self.allkey

    def Setdirectorytempinfo(self):
        """
        create directory
        """
        dirtempinfo = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "INFOSTMP"
        )
        if not os.path.exists(dirtempinfo):
            os.makedirs(dirtempinfo, mode=0o700)
        return dirtempinfo

    def signedmsg(self, msg):
        """
        Function signed message with key private.
        """
        return self.allkey.sign(msg, None)[0]

    def verifymsg(self, keypublic, msg, signed_message):
        """
        Function verify message with footprint
        """
        signature = int(signed_message)
        return keypublic.verify(msg, (signature,))
