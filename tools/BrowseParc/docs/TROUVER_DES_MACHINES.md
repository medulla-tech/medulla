# Trouver des machines — mode d'emploi

Fiche pratique pour l'écran **Admin → Parcourir mon parc**.
Elle donne les valeurs à saisir pour votre environnement (`gla`, domaine `medulla.lan`).

---

## 1. Le plus simple : balayage réseau (compte requis)

Un compte est demandé, comme pour Active Directory : la recherche sert à préparer
l'installation, qui en a besoin. Un **mot de passe** ou une **clé SSH** convient.

| Champ | Valeur à saisir |
|---|---|
| Mode | **Balayage réseau (nmap)** |
| Plage réseau (CIDR) | `172.16.12.0/24` |
| Filtre sur le nom | *(vide)* |
| Identifiant | `Administrateur` (le compte utilisé sur le parc) |
| Mot de passe | celui de ce compte — **ou** une clé SSH à la place |

**Résultat obtenu le 09/10 sur cette plage : 41 machines.**

C'est le mode à utiliser pour un premier repérage ou quand on n'a pas de compte de
domaine. Il ne remonte ni le système d'exploitation ni l'OU, mais il détecte les
services (voir §3).

> **Sans compte, la recherche ne part pas** : le message s'affiche **sous les
> boutons** — *« Un identifiant et un mot de passe (ou une clé SSH) sont requis
> pour lancer la recherche. »* En mode **Active Directory**, l'identifiant et le
> mot de passe sont obligatoires (une clé SSH n'a pas de sens face à un annuaire).
> Seuls les contrôles qui ne touchent aucune machine (vérification des
> prérequis, recherche d'UUID) se passent de compte.

---

## 2. Le plus complet : Active Directory (identifiants requis)

| Champ | Valeur |
|---|---|
| Mode | **Active Directory** |
| Serveur AD | `172.16.12.141` *(ou `srv-win25-01.medulla.lan`)* |
| Domaine NetBIOS | `MEDULLA` |
| OU (base de recherche) | `DC=medulla,DC=lan` — ou une OU précise (voir ci-dessous) |
| Filtre sur le nom | *(vide)*, ou par ex. `srv-` pour ne sortir que les serveurs |
| Identifiant | `MEDULLA\administrateur` *(un compte de domaine)* |
| Mot de passe | celui du compte |

Ces valeurs viennent de la configuration du serveur
(`/etc/mmc/plugins/base.ini.local`) :

```ini
baseDN       = dc=medulla,dc=lan
baseUsersDN  = ou=Users, dc=medulla,dc=lan
baseGroupsDN = ou=Groups, dc=medulla,dc=lan
```

### OUs utilisables dans le champ « OU »

| Objectif | Valeur |
|---|---|
| Tout l'annuaire | `DC=medulla,DC=lan` |
| Uniquement les comptes utilisateurs | `OU=Users,DC=medulla,DC=lan` |
| Uniquement les groupes | `OU=Groups,DC=medulla,DC=lan` |
| Une OU métier | `OU=Serveurs,OU=Users,DC=medulla,DC=lan` *(à adapter)* |

> Le bouton **Lister les OU** affiche l'annuaire sous forme d'**arbre** : le
> domaine à la racine, puis ses unités d'organisation. Chaque nœud porte le
> **nombre de machines** qu'il contient, et **seules les branches qui contiennent
> réellement des machines sont affichées** — inutile de parcourir des OU vides.
> Cliquer sur une branche la sélectionne pour la recherche suivante ; cliquer sur
> le domaine cherche dans tout l'annuaire. Il demande le serveur et les
> identifiants.

Exemple d'arbre rendu :

```
medulla (9 machines)
  ├─ Serveurs (5 machines)
  │    └─ DMZ (2 machines)
  ├─ Postes de travail (2 machines)
  └─ Computers  [CONTENEUR] (2 machines)
```

Le compteur d'un nœud **inclut ses sous-OU** : `Serveurs` annonce 5 machines même
si 2 d'entre elles sont rangées dans `DMZ`.

Les machines créées par défaut dans un domaine ne sont pas rangées dans une OU
mais dans le conteneur **`CN=Computers`** : il figure donc dans l'arbre, marqué
`CONTENEUR`. Il se sélectionne comme n'importe quelle branche (un conteneur est
une base de recherche valide). Tout autre conteneur du domaine contenant des
machines apparaît de la même façon. Seuls les conteneurs **vides** sont masqués.

### Ce que ce mode apporte en plus

- le **système d'exploitation** de chaque machine (donc le bon mode d'installation) ;
- l'**OU d'appartenance** ;
- les machines **sans port ouvert** détecté (postes éteints mais présents dans l'annuaire).

**Le compte doit pouvoir lire l'annuaire.** Un compte de domaine standard suffit ;
inutile d'être administrateur pour la découverte (mais nécessaire pour installer).

---

## 3. Les ports détectés, et ce qu'ils permettent

La découverte scanne `22, 3389, 5985` sur chaque machine :

| Port | Service | Colonne « Prise en main » |
|---|---|---|
| 3389 | RDP | **bouton RDP** |
| 22 | SSH | **bouton SSH** (Linux) |
| 5985 | WinRM | *aucun bouton* — sert à **installer l'agent** |
| 445 | SMB | *aucun bouton* — sert à **installer l'agent** sans WinRM (impacket) |

Sur votre parc, 40 machines sur 41 ont un bouton : 39 en **SSH**, et
`kno.medulla.lan` (172.16.12.115) en **SSH + RDP**. Le contrôleur de domaine
`srv-win25-01` n'ouvre que WinRM — il n'a donc pas de bouton de prise en main,
ce qui est normal.

Pour changer les ports scannés :

```bash
# Une recherche exige toujours un compte (mot de passe par variable, jamais en argument)
BROWSE_PARC_PASSWORD='...' /usr/sbin/medulla-deploy-agent.sh --target=172.16.12.0/24 \
  --discover --json --discover-ports=22,3389,5985 \
  --username=Administrateur --password-env=BROWSE_PARC_PASSWORD

# 4. Très grand réseau : augmenter la taille des lots nmap
BROWSE_PARC_PASSWORD='...' /usr/sbin/medulla-deploy-agent.sh --target=10.0.0.0/16 \
  --discover --min-hostgroup=256 --json --skip-ps-setup --non-interactive \
  --username=Administrateur --password-env=BROWSE_PARC_PASSWORD
```

---

## 3 bis. Identifier le système d'exploitation

La colonne **Système** du tableau est renseignée dans les deux modes. Le serveur
interroge la machine au lieu de deviner :

| Ce qui répond | Ce qui est affiché |
|---|---|
| SSH (port 22) | `Debian 12`, `Debian 13`, `Ubuntu`, `CentOS`, `FreeBSD`… |
| WinRM (port 5985) | `Windows` |
| Rien de concluant | `Windows (assumed)`, `Linux/Unix (assumed)`, `Unknown` |

En mode Active Directory, c'est l'OS de l'annuaire qui est retenu (plus précis),
la détection ne servant qu'à combler les machines sans information.

**Sur ce parc** : 41 machines identifiées — 30 Debian 12, 8 Debian 13,
2 Linux/Unix, 1 Windows. `kno.medulla.lan` ressort en **Debian 12**, ce qui
confirme qu'il ne s'agit pas d'un Windows.

> Une découverte sur une **seule machine** scanne désormais aussi ses ports :
> sans cela elle n'avait ni système ni bouton de prise en main.

## 3 ter. Méthode d'installation

La colonne **Méthode** annonce, avant de lancer quoi que ce soit, le transport
qui sera utilisé :

| Système détecté | Méthode |
|---|---|
| Windows avec WinRM | **WinRM** (5985) |
| Windows sans WinRM, avec SMB (445) seulement | **SMB** (impacket, compte administrateur local) |
| Windows joignable seulement en SSH | **SSH** |
| Debian, Ubuntu, Linux, CentOS, Rocky, Alpine, FreeBSD… | **SSH** (22) |
| macOS | **SSH** (22) |
| Système inconnu | sonde de la cible sur le port du formulaire (comportement historique) |

Si WinRM est injoignable, l'installation bascule seule sur SMB (445) quand c'est possible. Pour un
Linux sans SSH, le rapport d'échec affiche la commande `curl … | sudo bash` à taper sur la machine.

Le **port saisi dans le formulaire reste prioritaire** s'il est réellement ouvert
sur la machine : si vous imposez un port, il est respecté.

Vous n'avez donc plus à changer le port selon le type de machine : sélectionnez
Windows et Linux ensemble, chacun partira par le bon transport.

> **Bonne nouvelle** : cette fonctionnalité a révélé que l'action *Installer
> l'agent sur la sélection* était **cassée** — l'interface envoie des objets
> machines, le serveur attendait des chaînes. C'est corrigé.

### Installation sur macOS

Le script reconnaît un Mac (`uname -s` = `Darwin`), lit son architecture et installe le
`.pkg` correspondant. Prérequis :

- l'accès SSH par **clé** (la connexion par mot de passe n'est pas utilisée) ;
- un compte **root**, ou un compte disposant d'un `sudo` **sans mot de passe**
  (`sudo -n` : le mot de passe n'est jamais envoyé) ;
- un paquet par architecture dans `/var/lib/pulse2/clients/mac/` (ou le dossier de
  l'entité) nommé `Medulla-Agent-mac-arm64-<version>-….pkg` (Apple Silicon) et/ou
  `Medulla-Agent-mac-x86_64-<version>-….pkg` (Intel). Le plus récent est retenu ; sans
  paquet pour l'architecture, la machine est en échec avec la cause « paquet absent ».

### Journal et cause d'un échec

Pour chaque machine, le script consigne les étapes **transport, connexion, détection,
préparation, transfert, téléchargement, installation, fin** dans le journal de la tâche et dans
un journal propre à la machine. À la fin d'une installation, le **rapport** sous le journal liste
les machines en échec avec l'**étape**, la **cause** (authentification, DNS, connexion refusée,
injoignable, sudo requis, disque plein, téléchargement, installeur, délai dépassé, paquet absent…)
et le message distant ; *Afficher le journal* ouvre le détail de la machine.

## 3 quater. Suivre une tâche

La section **Tâches récentes** liste les dernières découvertes et installations,
avec deux boutons.

**Suivre** ouvre le **journal de la tâche juste sous sa propre ligne**, dans le
tableau :

- le journal est **complet**, relu depuis le début ;
- si la tâche tourne encore, il **se complète en direct** ;
- l'en-tête rappelle l'identifiant, le mode, la progression, l'état et le nombre
  de machines ;
- le bouton devient *Masquer* pour refermer ; un seul journal est ouvert à la
  fois ;
- le journal **reste ouvert** quand le tableau se rafraîchit.

C'est là qu'on trouve la raison d'un échec, par exemple :

```
Medulla agent will be installed on the following machines:
- 172.16.12.141
172.16.12.141: OpenError: Connecting to remote server 172.16.12.141 failed
with the following error message : Authorization failed
```

**Annuler** arrête une tâche **en cours** : le script et ses processus enfants
(nmap, WinRM, SSH) reçoivent un `SIGTERM`. La ligne passe alors à **annulée**
(pastille orange) — et non « terminée » — et le **journal de la tâche s'ouvre**
sous la ligne pour le montrer. Le bouton n'apparaît **que sur une tâche en
cours**, après confirmation.

### Changer de type de recherche

Basculer entre **Active Directory** et **balayage réseau** repart d'une situation
propre :

- les champs du mode quitté sont **vidés** (ils appartiennent à l'autre type de
  recherche) ;
- l'arbre des OU et la sélection sont réinitialisés ;
- la **tâche en cours est annulée**, puisqu'elle appartient au mode précédent ;
- les **identifiants sont conservés** : les deux modes les utilisent.

> Le panneau en haut de la page reste consacré à la tâche **lancée depuis la
> page** : il ne sert plus à suivre une tâche de la liste.

## 4. En ligne de commande (sans passer par l'interface)

```bash
# 1. Balayage réseau, résultat lisible
/usr/sbin/medulla-deploy-agent.sh --target=172.16.12.0/24 --discover \
  --json --skip-ps-setup --non-interactive

# 2. Contrôle des prérequis du serveur
/usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive

# 3. Lister les OU de l'annuaire (demande les identifiants)
/usr/sbin/medulla-deploy-agent.sh --list-ous --server=172.16.12.141 \
  --domain=MEDULLA --ou=DC=medulla,DC=lan --username='MEDULLA\administrateur' \
  --password-env=BROWSE_PARC_PASSWORD --json --non-interactive
```

Le mot de passe se passe **par variable d'environnement**, jamais en argument :

```bash
export BROWSE_PARC_PASSWORD='...'
```

---

## 5. Lire le résultat, puis agir

La découverte remplit le tableau : *Nom / IP / Source / OU / Système / Agent*.

1. **Cocher** les machines (ou *Tout sélectionner*), éventuellement filtrer.
2. **Installer l'agent** : choisir d'abord l'agent à déployer (liste
   déroulante), puis cliquer sur *Installer l'agent sur la sélection*.
