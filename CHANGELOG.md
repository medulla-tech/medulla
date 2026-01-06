# Change Log

## [5.4.6](https://github.com/medulla-tech/medulla/releases/tag/5.4.6) (2025-12-31)
- [FEATURE] Add regex-based team filtering for profiles
- [FEATURE] Add proxy support for OIDC providers
- [BUGFIX]  Improve the time to get the xmpp computers page

## [5.4.5](https://github.com/medulla-tech/medulla/releases/tag/5.4.5) (2025-12-17)
- [FEATURE] Dashboard widgets are now based on user's allowed entities
- [FEATURE] Improve speed of query listing machines of allowed entities
- [BUGFIX]  Fix display of packages list
- [BUGFIX]  Fix filtering of packages based on machine's OS
- [BUGFIX]  Fix traceback on update by machine page when the list is empty
- [BUGFIX]  Fix traceback on dashboard right after login
- [BUGFIX]  Update the progress bar style on details by machine update view
- [BUGFIX]  Fix external ldap default organisation to MMC when now provided
- [BUGFIX]  Fix filter used on group for updates
- [BUGFIX]  Fix import in package server when used on relays
- [BUGFIX]  Improve handling of kiosk updates after package creation

## [5.4.4](https://github.com/medulla-tech/medulla/releases/tag/5.4.4) (2025-12-01)
- [FEATURE] Dashboard widgets are now scoped to the user’s allowed entities
- [FEATURE] Initial support for GLPI version 11
- [FEATURE] Support for Ubuntu distributions for clients
- [FEATURE] Improve imaging experience on post imaging scripts and master images
- [BUGFIX]  Fix support for ITSM-NG version 2.1
- [BUGFIX]  Fix insertion of packages in the database when shares other than global are used
- [BUGFIX]  Fix detection of Linux distributions for quick actions

## [5.4.3](https://github.com/medulla-tech/medulla/releases/tag/5.4.3) (2025-11-19)
- [FEATURE] Update Office and Visual Studio through Windows update module
- [FEATURE] Remove unused locale
- [FEATURE] Improve translations
- [FEATURE] When a user password is changed in Medulla, also change it in GLPI
- [FEATURE] Improve display of quick action results
- [FEATURE] Add support for ITSM-NG version 2.1
- [BUGFIX]  Fix packages depencies list which was empty
- [BUGFIX]  Fix getting of user profiles when glpi database name is not glpi
- [BUGFIX]  Fix broken deployments 
- [BUGFIX]  Various fixes due to a broken stylesheet
- [BUGFIX]  Fix use of filters in table views
- [BUGFIX]  Fix inventory quick action that didn't run
- [BUGFIX]  Fix duplication of deployments on groups
- [BUGFIX]  Fix convergence deployments

## [5.4.2](https://github.com/medulla-tech/medulla/releases/tag/5.4.2) (2025-10-31)
- [FEATURE] Improve styles across the web interface
- [FEATURE] Improve user experience on various modules
- [FEATURE] Add support for Windows Servers in Updates Module
- [FEATURE] Manage Medulla users from the Admin module
- [FEATURE] Define update deployment rules per entity in Updates module
- [FEATURE] Improve the handling of drivers in Imaging module
- [BUGFIX]  Fix creation of entities having an apostrophe in their names
- [BUGFIX]  Fix creation of profile in Kiosk module for entities that are not allowed

## [5.4.1](https://github.com/medulla-tech/medulla/releases/tag/5.4.1) (2025-10-10)
- [FEATURE] Ability to restart Medulla services from the dashboard
- [FEATURE] Ability to generate agents from the dashboard
- [FEATURE] Ability to log in using a magic link
- [FEATURE] Improve user creation

## [5.4.0](https://github.com/medulla-tech/medulla/releases/tag/5.4.0) (2025-10-02)
- [FEATURE] Improve generation of update database product tables
- [FEATURE] Management of entities and users from within Medulla management console
- [FEATURE] Management of OIDC parameters from within Medulla management console
- [FEATURE] Generation of tagged agents to auto-assign machines to entities

