# ExtractDrivers v2 - collecte des drivers et certificats par XMPP

Cette version **remplace** la copie par partage SMB (`ExtractDriversCertificates/`).
Le poste extrait ses drivers tiers et les certificats de ses pilotes, puis les
depose dans le depot du serveur Medulla **via XMPP uniquement**, par un plugin
du substitut maitre. Aucun identifiant de partage n'est present sur le poste.

## 1. Securite : a faire avant tout

> **Le mot de passe du compte de service `drivers` etait en clair dans
> `ExtractDrivers.ps1` (version SMB). Il doit etre considere comme compromis.**
>
> 1. **Le changer (ou desactiver le compte) cote serveur / partage maintenant.**
> 2. Retirer l'ancien script de tous les packages, depots Git et sauvegardes.
> 3. Ne plus deployer la version SMB : elle est **retiree**. Ce dossier ne
>    contient ni `ExtractDrivers.ps1` ni le mot de passe, volontairement.

La v2 n'embarque aucun secret : le poste s'authentifie avec les identifiants
XMPP de l'agent Medulla deja installe (`agentconf.ini`).

## 2. Ce qui change par rapport a la v1 (SMB)

| Sujet | v1 SMB | v2 XMPP |
|---|---|---|
| Transport | partage `\\serveur\drivers` | XMPP (agent Medulla) |
| Secret sur le poste | oui (mot de passe en clair) | aucun |
| Reception | n/a | plugin serveur `plugin_extract_drivers.py` |
| Donnees envoyees | tout, a chaque fois | **differentiel** : seuls les packages/certificats absents ou differents |
| Interruption | recommencer | **reprise** au dernier point de controle serveur |
| Depot deja a jour | recopie | rien n'est envoye, code 0 |
| Integrite | aucune | md5 par bloc, sha256 de l'archive, empreinte de chaque package |

### Codes de sortie (convergents)

| Code | Signification |
|---|---|
| 0 | Succes, **y compris** "depot deja a jour, rien a envoyer" |
| 1 | Script non lance en administrateur |
| 2 | Prerequis, configuration, metadonnees ou dossier de travail invalides |
| 3 | Connexion / authentification XMPP impossible |
| 4 | Echec de l'extraction des drivers |
| 5 | Echec du transfert (refus serveur, plan/ACK absent, ...) |
| 99 | Erreur inattendue (voir `extract-drivers.log`) |

**Attention** : les codes 2, 3 et 5 n'avaient pas le meme sens dans la version
SMB. Adapter les regles de supervision / de package Medulla qui les
interpretaient.

## 3. Contenu du dossier

```
ExtractDrivers-XMPP.ps1        script PowerShell (extraction + appel du transporteur)
Send-DriversOverXmpp.py        transporteur XMPP (inventaire, archive differentielle, blocs)
server/plugin_extract_drivers.py   plugin du substitut maitre (reception, depot)
tests/                         validation hors ligne (aucun reseau)
README.md / PROTOCOLE.md       ce document / specification du protocole
```

## 4. Deploiement du plugin serveur

1. Copier `server/plugin_extract_drivers.py` dans le dossier
   `pluginsmastersubstitute/` du serveur (a cote de `plugin_big_data.py`).
