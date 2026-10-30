# Protocole XMPP `extract_drivers` - schema `medulla.extractdrivers.v2`

Specification entre `Send-DriversOverXmpp.py` (poste) et
`server/plugin_extract_drivers.py` (substitut maitre).

## 1. Encadrement dans le dispatcher Medulla

Chaque trame est un message XMPP `type=chat` vers `master@pulse`, dont le corps
est un JSON :

```json
{"action": "extract_drivers", "sessionid": "drivers_<horodatage>_<pid>_<alea>",
 "ret": 0, "base64": false, "data": { ... }}
```

`data` est toujours un dictionnaire non vide. Le serveur charge
`pluginsmastersubstitute/plugin_<action>.py` ; signature du plugin :
`action(xmppobject, action, sessionid, data, msg, ret, dataerreur)`.

Les reponses sont envoyees en `chat` vers `msg["from"]` avec le meme
`sessionid`. Le client n'accepte que les messages du JID `master` portant son
propre `sessionid`.

Le champ `data.type` distingue les trames : `inventory`, `meta`, `data`.

## 2. Deroulement

```
Poste                                   Serveur
  |-- inventory ----------------------->|  compare au depot
  |<------------------- plan (n parties)|  ce qui manque (ou done si rien)
  |-- meta (archive differentielle) --->|  prepare/recupere le .part
  |<---------------------------- resume |  prochain bloc attendu
  |-- data[next .. N-1] --------------->|  ecriture par index
  |<------------------ resend (eventuel)|  bloc perdu/corrompu (max 3 fois)
  |<----------------------------- done  |  verification + installation
```

### 2.1 Phase 1 - inventaire

```json
{"type":"inventory","schema":"medulla.extractdrivers.v2",
 "metadata":{"relative_dir":"Windows10/DellInc/OptiPlex_7090", "...":"..."},
 "packages":[{"id":"DRIVERS/Net/netrtl8111","files":2,"size":120040,"digest":"<sha256>"}],
 "certs":[{"thumbprint":"AABB...","size":300,"sha256":"<sha256>"}]}
```

- `digest` d'un package : sha256 du texte forme des lignes
  `"<chemin relatif posix>\t<taille>\t<sha256>\n"`, triees par chemin relatif.
  Le client et le serveur utilisent le meme calcul (verifie par les tests).
- Si le JSON depasse 65535 caracteres, l'inventaire est emis dans une trame
  `big_data` (zlib + base64, tranches de 65535) ; le plugin natif reinjecte
  `data["from"]`. Les blocs de la phase 3 n'utilisent **jamais** `big_data`.

Le serveur determine ce qui est necessaire : un package est requis si le dossier
cible est absent ou si sa signature (nombre de fichiers, octets) differe ; un
certificat si absent ou si taille/sha256 different.

Reponses :

- Rien a envoyer : `<action>_done` avec
  `{"status":"ok","nothing_to_send":true,"relative_dir","depot_path","packages_skipped","certs_skipped"}`.
  Le client se termine en code 0.
- Sinon : une ou plusieurs trames `<action>_plan`
  `{"status":"plan","part","parts","need":[...],"need_total","packages_skipped","certs_skipped"}`,
  par paquets de 4000 indices. Indice de package `>= 0` (position dans
  `packages`), indice de certificat `-(i+1)`.

### 2.2 Phase 2 - archive et reprise

Le client construit un zip **deterministe** des seuls elements requis :
entrees triees, date fixe 1980-01-01, `create_system=0`, `external_attr=0`,
zip64 pour les fichiers >= 2 Gio, pas de `metadata.json`. Noms d'entrees :
`<relative_dir>/<id du package>/<chemin>` et `<relative_dir>/CERTS/<empreinte>.cer`.
Un meme contenu donne donc toujours le meme sha256, ce qui permet la reprise.

Trame `meta` :

```json
{"type":"meta","schema":"medulla.extractdrivers.v2","delta":true,
 "size":123,"md5":"...","sha256":"...","segment_bytes":25000,"segment_total":N,
 "unpacked_size":456,"filename":"...","packages":3,"certs":2,
 "metadata":{"relative_dir":"..."}}
```

Le serveur indexe le transfert par le sha256 : `.incoming/<sha256>.part` et
`.json` (etat). Reponse `<action>_resume`
`{"status":"resume","next_segment":K,"segment_total":N}`, ou directement
`_done` si le `.part` est deja complet. L'etat est ecrit tous les 40 blocs
contigus : apres coupure, la reprise redemarre au dernier multiple de 40.

