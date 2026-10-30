# Intégration du mode « Parcourir mon parc »

Document d'intégration : ce que le mode ajoute à une console Medulla, où il
s'installe, de quoi il dépend, comment le vérifier et le retirer.

Pour l'usage quotidien, voir [TROUVER_DES_MACHINES.md](TROUVER_DES_MACHINES.md) ;
pour le détail d'installation, [../INSTALL.md](../INSTALL.md).

---

## 1. En trois composants

Le mode n'est pas un module autonome : il s'ajoute au module `admin` existant.

| Composant | Rôle | Emplacement final |
|---|---|---|
| **Script de déploiement** | découverte réseau/AD, installation de l'agent | `/usr/sbin/medulla-deploy-agent.sh` |
| **Plugin de l'agent MMC** | orchestre les tâches, porte les méthodes XMLRPC | `/usr/lib/python3/dist-packages/mmc/plugins/admin/browseparc.py` |
| **Page web** | interface de l'onglet Admin | `/usr/share/mmc/modules/admin/admin/browseparc*.php` |

Le script reste **rétrocompatible** : sans ses nouvelles options, il se comporte
exactement comme l'original (voir §5).

---

## 2. Points d'intégration dans Medulla

L'installation touche **quatre** fichiers de la console, en plus des fichiers
posés. Chaque modification est **marquée** (commentaires `browseparc`) et
**idempotente** : la relancer ne duplique rien.

| Fichier | Modification |
|---|---|
| `modules/admin/infoPackage.inc.php` | déclare le `Module` / `SubModule` / `Page` de la page |
| `modules/admin/admin/localSidebar.php` | ajoute l'entrée `SideMenu` dans le menu Admin |
| `plugins/admin/__init__.py` | importe `browseparc` et expose ses méthodes XMLRPC |
| `modules/admin/locale/<langue>/LC_MESSAGES/admin.mo` | fusion des traductions de la page |

Fichiers **posés** (remplacés à chaque déploiement) :

| Source | Destination | Droits |
|---|---|---|
| `server/medulla-deploy-agent.sh` | `/usr/sbin/medulla-deploy-agent.sh` | `755` |
| `server/python/browseparc.py` | `…/mmc/plugins/admin/browseparc.py` | `644` |
| `web/browseparc.php` | `…/modules/admin/admin/` | `644` |
| `web/browseparcAjax.php` | `…/modules/admin/admin/` | `644` |
| `web/browseparc_common.php` | `…/modules/admin/admin/` | `644` |
| `web/browseparc.js` | `…/modules/admin/graph/js/` | `644` |
| `web/browseparc.css` | `…/modules/admin/graph/css/` | `644` |

### Contrôle d'accès

Une entrée est créée dans `admin.acl_feature_definitions` :

```
feature_key    : admin_fleet_discovery
acl_entry      : admin#admin#browseparc
access_type    : rw
install_types  : onpremise,saas       (colonne apparue en Medulla 5.6.5)
```

La colonne **`install_types`** (NOT NULL) n'existe qu'à partir de **Medulla 5.6.5**.
L'installateur **détecte sa présence** avant de construire la requête : le même
déploiement fonctionne donc en 5.5.x comme en 5.6.x. La fonctionnalité est
disponible quel que soit le type d'installation, d'où les deux valeurs.

L'accès à la page et à son endpoint AJAX en dépend. Le super administrateur y a
accès d'office ; les autres profils doivent se voir attribuer la fonctionnalité.

### Traductions

Les catalogues livrés (`locale/browseparc_fr.po`, `browseparc_es.po`) sont
fusionnés dans le `admin.mo` de la langue correspondante. Ce sont les langues
fournies par le module `admin` de Medulla : la page est donc au même niveau que
le reste de la console. Une langue absente retombe sur l'anglais (le `msgid`).

> **Important** : PHP garde les catalogues gettext **en mémoire dans chaque
> processus php-fpm**. Le déploiement **recharge php-fpm** dès qu'un catalogue
> change, sinon les nouveaux libellés restent invisibles (« titres en anglais »).

---

### Versions de Medulla

