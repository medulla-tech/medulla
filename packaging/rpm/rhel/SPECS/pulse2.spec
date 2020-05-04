# RHEL6 compat hacks
%if %_vendor == "redhat"
%define configure2_5x %configure
%define make %{__make}
%define makeinstall_std %{__make} DESTDIR=%{?buildroot:%{buildroot}} install
%define mkrel(c:) %{-c: 0.%{-c*}.}%{1}%{?subrel:.%subrel}%{?distsuffix:%distsuffix}%{?!distsuffix:.el6}
%define py_puresitedir %(python -c 'import distutils.sysconfig; print distutils.sysconfig.get_python_lib()' 2>/dev/null || echo PYTHON-LIBDIR-NOT-FOUND)
%endif
# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define __requires_exclude ^(pear\\(graph.*|pear\\(includes.*|pear\\(modules.*)$

%if %_vendor == "Mageia"
%define webappsdir /httpd/conf/webapps.d
%define with_report 1
%else
%define webappsdir /httpd/conf.d
%define _webappconfdir %_sysconfdir/httpd/conf.d
%define with_report 1
%endif


%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

%define use_git                1
%define git                    SHA
%define real_version           4.6.1
%define mmc_version            4.6.1

Summary:	Management Console
Name:		pulse2
Version:	%real_version
%if ! %use_git
Release:        1%{?dist}
%else
Release:        0.%git.1%{?dist}
%endif
License:	GPL
Group:		System/Servers
URL:		https://github.com/pulse-project/pulse
Source0:        %{name}_%{real_version}.orig.tar.gz
#TODO: Adapt for Mageia
Source1:        pulse2-dlp-server.init
Source2:        pulse2-inventory-server.service
Source3:        pulse2-imaging-server.service
Source4:        pulse2-register-pxe.service
Source5:        output.py
Source6:        get_file.php

BuildRequires:	python-devel
BuildRequires:	gettext
BuildRequires:	gettext-devel
BuildRequires:  libxslt
BuildRequires:  wget
BuildRequires:  docbook-style-xsl

Requires:       mmc-agent
Requires:       mmc-web-base
Requires:       python-mmc-base
Requires:       mmc-web-dyngroup
Requires:       python-mmc-dyngroup
Requires:       mmc-web-imaging
Requires:       python-mmc-imaging
Requires:       mmc-web-msc
Requires:       python-mmc-msc
Requires:       mmc-web-pkgs
Requires:       python-mmc-pkgs
Requires:       mmc-web-pulse2
Requires:       python-mmc-pulse2
Requires:       mmc-web-kiosk
Requires:       python-mmc-kiosk
Requires:       pulse2-common
Requires:       pulse2-davos-client
Requires:       pulse2-inventory-server
Requires:       pulse2-package-server
Requires:       pulse2-scheduler
Requires:       python-pulse2-common-database-dyngroup
Requires:       pulse-mmc-web-computers-inventory-backend
Requires:       pulse-python-mmc-computers-inventory-backend
Requires:       pulse2-homepage

%description
Management Console agent & web interface with
base and password policies modules.

%files

#--------------------------------------------------------------------

%package -n python-mmc-dyngroup
Summary:    Dynamic computer group plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-pulse2-common-database-dyngroup = %version-%release

%description -n python-mmc-dyngroup
This package contains the dynamic computer group plugin for the MMC agent. It
stores into a database static and dynamic group of computers to ease massive
software deployment.

%files -n python-mmc-dyngroup
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/dyngroup.ini
%python2_sitelib/mmc/plugins/dyngroup

#--------------------------------------------------------------------

%package -n     mmc-web-dyngroup
Summary:        Dynamic computer group plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version

%description -n mmc-web-dyngroup
This package contains the dynamic computer group plugin for the MMC web
interface. It allows one to build static and dynamic group of computers to
ease massive software deployment.

%files -n mmc-web-dyngroup
%{_datadir}/mmc/modules/dyngroup

#--------------------------------------------------------------------

%package -n python-mmc-backuppc
Summary:    Backuppc plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   p7zip
Requires:   python-pyquery

%description -n python-mmc-backuppc
This package contains the backuppc plugin for the MMC agent.

%files -n python-mmc-backuppc
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/backuppc.ini
%python2_sitelib/mmc/plugins/backuppc
%python2_sitelib/pulse2/database/backuppc
%_sbindir/pulse2-backup-servers
%_bindir/pulse2-backup-handler
%_sbindir/pulse2-connect-machine-backuppc
%_sbindir/pulse2-disconnect-machine-backuppc

#--------------------------------------------------------------------

%package -n python-mmc-connection-manager
Summary:    Connection Manager plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   p7zip
Requires:   python-pyquery

%description -n python-mmc-connection-manager
This package contains the connection manager plugin for the MMC agent.

%files -n python-mmc-connection-manager
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/pulse2/cm
%python2_sitelib/mmc/plugins/backuppc
%python2_sitelib/pulse2/cm
%{_sysconfdir}/init.d/pulse2-cm
%_sbindir/pulse2-cm
%_sbindir/pulse2-create-group