3. **Prendre la main** : cliquer sur le bouton du protocole dans la colonne
   *Prise en main* — la session s'ouvre dans un nouvel onglet.
4. **Créer un groupe d'installation agent** : garde la sélection (ports et services compris) pour y déployer l'agent ensuite ; ce groupe est propre à cette page, distinct des groupes Medulla classiques.

### Quel agent déployer sur ce serveur

Le sélecteur ne propose que ce qui existe réellement :

- **`Agent 0e1ab1d2`** — l'agent de l'entité, **le seul déployable** ici
  (Windows et Linux) ;
- **`Agent générique`** — proposé, mais **inutilisable sur `gla`** : les paquets
  génériques sont absents du serveur (`/downloads/win/…` → 404).

### Point d'attention pour Windows

Le certificat de `gla` est auto-signé : pour installer sur une machine Windows,
cochez **« Ignorer le certificat HTTPS »**, sinon le téléchargement de l'agent
échoue à cause du certificat.

---

## 6. Si aucune machine n'est trouvée

| Symptôme | Cause probable | Action |
|---|---|---|
| 0 machine en balayage réseau | plage erronée, ou machines filtrées | vérifier le CIDR (`172.16.12.0/24`) ; tester `--target=172.16.12.141/32` |
| 0 machine en Active Directory | identifiants ou domaine incorrects | tester le compte, vérifier `MEDULLA` et le serveur `172.16.12.141` |
| `Authorization failed` | compte sans droit de lecture sur l'annuaire | utiliser un autre compte |
| Pas d'OU dans la liste | base de recherche hors du bon conteneur | laisser `DC=medulla,DC=lan` |
| Découverte très lente | plage trop large (`/16`) | découper en `/24` |
| `Réponse vide de l'agent MMC` | incident corrigé en 1.2.3 (codes couleur ANSI interrompant la réponse XML) | recharger la page |
| `The PowerShell WSMan client (PSWSMan) is missing` alors qu'il est installé | le module est dans le profil de root et le démon tourne sans `HOME` (corrigé en 1.9.3) | mettre à jour le script, ou installer en `-Scope AllUsers` |
| `Votre session MMC a expiré` / `HTTP 200` | la session MMC du navigateur a expiré | recharger la page (F5) et se reconnecter |