| Version | État |
|---|---|
| **5.6.5** | version de référence actuelle — intégration revalidée (patchs, ACL, traductions, XMLRPC, Guacamole) |
| 5.5.2 | première version validée ; intégration inchangée |

Les points d'accroche utilisés (page, menu, plugin, ACL, gettext) sont stables
entre ces deux versions. Le seul écart rencontré est la colonne
`install_types` décrite ci-dessus.

> **Après une mise à jour de Medulla**, les paquets remplacent
> `infoPackage.inc.php`, `localSidebar.php`, `__init__.py` et `admin.mo` : les
> patchs et les traductions sont **perdus** et la page disparaît du menu. Un
> simple redéploiement les réapplique — les fichiers posés (page, plugin,
> script) survivent, eux, car aucun paquet ne les fournit.

## 3. Prérequis serveur

Le serveur Medulla doit disposer de :

| Dépendance | Usage | Contrôle |
|---|---|---|
| `python3` | tâches, analyse JSON, sondes | `python3 --version` |
| `nmap` | découverte réseau et des services | `nmap --version` |
| `pwsh` | WinRM, requêtes Active Directory | `pwsh -v` |
| module **PSWSMan** | transport WinRM depuis PowerShell | `env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin /usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive` → `"wsman":true` |
| `python3-impacket` (optionnel) | installation Windows par SMB, sans WinRM | `apt install python3-impacket` puis `/usr/sbin/medulla-deploy-agent-smb.py --check` |
| client `mysql` | correspondance des entités | `mysql --version` |
| `dig` | résolution inverse des machines | `dig -v` |

Contrôle en une commande :

```bash
/usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive
# {"status":"ok","prerequisites":{"pwsh":true,"wsman":true,"nmap":true,
#                                 "python3":true,"mysql":true,"dig":true}}
```

Pour la **prise en main à distance**, en plus :

| Dépendance | Contrôle |
|---|---|
| `guacd` actif | `systemctl is-active guacd` |
| plugins guacd `rdp` / `ssh` | `ls /usr/lib/x86_64-linux-gnu/libguac-client-*.so` |
| webapp Guacamole derrière Apache | `curl -sk -o /dev/null -w '%{http_code}' https://127.0.0.1/guacamole/` → `200` |
| `guacamole_baseurl` renseigné | `grep guacamole_baseurl /etc/mmc/plugins/xmppmaster.ini*` |

---

## 4. Interfaces exposées

### Méthodes XMLRPC (`admin.*`)

| Méthode | Objet |
|---|---|
| `browse_parc_start` | démarre une tâche (découverte, installation, prérequis, OU, UUID) |
| `browse_parc_status` | état, progression, journal et résultats d'une tâche (par machine : `transport`, `system`, `step`, `code`, `reason`) |
| `browse_parc_machine_log` | journal détaillé d'une machine pour une tâche d'installation (128 Ko max) |
| `browse_parc_cancel` | arrête une tâche en cours |
| `browse_parc_jobs` | dernières tâches |
| `browse_parc_prerequisites` | état des prérequis (lecture non bloquante, cache) |
| `browse_parc_groups_list` / `group_get` / `group_save` / `group_delete` | groupes d'installation agent |
| `browse_parc_agents` | agents déployables (entités + générique) |
| `browse_parc_session` | ouvre une session distante (crée la connexion Guacamole) |

### Commandes de l'endpoint AJAX

`prereq`, `status`, `jobs`, `groups`, `agents`, `group_get`, `machine_log`, `start`, `session`,
`cancel`, `group_save`, `group_delete`.

Les commandes de **lecture** passent en `GET` ; les commandes d'**écriture** sont
en `POST` protégé par le jeton CSRF de la session MMC.

### Options du script