##--------------------------------------------------------------------

%package -n     mmc-web-backuppc
Summary:        Backuppc plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version

%description -n mmc-web-backuppc
This package contains the backuppc plugin for the MMC web interface.

%files -n mmc-web-backuppc
%{_datadir}/mmc/modules/backuppc

#--------------------------------------------------------------------

%package -n     pulse2-launchers
Summary:        Pulse 2 launcher service
Group:          System/Servers
Obsoletes:      pulse2-launcher < 1.5.0
Provides:       pulse2-launcher = %version-%release

%description -n pulse2-launchers
This package contains the Pulse 2 launcher service. The Pulse 2 scheduler
service asks the launcher to connect to a set of target computers and start
a deployment. Multiple launchers can be instantiated at the same time for
scalability.

%post -n pulse2-launchers
service pulse2-launchers start >/dev/null 2>&1 || :

%preun -n pulse2-launchers
service pulse2-launchers stop >/dev/null 2>&1 || :

%files -n pulse2-launchers
%{_sysconfdir}/mmc/pulse2/launchers/keys

#--------------------------------------------------------------------

%package -n python-mmc-glpi
Summary:    GLPI plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-base >= %mmc_version
Requires:   python-sqlalchemy >= 0.6.3
Requires:   MySQL-python >= 1.2.1
Requires:   python-pulse2-common = %version-%release

Provides:   pulse-python-mmc-computers-inventory-backend = %version-%release

%description -n python-mmc-glpi
This package contains the GLPI plugin for the MMC agent. It connects to a
GLPI database to get a company inventory. This package contains the
inventory plugin for the MMC agent.

%files -n python-mmc-glpi
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/glpi.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/glpi_search_options.ini
%python2_sitelib/mmc/plugins/glpi
%_sbindir/pulse2-extract-glpi-search-options

#--------------------------------------------------------------------

%package -n     mmc-web-glpi
Summary:        GLPI plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version

Provides:       pulse-mmc-web-computers-inventory-backend = %version-%release

%description -n mmc-web-glpi
This package contains the GLPI plugin for the MMC web interface. It
allows one to query a GLPI database to display computer inventory.

%files -n mmc-web-glpi
%{_datadir}/mmc/modules/glpi

#--------------------------------------------------------------------

%package -n python-mmc-msc
Summary:    Pulse 2 MSC plugin for MMC agent
Group:      System/Servers
Requires:   python-libs
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-base >= %mmc_version
Requires:   python-pulse2-common-database-msc = %version-%release
Requires:   python-xlwt

%description -n python-mmc-msc
This package contains the MSC (Mageia Secure Control) plugin for the MMC
agent. It allows one to control and manage the entire software deployment
process.

%files -n python-mmc-msc
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/msc.ini
%python2_sitelib/mmc/plugins/msc
%{_var}/lib/pulse2/qactions
%_sbindir/pulse2-msc-clean-database
%_mandir/man1/pulse2-msc-clean-database.1.*

#--------------------------------------------------------------------

%package -n     mmc-web-msc
Summary:        MSC plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version

%description -n mmc-web-msc
This package contains the MSC (Mageia Secure Control) plugin for the
MMC web interface. It allows one to control and manage the entire software
deployment process.

%files -n mmc-web-msc
%{_datadir}/mmc/modules/msc

#--------------------------------------------------------------------

%package -n python-mmc-imaging
Summary:    Imaging plugin for MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-pulse2-common-database-imaging = %version-%release
# Needed for ImportError: No module named tasks
Requires:   python-mmc-core >= 3.1.1
Requires:   python-ipaddr
%description -n python-mmc-imaging
This package contains the imaging plugin for MMC agent.

%files -n python-mmc-imaging
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/imaging.ini
%python2_sitelib/mmc/plugins/imaging

#--------------------------------------------------------------------

%package -n	mmc-web-imaging
Summary:	Imaging plugin for the MMC web interface
Group:		System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-mmc-base >= %mmc_version

%description -n mmc-web-imaging
This package contains the imaging plugin for the MMC web interface.

%files -n mmc-web-imaging
%defattr(-,root,root,0755)
%{_datadir}/mmc/modules/imaging

#--------------------------------------------------------------------

%package -n python-mmc-support
Summary:    Imaging plugin for MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-pulse2-common-database-imaging = %version-%release
# Needed for ImportError: No module named tasks
Requires:   python-mmc-core >= 3.1.1

%description -n python-mmc-support
This package contains the imaging plugin for MMC agent.

%files -n python-mmc-support
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/support.ini
%python2_sitelib/mmc/plugins/support

#--------------------------------------------------------------------

%package -n     mmc-web-support
Summary:        Imaging plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-mmc-base >= %mmc_version

%description -n mmc-web-support
This package contains the imaging plugin for the MMC web interface.

%files -n mmc-web-support
%defattr(-,root,root,0755)
%{_datadir}/mmc/modules/support

#--------------------------------------------------------------------

