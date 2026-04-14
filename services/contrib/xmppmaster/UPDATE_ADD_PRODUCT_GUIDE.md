# Guide: ajouter un produit WSUS dans xmppmaster

Ce document explique comment ajouter un nouveau produit, avec la convention de nommage, la source attendue des donnees de mises a jour et la progression dans les schemas SQL.

Exemple cible: Windows Security platform (comme dans schema-100.sql).

## 1) Source obligatoire des donnees update_data

Les procedures produit de xmppmaster travaillent sur la table:

- xmppmaster.update_data

Mais cette table n est pas la source primaire des mises a jour.

Le flux attendu est le suivant:

1. Les mises a jour doivent d abord exister dans base_wsusscn2.update_data.
2. Cette table est generee par le projet integration/medulla-wsusdb.
3. La procedure xmppmaster.up_reinit_table_update_data recree ensuite xmppmaster.update_data comme image de base_wsusscn2.update_data.

Point important:

- Pour qu un nouveau produit soit exploitable dans xmppmaster, ses mises a jour doivent donc etre presentes dans base_wsusscn2.update_data.
- Il ne faut pas considerer xmppmaster.update_data comme la source a alimenter manuellement en premier.

Documentation de reference pour generer et completer la base source:

- integration/medulla-wsusdb/medulla-wsusdb-create-base-wsusscn2.md : generation de la base base_wsusscn2 a partir de wsusscn2.cab.
- integration/medulla-wsusdb/medulla-wsusdb-inject-extracted-packages.md : injection complementaire depuis le Microsoft Update Catalog pour les mises a jour tres recentes.

Quand l option update_data_injection = yes est active dans le projet medulla-wsusdb:

- les mises a jour absentes de la base issue de wsusscn2.cab sont ajoutees dans base_wsusscn2.update_data ;
- cela permet ensuite de regenerer xmppmaster.update_data avec ces mises a jour recentes.

## 2) Tables en jeu pour un ajout de produit

Les tables principales impliquees dans l ajout d un produit sont les suivantes.

### base_wsusscn2.update_data

- C est la source primaire des mises a jour.
- Elle est generee par integration/medulla-wsusdb a partir de wsusscn2.cab, puis eventuellement completee via Microsoft Update Catalog.
- Si les lignes du produit n existent pas ici, le produit ne pourra pas etre reconstruit correctement dans xmppmaster.

### xmppmaster.update_data

- C est la copie de travail utilisee par les procedures xmppmaster.
- Elle est recreee a partir de base_wsusscn2.update_data par la procedure up_reinit_table_update_data().
- Toutes les procedures de creation de tables produit lisent cette table.

### xmppmaster.applicationconfig

- Cette table contient la configuration declarative des produits et des regles.
- Pour un produit, on y ajoute une ligne avec:
  - key = table produits
  - value = nom de la table produit, par exemple up_packages_Win11_X64_25H2
  - context = entity
  - module = xmppmaster/update
  - enable = 1 ou 0 selon l activation par defaut
- Cette table sert aussi a stocker les regles automatiques avec les entrees table rules.

### xmppmaster.up_packages_<ProductToken>

- Ce sont les tables produit construites a partir de xmppmaster.update_data.
- Chaque table contient le sous-ensemble des mises a jour correspondant a un produit cible.
- Exemple existant: xmppmaster.up_packages_Win11_X64_21H2.
- Exemple d ajout: xmppmaster.up_packages_Win11_X64_25H2.

### xmppmaster.up_list_produit

- Cette table associe les produits aux entites.
- Elle est alimentee a partir de xmppmaster.applicationconfig par les procedures de generation par entite.
- Le champ name_procedure contient en pratique le nom de la table produit, par exemple up_packages_Win11_X64_25H2.

### xmppmaster.up_auto_approve_rules

- Cette table contient les regles d approbation automatique des mises a jour par entite.
- Elle est alimentee a partir de xmppmaster.applicationconfig pour les lignes de type table rules.

### xmppmaster.local_glpi_entities

- Cette table sert de reference pour verifier qu une entite existe avant d initialiser ses produits ou ses regles.
- Les procedures up_genere_list_produit_entity() et up_genere_list_rule_entity() s appuient dessus.

## 3) Vue PHP et visibilite des produits

La vue PHP de selection des produits se trouve dans:

