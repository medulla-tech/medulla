#!/usr/bin/env python3
"""Liste les methodes XMLRPC reellement exposees par le mmc-agent."""
import base64
import ssl
import sys
import xmlrpc.client


class BasicAuth(xmlrpc.client.SafeTransport):
    def __init__(self, user, password):
        super().__init__(context=ssl._create_unverified_context())
        self._auth = base64.b64encode(("%s:%s" % (user, password)).encode()).decode()

    def send_headers(self, connection, headers):
        headers.append(("Authorization", "Basic " + self._auth))
        super().send_headers(connection, headers)


transport = BasicAuth("mmc", "s3cr3t")
proxy = xmlrpc.client.ServerProxy("https://127.0.0.1:7080", transport=transport,
                                  allow_none=True)

for method in ("system.listMethods", "listMethods"):
    try:
        result = None
        if method == "system.listMethods":
            result = proxy.system.listMethods()
        else:
            result = proxy.listMethods()
        print("--- %s : type=%s" % (method, type(result).__name__))
        print("--- valeur brute : %s" % repr(result)[:600])
        methods = result if isinstance(result, list) else [str(result)]
        interesting = [m for m in methods if "browse" in m or "guacamole" in m.lower()]
        print("--- methodes browse* / guacamole :")
        for name in sorted(interesting):
            print("      %s" % name)
        missing = [m for m in ("admin.browse_parc_start", "admin.browse_parc_session",
                               "admin.browse_parc_agents", "admin.browse_parc_status")
                   if m not in methods]
        print("--- manquantes : %s" % (missing if missing else "aucune"))
        sys.exit(0)
    except xmlrpc.client.Fault as fault:
        print("--- %s -> FAULT %s : %s" % (method, fault.faultCode, fault.faultString[:120]))
    except Exception as exc:
        print("--- %s -> %s" % (method, exc))
print("--- aucune introspection disponible")