%package -n python-mmc-inventory
Summary:    Inventory plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-base >= %mmc_version
Requires:   python-pulse2-common-database-inventory = %version-%release
Requires:   python-magic
Requires:   python-inotify

Provides:   pulse-python-mmc-computers-inventory-backend = %version-%release

%description -n python-mmc-inventory
This package contains the inventory plugin for the MMC agent

%files -n python-mmc-inventory
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/inventory.ini
%python2_sitelib/mmc/plugins/inventory
%_sbindir/pulse2-inventory-clean-database
%exclude %_sysconfdir/init.d/pulse2-register-pxe
%_mandir/man1/pulse2-inventory-clean-database.1.*

#--------------------------------------------------------------------

%package -n pulse2-register-pxe
Summary:    Pulse 2 Register PXE Servic/
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-base >= %mmc_version
Requires:   python-pulse2-common-database-inventory = %version-%release
Requires:   python-magic
Requires:   python-inotify

Conflicts:  python-mmc-inventory < 4.6.1

%description -n pulse2-register-pxe
Pulse 2 Register PXE Service

%files -n pulse2-register-pxe
%exclude %_sysconfdir/init.d/pulse2-register-pxe
%_prefix/lib/systemd/system/pulse2-register-pxe.service
%_sbindir/pulse2-register-pxe.py

#--------------------------------------------------------------------

%package -n     mmc-web-inventory
Summary:        Inventory plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version

Provides:       pulse-mmc-web-computers-inventory-backend = %version-%release

%description -n mmc-web-inventory
This package contains the inventory plugin for the MMC web interface.

%files -n mmc-web-inventory
%{_datadir}/mmc/modules/inventory

#--------------------------------------------------------------------

%package -n python-mmc-pkgs
Summary:    Pkgs plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-msc = %version-%release
Requires:   python2-requests
Requires:   python2-unidecode

%description -n python-mmc-pkgs
This package contains the pkgs plugin for the MMC agent.

%files -n python-mmc-pkgs
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/pkgs.ini
%python2_sitelib/mmc/plugins/pkgs
%python2_sitelib/pulse2/database/pkgs

#--------------------------------------------------------------------

%package -n python-mmc-kiosk
Summary:    Kiosk plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release

%description -n python-mmc-kiosk
This package contains the pkgs plugin for the MMC agent.

%files -n python-mmc-kiosk
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/kiosk.ini
%python2_sitelib/mmc/plugins/kiosk
%python2_sitelib/pulse2/database/kiosk

#--------------------------------------------------------------------

%package -n python-mmc-xmppmaster
Summary:    Xmppmaster plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-msc = %version-%release
Requires:   python-GeoIP
Requires:   GeoIP-data
Requires:   python-croniter

%description -n python-mmc-xmppmaster
This package contains the xmppmaster plugin for the MMC agent.

%files -n python-mmc-xmppmaster
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/xmppmaster.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/inventoryconf.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/resultinventory.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/assessor_agent.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/loadautoupdate.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/loadlogsrotation.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/loadpluginlistversion.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/loadpluginschedulerlistversion.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/loadshowregistration.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/registeryagent.ini
%python2_sitelib/mmc/plugins/xmppmaster
%python2_sitelib/pulse2/database/xmppmaster

#--------------------------------------------------------------------

%package -n python-mmc-guacamole
Summary:    Guacamole plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-msc = %version-%release

%description -n python-mmc-guacamole
This package contains the guacamole plugin for the MMC agent.

%files -n python-mmc-guacamole
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/guacamole.ini
%python2_sitelib/mmc/plugins/guacamole
%_datadir/mmc/modules/guacamole/locale

#--------------------------------------------------------------------

%package -n     mmc-web-pkgs
Summary:        Package management plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version


%description -n mmc-web-pkgs
This package contains the package management plugin for the MMC web
interface.

%files -n mmc-web-pkgs
%{_datadir}/mmc/modules/pkgs

#--------------------------------------------------------------------

%package -n     mmc-web-kiosk
Summary:        Kiosk plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version


%description -n mmc-web-kiosk
This package contains the kiosk plugin for the MMC web
interface.

%files -n mmc-web-kiosk
%{_datadir}/mmc/modules/kiosk

#--------------------------------------------------------------------

%package -n python-mmc-pulse2
Summary:    Pulse 2 MMC agent interface plugins
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python-mmc-base >= %mmc_version
Requires:   python-mmc-msc = %version-%release
Requires:   python-mmc-dyngroup = %version-%release
Requires:   python-mmc-pkgs = %version-%release
Requires:   python-pulse2-common = %version-%release
Requires:   python-sqlalchemy >= 0.6.3
Requires:   pulse-python-mmc-computers-inventory-backend = %version-%release
Requires:   python-service-identity

%description -n python-mmc-pulse2
This package will install all the Pulse 2 MMC agent interface plugins

%files -n python-mmc-pulse2
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/pulse2.ini
%python2_sitelib/mmc/plugins/pulse2

