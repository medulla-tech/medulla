import time
import logging
import requests
from itertools import combinations
from packaging import version as packaging_version


class CVEChecker:
    """
    Recherche CVE par mot-clé (avec variantes) + fallback CPE,
    pagination NVD, déduplication par ID, et match de versions
    (bornes inclusives/exclusives + match exact depuis CPE criteria).
    """

    def __init__(self, api_key: str, verbose: bool = False, *, timeout: int = 12):
        self.api_key = api_key
        self.verbose = verbose
        self.timeout = timeout
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cpe_url = "https://services.nvd.nist.gov/rest/json/cpes/2.0"

        self.session = requests.Session()
        # NVD accepte apiKey dans header ou query param; header suffit.
        self.session.headers.update({"apiKey": self.api_key, "Accept": "application/json"})

    # ==============================
    # Helpers HTTP / NVD
    # ==============================
    def _http_get(self, url: str, params: dict, *, max_retries: int = 3, backoff: float = 1.0):
        """
        GET avec petit backoff sur 429/5xx. Retourne JSON dict (ou None).
        """
        for attempt in range(1, max_retries + 1):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (429, 500, 502, 503, 504):
                    if self.verbose:
                        print(f"[DEBUG] NVD {r.status_code}, retry {attempt}/{max_retries}...")
                    time.sleep(backoff * attempt)
                    continue
                # autre code → log et stop
                logging.warning("NVD GET %s params=%s → HTTP %s body=%s",
                                url, params, r.status_code, r.text[:300])
                return None
            except requests.RequestException as e:
                if attempt == max_retries:
                    logging.warning("[ERROR] NVD GET failed after retries: %s", e)
                    return None
                if self.verbose:
                    print(f"[DEBUG] Exception {e}, retry {attempt}/{max_retries}...")
                time.sleep(backoff * attempt)
        return None

    def _query_nvd_cves_paginated(self, params: dict, *, max_pages: int = 3, results_per_page: int = 200):
        """
        Récupère plusieurs pages côté CVE (jusqu’à max_pages). Déduplique à la fin.
        """
        params = dict(params)  # copy
        params.setdefault("resultsPerPage", results_per_page)
        params.setdefault("startIndex", 0)

        seen_ids = set()
        agg = []
        for _ in range(max_pages):
            data = self._http_get(self.base_url, params)
            if not data:
                break
            items = data.get("vulnerabilities", []) or []
            if not items:
                break
            for it in items:
                cve_id = (it.get("cve", {}) or {}).get("id")
                if not cve_id or cve_id in seen_ids:
                    continue
                seen_ids.add(cve_id)
                agg.append(it)

            total = data.get("totalResults")
            if total is not None and params["startIndex"] + params["resultsPerPage"] >= total:
                break
            params["startIndex"] += params["resultsPerPage"]
        return agg

    def _search_cpes(self, keyword: str, *, limit: int = 50):
        """
        Fallback CPE: map nom → CPE; on retourne une liste de cpeName uniques.
        """
        params = {"keyword": keyword, "resultsPerPage": limit}
        data = self._http_get(self.cpe_url, params)
        if not data:
            return []
        products = data.get("products", []) or []
        out = []
        seen = set()
        for p in products:
            c = p.get("cpe", {}) or {}
            name = c.get("cpeName")
            if name and name not in seen:
                seen.add(name)
                out.append(name)
        if self.verbose:
            print(f"[DEBUG] 🔁 CPE fallback {keyword} → {len(out)} CPEs")
        return out

    # ==============================
    # Variantes mots-clés
    # ==============================
    def generate_keyword_variants(self, keyword: str):
        """
        Variantes n-gram, dash/space, quelques alias connus.
        """
        base = (keyword or "").strip().lower()
        if not base:
            return []

        # normalisation simple
        norm = base.replace("_", "-").replace(".", "-").replace(":", " ")
        parts = [p for p in norm.split("-") if p]

        variants = set([base, norm])
        # n-grams (1..n)
        for i in range(1, len(parts) + 1):
            for combo in combinations(parts, i):
                joined = " ".join(combo)
                variants.add(joined)
                variants.add(joined.replace(" ", "-"))

        # alias log4j
        if "log4j" in base:
            variants.update({
                "apache log4j", "apache log4j2", "log4j2",
                "org.apache.logging.log4j", "log4j-core", "log4j api", "apache logging"
            })

        # quelques lib courantes
        alias_map = {
            "openssl": {"openssl", "libssl"},
            "curl": {"curl", "libcurl"},
            "linux kernel": {"linux kernel", "linux_kernel", "kernel"},
        }
        for k, al in alias_map.items():
            if k in base:
                variants |= set(al)

        return list(variants)

    # ==============================
    # Entrées CVE
    # ==============================
    def get_cves_for_package(self, keyword: str, *, results_per_page: int = 200, max_pages: int = 2):
        """
        Recherche par mot-clé (toutes variantes) puis fallback CPE, dédupliqué.
        """
        seen_ids = set()
        agg = []

        # 1) par mots-clés
        for kw in self.generate_keyword_variants(keyword):
            cves = self._query_nvd_cves_paginated(
                {"keywordSearch": kw}, max_pages=max_pages, results_per_page=results_per_page
            )
            for it in cves:
                cve_id = (it.get("cve", {}) or {}).get("id")
                if cve_id and cve_id not in seen_ids:
                    seen_ids.add(cve_id)
                    agg.append(it)

        if self.verbose:
            print(f"[DEBUG] 🔎 keywords({keyword}) → {len(agg)} uniques")

        # 2) fallback via CPE (si pas/peu de résultat)
        if len(agg) < 5:
            for cpe in self._search_cpes(keyword):
                cves = self._query_nvd_cves_paginated(
                    {"cpeName": cpe}, max_pages=max_pages, results_per_page=results_per_page
                )
                for it in cves:
                    cve_id = (it.get("cve", {}) or {}).get("id")
                    if cve_id and cve_id not in seen_ids:
                        seen_ids.add(cve_id)
                        agg.append(it)

        if self.verbose:
            print(f"[DEBUG] 🔎 total({keyword}) → {len(agg)} uniques (kw + cpe)")
        return self._extract_cve_metadata(agg, keyword)

    def get_cves_by_cpe(self, cpe: str, *, results_per_page: int = 200, max_pages: int = 2):
        cves = self._query_nvd_cves_paginated(
            {"cpeName": cpe}, max_pages=max_pages, results_per_page=results_per_page
        )
        return self._extract_cve_metadata(cves, cpe)

    # ==============================
    # Parsing / Normalisation
    # ==============================
    def _parse_cpe_version(self, cpe_23: str):
        """
        Extrait la composante version d’un CPE 2.3 (index 5).
        """
        if not cpe_23 or not cpe_23.startswith("cpe:2.3:"):
            return None
        try:
            parts = cpe_23.split(":")
            # cpe:2.3:a:vendor:product:version:...
            if len(parts) >= 6:
                ver = parts[5]
                return None if ver in ("*", "-", "") else ver
        except Exception:
            return None
        return None

    def _best_severity_and_score(self, metrics: dict):
        """
        Sélectionne la meilleure sévérité/score dispo (préf. v3.1, sinon v3.0, sinon v2).
        Si plusieurs entrées, on prend le score max et la sévérité la plus haute vue.
        """
        order = ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2")
        score = 0.0
        severity = "UNKNOWN"
        for key in order:
            for m in metrics.get(key, []) or []:
                data = m.get("cvssData", {}) or {}
                s = data.get("baseScore")
                sev = (m.get("baseSeverity") or severity or "UNKNOWN").upper()
                if s is not None and (score is None or s > score):
                    score = float(s)
                    severity = sev
                else:
                    # si pas de meilleur score mais meilleure sévérité visible
                    if severity == "UNKNOWN" and sev != "UNKNOWN":
                        severity = sev
        return (score or 0.0), (severity or "UNKNOWN").upper()

    def _extract_cve_metadata(self, cve_items, raw_name: str):
        """
        Transforme les items NVD en structure plate avec métadonnées utiles.
        """
        results = []
        for item in cve_items or []:
            cve_data = item.get("cve", {}) or {}
            cve_id = cve_data.get("id")
            if not cve_id:
                continue

            # description EN
            description = ""
            for d in cve_data.get("descriptions", []) or []:
                if d.get("lang") == "en" and d.get("value"):
                    description = d["value"]
                    break

            # metrics → score/sévérité
            metrics = cve_data.get("metrics", {}) or {}
            score, severity = self._best_severity_and_score(metrics)

            # CWE
            cwes = []
            for w in cve_data.get("weaknesses", []) or []:
                for desc in w.get("description", []) or []:
                    val = desc.get("value")
                    if val and val not in cwes:
                        cwes.append(val)

            # versions
            version_ranges = []
            for config in cve_data.get("configurations", []) or []:
                for node in config.get("nodes", []) or []:
                    for match in node.get("cpeMatch", []) or []:
                        if match.get("vulnerable"):
                            version_ranges.append({
                                "cpe": match.get("criteria"),
                                "versionStartIncluding": match.get("versionStartIncluding"),
                                "versionStartExcluding": match.get("versionStartExcluding"),
                                "versionEndIncluding": match.get("versionEndIncluding"),
                                "versionEndExcluding": match.get("versionEndExcluding"),
                            })

            results.append({
                "id": cve_id,
                "description": description,
                "score": score or 0.0,
                "severity": (severity or "UNKNOWN").upper(),
                "cwes": cwes,
                "published": cve_data.get("published"),
                "lastModified": cve_data.get("lastModified"),
                "source": cve_data.get("sourceIdentifier"),
                "version_ranges": version_ranges,
                "raw_name": (raw_name or "").lower(),
            })
        return results

    # ==============================
    # Matching de version
    # ==============================
    def is_version_in_range(self, version_str, start_inc=None, end_exc=None, *, start_exc=None, end_inc=None):
        """
        Compare version_str à une plage (bornes inclusives/exclusives).
        On tolère '*' en le remplaçant par 0 (approximation).
        """
        try:
            if not version_str:
                return False
            v = packaging_version.parse(str(version_str).replace("*", "0"))
            if start_inc and v < packaging_version.parse(str(start_inc).replace("*", "0")):
                return False
            if start_exc and v <= packaging_version.parse(str(start_exc).replace("*", "0")):
                return False
            if end_exc and v >= packaging_version.parse(str(end_exc).replace("*", "0")):
                return False
            if end_inc and v > packaging_version.parse(str(end_inc).replace("*", "0")):
                return False
            return True
        except Exception:
            return False

    def _match_against_ranges_or_exact_cpe(self, pkg_version: str, ranges: list) -> bool:
        """
        True si pkg_version match au moins une plage OU est égal à la version
        précise présente dans un CPE criteria.
        """
        if not ranges:
            return True
        for vr in ranges:
            # 1) match plage
            if self.is_version_in_range(
                pkg_version,
                vr.get("versionStartIncluding"),
                vr.get("versionEndExcluding"),
                start_exc=vr.get("versionStartExcluding"),
                end_inc=vr.get("versionEndIncluding"),
            ):
                return True
            # 2) match exact version dans criteria (si renseigné)
            cpe = vr.get("cpe")
            exact = self._parse_cpe_version(cpe)
            if exact:
                try:
                    if packaging_version.parse(pkg_version) == packaging_version.parse(exact):
                        return True
                except Exception:
                    # fallback basique si version exotique
                    if pkg_version == exact:
                        return True
        return False

    # ==============================
    # API publique
    # ==============================
    def check_package_vuln(
        self,
        name_or_cpe: str,
        version: str = "",
        *,
        min_cvss: float = 0.0,
        severities=None,
        assume_unknown_version_vulnerable: bool = True,
    ):
        """
        Retourne la liste des CVE filtrées pour un package/CPE donné.
        - agrège mot-clé + CPE fallback (si non CPE)
        - filtre score/sévérité
        - match versions (plages/exactes)
        - si version inconnue, peut (optionnel) considérer vulnérable par défaut
        """
        is_cpe = (name_or_cpe or "").startswith("cpe:")
        cves = self.get_cves_by_cpe(name_or_cpe) if is_cpe else self.get_cves_for_package(name_or_cpe)

        filtered = []
        for cve in cves:
            score = float(cve.get("score") or 0.0)
            severity = (cve.get("severity") or "UNKNOWN").upper()

            if score < min_cvss:
                continue
            if severities and severity not in severities:
                continue

            # Version inconnue → stratégie configurable
            if not version:
                if assume_unknown_version_vulnerable:
                    filtered.append({**cve, "match": "version_unknown"})
                else:
                    # n'ajouter que si le nom apparaît au moins dans le contexte
                    rn = (cve.get("raw_name") or "")
                    if name_or_cpe.lower() in rn or name_or_cpe.lower() in (cve.get("description", "").lower()):
                        filtered.append({**cve, "match": "name_match_only"})
                continue

            # Version connue → vérifier plage / exact cpe
            if self._match_against_ranges_or_exact_cpe(version, cve.get("version_ranges") or []):
                filtered.append({**cve, "match": "range_or_exact"})

        # tri: sévérité puis score desc puis id
        sev_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
        filtered.sort(key=lambda x: (sev_order.get(x.get("severity", "UNKNOWN"), 0), x.get("score", 0.0), x.get("id", "")), reverse=True)

        if self.verbose:
            print(f"[DEBUG] {name_or_cpe} ({version or '⊘'}) → {len(filtered)} CVEs filtrées")
        return filtered

    def check_machine_vuln(self, inventory_path: str, *, min_cvss: float = 0.0, severities=None):
        """
        Lit un inventaire JSON (OS + packages) et renvoie un dict:
        { "machine": ..., "cve_results": [...] }
        """
        import json
        with open(inventory_path, "r", encoding="utf-8") as f:
            machine = json.load(f)

        results = []
        os_info = machine.get("os", {}) or {}
        if os_info.get("cpe"):
            results.extend(self.check_package_vuln(os_info["cpe"], os_info.get("version", ""), min_cvss=min_cvss, severities=severities))

        kernel = machine.get("kernel")
        if kernel:
            results.extend(self.check_package_vuln("linux kernel", kernel, min_cvss=min_cvss, severities=severities))

        # Packages
        for pkg in machine.get("packages", []) or []:
            name = pkg.get("name")
            version = pkg.get("version", "")
            if not name:
                continue
            results.extend(self.check_package_vuln(name, version, min_cvss=min_cvss, severities=severities))

        # Matériel
        hw = machine.get("hardware", {}) or {}
        if hw.get("cpe"):
            results.extend(self.check_package_vuln(hw["cpe"], hw.get("firmware_version", ""), min_cvss=min_cvss, severities=severities))

        return {
            "machine": machine.get("machine", "unknown"),
            "cve_results": results,
        }
