# Journal des modifications

## 1.13.0 — 2026-10-30

### Sécurité

- Les textes traduits et le jeton CSRF sont injectés dans la page par `json_encode`
  (`JSON_HEX_*`) : une traduction contenant une apostrophe ou `</script>` ne casse
  plus le script. Les journaux et messages sont insérés comme texte, plus comme HTML.
- Réseau : un CIDR plus large que `/16` est refusé (réglable, `min_cidr_prefix`).
- Clés SSH : les dossiers autorisés sont réglables (`ssh_key_dirs`) et chaque lecture
  de clé est journalisée.
- `medulla-deploy-agent.sh` : le mot de passe de la base n'est plus passé en `-p` (visible
  dans `ps`) mais par un fichier d'options anonyme (`--defaults-file=<(...)`). La variable
  `MYSQL_PWD` ne convenait pas : un `password=` dans `/root/.my.cnf` la supplante et la
  résolution des identifiants de machines échouait en silence.

### Robustesse et performances

- Démarrage des jobs sérialisé (plafond de 5 jobs réellement respecté) ; verrous sur
  les caches partagés entre threads.
- Purge automatique des vieux jobs (30 jours / 200 jobs, réglable).
- Lecture des événements incrémentale (plus de relecture complète à chaque sondage).
- Journal lu par octets avec `log_more` / `log_truncated` : un gros journal est servi
  par tranches de 256 Ko, l'interface relance aussitôt la lecture de la suite.
- Écriture des groupes atomique ; jeton Guacamole mis en cache.
- `browse_parc_status(job, log_offset, with_log)` : `with_log=false` saute le journal.
- Correction : le résultat `uuid_lookup` (dictionnaire) n'écrase plus la liste `machines`.

### Interface (suivi)

- Chrome ne propose plus d'enregistrer le mot de passe : le champ n'est plus de type `password` (Chrome ignore `autocomplete=off` dessus) mais un champ texte masqué par CSS, avec les attributs d'exclusion des gestionnaires de mots de passe.

- *Installer* (depuis un groupe ou la sélection) remonte directement la page sur le journal de la tâche.

### Internationalisation

- Les **messages de l'agent MMC** (python, en anglais : « Invalid machine », « Unknown job »,
  erreurs Guacamole, clé SSH, réseau trop large…) sont désormais traduits dans la langue de la
  session par `bp_translate_message()` (`browseparc_common.php`, appels `_T()` littéraux donc
  extractibles). Un message inconnu est affiché tel quel.
- Libellés qui restaient en dur : préfixe du nom de groupe par défaut (« Parc »), noms des
  prérequis (« client WSMan », « client mysql »), message AD « Active Directory query failed ».
- Nouveau **modèle `locale/browseparc.pot`**, généré par `tools/make_pot.py` (références de
  sources, `php-format`), comme `admin.pot` des autres modules. Les tests exigent qu'il soit à
  jour, que `fr` et `es` couvrent exactement les mêmes chaînes et que chaque message de l'agent
  soit traduisible.