#--------------------------------------------------------------------

%package -n     mmc-web-pulse2
Summary:        Base plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version
Requires:       mmc-web-imaging

%description -n mmc-web-pulse2
This package contains the base plugin for the MMC web interface.

%files -n mmc-web-pulse2
%{_datadir}/mmc/modules/pulse2

#--------------------------------------------------------------------

%package -n     pulse2-common
Summary:        Pulse2 common files
Group:          System/Servers
Requires:       p7zip
Requires:       python-configobj
Requires:       curl
Requires:       nsis
Requires:       bind-utils
Requires:       python-psutil >= 0.6.1
Requires:       python-netaddr
Requires:       python-netifaces

Requires:       python-mmc-connection-manager

Provides:       /usr/sbin/pulse2-debug

%description -n pulse2-common
This package contains Pulse 2 common files like documentation.

%files -n pulse2-common
%{_sbindir}/pulse2-setup
%{_sbindir}/pulse2-load-defaults
%{_sbindir}/pulse2-dbupdate
%{_sbindir}/pulse2-debug
%{_sbindir}/pulse2-collect-info
%{_sbindir}/restart-pulse-services
%{_sbindir}/pulse2-packageparser.py
%_docdir/mmc/contrib/
%_datadir/mmc/conf/apache/pulse.conf
%config(noreplace) %_sysconfdir/httpd/conf.d/pulse.conf
%_var/lib/pulse2/file-transfer
#FIXME: Move on the correct package later
# Does not belong to here, lefover file.
%exclude %_sysconfdir/mmc/pulse2/atftpd/pcre.conf

# Split later in its own rpm
%python2_sitelib/pulse2/tests/test_utils.py

#--------------------------------------------------------------------

%package -n     pulse2-inventory-server
Summary:        Pulse 2 inventory server
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-pulse2-common = %version-%release
Requires:       python-pulse2-common-database-inventory = %version-%release
Requires:       python-mmc-base >= %mmc_version
Requires:       pyOpenSSL

%description -n pulse2-inventory-server
This package contains Pulse 2 inventory server. It collects computers
inventories and insert them into the database.

%post -n pulse2-inventory-server
service pulse2-inventory-server start >/dev/null 2>&1 || :

%preun -n pulse2-inventory-server
service pulse2-inventory-server stop >/dev/null 2>&1 || :

%files -n pulse2-inventory-server
%exclude %{_sysconfdir}/init.d/pulse2-inventory-server
%_prefix/lib/systemd/system/pulse2-inventory-server.service
%config(noreplace) %{_sysconfdir}/mmc/pulse2/inventory-server/inventory-server.ini
%{_sysconfdir}/mmc/pulse2/inventory-server/OcsNGMap.xml
%{_sysconfdir}/mmc/pulse2/inventory-server/keys/
%{_sysconfdir}/mmc/pulse2/inventory-server/xml-fix/
%{_sbindir}/pulse2-inventory-server
%_mandir/man1/pulse2-inventory-server.1*
%python2_sitelib/pulse2/inventoryserver

#--------------------------------------------------------------------

%package -n     pulse2-package-server
Summary:        Pulse 2 package server
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-pulse2-common = %version-%release
Requires:       python-mmc-core
Requires:       genisoimage
Requires:       pyOpenSSL

Provides:       pulse2-imaging-server = %version-%release
Obsoletes:      pulse2-imaging-server < %version-%release

%description -n pulse2-package-server
This package contains the Pulse 2 package server. The package server manages
the packages and the images repository.

%post -n pulse2-package-server
service pulse2-package-server start >/dev/null 2>&1 || :

%preun -n pulse2-package-server
service pulse2-package-server start >/dev/null 2>&1 || :

%files -n pulse2-package-server
%_prefix/lib/systemd/system/pulse2-imaging-server.service
%{_sysconfdir}/init.d/pulse2-package-server
%{_bindir}/pulse2-synch-masters
%config(noreplace) %_sysconfdir/mmc/pulse2/package-server/package-server.ini
%{_sysconfdir}/mmc/pulse2/package-server/keys
%{_sbindir}/pulse2-package-server
%{_sbindir}/pulse2-package-server-register-imaging
%_mandir/man1/pulse2-package-server.1*
%_mandir/man1/pulse2-package-server-register-imaging.1.*
%python2_sitelib/pulse2/package_server

#--------------------------------------------------------------------

%package -n     pulse2-scheduler
Summary:        Pulse 2 scheduler service
Group:          System/Servers
Requires:       python-mmc-database

%description -n pulse2-scheduler
This package contains the Pulse 2 scheduler service. It connects to the MSC
(Mageia Secure Control) database and tell to Pulse 2 launchers to start
new deployment jobs when needed.

%post -n pulse2-scheduler
service pulse2-scheduler start >/dev/null 2>&1 || :

%preun -n pulse2-scheduler
service pulse2-scheduler stop >/dev/null 2>&1 || :