### 2.3 Phase 3 - blocs

```json
{"type":"data","segment_idx":K,"segment_total":N,"raw_size":25000,
 "md5_segment":"...","data_b64":"<zlib+base64>","last":false}
```

Taille de bloc brute : 25000 par defaut, bornes 1024 - 48000. Le dernier bloc
porte `last:true`, `md5_total` et `sha256_total`.

Le serveur ecrit chaque bloc a son index. Un bloc invalide (md5, taille) ou
manquant provoque `<action>_resend {"segment_idx":K}` (3 renvois maximum par
bloc, sinon `_error`).

### 2.4 Finalisation

1. verification taille, md5, sha256 de l'archive ;
2. `plan_zip_entries` : validation de **toutes** les entrees (voir 4) ;
3. extraction dans un dossier temporaire ;
4. verification de chaque package (empreinte) et chaque certificat (sha256)
   contre l'inventaire ;
5. installation sous verrou, fichier par fichier (`tmp` + `os.replace`),
   sans jamais supprimer.

Reponse `<action>_done` :
`{"status":"ok","relative_dir","depot_path","sha256","bytes","packages_received","certs_received","packages_skipped","certs_skipped"}`.

## 3. Erreurs et nouvelles tentatives

`<action>_error` : `{"status":"error","message":"...","retryable":true|false}`.

| Situation | Comportement client |
|---|---|
| Plan non recu dans `--plan-timeout` | echec code 5, **non** retentable |
| Reponse de reprise non recue | echec, retentable |
| ACK final absent | `required` : code 5 ; `optional` : code 0, `status:"unconfirmed"` ; `none` : code 0 |
| `_error` `retryable:false` | code 5, aucune nouvelle tentative |
| Coupure de connexion | nouvelle tentative (nouvelle session, reprise grace au sha256) |
| Authentification / connexion | code 3 |

## 4. Regles de validation cote serveur

- Nom de composant : `^[^\x00-\x1f\x7f\\/:*?"<>|]{1,200}$`, ni `.` ni `..`, pas
  d'espace en debut/fin, pas de `.` final.
- `relative_dir` : exactement 3 composants valides, aucun ne commence par `.`.
- Empreinte de certificat : `^[0-9A-Fa-f]{8,128}$`.
- Entrees du zip : pas de chemin absolu, de lecteur, d'antislash, de `..`, de
  lien symbolique ni de chiffrement ; toutes sous `relative_dir` ; chaque
  package/certificat doit figurer dans l'inventaire **et** dans le plan.
- Limites : archive 8 Gio, decompresse 24 Gio, 200 000 entrees, 20 000
  packages, 5 000 certificats.
- Session liee au JID de l'expediteur ; un autre expediteur est refuse pendant
  `ACTIVE_TTL` (180 s) ; session purgee apres 6 h ; restes `.incoming` purges
  apres 7 jours.

## 5. Arborescence du depot

```
<DEPOT_ROOT>[/<DEPOT_SUBDIR>]/<OS>/<Fabricant>/<Modele>/
    DRIVERS/<Classe>/<package>/...
    CERTS/<empreinte>.cer
    .extract-metadata.json
<DEPOT_ROOT>[/<DEPOT_SUBDIR>]/.incoming/<sha256>.part|.json
```

Nommage : `<Fabricant>` = fabricant sans espaces ni points, `<Modele>` = modele avec
`_` a la place des espaces (comme l'ancien script). Quand le BIOS renvoie une valeur
bidon (`Default string`, `System Product Name`, `To Be Filled By O.E.M.`...), le poste
prend la carte mere (`Win32_BaseBoard`), puis `Win32_ComputerSystemProduct` et le SKU pour le modele, ou le BIOS pour le fabricant ; sinon `Inconnu` (modele : `Inconnu_BIOS-<version>` quand la version du BIOS est renseignee).
Les valeurs d'origine restent dans `.extract-metadata.json` (`manufacturer_raw`, `model_raw`).

## 6. Outils de validation

```bash
python3 Send-DriversOverXmpp.py --self-test
python3 tests/test_protocol.py
# Capture puis rejeu des trames
python3 Send-DriversOverXmpp.py ... --dump-frames trames.jsonl
python3 tests/mock_receiver.py --frames trames.jsonl --depot /tmp/depot
```