- web/modules/updates/updates/ajaxApproveProduct.php

Son role est d afficher a l utilisateur la liste des produits approuvables pour une entite, avec une case a cocher par produit.

Flux utilise par la vue:

1. ajaxApproveProduct.php appelle xmlrpc_get_approve_products().
2. Le backend retourne les lignes de xmppmaster.up_list_produit pour l entite, filtrees par la configuration active.
3. La vue affiche ensuite les produits par famille Windows, Office, Visual Studio, Server, etc.

Point important:

- Seuls les produits declares dans xmppmaster.applicationconfig avec enable = 1 doivent etre visibles dans cette vue.
- Le champ enable de xmppmaster.applicationconfig controle la visibilite fonctionnelle du produit dans l interface.
- Le champ enable de xmppmaster.up_list_produit reste, lui, l etat de selection du produit pour l entite.

En pratique:

- si un produit existe dans xmppmaster.up_list_produit mais que son entree correspondante est desactivee dans xmppmaster.applicationconfig, il ne doit pas etre affiche a l utilisateur ;
- si un produit est actif dans xmppmaster.applicationconfig, il peut etre affiche dans la vue, puis coche ou decocher par entite via xmppmaster.up_list_produit.

## 4) Procedures en jeu et utilite

Voici les procedures importantes pour comprendre le cycle complet d ajout d un produit.

### up_reinit_table_update_data()

Utilite:

- Recopier base_wsusscn2.update_data dans xmppmaster.update_data.
- Recreer les index necessaires sur la copie xmppmaster.

Role pratique:

- C est la passerelle entre la base WSUS source et les procedures xmppmaster.
- Elle doit etre executee apres mise a jour de base_wsusscn2.update_data et avant regeneration des tables produit.

Tables utilisees:

- lecture: base_wsusscn2.update_data
- ecriture: xmppmaster.update_datacopy puis xmppmaster.update_data

### up_create_product_tables()

Utilite:

- Parcourir toutes les procedures dont le nom suit la convention up_init_packages_%.
- Les executer dynamiquement une par une.

Role pratique:

- Cette procedure regenere en une fois toutes les tables produit declarees par convention de nommage.
- Elle evite d appeler manuellement chaque procedure produit.

Tables et objets utilises:

- lecture: information_schema.ROUTINES pour trouver les procedures
- execution: toutes les procedures up_init_packages_*
- effet final: recreation des tables xmppmaster.up_packages_*

### up_genere_list_produit_entity(p_entity_id)

Utilite:

- Initialiser les produits disponibles pour une entite.
- Inserer dans xmppmaster.up_list_produit les produits declares dans xmppmaster.applicationconfig.

Role pratique:

- Cette procedure rattache les produits a une entite donnee.
- Elle utilise les entrees configurees avec key = table produits et context = entity.

Tables utilisees:

- lecture: xmppmaster.applicationconfig
- verification: xmppmaster.local_glpi_entities
- ecriture: xmppmaster.up_list_produit

### up_genere_list_rule_entity(p_entity_id)

Utilite:

- Initialiser les regles automatiques pour une entite.
- Inserer dans xmppmaster.up_auto_approve_rules les regles declarees dans xmppmaster.applicationconfig.

Role pratique:

- Cette procedure prepare les regles d approbation automatique pour l entite.
- Elle lit les entrees de configuration correspondant aux table rules.

Tables utilisees:

- lecture: xmppmaster.applicationconfig
- verification: xmppmaster.local_glpi_entities
- ecriture: xmppmaster.up_auto_approve_rules

### up_init_packages_<ProductToken>()

Utilite:

- Creer ou recreer la table produit correspondant a un produit cible.
- Filtrer xmppmaster.update_data selon des criteres metier title, product, architecture, famille, etc.

Role pratique:

- Chaque procedure up_init_packages_* produit une table xmppmaster.up_packages_*.
- C est le coeur de l ajout d un nouveau produit.

Exemple concret:

- up_init_packages_Win11_X64_25H2() supprime puis recree up_packages_Win11_X64_25H2.
- Elle lit xmppmaster.update_data avec la jointure historique:
  - aa = ligne de mise a jour principale
  - bb = ligne jointe via bb.bundledby_revision = aa.revisionid pour recuperer notamment payloadfiles et updateid_package

Tables utilisees:

- lecture: xmppmaster.update_data
- ecriture: xmppmaster.up_packages_<ProductToken>

## 5) Convention de nommage

Respecter strictement ce pattern pour etre pris en charge automatiquement par la procedure dynamique up_create_product_tables (definie dans schema-095.sql):

- Nom de procedure: up_init_packages_<ProductToken>
- Nom de table creee: up_packages_<ProductToken>

Exemple:

- Procedure: up_init_packages_Windows_Security_platform
- Table: up_packages_Windows_Security_platform

Important:

- Le prefixe doit etre exactement up_init_packages_ (avec s a packages).
- Si le prefixe change, la procedure dynamique ne trouvera pas la procedure.

## 6) Ajouter la procedure dans le schema courant

Dans le nouveau schema (par exemple schema-100.sql, ou schema-101.sql pour un prochain ajout):

1. Ajouter DROP PROCEDURE IF EXISTS sur le nom de procedure.
2. Creer la procedure avec DELIMITER $$ ... END$$.
3. Dans la procedure:
   - DROP TABLE IF EXISTS up_packages_<ProductToken>
   - CREATE TABLE up_packages_<ProductToken> AS SELECT ...
   - Utiliser la jointure standard:
     - aa = xmppmaster.update_data
     - bb = xmppmaster.update_data ON bb.bundledby_revision = aa.revisionid
   - Conserver les colonnes standard deja utilisees par les autres produits.
4. Filtrer avec les criteres du produit (title, product, exclusions ARM64/X86/Dynamic si necessaire).

Exemple de filtre pour Windows Security platform:

- aa.product LIKE '%Windows Security platform%'
- aa.title LIKE '%Windows Security platform%'

Remarque:

- Si aucune ligne pertinente n existe deja dans base_wsusscn2.update_data puis xmppmaster.update_data, la table produit sera creee mais vide.

## 7) Ordre logique d utilisation des procedures

Pour un ajout de produit, l ordre logique est le suivant:

1. Alimenter base_wsusscn2.update_data via le projet medulla-wsusdb.
2. Executer up_reinit_table_update_data() pour remettre a jour xmppmaster.update_data.
3. Ajouter ou mettre a jour la procedure up_init_packages_<ProductToken>().
4. Ajouter ou mettre a jour l entree correspondante dans xmppmaster.applicationconfig.
5. Executer up_create_product_tables() pour recreer les tables produit.
6. Executer up_genere_list_produit_entity(p_entity_id) pour exposer le produit a une entite.
7. Executer up_genere_list_rule_entity(p_entity_id) si l entite doit aussi recevoir les regles automatiques.

## 8) Prise en compte automatique via up_create_product_tables

La procedure up_create_product_tables (schema-095.sql) execute dynamiquement toutes les procedures dont le nom matche:

- up_init_packages_%

Donc:

- Si votre nouvelle procedure respecte le nommage, elle sera appelee automatiquement.
- Il est inutile de redefinir up_create_product_tables dans chaque nouveau schema.

Dans le schema d ajout, on garde seulement l appel:

- CALL xmppmaster.up_create_product_tables();

## 9) Enregistrer le produit pour les entites

Pour que le produit apparaisse dans la gestion par entite (table up_list_produit), il faut ajouter une entree dans applicationconfig avec:

- key = 'table produits'
- value = up_packages_<ProductToken>
- context = 'entity'
- module = 'xmppmaster/update'
- enable = 1 pour activer le produit par defaut (cas recommande ici)

Exemple:

- value = up_packages_Windows_Security_platform

Exemple SQL complet (comme schema-100.sql):

```sql
INSERT IGNORE INTO `xmppmaster`.`applicationconfig` (
  `key`,
  `value`,
  `comment`,
  `context`,
  `module`,
  `enable`
) VALUES (
  'table produits',
  'up_packages_Windows_Security_platform',
  'Windows Security platform',
  'entity',
  'xmppmaster/update',
  1
);
```

Remarque:

- up_list_produit utilise les valeurs issues de applicationconfig.
- Le champ name_procedure de up_list_produit doit correspondre au nom de table produit (up_packages_*), pas au nom de procedure SQL.

## 10) Progression schema par schema

Checklist migration:

1. Verifier que les mises a jour du produit existent bien dans base_wsusscn2.update_data.
2. Regenerer xmppmaster.update_data depuis cette source si necessaire.
3. Creer la procedure up_init_packages_<ProductToken> dans le schema N.
4. Ajouter ou mettre a jour l entree applicationconfig pour table produits.
5. Lancer CALL xmppmaster.up_create_product_tables(); dans le schema N.
6. Mettre a jour UPDATE version SET Number = N.

Pour un produit actif immediatement, utiliser enable = 1 a l etape 4.

## 11) Verification rapide avant et apres migration

Verifier d abord la presence des mises a jour dans la base source:

- SELECT COUNT(*) FROM base_wsusscn2.update_data WHERE product LIKE '%Windows Security platform%' OR title LIKE '%Windows Security platform%';

Verifier ensuite la presence dans la copie xmppmaster:

- SELECT COUNT(*) FROM xmppmaster.update_data WHERE product LIKE '%Windows Security platform%' OR title LIKE '%Windows Security platform%';

Verifier que la procedure existe:

- SHOW PROCEDURE STATUS WHERE Db='xmppmaster' AND Name='up_init_packages_Windows_Security_platform';

Verifier que la table produit est creee:

- SHOW TABLES LIKE 'up_packages_Windows_Security_platform';

Verifier que le produit est present dans applicationconfig:

- SELECT `key`, `value`, `context`, `module`, `enable`
  FROM xmppmaster.applicationconfig
  WHERE `key`='table produits'
    AND `value`='up_packages_Windows_Security_platform';

Verifier la presence dans up_list_produit (apres regen):

- SELECT *
  FROM xmppmaster.up_list_produit
  WHERE name_procedure='up_packages_Windows_Security_platform';

## 12) Erreurs frequentes

- Alimenter uniquement xmppmaster.update_data sans traiter la source base_wsusscn2.update_data.
- Oublier l injection complementaire du Microsoft Update Catalog si le produit depend de mises a jour tres recentes.
- Oublier que la vue PHP doit masquer les produits dont xmppmaster.applicationconfig.enable = 0.
- Oublier le s dans up_init_packages_.
- Enregistrer dans up_list_produit un nom de procedure au lieu du nom de table up_packages_*.
- Redefinir up_create_product_tables dans un schema plus recent et ecraser la version dynamique.
- Oublier l entree applicationconfig, ce qui empeche l exposition par entite.

## 13) Flux complet d activation: exemple Win11 25H2

Le cas Win11 25H2 permet de verifier tout le chemin fonctionnel, depuis la declaration du produit jusqu a la case visible dans la page MMC.

Dans schema-098.sql:

- la procedure up_init_packages_Win11_X64_25H2() cree la table xmppmaster.up_packages_Win11_X64_25H2 ;
- une entree applicationconfig active est ajoutee pour up_packages_Win11_X64_25H2 avec enable = 1 ;
- une entree applicationconfig inactive est ajoutee pour up_packages_Win11_X64_26H2 avec enable = 0.

Le flux complet est alors le suivant:

1. base_wsusscn2.update_data contient les lignes WSUS du produit.
2. up_reinit_table_update_data() recree xmppmaster.update_data.
3. up_init_packages_Win11_X64_25H2() recree xmppmaster.up_packages_Win11_X64_25H2.
4. L entree active de xmppmaster.applicationconfig reference up_packages_Win11_X64_25H2.
5. Quand la page approve_products.php charge la vue ajaxApproveProduct.php, elle appelle xmlrpc_get_approve_products(entity_id).
6. Le backend xmppmaster.get_approve_products() appelle d abord up_genere_list_produit_entity(entity_id), ce qui insere dans xmppmaster.up_list_produit les produits actifs de applicationconfig manquants pour cette entite, avec enable = 0 par defaut.
7. Le meme backend relit ensuite xmppmaster.up_list_produit en le joignant a xmppmaster.applicationconfig, avec le filtre applicationconfig.enable = 1.
8. Resultat: Win11 25H2 est visible dans la page, alors que Win11 26H2 reste masque tant que son entree applicationconfig reste a 0.
9. Dans la vue PHP, la visibilite depend donc de applicationconfig.enable, mais l etat coche ou non coche depend de up_list_produit.enable.
10. Quand l utilisateur valide le formulaire, approve_products.php appelle xmlrpc_update_approve_products(), qui met a jour up_list_produit.enable pour l entite.
11. Le plugin agent ne lit ensuite que les produits coches via list_produits_entity(entity_id, enable = 1).