%files -n pulse2-scheduler
%{_sysconfdir}/init.d/pulse2-scheduler
%dir %_var/lib/pulse2/packages
%dir %_var/lib/pulse2/imaging
%dir %_var/lib/pulse2/imaging/bootmenus
%dir %_var/lib/pulse2/imaging/isos
%dir %_var/lib/pulse2/imaging/computers
%dir %_var/lib/pulse2/imaging/inventories
%dir %_var/lib/pulse2/imaging/masters
#%dir %_var/lib/pulse2/imaging/custom
%dir %_var/lib/pulse2/imaging/archives
%config(noreplace) %_sysconfdir/mmc/pulse2/scheduler/scheduler.ini
%{_sysconfdir}/mmc/pulse2/scheduler/keys
%{_sbindir}/pulse2-scheduler
%{_sbindir}/pulse2-scheduler-manager
%{_sbindir}/pulse2-scheduler-proxy
%_mandir/man1/pulse2-scheduler*.1*
%python2_sitelib/pulse2/scheduler

#--------------------------------------------------------------------

%package -n     python-pulse2-common-database-dyngroup
Summary:        Pulse 2 common dynamic groups database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-pulse2-common-database = %version-%release

%description -n python-pulse2-common-database-dyngroup
This package contains Pulse 2 common dynamic groups database files.

%files -n python-pulse2-common-database-dyngroup
%python2_sitelib/pulse2/database/dyngroup

#--------------------------------------------------------------------

%package -n     python-pulse2-common-database-imaging
Summary:        Pulse 2 common imaging database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-pulse2-common-database = %version-%release

%description -n python-pulse2-common-database-imaging
This package contains Pulse 2 common imaging database files

%files -n python-pulse2-common-database-imaging
%python2_sitelib/pulse2/database/imaging

#--------------------------------------------------------------------

%package -n     python-pulse2-common-database-inventory
Summary:        Pulse 2 common inventory database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-pulse2-common-database = %version-%release

%description -n python-pulse2-common-database-inventory
This package contains Pulse 2 common inventory database files

%files -n python-pulse2-common-database-inventory
%python2_sitelib/pulse2/database/inventory

#--------------------------------------------------------------------

%package -n     python-pulse2-common-database-msc
Summary:        Pulse 2 common MSC database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-pulse2-common-database = %version-%release

%description -n python-pulse2-common-database-msc
This package contains Pulse 2 common MSC database files

%files -n python-pulse2-common-database-msc
%python2_sitelib/pulse2/database/msc

#--------------------------------------------------------------------

%package -n     python-pulse2-common-database
Summary:        Pulse 2 common database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-pulse2-common = %version-%release
Requires:       python-sqlalchemy >= 0.6.3
Requires:       MySQL-python

%description -n python-pulse2-common-database
This package contains Pulse 2 common database files.

%files -n python-pulse2-common-database
%python2_sitelib/pulse2/database/__init__.py
%python2_sitelib/pulse2/database/pulse/__init__.py
%python2_sitelib/pulse2/database/pulse/config.py

#--------------------------------------------------------------------

%package -n     pulse2-uuid-resolver
Summary:        Helper to resolve Pulse's UUID into IP address
Group:          System/Servers
Requires:       python-pulse2-common = %version-%release

%description -n pulse2-uuid-resolver
This package contains a helper to resolve Pulse's UUID into IP address.

%files -n pulse2-uuid-resolver
%dir %{_sysconfdir}/mmc/pulse2/uuid-resolver
%attr(0644,root,root) %config(noreplace) %_sysconfdir/mmc/pulse2/uuid-resolver/uuid-resolver.ini
%_bindir/pulse2-uuid-resolver

#--------------------------------------------------------------------
%package -n     pulse2-dlp-server
Summary:        Pulse 2 Download provider service
Group:          System/Servers
Requires:       python-pulse2-common = %version-%release
Requires:       python-cherrypy

%description -n pulse2-dlp-server
This package contains a WSGI daemon to provide "pull mode" interface
for clients outside the corporate LAN.

%post -n pulse2-dlp-server
service pulse2-dlp-server start >/dev/null 2>&1 || :


%preun -n pulse2-dlp-server
service pulse2-dlp-server stop >/dev/null 2>&1 || :

%files -n pulse2-dlp-server
%_bindir/pulse2-dlp-server
%attr(0640,root,root) %config(noreplace) %_sysconfdir/mmc/pulse2/dlp-server/dlp-apache.conf
%attr(0640,root,root) %config(noreplace) %_sysconfdir/mmc/pulse2/dlp-server/dlp-server.ini
%attr(0640,root,root) %config(noreplace) %_sysconfdir/mmc/pulse2/dlp-server/dlp-wsgi.ini
%python2_sitelib/pulse2/dlp
%_sysconfdir/init.d/pulse2-dlp-server

#--------------------------------------------------------------------

%package -n     python-pulse2-common
Summary:        Pulse 2 common files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-twisted-web >= 2.4.0

Provides:       python-pulse2-meta < 1.5.0
Obsoletes:      python-pulse2-meta = %version-%release

