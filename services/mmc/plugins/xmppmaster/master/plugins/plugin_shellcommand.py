# -*- coding: utf-8 -*-
from  lib.utils import pulginprocess
import sys, os
from  lib.utils import file_get_content, file_put_content, typelinux, servicelinuxinit, isprogramme, simplecommande, simplecommandestr, CreateWinUser

plugin={"VERSION": "1.0", "NAME" :"shellcommand"}

# le decorateur @pulginprocess
# defini squelette du dict result sectionid action et ret definie
# se charge d'envoyé message result si pas d'exception ou dict erreur si exception
# le code de retour est 8 par default si erreur sinon redefinissait le code d'erreur result['ret']=numerreur
# le message d'erreur par default est "ERROR : %s"%action  sinon redefinir le message d'erreur
# data est directement utilisable meme si celui ci était passé en base64.
# si vous voulez que data soit en base 64 lors de l'envoi definiser result['base64'] = True

@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur, result):
    obj = simplecommande(data['cmd'])
    for i in range(len(obj['result'])):
        obj['result'][i]=obj['result'][i].rstrip('\n')
    a = "\n".join(obj['result'])
    dataerreur['ret'] = obj['code']
    if obj['code'] == 0:
        result['data']['result'] = a
    else:
        dataerreur['data']['msg']="Erreur commande\n %s"%a
        raise
