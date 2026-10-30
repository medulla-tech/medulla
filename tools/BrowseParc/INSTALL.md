# Installation — Parcourir mon parc

## 1. Prérequis

Sur le serveur Medulla :

| Élément | Nécessaire pour | Vérification |
|---|---|---|
| `nmap` | découverte réseau | `nmap --version` |
| `dig` | résolution inverse (noms d'hôtes) | `dig -v` |
| `pwsh` (PowerShell 7+) | découverte AD et installation WinRM | `pwsh -v` |
| module **PSWSMan** | remoting WinRM / cmdlets Active Directory | bouton *Vérifier les prérequis* — voir [§1 bis](#1-bis-prérequis-powershell-pswsman--installation) |
| `python3` | parsing des réponses PowerShell | `python3 -V` |
| client `mysql` | détection « agent déjà installé » | `mysql --version` |
| `msgfmt`, `msgcat`, `msgunfmt` | fusion des traductions française et espagnole | `which msgfmt` |

Si PSWSMan manque, la page affiche une bannière et propose de l'installer
(bouton *Installer les prérequis PowerShell*), ou en ligne de commande :

```bash
/usr/sbin/medulla-deploy-agent.sh --ps-setup
```

Cette étape nécessite un accès au dépôt PowerShell Gallery.

## 1 bis. Prérequis PowerShell (PSWSMan) — installation

### Pourquoi

Le module **PSWSMan** fournit le client WSMan utilisé par PowerShell sous Linux.
Sans lui, `Invoke-Command -ComputerName …` échoue et, par conséquent :

- la **découverte Active Directory** et la **liste des unités d'organisation** ;
- l'**installation de l'agent sur une machine Windows** (WinRM)

sont impossibles. La **découverte réseau (nmap)** et l'installation **Linux en SSH**
n'en ont pas besoin.

Il s'installe **sur le serveur Medulla** (celui qui exécute `mmc-agent`), jamais
sur les postes ni sur le poste d'administration.

### Où

PowerShell cherche ses modules dans cet ordre ; l'installation se fait dans le
premier dossier inscriptible :

```
/root/.local/share/powershell/Modules          (Install-Module sans -Scope, exécuté en root)
/usr/local/share/powershell/Modules            (Install-Module -Scope AllUsers)
/opt/microsoft/powershell/7/Modules
```

Le module est téléchargé depuis **PowerShell Gallery** (`www.powershellgallery.com`).
Sur un serveur sans accès Internet, voir la variante « dépôt interne » plus bas.

### Méthode 1 — depuis l'interface

Onglet **Admin → Parcourir mon parc**, bouton **Vérifier les prérequis**, puis
**Installer les prérequis PowerShell** dans la bannière qui s'affiche si le
client WSMan manque. La tâche est lancée en arrière-plan et son avancement est
visible dans la page.

### Méthode 2 — en ligne de commande, sur le serveur

```bash
/usr/sbin/medulla-deploy-agent.sh --ps-setup
```

Cette commande exécute, dans l'ordre :

```powershell
Register-PSRepository -Default
Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted
# -Scope AllUsers : le module va dans /usr/local/share/powershell/Modules et
# reste visible par tout processus, quel que soit son HOME.
Install-Module -Name PSWSMan -Force -AllowClobber -Scope AllUsers
Install-WSMan
```

> **Piège à connaître — `HOME` et le service `mmc-agent`.** Sans `-Scope AllUsers`,
> le module s'installe dans le **profil de l'utilisateur** qui le pose
> (`/root/.local/share/powershell/Modules`). Or `pwsh` ne cherche ce dossier que
> si **`HOME` est défini**, et le service `mmc-agent` est lancé par systemd
> **sans `HOME`**. Résultat : `pwsh` ne voyait plus le module depuis l'interface
> web et toutes les opérations Active Directory répondaient
> « The PowerShell WSMan client (PSWSMan) is missing… », alors qu'il était
> installé — et que le même contrôle lancé depuis un shell fonctionnait.
>
> Le script fournit désormais `HOME` à tous ses appels `pwsh`, et `--ps-setup`
> installe en `-Scope AllUsers`. Les deux corrections rendent le prérequis
> indépendant de l'environnement du démon.

Contrôle, **sans `HOME`**, tel que le fait le démon :

```bash
env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin \
  /usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive
# doit renvoyer "wsman":true
```

puis **revérifie** et renvoie `{"status":"ok","wsman":true}`. En cas d'échec elle
renvoie `{"status":"error","wsman":false,"message":"…"}`.

### Méthode 3 — automatisée par le playbook Ansible du serveur (recommandé)

Pour que tout serveur Medulla soit déployé avec le prérequis, ajouter ces tâches
au playbook de provisioning du serveur (idempotent : rien n'est réinstallé si
PSWSMan est déjà présent) :

```yaml
# --- Prérequis PowerShell pour le déploiement d'agents à distance -----------
# PSWSMan = client WSMan pour PowerShell sous Linux, indispensable à
#   * Invoke-Command -ComputerName (WinRM : installation de l'agent Windows)
#   * Get-ADComputer / Get-ADOrganizationalUnit (découverte Active Directory)
# À installer sur le serveur Medulla (celui qui exécute mmc-agent).
- name: Prérequis PowerShell - le module PSWSMan est-il présent ?
  ansible.builtin.command:
    cmd: >-
      pwsh -NoProfile -NonInteractive -Command
      "if (Get-Module -ListAvailable -Name PSWSMan) { exit 0 } else { exit 1 }"
  register: medulla_pswsman
  changed_when: false
  failed_when: false

- name: Prérequis PowerShell - installer PSWSMan
  when: medulla_pswsman.rc != 0
  block:
    - name: Prérequis PowerShell - déclarer et approuver PowerShell Gallery
      ansible.builtin.command:
        cmd: "pwsh -NoProfile -NonInteractive -Command "{{ item }}""
      loop:
        - Register-PSRepository -Default
        - Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted
      changed_when: true

    - name: Prérequis PowerShell - installer le module PSWSMan (tous les comptes)
      ansible.builtin.command:
        cmd: >-
          pwsh -NoProfile -NonInteractive -Command
          "Install-Module -Name PSWSMan -Scope AllUsers -Force -AllowClobber"
      changed_when: true

    - name: Prérequis PowerShell - installer le client WSMan
      ansible.builtin.command:
        cmd: pwsh -NoProfile -NonInteractive -Command "Install-WSMan"
      changed_when: true

- name: Prérequis PowerShell - contrôler le résultat
  ansible.builtin.command:
    cmd: /usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive
  register: medulla_prereq
  changed_when: false

- name: Prérequis PowerShell - échouer si le client WSMan reste absent
  ansible.builtin.fail:
    msg: "PSWSMan est toujours absent : {{ medulla_prereq.stdout }}"
  when: "'"wsman": true' not in medulla_prereq.stdout"
```

Notes :

- `-Scope AllUsers` installe dans `/usr/local/share/powershell/Modules` : le
  module est alors disponible pour **tous les comptes**, ce qui est la bonne
  pratique sur un serveur (le script Medulla, lui, installe dans le profil root).
- Une connexion sortante vers `www.powershellgallery.com` est nécessaire. Sur un
  réseau fermé, enregistrer un dépôt interne puis remplacer le nom du dépôt :

  ```yaml
      - name: Enregistrer le dépôt PowerShell interne
        ansible.builtin.command:
          cmd: >-
            pwsh -NoProfile -NonInteractive -Command
            "Register-PSRepository -Name Interne -SourceLocation https://depot.interne/psgallery
             -InstallationPolicy Trusted -PackageManagementProvider NuGet"
      - name: Installer PSWSMan depuis le dépôt interne
        ansible.builtin.command:
          cmd: >-
            pwsh -NoProfile -NonInteractive -Command
            "Install-Module -Name PSWSMan -Repository Interne -Scope AllUsers -Force -AllowClobber"
  ```

- Vérification manuelle après coup, sur le serveur :

  ```bash
  /usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive
  # attendu : {"status":"ok","prerequisites":{"pwsh":true,"wsman":true,...}}
  ```

## 2. Déploiement

Depuis le poste d'administration (le dossier `BrowseParc/` complet est requis) :

```bash
cd BrowseParc
./deploy/deploy_browseparc.sh deploy gla
```

`gla` est un alias SSH. On peut aussi passer un autre hôte, et choisir le
comportement vis-à-vis de `mmc-agent` (voir [§2 bis](#2-bis-fenêtre-de-maintenance-et-redémarrage-de-lagent)) :

```bash
./deploy/deploy_browseparc.sh deploy mon-serveur-medulla
./deploy/deploy_browseparc.sh deploy gla --no-restart      # ne jamais redémarrer l'agent
./deploy/deploy_browseparc.sh deploy gla --force-restart   # redémarrer même si rien n'a changé
```

La commande se termine avec un **code de sortie non nul** si une étape ou une
vérification échoue ; « deployed » n'est affiché que si tout est bon.

Le script :

1. construit une arborescence de staging dans `/root/browseparc-stage` sur le serveur ;
2. **sauvegarde** chaque fichier concerné dans `/root/browseparc-backup-<horodatage>/`
   (avec un `manifest.json` listant les fichiers existants ou non, leurs mode et
   propriétaire), y compris **tous** les `admin.mo` de `locale/*/LC_MESSAGES/` ;
   le chemin de la sauvegarde est enregistré dans `/root/.browseparc-state.json` ;
3. installe les nouveaux fichiers :
   - `/usr/sbin/medulla-deploy-agent.sh` (0755)
   - `/usr/lib/python3/dist-packages/mmc/plugins/admin/browseparc.py`
   - `/usr/share/mmc/modules/admin/admin/browseparc.php`
   - `/usr/share/mmc/modules/admin/admin/browseparcAjax.php`
   - `/usr/share/mmc/modules/admin/admin/browseparc_common.php`
   - `/usr/share/mmc/modules/admin/graph/js/browseparc.js`
   - `/usr/share/mmc/modules/admin/graph/css/browseparc.css`
4. patche **entre marqueurs** (opération idempotente) :
   - `modules/admin/infoPackage.inc.php` — déclaration des deux pages ;
   - `modules/admin/admin/localSidebar.php` — entrée de menu dans l'onglet Admin ;
   - `mmc/plugins/admin/__init__.py` — import du module `browseparc` (protégé par
     `try/except`, un problème de chargement ne peut pas empêcher le démarrage de l'agent) ;
5. ajoute l'entrée ACL `admin_fleet_discovery` (`admin#admin#browseparc`, `rw`)
   en une seule transaction SQL (suppression puis insertion, jamais l'une sans l'autre) ;
6. fusionne les traductions **française (`fr_FR`) et espagnole (`es_ES`)** dans
   leur `admin.mo` : à msgid égal, le texte du projet remplace l'ancien (les
   chaînes de Medulla absentes du projet et son en-tête sont conservés) ; contrôle :
   le nombre d'entrées ne peut pas diminuer, sinon l'opération est annulée ;
7. recharge `php-fpm` (unités détectées dynamiquement) et redémarre `mmc-agent`
   selon la règle de la [§2 bis](#2-bis-fenêtre-de-maintenance-et-redémarrage-de-lagent) ;
8. vérifie : présence des fichiers, `php -l` des pages, compilation Python,
   **exposition de toutes les méthodes XMLRPC**, état du service.

Si une des étapes 2 à 7 échoue, l'installation est **annulée automatiquement**
(restauration depuis la sauvegarde qui vient d'être faite) et la commande sort
en erreur. Si seule la vérification (étape 8) échoue, rien n'est annulé :
la commande sort en erreur et affiche les contrôles en échec.

Le rapport final est affiché en JSON et résumé en fin de commande.

### Exemple de sortie

```
backup      : /root/browseparc-backup-20261009-161828
translations: 373 entries (311 before)
service     : mmc-agent restart: ok
service     : mmc-agent: active
verification:
  browseparc.php                     syntax ok
  infoPackage.inc.php                patched
  localSidebar.php                   patched
  xmlrpc namespace                   EXPOSED
  mmc-agent                          active
```

Une fois déployé : reconnectez-vous à la console Medulla, onglet **Admin**,
entrée **Parcourir mon parc**.

## 2 bis. Fenêtre de maintenance et redémarrage de l'agent

Le déploiement redémarre `mmc-agent` **uniquement** dans les cas suivants :

- le module Python a changé (`browseparc.py` ou `__init__.py`) ;
- ou la version actuellement sur disque n'a jamais été chargée par l'agent
  (un déploiement précédent a écrit les fichiers puis a échoué avant le
  redémarrage ; l'empreinte du dernier redémarrage réussi est dans
  `/root/.browseparc-state.json`) ;
- ou l'agent est arrêté ;
- ou `--force-restart` est passé.

`--no-restart` désactive le redémarrage lié au module Python (l'agent arrêté
est tout de même relancé). Un déploiement de PHP, JS, CSS, traduction ou
documentation n'interrompt donc pas la console.

Quand le module Python change, le redémarrage est nécessaire et **coûteux** :

- l'agent n'écoute plus pendant quelques secondes (son socket est fermé) : les
  appels XMLRPC de la console échouent durant cet intervalle ;
- au démarrage, il réactive ses plugins **à la première requête qui en a
  besoin** ; l'activation du plugin GLPI (connexion à l'API) est coûteuse et a
  été observée **46 secondes** après le redémarrage dans les journaux ;
- avec un pool `php-fpm` petit (`pm.max_children = 5` sur le serveur de test),
  ces requêtes lentes ou les plantages de workers qui peuvent les accompagner se
  traduisent par **503 Service Unavailable** pour l'utilisateur.

> À noter : le multithreading de l'agent est **actif par défaut** (`True`,
> 20 threads) ; l'option commentée dans `config.ini` n'a aucun effet. Les blocs
> `multithreading = 1` / `maxthreads = 20` sont désormais écrits explicitement
> sur `gla` pour refléter le réglage réel.

En pratique :

- déployez **en dehors des heures d'utilisation** (c'est le seul cas gênant) ;
- ou utilisez `--no-restart` si seul le web est concerné (le module Python
  déployé ne sera alors pris en compte qu'au prochain redémarrage, ou au prochain
  déploiement qui détectera qu'il n'a jamais été chargé) ;
- `--force-restart` force le redémarrage (utile après une modification manuelle) ;
- le déploiement écrit tous les fichiers de façon **atomique** (temporaire puis
  `os.replace`) : une requête concurrente ne peut plus lire un fichier tronqué
  (le `.mo` de traduction est chargé par `mmap` dans libc, le réécrire en place
  faisait planter les workers `php-fpm`) ;
- pour rendre la console résiliente à un agent lent, il serait possible
  d'augmenter `pm.max_children` dans `/etc/php/8.2/fpm/pool.d/www.conf` (puis
  `systemctl reload php8.2-fpm`) **en tenant compte de la mémoire disponible**
  (compter ~35 Mo par worker) et d'ajouter `pm.max_requests = 500` pour recycler
  périodiquement les workers. **Sur `gla`, l'exploitant a choisi de ne pas
  modifier php-fpm.**

## 2 bis. Prise en main à distance (Guacamole)

### Prérequis serveur

| Élément | Vérification |
|---|---|
| `guacd` actif | `systemctl is-active guacd` |
| plugins guacd (rdp / ssh / vnc) | `ls /usr/lib/x86_64-linux-gnu/libguac-client-*.so` |
| webapp Guacamole derrière Apache | `curl -sk -o /dev/null -w "%{http_code}" https://127.0.0.1/guacamole/` → 200 |
| URL et identifiants du client | `grep guacamole_baseurl /etc/mmc/plugins/xmppmaster.ini /etc/mmc/plugins/xmppmaster.ini.local` |
| compte Guacamole | doit disposer de `CREATE_CONNECTION` (ou `ADMINISTER`) |

L'URL doit contenir `@@CUX_ID@@` et les identifiants du compte Guacamole :

```ini
guacamole_baseurl = https://<serveur>/guacamole/#/client/@@CUX_ID@@?username=root&password=<mot de passe>
```

### Points d'attention

- **Le mot de passe MySQL du relais est inutilisé** : `/etc/pulse-xmpp-agent/guacamoleconf.ini`
  contient un `guacamole_dbpasswd` qui ne fonctionne plus sur `gla`
  (`Access denied`). Le module passe par l'API REST, précisément pour ne pas en
  dépendre. Le corriger côté serveur est recommandé pour la cohérence.
- Les **ports de prise en main** scannés sont `22, 3389, 5985` et peuvent
  être changés avec `--discover-ports=`.
- La session est ouverte **depuis le serveur** (guacd) : la cible doit être
  joignable par le serveur sur le port du protocole.
- Les identifiants saisis dans la page sont **enregistrés dans la connexion
  Guacamole** — nécessaire pour ouvrir la session.
- L'URL de session contient les identifiants Guacamole : à ne pas diffuser.

### Vérifier une connexion créée

```bash
python3 - <<'EOF'
import configparser, json, ssl, urllib.request, urllib.parse
tpl = None
for p in ("/etc/mmc/plugins/xmppmaster.ini", "/etc/mmc/plugins/xmppmaster.ini.local"):
    c = configparser.ConfigParser(interpolation=None); c.read(p)
    for sec in c.sections():
        if c.has_option(sec, "guacamole_baseurl"): tpl = c.get(sec, "guacamole_baseurl")
creds = urllib.parse.parse_qs(tpl.split("?", 1)[1])
data = urllib.parse.urlencode({"username": creds["username"][0], "password": creds["password"][0]}).encode()
ctx = ssl._create_unverified_context()
tok = json.load(urllib.request.urlopen(urllib.request.Request(
    "https://127.0.0.1/guacamole/api/tokens", data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}), context=ctx))["authToken"]
req = urllib.request.Request("https://127.0.0.1/guacamole/api/session/data/mysql/connections",
                             headers={"Guacamole-Token": tok})
for cid, conn in json.load(urllib.request.urlopen(req, context=ctx)).items():
    print(cid, conn["name"], conn["protocol"])
EOF
```

## 2 ter. Agents déployables (agents des entités)

Le sélecteur **« Agent à déployer »** de la page liste ce que le serveur peut
réellement déployer :

| Emplacement | Contenu | Publié par Apache |
|---|---|---|
| `/var/lib/pulse2/medulla_agent/<dl_tag>/` | agents générés par entité (`Medulla-Agent-windows-FULL-latest.exe`, `Medulla-Agent-linux-MINIMAL-latest.sh`) | `/medulla_agent/<dl_tag>/…` — alias protégé par un contrôle de `Referer` |
| `/var/lib/pulse2/clients/win/install-agent.ps1` | agent générique Windows (comportement historique) | `/downloads/win/install-agent.ps1` |
| `/var/lib/pulse2/clients/lin/Medulla-Agent-linux-MINIMAL-latest.sh` | agent générique Linux | `/downloads/lin/…` |

La correspondance entre une organisation et son `dl_tag` est lue dans la table
`saas_organisations` de la base `admin` ; à défaut, le `dl_tag` sert de libellé.

### Vérifier ce qui est disponible

```bash
ls -la /var/lib/pulse2/medulla_agent/*/            # agents d'entité
ls -la /var/lib/pulse2/clients/win/ /var/lib/pulse2/clients/lin/
curl -sk -o /dev/null -w "%{http_code}\n" -H "Referer: https://<serveur>/" \
  https://<serveur>/medulla_agent/<dl_tag>/Medulla-Agent-windows-FULL-latest.exe
```

### Points d'attention

- **Le paquet Windows générique n'est pas toujours présent.** Medulla le place
  dans `medulla_agent/<dl_tag>/` : si `/downloads/win/Medulla-Agent-windows-FULL-latest.exe`
  renvoie 404, l'agent générique ne pourra pas être installé sur Windows — il
  faut choisir un agent d'entité.
- **Certificat auto-signé** : cocher *Ignorer le certificat HTTPS* dans la page
  (le téléchargement se fait depuis la machine cible). L'option est désactivée
  par défaut car elle affaiblit la vérification TLS.
- **Linux** : le fichier est transmis par SSH, aucun accès HTTP n'est nécessaire.
- Le navigateur n'envoie jamais de chemin : seulement un identifiant validé côté
  serveur.

## 3. Vérification

```bash
./deploy/deploy_browseparc.sh verify gla
```

La commande sort avec un code non nul si un contrôle échoue (`status` fait de même).

Ou directement sur le serveur (le dossier de staging n'est pas nécessaire : le
script peut être envoyé sur l'entrée standard) :

```bash
python3 /root/browseparc-stage/patch_remote.py verify
# ou, sans staging, depuis le poste d'administration :
ssh gla 'python3 - verify' < deploy/patch_remote.py
```

## 4. Retour arrière

```bash
# dernière sauvegarde (lue dans /root/.browseparc-state.json)
./deploy/deploy_browseparc.sh rollback gla

# sauvegarde précise
./deploy/deploy_browseparc.sh rollback gla /root/browseparc-backup-20261009-161828
```

Le retour arrière ne nécessite **pas** le dossier de staging. Il restaure les
fichiers sauvegardés (contenu, mode et propriétaire, **tous** les `admin.mo`),
supprime ceux qui n'existaient pas avant, retire l'entrée ACL, recharge `php-fpm`
et redémarre `mmc-agent`.

Attention : il revient à l'**état précédant le dernier déploiement**. Si une
version antérieure de BrowseParc était installée, elle est restaurée, mais
l'entrée ACL est retirée ; relancer `deploy` la recrée.

## 5. Mise à jour du script de déploiement seul

Le script est autonome. Si seul `/usr/sbin/medulla-deploy-agent.sh` doit être mis
à jour :

```bash
scp server/medulla-deploy-agent.sh mon-serveur:/usr/sbin/medulla-deploy-agent.sh
ssh mon-serveur 'chmod 755 /usr/sbin/medulla-deploy-agent.sh'
```

Aucun redémarrage n'est nécessaire (le script est lancé à chaque job).

## 6. Désinstallation complète

Le retour arrière simple (§4) **n'est pas** une désinstallation : il restaure
la dernière sauvegarde, c'est-à-dire l'état avant le dernier déploiement, ce qui
laisse BrowseParc en place si une version précédente existait. Pour tout retirer,
revenir à la **plus ancienne** sauvegarde (celle d'avant la première installation) :

```bash
OLDEST=$(ssh gla 'ls -d /root/browseparc-backup-* | head -1')
./deploy/deploy_browseparc.sh rollback gla "$OLDEST"
```

puis, si souhaité, sur le serveur :

```bash
rm -rf /var/lib/medulla/browseparc      # historique des jobs et groupes
rm -rf /root/browseparc-stage /root/browseparc-backup-*
```

## 7. Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| L'entrée de menu n'apparaît pas | patchs non appliqués ou cache | `patch_remote.py verify`, vérifier `infoPackage.inc.php` et `localSidebar.php`, vider le cache navigateur |
| « Agent MMC injoignable » | `mmc-agent` arrêté | `systemctl status mmc-agent` |
| « le client WSMan (PSWSMan) est absent » | prérequis PowerShell | bouton *Installer les prérequis PowerShell* |
| Découverte AD : erreur d'authentification | compte sans droit de lecture AD | vérifier le compte, le domaine NetBIOS et le nom du contrôleur |
| Installation Windows : échec systématique | WinRM non activé sur la cible | activer WinRM (`winrm quickconfig`) côté Windows |
| Rien ne remonte en découverte réseau | port filtré ou mauvais port | tester avec `--port=22` (SSH) ou `--port=5985` (WinRM) |
| Jobs bloqués en « en cours » | processus tué | les jobs terminés sont détectés automatiquement ; annuler puis relancer |
| **503 Service Unavailable** sur toute la console | 1) un déploiement vient de redémarrer `mmc-agent` et l'activation paresseuse de ses plugins bloque le réacteur ; 2) ou un appel bloquant (l'option `multithreading` de `/etc/mmc/agent/config.ini` est commentée : les méthodes s'exécutent dans le réacteur Twisted) ; dans les deux cas, saturation des workers `php-fpm` (`pm.max_children = 5`) | vérifier `grep -i proxy_fcgi /var/log/apache2/error.log` ; cette fonctionnalité ne bloque jamais, mais si un autre module le fait : `systemctl restart mmc-agent`. Recommandé : activer `multithreading = 1` dans `/etc/mmc/agent/config.ini` puis `systemctl restart mmc-agent` |
