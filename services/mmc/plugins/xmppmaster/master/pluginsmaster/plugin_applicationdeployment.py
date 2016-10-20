# -*- coding: utf-8; -*-
import base64
import json
import os
import utils
import pprint

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    try:
        if 'Dtypequery' in  data:
            if data['Dtypequery'] == 'TED':
                print "Delete session %s"%sessionid
                # Set deployment to done in database
                xmppobject.session.clear(sessionid)
                print "_______________________________________________________________________"
                print "_________________________RESULT DEPLOYMENT_____________________________"
                print "_______________________________________________________________________"
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(data['descriptor'])
                print "_______________________________________________________________________"

            elif  data['Dtypequery'] == 'TE':
                # clear session
                xmppobject.session.clear(sessionid)
                # Set deployment to error in database
            else:
                # Update session with data
                xmppobject.session.sessionsetdata(sessionid, data)
    except Exception as e:
        print "Error in plugin %s"%str(e)
