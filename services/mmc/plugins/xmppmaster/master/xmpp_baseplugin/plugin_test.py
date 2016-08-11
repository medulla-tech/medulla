# -*- coding: utf-8 -*-
from  lib.utils import pulginprocess
plugin={"VERSION": "1.0", "NAME" :"test"}
@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur,result):
    if data['afficherliste'] [0] !=   'je suis un test':
        dataerreur['data']['msg'] = 'bon bah il y a une erreur dans ret sera différent de 0'
        raise
    result['data']['afficherliste'] = data['afficherliste']
    result['base64'] = True
