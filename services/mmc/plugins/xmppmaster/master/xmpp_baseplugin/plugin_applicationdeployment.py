# -*- coding: utf-8 -*-
import json
#jfk
from lib.utils import  simplecommandestr, simplecommande, pulgindeploy, merge_dicts, name_random
import sys, os, platform
#JFK
from lib.managepackage import managepackage
#from lib.managesession import sessiondatainfo, session
from lib.grafcetdeploy import sequentialevolutionquery
import pprint
import traceback

import logging

logger = logging.getLogger()


plugin = { "VERSION" : "1.1", "NAME" : "applicationdeployment", "TYPE" : "all" }


"""
Plugins for deploiment application 
"""


#loginformationinfomaster(self, msgdata)

#TQ type message query
#TR type message Reponse
#TE type message Error
#TED type message END deploy
#TEVENT remote event


def checkosindescriptor(listkeys, os):
    for i in listkeys.keys():
        if os.startswith(i):
            return True
    return False

def action( objectxmpp, action, sessionid, data, message, dataerreur):

    try:
        if not 'Devent' in data : data['Devent'] = ""
        if not "Dtypequery" in data : data['Dtypequery'] = "missing"
        if not 'Daction' in data : data['Daction'] = ""
        if not "rsetape" in data : 
            dede = -1 
        else: 
            dede = data['rsetape']
        logging.info('------------------------------------------------------------------')
        logging.info('{0:12}|{1:25}|{2:20}'.format("MachineType","plugin","sessionid"))
        logging.info('{0:12}|{1:25}|{2:20}'.format(objectxmpp.config.agenttype, action, sessionid))
        logging.info('------------------------------------------------------------------')
        logging.info('{0:3}|{1:10}|{2:25}|{3:25}'.format("etape", "querytype", "event", "action"))
        logging.info('{0:3}|{1:10}|{2:25}|{3:25}'.format(dede, data['Dtypequery'], data['Devent'], data['Daction']))
        logging.info('------------------------------------------------------------------')

        objectsession =  objectxmpp.session.sessionfromsessiondata(sessionid)

        #structure message for log 
        msglog = {
                    'action': 'loginfos',
                    'sessionid': sessionid,
                    'data' : {'tag' : 'deploy'},
                    'ret' : 0,
                    'base64' : False
                }
        #structure message for signal repprise
        datasignal = {
                    'action': action,
                    'sessionid': sessionid,
                    'data' : {},
                    'ret' : 0,
                    'base64' : False,
                    'retourmessage' : str(message['from']),
                    'continue' : 'break'
                }

        if not ('Devent' in data and "Dtypequery" in data ):
            return
        #gestion evennement
        if  data['Dtypequery'] == 'TEVENT':
            if objectxmpp.session.isexist(sessionid):
                data['Dtypequery'] = 'TR'
                datacontinue = {
                        'to' : objectxmpp.boundjid.bare,
                        'action': action,
                        'sessionid': sessionid,
                        'data' : dict(objectxmpp.session.sessionfromsessiondata(sessionid).datasession.items() + data.items()),
                        'ret' : 0,
                        'base64' : False
                }
                objectxmpp.eventmanage.addevent(datacontinue)
            return


        #seul master peut demander un deploiement
        if not (objectxmpp.session.isexist(sessionid)) and objectxmpp.config.agenttype == "relayserver" :
            #start deploy if Master command
            if not (message['from'].user == 'master' and data['Devent']=="STARDEPLOY" and data['Dtypequery'] ==  "TQ" ):
                return
 

        ret = 0
        msg = ""


        if  data['Dtypequery'] == 'TQ':
            msglog['data']['msg'] = "**DEPLOY  %s : %s %s %s %s %s %s %s %s %s"\
                %(data['name'],sessionid, sys.platform, objectxmpp.boundjid.bare, data['Dtypequery'], action, data['Daction'], data['Devent'], objectxmpp.config.agenttype, message['from'])
        elif data['Dtypequery'] == 'TR':
            msglog['data']['msg'] = "**ACQUIT %s : %s %s %s %s %s %s %s %s %s "\
                %(data['name'], sessionid, sys.platform,objectxmpp.boundjid.bare, data['Dtypequery'], action, data['Daction'], data['Devent'], objectxmpp.config.agenttype, message['from'])
        else:
            msglog['data']['msg'] = "**STATUS %s : %s %s %s %s %s %s %s %s %s "\
                %(data['name'],sessionid,sys.platform,objectxmpp.boundjid.bare,  data['Dtypequery'], action, data['Daction'], data['Devent'], objectxmpp.config.agenttype, message['from'])
        logging.debug(msglog['data']['msg'])
        objectxmpp.event("loginfotomaster", msglog)


        #controle affichage erreur suivant ret
        if 'ret' in message['body']: 
            ret = message['body']['ret']
        if "msg" in data: msg = data["msg"]
        if data['Dtypequery'] == "TE":
            msglog['data']['msg']  =  "ERROR CODE %s \nERROR MSG : %s"%(message['body']['ret'], msg)
            objectxmpp.event("loginfotomaster", msglog)
            logging.debug(msglog['data']['msg'])
            objectxmpp.session.clear(sessionid, objectxmpp)
            return

        # controle fin de deployment 
        if 'Devent' in data and data['Devent'] == "ENDDEPLOY":
            msglog['data']['msg']  = "DEPLOYEND %s %s"% (data['name'], sessionid )
            objectxmpp.event("loginfotomaster", msglog)
            logging.debug("DEPLOYEMENT FINISH :"%(msglog['data']['msg']))
            objectxmpp.session.clear(sessionid, objectxmpp)
            return


        msgdata = {
                    'action': action,
                    'sessionid': sessionid,
                    'data' : "",
                    'ret' : 0,
                    'base64' : False
                }

        if data['Dtypequery'] == 'TED':
            if objectxmpp.config.agenttype == 'relayserver':
                msgdata['data'] = data
                objectxmpp.send_message( mto=objectxmpp.agentmaster,
                                            mbody=json.dumps(msgdata),
                                            mtype='chat')
            ## fin de session
            msglog['data']['msg']  = "DEPLOYEND %s %s"% (data['name'], sessionid )
            objectxmpp.event("loginfotomaster", msglog)
            logging.debug(msglog['data']['msg'])
            objectxmpp.session.clear(sessionid, objectxmpp)
            return


        ###attention comportement different suivant machine ou relais serveur
        try:
            if objectxmpp.config.agenttype == "relayserver":
                #TRAITEMENT PLUGIN RELAISSERVER
                if sys.platform.startswith('linux'):
                    ##############################################################################
                    # phase 1 creation d'une session et demande os et path a machine
                    ##############################################################################
                    # creation d'une session de deployement sur relyserver
                    if not objectxmpp.session.isexist(sessionid):
                        try:
                            #data possede les jid master, relayserver et machine et ips
                            datasession = data
                            #embarquement du descriptaur de deployement
                            datasession['descriptor'] = managepackage.getdescriptorpackagename(data['name'])
                            #recuperation des os que l'on peut traiter depuis descripteur

                            datasession['srcpackage'] = managepackage.getpathpackagename(data['name'])
                            datasession['srcpackageuuid'] = os.path.basename(datasession['srcpackage'])
                            # charge descripteur json
                            datasession['Devent'] =  "pathdeploy"
                            datasession['Dtypequery'] = "TQ"
                            datasession['rsetape'] = 1
                            msgdata['data'] = datasession
                            #creation session
                            msglog['data']['msg'] = "SESSION CREATION %s %s %s %s %s"%(data['name'],sys.platform, objectxmpp.config.agenttype, objectxmpp.boundjid.bare, sessionid)
                            objectxmpp.session.createsessiondatainfo(sessionid,  datasession = datasession, timevalid = 10)
                            objectxmpp.event("loginfotomaster", msglog)
                            logging.debug(msglog['data']['msg'])
                            #les package ne sont enregistre dans different repertoire suivant os 
                            #envoi message a l'agent machine demande os et path des pacquages sur machine
                            print "**********************************************"
                            print "envoi query machine pour renseignement OS et chemin d'install du package"
                            print "**********************************************"
                            objectxmpp.send_message( mto=data['jidmachine'],
                                            mbody=json.dumps(msgdata),
                                            mtype='chat')
                            #print "--------------------------------------------------------------"
                            #print "Ne pas envoyer de reponse a master pour le momment"
                            objectxmpp.send_message( mto=message['from'],
                                            mbody=json.dumps(msgdata),
                                            mtype='chat')

                            return
                        except Exception as e:
                            msglog['data']['msg']  =  "ERREURDEPLOY %s %s relayserver creation session : %s"%(data['name'], sessionid, str(e))
                            msglog['ret'] = 67
                            objectxmpp.event("loginfotomaster", msglog)
                            logging.error(msglog['data']['msg'])
                            traceback.print_exc(file=sys.stdout)
                            return
                    else:
                        try:
                            ##############################################################################
                            # phase 2 RECOIS OS ET PATH INSTALL PACKAGE SUR MACHINE
                            ##############################################################################
                            objectxmpp.session.reactualisesession(sessionid)
                            #traitement  path et os de machine
                            if data['Devent'] == "pathdeploy" and data['Dtypequery'] == "TR":
                                # "Reponse pathdeploy dans  data['result']"
                                #mise a jour data avec result
                                data['osmachine'] = data['result']['os']
                                ##################################
                                # check possible deploy sur cet os [si non possible gere erreur]
                                ###################################
                                if not checkosindescriptor(data['descriptor'], data['osmachine']):
                                    #on ne peut pas deploye sur cet os
                                    data['Dtypequery'] = "TE"
                                    msglog['data']['msg']  =  "ERREURDEPLOY %s %s : can not deploy. Os for this deployment is not expected"%(data['name'], sessionid )
                                    # message erreur a master 
                                    objectxmpp.event("loginfotomaster", msglog)
                                    msgdata['data'] = data
                                    msgdata['data']['msg'] = msglog['data']['msg']
                                    msgdata['ret']  = 128
                                    objectxmpp.send_message( mto=message['from'],
                                            mbody = json.dumps(msgdata),
                                            mtype='chat')
                                    #termine session
                                    objectxmpp.session.clear(sessionid, objectxmpp)
                                    return
                                print "**********************************************"
                                print "the package %s is installable on the OS %s"%(data['name'],data['osmachine'])
                                print "**********************************************"
                                data['srcdest'] = data['result']['srcdest']
                                data['srcdestmachine'] = os.path.join(data['result']['srcdest'],data['srcpackageuuid'])

                                #sauve session data
                                msgdata['ret']  = 0
                                msglog['data']['msg']  =  "DEPLOYACTION %s %s : syncho package %s on machine"\
                                    "%s"%(data['name'],sessionid, data['name'], data['jidmachine'])

                                objectxmpp.event("loginfotomaster", msglog)
                                #sauve dans session
                                data['rsetape'] = 2
                                objectxmpp.session.sessionsetdata(sessionid, data)
                                return

                            if objectxmpp.session.sessionfromsessiondata(sessionid).datasession['rsetape'] == 2 and  data['Dtypequery'] == "TR":

                                #print "FILE TRANSFERT %s  %s"%(data['Devent'],objectxmpp.session.sessionfromsessiondata(sessionid).datasession['RSfinishevent'])
                                if data['Devent'] == objectxmpp.session.sessionfromsessiondata(sessionid).datasession['RSfinishevent']:
                                    
                                    logging.debug("FILE TRANSFERT MASTER TO RS TERMINER")
                                    objectxmpp.eventmanage.delmessage_loop( data['RSfinishevent'])
                                    #############################################################################
                                    # on peut passer a la phase suivante. On a recu un TEVENT injecter dans loop message copy fichier package terminer master to relayserver
                                    #############################################################################
                                    # On prepare transfert file package de relayserver to machine
                                    #############################################################################
                                    ##############################################################################
                                    # phase 3 envoi des package sur machine
                                    ##############################################################################
                                    # register les evenements possibles
                                    # transfert fil termine
                                    data['rsetape'] = data['rsetape'] + 1
                                    datacontinue = {
                                                    'to' : objectxmpp.boundjid.bare,
                                                    'action': action,
                                                    'sessionid': sessionid,
                                                    'data' : dict(objectxmpp.session.sessionfromsessiondata(sessionid).datasession.items()+ data.items()),
                                                    'ret' : 0,
                                                    'base64' : False
                                    }
                                    datacontinue['data']['Dtypequery'] = 'TR'
                                    datacontinue['data']['Devent'] = data['Mfinishevent']
                                    objectxmpp.session.sessionsetdata(sessionid, data)

                                    #command =  "rsync --delete -av %s %s:%s"%(data['path'], data['iprelais'], data['path'])
                                    if data['ipmachine'] != data['iprelais']:
                                        print "**********************************************"
                                        print "FICHIER  source et destination son sur 2 serveurs differents"
                                        print "**********************************************"
                                        cmd = "rsync -av %s/ %s:%s/"%(data['srcpackage'], data['ipmachine'],os.path.join(data['srcdest'],data['srcpackageuuid']))
                                        msglog['data']['msg']  =  "DEPLOYACTION : %s command %s"%(sessionid, cmd)
                                        objectxmpp.event("loginfotomaster", msglog)
                                        msglog['data']['msg']  =  "DEPLOYACTION : %s synchronise package [relayserver/machine] from %s/ to %s:%s/"%(sessionid, data['srcpackage'], data['ipmachine'],os.path.join(data['srcdest'],data['srcpackageuuid']))
                                        objectxmpp.event("loginfotomaster", msglog)
                                        logging.debug(msglog['data']['msg'])
                                        #synchro = simplecommandestr(cmd)
                                        #mise à jour session
                                        # copy fichier vers machines envoi message TEVENT vers machine
                                        objectxmpp.mannageprocess.add_processcommand( cmd , sessionid, False, datacontinue, False )
                                    else:
                                        msglog['data']['msg']  =  "WARNINGDEPLOY %s  : relay server machine and even machine to sync [task not performed]"%(sessionid)
                                        objectxmpp.event("loginfotomaster", msglog)
                                        logging.debug(msglog['data']['msg'])
                                        #inject message datacontinue dans loop rs pour passer etape suivante
                                        objectxmpp.eventmanage.addevent(datacontinue)
                                        # enregistre evenement transfert file ternime
                                    return
                            elif data['Devent'] == objectxmpp.session.sessionfromsessiondata(sessionid).datasession['RSerrorevent']:
                                    #on ne peut pas deploye
                                    data['Dtypequery'] = "TE"
                                    msglog['data']['msg']  =  "ERREURDEPLOY %s %s : can not transfert package files to RS.%s"%(data['name'], sessionid, jidmachine )
                                    # message erreur a master 
                                    objectxmpp.event("loginfotomaster", msglog)
                                    logging.error(msglog['data']['msg'])
                                    #termine session
                                    objectxmpp.session.clear(sessionid, objectxmpp)
                                    return

                            if objectxmpp.session.sessionfromsessiondata(sessionid).datasession['rsetape'] == 3 and  data['Dtypequery'] == "TR":
                                if data['Devent'] == objectxmpp.session.sessionfromsessiondata(sessionid).datasession['Mfinishevent']:
                                    logging.debug("FILE TRANSFERT RS TO MACHINE FINISH")
                                    print "FILE TRANSFERT RS TO MACHINE FINISH"
                                    objectxmpp.eventmanage.delmessage_loop( data['Mfinishevent'])
                                    data['rsetape'] = data['rsetape'] + 1
                                    objectxmpp.session.sessionsetdata(sessionid, data)
                                    datacontinue = {
                                                'to' : objectxmpp.boundjid.bare,
                                                'action': action,
                                                'sessionid': sessionid,
                                                'data' : dict(objectxmpp.session.sessionfromsessiondata(sessionid).datasession.items()+ data.items()),
                                                'ret' : 0,
                                                'base64' : False
                                    }
                                    datacontinue['data']['Dtypequery'] = 'TREPRISEPhase4'
                                    datacontinue['data']['Devent'] = 'suite'
                                    datacontinue['data']['nameevent'] = 'autremessage'
                                    objectxmpp.eventmanage.addevent(datacontinue)
                                    return
                                elif data['Devent'] == objectxmpp.session.sessionfromsessiondata(sessionid).datasession['Merrorevent']:
                                    #on ne peut pas deploye
                                    print "NOT FILE TRANSFERT RS TO MACHINE FINISH"
                                    data['Dtypequery'] = "TE"
                                    msglog['data']['msg']  =  "ERREURDEPLOY %s %s : can not transfert package files to machine.%s"%(data['name'], sessionid, jidmachine )
                                    # message erreur a master 
                                    objectxmpp.event("loginfotomaster", msglog)
                                    #termine session
                                    objectxmpp.session.clear(sessionid, objectxmpp)
                                    return

                            if objectxmpp.session.sessionfromsessiondata(sessionid).datasession['rsetape'] == 4 and  data['Dtypequery'] == 'TREPRISEPhase4':
                                print "**********************************************"
                                print "packages %s available on Machine %s"%(data['name'], data['jidmachine'])
                                print "START DEPLOY"
                                print "**********************************************"

                                logging.debug("Start grapcet deploy")
                                objectxmpp.eventmanage.delmessage_loop_Dtypequery('TREPRISEPhase4')
                                data['Dtypequery'] ='TR'
                                # on doit initialiser le graphcet et faire ces demande
                                # initialisation graphcet
                                data['rsetape'] = data['rsetape'] + 1
                                objectxmpp.session.sessionsetdata(sessionid, data)
                                evolution = sequentialevolutionquery(objectxmpp, msglog, datasignal, data, init=True)
                                msgdata['data'] = evolution.getdata()
                                msgdata['ret']  = evolution.geterrorcode()
                                if msgdata['data']['Dtypequery'] == "TE":
                                    msglog['data']['msg']  =  "ERREURDEPLOY %s  : deployement event %s on machine %s" %(sessionid, msgdata['data']['Devent'], msgdata['data']['jidmachine'])
                                    objectxmpp.event("loginfotomaster", msglog)
                                    logging.debug(msglog['data']['msg'])
                                    msgdata['data'] = data
                                    msgdata['data']['msg'] = msglog['data']['msg']
                                    msgdata['ret']  = 127
                                    #termine session
                                    objectxmpp.session.clear(sessionid, objectxmpp)

                                objectxmpp.send_message( mto=data['jidmachine'],
                                            mbody=json.dumps(msgdata),
                                            mtype='chat')
                                return

                            if objectxmpp.session.sessionfromsessiondata(sessionid).datasession['rsetape'] >= 5:

                                objectxmpp.session.reactualisesession(sessionid)

                                # call class dedeploiement pour envoyé reponse:
                                evolution = sequentialevolutionquery(objectxmpp, msglog, datasignal, data)
                                msgdata['data'] = evolution.getdata()
                                msgdata['ret']  = evolution.geterrorcode()
                                objectxmpp.send_message( mto=data['jidmachine'],
                                        mbody = json.dumps(msgdata),
                                        mtype='chat')
                                data['rsetape'] = data['rsetape'] + 1
                                objectxmpp.session.sessionsetdata(sessionid, data)
                                if data['Dtypequery'] == 'TED':
                                    objectxmpp.send_message( mto=objectxmpp.agentmaster,
                                            mbody=json.dumps(msgdata),
                                            mtype='chat')
                                    ## fin de session
                                    msglog['data']['msg']  = "DEPLOYEND  %s %s for Relayserver %s"% (data['name'], sessionid, objectxmpp.boundjid )
                                    objectxmpp.event("loginfotomaster", msglog)
                                    logging.debug(msglog['data']['msg'])
                                    objectxmpp.session.clear(sessionid, objectxmpp)
                                return

                        except Exception as e:
                            msglog['data']['msg']  =  "ERREURDEPLOY %s deployment processing relayserver [%s]"%(sessionid,str(e))
                            objectxmpp.event("loginfotomaster", msglog)
                            logging.debug(msglog['data']['msg'])
                            traceback.print_exc(file=sys.stdout)
                            return
            else:
                #TRAITEMENT PLUGIN MACHINE
                if not objectxmpp.session.isexist(sessionid):
                    try:
                        if data['Devent'] == "pathdeploy" and data['Dtypequery'] == "TQ":
                            # demande de os et chemin d'installation des pacquages
                            data['result'] = { 'srcdest' : managepackage.packagedir(), 'os' : sys.platform }
                            msglog['data']['msg']= "DEPLOYACTION : %s research OS and packages directory on machine [%s] "%(sessionid,data['result'])
                            objectxmpp.event("loginfotomaster", msglog)
                            logging.debug(msglog['data']['msg'])
                        else:
                            data['Dtypequery'] = "TE"
                            msglog['data']['msg'] = "ERREURDEPLOY %s  research OS and packages directory"%(sessionid)
                            objectxmpp.event("loginfotomaster", msglog)
                            logging.debug(msglog['data']['msg'])

                        data['Dtypequery'] = "TR"
                        msglog['data']['msg']= "SESSION CREATION %s %s %s %s"%(sys.platform, objectxmpp.config.agenttype, objectxmpp.boundjid.bare, sessionid)
                        objectxmpp.event("loginfotomaster", msglog)
                        logging.debug(msglog['data']['msg'])
                        objectxmpp.session.createsessiondatainfo(sessionid,  datasession = data, timevalid = 10)
                        msgdata['data'] = data
                        objectxmpp.send_message( mto=message['from'],
                                            mbody=json.dumps(msgdata),
                                            mtype='chat')
                        return
                    except Exception as e:
                        msglog['data']['msg']  =  "ERREURDEPLOY %s  creation session on machine [%s]"%(sessionid,str(e))
                        objectxmpp.event("loginfotomaster", msglog)
                        logging.debug(msglog['data']['msg'])
                        data['Dtypequery'] = "TE"
                        msgdata['data'] = data
                        msgdata['data']['msg'] = msglog['data']['msg']
                        msgdata['ret']  = 127
                        objectxmpp.send_message( mto = msg['from'],
                                                mbody=json.dumps(msgdata),
                                                mtype='chat')
                        #termine session
                        objectxmpp.session.clear(sessionid, objectxmpp)
                        traceback.print_exc(file=sys.stdout)
                        return
                else:
                    try:
                        objectxmpp.session.reactualisesession(sessionid)
                        evolution = sequentialevolutionquery(objectxmpp, msglog, datasignal, data)
                        msgdata['data'] = evolution.getdata()
                        msgdata['ret']  = evolution.geterrorcode()

                        # traitement si message est signler
                        if 'signal' in msgdata:
                            logging.debug("session %s signal action"%sessionid)
                            #controle si on doit envoyé message ou non
                            #break sort sans envoye message
                            #message sera envoye a reprise session
                            if msgdata['signal']['continue'] == 'break':
                                return
                        # si erreur TE est leve cote grapcet
                        objectxmpp.send_message( mto=message['from'],
                                mbody = json.dumps(msgdata),
                                mtype='chat')
                        if data['Dtypequery'] == 'TED':
                            ## fin de session
                            msglog['data']['msg']  = "DEPLOYEND  %s %s for machine %s"% (data['name'], sessionid, objectxmpp.boundjid )
                            objectxmpp.event("loginfotomaster", msglog)
                            logging.debug(msglog['data']['msg'])
                            objectxmpp.session.clear(sessionid, objectxmpp)
                        return

                    except Exception as e:
                        msglog['data']['msg']  =  "ERREURDEPLOY %s deployment processing machines [%s]"%(sessionid,str(e))
                        objectxmpp.event("loginfotomaster", msglog)
                        logging.debug(msglog['data']['msg'])
                        traceback.print_exc(file=sys.stdout)
        except Exception as e:
            msglog['data']['msg']  =  "ERREURDEPLOY %s erreur plugin [%s]"%(sessionid,str(e))
            objectxmpp.event("loginfotomaster", msglog)
            logging.debug(msglog['data']['msg'])
            traceback.print_exc(file=sys.stdout)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        traceback.print_exc(file=sys.stdout)