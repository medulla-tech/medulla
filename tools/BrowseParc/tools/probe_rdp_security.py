#!/usr/bin/env python3
"""Interroge un serveur RDP pour connaitre le mode de securite qu'il exige.

Envoie une X.224 Connection Request avec une RDP Negotiation Request et lit la
reponse COMPLETE (TPKT), puis decode la RDP Negotiation Response/Failure.
"""
import socket
import struct
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "172.16.12.115"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 3389

MODES = {
    0x00000000: "RDP standard (aucun TLS)",
    0x00000001: "TLS",
    0x00000002: "NLA / CredSSP",
    0x00000003: "TLS + NLA",
    0x00000008: "RDP standard + TLS + NLA",
}
FAILURES = {
    0x00000001: "SSL_REQUIRED_BY_SERVER",
    0x00000002: "SSL_NOT_ALLOWED_BY_SERVER",
    0x00000003: "SSL_CERT_NOT_ON_SERVER",
    0x00000004: "INCONSISTENT_FLAGS",
    0x00000005: "HYBRID_REQUIRED_BY_SERVER",
    0x00000006: "SSL_WITH_USER_AUTH_REQUIRED_BY_SERVER",
}


def read_tpkt(sock):
    """Lit un paquet TPKT complet."""
    header = b""
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            return header
        header += chunk
    length = struct.unpack(">H", header[2:4])[0]
    body = b""
    while len(body) < length - 4:
        chunk = sock.recv(length - 4 - len(body))
        if not chunk:
            break
        body += chunk
    return header + body


def probe(requested):
    request = (b"\x03\x00\x00\x13"          # TPKT, 19 octets
               b"\x0e\xe0\x00\x00\x00\x00\x00"  # X.224 Connection Request
               b"\x01\x00\x08\x00"          # RDP_NEG_REQ, longueur 8
               + struct.pack("<I", requested))
    sock = socket.create_connection((HOST, PORT), timeout=8)
    sock.send(request)
    data = read_tpkt(sock)
    sock.close()
    return data


print("--- serveur RDP %s:%d" % (HOST, PORT))
for mode, label in MODES.items():
    try:
        data = probe(mode)
    except Exception as exc:  # noqa: BLE001
        print("  %-26s erreur : %s" % (label, exc))
        continue
    verdict = "reponse inattendue"
    # RDP_NEG_RSP/RDP_NEG_FAILURE : type(1) drapeaux(1) longueur(2) valeur(4).
    # Les drapeaux varient (0x01 = EXTENDED_CLIENT_DATA_SUPPORTED).
    for index in range(max(0, len(data) - 7)):
        if data[index + 2:index + 4] != b"\x08\x00":
            continue
        if data[index] == 0x02:
            selected = struct.unpack("<I", data[index + 4:index + 8])[0]
            verdict = "ACCEPTE -> mode retenu : %s" % MODES.get(selected, hex(selected))
            break
        if data[index] == 0x03:
            code = struct.unpack("<I", data[index + 4:index + 8])[0]
            verdict = "REFUSE -> %s" % FAILURES.get(code, hex(code))
            break
    print("  %-26s %s" % (label, verdict))
    print("       brut : %s" % data.hex())