**Le contrôleur de domaine répond bien** sur son réseau : ports 88 (Kerberos),
389 (LDAP), 445 (SMB) et 5985 (WinRM) ouverts, résolution
`srv-win25-01.medulla.lan` → `172.16.12.141` vérifiée.

---

## 6 bis. Un bouton par protocole détecté

La prise en main s'appuie uniquement sur les protocoles trouvés ouverts sur la machine
**avant** l'installation de l'agent : un bouton RDP si 3389 répond, un bouton SSH si 22
répond. Aucune règle ne masque un protocole selon le système.

Sur Linux, le service RDP est généralement **xrdp** : il peut répondre à la négociation tout
en ne parvenant pas à ouvrir de session. Ce cas n'est pas contrôlé à l'avance (ouvrir une
session de test perturbe la machine) ; le message d'erreur de la connexion l'indique.

**VNC a été retiré** : plus proposé, plus scanné.

## 7. Prendre la main : ce qu'il faut savoir

### Windows (RDP)

Renseignez un **compte autorisé à ouvrir une session à distance** et son mot de
passe. Sur un Windows sain, RDP négocie NLA ou TLS et la session s'ouvre.

### Linux (SSH)

Beaucoup de machines n'acceptent **pas** l'authentification par mot de passe :

```
Password and keyboard-interactive authentication are not supported by the SSH server
```

