#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import smtplib
import sys, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

to_addrs_array = []
html = u"""@@@@@event@@@@@"""

to_addrs_string = u"""@@@@@to_addrs_string@@@@@"""
html = html.strip() 
if html.strip() == '' or html.startswith("@@@@@event"):
    # pas de message html
    sys.exit(-1)

to_addrs_string = to_addrs_string.strip() 
if to_addrs_string != '' and not to_addrs_string.startswith("@@@@@to_addrs_string"):
    to_addrs_array = [x.strip("'\" \n") for x in to_addrs_string.split(",") if "@" in x]

if not to_addrs_array:
    #pas de destinataire
    sys.exit(-1)

server = smtplib.SMTP_SSL() # On utilise SMTP_SSL() à la place de SMTP()
server.connect('smtp-fr.securemail.pro', 465) # On indique le port TLS
server.ehlo() # On utilise la commande EHLO
server.login('systemdev@siveo.net', 'P@ssw0rd$')
# (235, '2.7.0 Authentication successful') # Réponse du serveur
fromaddr = 'Alert <systemdev@siveo.net>'
sujet = "Rapport event"
text = u"Ne pas repondre a ce message!"
msg = MIMEMultipart('alternative')
msg['Subject'] = sujet
msg['From'] = fromaddr
msg['To'] = ','.join(to_addrs_array)
# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)
try:
    server.sendmail(fromaddr, to_addrs_array, msg.as_string())
except smtplib.SMTPException as e:
    print(e)

server.quit()
sys.exit(0)