## [5.3.0](https://github.com/medulla-tech/medulla/releases/tag/5.3.0) (2025-07-31)
- [FEATURE] Optimisation of SQL queries regarding imaging server status
- [FEATURE] Allow automatic whitelisting of Windows updates based on severity and classification
- [FEATURE] Improve management of major OS updates
- [FEATURE] Uninstallation convergences allows user to make sure a package is not installed
- [FEATURE] Improve user experience on various modules
- [FEATURE] Imaging profiles allow user to dissociate post-imaging scripts from master images
- [FEATURE] New user documentation (https://docs.medulla-tech.io)
- [BUGFIX]  Fix duplicates when adding a master to imaging boot menu
- [BUGFIX]  Fix traceback in imaging when resetting menus
- [BUGFIX]  Fix Windows updates for product families that are not displayed
- [BUGFIX]  Fix updating Medulla from the dashboard

## [5.2.1](https://github.com/medulla-tech/medulla/releases/tag/5.2.1) (unreleased)
- [FEATURE] Add new sections in Audit page for the convergences
- [FEATURE] Add the possibility to use profiles to imaging
- [FEATURE] Add Convergence sections in the Audit page
- [BUGFIX]  Add several fixes in the OIDC support
- [BUGFIX]  Fix the pulse2-synch-masters script
- [BUGFIX]  Fix deploying masters by stop using datas from uuid-cache.txt
- [BUGFIX]  Fix deploying masters by using the full path of the pulse2-synch-masters script
- [BUGFIX]  Fix Glpi 9.3 support
- [BUGFIX]  Fix multicast ( broken due to python 3 migration )
- [BUGFIX]  Remove pieces not needed in the imaging, now we use SQL storage for IPXE instead of files

## [5.2.0](https://github.com/medulla-tech/medulla/releases/tag/5.2.0) (unreleased)
- [FEATURE] Use SQL to manage imaging menus.
- [FEATURE] Support for OIDC
- [BUGFIX]  Fix detection of a proxy for downloading updates
- [BUGFIX]  Prevent creation of multiple records for the same information in substituteconf
- [BUGFIX]  Fix Audit view where the hostname was not displayed for Kiosk deployments
- [BUGFIX]  Fix convergence owner when it was enabled on a group shared by someone else
- [BUGFIX]  Fix the counters on patch management to take into consideration the ITSM database
- [BUGFIX]  Fix pagination issues on the update module
- [BUGFIX]  Add constrain on the datepickers
- [BUGFIX]  Change am/pm hour to 0-23 digit on datepicker
- [BUGFIX]  Fix the management of sessions between xml-rpc and php

## [5.1.1](https://github.com/medulla-tech/medulla/releases/tag/5.1.1) (unreleased)
- [FEATURE] Add button on search field in audit group deploy page
- [FEATURE] Support newer Glpi
- [BUGFIX]  Fix a crash when in the dashboard when no ubuntu version is provided
- [BUGFIX]  Update quick action that displays the last 100 lines of logs
- [BUGFIX]  Fix cmd to Restart Medulla Agent service on windows
- [BUGFIX]  Fix a crash when deploying because of a missing json key
- [BUGFIX]  Fix quick action command launch and display
- [BUGFIX]  Several kiosk fixes
- [BUGFIX]  Fix displaying the machine name in the update module

## [5.1.0](https://github.com/medulla-tech/medulla/releases/tag/5.1.0) (unreleased)
- [BUGFIX]  Fix adding files on existing packages
- [BUGFIX]  Fix download of updates when a proxy is defined
- [BUGFIX]  Fix ordering machines, done alphabetically now.
- [BUGFIX]  Fix displaying the audit webpage after starting a deploiement.

[Full Changelog](https://github.com/medulla-tech/medulla/compare/5.0.1...5.1.0)

## [5.0.1](https://github.com/medulla-tech/medulla/releases/tag/5.0.1) (unreleased)
- [FEATURE] Add auto-refresh on the deployment page
- [FEATURE] Make the imaging inventory use xmpp to send inventory.
- [BUGFIX]  Fix Translations
- [BUGFIX]  Fix display of the inventory of a machine when it is offline
- [BUGFIX]  Fix creating group from a boolean
- [BUGFIX]  Remove some visible debugs
- [BUGFIX]  Fix displaying Agent details QA
- [BUGFIX]  Fix logging with a local user
- [BUGFIX]  Fix special character in creation of groups
- [BUGFIX]  Fix programming group deploiements

[Full Changelog](https://github.com/medulla-tech/medulla/compare/5.0.0...5.0.1)


## [5.0.0](https://github.com/medulla-tech/medulla/releases/tag/5.0.0) (2023-12-13)
- [FEATURE] Add windows 11 sysprep support
- [FEATURE] Port Medulla to php 8.2
- [FEATURE] Port Medulla to python 3.11
- [FEATURE] Add new Updates module to handle microsoft updates in Medulla
- [FEATURE] Add link to reset all entity menus
- [BUGFIX]  Fix handling accentuated letters in the script that add packages in the database.
- [BUGFIX]  Fix importing big groups with csv files
- [BUGFIX]  Fix counting of inventory machines in the dashboard
- [BUGFIX]  Fix counting of antivirus in the dashboard
- [BUGFIX]  Fix multicast support
- [BUGFIX]  Fix ipxe support
- [BUGFIX]  Adapt to new Sqlalchemy syntax
- [BUGFIX]  Fix support to glpi 10

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.11...5.0.0)

## [4.6.11](https://github.com/medulla-tech/medulla/releases/tag/4.6.11) (2023-04-14)
- [FEATURE] Packaging feature allows to define return codes different to 0 and 1 for branching to other steps
- [FEATURE] Ability to restart a failed deployment from the interface
- [FEATURE] Improve Admin view when connected user is root
- [FEATURE] Add itsm-ng support
- [FEATURE] Add GLPI 10 support
- [FEATURE] Add iPXE support
- [FEATURE] Add new feature for integrity of packages.
- [FEATURE] Allow to display the name of the used ITSM
- [FEATURE] Add user notification 
- [FEATURE] Use new Medulla branding
- [FEATURE] Add systemctl support in pulse2-setup
- [BUGFIX]  Fix diplay of config files
- [BUGFIX]  Support Optiplex 3050 in iPXE
- [BUGFIX]  Fix display of the Master list page when there is a lot of
computers listed.
- [BUGFIX]  Fix php support up to 7.4 in the imaging page.
- [BUGFIX]  Fix modification of packages and correctness of xmppdeploy.json
- [BUGFIX]  Fix traceback when displaying results of a quick action executed on an uninventoried machine
- [BUGFIX]  Fix searching from relay jid, hostname or uuid in deploy audit log
- [BUGFIX]  Fix the History menu. It was displayed twice.
- [BUGFIX]  Fix deleting a deploiement after it had been processed.
- [BUGFIX]  Fix displaying actions depending of the ACLs
- [BUGFIX]  Fix GLPI 9.3 Compatibility
- [BUGFIX]  Fix multicast menu synchronisation
- [BUGFIX]  Fix pulse2-setup where glpi is on a different port than 3306
- [BUGFIX]  Fix GLPI 9.4 Compatibility
- [BUGFIX]  Fix registration of relay servers
- [BUGFIX]  Fix inventory for machines from a PXE inventory
- [BUGFIX]  Fix displaying missing hostname in audit page
- [BUGFIX]  Fix ordering machines in the computer page
- [BUGFIX]  Fix displaying machines in the GLPI view
- [BUGFIX]  Fix displaying of teams in Audit
- [BUGFIX]  Fix displaying package order when editing a package
- [BUGFIX]  Fix deleting machines not available in glpi
- [BUGFIX]  Fix creation of the reversessh in backuppc
- [BUGFIX]  Fix removing computers not on glpi anymore
- [BUGFIX]  Fix computer default name in sysprep configuration page
- [BUGFIX]  Fix order bug in rules list
- [BUGFIX]  Fix restart of deployment if transfer has already started
- [BUGFIX]  Fix backtraces when editing packages
- [BUGFIX]  Fix php 7.4 support in the imaging section
- [BUGFIX]  Fix selecting the entity in imaging
- [BUGFIX]  Add ids in the webpages (used in playwright functional tests)
- [BUGFIX]  Fix xmlrpc int limits
- [BUGFIX]  Fix WOL support

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.9...4.6.11)

## [4.6.9](https://github.com/medulla-tech/medulla/releases/tag/4.6.9) (2021-09-09)
- [FEATURE] Add Team support in Audit page
- [FEATURE] Add new infos in the fileviewer as config ( server, port, size
popup, etc.)
- [FEATURE] Add link to machines in the Quick Action summary page
- [FEATURE] Add a button to run the researches on computers
- [FEATURE] Remove the "Restart machine agent" Quick action
- [FEATURE] Optimize Comuter view display
- [FEATURE] Optimize admin view display
- [FEATURE] Add online/offline switch to the uninventoried page
- [FEATURE] Add a @@@DEBUG@@@ option in queries to show played SQL Requests
- [FEATURE] Add the possibility to add a limit number to the autoupdate feature.
- [FEATURE] Change the way WOL is handled.
- [BUGFIX]  Fix removing packages from the database. Bug#1323
- [BUGFIX]  Fix deleting old users in ejabberd
- [BUGFIX]  Remove cdn from js files import. Use local files instead
- [BUGFIX]  Several SQL Optimisations
- [BUGFIX]  Fix shown state when starting a deployment
- [BUGFIX]  Fix handling some accounts creation
- [BUGFIX]  Fix display infos on group deployment audit
- [BUGFIX]  Fix creating groups based on ADs
- [BUGFIX]  The abort deployment button was always disabled
- [BUGFIX]  Fix creation of groups based on OU or AD. Bug#1238
- [BUGFIX]  Add carriage return on "Executed command" info in detail view
- [BUGFIX]  Fix detection of online machines with glpi 0.84

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.8...4.6.9)