Provides:       pulse2-common-client-apis < 1.5.0
Obsoletes:      pulse2-common-client-apis = %version-%release


%description -n python-pulse2-common
This package contains Pulse 2 common files.

%files -n python-pulse2-common
%python2_sitelib/pulse2/apis
%python2_sitelib/pulse2/imaging
%python2_sitelib/pulse2/managers
%python2_sitelib/pulse2/__init__.py
%python2_sitelib/pulse2/cache.py
%python2_sitelib/pulse2/consts.py
%python2_sitelib/pulse2/health.py
%python2_sitelib/pulse2/site.py
%python2_sitelib/pulse2/time_intervals.py
%python2_sitelib/pulse2/utils.py
%python2_sitelib/pulse2/version.py
%python2_sitelib/pulse2/xmlrpc.py
%python2_sitelib/pulse2/network.py

%doc %_docdir/pulse2

#--------------------------------------------------------------------

%package -n mmc-agent
Summary:    Console agent
Group:      System/Servers
%if %_vendor == "Mageia"
Requires:   python-base
Requires:   python-OpenSSL
Requires:   python-gobject
%else
Requires:   python
Requires:   pyOpenSSL
Requires:   pygobject2
%endif
Requires:   python-mmc-base
Requires:   logrotate
Requires(pre): python-mmc-base
Requires:   python-mmc-base
Requires:   ajax-php-file-manager
Requires:   python-memory-profiler
Requires:   python-dateutil

%description -n mmc-agent
XMLRPC server of the Console API.
This is the underlying service used by the MMC web interface.

%files -n mmc-agent
%defattr(-,root,root,0755)
%doc COPYING ChangeLog
%attr(0755,root,root) %{_unitdir}/mmc-agent.service
%attr(0755,root,root) %dir %{_sysconfdir}/mmc
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/agent
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/agent/keys
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/config.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/keys/cacert.pem
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/keys/privkey.pem
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/mmc-agent
%attr(0755,root,root) %{_sbindir}/mmc-agent
%attr(0755,root,root) %{_sbindir}/mmc-add-schema
%attr(0755,root,root) %{_bindir}/mmc-helper
%attr(0755,root,root) %{_bindir}/mmc-stats
%attr(0750,root,root) %dir /var/log/mmc
%attr(0750,root,root) %dir /var/lib/mmc
%doc %{_mandir}/man1/mmc-add-schema.1.*
%doc %{_mandir}/man1/mmc-agent.1.*
%doc %{_mandir}/man1/mmc-helper.1.*
%doc %{_mandir}/man1/mmc-stats.1.*
%dir %{py_puresitedir}/mmc
%{py_puresitedir}/mmc/agent.py*
%{_docdir}/mmc/contrib/monit/mmc-agent

#--------------------------------------------------------------------

%package -n python-mmc-core
Summary:    Console core
Group:      System/Servers
%if %_vendor == "Mageia"
Requires:   python-base
%else
Requires:   python
%endif
Requires:   python-twisted-web

%description -n python-mmc-core
Contains the mmc core python classes used by all other
modules.

%files -n python-mmc-core
%defattr(-,root,root,0755)
%dir %{py_puresitedir}/mmc
%{py_puresitedir}/mmc/core
%{py_puresitedir}/mmc/support
%{py_puresitedir}/mmc/__init__.py*
%{py_puresitedir}/mmc/site.py*
%{py_puresitedir}/mmc/ssl.py*
%{py_puresitedir}/mmc/client
%dir %{py_puresitedir}/mmc/plugins
%{py_puresitedir}/mmc/plugins/__init__.py*
%{_docdir}/mmc/contrib/audit

#--------------------------------------------------------------------

%package -n	    python-mmc-base
Summary:	    Console base plugin
Group:      	System/Servers
%if %_vendor == "Mageia"
Requires:       python-base
%else
Requires:       python
%endif
Requires:  	python-ldap
Requires:   	python-mmc-plugins-tools
Requires:   	python-mmc-core
Requires:   	python-mmc-dashboard >= %{version}

%description -n	python-mmc-base
Contains the base infrastructure for all MMC plugins:
 * support classes
 * base LDAP management classes

%post -n python-mmc-base
sed -i 's!%%(basedn)s!%%(baseDN)s!g' %{_sysconfdir}/mmc/plugins/base.ini

%files -n python-mmc-base
%defattr(-,root,root,0755)
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/plugins
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/base.ini
%attr(0755,root,root) %{_sbindir}/mds-report
%dir %{py_puresitedir}/mmc
%dir %{py_puresitedir}/mmc/plugins
%{py_puresitedir}/mmc/plugins/base
%{_docdir}/mmc/contrib/base
%{_docdir}/mmc/contrib/scripts/usertoken-example
%{_docdir}/mmc/contrib/scripts/mmc-check-users-primary-group
%exclude %{py_puresitedir}/mmc/plugins/report

#--------------------------------------------------------------------

%package -n python-mmc-ppolicy
Summary:    Console password policy plugin
Group:      System/Servers
%if %_vendor == "Mageia"
Requires:       python-base
%else
Requires:       python
%endif
Requires:   python-mmc-core

