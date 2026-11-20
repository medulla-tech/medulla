# -*- coding: utf-8 -*-
"""
Faux `pulse_xmpp_agent.lib.configuration` (tests uniquement).

Reproduit le strict necessaire de l'agent reel : un objet `confParameter`
exposant `jidagent`, dont la partie `bare` est celle que le serveur connait.
Il permet de tester la voie preferee du transporteur
(`derive_jid_via_agent`), qui est celle utilisee en production.
"""

#: JID factice de la machine, tel que le fournirait l'agent configure.
#: Le suffixe `.7zz` correspond volontairement au contenu de
#: `lib/INFOSTMP/JIDSUFFIXE` de ce faux paquet, afin qu'un test puisse
#: verifier que le transporteur lit bien ce fichier.
FAKE_JIDAGENT = "pc-stub.7zz@pulse/aa-bb-cc-dd-ee-ff"


class confParameter:
    def __init__(self, typeconf="machine"):
        self.agenttype = typeconf
        self.jidagent = FAKE_JIDAGENT
        self.confserver = "127.0.0.1"
        self.confport = 5222
        self.confpassword = "motdepasse-de-test"
        self.confdomain = "pulse"
        self.sub_registration = ["master_reg@pulse"]