## [4.6.8](https://github.com/medulla-tech/medulla/releases/tag/4.6.8) (2021-06-08)
- [FEATURE] Disable relay list page from computers menu
- [FEATURE] Add utilities to migrate to new package server
- [FEATURE] Disable new sharing mode by default
- [FEATURE] Update translations
- [FEATURE] Rename "Localisation server" to "Share" and remove the search field
- [FEATURE] Remove "add package" from menu when the user has no writing rights
- [FEATURE] Update the package parser to catch more errors
- [FEATURE] Enhance error messages.
- [FEATURE] Fix several XSS issues.
- [FEATURE] Allow to retrieve the glpi uuid if missing
- [FEATURE] Convergences are now identified by their name + date
- [FEATURE] Do not display old view when creating the packages.
- [FEATURE] Allow to filter searches based on the relay jid
- [BUGFIX]  Fix backtrace during deployment
- [BUGFIX]  Fixes listing of packages for deployment
- [BUGFIX]  Add acl for relays actions
- [BUGFIX]  Fix rendering of accentuated letters from glpi to pulse.
- [BUGFIX]  Fix detection of online/offline machine in the Glpi view
- [BUGFIX]  Add back addMachinesToCommand function ( fixing restarting
convergences)
- [BUGFIX]  Do not allow ; in computers descriptions
- [BUGFIX]  Fix the int limitation problem for quotas in sharing
- [BUGFIX]  Change the size of the packages size column
- [BUGFIX]  Fix use of older SQLAlchey
- [BUGFIX]  Fix registry when there no uuidsetup defined
- [BUGFIX]  Change glpi_description sql field to text
- [BUGFIX]  Fix display of active/available convergences
- [BUGFIX]  Fix permissions for viewing ars based on clusters
- [BUGFIX]  Grant Rights for Admin on the ARS Cluster.
- [BUGFIX]  Fix use of <br> in the description field (glpi )
- [BUGFIX]  Escape simple quotes in descriptions ( glpi )
- [BUGFIX]  Fix listing enabled plugins.
- [BUGFIX]  Fix crash when metagenerator is missing
- [BUGFIX]  Set metagenerator key to expert if missing
- [BUGFIX]  Fix registration when there is no entity in xmppmaster database yet
- [BUGFIX]  Fixes traceback when editing
- [BUGFIX]  Convert id from string to int for glpi 084 and 92
- [BUGFIX]  Use OCS inventory date if exists
- [BUGFIX]  All entities return all entities uuids allowed to the user
- [BUGFIX]  Fix search in entities
- [BUGFIX]  Add the entity to the search.
- [BUGFIX]  Fix a problem when the hostname changed.
- [BUGFIX]  Pkgs display on "os" definition in config.json
- [BUGFIX]  Fix the edition status if the metagenerator is set to manual
- [BUGFIX]  Remove too many arguments in the formatted filter
- [BUGFIX]  Set to "" the none values on sharings infos
- [BUGFIX]  A undefined variable were used, replaced it by the real name
- [BUGFIX]  Modify assert tests to conditionnal tests in the page generator
- [BUGFIX]  Do not look for installation command if package is larger than 500MB
- [BUGFIX]  Fix backtrace when no machines are associated to a relay
- [BUGFIX]  Fix pagination on packages list admin page
- [BUGFIX]  Enhance glpi 0.84 support
- [BUGFIX]  Remove registries from machines filters
- [BUGFIX]  Keep the partial count and use the total
- [BUGFIX]  Fixes the pagination for the computers list
- [BUGFIX]  Fix pagination in admin relay page
- [BUGFIX]  Fix traceback when a user doesn't have rights on shares for relays list in admin
- [BUGFIX]  Fix missing declaration for an array in glpi 0.84
- [BUGFIX]  Remove old parameters from the filter
- [BUGFIX]  Fix traceback on arraykeys when listing all computers in glpi 0.84
- [BUGFIX]  Fix deployment action when machine is offline
- [BUGFIX]  User can view only the relays allowed in pkgs_rules_local
- [BUGFIX]  Fix wol by correcting a wrong variable name
- [BUGFIX]  Fix size output to be human readable
- [BUGFIX]  Fix package page when there is no packages to display
- [BUGFIX]  Fix checking if new sharing is used, if not used the old style
- [BUGFIX]  Add name to csv when the group is created
- [BUGFIX]  Add missing parameters in pkgs.ini and initialise pkgs_rules_algo table
- [BUGFIX]  Fix pagination in GLPI View
- [BUGFIX]  Fix registering ARS
- [BUGFIX]  Fix displaying the relay list
- [BUGFIX]  Fix and add ACLs
- [BUGFIX]  Fix migration to new packages layout
- [BUGFIX]  Change hostname in cluster_resources size to 255
- [BUGFIX]  Remove description from csv generation
- [BUGFIX]  Modify concatenation of " bracket from csv generation
- [BUGFIX]  Fix display of dates in the audit page

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.7...4.6.8)