Dans ce cas, renseignez le champ **clé SSH** avec le chemin d'une clé privée
**sur le serveur** (par exemple `/root/.ssh/id_rsa`). Si vous laissez le champ
vide, le serveur utilise automatiquement la clé du relais Medulla avec le compte
`pulseuser` — la convention de Medulla, adaptée à un parc déjà géré.

### Contrôle automatique avant l'ouverture

Pour RDP, le serveur interroge la cible avant de créer la connexion :

| Situation | Ce que vous voyez |
|---|---|
| RDP standard uniquement | la session s'ouvre, configurée automatiquement en `security=rdp`, avec un **avertissement** informatif |
| TLS ou NLA | la session s'ouvre normalement |
| Machine injoignable | la session est tentée : Guacamole remonte l'erreur réelle |

Le contrôle **ne bloque jamais** : il adapte les paramètres et prévient, mais
c'est toujours Guacamole qui décide. Un bouton affiché reste donc cliquable.

### Si la session ne s'ouvre pas

Guacamole affiche toujours le même message générique. La cause réelle est dans
le journal de `guacd` sur le serveur :

```bash
journalctl -u guacd -n 30 --no-pager
```

| Message | Cause | Correction |
|---|---|---|
| `...authentication are not supported` | SSH par clé uniquement | renseigner la clé SSH |
| `Authentication failure` | mauvais compte ou mot de passe | corriger les identifiants |
| `Security negotiation failed (wrong security type?)` | ancien défaut, corrigé : l'agent pose désormais `security=rdp` | si l'erreur persiste, activer TLS sur le serveur RDP |
| `Upstream error` | le service RDP de la cible ferme la connexion | vérifier RDP sur la machine (service, pare-feu, sessions) |

**Exemple réel** : `kno.medulla.lan` (172.16.12.115) est une **Debian 12 avec
xrdp**, pas un Windows. Interrogée avec tous les modes possibles (standard, TLS,
NLA, TLS+NLA, tous), elle répond **toujours « RDP standard »** : son xrdp est en
`security_layer=rdp`. FreeRDP sait faire le RDP standard, mais le serveur ferme
la connexion pendant l'échange de clés.

Deux solutions pour cette machine :

```bash
# 1. côté machine : passer xrdp en TLS (recommandé)
sudo sed -i 's/^security_layer=.*/security_layer=tls/' /etc/xrdp/xrdp.ini
sudo systemctl restart xrdp

# 2. ou depuis l'interface : utiliser SSH avec une clé
```

## 8. Rappel : ce que la découverte ne fait pas

- Elle n'**installe rien** : elle n'inventorie et ne cible.
- Elle ne **stocke pas** votre mot de passe : il n'existe que le temps de
  l'appel, dans l'environnement du processus.
- Elle n'ajoute pas au parc Medulla les machines découvertes : elles
  n'apparaissent dans la console qu'une fois l'agent installé et enregistré.
