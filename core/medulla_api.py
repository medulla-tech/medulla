# core/medulla_api.py
import logging
import requests
import urllib3
from xml.etree import ElementTree as ET
from xmlrpc.client import dumps


class MedullaAPIClient:
    def __init__(self, url, username, password, *, verify=False):
        self.url = url
        self.username = username
        self.password = password
        self.verify = verify

        # Persistent session (keeps BasicAuth + server cookies)
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.session.verify = self.verify
        self.session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8',
            'Accept': 'text/xml'
        })

        if not self.verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self._is_authenticated = False
        self._ldap_user = None
        self._ldap_pass = None

        # explicit app-cookie store (name + value)
        self._cookie_name = None
        self._cookie_value = None

    # -------------------- Low-level HTTP / XML-RPC --------------------
    def authenticate(self, ldap_user, ldap_pass):
        """Perform base.ldapAuth and keep cookies in self.session."""
        self._ldap_user = ldap_user
        self._ldap_pass = ldap_pass

        payload = f"""<?xml version='1.0'?>
<methodCall>
  <methodName>base.ldapAuth</methodName>
  <params>
    <param><value><string>{ldap_user}</string></value></param>
    <param><value><string>{ldap_pass}</string></value></param>
  </params>
</methodCall>"""

        try:
            r = self.session.post(self.url, data=payload, timeout=20)
            r.raise_for_status()

            # Try to detect an explicit success in XML (not all servers return it)
            login_ok = False
            try:
                root = ET.fromstring(r.text)
                b = root.findtext(".//boolean")
                if b and b.strip() in ("1", "true", "True"):
                    login_ok = True
                if not login_ok:
                    res = root.findtext(".//member[name='result']/value/string") or ""
                    if res.strip().lower() in ("ok", "success", "true"):
                        login_ok = True
            except Exception:
                pass  # some servers don't return a clear state

            # Capture a TWISTED_* cookie if provided (but don't wipe old one if missing)
            new_name = new_value = None
            for c in r.cookies:
                if c.name in ("TWISTED_SECURE_SESSION", "TWISTED_SESSION"):
                    new_name, new_value = c.name, c.value
                    break
            if new_value:
                self._cookie_name = new_name
                self._cookie_value = new_value
                logging.debug("Session cookie received: %s=<hidden>", self._cookie_name)
            else:
                logging.debug("No new TWISTED_* cookie (keeping previous if any).")

            if not login_ok and not self._cookie_value:
                logging.error("LDAP auth HTTP OK but no 'success' flag and no session cookie.")
                self._is_authenticated = False
                return False

            self._is_authenticated = True
            logging.info("Authentification réussie.")
            return True

        except requests.RequestException as e:
            logging.error("[auth] HTTP error: %s", e)
            self._is_authenticated = False
            return False

    def _post_request(self, payload, _retry=True):
        """POST XML-RPC with session/cookies. Retry once if 'Authentication needed'."""
        if not self._is_authenticated:
            raise ValueError("Session non authentifiée. Appelez authenticate() d'abord.")

        # Always force the app cookie if we have one (bypass path/domain issues)
        forced_cookies = {self._cookie_name: self._cookie_value} if (self._cookie_name and self._cookie_value) else None

        r = self.session.post(self.url, data=payload, timeout=30, cookies=forced_cookies)
        if r.status_code != 200:
            raise Exception(f"Erreur HTTP : {r.status_code}")

        text = r.text or ""
        if "<fault>" in text:
            if "Authentication needed" in text and _retry and self._ldap_user and self._ldap_pass:
                logging.warning("⚠️ Ré-authentification demandée par le serveur, on retente…")
                prev_cookie = (self._cookie_name, self._cookie_value)
                if self.authenticate(self._ldap_user, self._ldap_pass):
                    # if authenticate() didn't receive a new cookie, keep the previous one
                    if not (self._cookie_name and self._cookie_value) and prev_cookie[1]:
                        self._cookie_name, self._cookie_value = prev_cookie
                    forced_cookies = {self._cookie_name: self._cookie_value} if (self._cookie_name and self._cookie_value) else None

                    r = self.session.post(self.url, data=payload, timeout=30, cookies=forced_cookies)
                    r.raise_for_status()
                    text = r.text or ""
                    if "<fault>" not in text:
                        return text
            logging.error("Erreur XML-RPC :\n%s", text)
            raise Exception("Erreur XML-RPC.")

        return text

    def send_xmlrpc(self, method: str, params: tuple = (), raw=False):
        """Send an XML-RPC call. Returns str (raw=True) or ET.Element."""
        try:
            payload = dumps(params, methodname=method)
            logging.debug("[send_xmlrpc] Payload :\n%s", payload)
            xml_response = self._post_request(payload)
            if not xml_response:
                logging.warning("Aucune réponse XML.")
                return None
            return xml_response if raw else ET.fromstring(xml_response)
        except Exception as e:
            logging.error("[send_xmlrpc] Exception : %s", e)
            return None

    # -------------------- XML helpers --------------------
    @staticmethod
    def _find_member_text(root: ET.Element, member_name: str):
        """Return text under member[name='X']/value/... if present."""
        if root is None:
            return None
        node = root.find(f".//member[name='{member_name}']/value")
        if node is None:
            return None
        s = node.find("string")
        if s is not None and s.text:
            return s.text.strip()
        txt = "".join(node.itertext()).strip()
        return txt or None

    @staticmethod
    def _struct_to_dict(struct_elem: ET.Element) -> dict:
        """Convert a <struct> XML-RPC into a Python dict {name: text}."""
        d = {}
        for m in struct_elem.findall("member"):
            key = (m.findtext("name") or "").strip()
            val_node = m.find("value")
            if not key or val_node is None:
                continue
            s = val_node.find("string")
            if s is not None and s.text is not None:
                d[key] = s.text.strip()
            else:
                d[key] = "".join(val_node.itertext()).strip()
        return d

    # -------------------- Business API --------------------
    def get_machines_paged(self, source="xmpp", page_size=200):
        """Optional paginator; returns list of raw XML pages."""
        if source != "xmpp":
            logging.warning("Seul 'xmpp' paginé est implémenté.")
            return None
        offset = 0
        chunks = []
        ctx = {'filter': '', 'field': 'allchamp'}
        while True:
            xml = self.send_xmlrpc("xmppmaster.get_machines_list", (offset, page_size, ctx), raw=True)
            if not xml:
                break
            chunks.append(xml)
            root = ET.fromstring(xml)
            count = len(root.findall(".//member[name='data']/value/array/data/value/struct"))
            if count < page_size:
                break
            offset += page_size
        return chunks

    def get_machines(self, source="xmpp", raw=False):
        if source == "xmpp":
            ctx = {'filter': '', 'field': 'allchamp'}
            return self.send_xmlrpc("xmppmaster.get_machines_list", (0, 50, ctx), raw=raw)
        elif source == "glpi":
            logging.warning("GLPI non supporté pour le moment.")
            return None
        else:
            raise ValueError(f"Source inconnue : {source}")

    def get_inventory_dict(self, uuid: str, uuid_inventory: str) -> dict:
        """Fetch HARDWARE inventory and normalize it."""
        try:
            req = {
                "uuid_serial_machine": uuid,
                "uuid_inventory": uuid_inventory,
                "inventory_part": "HARDWARE"
            }
            root = self.send_xmlrpc("glpi.getLastMachineInventoryPart", (req,))
            if root is None:
                logging.warning("Aucune donnée reçue de Medulla (HARDWARE).")
                return {}

            hostname = self._find_member_text(root, "hostname") or "unknown"
            osname = (self._find_member_text(root, "osname") or "windows_10").lower()
            osversion = self._find_member_text(root, "osversion") or "22h2"
            manufacturer = self._find_member_text(root, "manufacturer") or "unknown"
            model = self._find_member_text(root, "model") or ""
            bios = self._find_member_text(root, "biosversion") or ""

            inventory = {
                "machine": hostname,
                "uuid": uuid_inventory,
                "os": {
                    "name": osname,
                    "vendor": "microsoft" if "win" in osname else "",
                    "version": osversion,
                    "cpe": f"cpe:2.3:o:microsoft:{osname}:{osversion}:*:*:*:*:*:*:*"
                },
                "packages": [],
                "hardware": {
                    "vendor": manufacturer,
                    "model": model,
                    "firmware_version": bios,
                    "cpe": ""
                },
                "roles": []
            }
            return inventory
        except Exception as e:
            logging.error("Erreur lors de la récupération d'inventaire : %s", e)
            return {}

    def get_inventory_softwares(self, uuid: str, uuid_inventory: str) -> list[dict]:
        """Return [{'name','version'}] from SOFTWARES, with a full-inventory fallback."""
        def _extract_pkgs(root: ET.Element) -> list[dict]:
            pkgs: list[dict] = []
            if root is None:
                return pkgs

            # Prefer SOFTWARES/PROGRAMS subtree, otherwise scan all structs
            candidates = []
            for key in ("SOFTWARES", "PROGRAMS", "softwares", "software", "programs"):
                v = root.find(f".//member[name='{key}']/value")
                if v is not None:
                    candidates.append(v)
            if not candidates:
                candidates = [root]

            for subtree in candidates:
                for struct in subtree.findall(".//struct"):
                    d = self._struct_to_dict(struct)
                    name = (
                        d.get("name") or d.get("NAME")
                        or d.get("DisplayName") or d.get("DISPLAYNAME")
                        or d.get("ProductName") or d.get("PRODUCTNAME")
                    )
                    ver = (
                        d.get("version") or d.get("VERSION")
                        or d.get("DisplayVersion") or d.get("DISPLAYVERSION")
                    )
                    if name:
                        pkgs.append({"name": name.strip(), "version": (ver or "").strip()})

            # de-dup by (lower(name), version)
            seen, out = set(), []
            for p in pkgs:
                key = (p["name"].lower(), p["version"])
                if key in seen:
                    continue
                seen.add(key)
                out.append(p)
            return out

        # SOFTWARES part
        try:
            req = {"uuid_serial_machine": uuid, "uuid_inventory": uuid_inventory, "inventory_part": "SOFTWARES"}
            root = self.send_xmlrpc("glpi.getLastMachineInventoryPart", (req,))
            pkgs = _extract_pkgs(root)
            if pkgs:
                return pkgs
        except Exception as e:
            logging.warning("SOFTWARES part indisponible : %s", e)

        # Full inventory fallback
        try:
            req2 = {"uuid_serial_machine": uuid, "uuid_inventory": uuid_inventory}
            root_full = self.send_xmlrpc("glpi.getLastMachineInventoryFull", (req2,))
            return _extract_pkgs(root_full)
        except Exception as e:
            logging.error("Inventaire complet indisponible : %s", e)
            return []

    def trigger_inventory(self, uuid_machine: str) -> bool:
        """Trigger an inventory on the agent."""
        try:
            xml = self.send_xmlrpc("xmppmaster.callInventory", (uuid_machine,), raw=True)
            return xml is not None
        except Exception as e:
            logging.error("trigger_inventory error: %s", e)
            return False

    def run_remote_cmd(self, uuid_machine: str, command: str, shell: str = "cmd") -> str | None:
        """
        Execute a command on the Windows agent through Medulla.
        shell: "cmd" or "powershell"
        Returns raw XML string (or None on error).
        """
        try:
            return self.send_xmlrpc(
                "xmppmaster.callremotecommandshell",
                (uuid_machine, shell, command),
                raw=True
            )
        except Exception as e:
            logging.error("run_remote_cmd error: %s", e)
            return None

    def inject_uninstall_entry(self, uuid_machine: str, name: str, version: str,
                               publisher: str = "Apache Software Foundation") -> bool:
        """
        Create HKLM Uninstall entries (64-bit + Wow6432Node) so the agent inventories a 'fake' software.
        """
        base64 = r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SIVEO_Medulla_Fake'
        base32 = r'HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\SIVEO_Medulla_Fake'
        cmds = [
            fr'reg add "{base64}" /v DisplayName /t REG_SZ /d "{name}" /f',
            fr'reg add "{base64}" /v DisplayVersion /t REG_SZ /d "{version}" /f',
            fr'reg add "{base64}" /v Publisher /t REG_SZ /d "{publisher}" /f',
            fr'reg add "{base64}" /v UninstallString /t REG_SZ /d "\"C:\Program Files\FakeVendor\{name}\uninstall.exe\"" /f',
            fr'reg add "{base32}" /v DisplayName /t REG_SZ /d "{name}" /f',
            fr'reg add "{base32}" /v DisplayVersion /t REG_SZ /d "{version}" /f',
            fr'reg add "{base32}" /v Publisher /t REG_SZ /d "{publisher}" /f',
            fr'reg add "{base32}" /v UninstallString /t REG_SZ /d "\"C:\Program Files (x86)\FakeVendor\{name}\uninstall.exe\"" /f',
        ]
        ok = True
        for c in cmds:
            if not self.run_remote_cmd(uuid_machine, c, shell="cmd"):
                ok = False
        return ok

    def tail_agent_log(self, uuid_machine: str, lines: int = 80) -> str | None:
        """
        Return the last N lines of the agent log from Program Files or Program Files (x86).
        """
        ps = (
            f"$p1 = Join-Path $env:ProgramFiles 'Medulla\\var\\log\\xmpp-agent-machine.log';"
            f"$p2 = Join-Path $env:ProgramFiles(x86) 'Medulla\\var\\log\\xmpp-agent-machine.log';"
            f"if (Test-Path $p1) {{ Get-Content $p1 -Tail {lines} }} "
            f"elseif (Test-Path $p2) {{ Get-Content $p2 -Tail {lines} }} "
            "else { Write-Host 'log not found' }"
        )
        return self.run_remote_cmd(uuid_machine, ps, shell="powershell")


