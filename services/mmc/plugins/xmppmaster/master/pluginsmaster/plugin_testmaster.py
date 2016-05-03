# -*- coding: utf-8 -*-
from utils import pulginmaster, pulginmastersessionaction

@pulginmastersessionaction("actualise",20)
def action( objetxmpp, action, sessionid, data, message, ret, objsessiondata):
    #if ret == 0:
        ###
        ###objetxmpp.session.reactualisesession(sessionid, 10)
        ###or
        #objetxmpp.session.affiche()
        #objetxmpp.session.clear(sessionid)
        #print sessionid
        #print "mmm"
    objetxmpp.session.affiche()
    #else:
        #print "erreur"
    print "fff"
