# Outils de diagnostic

Ces scripts ne font pas partie des suites de tests : ce sont des **sondes**
utilisées pour diagnostiquer un incident sur une instance déployée. Ils se
lancent sur le serveur Medulla (ou depuis un poste qui l'atteint).

| Outil | Ce qu'il fait | Quand l'utiliser |
|---|---|---|
| `probe_xmlrpc.py` | interroge le mmc-agent en XMLRPC et affiche la réponse brute | l'interface dit « réponse inattendue de l'agent » |
| `guacd_probe.py` | pilote **guacd** en direct avec les paramètres d'une connexion Guacamole et rapporte la vraie erreur | une session distante ne s'ouvre pas |
| `compare_rdp_usable.py` | compare une cible RDP saine et une cible cassée avec des identifiants factices | comprendre un `Upstream error` RDP |
| `probe_rdp_security.py` | demande à un serveur RDP le mode de sécurité qu'il sélectionne (standard / TLS / NLA) | vérifier ce qu'annonce une machine |
| `inspect_guacamole_api.py` | liste les connexions Guacamole et leurs paramètres via l'API REST | vérifier ce que la page a réellement enregistré |
| `probe_methods.py` | liste les méthodes XMLRPC exposées par l'agent | douter de la présence d'une méthode |
| `probe_session.py` | ouvre une session XMLRPC et appelle une méthode authentifiée | reproduire un appel de la console |
| `test_ssh_session_live.py` | crée une connexion SSH puis ouvre une session guacd | vérifier la prise en main SSH |
| `test_sshkey_live.py` | **ajoute une clé de test au compte `support`**, vérifie la session par clé, puis **restaure `authorized_keys`** | valider l'authentification par clé (à manier avec précaution) |
| `repro_admin_activation.py` | reproduit l'activation du plugin admin | le journal signale « Plugin admin not loaded » |
| `repro_status_poll.py` | interroge un statut de tâche en boucle pendant son exécution | soupçonner une réponse vide sur `browse_parc_status` |
| `time_agents.py` | chronomètre la liste des agents déployables | soupçonner une lenteur côté agent |

**Rappel** : plusieurs de ces sondes ouvrent de vraies sessions RDP ou SSH avec
des identifiants factices. Sur certaines machines (Windows en particulier), cela
**sature la limite de sessions** et fait échouer les tentatives suivantes pendant
quelques minutes. À utiliser avec discernement sur un parc en production.
