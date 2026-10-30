# Parcourir mon parc — découverte et déploiement de l'agent Medulla

Nouvelle entrée de menu dans l'onglet **Admin** de la console MMC Medulla.

Elle permet de :

1. **découvrir le parc** — balayage réseau (nmap) ou requête Active Directory ;
2. **sélectionner** des machines (unités d'organisation, filtre, cases à cocher) ;
3. **créer des groupes d'installation agent** réutilisables ;
4. **lancer l'installation de l'agent** sur la sélection, avec suivi de progression
   en direct (barre de progression + journal), annulation possible.

L'ensemble s'appuie sur le script existant `/usr/sbin/medulla-deploy-agent.sh`,
étendu de modes non interactifs et d'une sortie JSON.

---

## Sommaire

- [Aperçu fonctionnel](#aperçu-fonctionnel)
- [Architecture](#architecture)
- [Arborescence du livrable](#arborescence-du-livrable)
- [Le script étendu](#le-script-étendu)
- [L'API du mmc-agent (Python)](#lapi-du-mmc-agent-python)
- [L'interface web (PHP / JS)](#linterface-web-php--js)
- [Sécurité](#sécurité)
- [Déploiement](#déploiement)
- [Tests](#tests)
- [Limites connues et points à valider](#limites-connues-et-points-à-valider)

---

## Aperçu fonctionnel

### Écran « Parcourir mon parc »

| Section | Contenu |
|---|---|
| **Découvrir le parc** | Mode *Balayage réseau (nmap)* ou *Active Directory*. Champs CIDR / serveur AD, OU, domaine NetBIOS, filtre sur le nom, port (5985 WinRM / 22 SSH), identifiant, mot de passe, clé SSH. **Sélecteur « Agent à déployer »** (agents des entités + agent générique) et option *Ignorer le certificat HTTPS*. Boutons *Lancer la découverte*, *Vérifier les prérequis*. En mode Active Directory, le bouton **Lister les OU** affiche l'annuaire en **arbre** (domaine + unités d'organisation) : chaque nœud porte son nombre de machines et les branches vides sont masquées ; le conteneur `CN=Computers` (où atterrissent les machines par défaut) y figure, marqué *Conteneur*. |
> **Méthode** : la colonne annonce le transport que l'installation utilisera
> (WinRM ou SSH), décidé d'après le système détecté — il n'est plus nécessaire de
> changer le port du formulaire selon le type de machine. Le compteur de sélection
> donne la répartition (`3 sélectionnées (2 SSH, 1 WinRM)`).

> **Système** : la colonne est renseignée en découverte réseau comme en Active
> Directory. Le serveur interroge la machine (bannière SSH, en-tête WinRM) plutôt
> que de deviner d'après les ports, ce qui donne la distribution et sa version —
> voir [`docs/TROUVER_DES_MACHINES.md`](docs/TROUVER_DES_MACHINES.md).

| **Machines trouvées** | Tableau nom / IP / source / OU / système / agent déjà présent / **prise en main**. Filtre, tout sélectionner, compteur de sélection, case *Réinstaller*. Boutons *Installer l'agent sur la sélection*, *Créer un groupe de ciblage* (fenêtre nom + description ; groupe propre à la page, distinct des groupes Medulla, pour déployer l'agent ensuite), *Créer un groupe Medulla standard* (machines déjà équipées), et par machine les boutons **RDP / SSH** correspondant aux services réellement détectés. |
| **Groupes d'installation agent** | Enregistrement de la sélection courante sous un nom, puis *Installer*, *Suivre* (ouvre la progression de la dernière installation lancée depuis le groupe), *Supprimer*. |
| **Tâches récentes** | Historique des jobs de découverte / installation. **Suivre** ouvre le **journal de la tâche juste sous sa ligne**, dans le tableau : complet, relu depuis le début, puis suivi en direct tant que la tâche tourne. Rien ne bouge à l'écran et le journal reste ouvert lors des rafraîchissements. **Annuler** arrête une tâche **en cours** — la ligne passe à *annulée* (et non *terminée*) et le journal de la tâche s'ouvre pour le montrer. `SIGTERM` au groupe de processus (script et ses enfants nmap / WinRM / SSH), la tâche étant marquée *annulée* pour ne pas ressembler à un plantage. Le bouton n'apparaît que sur une tâche en cours, après confirmation. |

Le suivi d'une tâche affiche une barre de progression, le compteur `fait/total`,
le journal du script en temps réel, et le détail des échecs.

### Groupe d'installation agent

Un **groupe d'installation agent** est une liste nommée de machines/OUs
découvertes, propre à la page et stockée sur le serveur (ports et services
compris). Il fonctionne **même pour des machines qui n'ont pas encore l'agent** :
c'est fait pour y déployer l'agent. Ce n'est pas un groupe Medulla classique.

---

## Langues

La page suit le mécanisme de MMC : **le code source est en anglais**
(`_T('English text', 'admin')`) et l'affichage est traduit à l'exécution selon la
langue de la session.

| Langue | Fichier | Catalogue |
|---|---|---|
| Anglais | `locale/browseparc_en.po` | `admin/locale/en_US/LC_MESSAGES/admin.mo` (si présent ; sinon l'anglais est le texte source) |
| Français | `locale/browseparc_fr.po` | `admin/locale/fr_FR/LC_MESSAGES/admin.mo` |
| Espagnol | `locale/browseparc_es.po` | `admin/locale/es_ES/LC_MESSAGES/admin.mo` |

Français, anglais et espagnol sont livrés : l'anglais est la langue source des `msgid` (un
catalogue `en_US` n'est fusionné que s'il existe), le français et l'espagnol sont ceux du module
`admin` de Medulla, la page est donc au même niveau que le reste de la console. Ajouter une langue se limite à
déposer `locale/browseparc_<langue>.po` — le déploiement le fusionne
automatiquement. Une langue absente retombe sur l'anglais.

Comme les autres modules, la page fournit un **modèle de traduction**
`locale/browseparc.pot` (régénéré par `python3 tools/make_pot.py`, vérifié par les tests). Les
messages de l'agent MMC (écrits en anglais côté python) sont traduits par
`bp_translate_message()` dans `web/browseparc_common.php` avant d'arriver au navigateur ; les
messages du système distant (sortie des installeurs) restent ceux de la machine.

## Architecture

```
Navigateur
   │  jQuery / JSON
   ▼
MMC web (PHP, php-fpm)
   ├── modules/admin/admin/browseparc.php        page + formulaire
   ├── modules/admin/admin/browseparcAjax.php    endpoint JSON (+ CSRF + ACL)
   └── modules/admin/admin/browseparc_common.php helpers
   │  XMLRPC (xmlCall) — la voie Medulla habituelle
   ▼
mmc-agent (Python, root)
   └── mmc/plugins/admin/browseparc.py
         ├── validation des entrées
         ├── gestion des jobs (dossier /var/lib/medulla/browseparc/jobs)
         ├── stockage des groupes (/var/lib/medulla/browseparc/groups)
         └── exécution de /usr/sbin/medulla-deploy-agent.sh
   │
   ▼
medulla-deploy-agent.sh  →  nmap / pwsh (WinRM) / ssh / SMB (impacket) / mysql
```

Le mot de passe AD n'est **jamais écrit sur disque** : il traverse la chaîne
PHP → XMLRPC → agent → processus enfant **par variable d'environnement**
(`BROWSE_PARC_PASSWORD`), et le script reçoit `--password-env=BROWSE_PARC_PASSWORD`.
Il n'apparaît donc ni dans les arguments des processus (`ps`), ni dans les
fichiers de job.

---

## Choix de l'agent à déployer

Le sélecteur **« Agent à déployer »** de l'écran de découverte liste les agents
réellement présents sur le serveur :

| Entrée | Origine |
|---|---|
| **Agents des entités** | `/var/lib/pulse2/medulla_agent/<dl_tag>/` — les paquets générés par Medulla pour chaque organisation (`Admin → Entités → Download Agent`). Le nom affiché provient de la table `saas_organisations` (`dl_tag` → organisation/entité), sinon du `dl_tag`. |
| **Agent générique** | `/var/lib/pulse2/clients/win/install-agent.ps1` (Windows) et `/var/lib/pulse2/clients/lin/Medulla-Agent-linux-MINIMAL-latest.sh` (Linux) — c'est le comportement historique du script. |

Chaque entrée indique les systèmes disponibles (`Windows` / `Linux`), la taille et
la date du fichier.

### Comment l'agent est déployé

| Cible | Mécanisme |
|---|---|
| **Windows** (WinRM **ou** SSH) | Le script PowerShell envoyé à la machine la fait **télécharger l'agent** puis l'exécuter en silencieux (`/S`), exactement comme le fait Medulla avec son propre `install-agent.ps1`. L'agent d'entité est publié par Apache sous `/medulla_agent/<dl_tag>/` (alias protégé par un contrôle de `Referer`, que le script renvoie). |
| **Linux** (SSH) | Le fichier `.sh` choisi est **transmis par SSH** et exécuté (`bash -s`). |
| **Générique Windows** | Inchangé : `Invoke-Command -FilePath install-agent.ps1` (comportement historique). |

### Sécurité

Le navigateur ne transmet **jamais** de chemin ni d'URL : il envoie un
**identifiant** (`generic` ou `entity:<dl_tag>`) que le serveur confronte à la
liste des agents réellement présents. Un identifiant inconnu ou une tentative de
traversée de chemin (`entity:../../etc/passwd`) est refusé côté agent MMC.

L'option **« Ignorer le certificat HTTPS »** (désactivée par défaut) ajoute le
contournement de validation du certificat dans le script envoyé à la machine.
Elle est nécessaire lorsque le serveur Medulla utilise un certificat
auto-signé ; elle affaiblit la vérification TLS et doit rester l'exception.

> **État sur `gla`** : le paquet **Windows générique est absent**
> (`/downloads/win/Medulla-Agent-windows-FULL-latest.exe` → 404) et le script
> Linux générique (`clients/lin/Medulla-Agent-linux-MINIMAL-latest.sh`) n'existe
> pas non plus. **Seul l'agent de l'entité est réellement déployable** sur ce
> serveur : c'est exactement ce que permet le nouveau sélecteur.

## Documentation

| Document | Contenu |
|---|---|
| [`docs/INTEGRATION.md`](docs/INTEGRATION.md) | **intégration** : points d'accroche dans Medulla, prérequis, interfaces, services, sécurité, portage |
| [`docs/TROUVER_DES_MACHINES.md`](docs/TROUVER_DES_MACHINES.md) | mode d'emploi : valeurs à saisir, prise en main, dépannage |
| [`INSTALL.md`](INSTALL.md) | installation pas à pas |
| [`docs/RAPPORT_DE_TEST.md`](docs/RAPPORT_DE_TEST.md) | rapport de test et incidents rencontrés |
| [`CHANGELOG.md`](CHANGELOG.md) | historique des versions |
| [`tools/README.md`](tools/README.md) | sondes de diagnostic |

## Trouver des machines — fiche pratique

Les valeurs concrètes à saisir pour votre environnement (plage réseau, serveur
AD, domaine, OU, ports, agent à déployer, dépannage) sont regroupées dans
[`docs/TROUVER_DES_MACHINES.md`](docs/TROUVER_DES_MACHINES.md).

| Objectif | À saisir |
|---|---|
| Repérage rapide, sans compte | Mode *Balayage réseau*, CIDR `172.16.12.0/24` → **41 machines** |
| Découverte complète (OS + OU) | Mode *Active Directory*, serveur `172.16.12.141`, domaine `MEDULLA`, OU `DC=medulla,DC=lan` |
| Lister les OU existantes | bouton *Lister les OU* (serveur + identifiants requis) |

## Prise en main à distance (Guacamole)

Chaque machine découverte affiche les **protocoles de prise en main réellement
disponibles** (déduits des ports ouverts) et un bouton par protocole : **RDP**
ou **SSH**. Le clic ouvre la session dans un nouvel onglet, **sans que la machine
ait besoin de l'agent Medulla**.

> **VNC n'est pas proposé.** Les boutons ne dépendent que des ports détectés
> **avant** l'installation de l'agent : RDP si 3389 répond, SSH si 22 répond, quel
> que soit le système de la machine.

### Détection des services

La découverte ne scanne plus un seul port mais
`22, 3389, 5900, 5985` (option `--discover-ports=`), et remonte pour chaque
machine la liste des ports ouverts :

```json
{"target":"srv-win25-01.medulla.lan","ip":"172.16.12.141",
 "ports":[5985],"services":["winrm"]}
```

| Port | Service | Prise en main proposée |
|---|---|---|
| 3389 | RDP | oui |
| 22 | SSH | oui |
| 5985 | WinRM | non — sert à installer l'agent |

> La colonne **Prise en main** affiche d'abord les services détectés
> (`ssh`, `rdp`, `winrm`…) puis un bouton par protocole exploitable. Une machine
> qui n'ouvre que WinRM n'a donc **aucun bouton** : la colonne montre `winrm`,
> ce qui rend la situation lisible plutôt que trompeuse.

> **Après une mise à jour du module**, rechargez la page : les URL du script et
> de la feuille de style sont versionnées (`?v=<mtime>`), le navigateur récupère
> donc la nouvelle version sans vider son cache.


En mode Active Directory, les machines sont listées par `Get-ADComputer` puis
leurs ports sont scannés en une passe supplémentaire.

### Comment la session est ouverte

C'est l'agent MMC qui crée la connexion, via l'**API REST Guacamole** :

1. lecture de `guacamole_baseurl` dans `/etc/mmc/plugins/xmppmaster.ini[.local]`
   (URL du client **et** identifiants du compte Guacamole) ;
2. jeton d'authentification (`POST /api/tokens`) ;
3. création ou mise à jour de la connexion nommée `<PROTO>_<hôte>` — la même
   convention que celle utilisée par l'agent Medulla (`plugin_guacamoleconf.py`),
   donc une connexion existante est **rafraîchie** au lieu d'être dupliquée ;
4. paramètres : `hostname`, `port`, `username`, `password`, complétés par les
   options du relais (`rdp_server-layout`, `vnc_color-depth`, …) ;
5. construction de l'URL : `@@CUX_ID@@` est remplacé par
   `base64(<id> + "\0c\0mysql")`, exactement comme `msc/vnc_guacamole.php`.

> **Pourquoi l'API et pas la base ?** Le mot de passe MySQL présent dans
> `/etc/pulse-xmpp-agent/guacamoleconf.ini` est **périmé** (`Access denied`), alors
> que l'API répond avec les identifiants du compte Guacamole de l'URL. Le module
> utilise donc l'interface officielle.

### Identifiants de la session distante

Le compte saisi dans la page (identifiant / mot de passe) est **réutilisé** pour
la prise en main. Il est enregistré dans la connexion Guacamole (nécessaire pour
que Guacamole ouvre la session) — à garder en tête du point de vue sécurité.

### SSH : authentification par clé

Les machines durcies **refusent l'authentification par mot de passe** :

```
Password and keyboard-interactive authentication are not supported by the SSH server
```

Le champ **clé SSH** du formulaire (chemin d'un fichier sur le serveur) est donc
transmis à la prise en main. Sans clé indiquée, le serveur reprend
automatiquement celle du relais (`ssh_keyfile = /root/.ssh/id_rsa`) avec le
compte `pulseuser` : c'est exactement ce que fait Medulla pour ses propres
connexions.

La lecture d'une clé est **restreinte** à `/root/.ssh` et `/home/*/.ssh`, le
chemin est résolu (les liens symboliques ne permettent pas d'en sortir) et le
contenu doit contenir `PRIVATE KEY` : un compte administrateur ne peut pas faire
lire `/etc/shadow` à l'agent.

### Contrôle préalable du RDP

Avant d'ouvrir une session RDP, l'agent interroge la cible et adapte son
comportement :

- **aucun service RDP** → la session est refusée avec le port concerné ;
- **RDP standard uniquement** → le mode `security=rdp` est posé et un
  avertissement explique que la machine n'offre pas TLS (correction côté
  serveur RDP) ;
- **TLS / NLA** → rien à signaler.

Une adresse non routable est donc rejetée immédiatement, au lieu d'ouvrir un
onglet qui échouerait.

### Quand une session échoue

Guacamole n'affiche qu'un message générique ; la cause réelle est dans le
journal de `guacd` (`journalctl -u guacd`).

| Message guacd | Signification | Correction |
|---|---|---|
| `Password and keyboard-interactive authentication are not supported` | SSH par clé uniquement | renseigner le champ *clé SSH* |
| `Security negotiation failed (wrong security type?)` | la cible n'offre que le **RDP standard** et le client n'a pas été configuré pour | l'agent pose automatiquement `security=rdp` ; si l'erreur persiste, activer TLS sur le serveur RDP |
| `Upstream error` | le service RDP ferme la connexion | vérifier le service RDP de la cible (xrdp, pare-feu, sessions) |
| `Authentication failure` | identifiants refusés | corriger le compte ou le mot de passe |

> **Cas rencontré** : `kno.medulla.lan` est une **Debian 12 avec xrdp**. Son RDP
> n'annonce que le mode standard et ferme la connexion, et son SSH exige une
> clé. Les deux refus viennent de la machine, pas de l'intégration — reproduit en
> pilotant guacd directement.

### Limites

- **Guacamole doit joindre la machine** : la connexion s'établit depuis le serveur
  (guacd), pas depuis le navigateur. Un poste filtré restera inaccessible ;
- les protocoles doivent être actifs sur la cible (RDP activé sur Windows, serveur
  SSH sur Linux) ;
- RDP : le certificat du serveur est ignoré (`ignore-cert`) ;
- SSH : mot de passe ou clé privée (voir plus haut) — aucune clé n'est déposée sur
  la cible ;
- l'URL contient les identifiants Guacamole : elle est à traiter comme sensible.

## Contrainte d'architecture : l'agent MMC et ses threads

### État réel de l'agent

Le `mmc-agent` est une application **Twisted**. Son code initialise :

```python
config.multithreading = True      # valeur par défaut
config.maxthreads = 20
try:
    config.multithreading = config.getboolean("main", "multithreading")
except configparser.NoOptionError:
    pass                          # clé absente → le défaut (True) est conservé
```

Autrement dit, **le multithreading est actif par défaut** : les méthodes des
plugins sont exécutées dans un pool de 20 threads, et non dans le réacteur. Ce
n'est que si un exploitant écrit explicitement `multithreading = 0` que les
méthodes s'exécutent dans le réacteur — une méthode bloquante gèlerait alors
**toute** la console.

Sur `gla`, l'option était commentée : elle n'avait donc aucun effet. Elle a été
rendue explicite (`multithreading = 1`, `maxthreads = 20`) pour documenter le
réglage réellement appliqué.

### Ce que le module fait malgré tout

Quelle que soit la configuration, **aucune méthode ne bloque** :

- tout travail long (nmap, WinRM, AD, résolution d'UUID) est lancé comme
  **processus détaché** (`start_new_session`) ; la méthode rend la main
  immédiatement et le navigateur suit l'avancement par interrogation de statut ;
- le contrôle des **prérequis** est servi depuis un **cache disque**
  (`/var/lib/medulla/browseparc/prerequisites.json`, TTL 300 s) rafraîchi par un
  processus détaché : un chargement de page ne déclenche jamais `pwsh` dans
  l'agent ;
- les lectures de statut, d'historique et de groupes ne font que de la **lecture
  de fichiers** ;
- les commandes lancées par le script sont bornées (`timeout`).

Ce choix garde le module correct même si `multithreading` est désactivé, et
évite d'occuper inutilement les 20 threads du pool.

### Piège PowerShell

**`pwsh -Command -` lit son entrée ligne par ligne.** Un bloc PowerShell
multi-ligne (`try { … } catch { … }`) n'est donc **jamais exécuté** et ne produit
aucune sortie. Les blocs sont écrits avec des séparateurs `;` explicites et
`ps_run` replie les sauts de ligne avant l'envoi ; `tests/test_powershell_blocks.py`
verrouille cette contrainte.

### Déploiement et disponibilité

Un redémarrage de `mmc-agent` rend la console indisponible le temps de sa
réinitialisation (quelques secondes) puis de l'activation paresseuse de ses
plugins (connexion à l'API GLPI : plusieurs dizaines de secondes dans les logs
observés). Le déploiement **ne redémarre donc l'agent que si le module Python a
changé** (comparaison SHA-256), et écrit tous les fichiers de façon **atomique**
(un lecteur concurrent ne voit jamais un fichier tronqué — `admin.mo` est chargé
par `mmap` dans libc).

## Arborescence du livrable

```
BrowseParc/
├── README.md                          ce document
├── INSTALL.md                         procédure de déploiement / retour arrière
├── CHANGELOG.md
├── docs/
│   ├── TROUVER_DES_MACHINES.md
│   └── RAPPORT_DE_TEST.md             résultats de test détaillés
├── server/
│   ├── medulla-deploy-agent.sh        script étendu (à copier dans /usr/sbin)
│   ├── medulla-deploy-agent-smb.py    installation Windows sans WinRM, par SMB (impacket)
│   └── python/
│       └── browseparc.py              module ajouté au plugin admin
├── web/
│   ├── browseparc.php                 page « Parcourir mon parc »
│   ├── browseparcAjax.php             endpoint JSON
│   ├── browseparc_common.php          helpers PHP
│   ├── browseparc.js                  logique client
│   └── browseparc.css                 styles
├── locale/
│   ├── browseparc.pot                 modèle de traduction (tools/make_pot.py)
│   ├── browseparc_en.po               libellés anglais (langue source)
│   ├── browseparc_fr.po               traduction française (fusionnée dans admin.mo)
│   └── browseparc_es.po               traduction espagnole (idem es_ES)
├── deploy/
│   ├── deploy_browseparc.sh           orchestrateur (à lancer depuis le poste admin)
│   └── patch_remote.py                installateur côté serveur (sauvegarde + patch + rollback)
├── tests/                             suites automatisées
│   ├── test_browseparc.py             unitaires du backend + couverture des traductions
│   ├── test_install_logging.py        journal d'installation et macOS (faux ssh, bash ≥ 4)
│   ├── test_patches.py                tests des patchs in-place
│   ├── test_powershell_blocks.py      blocs PowerShell générés
│   ├── test_render_js.js              logique d'affichage du JavaScript (node)
│   ├── test_smb_helper.py             assistant SMB (faux impacket dans tests/fake_impacket)
│   ├── test_ui_on_server.sh           rendu, traductions (dont php-fpm), script, découverte
│   ├── test_backend_on_server.py      bout en bout via le plugin
│   ├── test_guacamole_session.py      création de sessions Guacamole
│   ├── test_load_on_server.py         non-blocage de l'agent
│   ├── fake_deploy_agent.py           script factice pour les tests
│   └── bp_render_test.php             rendu de la page en CLI
├── tools/                             sondes de diagnostic (voir tools/README.md)
└── reference/gla/                     fichiers d'origine du serveur cible (référence)
```

---

## Le script étendu

`/usr/sbin/medulla-deploy-agent.sh` reste **100 % rétrocompatible** : sans
nouvelle option, son comportement est identique à l'original.

### Options ajoutées

| Option | Rôle |
|---|---|
| `--discover` | liste les machines sans rien installer (un compte est requis, comme pour Active Directory) |
| `--list-ous` | liste les unités d'organisation AD en JSON |
| `--targets=a,b,c` | installe sur une liste explicite (pas de découverte) |
| `--json` | sortie JSON exploitable ; les messages humains passent sur stderr |
| `--state-file=<chemin>` | journal JSONL des événements (progression) |
| `--password-env=<VAR>` | lit le mot de passe dans l'environnement |
| `--non-interactive` | ne pose jamais de question, échoue proprement |
| `--skip-ps-setup` | ne (ré)installe pas les prérequis PowerShell |
| `--ps-setup` | installe les prérequis PowerShell (PSWSMan) et rend compte en JSON |
| `--check-prereq` | rapport JSON des prérequis (pwsh, wsman, nmap, python3, mysql, dig) |
| `--uuid-lookup` | lit des noms d'hôtes sur stdin, renvoie `hôte<TAB>nom<TAB>uuid<TAB>jid` |
| `--timeout=<s>` | délai maximal par machine |
| `--discover-ports=22,3389,5900,5985` | ports scannés en découverte (services distants) |
| `--min-hostgroup=64` | machines gardées en vol par nmap (64 par défaut ; monter seulement pour de très grands réseaux) |

### Format de sortie

Découverte :

```json
{"status":"ok","mode":"discover","total":1,
 "machines":[{"target":"srv-win25-01.medulla.lan","name":"srv-win25-01.medulla.lan",
              "ip":"172.16.12.141","source":"network","ou":"","os":"","installed":false}]}
```

Installation :

```json
{"status":"ok","mode":"install","total":2,"ok":1,"ko":1,
 "results":[{"target":"pc1","name":"pc1","status":"ok"},
            {"target":"pc2","name":"pc2","status":"ko"}]}
```

Erreur (le script sort en code 1) :

```json
{"status":"error","message":"The PowerShell WSMan client (PSWSMan) is missing ...","machines":[]}
```

### Journal d'événements (`--state-file`)

Une ligne JSON par événement, écriture atomique sous `flock` :
`start` → `machine` / `ou` → `progress` → `end` (ou `error`).

### Améliorations apportées au script d'origine

- la détection « machine déjà équipée » tient compte du **nom, du FQDN ou de l'IP**
  (`hostname` ou `ip_xmpp` en base) et n'exclut plus silencieusement les machines
  en mode découverte : elles sont **signalées** (`installed: true`) ;
- en mode JSON/`--state-file`, le script **attend** la fin des installations
  parallèles pour produire un bilan exploitable ;
- les échanges PowerShell passent par **stdin** (`pwsh -Command -`), plus aucune
  information d'authentification dans la ligne de commande ;
- détection explicite des **prérequis WSMan** avec message actionnable ;
- parsing robuste des réponses PowerShell (nettoyage des séquences ANSI, enveloppe
  `{ok, items}` / `{ok, error}`) : une erreur d'authentification AD n'est plus
  confondue avec « aucune OU ».

---

## L'API du mmc-agent (Python)

Module `mmc/plugins/admin/browseparc.py`, exposé par le plugin `admin`
(11 méthodes XMLRPC, plus l'action `uuid_lookup` de `browse_parc_start`, que l'interface n'utilise plus) :

| Méthode | Paramètres | Rôle |
|---|---|---|
| `browse_parc_start` | `params` (dict) | démarre un job (`discover`, `install`, `list_ous`, `ps_setup`, `prereq`) → `{ok, job}` |
| `browse_parc_status` | `job`, `log_offset`, `with_log` | état agrégé : statut, progression, machines, OUs, résultats, journal. `log_offset` est un **décalage en octets** ; la réponse porte `log_offset`, `log_more` (suite disponible) et `log_truncated` (journal trop gros : seule la fin est renvoyée). `with_log=false` saute la lecture du journal |
| `browse_parc_cancel` | `job` | arrête le groupe de processus du job (statut `cancelled`) |
| `browse_parc_jobs` | `limit` | derniers jobs |
| `browse_parc_prerequisites` | `force` | rapport de prérequis, **servi depuis le cache** (jamais bloquant) |
| `browse_parc_groups_list` | — | groupes d'installation agent |
| `browse_parc_group_get` | `name` | un groupe et ses machines |
| `browse_parc_group_save` | `name`, `machines`, `description` | création / remplacement |
| `browse_parc_group_delete` | `name` | suppression |
| `browse_parc_agents` | — | agents déployables (entités + générique), avec URL, chemins, tailles et dates |
| `browse_parc_session` | `target`, `protocol`, `port`, `username`, `password`, `sshkey` | crée/rafraîchit la connexion Guacamole de la machine et renvoie l'URL de session |
| `browse_parc_start` (`action: uuid_lookup`) | `targets` | associe des noms d'hôtes aux identifiants Medulla (uuid / jid), en tâche de fond |

Stockage :

```
/var/lib/medulla/browseparc/            (0700, root)
├── jobs/<job_id>/                      request.json, events.jsonl,
│                                       stdout.log, stderr.log, pid, started
└── groups/<nom>.json                   nom, description, dates, machines[]
```

Conception :

- **validation stricte** de toutes les entrées (CIDR, IP, nom d'hôte, port,
  identifiant, DN d'OU, chemin de clé SSH, nom de groupe) — pas d'injection
  possible vers le shell ou le SQL ;
- les jobs sont des **processus enfants détachés** (`start_new_session`) ;
  l'agent n'est jamais bloqué par un scan long ;
- la vivacité d'un processus est lue dans `/proc/<pid>/stat` : un enfant terminé
  mais non reaper (zombie) est correctement considéré comme terminé ;
- 5 jobs simultanés au maximum (démarrage sérialisé par un verrou), listes limitées
  à 512 machines ;
- les jobs terminés sont **purgés** (30 jours, 200 jobs au plus) ; les groupes sont
  écrits de façon atomique ;
- un CIDR plus large que `/16` est refusé par défaut (`min_cidr_prefix`).

Réglages facultatifs, section `[browseparc]` de `/etc/mmc/plugins/admin.ini.local` :

| Clé | Défaut | Rôle |
|---|---|---|
| `min_cidr_prefix` | `16` | préfixe CIDR minimal accepté (8 à 32) |
| `job_retention_days` | `30` | âge maximal des jobs terminés |
| `job_retention_max` | `200` | nombre maximal de jobs conservés |
| `ssh_key_dirs` | `/root/.ssh,/home/*/.ssh` | dossiers autorisés pour les clés SSH |

---

## L'interface web (PHP / JS)

- **Page** : `Page` `browseparc` déclarée dans `modules/admin/infoPackage.inc.php`,
  entrée de menu dans `modules/admin/admin/localSidebar.php`.
- **Endpoint** : `browseparcAjax`, déclaré en `AJAX => true` (donc sans en-tête
  ni pied de page : la réponse est du JSON pur).

  > Le dispatcher MMC **ne contrôle pas l'ACL** des pages AJAX. L'endpoint applique
  > donc lui-même : contrôle d'accès (`browseparc`) puis jeton CSRF pour toute
  > action d'écriture.

- Commandes : `prereq`, `status`, `jobs`, `groups`, `agents`, `group_get`
  (lecture, GET) ; `start`, `cancel`, `group_save`, `group_delete`,
  `session` (écriture, POST + CSRF).
- Les textes traduits et le jeton sont injectés dans la page par `json_encode`
  (flags `JSON_HEX_*`) ; les journaux sont insérés comme texte, jamais comme HTML.
- Le contrôle d'accès reprend la sémantique MMC : `root` passe, les autres
  profils ont besoin du droit `admin#admin#browseparc` (nouvelle entrée ACL
  `admin_fleet_discovery`, catégorie *admin*).

---

## Sécurité

| Point | Mesure |
|---|---|
| Mot de passe AD | jamais en argument de commande, jamais sur disque ; transmis par variable d'environnement du processus enfant |
| Injection shell | validation par liste blanche avant toute construction de commande |
| Injection SQL | requêtes construites après validation stricte (`hostname`, IP) |
| Injection de chemin | noms de groupes et identifiants de jobs validés, pas de traversée |
| Accès | ACL `admin#admin#browseparc` + CSRF sur les actions d'écriture |
| Droits | l'endpoint web n'exécute rien lui-même : tout passe par le mmc-agent (root) |
| Journalisation | les requêtes de job sont conservées sans le mot de passe (`credential_provided: true`) |

---

## Déploiement

Voir [INSTALL.md](INSTALL.md). En résumé, depuis le poste d'administration :

```bash
./deploy/deploy_browseparc.sh deploy   gla    # installation / mise à jour
./deploy/deploy_browseparc.sh verify   gla    # vérification
./deploy/deploy_browseparc.sh rollback gla    # retour arrière (dernière sauvegarde)
```

Le déploiement sauvegarde chaque fichier remplacé dans
`/root/browseparc-backup-<horodatage>/` et redémarre `mmc-agent`.

---

## Tests

| Suite | Où | Résultat |
|---|---|---|
| `tests/test_browseparc.py` | local | **201 / 201** |
| `tests/test_patches.py` | local | **91 / 91** |
| `tests/test_powershell_blocks.py` | local | **21 / 21** |
| `tests/test_ad_ou_parser.py` | local | **21 / 21** |
| `tests/test_render_js.js` | local (node) | **109 / 109** |
| `tests/test_install_logging.py` | serveur (bash ≥ 4) | **117 / 117** |
| `tests/test_smb_helper.py` | serveur | **28 / 28** |
| `tests/test_ui_on_server.sh` | serveur | **85 / 85** |
| `tests/test_guacamole_session.py` | serveur | **23 / 23** |
| `tests/test_backend_on_server.py` | serveur | **72 / 72** |
| `tests/test_load_on_server.py` | serveur | **8 / 8** |

Détail complet et analyse de l'incident dans
[docs/RAPPORT_DE_TEST.md](docs/RAPPORT_DE_TEST.md).

---

## Limites connues et points à valider

1. **Prérequis PowerShell (PSWSMan) — installés sur `gla`** (version 2.3.1,
   dans `/root/.local/share/powershell/Modules`). La chaîne WinRM/AD est
   désormais fonctionnelle : `Invoke-Command` atteint le contrôleur de domaine
   et ne renvoie plus que l'erreur d'autorisation tant que des identifiants
   valides ne sont pas saisis. La procédure d'installation (interface, ligne de
   commande, et **tâche Ansible à ajouter au playbook du serveur**) est
   documentée dans
   [INSTALL.md, §1 bis](INSTALL.md#1-bis-prérequis-powershell-pswsman--installation).
2. **Découverte et installation Active Directory non validées de bout en bout**
   faute d'un compte de domaine de test (le chemin technique, lui, est validé
   jusqu'à la connexion au contrôleur de domaine) : le chemin AD a été validé sur la
   génération de commande, la gestion d'erreur (échec d'authentification rendu
   proprement en JSON) et le parsing des réponses, mais pas une exécution réelle
   avec des identifiants valides.
3. **Le parcours navigateur authentifié** n'a pas pu être automatisé : sur cette
   instance, la connexion web passe par OIDC/GLPI et aucune session MMC ne peut
   être obtenue par script. La page est validée par rendu PHP réel (en-têtes,
   menu, traductions) et l'endpoint par appels directs, mais un clic de
   confirmation dans l'interface reste souhaitable.
4. `--list-ous` et la sélection d'OU nécessitent un compte disposant des droits
   de lecture AD sur le contrôleur de domaine.