## [4.6.7](https://github.com/medulla-tech/medulla/releases/tag/4.6.7) (2021-03-29)
- [FEATURE] Order relay list
- [FEATURE] Add ACL on the package synchronisation
- [FEATURE] Add ACL on the GLPI view
- [FEATURE] Add ACL on package and relay view
- [FEATURE] Add Quotas for relay servers
- [FEATURE] New computer view
- [BUGFIX] Fix deploying packages with the same name
- [BUGFIX] Fix creating a package using the Zip action
- [BUGFIX] Hide convergence if not available.
- [BUGFIX] Export CSV

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.6...4.6.7)

## [4.6.6](https://github.com/medulla-tech/medulla/releases/tag/4.6.6) (2021-01-20)
- [FEATURE] Add admin page
- [FEATURE] Allow to set up the send of WOL
- [FEATURE] Allow to disable the use of UUID for glpi association
- [FEATURE] Show non sync relays at the top of the list ( package view )
- [FEATURE] Create packages in pushrsync by default and fallback in pulldirect if pushrsync fails.
- [FEATURE] Ajout du camembert intermédiaire une fois le déploiement terminé
- [FEATURE] Add  the percent in the Audit  view
- [BUGFIX] Fix packages sync when a relay is down
- [BUGFIX] Fix the percentages in the deploy view
- [BUGFIX] Fix the action "set_config" in packaging
- [BUGFIX] Fix the dates when planning a deployment
- [BUGFIX] Fix detection of the package server when using pulldirect

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.5...4.6.6)

## [4.6.5](https://github.com/medulla-tech/medulla/releases/tag/4.6.5) (2020-12-01)
- [FEATURE] Add Glpi 9.5 Support
- [FEATURE] Support php-fpm by default
- [FEATURE] Save Online/Offline states and their duration, to be used later
- [FEATURE] Add grafana support for monitoring
- [FEATURE] Allow to create a reversessh tunel from a QuickAction
- [FEATURE] Rename log files to have the name of  the service (machine/relay)
- [FEATURE] Use glpi's UUID uniq value add machines in the machines sql table
- [FEATURE] Set pulldirect deployement mode by default
- [FEATURE] Add support for python-ldap from version 3.2.0
- [FEATURE] Add Notify recording ARS
- [FEATURE] Allow to disable the UUID feature ( if using an old GLPI for ex.)
- [BUGFIX] Update Translations
- [BUGFIX] The Relay List now show the good JID
- [BUGFIX] The Computer page now list the machines by name
- [BUGFIX] Add the firmware column to the filter
- [BUGFIX] Fix reversessh support
- [BUGFIX] Fix support with MariaDB 10.3
- [BUGFIX] Fix Audit page when the machines has several mac addresses
- [BUGFIX] Fix registering the machines if the interface changes
- [BUGFIX] Fix wording regarding source of IP address in audit view

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.4...4.6.5)

## [4.6.4](https://github.com/medulla-tech/medulla/releases/tag/4.6.4) (2020-07-27)
- [FEATURE] Add quick actions to relays management
- [FEATURE] Guacamole operations are now linked to XMPP inventory instead of GLPI
- [FEATURE] Agents now use ifconfig.co webservice to find location
- [FEATURE] User can now decide if he wants to force an inventory in packages
- [FEATURE] File transfer now uses a specific user instead of root
- [FEATURE] Agents autoupdate by relay servers is now the default method
- [FEATURE] Add console, guacamole and config file edition for uninventoried machines
- [BUGFIX]  Fix sharing of groups. All groups are now shared with root user
- [BUGFIX]  Fix reconfiguration of machines
- [BUGFIX]  Fix missing hostname in Audit page
- [BUGFIX]  Eliminate mac addresses that are blacklisted as soon as they are received
- [BUGFIX]  Fix PKI for generating certificates for multiple addresses
- [BUGFIX]  Fix display of mac address for deployment
- [BUGFIX]  Clean old jids from machines table
- [BUGFIX]  Fix update of deployment statuses
- [BUGFIX]  Fix order in which machines are displayed

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.3...4.6.4)

## [4.6.3](https://github.com/medulla-tech/medulla/releases/tag/4.6.3) (2020-05-19)
- [FEATURE] Manage relay servers from Pulse console
- [FEATURE] Ask reconfiguration of all machines connected to a relay
- [FEATURE] List uninventoried machines
- [BUGFIX]  Fix count of machines in audit view based on deployment statuses

