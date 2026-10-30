# Rapport de test — Parcourir mon parc

Date : 2026-10-09
Serveur de validation : `gla` (gla.medulla-tech.io, Debian 12, PHP 8.2/php-fpm)
Version Medulla : **5.6.5** (l'intégration a d'abord été validée en 5.5.2 ;
la migration est décrite au § 12)

## Synthèse

| Suite | Emplacement | Exécution | Résultat |
|---|---|---|---|
| `tests/test_browseparc.py` | poste de dev | locale | **132 / 132** |
| `tests/test_patches.py` | poste de dev | locale | tous OK (voir la sortie du test) |
| `tests/test_powershell_blocks.py` | poste de dev | locale | **21 / 21** |
| `tests/test_ad_ou_parser.py` | poste de dev | locale | **21 / 21** |
| `tests/test_render_js.js` | poste de dev | node | **62 / 62** |
| `tests/test_ui_on_server.sh` | serveur | `gla` | **72 / 72** |
| `tests/test_guacamole_session.py` | serveur | `gla` | **23 / 23** |
| `tests/test_backend_on_server.py` | serveur | `gla` | **71 / 71** |
| `tests/test_load_on_server.py` | serveur | `gla` | **8 / 8** |
| **Total** | | | **446 / 446** |

## 1. Tests unitaires du backend — 132 / 132

`python3 tests/test_browseparc.py`

Le module `browseparc.py` est testé isolément, avec un script de déploiement
factice (`tests/fake_deploy_agent.py`) et un répertoire de travail temporaire.

Couverture :

- **validation des entrées** : CIDR, IP, FQDN acceptés ; `;`, backticks,
  `$(...)`, CIDR `/99`, ports hors plage, noms de groupes avec `../` ou `/`
  refusés ;
- **cycle de vie d'un job** : démarrage, statut, progression, machines
  remontées, drapeau « déjà équipé » ;
- **mot de passe** : circule par l'environnement (`password-in-env=True` dans le
  journal), absent de `request.json`, absent de la commande enregistrée, absent
  de **tous** les fichiers du job ;
- **installation** : agrégation succès/échec (1 ok / 1 ko) et détail par machine ;
- **liste des OU** Active Directory ;
- **refus** : action inconnue, cible invalide, AD sans serveur, installation sans
  machine, machine invalide ;
- **groupes de ciblage** : création, dédoublonnage, liste, relecture,
  remplacement, suppression, nom invalide refusé ;
- **résolution d'UUID** : machine connue / inconnue ;
- **annulation** d'un job en cours : le processus est bien arrêté ;
- **statut d'un job inconnu** ou avec identifiant invalide refusé.

## 2. Tests des patchs et de la logique de déploiement

`python3 tests/test_patches.py`

Les patchs sont appliqués sur les **fichiers réels du serveur** conservés dans
`reference/gla/`, ce qui valide les ancres de remplacement.

- `infoPackage.inc.php` : ancre `$mod->addSubmod($submod);` unique avant et après,
  déclaration des deux pages, option `AJAX` posée, **idempotence** vérifiée ;
- `localSidebar.php` : entrée de menu ajoutée, idempotence ;
- `__init__.py` du plugin : import ajouté, protégé par `try/except` avec
  journalisation, le fichier patché **compile** ;
- module `browseparc.py` : les 11 méthodes attendues figurent dans `__all__` et
  sont appelables (ensemble exact vérifié) ;
- fusion des traductions : le texte du projet l'emporte sur l'ancien, l'en-tête
  de Medulla est conservé, `install_translations` renvoie toujours
  `(rapport, modifié)` ;
- sauvegarde / rollback de tous les `admin.mo` (modes conservés, sans staging) ;
- échec d'une étape d'installation → rollback et erreur ; `--no-restart` /
  `--force-restart` ; ACL en une transaction ; citation du fichier d'options MySQL ;
- le script de déploiement embarque bien tous les fichiers nécessaires.

## 3. Tests d'interface — 33 / 33

`bash tests/test_ui_on_server.sh /root/browseparc-stage` (sur le serveur)

> La connexion web de cette instance passe par OIDC/GLPI : aucune session MMC ne
> peut être obtenue par script. La page est donc **réellement rendue par PHP**
> avec un amorçage MMC minimal (`tests/bp_render_test.php`) qui n'enregistre que
> le module `admin` et n'appelle pas l'agent. `bp_render_test.php` impose de
> démarrer PHP avec `-d short_open_tag=1`, comme le fait php-fpm.