%description -n python-mmc-ppolicy
Contains the password policy python classes to handle
password policies in LDAP.

%files -n python-mmc-ppolicy
%defattr(-,root,root,0755)
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/plugins
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/ppolicy.ini
%dir %{py_puresitedir}/mmc
%dir %{py_puresitedir}/mmc/plugins
%{py_puresitedir}/mmc/plugins/ppolicy
%{_docdir}/mmc/contrib/ppolicy
%{_docdir}/mmc/contrib/scripts/mmc-check-expired-passwords-example

#--------------------------------------------------------------------

%package -n python-mmc-dashboard
Summary:    Console dashboard plugin
Group:      System/Servers
%if %_vendor == "Mageia"
Requires:   python-base
%else
Requires:   python
%endif
Requires:   python-mmc-base >= %{version}
Requires:   python-psutil >= 0.6.1

%description -n python-mmc-dashboard
Console dashboard plugin

%files -n python-mmc-dashboard
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/dashboard.ini
%{py_puresitedir}/mmc/plugins/dashboard

#--------------------------------------------------------------------

%package -n     mmc-web-dashboard
Summary:        Dashboard module for the MMC web interface
Group:          System/Servers
Requires:       mmc-web-base >= %{version}

%description -n mmc-web-dashboard
Dashboard module for the MMC web interface

%files -n mmc-web-dashboard
%{_datadir}/mmc/modules/dashboard

#--------------------------------------------------------------------

%package -n python-mmc-services
Summary:    Console services plugin
Group:      System/Servers
%if %_vendor == "Mageia"
Requires:   python-base
%else
Requires:   python
%endif
Requires:   python-mmc-base >= %{version}
Requires:   python-systemd-dbus
Requires:   python-dbus

%description -n python-mmc-services
Console services plugin

%files -n python-mmc-services
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/services.ini
%{py_puresitedir}/mmc/plugins/services

%post -n python-mmc-services
%if %_vendor == "Mageia"
sed -i 's!named,!!' %{_sysconfdir}/mmc/plugins/services.ini
%endif
# remove ldap from the services list if present
sed -i '/base = ldap/d' %{_sysconfdir}/mmc/plugins/services.ini
# add blacklist option if not present
grep -q '^blacklist' %{_sysconfdir}/mmc/plugins/services.ini
[ $? -eq 1 ] && sed -i '/journalctl_path/ ablacklist = ldap,slapd,named' %{_sysconfdir}/mmc/plugins/services.ini || :

#--------------------------------------------------------------------

%package -n     mmc-web-services
Summary:        Services module for the MMC web interface
Group:          System/Servers
Requires:       mmc-web-base >= %{version}

%description -n mmc-web-services
Services module for the MMC web interface

%files -n mmc-web-services
%{_datadir}/mmc/modules/services

#--------------------------------------------------------------------

%package -n	mmc-web-ppolicy
Summary:	Password policies plugin
Group:		System/Servers
Requires:	mmc-web-base

%description -n mmc-web-ppolicy
Contains the password policy web interface

%files -n mmc-web-ppolicy
%defattr(-,root,root,0755)
%{_datadir}/mmc/modules/ppolicy

#--------------------------------------------------------------------

%package -n 	mmc-web-base
Summary:        MMC web interface to interact with a MMC agent
Group:          System/Servers
%if %_vendor == "Mageia"
Requires:       apache >= 2.0.52
Requires:       apache-mod_php
%else
Requires:       httpd >= 2.0.52
Requires:       php
%endif
Requires:       php-xmlrpc
Requires:       php-iconv
Requires:   	mmc-web-dashboard >= %{version}
Requires:       node-d3

%description -n mmc-web-base
Console web interface designed by Linbox.

%post -n mmc-web-base
if [ ! -L "/usr/share/mmc/jsframework/d3" ];
then
    ln -s /usr/lib/node_modules/d3 /usr/share/mmc/jsframework/d3
fi