2. Definir l'emplacement du depot pour le service du substitut maitre :
   Les variables ne sont lues qu'au demarrage du service : drop-in systemd sur
   `pulse-xmpp-master-substitute-master.service` (`Environment=...`), puis `daemon-reload`
   et `restart` de ce seul service. Sur gla : `/var/lib/pulse2/imaging/postinst/sysprep/drivers` (le dossier du partage SMB `[drivers]`), sous-dossier vide.

   | Variable | Defaut | Role |
   |---|---|---|
   | `MEDULLA_DRIVERS_DEPOT` | `/mnt/drivers` | racine du depot (le dossier doit exister) |
   | `MEDULLA_DRIVERS_SUBDIR` | `drivers` | sous-dossier sous la racine ; **vide** = modeles directement sous la racine (disposition de l'ancien partage SMB) |
   | `MEDULLA_DRIVERS_REQUIRE_MOUNT` | `0` | `1` : refuser si la racine n'est pas un point de montage |

3. Aucun redemarrage n'est necessaire : le substitut maitre recharge le plugin a chaque
   trame recue (verifie sur gla). Les variables d'environnement, elles, ne sont lues
   qu'au demarrage du service.
4. Le plugin ecrit sous `<racine>[/<sous-dossier>]/<OS>/<Fabricant>/<Modele>/`
   (`DRIVERS/<Classe>/<package>/` et `CERTS/<empreinte>.cer`), plus
   `.extract-metadata.json`. Il **ne supprime jamais** de contenu existant.
   Les transferts en cours vivent dans `<racine>[/<sous-dossier>]/.incoming/`
   (nettoyes apres 7 jours d'abandon).
5. Dependance : le transfert de l'inventaire peut passer par le plugin natif
   `plugin_big_data` (si l'inventaire depasse 65535 caracteres). Celui-ci doit
   reinjecter `data["from"]` comme expediteur, ce qui est son comportement
   standard.

Limites cote serveur : archive 8 Gio, contenu decompresse 24 Gio, 200 000
entrees, 20 000 packages, 5 000 certificats.

## 5. Utilisation sur le poste

Prerequis : PowerShell 5.1, droits administrateur, agent Medulla installe
(Python `C:\Program Files\Python3\python.exe`, `slixmpp`, configuration
`C:\Program Files\Medulla\etc\agentconf.ini`).

```powershell
# Execution normale
powershell.exe -ExecutionPolicy Bypass -File .\ExtractDrivers-XMPP.ps1

# Verifier uniquement la connexion XMPP (aucune extraction, aucun transfert)
.\ExtractDrivers-XMPP.ps1 -CheckXmpp

# Simulation / conservation du dossier de travail
.\ExtractDrivers-XMPP.ps1 -DryRun
.\ExtractDrivers-XMPP.ps1 -KeepStaging
```

Le script extrait, construit l'inventaire, demande au serveur ce qui manque
(plan), n'archive que cela (zip deterministe), l'envoie par blocs et attend la
confirmation d'installation. Si le transfert est coupe, la relance reprend au
dernier point de controle (tous les 40 blocs) tant que le fichier partiel existe
cote serveur et que l'archive est identique (elle l'est : zip deterministe).

### Parametres principaux

| Parametre | Defaut | Role |
|---|---|---|
| `-ExtractMethod` | `pnp` | `pnp` ou `ddc` |
| `-RemoteAction` | `extract_drivers` | nom du plugin serveur |
| `-MasterJid` | `master@pulse` | destinataire |
| `-AckMode` | `required` | `required` / `optional` / `none` : exigence de confirmation finale |
| `-PlanTimeoutSeconds` | 120 | attente du plan apres l'inventaire |
| `-ResumeTimeoutSeconds` | 120 | attente de la reponse de reprise |
| `-AckTimeoutSeconds` | 300 | attente de la confirmation finale |
| `-ConnectTimeoutSeconds` | 30 | connexion / authentification |
| `-MaxRetries` / `-RetryDelaySeconds` | 3 / 15 | tentatives de transfert |
| `-SegmentBytes` | 25000 | taille des blocs bruts (1024 - 48000) |
| `-DelayMs` | 0 | pause entre trames |
| `-TotalTimeoutSeconds` | 3600 | delai global |
| `-CaCertPath`, `-SkipTlsVerify`, `-RequireStartTls` | - | options TLS |
| `-ConfigSource`, `-XmppServer`, `-XmppPort` | `auto` | origine du JID / forcage serveur |
| `-PythonPath`, `-AgentConfPath`, `-SenderScript` | auto | chemins |
| `-CheckXmpp`, `-KeepStaging`, `-DryRun`, `-Verbose` | - | diagnostic |

Les parametres `-TransportMode` et `-BigDataMaxMb` de la v1 n'existent plus.

## 6. Journaux et resultat

Dans `C:\ProgramData\Medulla\ExtractDrivers\` :

- `extract-drivers.log` : journal du script ;
- `xmpp-send.log`, `xmpp-console.log` : journal du transporteur ;
- `xmpp-result.json` : resultat machine-lisible.

Champs de `xmpp-result.json` : `status` (`ok`, `unconfirmed`, `error`),
`exit_code`, `retryable`, `sessionid`, `confirmed`, `frames_sent`,
`nothing_to_send`, `packages_sent`, `packages_skipped`, `certs_sent`,
`certs_skipped`, `resumed_from_block`, `archive` (taille, md5, sha256),
`depot_path`, `relative_dir`, `inventory`, `jid`, `master_jid`, `error`,
`duration_s`.

## 7. Depannage

| Symptome | Cause probable | Action |
|---|---|---|
| Code 3 | agent arrete, mot de passe XMPP, pare-feu 5222, TLS | `-CheckXmpp`, `--verbose`, verifier `agentconf.ini` |
| Code 5, "aucune reponse du serveur a l'inventaire" | plugin absent ou illisible | deployer le plugin dans `pluginsmastersubstitute/`, voir `/var/log/mmc/master-*.log` |
| Code 5, "depot introuvable cote serveur" | `MEDULLA_DRIVERS_DEPOT` faux ou partage non monte | corriger la variable / monter le depot |
| Code 5, "emetteur" | autre poste utilise la meme session | relancer |
| Code 5 apres coupure | transfert interrompu | relancer : reprise automatique |
| `unconfirmed` / code 0 avec `-AckMode optional` | serveur n'a pas acquitte | verifier le journal du substitut |
| Code 2 | `relative_dir` invalide, dossier vide, `-SegmentBytes` hors bornes | lire `extract-drivers.log` |

## 8. Securite du protocole

- Le plugin valide chaque nom (pas de `..`, ni `\`, ni caractere interdit) et
  `relative_dir` (exactement 3 composants), refuse zip-slip, chemins absolus,
  liens symboliques, archives chiffrees, entrees hors du modele demande ou
  packages/certificats non annonces dans l'inventaire.
- Chaque package extrait est recompare a l'empreinte de l'inventaire, chaque
  certificat a son sha256, **avant** toute installation dans le depot.
- Installation fichier par fichier (`tmp` + `os.replace`), sous verrou, sans
  suppression.
- Une session est liee a l'expediteur XMPP ; le client ignore toute reponse
  qui ne vient pas du `master` avec son propre `sessionid`.

## 9. Validation

```bash
python3 Send-DriversOverXmpp.py --self-test        # protocole, hors ligne
python3 tests/test_protocol.py                      # bout en bout (133 controles)
```

La suite execute le vrai transporteur et le vrai plugin avec un faux slixmpp :
premier transfert, second passage, differentiel, reprise (meme execution et
entre deux executions), blocs perdus/corrompus, ACK absent, refus serveur,
echecs de connexion, JID, rejeu de capture, gros transfert, et attaques par
archives fabriquees.

## 10. Packaging Medulla

Deployer sur les postes : `ExtractDrivers-XMPP.ps1` et
`Send-DriversOverXmpp.py` dans le meme dossier, commande
`powershell.exe -ExecutionPolicy Bypass -File ExtractDrivers-XMPP.ps1`, execute
en SYSTEM. Le plugin serveur se deploie une fois (section 4). Interpreter le
code 0 comme succes (y compris depot deja a jour) et 3/5 comme echecs
retentables.