- **Trois langues livrées : français, anglais, espagnol.** Nouveau `locale/browseparc_en.po`
  (fusionné dans `en_US/admin.mo` quand ce catalogue existe ; sinon l'anglais est le texte
  source, aucun changement pour l'utilisateur).
- Tests : `test_browseparc.py` 201, `test_ui_on_server.sh` 85 (traduction fr/es des messages
  de l'agent via php).

### Installation sans WinRM ni SSH

- **Transport SMB pour Windows** (port 445, sans WinRM) : nouvel assistant
  `/usr/sbin/medulla-deploy-agent-smb.py` (python3 + **impacket**, à installer :
  `apt install python3-impacket`). Il copie le script PowerShell dans `C$\Windows\Temp`,
  le lance par un service éphémère (même principe que PsExec) détaché du gestionnaire de
  services, attend le fichier de résultat puis nettoie. Il faut un compte **administrateur
  local** de la machine. Identifiants uniquement par l'environnement
  (`BP_USERNAME`/`BP_PASSWORD`/`BP_DOMAIN`/`BP_TARGET`), jamais en argument ni sur disque.
- Choix du transport : SMB seulement s'il est demandé ou si 445 est le seul port
  d'administration ouvert (colonne *Méthode* : **SMB**). Si WinRM est injoignable
  (`winrm_unreachable`, `connection_refused`, `unreachable`) avant toute étape distante, le
  script **bascule sur SMB** quand 445 est ouvert et que l'assistant est disponible ; jamais
  après un échec d'authentification.
- Nouvelles causes d'échec : `admin_required`, `smb_unavailable`, `smb_client_missing`
  (traduites en français et en espagnol).
- **Linux sans SSH** : quand SSH échoue (connexion refusée, authentification, `sudo`…), le
  rapport d'échec et le journal de la machine affichent la commande à taper sur la machine
  (`curl -fsSk -e '<referer>' '<url agent>' | sudo bash`), construite à partir de l'agent
  choisi (options `--agent-lin-url` / `--agent-lin-referer`, URL validées : pas d'espace, de
  quote ni de métacaractère shell). Affichée en texte, jamais en HTML.
- Tests : `test_smb_helper.py` (28, faux impacket dans `tests/fake_impacket`), extensions de
  `test_install_logging.py`, `test_browseparc.py` et `test_render_js.js`.

### Installation de l'agent : journal par machine, cause d'échec, macOS

- **Journal de chaque tâche** : pour chaque machine, `medulla-deploy-agent.sh` consigne les étapes
  `transport`, `connect`, `detect`, `prepare`, `transfer`, `download`, `install`, `done`
  (début, réussite ou échec, avec le message distant) dans
  `jobs/<id>/logs/<machine>.log` et dans le journal de la tâche. Chaque étape émet aussi un
  événement `step` dans `events.jsonl`. La sortie complète de l'installeur est conservée
  (20 Ko max) dans le journal de la machine.
- **Où et pourquoi un échec** : chaque résultat porte `transport`, `system`, `step`, `code`
  (`auth_failed`, `dns_failed`, `connection_refused`, `unreachable`, `sudo_required`, `host_key`,
  `winrm_unreachable`, `disk_full`, `download_failed`, `installer_failed`, `transfer_failed`,
  `timeout`, `no_package`, `crashed`, `unknown`) et `reason` (message distant abrégé). Sous
  WinRM et Windows via SSH, des marqueurs émis par le PowerShell distant indiquent si l'échec a
  eu lieu au téléchargement ou à l'installation.
- Interface : à la fin d'une tâche d'installation, un **rapport** liste les machines en échec
  (étape, cause traduite, message distant) avec un bouton *Afficher le journal* par machine.
  Nouvelle commande `browse_parc_machine_log(job, machine)` / Ajax `machine_log` (lecture,
  128 Ko max, nom de machine assaini : pas de sortie du dossier de la tâche).
- **Installation sur macOS** (SSH) : le script détecte `Darwin`, lit l'architecture (`uname -m`),
  choisit le `.pkg` le plus récent `Medulla-Agent-mac-<arm64|x86_64>-*.pkg` dans
  `/var/lib/pulse2/clients/mac/` (ou le dossier de l'entité, option `--agent-mac`), le copie dans
  un dossier temporaire privé et l'installe avec `installer -pkg … -target /` (root, ou
  `sudo -n` : le mot de passe n'est jamais envoyé). La liste des agents indique « macOS ».
- **Prise en main** : un bouton par protocole détecté **avant** l'installation de l'agent. La
  règle « RDP masqué sur Linux quand SSH est ouvert » est supprimée.
- Tests : `test_install_logging.py` (56 vérifications, faux `ssh`, bash ≥ 4 : à lancer sur le serveur).

### Interface

- **Groupes d'installation agent** (anciennement « groupes de ciblage ») : bouton *Créer un groupe d'installation agent* sur la sélection (fenêtre nom + description, refus d'un nom déjà pris). Ces groupes sont propres à la page, distincts des groupes Medulla, et servent à déployer l'agent.
- *Installer* depuis un groupe enregistre le nom du groupe dans la tâche ; *Suivre* ouvre dans le panneau de progression la **dernière installation lancée depuis ce groupe** (message si aucune). `browse_parc_jobs(limit, group)` accepte un filtre par groupe. Le bouton *Charger/Éditer* est retiré (la recherche étant effacée, il ne permettait que de retirer des machines).
- **Retrait** du bouton et de la commande `group_push` (création d'un groupe Medulla standard) : peu pertinents, les machines devaient déjà avoir l'agent. Ils conservent désormais les ports et services des machines (sinon l'installation depuis un groupe pouvait choisir WinRM au lieu de SSH). Le groupe Medulla classique est renommé *Créer un groupe Medulla standard*.
- Les boîtes natives `prompt`/`confirm` sont remplacées par une fenêtre intégrée ; les messages s'affichent aussi en notification visible en bas de l'écran.
- La fenêtre de prise en main est ouverte dans le clic (plus bloquée comme pop-up) ;
  message explicite si le navigateur la refuse.
- Journaux plafonnés (200 000 caractères), suivi en ligne mis en pause quand l'onglet
  est masqué.
- Libellés traduits : agent générique, bouton d'installation des prérequis (était en
  français en dur), avis de journal tronqué, pop-up bloquée.
- Nettoyage : clé morte `credentialsRequired`, code mort de `doDiscover`, sélecteurs
  jQuery construits sans concaténation, entrées `.po` manquantes ou inutilisées.

### Tests et documentation

- `test_browseparc.py` : 188 vérifications ; `test_render_js.js` : 101 ; `test_patches.py` : 91.
- README : méthodes et commandes AJAX à jour, section `[browseparc]` documentée.

## 1.12.0 — 2026-10-10

### Ajouté — une recherche sans compte ne part plus

Le mode *Active Directory* refusait de chercher sans compte de domaine, mais le
**balayage réseau** partait sans rien demander : on pouvait donc lancer une
recherche inexploitable pour l'installation qui suit.

Le script applique désormais **la même règle aux deux modes** :

- **Active Directory** : identifiant **et** mot de passe obligatoires (une clé SSH
  n'a pas de sens face à un annuaire) ;
- **Balayage réseau** : identifiant **et** mot de passe, **ou** une **clé SSH**
  (qui remplace le mot de passe) ;
- restent sans compte les seuls contrôles qui ne touchent aucune machine :
  `--check-prereq`, `--uuid-lookup`, `--ps-setup`.

Deux messages distincts selon le cas :

```
Please provide a domain account for accessing the machines and/or the Active Directory.
Please provide a login and a password (or an SSH key) to search the machines.
```

### Corrigé — le refus était invisible

Le contrôle existait déjà côté page, mais son message était écrit dans le
**panneau de tâche masqué** : cliquer sur *Lancer la découverte* sans identifiants
ne montrait donc **rien**, ce qui laissait croire que la règle n'existait pas.

- le message s'affiche maintenant **dans le formulaire, sous les boutons** ;
- la page vérifie avant de partir (aucune tâche créée pour rien) : découverte,
  listage des OU **et** installation ;
- la règle de la page **reflète celle du serveur** (clé SSH acceptée en réseau,
  refusée en Active Directory) — l'ancien contrôle bloquait à tort une
  installation Linux par clé SSH.

### Corrigé — l'état d'une tâche annulée

`browse_parc_jobs` plaçait l'état `running` avant le marqueur d'annulation : la
ligne restait « en cours » un instant après le clic, alors que le statut détaillé
répondait déjà `annulée`. Le marqueur prime désormais, comme dans
`browse_parc_status` : la ligne bascule **immédiatement**.

### Vérifié

| Contrôle | Résultat |
|---|---|
| Découverte réseau refusée sans compte, acceptée avec | 4 contrôles serveur |
| Clé SSH acceptée en réseau, refusée en AD | inclus |
| `--check-prereq` toujours sans compte | inclus |
| Liste des tâches : `cancelled` dès l'annulation | 2 contrôles serveur |
| Contrôle des identifiants dans la page (3 actions) | 8 contrôles JS |

## 1.11.0 — 2026-10-10

### Corrigé — le bouton « Annuler » semblait ne rien faire

L'annulation fonctionnait — le processus de la tâche était bien arrêté — mais
**rien ne le montrait** :

- la liste des tâches renvoyait l'état `finished` pour une tâche annulée, donc le
  tableau affichait « **terminé** » : on pouvait croire que l'installation avait
  abouti ;
- le message de confirmation était écrit dans le panneau du **haut** de la page
  (masqué quand on travaille dans le tableau du bas) : invisible.

Corrigé :

- la liste des tâches distingue désormais **en cours / terminée / annulée / en
  erreur** (le marqueur d'annulation et le statut de fin sont lus) ;
- chaque état a sa **pastille colorée** dans le tableau ;
- `notify()` écrit **là où l'utilisateur regarde** : dans le journal du panneau du
  haut s'il est visible, sinon dans une zone de messages placée sous le tableau ;
- annuler **ouvre le journal de la tâche**, dont l'en-tête indique « annulée » —
  juste sous le bouton qu'on vient de cliquer.

### Ajouté — changer de mode remet la recherche à zéro

Passer de la découverte **Active Directory** au **balayage réseau** (et
inversement) conserve désormais un état cohérent :

- les champs du mode quitté sont **vidés** (serveur, OU, arbre, domaine, filtre
  pour Active Directory ; CIDR pour le réseau) — ils appartiennent à l'autre type
  de recherche et seraient envoyés par erreur ;
- l'**arbre des OU** et la sélection sont réinitialisés ;
- la **tâche en cours est annulée** (elle appartient au mode précédent) et le
  panneau est masqué ;
- les **identifiants sont conservés** : les deux modes les utilisent.

### Vérifié

| Contrôle | Résultat |
|---|---|
| État d'une tâche annulée (test serveur, tâche réelle annulée) | `cancelled`, plus `finished` |
| La tâche ne reste pas `running` après annulation | 6 nouveaux contrôles serveur |
| Libellés et pastilles d'état, message au bon endroit | 12 nouveaux contrôles JS |
| Changement de mode : champs vidés, tâche annulée, identifiants gardés | inclus |

## 1.10.0 — 2026-10-10

### Ajouté — l'annuaire Active Directory s'affiche en arbre

Le bouton *Lister les OU* remplissait une liste déroulante **plate** : toutes les
unités d'organisation y figuraient, y compris les vides, sans hiérarchie ni
indication de contenu. Difficile de savoir où sont réellement les machines.

Il affiche désormais un **arbre** :

```
medulla (7 machines)
  ├─ Serveurs (5 machines)
  │    └─ DMZ (2 machines)
  └─ Postes de travail (3 machines)
```

- le **domaine** est la racine (le sélectionner cherche dans tout l'annuaire) ;
- le conteneur **`CN=Computers`** — où atterrissent par défaut les machines d'un
  domaine, et qui n'est pas une OU — figure dans l'arbre, marqué *Conteneur* et
  sélectionnable comme n'importe quelle branche. Tout autre conteneur du domaine
  contenant des machines apparaît pareillement ; seuls les conteneurs vides sont
  masqués ;
- chaque nœud porte le **nombre de machines** de son sous-arbre ;
- **seules les branches contenant au moins une machine sont affichées** ;
- cliquer sur une branche la cible pour la recherche suivante.

Côté serveur, la requête Active Directory ramène désormais le domaine, ses unités
d'organisation **et** leurs ordinateurs, puis comptabilise pour chaque unité les
machines qu'elle contient directement et celles de ses sous-unités. Un ordinateur
n'est demandé qu'une fois (`Get-ADComputer -Filter *`), et non une fois par unité :
le comptage est fait en mémoire.

### Corrigé — commentaire `#` dans un bloc PowerShell

Le nouveau bloc de requête contenait des commentaires `#`. Or `ps_run` **replie
les blocs sur une seule ligne** avant de les envoyer à `pwsh` : le `#` commentait
alors tout ce qui suivait, accolade fermante comprise. Le bloc devenait invalide
et l'annuaire ne répondait plus du tout (`No JSON answer from the Active Directory
server`), sans message explicite.

Le test des blocs PowerShell vérifie maintenant qu'**aucun bloc ne contient de
`#`** — la panne ne peut plus repasser inaperçue.

### Vérifié

| Contrôle | Résultat |
|---|---|
| Comptage des machines (DN simulés) | direct et par sous-arbre exacts |
| Syntaxe des blocs PowerShell (parseur PowerShell) | valide, replié comme déployé |
| Hiérarchie côté client (racine, rattachement, parent absent) | 4 contrôles |
| Rendu de la page (arbre présent, invite traduite, plus de sélecteur plat) | 4 contrôles |
| Absence de `#` dans les blocs PowerShell | 5 contrôles |
| Parser des OU et conteneurs (`test_ad_ou_parser.py`) | **21 / 21** : filtrage, hiérarchie, comptages, types, réponses dégradées |

## 1.9.3 — 2026-10-10

### Corrigé — « PSWSMan is missing » alors que le module est installé

Depuis l'interface, toute recherche Active Directory répondait :

```
The PowerShell WSMan client (PSWSMan) is missing on the Medulla server:
listing the Active Directory objects is not possible.
```

alors que `--check-prereq` lancé depuis un shell renvoyait `"wsman": true`.

**Cause** : PSWSMan est installé dans le **profil de l'utilisateur** qui l'a posé
(`/root/.local/share/powershell/Modules/PSWSMan`). `pwsh` ne cherche ce dossier
que si **`HOME` est défini** — et le service `mmc-agent` est lancé par systemd
avec un environnement vide (`Environment=`), donc **sans `HOME`** :

```
pwsh sans HOME        -> MISSING
pwsh avec HOME=/root  -> OK
```

Le contrôle lancé à la main (shell, avec `HOME`) trouvait le module ; le même
contrôle exécuté dans une tâche par le démon ne le trouvait plus. D'où l'écart
entre « ça marche en ligne de commande » et « ça échoue depuis l'interface ».

**Corrigé à deux niveaux** :

1. le script fournit désormais **`HOME`** (`/root`, surchargeable par
   `BP_PWSH_HOME`) à **tous** ses appels `pwsh` — détection des prérequis, remoting
   WinRM, exécution du `--ps-setup` ;
2. `--ps-setup` installe en **`-Scope AllUsers`**
   (`/usr/local/share/powershell/Modules`), donc visible quel que soit `HOME`.

La détection nettoie au passage les séquences terminal que `pwsh` émet
(`ESC[?1h`) avant de conclure.

### Ajouté — contrôles

Deux vérifications rejouent l'environnement du démon :

- `--check-prereq` **sans `HOME`** doit renvoyer `"wsman": true` ;
- un parcours Active Directory **sans `HOME`** ne doit plus réclamer PSWSMan
  (il échoue désormais sur le compte manquant, preuve que le contrôle passe).

### Vérifié

| Contrôle | Résultat |
|---|---|
| `--check-prereq` sans environnement | `pwsh, wsman, nmap, python3, mysql, dig` : **tous true** |
| Parcours AD sans environnement | demande le compte, **plus** PSWSMan |
| Avec `HOME` (shell) | inchangé |

## 1.9.2 — 2026-10-10

### Corrigé — avertissement nmap « highly aggressive --min-hostgroup »

Le script d'origine imposait `--min-hostgroup 512` à chaque scan. Au-delà de
**128**, nmap avertit :

```
Warning: You specified a highly aggressive --min-hostgroup.
```

Un lot de 512 machines « en vol » peut faire **manquer des machines lentes**
(timeouts qui s'accumulent) et retarde l'affichage, puisque les résultats ne
sortent qu'à la fin d'un lot.

**Mesuré sur le parc** : `--min-hostgroup 64` et `512` donnent exactement le
même résultat — **41 machines en 3,1 s** — sur un /24. La valeur agressive
n'apportait donc rien, seulement l'avertissement et le risque.

- valeur par défaut ramenée à **64**, sous le seuil d'alerte ;
- nouvelle option **`--min-hostgroup=N`** pour les très grands réseaux ;
- au passage, le message de débogage listait `-p` **deux fois** : corrigé.

### Vérifié

| Contrôle | Résultat |
|---|---|
| Découverte du `/24` | **41 machines** (identique), en 5,9 s |
| Systèmes identifiés | 30 Debian 12, 8 Debian 13, 2 Linux/Unix, 1 Windows |
| Avertissements nmap | **0** (contre 1 avant) |
| Option `--min-hostgroup=` | acceptée |

## 1.9.1 — 2026-10-10

### Modifié — le journal d'une tâche s'ouvre dans le tableau

Le bouton *Suivre* ramenait la page en haut, vers le panneau de la tâche : on
perdait sa place dans la liste et l'information demandée se trouvait ailleurs.
Conception revue :

- cliquer sur **Suivre** ouvre le **journal de cette tâche juste sous sa ligne**,
  dans la section *Tâches récentes* — le lecteur ne bouge plus ;
- le journal est **complet** (relu depuis le début) et **suit en direct** tant que
  la tâche tourne, puis s'arrête ;
- l'en-tête du journal rappelle l'identifiant, le mode, la progression, l'état et
  le nombre de machines ;
- un seul journal est ouvert à la fois ; le bouton devient *Masquer* ;
- le journal **reste ouvert** lors des rafraîchissements du tableau (le tableau
  est reconstruit à chaque mise à jour, le panneau est réinséré sous sa ligne).

Le panneau du haut reste consacré à la tâche lancée depuis la page.

### Ajouté — contrôles

Neuf contrôles verrouillent la nouvelle conception : ouverture en ligne, absence
de remontée en haut de page, provenance du journal (la tâche et non le panneau),
identifiant porté par la ligne, survie au rafraîchissement, arrêt du suivi en fin
de tâche, bascule du bouton en *Masquer*.

## 1.9.0 — 2026-10-10

### Compatibilité Medulla 5.6.5

`gla` a été mis à jour de 5.5.2 vers **5.6.5**. L'intégration a été revalidée :
les points d'accroche (page, menu, plugin, gettext, Guacamole) sont compatibles
**sans modification du code de la page ni du plugin**.

Un seul écart a dû être traité :

- la table `admin.acl_feature_definitions` gagne une colonne **`install_types`**
  (`set('onpremise','saas')`, NOT NULL). L'`INSERT` de l'ACL ne la renseignait
  pas : la requête aurait été refusée. L'installateur **détecte** désormais la
  colonne et ne l'ajoute que si elle existe — le même déploiement reste valable
  en 5.5.x.

**Après la mise à jour**, les paquets avaient remplacé `infoPackage.inc.php`,
`localSidebar.php`, `__init__.py` et `admin.mo` : les patchs et les traductions
avaient disparu, la page n'était plus enregistrée. Le redéploiement les a
réappliqués (`patched`), l'ACL a été réécrite, les catalogues rechargés et
php-fpm rechargé.

### Mis à jour

- `reference/gla/` reflète les fichiers d'origine **5.6.5** du serveur cible ;
- le rapport de test situe la validation (5.5.2 puis 5.6.5).

### Vérifié après migration

| Suite | Résultat |
|---|---|
| Interface serveur | 58 / 58 |
| Guacamole | 23 / 23 |
| Bout en bout serveur | 65 / 65 |
| Charge | 8 / 8 |
| Unitaires backend | 132 / 132 |
| Patchs | 36 / 36 |
| Blocs PowerShell | 16 / 16 |
| Rendu JS | 34 / 34 |
| **Total** | **446 / 446** |

## 1.8.0 — 2026-10-10

### Ajouté — documentation d'intégration

`docs/INTEGRATION.md` décrit ce que le mode ajoute à une console Medulla :
les quatre points d'accroche (page, menu, plugin, traductions), les fichiers
posés et leurs destinations, l'entrée ACL `admin_fleet_discovery`, les
prérequis serveur, les interfaces exposées (11 méthodes XMLRPC, 12 commandes
AJAX, les options du script), les répertoires de données, les services
concernés et leurs conditions de redémarrage, la procédure d'installation, de
vérification et de retour arrière, les invariants de sécurité, le portage vers
une autre instance et le dépannage.

Le README reçoit un index de la documentation.

### Modifié — arborescence du livrable

- les **sondes de diagnostic** quittent `tests/` pour `tools/`, avec leur propre
  notice (`tools/README.md`) : `tests/` ne contient plus que les suites et leurs
  aides, ce qui évite de les confondre avec des vérifications automatiques ;
- les outils sont désormais copiés sur le serveur avec le reste de
  l'arborescence de transit, pour pouvoir diagnostiquer une instance déployée ;
- suppression de deux artefacts : un script de bricolage resté à la racine
  (`patch_ports.py`) et une sonde Guacamole devenue obsolète (approche par la
  base MySQL, remplacée par l'API REST).

## 1.7.3 — 2026-10-10

### Corrigé — le bouton « Suivre » semblait ne rien faire

Deux causes indépendantes, aucune dans la logique du bouton :

**1. Le panneau se mettait à jour hors de la vue.** Le panneau de tâche est en
**haut** de la page (section *Découvrir le parc*), tandis que le tableau des
tâches — et son bouton *Suivre* — est **en bas** (*Tâches récentes*). Le clic
mettait bien le panneau à jour… en dehors de l'écran. Le *Suivre* des groupes
faisait déjà défiler la page (`scrollTop` vers le tableau des machines), celui des
tâches non.

Désormais le clic **fait défiler jusqu'au panneau**, y écrit une ligne de
confirmation (« Suivi de la tâche … ») puis lance le suivi.

**2. Les messages de succès étaient jetés silencieusement.** `notify()` contenait
ce garde-fou :

```js
if (window.NotifyWidgetSuccess && !isError) { return; }
```

Or **MMC définit bien `NotifyWidgetSuccess`** (`includes/PageGenerator.php`) :
tous les messages **non-erreur** étaient donc supprimés — « session distante
ouverte », « groupe enregistré », « suivi de la tâche »… Seules les erreurs
s'affichaient. La page possède sa propre zone de messages (`#bpJobLog`) et
n'appelle jamais l'assistant de MMC : le garde-fou est supprimé.

### Modifié — le panneau indique la tâche suivie

Le libellé n'affichait que le mode et la progression (« network 41/41 -
terminé »), sans dire **de quelle tâche** il s'agissait. Il commence maintenant
par l'identifiant : `20261009-205900-73606298 - network 41/41 - terminé`.

### Ajouté — contrôles

- le bouton *Suivre* doit **défiler jusqu'au panneau**, confirmer la tâche suivie
  et relancer le suivi ;
- `notify()` ne doit plus ignorer les messages de succès ;
- le panneau doit afficher l'identifiant de la tâche.

## 1.7.2 — 2026-10-10

### Corrigé — bouton « Annuler » proposé sur des tâches terminées

Deux défauts sur les boutons de la section *Tâches récentes* :

1. **« Annuler » était affiché pour toutes les tâches**, y compris terminées.
   Cliquer dessus répondait `ok:true, cancelled:false` (« la tâche ne tourne
   plus ») et l'interface annonçait malgré tout « Annulation demandée » : le
   message était faux.
2. Aucune confirmation n'était demandée, alors qu'annuler interrompt une
   installation en cours.

Corrigé : le bouton n'apparaît que sur une tâche **en cours**, une confirmation
est demandée, et le message distingue les trois cas (annulation demandée, tâche
déjà terminée, échec).

### Corrigé — libellés du JavaScript hors du système de traduction

Une trentaine de libellés étaient écrits **en français en dur** dans
`browseparc.js` : « Suivre », « Annuler », « Charger », « Installer »,
« Supprimer », « Aucun job », « Aucun groupe », les messages de création de
groupe, etc. Ils **échappaient à gettext** : un utilisateur hispanophone voyait
donc du français — pire qu'un repli sur l'anglais.

Les **53 chaînes** du JavaScript passent désormais par le dictionnaire
`BROWSE_PARC.i18n`, alimenté par `_T()`, et sont traduites en français **et** en
espagnol. Chaque catalogue compte **110 chaînes**.

### Ajouté — contrôles de couverture

- toute chaîne demandée par la page (`_T()`) doit exister dans **chaque** langue ;
- plus aucun libellé français en dur dans le JavaScript ;
- toute clé `t("...")` utilisée doit être déclarée.

## 1.7.1 — 2026-10-10

### Corrigé — les titres s'affichaient en anglais malgré la traduction

Le catalogue français contenait bien les traductions, mais **php-fpm servait une
version périmée**. PHP garde les catalogues gettext **en mémoire, par processus
php-fpm** : après la fusion d'un `admin.mo`, les workers continuaient de servir
l'ancien — qui connaissait encore les titres **numérotés** et ignorait les
nouveaux. Gettext retombait alors sur l'anglais (le `msgid`).

La sonde servie par php-fpm est sans ambiguïté :

```
fr_FR :
   Browse my fleet       => Parcourir mon parc      (ancienne chaîne, en cache)
   1. Discover the fleet => 1. Découvrir le parc    (l'ANCIENNE chaîne, encore servie)
   Discover the fleet    => Discover the fleet      (anglais : absente du cache)
es_ES :
   Discover the fleet    => Descubrir el parque     (catalogue jamais chargé : correct)
```

### Corrigé — déploiement

- le déploiement **recharge php-fpm** (rechargement gracieux, sans couper les
  requêtes en cours) dès qu'un catalogue change réellement ; le rapport
  l'indique : `php8.2-fpm reloaded (catalogues gettext rechargees)` ;
- une nouvelle vérification interroge la traduction **à travers php-fpm** (sonde
  HTTP temporaire) et non plus seulement en CLI, pour les deux langues.

### Pourquoi les tests ne l'avaient pas vu

Les tests rendaient la page avec le **CLI** (`php -d short_open_tag=1`), qui
démarre un processus neuf à chaque fois : le cache de php-fpm y est invisible.
La traduction y était donc correcte… alors que le navigateur recevait l'anglais.
C'est exactement le type d'écart qu'un test par le chemin réel permet de
détecter — il est maintenant en place.

## 1.7.0 — 2026-10-10

### Ajouté — multilingue complet (français + espagnol)

La page suit le mécanisme de MMC : le **code source est en anglais**
(`_T('Discover the fleet', 'admin')`) et l'affichage est traduit à l'exécution
selon la langue de la session. C'est la convention de toute la console, pas un
choix propre à cette page.

Le module `admin` livre deux langues — `fr_FR` et `es_ES` — et la page n'en
fournissait qu'une. Elle fournit désormais **les deux** :

| Fichier | Catalogue visé |
|---|---|
| `locale/browseparc_fr.po` | `modules/admin/locale/fr_FR/LC_MESSAGES/admin.mo` |
| `locale/browseparc_es.po` | `modules/admin/locale/es_ES/LC_MESSAGES/admin.mo` |

- le déploiement **n'est plus codé en dur pour le français** : il fusionne chaque
  `browseparc_<langue>.po` présent dans la zone de transit vers le catalogue
  correspondant, et rapporte ce qu'il a fait
  (`es_ES: 383 entries (309 before); fr_FR: 389 entries`);
- les traductions déjà présentes dans MMC sont **prioritaires** : par exemple
  `Remote control` garde la traduction existante du module (« Prise en main à
  distance ») plutôt que celle de la page ;
- une langue sans fichier `.po` retombe sur l'anglais (le `msgid`), comme pour
  n'importe quel module Medulla.

### Vérifié

| Contrôle | Résultat |
|---|---|
| Page rendue en français | `Découvrir le parc`, `Machines trouvées`, `Groupes de ciblage`, `Tâches récentes` |
| Page rendue **en espagnol** | `Descubrir el parque`, `Máquinas encontradas`, `Grupos de destino`, `Tareas recientes` |
| Cohérence des catalogues | français et espagnol couvrent exactement les **mêmes 77 chaînes** |
| Qualité des `.po` | aucun `msgid` en double, aucune chaîne non traduite |

## 1.6.1 — 2026-10-10

### Modifié — titres de section sans numérotation

Les quatre titres de la page ne sont plus numérotés :
« Découvrir le parc », « Machines trouvées », « Groupes de ciblage »,
« Tâches récentes ». Les chaînes anglaises (`_T`) et les traductions françaises
ont été mises à jour ensemble, et le tableau du README suit.

Un contrôle de la suite d'interface vérifie qu'**aucun titre de section n'est
numéroté** : la numérotation ne peut donc pas revenir par inadvertance.

## 1.6.0 — 2026-10-10

### Retiré — VNC

VNC n'est plus proposé ni scanné :

- ports scannés par défaut : `22, 3389, 5985` (5900/5901 retirés) ;
- plus de service `vnc` dans les résultats de découverte ;
- le protocole est refusé par l'API de prise en main.

### Modifié — RDP sur Linux : masqué sauf s'il est le seul accès

> Règle **supprimée en 1.13.0** : un bouton par protocole détecté avant l'installation.

Sur Linux, « Bureau à distance » signifie **xrdp** : un service qui peut être
installé et répondre à la négociation tout en étant **incapable d'ouvrir une
session**. C'est le cas de `kno.medulla.lan`.

Vérifier pour de vrai supposerait d'ouvrir une session sur la machine (avec des
identifiants factices) : c'est **intrusif** — les tests successifs saturent la
limite de sessions et font échouer les tentatives suivantes — et **peu fiable**,
comme l'a montré une machine répondant correctement puis refusant quelques
instants plus tard.

Règle retenue, appliquée à l'affichage :

| Système détecté | Bouton RDP |
|---|---|
| **Windows** | conservé |
| **Linux/Unix avec SSH ouvert** | **masqué** — SSH reste, c'est la voie fiable |
| **Linux/Unix sans SSH** | conservé — c'est le seul moyen d'entrer |
| Système inconnu | conservé — mieux vaut ne pas masquer un service qui marche |

Concrètement, sur le parc : `kno.medulla.lan` et `172.16.13.61` (toutes deux
**Debian 12**) perdent leur bouton RDP au profit de SSH, tandis que
`172.16.13.7` (**Windows**) le conserve.

## 1.5.1 — 2026-10-10

### Corrigé — le contrôle RDP bloquait des machines parfaitement saines

Un bouton RDP s'affichait, mais le clic répondait :

```
No RDP service on 172.16.13.7:3389 (the server refused the negotiation)
```

Or ces machines **ont** un service RDP. Voici leur réponse brute :

```
03 00 00 13 0ed0 00001234 00 | 03 00 0800 | 02 000000
     CC (Connection Confirm)   NEG_FAILURE  code 2 = SSL_NOT_ALLOWED_BY_SERVER
```

`SSL_NOT_ALLOWED_BY_SERVER` ne veut pas dire « pas de RDP » : cela veut dire
« **je ne fais pas TLS, utilisez le RDP standard** ». Le contrôle le lisait comme
un refus et **empêchait la session**. Corrigé :

- les codes d'échec sont décodés ; `selectedProtocol = 0` **et**
  `SSL_NOT_ALLOWED_BY_SERVER` mènent au même traitement : la connexion est créée
  avec **`security=rdp`**, le seul mode que ces serveurs acceptent ;
- **le contrôle ne bloque plus jamais** : s'il ne peut rien conclure (machine
  injoignable, réponse inhabituelle), la session est créée quand même et
  Guacamole remonte l'erreur réelle ;
- l'avertissement n'annonce plus un refus du client mais une information :
  « cette machine n'offre pas TLS, la session utilise le RDP standard ».

**Vérifié de bout en bout** sur `172.16.13.7` : session créée, `security=rdp`
enregistré, et côté guacd

```
Security mode: RDP
Connected to RDPDR 1.13 as client 0x0002      <- session RDP établie
```

### Corrigé — une affirmation erronée des versions précédentes

Les notes précédentes indiquaient que « FreeRDP refuse le RDP standard ». C'est
faux : FreeRDP **sait** le faire, il suffit de le lui demander (`security=rdp`).
Ce qui échouait, c'était la **négociation par défaut**, qui refuse d'elle-même le
RDP standard — d'où le message `wrong security type`.

Reste un cas particulier : **`kno.medulla.lan`** échoue même avec
`security=rdp` (`Upstream error` : le serveur ferme la connexion). Ce n'est donc
pas le client mais **son xrdp** qui est en cause.

## 1.5.0 — 2026-10-09

### Ajouté — méthode d'installation choisie selon l'OS

L'installation dépendait d'un **port unique saisi dans le formulaire** (5985 par
défaut) : installer un serveur Linux supposait de penser à mettre 22, sinon tout
partait en WinRM. Le transport est maintenant décidé **machine par machine**,
d'après le système détecté :

| Cas | Transport retenu |
|---|---|
| Windows avec WinRM ouvert | **WinRM** (5985) |
| Windows joignable seulement en SSH | **SSH** |
| Debian, Ubuntu, Linux, CentOS, Rocky, Alpine, FreeBSD… | **SSH** (22) |
| Système inconnu | comportement historique : sonde de la cible sur le port du formulaire |

- nouvelle colonne **Méthode** dans le tableau : ce que l'installation utilisera
  réellement, avant de la lancer ;
- le compteur de sélection donne la répartition : `3 sélectionnées (2 SSH, 1 WinRM)` ;
- le port saisi dans le formulaire **reste prioritaire** lorsqu'il est réellement
  ouvert sur la machine : un choix explicite n'est jamais écrasé ;
- le tout est optionnel : `--targets=a,b,c` sans information conserve exactement
  le comportement précédent.

### Corrigé — l'installation depuis l'interface était cassée

L'interface envoie les **objets machines complets** (nom, IP, OS, ports), alors
que le serveur validait chaque entrée comme une **chaîne** :

```
AttributeError: 'dict' object has no attribute 'strip'
```

L'action *Installer l'agent sur la sélection* échouait donc depuis le dernier
changement du formulaire. Les deux formes sont désormais acceptées (objets et
noms simples), et les informations par machine sont transmises au script via
`--target-info`.

### Sécurité

Le libellé d'OS vient du navigateur : il est validé (`^[A-Za-z0-9][A-Za-z0-9 ._()/+-]{0,63}$`)
avant d'atteindre la ligne de commande du script, et les ports sont filtrés
(entiers entre 1 et 65535, dédoublonnés).

## 1.4.0 — 2026-10-09

### Ajouté — identification du système d'exploitation

La colonne **Système** du tableau était remplie uniquement par le mode Active
Directory ; en découverte réseau elle restait vide. Le serveur identifie
maintenant l'OS de chaque machine en l'interrogeant :

| Source | Ce qu'elle donne |
|---|---|
| Bannière SSH (port 22) | le système **et** sa version : `Debian 12`, `Debian 13`, `Ubuntu`, `CentOS`, `FreeBSD`… (`OpenSSH_for_Windows` → Windows) |
| En-tête HTTP du WinRM (5985) | `Server: Microsoft-HTTPAPI/2.0` → **Windows** |
| Repli sur les ports | `Windows (assumed)`, `Linux/Unix (assumed)`, `VNC (unknown OS)`, `Unknown` |

- les sondes sont **parallèles** (32 fils) : une plage /24 coûte environ 2,5 s de
  plus (5,8 s au total) ;
- en mode Active Directory, l'OS fourni par l'annuaire **reste prioritaire** : la
  détection ne comble que les vides ;
- la colonne est déjà filtrable (le filtre du tableau porte sur le nom, l'IP,
  l'OU et le système).

### Corrigé — les cibles explicites n'étaient pas scannées

Une découverte sur **une seule machine** (`172.16.12.115`, `serveur.lan`, ou une
cible `/32`) inscrivait la machine **sans scanner ses ports** : ni système, ni
services, et donc **aucun bouton de prise en main**. Ces machines sont désormais
scannées en une passe nmap avant la détection du système.

### Vérifié

| Contrôle | Résultat |
|---|---|
| Découverte du `/24` | **41 / 41 machines identifiées** : 30 × Debian 12, 8 × Debian 13, 2 × Linux/Unix, 1 × Windows |
| Durée d'une découverte /24 | 5,8 s (contre 3,2 s sans la détection) |
| Cible unique `127.0.0.1` | `ports=[22]`, `services=[ssh]`, `os=Debian 12` |
| `kno.medulla.lan` | **Debian 12** — ce qui confirme qu'il ne s'agit pas d'un Windows |

## 1.3.2 — 2026-10-09

### Corrigé — « [error] HTTP 200 » au lieu d'un message utile

Le journal Apache montrait la cause :

```
[09/Oct/2026:20:04:46] "POST /mmc/main.php?...browseparcAjax" 302 4736
```

L'endpoint AJAX appelait `verifyCSRFToken()` de MMC, qui **détruit la session et
redirige** vers `index.php`. Le navigateur suivait la redirection, recevait la
**page de connexion** (4736 octets de HTML), échouait à la lire comme du JSON, et
le message affiché devenait le laconique `HTTP 200`.

- la vérification du jeton est désormais faite **dans l'endpoint**, qui répond en
  JSON : `{"ok":false,"expired":true,"error":"Votre session MMC a expiré,
  rechargez la page (F5)"}` — plus de redirection, plus de page HTML ;
- la session n'est plus détruite sur un jeton périmé : l'utilisateur n'est plus
  déconnecté par une action de la page ;
- l'erreur CSRF reste journalisée (`logCSRFError`) ;
- côté navigateur, une réponse non-JSON (`parsererror`, ou 200 sans JSON) est
  maintenant traduite en **« session expirée »** et non en « HTTP 200 ».

### Modifié — tests

La suite d'interface exige une **réponse JSON** à un POST sans jeton, l'absence
de redirection et de HTML : `40 / 40` au lieu de `38 / 38`.

## 1.3.1 — 2026-10-09

### Ajouté — contrôle préalable du RDP avant d'ouvrir une session

L'agent interroge désormais la cible (négociation X.224 / RDP) **avant** de créer
la connexion, au lieu d'ouvrir un onglet voué à l'échec :

| Réponse de la cible | Comportement |
|---|---|
| Aucun service RDP | session refusée : `No RDP service on <hôte>:<port> (Connection refused)` |
| RDP **standard** uniquement | le mode `security=rdp` est posé et un **avertissement explicite** est affiché : la machine n'offre que le RDP standard, corriger le serveur RDP (`xrdp: security_layer=tls`) ou utiliser SSH/VNC |
| TLS ou NLA | aucun changement, la session s'ouvre normalement |

### Diagnostic définitif — `kno.medulla.lan`

En demandant successivement le RDP standard, TLS, NLA, TLS+NLA puis « tout », la
machine **répond toujours `selectedProtocol = 0`** (RDP standard) :

```
03000013 0ed0 00001234 00 | 02 01 0800 00000000
     CC (Connection Confirm)   NEG_RSP  mode = 0
```

Son `xrdp` est donc configuré en `security_layer=rdp`, sans TLS ni NLA. Or
FreeRDP **sait** faire le RDP standard (`Enabling RDP security` présent dans la
bibliothèque) : c'est le serveur qui ferme la connexion (`Upstream error`) lors
de l'échange de clés. La correction est **sur la machine** :

```bash
sudo sed -i 's/^security_layer=.*/security_layer=tls/' /etc/xrdp/xrdp.ini
sudo systemctl restart xrdp
```

### Modifié — les tests serveur utilisent un faux serveur RDP

Le contrôle préalable exige un service RDP joignable : les tests qui visaient une
adresse non routable (`192.0.2.x`) démarrent maintenant un **petit serveur RDP
factice** sur la boucle locale, qui répond à la négociation.

## 1.3.0 — 2026-10-09

### Ajouté — authentification SSH par clé privée

Medulla authentifie ses connexions SSH avec une **clé privée**
(`ssh_keyfile = /root/.ssh/id_rsa`) et le compte `pulseuser`, car les machines
durcies refusent l'authentification par mot de passe. La prise en main SSH
faisait jusqu'ici l'inverse : elle n'envoyait qu'un mot de passe, donc elle
échouait sur ces machines.

- le champ **clé SSH** du formulaire (chemin d'un fichier sur le serveur) est
  désormais transmis à la prise en main et devient le paramètre
  `private-key` de la connexion Guacamole ;
- **sans clé fournie**, le serveur reprend automatiquement celle du relais
  (`ssh_keyfile`) avec le compte `pulseuser` — la convention de Medulla ;
- **lecture restreinte** : une clé n'est lue que dans `/root/.ssh` ou
  `/home/*/.ssh`, le chemin est résolu (`realpath`, ce qui neutralise les liens
  symboliques) et le contenu doit contenir `PRIVATE KEY`. Un administrateur ne
  peut donc pas faire lire `/etc/shadow` à l'agent ;
- la clé est validée **avant** tout appel à Guacamole : un chemin refusé ne crée
  aucune connexion.

### Diagnostic — prise en main sur `kno.medulla.lan` (xrdp)

La machine est une **Debian 12 avec xrdp** (bannière SSH `OpenSSH_9.2p1
Debian-2+deb12u10`), et non un Windows. Deux refus distincts, tous deux **côté
cible** :

| Protocole | Message exact | Cause |
|---|---|---|
| RDP | `Security negotiation failed (wrong security type?)` puis `Upstream error` | xrdp n'annonce que le **RDP standard** (`selectedProtocol = 0`) ; FreeRDP 2.11 le refuse par défaut, et forcé (`security=rdp` ou `any`) le serveur ferme la connexion |
| SSH | `Password and keyboard-interactive authentication are not supported by the SSH server` | la machine n'accepte que l'**authentification par clé** |

Ces messages ont été obtenus en pilotant **guacd directement** (hors Medulla),
ce qui prouve que l'intégration n'est pas en cause.

### Vérifié

| Contrôle | Résultat |
|---|---|
| Création de la connexion SSH avec clé | `private-key` enregistré, compte `support` |
| Session SSH réelle par clé | **stable 15 s**, terminal affiché (`rect`, `cfill`, `img`) |
| Clé temporaire de test | ajoutée puis **retirée**, `authorized_keys` restauré |
| Chemin de clé hors zone (`/etc/passwd`) | refusé **avant** tout appel |
| Fichier non-clé, clé absente, chemin relatif | refusés |
| RDP vers une machine saine | **non validé** : aucune machine du parc n'ouvre RDP à part `kno` |

> **Limite connue** : la prise en main RDP n'a pas pu être validée de bout en
> bout, faute de cible Windows exposant RDP dans ce parc (le contrôleur de
> domaine n'ouvre que WinRM). La chaîne Guacamole est correcte — la connexion
> est créée et guacd joint la cible — mais le succès final dépend du service RDP
> de la machine visée.

## 1.2.3 — 2026-10-09

### Corrigé — « Unexpected answer from the MMC agent (NULL) » : cause racine trouvée

**Symptôme** : par intermittence, la page affichait
`[error] Unexpected answer from the MMC agent (NULL)` au lancement d'une
découverte. Le diagnostic ajouté en 1.2.2 a désigné la méthode fautive :

```
browseparc: empty answer from admin.browse_parc_status, retrying
browseparc: unexpected answer from admin.browse_parc_status: type=NULL value=NULL
```

**Cause racine** : `browse_parc_status` renvoie une **tranche du journal du job**
(`stderr.log`). Les messages colorés du script y écrivaient des **séquences
d'échappement ANSI**, qui contiennent le caractère **ESC (0x1b)**. ESC est un
UTF-8 parfaitement valide mais **interdit par XML 1.0** :

```
$ python3 -c "import xml.dom.minidom; xml.dom.minidom.parseString('<a>\x1b</a>')"
xml.parsers.expat.ExpatError: not well-formed (invalid token): line 1, column 3
```

L'agent sérialisait donc un document XML **invalide**, que PHP refusait de
décoder : `xmlrpc_decode()` renvoyait `NULL`, d'où le message.

**Pourquoi par intermittence** : le statut ne renvoie que les lignes situées
**après `log_offset`**. Quand la tranche demandée contenait la ligne colorée,
la réponse était vide ; sinon elle passait. C'est ce qui rendait le défaut
difficile à reproduire (10 sondages consécutifs réussissaient).

### Corrigé à deux niveaux

1. **Cause racine — le script** : les couleurs ne sont émises que sur un
   **terminal** (`[ -t 1 ]`). Redirigé vers un fichier, `medulla-deploy-agent.sh`
   n'écrit plus aucune séquence ANSI.
2. **Défense en profondeur — l'agent** : `_xml_safe()` retire les séquences ANSI
   et tous les caractères interdits par XML 1.0 (`0x00-0x08`, `0x0b`, `0x0c`,
   `0x0e-0x1f`) de **tout texte renvoyé** — journaux, événements, fichiers JSON,
   et l'état complet du statut. Le texte utile est conservé.

### Vérifié

| Contrôle | Résultat |
|---|---|
| Fichiers de jobs anciens contenant ESC | **34** (dont le job en échec) |
| Statut assaini d'un journal contenant ESC | **0** ESC, document XML-RPC **valide** |
| Nouveau job après correctif | `stderr.log` : **0** ESC |
| Parseur strict (`minidom`, comme PHP) | accepte le document produit |

### Ajouté

- test local : un journal avec codes couleur doit produire un statut sans
  caractère interdit et un document XML-RPC analysable ;
- test serveur : le journal d'un job réel ne contient plus de code couleur et le
  statut est accepté par un parseur XML strict.

## 1.2.2 — 2026-10-09

### Corrigé — « Réponse inattendue de l'agent MMC »

Ce message apparaît lorsque la réponse de l'agent n'est **pas décodable en
tableau** : autrement dit quand l'agent renvoie un corps **vide** (requête tuée
avant la réponse) ou une valeur simple. Trois causes traitées :

1. **Délai d'exécution PHP.** Sous php-fpm, `max_execution_time = 30` (0 en CLI)
   alors que `xmlCall` attend l'agent jusqu'à 300 s. Au-delà de 30 s la requête
   est tuée et le navigateur reçoit un corps vide. Les appels du navigateur ont
   désormais un **délai de 25 s** (sous la limite PHP) et affichent *« L'agent MMC
   n'a pas répondu à temps »* au lieu de rester en attente.
2. **Réponse vide transitoire.** `bp_xml()` **réessaie une fois** après 400 ms
   avant d'abandonner, et le message d'erreur indique désormais le **type** reçu.
   La réponse brute est écrite dans le journal Apache (`browseparc: unexpected
   answer from ...`) pour permettre le diagnostic.
3. **Commandes de lecture envoyées en POST.** `cmd=agents` partait en **POST à
   chaque chargement de page** (donc avec jeton CSRF) au lieu d'un GET. Les
   commandes de lecture pures (`status`, `jobs`, `groups`, `group_get`,
   `agents`, `prereq`) passent maintenant en **GET**, les commandes d'écriture
   restant en POST protégé par CSRF.

### Corrigé — déploiement refusé par un doublon de traduction

Le fichier `.po` contenait deux fois `msgid "MMC agent unreachable"` : `msgcat`
refusait la fusion et **le déploiement échouait**. Doublon supprimé, et la suite
`tests/test_browseparc.py` vérifie désormais qu'aucun `msgid` n'est dupliqué et
que toutes les chaînes sont traduites.

### Diagnostic

| Symptôme | Signification |
|---|---|
| `Réponse inattendue de l'agent MMC (NULL)` | corps vide : requête tuée ou connexion interrompue |
| `Réponse inattendue de l'agent MMC (string)` | réponse simple au lieu d'une structure |
| `L'agent MMC n'a pas répondu à temps` | délai de 25 s dépassé côté navigateur |
| `Agent MMC injoignable` | connexion refusée avant toute réponse |

## 1.2.1 — 2026-10-09

### Corrigé — la colonne « Prise en main » n'apparaissait pas

Deux causes distinctes :

1. **Cache navigateur.** Les fichiers statiques de MMC sont servis **sans en-tête
   `Cache-Control`** : le navigateur gardait l'ancien `browseparc.js`, qui ne
   construisait pas la colonne. Les URL du script et de la feuille de style
   portent désormais une **version `?v=<mtime>`** : un simple rechargement de la
   page suffit à récupérer la nouvelle version.
2. **Machines sans protocole de prise en main.** Un bouton n'est proposé que pour
   les services réellement détectés (RDP 3389, VNC 5900, SSH 22). Une machine qui
   n'ouvre que WinRM (5985) — cas du contrôleur de domaine — n'a **aucun bouton**.
   La colonne affiche désormais **les services détectés** (`winrm`, `ssh`, …) à
   côté des boutons, pour que l'absence de bouton soit explicite au lieu de
   ressembler à un bug.

### Ajouté

- suite `tests/test_render_js.js` : teste la logique d'affichage de la colonne
  sans navigateur (boutons selon les services, cas « WinRM seul », anciens
  résultats sans champ `services`, échappement HTML).

## 1.2.0 — 2026-10-09

### Ajouté — prise en main à distance (RDP / VNC / SSH) via Guacamole

Chaque machine découverte peut désormais être prise en main **sans agent
Medulla**, en choisissant le protocole parmi ceux réellement détectés.

- la découverte scanne `22, 3389, 5900, 5985` (option `--discover-ports=`) et
  remonte `ports` et `services` par machine ; en mode Active Directory une passe
  nmap complète les machines listées ;
- l'interface propose un bouton **RDP / VNC / SSH** par machine selon les
  services trouvés, dans une nouvelle colonne *Prise en main* ;
- nouvelle méthode XMLRPC `admin.browse_parc_session` et commande AJAX
  `session` (POST + CSRF) : création/rafraîchissement de la connexion Guacamole
  et renvoi de l'URL de session ;
- la connexion suit **la convention de Medulla** (`<PROTO>_<hôte>`, comme
  `plugin_guacamoleconf.py`) : une connexion existante est mise à jour, jamais
  dupliquée ;
- les options de protocole du relais (`rdp_server-layout`, `vnc_color-depth`, …)
  sont reprises de `/etc/pulse-xmpp-agent/guacamoleconf.ini`.

### Choix techniques

- **API REST Guacamole** plutôt qu'écriture directe en base : le mot de passe
  MySQL du fichier de configuration du relais est **périmé** (`Access denied`),
  alors que l'API fonctionne avec les identifiants du compte Guacamole présents
  dans `guacamole_baseurl` ;
- l'API est appelée en boucle locale (`https://127.0.0.1/guacamole`), Apache
  réservant `/guacamole/` aux requêtes portant un `Referer` Medulla ;
- l'URL est reconstruite exactement comme `msc/vnc_guacamole.php` :
  `@@CUX_ID@@` → `base64(<id> + "\0c\0mysql")`.

### Sécurité

- protocole validé contre une liste blanche (`rdp`, `vnc`, `ssh`), machine et port
  validés, identifiants bornés en longueur ;
- le mot de passe saisi est **enregistré dans la connexion Guacamole** (nécessaire
  à l'ouverture de session) : c'est un choix explicite, documenté ;
- l'URL renvoyée contient les identifiants Guacamole et doit être traitée comme
  sensible.

### Note

Le fichier `/etc/pulse-xmpp-agent/guacamoleconf.ini` contient un mot de passe
MySQL **invalide** : à corriger côté serveur si l'on souhaite revenir à un accès
direct à la base.

## 1.1.0 — 2026-10-09

### Ajouté — choix de l'agent à déployer (agents des entités)

L'écran de découverte propose désormais un sélecteur **« Agent à déployer »**
reposant sur le mécanisme existant de Medulla (`Admin → Entités → Download
Agent`) :

- les **agents des entités** sont détectés dans
  `/var/lib/pulse2/medulla_agent/<dl_tag>/` et nommés à partir de la table
  `saas_organisations` (repli sur le `dl_tag`) ;
- l'**agent générique** historique reste proposé ;
- chaque entrée indique les systèmes disponibles (Windows / Linux), la taille et
  la date du paquet ;
- **Windows** : la machine cible télécharge l'agent et l'installe en silencieux
  (`/S`), exactement comme le fait `install-agent.ps1` de Medulla — l'URL passe
  par l'alias Apache `/medulla_agent/<dl_tag>/` (contrôle de `Referer` renvoyé) ;
- **Linux** : le `.sh` choisi est transmis par SSH puis exécuté ;
- nouvelle méthode XMLRPC `admin.browse_parc_agents` et commande AJAX `agents` ;
- option **« Ignorer le certificat HTTPS »** (désactivée par défaut) pour les
  serveurs à certificat auto-signé ;
- nouvelle option du script : `--agent-win-url`, `--agent-win-referer`,
  `--agent-lin`, `--agent-win-insecure`.

### Sécurité

- le navigateur transmet un **identifiant** d'agent (`generic` ou
  `entity:<dl_tag>`), jamais un chemin ni une URL : la résolution se fait côté
  serveur contre la liste des agents réellement présents ;
- un identifiant inconnu ou une traversée de chemin
  (`entity:../../etc/passwd`, `entity:/etc/shadow`) est refusé ;
- la validation de la sélection d'agent n'a lieu **que** pour une installation :
  la découverte, le listage des OU et le contrôle des prérequis ne sont pas
  affectés par un chemin d'agent absent.

### Corrigé

- un chemin Linux par défaut absent ne bloque plus l'installation Windows : le
  défaut est toléré, seul un `--agent-lin` fourni explicitement est validé, et
  l'échec est signalé par machine le cas échéant.

## 1.0.4 — 2026-10-09

### Corrigé — écritures de fichiers non atomiques pendant le service

Le déploiement réécrivait les fichiers **en place** (`shutil.copy*`). Une requête
PHP concurrente pouvait donc lire un fichier tronqué, et surtout `admin.mo` est
chargé par **`mmap` dans libc** : le réécrire pendant qu'un worker `php-fpm` le
lit provoque un plantage du worker (`segfault … in libc.so.6`), donc un **503**.

- tous les fichiers installés, le `.mo` de traduction et la restauration lors
  d'un retour arrière passent par une écriture **temporaire + `os.replace`**
  (atomique : les lecteurs gardent l'ancien inode) ;
- plus aucun fichier temporaire résiduel (vérifié).

### Corrigé — documentation d'une analyse erronée

L'analyse initiale attribuait les 503 au fait que `multithreading` est commenté
dans `/etc/mmc/agent/config.ini`. **C'est faux** : le code de l'agent initialise
`config.multithreading = True` et `maxthreads = 20` par défaut, et l'exception
`NoOptionError` conserve ces valeurs lorsque la clé est absente. Le
multithreading était donc **déjà actif**.

- l'option est désormais écrite explicitement dans la configuration
  (`multithreading = 1`, `maxthreads = 20`) pour refléter le réglage réel, sans
  redémarrage (la valeur effective est inchangée) ;
- README, INSTALL et rapport de test corrigés en conséquence.

### Cause réelle des 503 (rappel)

1. **Redémarrage inutile de l'agent** lors de chaque déploiement → console
   indisponible pendant sa réinitialisation puis l'activation paresseuse de ses
   plugins. Corrigé en 1.0.3 (redémarrage conditionnel).
2. **Écritures non atomiques** → plantage des workers `php-fpm` servant des
   requêtes concurrentes. Corrigé en 1.0.4.

## 1.0.3 — 2026-10-09

### Corrigé — « Service Unavailable » provoqué par le redémarrage du mmc-agent

**Cause identifiée dans les logs du serveur** : le déploiement redémarrait
systématiquement `mmc-agent`, même quand rien de Python n'avait changé. Or au
démarrage l'agent réactive ses plugins **paresseusement** ; la première requête
qui déclenche l'activation du plugin GLPI (connexion à l'API) bloque le réacteur
Twisted pendant plusieurs dizaines de secondes. Comme `php-fpm` ne dispose que de
`pm.max_children = 5` workers, les requêtes parallèles du navigateur saturaient le
pool et Apache répondait **503** à tout le monde.

Preuve : `mmc-agent` redémarré à 17:39:51, activation du backend GLPI journalisée à
17:40:41 (46 s plus tard, déclenchée par la requête de l'utilisateur), et 503 à
17:40:41 et 17:40:44.

- `patch_remote.py` compare désormais l'empreinte SHA-256 de `browseparc.py` et de
  `__init__.py` avant/après installation : **`mmc-agent` n'est redémarré que si le
  module Python a réellement changé** ;
- deux options explicites : `--force-restart` et `--no-restart`
  (`./deploy/deploy_browseparc.sh deploy gla --no-restart`) ;
- un déploiement de PHP / JS / CSS / documentation ne touche plus du tout à
  l'agent (vérifié : `ActiveEnterTimestamp` inchangé).

### Documentation

- [INSTALL.md](INSTALL.md) : fenêtre de maintenance, impact d'un redémarrage de
  l'agent, et recommandations de dimensionnement `php-fpm` pour un serveur
  contraint en mémoire.

## 1.0.2 — 2026-10-09

### Corrigé — les blocs PowerShell multi-lignes n'étaient jamais exécutés

`pwsh -Command -` lit son entrée **ligne par ligne** : un bloc multi-ligne
(`try { … } catch { … }`, scriptblock…) n'est **pas exécuté** et ne produit
aucune sortie. Conséquence : la découverte Active Directory et le listage des OU
renvoyaient « No JSON answer » au lieu du message d'erreur réel, et une
installation WinRM échouait sans explication.

- les blocs PowerShell sont désormais écrits avec des séparateurs `;` explicites ;
- `ps_run` replie les sauts de ligne avant l'envoi, de sorte que l'entrée
  standard ne contienne qu'**une seule ligne** ;
- vérifié : la découverte AD et le listage des OU renvoient maintenant une erreur
  exploitable (`Authorization failed`) au lieu d'une réponse vide ;
- nouveau test `tests/test_powershell_blocks.py` : valide la syntaxe de chaque
  bloc une fois replié et **démontre** qu'un bloc multi-ligne ne s'exécute pas.

### Corrigé — autres

- `--ps-setup` exigeait à tort un compte de domaine : le bouton *Installer les
  prérequis PowerShell* échouait immédiatement. Le mode fait maintenant partie
  des modes sans identifiants.
- La **cause d'un échec d'installation** (PowerShell ou SSH) est remontée dans le
  journal de la tâche au lieu d'être jetée : l'interface affiche désormais
  `OpenError: … Authorization failed …`.
- Le **statut « annulée »** l'emporte sur l'état du processus : une tâche
  annulée n'apparaît plus comme « en cours » ou en « erreur » selon le moment où
  le navigateur interroge son état.

### Modifié — interface

- La **bannière de prérequis** n'est plus affichée à chaque chargement de page :
  elle n'apparaît que si une action échoue réellement pour un prérequis manquant
  (ou sur demande explicite via *Vérifier les prérequis*).

### Ajouté — documentation

- [INSTALL.md, §1 bis](INSTALL.md) : où et comment installer PSWSMan, avec la
  **tâche Ansible prête à intégrer au playbook de provisioning du serveur**
  (idempotente, `-Scope AllUsers`, variante pour dépôt PowerShell interne).

## 1.0.1 — 2026-10-09

### Corrigé — incident « Service Unavailable » (503)

Le `mmc-agent` étant une application Twisted avec `multithreading` désactivé, les
méthodes des plugins s'exécutent dans le réacteur : tout appel bloquant gèle la
console MMC pour **tous** les utilisateurs. La page « Parcourir mon parc »
appelait le contrôle des prérequis à chaque chargement, lequel lançait `pwsh` de
façon synchrone. Avec `pm.max_children = 5`, quelques requêtes bloquées
saturaient php-fpm et Apache renvoyait 503.

- `browse_parc_prerequisites` ne bloque plus : rapport servi depuis un **cache
  disque** (TTL 300 s) rafraîchi par un **processus détaché** ;
- la résolution des identifiants de machines (`uuid_lookup`) devient une **tâche
  de fond** interrogée par le navigateur, au lieu d'un sous-processus synchrone
  dans l'agent ;
- la sonde `PSWSMan` du script est désormais bornée (`timeout 25`) : elle ne peut
  plus rester bloquée indéfiniment ;
- l'interface n'affiche plus de bannière de prérequis tant que le premier relevé
  n'est pas disponible (et le redemande après le rafraîchissement).

### Ajouté

- Statut **« annulée »** pour une tâche interrompue par l'utilisateur (au lieu de
  « erreur »), avec libellé traduit ;
- suite de tests **`test_load_on_server.py`** : vérifie qu'un job long (découverte
  d'un /24) ne dégrade pas la console (36 requêtes HTTP, latence max constatée
  0,003 s, aucun 503) ;
- test de non-régression sur le **temps de réponse** de la méthode de prérequis
  (< 1 s, constaté 0,000 s sur le serveur).

## 1.0.0 — 2026-10-09

Première version de la fonctionnalité **Parcourir mon parc** pour l'onglet Admin
de la console Medulla.

### Ajouté

- **Entrée de menu** « Parcourir mon parc » dans l'onglet Admin
  (`infoPackage.inc.php` + `localSidebar.php`).
- **Page** `browseparc.php` : découverte réseau (nmap) ou Active Directory,
  sélection de machines et d'OUs, installation de l'agent, gestion de groupes,
  suivi des tâches en temps réel.
- **Endpoint JSON** `browseparcAjax.php` : 11 commandes (`prereq`, `status`,
  `jobs`, `groups`, `group_get`, `start`, `cancel`, `group_save`, `group_delete`,
  `group_push`), avec contrôle d'accès et protection CSRF.
- **Logique client** `browseparc.js` et styles `browseparc.css`.
- **Backend mmc-agent** `mmc/plugins/admin/browseparc.py` : 10 méthodes XMLRPC
  (jobs de découverte et d'installation, suivi, annulation, groupes de ciblage,
  résolution des identifiants de machines).
- **Groupes de ciblage** stockés dans `/var/lib/medulla/browseparc/groups/`,
  utilisables même pour des machines sans agent.
- **Poussée vers un groupe statique Medulla** (`dyngroup`) pour les machines
  déjà connues du serveur.
- **Traduction française** de toute la page (`locale/browseparc_fr.po`, fusionnée
  dans `admin.mo` au déploiement).
- **Entrée ACL** `admin_fleet_discovery` (`admin#admin#browseparc`).
- **Outillage de déploiement** : `deploy_browseparc.sh` (orchestrateur) et
  `patch_remote.py` (installation, sauvegarde, vérification, retour arrière).
- **Suites de tests** : 157 vérifications automatisées (unitaires backend,
  patchs, interface, bout en bout serveur).

### Modifié — `/usr/sbin/medulla-deploy-agent.sh`

Le script reste **rétrocompatible** : sans nouvelle option, le comportement est
inchangé.

- Nouvelles options : `--discover`, `--list-ous`, `--targets`, `--json`,
  `--state-file`, `--password-env`, `--non-interactive`, `--skip-ps-setup`,
  `--ps-setup`, `--check-prereq`, `--uuid-lookup`, `--timeout`.
- Sortie JSON exploitable par l'interface ; en mode JSON, les messages destinés
  à l'humain passent sur `stderr` pour ne pas polluer `stdout`.
- Journal d'événements JSONL (`--state-file`) pour la progression en direct.
- Les identifiants PowerShell ne figurent **plus dans la ligne de commande** :
  le script est transmis à `pwsh -Command -` par l'entrée standard, le mot de
  passe par variable d'environnement.
- Détection explicite des prérequis (pwsh, client WSMan, python3) avec messages
  actionnables au lieu d'échecs silencieux.
- Réponses Active Directory encapsulées (`{ok, items}` / `{ok, error}`) et
  nettoyage des séquences ANSI de PowerShell : une erreur d'authentification
  n'est plus confondue avec « aucune OU ».
- Détection « machine déjà équipée » étendue au FQDN et à l'IP (`hostname` ou
  `ip_xmpp`) ; en mode découverte, les machines déjà équipées sont **signalées**
  au lieu d'être retirées silencieusement de la liste.
- En mode JSON/`--state-file`, les installations parallèles sont attendues pour
  produire un bilan complet (machines en succès / en échec).
- Ajout du mode `--uuid-lookup` (lecture des identifiants Medulla par nom d'hôte).

### Corrigé

- Le délai `--timeout` est appliqué au processus PowerShell lui-même.
- Les messages d'information ne sont plus émis sur `stdout` lorsque `--json`
  est demandé (détection du mode avant l'analyse des autres options).
- Un job terminé n'est plus considéré comme « en cours » (gestion des processus
  zombies : lecture de l'état dans `/proc`).

### Notes

- Sur l'instance de test `gla`, les prérequis PowerShell (module `PSWSMan`) ne
  sont pas installés : la découverte réseau fonctionne, WinRM/AD nécessite
  l'installation des prérequis depuis la page.
- La découverte et l'installation Active Directory restent à valider avec un
  compte de domaine réel.
