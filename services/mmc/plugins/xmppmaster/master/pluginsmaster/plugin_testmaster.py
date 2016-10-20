# -*- coding: utf-8 -*-
from utils import pluginmaster, pluginmastersessionaction

@pluginmastersessionaction("actualise",20)
def action( xmppobject, action, sessionid, data, message, ret, objsessiondata):
    xmppobject.session.affiche()
    print "fff"