# -------------------- Helpers outside the class --------------------
def parse_machine_list(xml_doc) -> list:
    """
    Accept a raw XML string or ET.Element and return a list of machines
    [{'uuid','hostname','uuid_inventory'}].
    """
    if not xml_doc:
        logging.error("XML machines manquant (None).")
        return []

    if isinstance(xml_doc, (str, bytes)):
        s = xml_doc if isinstance(xml_doc, str) else xml_doc.decode(errors="ignore")
        if "<fault>" in s:
            logging.error("Fault XML-RPC retourné par le serveur :\n%s", s)
            return []

    try:
        root = ET.fromstring(xml_doc) if isinstance(xml_doc, (str, bytes)) else xml_doc
    except Exception as e:
        logging.error("Erreur parsing XML machine list : %s", e)
        return []

    machines = []
    # multiple entries
    for st in root.findall(".//member[name='data']/value/array/data/value/struct"):
        uuid = _extract_member_text(st, "uuid_serial_machine")
        hostname = _extract_member_text(st, "hostname")
        uuid_inventory = _extract_member_text(st, "uuid_inventorymachine")
        if uuid and hostname and uuid_inventory:
            machines.append({
                "uuid": uuid.strip(),
                "hostname": hostname.strip(),
                "uuid_inventory": uuid_inventory.strip()
            })

    # fallback: single struct
    if not machines:
        data_struct = root.find(".//member[name='data']/value/struct")
        if data_struct is not None:
            uuid = _extract_member_text(data_struct, "uuid_serial_machine")
            hostname = _extract_member_text(data_struct, "hostname")
            uuid_inventory = _extract_member_text(data_struct, "uuid_inventorymachine")
            if uuid and hostname and uuid_inventory:
                machines.append({
                    "uuid": uuid.strip(),
                    "hostname": hostname.strip(),
                    "uuid_inventory": uuid_inventory.strip()
                })

    if machines:
        for m in machines:
            logging.info("Machine : %s | UUID: %s | InvUUID: %s",
                         m["hostname"], m["uuid"], m["uuid_inventory"])
    else:
        logging.warning("Aucune machine détectée dans la réponse XML.")
    return machines