Consequences pratiques:

- un produit peut etre visible dans la page mais non actif pour les machines de l entite si sa case n est pas cochee ;
- un produit non visible ne peut pas etre active par erreur depuis la page tant que son entree applicationconfig reste desactivee ;
- applicationconfig.enable pilote l exposition du produit ; up_list_produit.enable pilote son activation effective pour l entite.

Verification SQL minimale pour Win11 25H2:

- SELECT value, enable FROM xmppmaster.applicationconfig WHERE value IN ('up_packages_Win11_X64_25H2', 'up_packages_Win11_X64_26H2');
- SELECT entity_id, name_procedure, enable FROM xmppmaster.up_list_produit WHERE entity_id = <ENTITY_ID> AND name_procedure IN ('up_packages_Win11_X64_25H2', 'up_packages_Win11_X64_26H2');

Lecture attendue:

- up_packages_Win11_X64_25H2 apparait dans applicationconfig avec enable = 1 ;
- up_packages_Win11_X64_26H2 peut exister dans applicationconfig, mais reste invisible dans la page tant que enable = 0 ;
- dans up_list_produit, Win11 25H2 peut etre present avec enable = 0 ou 1 selon le choix de l entite ;
- le plugin ne prendra en compte Win11 25H2 que si up_list_produit.enable = 1.

## 14) Traitement dans plugin_update_windows.py

Le traitement agent se trouve dans medulla-agent, dans pulse_xmpp_master_substitute/pluginsmastersubstitute/plugin_update_windows.py.

Ce plugin ne lit pas directement xmppmaster.applicationconfig. Il consomme la selection deja preparee pour l entite dans xmppmaster.up_list_produit.

Flux fonctionnel du plugin:

1. action() verifie que la charge utile recue est bien un dictionnaire, journalise l appel et extrait hostname et bare_jid depuis le champ from du message XMPP.
2. Au premier appel, le plugin charge sa configuration via read_conf_remote_update_windows(), notamment exclude_history_list et deployment_intervals.
3. traitement_update() verifie la presence de system_info dans l inventaire remonte par l agent Windows.
4. getIdsEntityMachineInventaireFromJid() retrouve la machine inventaire et son entity_id a partir du JID.
5. ensure_auto_approve_rules_for_entity(entity_id) initialise les regles par defaut si aucune n existe encore dans up_auto_approve_rules.
6. list_produits_entity(entity_id) lit uniquement les produits coches pour l entite, c est a dire les lignes de up_list_produit avec enable = 1.
7. list_products_on() compare cette selection avec les informations d inventaire remontees par la machine pour ne garder que les tables produit pertinentes.

Le filtrage par inventaire dans list_products_on() repose principalement sur:

- system_info.platform_info.type pour distinguer Windows 10, Windows 11 ou Windows Server ;
- system_info.platform_info.machine pour l architecture X64, X86, ARM64 ;
- system_info.infobuild.ProductName et DisplayVersion pour choisir la bonne table OS, par exemple up_packages_Win11_X64_25H2 ;
- system_info.office et system_info.visual pour ajouter les tables Office ou Visual Studio si elles sont aussi cochees pour l entite.

Gestion des KB deja installees:

- si system_info.kb_list est absent, le plugin le reconstruit depuis system_info.kb_installed ;
- si exclude_history_list est a False, le plugin enrichit cette liste avec history_package_uuid via history_list_kb() pour eviter de reproposer des mises a jour deja deployees par le passe.

Recherche des mises a jour candidates:

1. test_black_list(jid, entity_id) charge les exclusions KB et updateid applicables a la machine.
2. Pour chaque table produit retenue:
   - cas standard: search_update_by_products(tableproduct, kb_list) appelle la procedure SQL up_search_kb_update ;
   - cas Windows Security platform: le plugin verifie la presence de la KB 5007651, lit InstalledOn, puis appelle search_update_windows_security_platform() ;
   - cas MSRT: le plugin exploite malicious_software_removal_tool et appelle search_update_windows_malicious_software_tool().
3. exclude_update_in_select() retire ensuite des resultats toutes les KB et tous les updateid presents dans la black list.

Synchronisation des mises a jour trouvees:

1. del_all_Up_machine_windows() nettoie les enregistrements devenus inutiles pour la machine et l entite.
2. setUp_machine_windows() enregistre les mises a jour retenues dans up_machine_windows.
3. setUp_machine_windows_gray_list() ajoute ou rafraichit chaque update retenu dans up_gray_list pour l entite.
4. select_updatepackageid_produit_table() prepare en parallele les mises a jour qui doivent etre desinstallees.
5. add_uninstall_kb_machine() puis deployuninstall() declenchent si besoin un flux de desinstallation.

Attention sur la disponibilite reelle du package:

- l ajout dans up_gray_list ne signifie pas que le package est instantanement disponible dans le partage ;
- l insertion en gray list declenche une commande differee vers up_action_update_packages ;
- cette commande appelle medulla_mysql_exec_update.sh, qui lance ensuite medulla-mariadb-move-update-package.py pour creer ou publier le package ;
- la creation peut inclure la recherche du payload, le telechargement depuis Windows Update ou Microsoft, puis la generation des fichiers de package Medulla ;
- cette etape n est executee que si necessaire: si le package existe deja completement sur disque ou dans le partage, le script ne le recree pas.

Consequence importante:

- juste apres qu une mise a jour entre en gray list, il peut exister une latence avant qu elle soit effectivement deployable ;
- pendant cette fenetre, la mise a jour est connue en base, mais son package peut ne pas encore etre present dans pkgs ou dans /var/lib/pulse2/packages/sharing/winupdates ;
- c est pour cela que le plugin verifie ensuite la presence du package en base et sur le disque, et journalise un avertissement si le package n est pas encore pret.

Point cle:

- la page d administration agit sur up_list_produit.enable ;
- le plugin n exploite ensuite que cette selection active ;
- la machine ne recoit donc des recherches de mises a jour que pour les familles de produits visibles puis explicitement cochees pour son entite.

## 15) Black list, gray list et white list

Les trois listes n ont pas le meme role et interviennent a des moments differents du cycle.

### Black list

- Table: xmppmaster.up_black_list.
- Role: exclusion explicite d une mise a jour, soit par KB, soit par updateid.
- Portee: la regle est portee par entityid et peut etre ciblee par userjid_regexp.
- Effet dans le plugin: test_black_list() charge ces exclusions avant la selection finale et exclude_update_in_select() retire les updates correspondants.
- Effet base de donnees: les triggers de up_black_list suppriment aussi des entrees de up_gray_list et up_gray_list_flop pour les regles globales userjid_regexp = '.*'.

### Gray list

- Table: xmppmaster.up_gray_list.
- Role: zone de staging des mises a jour detectees comme applicables a une entite.
- Alimentation: le plugin appelle setUp_machine_windows_gray_list() apres avoir retenu une mise a jour pour une machine.
- Source des donnees: insertion depuis la table produit concernee up_packages_*.
- Effet systeme: l insertion en gray list alimente la file xmppmaster.up_action_update_packages, qui est ensuite lue cycliquement pour lancer la creation ou la publication du package.
- Sens du champ valided:
  - valided = 0: mise a jour detectee mais non encore approuvee ;
  - valided = 1: mise a jour validee, exploitable par la logique de packages deployables.
- Particularite: si une mise a jour existe deja en white list pour l entite, setUp_machine_windows_gray_list() ne la reinjecte pas en gray list.
- Particularite operationnelle: une mise a jour peut donc etre visible en gray list avant que son package soit completement cree et disponible au deploiement.

### White list

- Table: xmppmaster.up_white_list.
- Role: stocker les mises a jour explicitement approuvees.
- Alimentation: approve_update() copie une entree depuis up_gray_list vers up_white_list avec valided = 1.
- Effet pratique: une mise a jour approuvee reste referencee dans la white list pour l entite, et le plugin evite ensuite de la remettre dans la gray list.

### Relation entre les trois listes

- black list = ne jamais proposer pour la cible concernee ;
- gray list = candidat detecte, encore en observation ou en validation ;
- white list = candidat approuve explicitement.

En resume:

- applicationconfig decide quels produits peuvent etre exposes ;
- up_list_produit decide quels produits sont actifs pour l entite ;
- le plugin transforme cette selection par produit en liste concrete de KB et updateid applicables ;
- black list retire des updates ;
- gray list stocke les updates detectes ;
- gray list declenche aussi, si necessaire, la creation asynchrone du package ;
- white list memorise les updates approuves.
