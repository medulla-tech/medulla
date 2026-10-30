#!/usr/bin/env python3
"""Probe an MMC agent XMLRPC method without a web session.

The MMC agent answers:
  * "NO_SUCH_FUNCTION" fault  -> the method is not exposed by any plugin
  * "Authentification nécessaire : <method>" -> the method exists but needs a
    user session (which is exactly what we want to prove after a deployment)

Usage: probe_xmlrpc.py <method> [method...]
"""
import base64
import ssl
import sys
import xmlrpc.client


class BasicAuthTransport(xmlrpc.client.SafeTransport):
    def __init__(self, user, password):
        super().__init__(context=ssl._create_unverified_context())
        self._auth = base64.b64encode(("%s:%s" % (user, password)).encode()).decode()

    def send_headers(self, connection, headers):
        headers.append(("Authorization", "Basic " + self._auth))
        super().send_headers(connection, headers)


def main():
    methods = sys.argv[1:] or ["admin.getApiVersion"]
    transport = BasicAuthTransport("mmc", "s3cr3t")
    proxy = xmlrpc.client.ServerProxy("https://127.0.0.1:7080", transport=transport,
                                      allow_none=True)
    exit_code = 0
    for method in methods:
        plugin, _, function = method.partition(".")
        try:
            result = getattr(getattr(proxy, plugin), function)()
            print("%s -> OK %s" % (method, str(result)[:120]))
        except xmlrpc.client.Fault as fault:
            message = fault.faultString or ""
            if "NO_SUCH_FUNCTION" in message or "No such function" in message:
                print("%s -> MISSING (%s)" % (method, message))
                exit_code = 2
            elif "Authentification" in message:
                print("%s -> EXPOSED (%s)" % (method, message))
            else:
                print("%s -> FAULT (%s)" % (method, message))
                exit_code = 3
        except Exception as exc:  # pragma: no cover - transport level
            print("%s -> TRANSPORT ERROR (%s)" % (method, exc))
            exit_code = 4
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