%files -n mmc-web-base
%defattr(-,root,root,0755)
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/apache
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/apache/mmc.conf
%attr(0640,root,root) %config(noreplace) %_webappconfdir/mmc.conf
%attr(0640,root,apache) %config(noreplace) %{_sysconfdir}/mmc/mmc.ini
%dir %{_datadir}/mmc
%{_datadir}/mmc/*
%exclude %{_datadir}/mmc/modules/ppolicy
%exclude %{_datadir}/mmc/modules/services
%exclude %{_datadir}/mmc/modules/dashboard

#--------------------------------------------------------------------

%package -n	python-mmc-plugins-tools
Summary:	Required tools for some MMC plugins
Group:		System/Servers
%if %_vendor == "Mageia"
Requires:	cdrkit-genisoimage
%else
Requires:       genisoimage
%endif
%description -n	python-mmc-plugins-tools
Contains common tools needed by some plugins of mmc-agent package.

%files -n python-mmc-plugins-tools
%defattr(-,root,root,0755)
%dir %{_libdir}/mmc
%dir %{_libdir}/mmc/backup-tools
%{_libdir}/mmc/backup-tools/cdlist
%{_libdir}/mmc/backup-tools/backup.sh

#--------------------------------------------------------------------

%if %with_report
%package -n python-mmc-report
Summary:    Console report plugin
Group:      System/Servers
%if %_vendor == "Mageia"
Requires:   python-base
%else
Requires:   python
%endif
Requires:   python-mmc-base >= %{version}
Requires:   python-psutil >= 0.6.1
Requires:   python-xlwt
Requires:   python-weasyprint

%description -n python-mmc-report
Console report plugin

%files -n python-mmc-report
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/report.ini
%{_sysconfdir}/mmc/plugins/report
%{py_puresitedir}/mmc/plugins/report
%{_docdir}/mmc/contrib/report

#--------------------------------------------------------------------

%package -n     mmc-web-report
Summary:        Report module for the MMC web interface
Group:          System/Servers
Requires:       mmc-web-base >= %{version}

%description -n mmc-web-report
Report module for the MMC web interface

%files -n mmc-web-report
%{_datadir}/mmc/modules/report

#--------------------------------------------------------------------

%package -n     python-mmc-database
Summary:        Console database common files
Group:          System/Servers
Requires:       python-mmc-base = %version-%release
Requires:       python-sqlalchemy >= 0.6.3
%if %_vendor == "Mageia"
Requires:       python-mysql
%else
Requires:       MySQL-python
%endif

%description -n python-mmc-database
Console database common files
Allow the use of SQL databases within MMC framework.

%files -n python-mmc-database
%{py_puresitedir}/mmc/database
%endif

#--------------------------------------------------------------------

%prep
%setup -q  -n pulse2-%version
cp %{SOURCE5}   agent/mmc/plugins/base
cp %{SOURCE6}   web/modules/base/computers

%build

%configure --disable-python-check --disable-wol

%make_build

%install
%makeinstall

mkdir -p %buildroot%{_sbindir}

mkdir -p %buildroot%_var/lib/pulse2/packages

rm -rf %buildroot%{_sysconfdir}/init.d/pulse2-imaging-server

mkdir -p %buildroot%_prefix/lib/systemd/system

cp %{SOURCE1} %buildroot%_sysconfdir/init.d/pulse2-dlp-server

cp %{SOURCE2} %buildroot%_prefix/lib/systemd/system
cp %{SOURCE3} %buildroot%_prefix/lib/systemd/system
cp %{SOURCE4} %buildroot%_prefix/lib/systemd/system

mkdir -p %buildroot%_sysconfdir/httpd/conf.d/
cp -fv %buildroot%_datadir/mmc/conf/apache/pulse.conf %buildroot%_sysconfdir/httpd/conf.d/

mkdir -p %buildroot%_var/lib/pulse2/file-transfer

cp services/contrib/glpi-92.sql %buildroot%_datadir/doc/mmc/contrib/

rm -f %buildroot%python2_sitelib/pulse2/apis/clients/mirror.py
mv %buildroot%python2_sitelib/pulse2/apis/clients/mirror1.py %buildroot%python2_sitelib/pulse2/apis/clients/mirror.py

rm -f %buildroot%python2_sitelib/pulse2/apis/clients/mirror_api.py
mv %buildroot%python2_sitelib/pulse2/apis/clients/mirror_api1.py %buildroot%python2_sitelib/pulse2/apis/clients/mirror_api.py

# install log rotation stuff
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/mmc-agent << EOF
/var/log/mmc/mmc-agent.log /var/log/dhcp-ldap-startup.log /var/log/mmc/mmc-fileprefix.log {
    create 644 root root
    monthly
    compress
    missingok
    postrotate
}
EOF

# create directory for MMC logo
install -d %{buildroot}%{_datadir}/mmc/img/logo/

# patch privkey.pem
mv %{buildroot}%{_sysconfdir}/mmc/agent/keys/localcert.pem %{buildroot}%{_sysconfdir}/mmc/agent/keys/privkey.pem
sed -i 's!localcert.pem!privkey.pem!g' %{buildroot}%{_sysconfdir}/mmc/agent/config.ini

# install apache configuration
install -d %{buildroot}%_webappconfdir
# apache 2.4 support
sed -i '/Order allow/ {N; s/Order allow,deny\n[ ]*allow from all/Require all granted/ }' %{buildroot}%{_sysconfdir}/mmc/apache/mmc.conf
cp %{buildroot}%{_sysconfdir}/mmc/apache/mmc.conf %{buildroot}%_webappconfdir/mmc.conf

#sed -i 's/^community.*$/community = no/' %{buildroot}%{_sysconfdir}/mmc/mmc.ini

mkdir -p %buildroot%_prefix/lib/systemd/system/
cp services/systemd/mmc-agent.service %buildroot%_prefix/lib/systemd/system/

# Cleanup
find '%{buildroot}' -name '*.pyc' -o -name '*.pyo' -delete