[Full Changelog](https://github.com/medulla-tech/medulla/compare/4.6.1...4.6.3)

Pulse 2 4.6.1
=============
- [FEATURE] Improve translations
- [FEATURE] Allow to use remote database for msc
- [FEATURE] Allow to black list MAC Adresses in jid ( when several machines
			has the same mac adress in a network )
- [FEATURE] Speed up a lot the Computer page
- [FEATURE] Add WOL 1, 2, 3 for the graph
- [FEATURE] Attribute ARS based on net mask addres
- [FEATURE] Allow to use an externalised msc database
- [BUGFIX]  Fix Wol for deployements in Audit web page
- [BUGFIX]  Various fixes about inventories
- [BUGFIX]  Fix the restarting a deployment after a WOL
- [BUGFIX]  Fix support to glpi when the database is not caller glpi
- [BUGFIX]  Fix systemd service files to automatically restart the services
- [BUGFIX]  Fix status of convergences ( available, used, etc.)

Pulse 2 4.6.0
=============
- [FEATURE] Improve translations
- [FEATURE] Add glpi 9.4 support
- [FEATURE] Add Syncthing support for packages deployment
- [FEATURE] Machine table is now static
- [FEATURE] Add the pulldirect tranfer method into the page edit package
- [FEATURE] Create packages in push mode. If the package cannot be deployed in push mode, pull mode will be used
- [FEATURE] Reboot is managed by xmpp and no longer package server
- [FEATURE] Add Substitute agents
- [BUGFIX]  Fix multicast synchronisation menu
- [BUGFIX]  Accelerates the display of the group audit view
- [BUGFIX]  Fix generating pxelinux menus for restoring.
- [BUGFIX]  The machine list was not visible in the static group creation page
- [BUGFIX]  Modify the sql request for topology functions
- [BUGFIX]  Modify the default value when a new machine is added to xmppmaster.machines

Pulse 2 4.5.2
=============
- [FEATURE] Allow install of plugin if a specific version of client is met
- [FEATURE] Switch from RaphaelJS to d3.js
- [FEATURE] Function to record execution time of plugins
- [BUGFIX]  Fix creating groups when the database is not called glpi
- [BUGFIX]  Fix dashboard counters
- [BUGFIX]  Fix the release of resources after a deployment
- [BUGFIX]  Fix generation of random deployment session names
- [BUGFIX]  Fix the release of resources in case of lost connections
- [BUGFIX]  Fix reconnection of master agent to xmpp server


Pulse 2 4.5.1
=============
- [FEATURE] Expert file download allows download of several files and folders
- [FEATURE] File download shows a tree view of the remote filesystem
- [FEATURE] Update the OS widget for the dashboard
- [FEATURE] Architecture and OS version can be used for creating dynamic groups
- [BUGFIX]  Make the remote control icons clickable when there is more than one access method
- [BUGFIX]  Fix user used for guacamole ssh connections
- [BUGFIX]  Fix user used for backup commands
- [BUGFIX]  Improve the function that detects the presence of clients
- [BUGFIX]  In expert mode the default action if a package step returns an error is to go to END_ERROR
- [BUGFIX]  Check package format before doing a deployment
- [BUGFIX]  Do not log machines info and plugins by default
- [BUGFIX]  Fix abort of deployments on groups in cases where the machines are offline
- [BUGFIX]  Fix copy of files when machine is connected to a relay server that is not on main Pulse server


Pulse 2 4.5
===========
- [FEATURE] Add glpi 9.2 support
- [FEATURE] Add glpi 9.3 support
- [FEATURE] Add Agent "Auto Update" feature
- [FEATURE] Show the presence status in backup machine list
- [FEATURE] New imaging post-install scripts available
- [FEATURE] Allow creation of dyngroups from registry keys
- [FEATURE] Allow import of static groups from csv containing registry keys
- [FEATURE] New quick action commands available
- [FEATURE] Assign a machine to a relay based on the machine's network address
- [FEATURE] New icon for SSH connection on Windows machines
- [FEATURE] Allow a deployment to be spooled in priority
- [FEATURE] Allow creation of dyngroups from Active Directory OU
- [FEATURE] Filter computer list view on registry contents
- [BUGFIX]  Fix encoding error in "Execute Script" action when creating package
- [BUGFIX]  Improve the creation of the groups for machineOnline widget
- [BUGFIX]  Allow to modify imaging groups for machines with more than one
            ethernet card
- [BUGFIX]  Do not modify py files directly
- [BUGFIX]  The action navbar is uniformized
- [BUGFIX]  Set the default package type as empty package
- [BUGFIX]  Fix date management in audit and history views
- [BUGFIX]  Improve audit view
- [BUGFIX]  Allow for jid up to 255 characters
- [BUGFIX]  Fix detection of MAC address for PXE registration
- [BUGFIX]  Fix several occurences of the same machine on relayservers in
            cluster mode
- [BUGFIX]  Clean deployment caches and used resources after a deployment
- [BUGFIX]  Logs and bundles no longer available from machine deployment view
- [BUGFIX]  Removing files from package does not generate an error
- [BUGFIX]  Fix detection of uploaded file types in package creation
- [BUGFIX]  Fix abort of deployments in cases where jidmachine and jidrelay are fake


Pulse 2 4.4.1
===========
- [BUGFIX]Fix displaying OSes in 'Operating system' dashboard widget
- [BUGFIX] Fix the display of the command executed
- [BUGFIX] Remove sql file to handle UEFI ( we need new davos first )
- [BUGFIX] Improve the creation of the groups for machineOnline widget
- [BUGFIX] Allow to modify imaging groups for machines with more than one
           ethernet card
- [BUGFIX] Fix editing configuration files in client machine
- [BUGFIX] Root can delete imaging groups shared with him
- [BUGFIX] The action navbar is uniformized
- [BUGFIX] In backuppc the computer icon is colored when the machine is
           on line
- [BUGFIX] use one database access instead of two
- [BUGFIX] Add the config button in the xmpp console page

Pulse 2 4.4
===========
- [FEATURE] Improve registry settings description in config files
- [FEATURE] Improve execution of commands by using synchronous operations
- [FEATURE] First version of Pulse Kiosk
- [FEATURE] Addition of an inventory step after deployment
- [FEATURE] Ability to run a custom quick action on a group
- [FEATURE] Creation of sysprep response files for UEFI systems
- [BUGFIX] Fix detection of MSI command for 64bit Windows
- [BUGFIX] Fix Ajax call for run backup command
- [BUGFIX] Fix researching of machine and user OUs
- [BUGFIX] Review dependencies in Pulse packaging
- [BUGFIX] Fix calling a plugin from a quick action
- [BUGFIX] Fix encoding for deployment stuck in START DEPLOY step
- [BUGFIX] Fix downloadfile plugin for launch as a quickaction on groups
- [BUGFIX] Fix the saving of registry keys after the inventory
- [BUGFIX] Fix the display of machines when registry keys inventories are present

Pulse 2 4.3
=============
- [FEATURE] Enable browsing and download of files from client machines
- [FEATURE] Add new logs for dump in support script
- [FEATURE] Allow registration of UEFI machines via PXE
- [FEATURE] Show macOS in operating systems distribution on dashboard
- [BUGFIX] Fix top action menu in action views
- [BUGFIX] Use system user for new machines where no user has logged in yet
- [BUGFIX] Fix the problem of editing package when we switch from standard to expert mode
- [BUGFIX] Fix restoring of files to macOS clients

Pulse 2 4.2
=============
- [FEATURE] Quick action to install ARS SSH key to Machines
- [FEATURE] Allow deployment of python scripts
- [FEATURE] Do not restart agent after an inventory
- [FEATURE] Auto-update scheduler plugins
- [FEATURE] Limit bandwidth usage during a deployment
- [FEATURE] Differentiate packages created in expert mode
- [FEATURE] Remove unused launcher service
- [FEATURE] Add the ability to display registry keys in the computers view
- [FEATURE] Download remote files from machines using XMPP
- [FEATURE] Allow to call a plugin from a quick action
- [BUGFIX] Standardize the size of dependencies boxes in package modification
- [BUGFIX] Fix the bug that deletes all packages if an empty package is created
- [BUGFIX] Fix download of files containing spaces
- [BUGFIX] Remove update module
- [BUGFIX] Fix user detection if no user logged in
- [BUGFIX] Update translations

Pulse 2 4.1
=============
- [FEATURE] New interface for building complex packages and workflows with dependencies
- [FEATURE] New history view that captures all operations
- [FEATURE] Pulse update module widget is now a standalone widget
- [FEATURE] Create and run custom quick actions
- [FEATURE] Ability to delay the execution step of deployments based on time, percentage or number of machines having received the package
- [FEATURE] Add support for UEFI in the DHCP server configuration for Pulse imaging
- [BUGFIX] Fix saving of sysprep answer files
- [BUGFIX] Fix the abortion of deployments
- [BUGFIX] Fix authentication to GLPI for user provisioning
- [BUGFIX] Fix multicast imaging in Debian Stretch

Pulse 2 4.0
=============
 * [FEATURE] Use xmpp to deliver messages, orders, etc
 * [FEATURE] Add glpi 9.1 Support
 * [FEATURE] Add a dashboard widget to follow backups
 * [FEATURE] Add a dashboard widget to know the number of machines (total,
 online, offline)
 * [BUGFIX]  Fix Antivirus detection with latest glpi
 * [BUGFIX]  Fix user creation with latest glpi
 * [BUGFIX]  Fix port to php7

Pulse 2 3.6.0
=============
 * [FEATURE] Replacement of historic Pulse PXE by PXELINUX
 * [FEATURE] Ability to define Clonezilla options for imaging
 * [FEATURE] Ability to define NFS mounts for imaging client
 * [BUGFIX]  Fix database schemas and format
 * [BUGFIX]  Improve detection of disks and partitions
 * [BUGFIX]  Fix options for PXE registration
 * [FEATURE] Add Mageia support in the dashboard
 * [BUGFIX]  Fix the loading of json files containing non printable characters in PXE registration
 * [BUGFIX]  Fix listing packages in Launch Bundle view of computer's secure control
 * [BUGFIX]  Fix for deployment on targets where IP address has changed
 * [FEATURE] Restore backup to other hosts
 * [BUGFIX]  Make use of preferred_network for the choice of launcher
 * [FEATURE] Upgrade inventory agent to 2.3.18
 * [BUGFIX]  Enable registration of assembled machines
 * [BUGFIX]  Fix detection of netmask
 * [FEATURE] Add sysprep answer file generator
 * [BUGFIX]  Clean the sysprep code
 * [BUGFIX]  Modify sysprep interface and form organization.
 * [BUGFIX]  Show notification when a sysprep answer file is created
 * [BUGFIX]  Add colors to sysprep xml file when displayed
 * [BUGFIX]  Fix support for new SqlAlchemy
 * [BUGFIX]  Fix download webpage ( issue #86 )
 * [BUGFIX]  Fix Backup restore failed ( issue #88 )
 * [BUGFIX]  Fix Group panel for non standart windows versions ( issue #32 )
 * [FEATURE] Add windows 8 and 10 backup templates ( issue #24 )
 * [FEATURE] Add Glpi 9.1.x support ( issue #26, #84, #90 )
 * [FEATURE] Migrate to GLPI API Rest ( issue #89 )
 * [BUGFIX]  Fix sysprep support ( issue #27, #30, #31, #70 )
 * [BUGFIX]  Fix registering computers if the hostname contains spaces
             ( issue #2 )
 * [FEATURE] Display available licences on the inventory ( issue #18 )
 * [BUGFIX]  Remove the need of java in mmc ( issue #38 )
 * [FEATURE] List computers with image or custom menu ( issue #40 )
 * [BUGFIX]  Fix Siveo logo on main page ( issue #67 )
 * [BUGFIX]  Fix selecting the good entity in backup and imaging module ( issue #33 )
 * [BUGFIX]  Fix mmc webpage layout ( issue #5 )
 * [BUGFIX]  Associate inventory to a package ( issue #92 )

Pulse 2 3.3.0
=============
 * [BUGFIX]  Allow to disable backuppc
 * [BUGFIX]  Enhance systemd support in pulse2-setup
 * [FEATURE] Add Multicast support
 * [BUGFIX]  Fix support for new sqlalchemy
 * [BUGFIX]  Fix support for new python-twisted
 * [BUGFIX]  Fix pulse2-cm initscipt for debian
 * [BUGFIX]  Removal of pulse2-cm
 * [FEATURE] Management of multiple entities in Imaging
 * [BUGFIX]  Fix restore of a specific version of a file
 * [FEATURE] Replacement of historic Pulse PXE by PXELINUX




mmc-core 4.6.2
==============
- [BUGFIX] Fix the value for the timed out machines in the audit page

mmc-core 4.6.1
==============
- [FEATURE] Add a toggle button for each panel. For each panel the user's choice is persistant
- [FEATURE] Add info of syncthing share
- [BUGFIX]  Improve translations
- [BUGFIX]  Update topology for d3 V5
- [BUGFIX]  Add refresh button for all the audit page
- [BUGFIX]  Fix the start deployment date
- [BUGFIX]  Add the refresh object for some page
- [BUGFIX]  Fix the start deployment date
- [BUGFIX]  Add some behaviours to the expert file manager

mmc-core 4.6.0
==============
- [BUGFIX]  Transform file and dir one-line list to real list in the bucket
- [BUGFIX]  Add spacing after filter input
- [BUGFIX]  Modify the cursor when it is hover some action icons
- [BUGFIX]  Translate the hide / show message when we clic on it
- [BUGFIX]  Fix the status in audit general pag
- [BUGFIX]  Fix the state for deployments in groups in audit page
- [BUGFIX]  Fix syncthing message displayed into audit
- [BUGFIX]  Fix the start deployment date
- [BUGFIX]  Add the refresh object for some page
- [BUGFIX]  Fix the start deployment date
- [BUGFIX]  Add some behaviours to the expert file manager
- [BUGFIX]  Transform file and dir one-line list to real list in the bucket

mmc-core 4.5.2
==============
- [FEATURE] Switch from RaphaelJS to d3.js
- [BUGFIX]  Fix dashboard counters
- [BUGFIX]  Fix the release of resources in case of lost connections

mmc-core 4.5.1
==============
- [FEATURE] New history page for file transfers
- [FEATURE] Expert file download allows download of several files and folders
- [FEATURE] File download shows a tree view of the remote filesystem
- [FEATURE] Enable changing of audit refresh time
- [BUGFIX]  Improve quick actions for Linux clients
- [BUGFIX]  Improve the detection of the presence of clients in groups
- [BUGFIX]  Quick actions moved to standard mode
- [BUGFIX]  Improve refresh of the dashboard and audit view
- [BUGFIX]  Fix abort of deployments on groups

mmc-core 4.5
--------------
- [FEATURE] The Quick Actions can be shared with others users
- [FEATURE] A "copy to clipboard" button is added to error popups
- [BUGFIX]  Fix the wrong count of machines in MachineOnline widget
- [BUGFIX]  Remove PluginPanel dashboard plugin
- [BUGFIX]  Fix Action list content
- [BUGFIX]  Fix VNC permissions change via quick action
- [BUGFIX]  Add cmd icon ( used for windows )
- [BUGFIX]  Fix editing Quick action
- [BUGFIX]  Fix command for quick action
- [BUGFIX]  Fix quick action for groups
- [BUGFIX]  Add root to share user list
- [BUGFIX]  Fix sharing Quick Actions
- [BUGFIX]  Fix Audit page pagination
- [BUGFIX]  Fix refresh rate in the audit page
- [BUGFIX]  Add ubuntu detection to quick action

mmc-core 4.4.1
--------------
- [BUGFIX] Fix wake on lan problem
- [BUGFIX] Modify the configuration icon computers action

mmc-core 4.4
--------------
- [FEATURE] Ability to use quick actions installed by the sql schemas for all users
- [FEATURE] Ability to run a custom quick action on a group
- [BUGFIX] Fix remote console shell for long commands


mmc-core 4.3
--------------

 * [FEATURE] Allow edition of clients config files from Pulse
 * [FEATURE] Filter computers list on presence status
 * [BUGFIX] Update translations


mmc-core 4.2
--------------

- [FEATURE] Quick action that installs the public key of the relay server to the machines
- [FEATURE] Allow a tooltip message on empty actions
- [FEATURE] Automatically redirect user to /mmc
- [FEATURE] Allow to call a plugin from a quick action
- [FEATURE] Add a file browser page for file-transfer folder
- [FEATURE] Download remote files from machines using XMPP
- [FEATURE] Add presence info on machines icons
- [BUGFIX] Fix the service module to work with newer systemd
- [BUGFIX] Fix the color of quick action alerts
- [BUGFIX] Fix quote characters in quick actions
- [BUGFIX] Fix alignment of action icons
- [BUGFIX] Update translations

mmc-core 4.1
--------------

- [FEATURE] New history view that captures all operations
- [FEATURE] Pulse update module widget is now a standalone widget
- [FEATURE] Create and run custom quick actions
- [BUGFIX]  Fix authentication to GLPI for user provisioning
- [BUGFIX]  Fix service module with new systemd

mmc-core 3.1.1
--------------

 * Feature #2170: Create defaultUserGroup when starting
 * Bug #2115: Mixup between client.async and client.sync cookies
 * Bug #2155: Change user password for root doesn't work
 * Bug #2156: Removed deprecated functions
 * Bug #2186: Users with "no password expiration" policy still have an expiration
              date on the samba side
 * Bug #2256: Allow to change SAMBA password when pwdReset is set
 * Bug #2257: Port to jQuery

mmc-core 3.1.0
--------------

 * New dashboard plugin
 * New services plugin (systemd integration)
 * Bug #1912: Fix MMC login page on IE9
 * Bug #1915: Fix UID between users and computers accounts

mmc-core 3.0.5
--------------

 * Bug #1708: Fix unhandled exception when user atttempt to create a already
   existing user home directory
 * Bug #1775: UID/GID should not be shown when adding a user
 * Bug #1777: Slashes in error messages on the login page

mmc-core 3.0.4
--------------

 * Feature #1687: Allow users to reset their password with a token based
   authentication
 * Password policies enhancements: Password complexity hints, show on the user
   edit page if the password if expired or if the user is in grace login mode
 * New MMC contrib scripts : mmc-check-expired-passwords / usertoken-example in
   /usr/share/doc/python-mmc-base/contrib/scripts
 * Audit : audit logs can be sent to syslog servers
 * Bug #1558: Broken user / group lists under IE7
 * Bug #1691: Bad mmc-agent PID file handling
 * Bug #1706: Previous - Next listing behavior
 * Bug #1739: pulse2-package-server-register-imaging on python 2.7
 * Feature #1594: Use localized languages labels on MMC login page
 * Feature #1671: Man pages for mmc-agent, mmc-helper and mmc-password-helper

 See http://projects.mandriva.org/versions/166

mmc-core 3.0.3.2
----------------

 * Bugfix release of 3.0.3.1
 * Details at http://mds.mandriva.org/milestone/MMC-CORE%203.0.3.2

mmc-core 3.0.3.1
----------------

 * Bugfix release of 3.0.3
 * Phone numbers can contain the '+' char
 * IE6 fixes
 * Details at http://mds.mandriva.org/milestone/MMC-CORE%203.0.3.1

mmc-core 3.0.3
--------------

 * Added preferedLanguage field in the user edit page
 * Option to use an existing home directory for a new user
 * Filled informations in the user edit page are not lost in case of error
 * Added a disable button to disable all modules of a user
 * More details at http://mds.mandriva.org/milestone/MMC-CORE%203.0.3

mmc-core 3.0.2.1
----------------

 * Bugfix release : http://mds.mandriva.org/milestone/MMC-CORE%203.0.2.1
   * Fix regexp on mail field in the user edit page
   * Fix update on empty multiple input fields
   * Fix agent return code in case of error in plugin activation (#409)

mmc-core 3.0.2
--------------

 * Merge MMC Agent and MMC web interface versions (web interface ChangeLog
   in web/Changelog
 * Migrate to autotools
 * More details at http://mds.mandriva.org/milestone/MMC-CORE%203.0.2

mmc-core 3.0.1 (MMC agent)
--------------------------

 * MMC agent session timeout is now configurable.
 * Add a subscription and support information system
 * New page that displays subscription and support informations
 * List widget improvement: configurable pagination, tooltips on column name
 * Bug fixes
 * More details at http://mds.mandriva.org/milestone/MMC-CORE%203.0.1

mmc-core 3.0.0 (MMC agent)
--------------------------

 * Audit framework
   * New mmc-helper command to manage the audit database
 * LDAP TLS support
 * New Password Policy module
   * New mmc-password-helper to check and generate password
   * New openldap-check-password password policy module for OpenLDAP
 * French translation update (Mandriva)
 * German translation update (Mario Fetka)
 * Spanish translation update (Francisco Garcia)
 * Brazilian Portuguese translation update (Sergio Rafael Lemke)

mmc-agent 2.3.2
---------------

 * Multi-threading support
 * TLS support with certificate check for incoming XML-RPC connections
 * base plugin:
   * Add change password hook for changeUserPasswd in base plugin
     (Original patch from Jan Gehring)
   * Default used LDAP user password scheme is now SSHA instead of CRYPT
 * network plugin:
   * Add support for NS and MX records edition
   * Fix issues with 64 bits platform when computing the next free IP address
     of a zone
 * samba plugin
   * SAMBA configuration parser is more robust
 * provisioning:
   * Add profile to group mapping capability when provisioning a user from a
     external LDAP
   * Network timeout for external LDAP connection
 * New ACL edit page

mmc-agent 2.3.1
---------------

 * minor bug fix release
 * hook scripts for SAMBA remote share and printer management
 * BASE64 obfuscated password support in /etc/mmc/mmc.ini
 * Fix bad path in expertMode cookie
 * New Russian translation by Vitaly Kolomeytsev
 * Brazilian Portuguese translation update from Wanderlei Antonio Cavassin
 * Spanish translation update from Juan Asensio Sánchez

mmc-agent 2.3.0
---------------

 * New "Computers" sub-module for computer management
 * Save interface mode (standard or expert) between two MMC sessions
 * User photo auto-resize if too large
 * Support page with tabs in the widget framework
 * Lots of code cleanup and bug fixes
 * external authentication and provisioning support
 * server-side session security context support
 * base plugin:
   * issue an error when the backup directory for user's home doesn't exist
   * Fix loginShell attribute problem when getting users list (Manuel Zach)
 * SAMBA plugin:
   * the path of a new SAMBA share can now be specified instead of using a
     default location
   * the OU that stores the SAMBA computer accounts is now read from samba.ini
 * mail plugin:
   * the mail LDAP schema features the mailhost attributes
   * the attribute mailhost is now managed

mmc-agent 2.2.0
---------------

 * server-side session management with the MMC web interface
 * a user must now be authenticated before any XML-RPC calls
 * put back HTTP basic authentication between the agent and the interface
 * SAMBA plugin:
   * issue a warning if NSCD is detected
 * network plugin:
   * Make "get next free IP address feature" works with Python 2.4
   * DHCP: authoritative flag management for subnet
   * DNS: allow to specify a DNS zone reader for BIND zone configuration files (initial patch by Josef Boleininger)
   * DNS: chrooted bind support
 * a title can now be set to the MMC login page
 * browser language auto-detection on the login page
 * ported a lot of old code to the new MMC framework

mmc-agent 2.1.0
---------------

 * LMC to MMC rename
 * new Mandriva graphical theme
 * configuration files have been relocated
 * Some new HTML widgets and widget framework improvements
 * Norwegian translation from Atle Johansen
 * Code cleanup and bug fixes

lmc-agent 2.0.0
---------------

 * network plugin
   * new module for DNS and DHCP management
 * base plugin
   * skelDir option bug fix
 * ox plugin
   * more provide the Open-Xchange plugin

lmc-agent 1.1.4
---------------

 * user photo (JPEG format) can now be uploaded
 * user list now display telephone number and mail address
 * user "cn", "displayName" and "title" LDAP attribute can now be edited
 * update scriptaculous AJAX framework to version 1.7.0
 * destroy user session when login out
 * code cleanup and bug fixes
 * Passwords can now contains special characters
 * UI cleanups
 * Spanish translation from Alejandro Escobar

lmc-agent 1.1.3
---------------

 * XML-RPC agent:
   * allow transfert of binary values in XML-RPC stream
 * some bug fixes

lmc-agent 1.1.2
---------------

 * user login shell attributes can now be edited
 * a group entry can now be edited
 * code cleanup and XHTML/CSS fixes
 * base plugin:
   * simple bug fixes for Fedora Directory Server (FDS) support
   * do cn="givenName sn" when adding a user
 * SAMBA plugin
   * more checks when SAMBA plugin starts
   * move machines management stuff from base plugin
 * mail plugin:
   * mail alias management for group
   * plugin can now be disabled by configuration
 * proxy plugin:
   * plugin can now be disabled by configuration
 * ox plugin:
   * plugin can now be disabled by configuration

lmc-agent 1.1.1
---------------

 * base plugin:
   * the POSIX primary group of a user can be changed
   * starting uid and gid numbers can now be configured
   * extra modifiers are now available when setting default attributes for new
     users
 * SAMBA plugin:
   * SAMBA user primary group can be changed
   * extra LDAP checks when activating module
   * joined machines on the domain are now added to the 'Domain Computers'
     group
 * mail plugin: virtual mail domain support
 * when searching a user, the scope is extended to uid, firstname and lastname
  (instead of uid only)
 * primary/secondary groups management
 * the group membership page now works with IE6
 * user mail address can be configured directly from the user edit page
 * assorted bug fixes

lmc-agent 1.1.0
---------------

 * New mail plugin to manage user email delivery with postfix
 * SAMBA plugin: shares connections and session status are now available
 * base plugin: All log files can now be accessed
 * New home page to improve navigation
 * The old home page has been moved to a new "Status" page
 * New Log page to show LDAP operations log
 * The number of users in a group is now displayed in the group list
 * Telephone number field is now available when editing a user
 * Internal module management improvement

lmc-agent 1.0.1
---------------

 * Fix a popup generator bug.

lmc-agent 1.0.0
---------------

 * Initial release.