| Option | Objet |
|---|---|
| `--target=` / `--server=` | plage CIDR / machine, ou serveur Active Directory |
| `--discover` / `--list-ous` | découverte, listage des OU |
| `--targets=a,b,c` | liste explicite (sans découverte) |
| `--target-info=<json>` | système et ports par machine (transport d'installation) |
| `--discover-ports=` | ports scannés (défaut `22,3389,5985`) |
| `--ou=`, `--namefilter=`, `--domain=` | critères Active Directory |
| `--username=`, `--password-env=`, `--sshkey=` | authentification |
| `--agent-win-url=`, `--agent-win-referer=`, `--agent-lin=` | agent à déployer |
| `--agent-win-insecure` | ignorer le certificat HTTPS de l'agent |
| `--check-prereq`, `--ps-setup`, `--skip-ps-setup` | prérequis PowerShell |
| `--json`, `--non-interactive`, `--state-file=`, `--timeout=` | exécution automatisée |

Le mot de passe passe par **variable d'environnement** (`--password-env`), jamais
en argument.

---

## 5. Données et répertoires

| Chemin | Contenu |
|---|---|
| `/var/lib/medulla/browseparc/jobs/<id>/` | état d'une tâche : `request.json`, `events.jsonl` (dont les événements `step`), `stdout.log`, `stderr.log`, `logs/<machine>.log`, `pid`, `cancelled` |
| `/var/lib/medulla/browseparc/groups/` | groupes d'installation agent (un fichier JSON par groupe, `600`) |
| `/var/lib/medulla/browseparc/prerequisites.json` | cache des prérequis (rafraîchissement en tâche de fond) |

Créés à la demande par l'agent (qui tourne en `root`). Aucun secret n'y est
écrit : le mot de passe ne vit que dans l'environnement du processus de tâche.

---

## 6. Services concernés

| Service | Action | Condition |
|---|---|---|
| `mmc-agent` | **redémarrage** | uniquement si `browseparc.py` ou `__init__.py` a changé (comparaison SHA-256) |
| `php-fpm` | **rechargement gracieux** | uniquement si un catalogue de traduction a changé |
| `apache2` | rechargement | après chaque déploiement |

Le redémarrage de `mmc-agent` **gèle brièvement la console** (le temps que ses
plugins se rechargent). C'est pourquoi il n'a lieu que lorsque c'est
indispensable : un simple changement de page ou de traduction ne le déclenche pas.

---

## 7. Installation et mise à jour

Depuis un poste qui atteint le serveur en SSH :

```bash
./deploy/deploy_browseparc.sh deploy  [hôte]     # installe ou met à jour
./deploy/deploy_browseparc.sh verify  [hôte]     # contrôle une installation
./deploy/deploy_browseparc.sh status  [hôte]     # état courant
./deploy/deploy_browseparc.sh rollback [hôte] [sauvegarde]
```

L'hôte par défaut est `gla`. Le déploiement :

1. construit une arborescence de transit et la copie sur le serveur ;
2. **sauvegarde** tous les fichiers touchés dans `/root/browseparc-backup-<horodatage>/`
   (avec un `manifest.json` permettant le retour arrière) ;
3. écrit les fichiers, applique les patchs marqués, met à jour l'ACL ;
4. fusionne les traductions et **recharge php-fpm** si nécessaire ;
5. redémarre `mmc-agent` **seulement** si le module Python a changé ;
6. vérifie : syntaxe PHP, compilation Python, présence des méthodes XMLRPC,
   service `mmc-agent` actif.

Le rapport final liste chaque étape :

```
backup      : /root/browseparc-backup-20261009-210317
translations: es_ES: 415 entries (415 before); fr_FR: 421 entries (421 before)
service     : mmc-agent laisse en service (module python inchange) : aucun gel
service     : php8.2-fpm reloaded (catalogues gettext rechargees)
```

---

## 8. Vérification après intégration

### Suites automatisées

| Suite | Où | Vérifications |
|---|---|---|
| `tests/test_browseparc.py` | local | 132 |
| `tests/test_patches.py` | local | 36 |
| `tests/test_powershell_blocks.py` | local | 16 |
| `tests/test_render_js.js` | local (`node`) | 34 |
| `tests/test_ui_on_server.sh` | serveur | 58 |
| `tests/test_guacamole_session.py` | serveur | 23 |
| `tests/test_backend_on_server.py` | serveur | 65 |
| `tests/test_load_on_server.py` | serveur | 8 |

Les suites serveur s'exécutent depuis `/root/browseparc-stage/tests/` après un
déploiement (elles sont copiées avec le reste de l'arborescence de transit).

### Contrôle manuel en trois commandes

```bash
# 1. le script répond et voit ses prérequis
/usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive

# 2. la découverte fonctionne et identifie le système
BROWSE_PARC_PASSWORD='...' /usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 \
  --discover --json --skip-ps-setup --non-interactive \
  --username=Administrateur --password-env=BROWSE_PARC_PASSWORD | python3 -m json.tool

# 3. les méthodes sont exposées à l'agent
grep -c browse_parc /usr/lib/python3/dist-packages/mmc/plugins/admin/__init__.py
```

Puis, dans la console : **Admin → Parcourir mon parc**, vérifier que la page
s'affiche, que les titres sont en français (ou espagnol selon la session) et
qu'une découverte sur `127.0.0.1/32` remonte une machine avec son système.

---

## 9. Sécurité

| Invariant | Mise en œuvre |
|---|---|
| Le mot de passe ne touche jamais le disque ni `argv` | transmis par `--password-env` (variable d'environnement du processus de tâche) |
| Le navigateur ne transmet jamais de chemin | il envoie un **identifiant d'agent** (`generic` ou `entity:<dl_tag>`), résolu côté serveur |
| Une clé SSH n'est lue que dans des zones autorisées | `/root/.ssh` et `/home/*/.ssh`, chemin résolu (`realpath`), contenu devant contenir `PRIVATE KEY` |
| Les appels d'écriture sont protégés | jeton CSRF de la session MMC ; l'endpoint répond en JSON (jamais de redirection) |
| Les identifiants distants ne sont enregistrés que dans Guacamole | c'est ce que Guacamole exige pour ouvrir la session ; l'URL de session les contient et doit être traitée comme sensible |
| Les entrées sont validées avant tout usage | machine, port, protocole, longueurs, étiquettes d'OS — les libellés issus du navigateur sont filtrés avant d'atteindre la ligne de commande |

---

## 10. Porter sur une autre instance Medulla

Le déploiement est portable : les chemins sont ceux d'un paquet Medulla Debian
standard, et les patchs sont **recherchés par marqueur** — ils s'appliquent si le
fichier correspond, sinon le déploiement le signale sans casser l'existant.

À adapter d'une instance à l'autre :

| Élément | Où | Remarque |
|---|---|---|
| Valeurs Active Directory | saisies dans la page | rien à modifier dans le code |
| `guacamole_baseurl` | `/etc/mmc/plugins/xmppmaster.ini[.local]` | URL du client **et** identifiants du compte Guacamole |
| Options de protocole Guacamole | `/etc/pulse-xmpp-agent/guacamoleconf.ini` | reprises telles quelles (`rdp_*`, `ssh_*`) |
| Clé SSH par défaut du relais | `ssh_keyfile` de ce même fichier | utilisée si l'opérateur n'en fournit pas |
| Agents des entités | `/var/lib/pulse2/medulla_agent/<dl_tag>/` | détectés automatiquement |

Les fichiers de `reference/gla/` sont les **originaux du serveur cible** utilisés
pour construire les patchs : ils servent de point de comparaison si une autre
instance a été personnalisée.

---

## 11. Dépannage

| Symptôme | Piste |
|---|---|
| La page n'apparaît pas dans le menu | entrée `SideMenu` non appliquée, ou ACL `admin_fleet_discovery` absente |
| `Accès refusé` | le profil n'a pas la fonctionnalité `admin_fleet_discovery` |
| Titres ou libellés en anglais | catalogue gettext en cache : recharger php-fpm |
| `Réponse inattendue de l'agent MMC (NULL)` | réponse vide : consulter `/var/log/apache2/error.log` (`browseparc: unexpected answer from …`) |
| `Votre session MMC a expiré` | la session du navigateur a expiré : recharger la page |
| Aucune machine découverte | vérifier la plage CIDR, ou le compte pour Active Directory |
| Installation qui part en WinRM sur une machine Linux | `--target-info` absent : la page doit envoyer le système et les ports |
| Une session distante ne s'ouvre pas | `journalctl -u guacd -n 30 --no-pager` puis `tools/guacd_probe.py` |

Outils de diagnostic : voir [../tools/README.md](../tools/README.md).