- **rendu** : aucune erreur fatale, aucun avertissement lié à la page ;
- **menu** : `<li id="browseparc" class="active">` présent dans la barre latérale
  de l'onglet Admin, lien vers `action=browseparc` ;
- **contenu** : conteneur de page, script client, feuille de style, boutons de
  découverte et d'installation, les trois tableaux (machines, groupes, tâches) ;
- **traduction** : 8 libellés français vérifiés dans le HTML rendu
  (« Parcourir mon parc », « Découvrir le parc », « Machines trouvées »,
  « Groupes de ciblage », « Tâches récentes », « Unité d'organisation »,
  « Identifiant », « Installer l'agent sur la sélection ») ;
- **endpoint AJAX** : JSON pour une commande inconnue, message traduit, aucune
  page HTML d'erreur ;
- **contrôle d'accès** : utilisateur sans droit → `Accès refusé` ; avec le droit
  `admin#admin#browseparc` → la commande est traitée ;
- **CSRF** : POST sans jeton rejeté, aucune réponse ;
- **ressources statiques** : `browseparc.js` et `browseparc.css` servis en HTTP 200 ;
- **exposition XMLRPC** : les 11 méthodes sont présentes dans le namespace du
  plugin `admin` chargé par l'agent ;
- **script** : `--check-prereq`, `--uuid-lookup` (1 machine connue sur 2) et une
  découverte réseau réelle sur `127.0.0.1/32` (JSON valide, 1 machine).

## 3 bis. Blocs PowerShell — 9 / 9

`python3 tests/test_powershell_blocks.py`

- les 4 blocs PowerShell extraits du script sont **valides une fois repliés sur
  une ligne** (analyse par `[Parser]::ParseInput`, rien n'est exécuté) ;
- `ps_run` replie bien les sauts de ligne, avec le commentaire explicatif ;
- le test **démontre la cause du bug** : le même `try/catch` sur plusieurs lignes
  ne produit aucun résultat, sur une seule ligne il fonctionne.

## 4. Tests de bout en bout serveur — 42 / 42

`python3 tests/test_backend_on_server.py` (sur le serveur)

Ce test appelle les fonctions **telles que l'agent les expose** (import du plugin
`mmc.plugins.admin`) et déclenche le **vrai** script `/usr/sbin/medulla-deploy-agent.sh`.

- exposition des 11 méthodes ;
- rapport de prérequis : `{"pwsh": true, "wsman": false, "nmap": true,
  "python3": true, "mysql": true, "dig": true}` ;
- **découverte réseau réelle** sur `127.0.0.1/32` : job démarré, terminé, machine
  remontée avec nom, IP et état d'installation, progression cohérente ;
- **découverte d'une plage CIDR** `172.16.12.140/30` : résultat
  `srv-win25-01.medulla.lan / 172.16.12.141` — la machine Windows du parc de test
  est correctement détectée via nmap puis résolue en nom par DNS inverse ;
- **refus** : injection shell (`127.0.0.1; id`), action inconnue, identifiant de
  job avec traversée, nom de groupe avec traversée ;
- **groupes** : enregistrement, présence dans la liste, relecture, suppression ;
- **résolution d'UUID** : `gla-w11-1` (machine connue de Medulla) résolue,
  machine inconnue signalée ;
- **installation WinRM sans client WSMan** : le job échoue proprement avec un
  message explicite mentionnant WSMan ;
- **le mot de passe n'est jamais persisté** : parcours de tous les fichiers de
  `/var/lib/medulla/browseparc` ;
- **le bloc PowerShell Active Directory s'exécute réellement** (régression) :
  avec des identifiants invalides, le listage des OU renvoie
  `Authorization failed` — et non « No JSON answer » comme avant la correction ;
- **la cause d'un échec d'installation remonte dans le journal** de la tâche ;
- **l'état réel des prérequis** est relu hors cache et affiché
  (`{"pwsh": true, "wsman": true, "nmap": true, "python3": true, "mysql": true, "dig": true}`).

## 5. Test de charge — non-blocage de la console — 8 / 8

`python3 tests/test_load_on_server.py` (sur le serveur)

Ce test reproduit la panne constatée et vérifie qu'elle ne peut plus se produire.

- `browse_parc_prerequisites()` rend la main en **moins de 1 s** (constaté 0,000 s,
  servi depuis le cache) ;
- une **découverte lancée sur `172.16.12.0/24`** (job long) tourne pendant que
  **36 requêtes HTTP** sont envoyées aux pages de la console
  (`index.php`, la nouvelle page, `relaysList`) :
  **latence maximale 0,003 s, aucune réponse en erreur, aucun 503** ;
- `browse_parc_status()` reste sous la seconde pendant le job ;
- l'annulation fonctionne et le statut final est bien **`cancelled`** ;
- aucun nouveau segfault `php-fpm` pendant l'épreuve.

## 6. Incident du 09/10/2026 — analyse et correction

| Élément | Détail |
|---|---|
| Symptôme | « Service Unavailable » (503) sur toute la console MMC, plus aucun accès |
| Cause racine (analyse initiale, **corrigée depuis**) | L'analyse initiale attribuait la panne au fait que `multithreading` est commenté dans `/etc/mmc/agent/config.ini`, ce qui aurait fait exécuter les méthodes dans le réacteur Twisted. **Cette analyse était fausse** : voir la section *Correction de l'analyse* ci-dessous. Le point réellement établi est que la page appelait `browse_parc_prerequisites()` à chaque chargement, qui lançait `pwsh` de façon synchrone — un défaut de conception corrigé indépendamment de la cause du 503. |
| Preuves | `proxy_fcgi:error AH01067 Failed to read FastCGI header` / `AH01075 Connection reset by peer` dans `/var/log/apache2/error.log` ; `pm.max_children = 5` dans `/etc/php/8.2/fpm/pool.d/www.conf` ; `#multithreading = 1` dans `/etc/mmc/agent/config.ini` ; appels `subprocess` synchrones dans le module |
| Correction | La méthode de prérequis ne bloque plus : **cache disque** (TTL 300 s) rafraîchi par un **processus détaché**. La résolution des UUID devient une **tâche de fond**. La sonde WSMan est bornée par `timeout 25`. |
| Vérification | Suite de charge ci-dessus : **36 requêtes HTTP pendant un job long, latence max 0,003 s, 0 échec**. Test de non-régression : prérequis rendus en 0,000 s sur le serveur. |
| État | Console MMC de nouveau accessible (HTTP 200 sur `https://gla.medulla-tech.io/mmc/`) |

> Les **2 segfaults `php-fpm`** observés (`segfault ... in libc.so.6`) n'ont pas
> pu être reproduits (10 requêtes sur la page de connexion, 10 sur la page
> admin, aucun nouveau plantage) et ne sont pas corrélés à cette
> fonctionnalité ; le `.mo` régénéré a été vérifié (`msgfmt --check` valide, 373
> entrées, aucun msgid en double). À surveiller.

## 6 bis. Second incident — blocs PowerShell jamais exécutés

| Élément | Détail |
|---|---|
| Symptôme | Découverte Active Directory et listage des OU en échec avec « No JSON answer from the Active Directory server » ; installation WinRM échouant sans explication |
| Cause racine | `pwsh -Command -` **lit son entrée ligne par ligne** : un bloc multi-ligne (`try { … } catch { … }`) n'est jamais exécuté et ne produit **aucune sortie**. Le problème était intermittent selon l'arrivée des données dans le tube, ce qui explique qu'il soit passé inaperçu aux premiers tests. |
| Preuves | Trace `bash -x` montrant `OUT='[?1h[?1h…'` (uniquement des séquences terminal, aucun JSON) ; test minimal : `try {
 throw "boom"
} catch {…}` via stdin → **aucune sortie**, la même sur une ligne → `CAUGHT`. |
| Correction | Blocs PowerShell réécrits avec des séparateurs `;` explicites ; `ps_run` replie les sauts de ligne avant l'envoi (une seule ligne sur stdin). |
| Vérification | Découverte AD et `--list-ous` renvoient maintenant `Authorization failed` (connexion au DC établie, seuls les identifiants manquent) ; test de non-régression local et serveur. |

## 6 ter. Prérequis PowerShell (PSWSMan)

Installé sur `gla` à la demande : **PSWSMan 2.3.1**, dans
`/root/.local/share/powershell/Modules/PSWSMan/2.3.1`.

| Contrôle | Résultat |
|---|---|
| `--check-prereq` | `{"pwsh": true, "wsman": true, "nmap": true, "python3": true, "mysql": true, "dig": true}` |
| `Invoke-Command -ComputerName 172.16.12.141` (identifiants bidon) | avant : « no supported WSMan client library was found » → après : **« Authorization failed »** (la connexion au contrôleur de domaine est établie) |
| `--ps-setup` sans identifiants | `{"status":"ok","wsman":true}` (le mode exigeait auparavant un compte, ce qui faisait échouer le bouton de la page) |

Procédure d'installation (interface, ligne de commande, tâche Ansible) :
[INSTALL.md, §1 bis](../INSTALL.md#1-bis-prérequis-powershell-pswsman--installation).

## 6 quater. Troisième incident — redémarrage inutile du mmc-agent

| Élément | Détail |
|---|---|
| Symptôme | 503 récurrent sur `GET /mmc/main.php`, y compris après reconnexion de l'utilisateur |
| Cause racine | Le déploiement redémarrait **systématiquement** `mmc-agent`. Au démarrage, l'agent réactive ses plugins paresseusement : la première requête déclenchant l'activation du plugin GLPI (session API) bloque le réacteur Twisted plusieurs dizaines de secondes. Avec `pm.max_children = 5`, les requêtes parallèles du navigateur saturent le pool → **503**. |
| Preuves | `ActiveEnterTimestamp=17:39:51` (redémarrage par le déploiement) ; journal de l'agent : `17:39:55 Listening to XML-RPC requests` puis `17:40:41 [PluginConfig] Backend ini file activé pour glpi` ; journal Apache : 503 à `17:40:41` et `17:40:44`. Journal d'accès : séquence de l'utilisateur `browseparc 302 → main.php 200 → index.php?agentsessionexpired=1 → POST index.php 302 → main.php 503`. |
| Reproduction | Impossible à reproduire hors redémarrage : 12 requêtes parallèles sur `main.php` avec session → **12 × 200 en 6 ms**, aucun segfault ; 20 requêtes séquentielles (session expirée et valide) → 200/302, aucun segfault. |
| Correction | `patch_remote.py` compare les empreintes SHA-256 de `browseparc.py` et `__init__.py` : l'agent n'est **redémarré que si le module Python a changé**. Options `--force-restart` / `--no-restart`. |
| Vérification | Redéploiement à 17:42:54 : rapport « **mmc-agent laisse en service (module python inchange)** », `ActiveEnterTimestamp` inchangé (17:39:51). |

### Contexte serveur (mesuré)

| Ressource | Valeur |
|---|---|
| Mémoire | 7,8 Go au total, **7,0 Go utilisés, 818 Mo disponibles**, pas de swap |
| Principaux consommateurs | `mariadbd` 3,3 Go, agents Medulla 1,3 Go, cortex-ia 789 Mo, java 262 Mo, `mmc-agent` 179 Mo |
| CPU | 2 cœurs |
| `php-fpm` | `pm.max_children = 5`, `pm.max_requests` **non défini** (workers jamais recyclés), pas de `request_terminate_timeout` |
| Segfaults php-fpm | 4 observés au total, non reproduits en 32 requêtes contrôlées ; deux causes possibles : réécriture non atomique de `admin.mo` (corrigée) et `pm.max_requests = 0` (workers jamais recyclés, non modifié sur décision de l'exploitant) |

> **Recommandation** : la mémoire disponible (818 Mo) ne permet pas d'augmenter
> fortement `pm.max_children` (~35 Mo par worker). Un passage de 5 à 8 workers et
> l'ajout de `pm.max_requests = 500` (aucun coût mémoire, recycle les workers)
> rendraient la console nettement plus résiliente à un agent lent.
> **Décision de l'exploitant : ne rien changer côté php-fpm.**

## 6 quinquies. Correction de l'analyse : le multithreading était déjà actif

L'analyse de l'incident 16:33 attribuait les 503 au fait que `multithreading` est
commenté dans `/etc/mmc/agent/config.ini`, en concluant que les méthodes des
plugins s'exécutaient dans le réacteur Twisted. **La lecture du code de l'agent
montre que c'est faux** :

```python
config.multithreading = True          # valeur par défaut
config.maxthreads = 20
try:
    config.multithreading = config.getboolean("main", "multithreading")
    config.maxthreads = config.getint("main", "maxthreads")
except configparser.NoOptionError:
    pass                              # clé absente → le défaut (True) est conservé
```

L'option étant commentée, `NoOptionError` est levée et **le défaut `True` est
conservé** : le multithreading était donc **déjà actif** (pool de 20 threads).
Sur `gla`, `multithreading = 1` et `maxthreads = 20` ont été rendus explicites
dans la configuration (sans redémarrage : la valeur effective est inchangée).

### Ce qui reste vrai

- **Les 503 sont réels et documentés** par `AH01067 Failed to read FastCGI header`
  / `AH01075 Connection reset by peer` : ce sont des **workers php-fpm qui
  meurent en cours de requête**, pas un pool saturé par un agent gelé.
- **Deux causes identifiées et corrigées** :
  1. le déploiement redémarrait l'agent à chaque fois (corrigé en 1.0.3 :
     redémarrage conditionnel sur empreinte SHA-256) ;
  2. les fichiers étaient réécrits **en place** pendant que des requêtes
     tournaient — `admin.mo` étant chargé par `mmap` dans libc, un remplacement
     concurrent fait planter le worker (corrigé en 1.0.4 : écriture temporaire +
     `os.replace`, atomique).
- **Les bonnes pratiques du module restent justifiées** : aucune méthode ne
  bloque (jobs détachés, cache de prérequis), ce qui le rend correct même si
  `multithreading` est un jour désactivé et évite d'occuper les threads du pool.

## 6 sexies. Choix de l'agent à déployer (agents des entités)

### Mécanisme retrouvé dans le code Medulla

| Élément | Emplacement |
|---|---|
| Page de téléchargement | `modules/admin/admin/downloadAgent.php` → `downloadAgentFile.php` |
| Correspondance organisation → agent | table `admin.saas_organisations` (`tag_name` → `dl_tag`) via `admin.get_dl_tag` |
| Dépôt des paquets | `/var/lib/pulse2/medulla_agent/<dl_tag>/` |
| Publication HTTP | `Alias /medulla_agent /var/lib/pulse2/medulla_agent/` (contrôle de `Referer`) et `Alias /downloads /var/lib/pulse2/clients/` |
| Installation Windows | `install-agent.ps1` télécharge le `.exe` puis `Start-Process /S` |

### Vérifications effectuées sur `gla`

| Contrôle | Résultat |
|---|---|
| Détection des agents | **1 agent d'entité** (`0e1ab1d2…`, Windows + Linux, 2026-05-04) + **1 agent générique** (Windows) |
| URL de base déduite | `https://gla.medulla-tech.io` (lue dans `install-agent.ps1`) |
| Téléchargement de l'agent d'entité | `206`/`200` **avec** l'en-tête `Referer`, `403` sans (protection Apache confirmée) |
| `Invoke-WebRequest` avec en-tête | `OK 200`, taille 9791 octets |
| Paquet Windows générique | **absent** : `/downloads/win/Medulla-Agent-windows-FULL-latest.exe` → 404 |
| Script Linux générique | **absent** : `clients/lin/Medulla-Agent-linux-MINIMAL-latest.sh` |
| Script généré pour l'agent choisi | une ligne, PowerShell valide, contient URL + `Referer` + `/S` (+ contournement TLS si demandé) |
| Refus d'un identifiant inconnu | `entity:../../etc/passwd` et `entity:/etc/shadow` → refusés |
| Validation non intrusive | `--check-prereq` et `--discover` fonctionnent même si le chemin Linux par défaut est absent (régression corrigée) |

> **Conclusion** : sur `gla`, seul **l'agent de l'entité** est réellement
> déployable (les paquets génériques sont absents du serveur). Le sélecteur
> répond donc directement au besoin.

## 6 septies. Prise en main à distance via Guacamole

### Mécanisme retrouvé dans le code Medulla

| Élément | Emplacement |
|---|---|
| Création des connexions | `pulse_xmpp_agent/pluginsrelay/plugin_guacamoleconf.py` (côté agent) |
| Convention de nommage | `<PROTO>_<hostname>` (`RDP_pc1`, `SSH_pc1`) — VNC retiré en 1.6.0 |
| Stockage de l'identifiant | `xmppmaster.has_guacamole` (`machine_id`, `protocol`, `idguacamole`) |
| Construction de l'URL | `msc/msc/vnc_guacamole.php` : `@@CUX_ID@@` = `base64(id + "\0c\0mysql")` |
| Options de protocole | `/etc/pulse-xmpp-agent/guacamoleconf.ini` (`rdp_*`, `ssh_*` ; les `vnc_*` existent côté Medulla mais ne sont plus utilisés par BrowseParc) |

### Vérifications menées sur `gla`

| Contrôle | Résultat |
|---|---|
| `guacd` et ses plugins | actif, plugins **rdp / ssh** utilisés (le plugin vnc est installé mais BrowseParc ne l'emploie plus) |
| Accès webapp | `/guacamole/` → 403 sans `Referer`, **200** avec |
| Compte Guacamole | `root` avec `ADMINISTER` + `CREATE_CONNECTION` |
| API REST (jeton) | `POST /api/tokens` → **200** avec les identifiants de `guacamole_baseurl` |
| Mot de passe MySQL du relais | **invalide** (`Access denied`) → l'API est utilisée à la place |
| Création d'une connexion RDP | **200**, connexion `RDP_192.0.2.99` retrouvée, identifiant attribué |
| URL produite | `https://gla.medulla-tech.io/guacamole/#/client/<base64>?username=root&password=…` |
| Mise à jour (2ᵉ appel) | action `updated`, **même identifiant** (pas de doublon) |
| Paramètres enregistrés | `hostname`, `port`, `username`, `password` vérifiés via l'endpoint dédié |
| Protocole SSH | connexion `SSH_<hôte>` créée et vérifiée (VNC : vérifié à l'époque, **historique**, retiré en 1.6.0) |
| Nettoyage | le test ne supprime que les connexions qu'il a lui-même créées (suivies par nom) |
| Détection des services | `172.16.12.140/30` → `srv-win25-01` avec `ports=[5985] services=[winrm]` |
| Refus | protocole hors liste, machine invalide, port hors plage, identifiants trop longs |

## 6 octies. Colonne « Prise en main » invisible — diagnostic

| Élément | Détail |
|---|---|
| Symptôme | L'utilisateur ne voit aucun bouton de prise en main dans la page |
| Cause 1 | Les fichiers statiques de MMC sont servis **sans `Cache-Control`** (`Last-Modified` + `ETag` seuls) : le navigateur gardait l'ancien `browseparc.js`, qui ne construisait pas la cellule |
| Correction 1 | URL versionnées `browseparc.js?v=<mtime>` et `browseparc.css?v=<mtime>` (vérifié dans le HTML rendu) |
| Cause 2 | Un bouton n'existe que pour RDP/SSH réellement détectés (RDP/SSH ; VNC n'est plus proposé) ; **le contrôleur de domaine n'ouvre que WinRM (5985)** |
| Correction 2 | La colonne affiche d'abord les **services détectés**, puis les boutons ; l'absence de bouton devient explicite |
| Vérification | Découverte réelle de `172.16.12.0/24` : **41 machines, 40 avec au moins un bouton** (39 × SSH, `kno.medulla.lan` en SSH+RDP), 1 sans bouton (`srv-win25-01`, WinRM seul) |
| Test dédié | `tests/test_render_js.js` : boutons selon les services, cas « WinRM seul », anciens résultats sans `services`, échappement HTML (15 vérifications) |

## 6 nonies. Incident « Unexpected answer from the MMC agent (NULL) »

| Étape | Constat |
|---|---|
| Symptôme | Message d'erreur intermittent au lancement d'une découverte |
| 1. Diagnostic | Le message venait de `bp_xml()` : l'agent n'avait renvoyé **aucun tableau décodable** |
| 2. Méthode fautive | `admin.browse_parc_status` (journal dans le journal Apache) |
| 3. Fausses pistes écartées | mot de passe MySQL périmé (`Access denied`), préfixe de 321 octets (c'était `%O`, en-têtes inclus), délai php-fpm seul, sérialisation `allow_none`, pool de threads |
| 4. **Cause racine** | `stderr.log` contenait des **codes couleur ANSI** ; ESC (0x1b) est interdit en **XML 1.0** → document XML invalide → `xmlrpc_decode()` = `NULL` |
| 5. Pourquoi intermittent | Le statut ne renvoie que la tranche après `log_offset` : l'échec dépendait des lignes renvoyées |
| 6. Preuve | `minidom.parseString('<a>\x1b</a>')` → *not well-formed (invalid token)*, exactement le comportement de PHP |
| 7. Portée | **34 jobs sur 34** contrôlés contenaient ESC dans `stderr.log` |
| 8. Correction | Couleurs uniquement si `[ -t 1 ]` (script) **et** `_xml_safe()` sur tout texte renvoyé (agent) |
| 9. Contrôle final | Nouveau job : 0 ESC dans le journal ; statut assaini : 0 ESC ; document XML-RPC accepté par un parseur strict |

> **Leçon** : une réponse XML-RPC ne peut transporter que les caractères autorisés
> par XML 1.0. Tout texte issu d'un journal (couleurs, binaire, sortie d'outil)
> doit être assaini **avant** de quitter l'agent.

## 6 decies. Incident « titres en anglais malgré la traduction »

| Étape | Constat |
|---|---|
| Symptôme | Les 4 titres de section s'affichaient en anglais dans une console française |
| 1. Première hypothèse | « le code source est en anglais, c'est la convention Medulla » — vraie mais incomplète |
| 2. Vérification du catalogue | `gettext` en Python et en CLI renvoyaient bien le français |
| 3. **Test par le chemin réel** | Sonde PHP servie par **php-fpm** : le français renvoyait l'anglais sur les nouveaux `msgid`, et servait encore les **anciens** titres numérotés |
| 4. Cause | PHP met en cache les catalogues gettext **par processus php-fpm** ; les workers gardaient l'ancien `admin.mo` |
| 5. Indice décisif | L'**espagnol**, jamais chargé par ces workers, fonctionnait correctement |
| 6. Correction | Rechargement gracieux de php-fpm dès qu'un catalogue change (déploiement), + test HTTP des deux langues |
| 7. Leçon | Un test en CLI ne prouve rien sur ce que sert php-fpm |

## 7. Vérifications manuelles complémentaires

| Vérification | Résultat |
|---|---|
| Syntaxe du script étendu (`bash -n` sur Debian) | OK |
| Le mot de passe est absent de la table des processus | 0 occurrence (`ps -eo args`) |
| `pwsh -NoProfile -NonInteractive -Command -` avec secret en environnement | ligne de commande = `pwsh -NoProfile -NonInteractive -Command -`, secret invisible |
| Parser JSON face à une sortie PowerShell polluée par des séquences ANSI | erreur correctement interprétée (`__ERROR__ <message>`) au lieu d'un plantage |
| Découverte d'un hôte WinRM (`172.16.12.141/32`, port 5985) | 1 machine, `installed=false` |
| Journal d'événements (`--state-file`) | `start` → `machine` → `end`, JSON valide |
| Idempotence du déploiement (2e passage) | `translations: 373 entries (373 before)`, patchs non dupliqués |
| Retour arrière | Procédure décrite dans `INSTALL.md`, manifeste écrit à chaque déploiement |

## 8. Ce qui n'a pas pu être validé

| Point | Raison | Contournement |
|---|---|---|
| Découverte et installation **Active Directory** avec identifiants réels | aucun compte de domaine de test disponible | génération de commande, gestion d'erreur et parsing validés ; exécution à confirmer avec un compte AD |
| Installation réelle d'un agent sur une machine Windows | identifiants Windows indisponibles | le client PSWSMan est désormais installé sur `gla` : la connexion au contrôleur de domaine aboutit, seul le compte manque |
| Parcours navigateur authentifié de bout en bout | connexion web OIDC/GLPI, pas de session scriptable | page rendue et testée côté PHP, endpoint testé par appels directs |

## 9. Reproduire les tests

```bash
# tests locaux (poste de développement)
python3 tests/test_browseparc.py
python3 tests/test_patches.py

# déploiement puis tests serveur
./deploy/deploy_browseparc.sh deploy gla
ssh gla 'bash /root/browseparc-stage/tests/test_ui_on_server.sh /root/browseparc-stage'
ssh gla 'python3 /root/browseparc-stage/tests/test_backend_on_server.py'
ssh gla 'python3 /root/browseparc-stage/tests/test_load_on_server.py'
python3 tests/test_powershell_blocks.py
```