def _extract_member_text(struct_elem: ET.Element, member_name: str):
    node = struct_elem.find(f".//member[name='{member_name}']/value")
    if node is None:
        return None
    s = node.find("string")
    if s is not None and s.text:
        return s.text
    return "".join(node.itertext()) or None


def parse_inventory_response(root: ET.Element, uuid_inventory: str, uuid_machine: str) -> dict:
    """
    Alternative: parse an ET.Element into our normalized inventory dict.
    (Otherwise prefer MedullaAPIClient.get_inventory_dict)
    """
    try:
        hostname = _extract_member_text(root, "hostname") or "unknown"
        osname = (_extract_member_text(root, "osname") or "windows_10").lower()
        osversion = _extract_member_text(root, "osversion") or "22h2"
        manufacturer = _extract_member_text(root, "manufacturer") or "unknown"
        model = _extract_member_text(root, "model") or ""
        bios = _extract_member_text(root, "biosversion") or ""

        return {
            "machine": hostname,
            "uuid": uuid_inventory,
            "os": {
                "name": osname,
                "vendor": "microsoft" if "win" in osname else "",
                "version": osversion,
                "cpe": f"cpe:2.3:o:microsoft:{osname}:{osversion}:*:*:*:*:*:*:*"
            },
            "packages": [],
            "hardware": {
                "vendor": manufacturer,
                "model": model,
                "firmware_version": bios,
                "cpe": ""
            },
            "roles": []
        }
    except Exception as e:
        logging.error("Erreur parse_inventory_response : %s", e)
        return {}
