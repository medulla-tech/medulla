# RHEL6 compat hacks
%if "%_vendor" == "redhat"
%define configure2_5x %configure
%define make %{__make}
%define makeinstall_std %{__make} DESTDIR=%{?buildroot:%{buildroot}} install
%define mkrel(c:) %{-c: 0.%{-c*}.}%{1}%{?subrel:.%subrel}%{?distsuffix:%distsuffix}%{?!distsuffix:.el6}
%endif
# Turn off the brp-python3-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define __requires_exclude ^(pear\\(graph.*|pear\\(includes.*|pear\\(modules.*)$


%global __python %{__python3}

%if "%_vendor" == "Mageia"
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
%define real_version           5.4.6
%define mmc_version            5.4.6

Summary:	Management Console
Name:		medulla
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
Source3:        pulse2-imaging-server.service
Source4:        pulse2-register-pxe.service

BuildRequires:	python3.11-devel
BuildRequires:	gettext
BuildRequires:	gettext-devel
%if "%_vendor" == "Mageia"
BuildRequires:  xsltproc
%else
BuildRequires:  libxslt
%endif
BuildRequires:  wget
BuildRequires:  docbook-style-xsl
BuildRequires:  systemd-rpm-macros

Requires:       mmc-agent
Requires:       mmc-web-base
Requires:       python3-mmc-base
Requires:       mmc-web-dyngroup
Requires:       python3-mmc-dyngroup
Requires:       mmc-web-imaging
Requires:       python3-mmc-imaging
Requires:       mmc-web-msc
Requires:       python3-mmc-msc
Requires:       mmc-web-pkgs
Requires:       python3-mmc-pkgs
Requires:       mmc-web-pulse2
Requires:       python3-mmc-pulse2
Requires:       mmc-web-kiosk
Requires:       python3-mmc-kiosk
Requires:       mmc-web-admin
Requires:       python3-mmc-admin
Requires:       mmc-web-urbackup
Requires:       python3-mmc-urbackup
Requires:       mmc-web-updates
Requires:       python3-mmc-updates
Requires:       mmc-web-mastering
Requires:       python3-mmc-mastering
Requires:       mmc-web-mobile
Requires:       python3-mmc-mobile
Requires:       pulse2-common
Requires:       pulse2-package-server
Requires:       python3-pulse2-common-database-dyngroup
Requires:       pulse-mmc-web-computers-inventory-backend
Requires:       pulse-python3-mmc-computers-inventory-backend

%description
Management Console agent & web interface with
base and password policies modules.

%files

#--------------------------------------------------------------------

%package -n python3-mmc-dyngroup
Summary:    Dynamic computer group plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-pulse2-common-database-dyngroup = %version-%release

Obsoletes:  python-mmc-dyngroup < 4.7.0
Provides:   python-mmc-dyngroup = %version-%release

%description -n python3-mmc-dyngroup
This package contains the dynamic computer group plugin for the MMC agent. It
stores into a database static and dynamic group of computers to ease massive
software deployment.

%files -n python3-mmc-dyngroup
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/dyngroup.ini
%python3_sitelib/mmc/plugins/dyngroup

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

%package -n python3-mmc-backuppc
Summary:    Backuppc plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   p7zip
Requires:   python3-pyquery

Obsoletes:  python-mmc-backuppc < 4.7.0
Provides:   python-mmc-backuppc = %version-%release

%description -n python3-mmc-backuppc
This package contains the backuppc plugin for the MMC agent.

%files -n python3-mmc-backuppc
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/backuppc.ini
%python3_sitelib/mmc/plugins/backuppc
%python3_sitelib/pulse2/database/backuppc
%_sbindir/pulse2-backup-servers
%_bindir/pulse2-backup-handler
%_sbindir/pulse2-connect-machine-backuppc
%_sbindir/pulse2-disconnect-machine-backuppc

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

%package -n python3-mmc-glpi
Summary:    GLPI plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-base >= %mmc_version
Requires:   python3-sqlalchemy >= 0.6.3
Requires:   python3.11-mysqlclient >= 1.2.1
Requires:   python3-pulse2-common = %version-%release

Provides:   pulse-python3-mmc-computers-inventory-backend = %version-%release

Obsoletes:  python-mmc-glpi < 4.7.0
Provides:   python-mmc-glpi = %version-%release


%description -n python3-mmc-glpi
This package contains the GLPI plugin for the MMC agent. It connects to a
GLPI database to get a company inventory. This package contains the
inventory plugin for the MMC agent.

%files -n python3-mmc-glpi
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/glpi.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/glpi_search_options.ini
%python3_sitelib/mmc/plugins/glpi
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

%package -n python3-mmc-msc
Summary:    Pulse 2 MSC plugin for MMC agent
Group:      System/Servers
%if "%_vendor" == "redhat"
Requires:   python3-libs
%endif
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-base >= %mmc_version
Requires:   python3-pulse2-common-database-msc = %version-%release
Requires:   python3-xlwt

Obsoletes:  python-mmc-msc < 4.7.0
Provides:   python-mmc-msc = %version-%release

%description -n python3-mmc-msc
This package contains the MSC (Mageia Secure Control) plugin for the MMC
agent. It allows one to control and manage the entire software deployment
process.

%files -n python3-mmc-msc
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/msc.ini
%python3_sitelib/mmc/plugins/msc
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

%package -n python3-mmc-imaging
Summary:    Imaging plugin for MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-pulse2-common-database-imaging = %version-%release
# Needed for ImportError: No module named tasks
Requires:   python3-mmc-core >= 3.1.1

Obsoletes:  python-mmc-imaging < 4.7.0
Provides:   python-mmc-imaging = %version-%release


%description -n python3-mmc-imaging
This package contains the imaging plugin for MMC agent.

%files -n python3-mmc-imaging
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/imaging.ini
%python3_sitelib/mmc/plugins/imaging
%_sbindir/message-sender.py

#--------------------------------------------------------------------

%package -n	mmc-web-imaging
Summary:	Imaging plugin for the MMC web interface
Group:		System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-mmc-base >= %mmc_version

%description -n mmc-web-imaging
This package contains the imaging plugin for the MMC web interface.

%files -n mmc-web-imaging
%defattr(-,root,root,0755)
%{_datadir}/mmc/modules/imaging
%{_datadir}/mmc/imaging/bootmenu.php

#--------------------------------------------------------------------

%package -n python3-mmc-support
Summary:    Imaging plugin for MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-pulse2-common-database-imaging = %version-%release
# Needed for ImportError: No module named tasks
Requires:   python3-mmc-core >= 3.1.1

Obsoletes:  python-mmc-support < 4.7.0
Provides:   python-mmc-support = %version-%release

%description -n python3-mmc-support
This package contains the imaging plugin for MMC agent.

%files -n python3-mmc-support
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/support.ini
%python3_sitelib/mmc/plugins/support

#--------------------------------------------------------------------

%package -n     mmc-web-support
Summary:        Imaging plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-mmc-base >= %mmc_version

%description -n mmc-web-support
This package contains the imaging plugin for the MMC web interface.

%files -n mmc-web-support
%defattr(-,root,root,0755)
%{_datadir}/mmc/modules/support

#--------------------------------------------------------------------

%package -n python3-mmc-urbackup
Summary:    Urbackup plugin for MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Obsoletes:  python-pulse2-common-database-urbackup

%description -n python3-mmc-urbackup
This package contains the urbackup plugin for MMC agent.

%files -n python3-mmc-urbackup
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/urbackup.ini
%python3_sitelib/mmc/plugins/urbackup
%python3_sitelib/pulse2/database/urbackup

#--------------------------------------------------------------------

%package -n     mmc-web-urbackup
Summary:        Urbackup plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python-mmc-base >= %mmc_version

%description -n mmc-web-urbackup
This package contains the urbackup plugin for the MMC web interface.

%files -n mmc-web-urbackup
%defattr(-,root,root,0755)
%{_datadir}/mmc/modules/urbackup

#--------------------------------------------------------------------

%package -n python3-mmc-inventory
Summary:    Inventory plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-base >= %mmc_version
Requires:   python3-pulse2-common-database-inventory = %version-%release
Requires:   python3-magic
Requires:   python3-inotify

Provides:   pulse-python3-mmc-computers-inventory-backend = %version-%release

Obsoletes:  python-mmc-inventory < 4.7.0
Provides:   python-mmc-inventory = %version-%release

%description -n python3-mmc-inventory
This package contains the inventory plugin for the MMC agent

%files -n python3-mmc-inventory
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/inventory.ini
%python3_sitelib/mmc/plugins/inventory
%_sbindir/pulse2-inventory-clean-database
%exclude %_sysconfdir/init.d/pulse2-register-pxe
%_mandir/man1/pulse2-inventory-clean-database.1.*

#--------------------------------------------------------------------

%package -n pulse2-register-pxe
Summary:    Pulse 2 Register PXE Servic/
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-base >= %mmc_version
Requires:   python3-pulse2-common-database-inventory = %version-%release
Requires:   python3-magic
Requires:   python3-inotify

Conflicts:  python3-mmc-inventory < 4.6.1

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

%package -n python3-mmc-pkgs
Summary:    Pkgs plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-msc = %version-%release
Requires:   python3-requests
Requires:   python3-unidecode
Requires:   python3-magic

Obsoletes:  python-mmc-pkgs < 4.7.0
Provides:   python-mmc-pkgs = %version-%release

%description -n python3-mmc-pkgs
This package contains the pkgs plugin for the MMC agent.

%files -n python3-mmc-pkgs
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/pkgs.ini
%python3_sitelib/mmc/plugins/pkgs
%python3_sitelib/pulse2/database/pkgs

#--------------------------------------------------------------------

%package -n python3-mmc-kiosk
Summary:    Kiosk plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release

Obsoletes:  python-mmc-kiosk < 4.7.0
Provides:   python-mmc-kiosk = %version-%release

%description -n python3-mmc-kiosk
This package contains the pkgs plugin for the MMC agent.

%files -n python3-mmc-kiosk
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/kiosk.ini
%python3_sitelib/mmc/plugins/kiosk
%python3_sitelib/pulse2/database/kiosk

#--------------------------------------------------------------------

%package -n python3-mmc-updates
Summary:    OS Updates plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release

%description -n python3-mmc-updates
This package contains the updates plugin for the MMC agent.

%files -n python3-mmc-updates
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/updates.ini
%python3_sitelib/mmc/plugins/updates
%python3_sitelib/pulse2/database/updates


#--------------------------------------------------------------------

%package -n python3-mmc-admin
Summary:    Kiosk plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-pulse2-common-database-admin = %version-%release

Obsoletes:  python-mmc-admin < 4.7.0
Provides:   python-mmc-admin = %version-%release

%description -n python3-mmc-admin
This package contains the admin plugin for the MMC agent.

%files -n python3-mmc-admin
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/admin.ini
%python3_sitelib/mmc/plugins/admin
%{_docdir}/pulse2/contrib/admin

#--------------------------------------------------------------------

%package -n python3-mmc-xmppmaster
Summary:    Xmppmaster plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-msc = %version-%release
Requires:   python3-GeoIP
Requires:   GeoIP-data
Requires:   python3-croniter

Obsoletes:  python-mmc-xmppmaster < 4.7.0
Provides:   python-mmc-xmppmaster = %version-%release

%description -n python3-mmc-xmppmaster
This package contains the xmppmaster plugin for the MMC agent.

%pre -n     python3-mmc-xmppmaster
if ! getent passwd | grep -q "^pulsetransfert:"; then
    echo -n "Adding user pulsetransfert..."
    adduser --system \
        -d /var/lib/pulse2/file-transfer \
        -s /bin/rbash \
        pulsetransfert
    echo "..done"
fi

%files -n python3-mmc-xmppmaster
%{_sysconfdir}/mmc/plugins/xmppmaster.ini
%{_sysconfdir}/mmc/plugins/inventoryconf.ini
%{_sysconfdir}/mmc/plugins/resultinventory.ini
%{_sysconfdir}/mmc/plugins/assessor_agent.ini
%{_sysconfdir}/mmc/plugins/loadautoupdate.ini
%{_sysconfdir}/mmc/plugins/loadlogsrotation.ini
%{_sysconfdir}/mmc/plugins/loadpluginlistversion.ini
%{_sysconfdir}/mmc/plugins/loadpluginschedulerlistversion.ini
%{_sysconfdir}/mmc/plugins/loadshowregistration.ini
%{_sysconfdir}/mmc/plugins/registeryagent.ini
%{_sysconfdir}/mmc/plugins/loadreconf.ini
%{_sysconfdir}/mmc/plugins/wakeonlangroup.ini
%{_sysconfdir}/mmc/plugins/wakeonlan.ini
%python3_sitelib/mmc/plugins/xmppmaster
%python3_sitelib/pulse2/database/xmppmaster

#--------------------------------------------------------------------

%package -n python3-mmc-guacamole
Summary:    Guacamole plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-msc = %version-%release

Obsoletes:  python-mmc-guacamole < 4.7.0
Provides:   python-mmc-guacamole = %version-%release

%description -n python3-mmc-guacamole
This package contains the guacamole plugin for the MMC agent.

%files -n python3-mmc-guacamole
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/guacamole.ini
%python3_sitelib/mmc/plugins/guacamole
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

%package -n     mmc-web-updates
Summary:        OS Updates plugin for the MMC web interface
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       mmc-web-base >= %mmc_version


%description -n mmc-web-updates
This package contains the updates plugin for the MMC web
interface.

%files -n mmc-web-updates
%{_datadir}/mmc/modules/updates

#--------------------------------------------------------------------

%package -n python3-mmc-pulse2
Summary:    Pulse 2 MMC agent interface plugins
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-mmc-base >= %mmc_version
Requires:   python3-mmc-msc = %version-%release
Requires:   python3-mmc-dyngroup = %version-%release
Requires:   python3-mmc-pkgs = %version-%release
Requires:   python3-mmc-kiosk = %version-%release
Requires:   python3-mmc-updates = %version-%release
Requires:   python3-pulse2-common = %version-%release
Requires:   python3-sqlalchemy >= 0.6.3
Requires:   pulse-python3-mmc-computers-inventory-backend = %version-%release
Requires:   python-service-identity

Obsoletes:  python-mmc-pulse2 < 4.7.0
Provides:   python-mmc-pulse2 = %version-%release

%description -n python3-mmc-pulse2
This package will install all the Pulse 2 MMC agent interface plugins

%files -n python3-mmc-pulse2
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/medulla_server.ini
%python3_sitelib/mmc/plugins/medulla_server

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
%{_datadir}/mmc/modules/medulla_server

#--------------------------------------------------------------------

%package -n     pulse2-common
Summary:        Pulse2 common files
Group:          System/Servers
Requires:       p7zip
Requires:       python3-configobj
Requires:       curl
Requires:       nsis
Requires:       bind-utils
Requires:       python3-psutil >= 0.6.1
Requires:       python3-netaddr
Requires:       python3-netifaces

Provides:       /usr/sbin/pulse2-debug

%description -n pulse2-common
This package contains Pulse 2 common files like documentation.

%files -n pulse2-common
%{_sbindir}/pulse2-setup
%{_sbindir}/pulse2-load-defaults
%{_sbindir}/pulse2-dbupdate
%{_sbindir}/pulse2-debug
%{_sbindir}/restart-pulse-services
%{_sbindir}/pulse2-packageparser.py
%{_sbindir}/pulse2-inscription_packages_in_base.py
%{_sbindir}/pulse2-generation_package.py
%{_sbindir}/pulse2-migration_old_package.py
%{_sbindir}/pulse2-create-group
%{_sbindir}/medulla-generate-update-package.py
%{_sbindir}/medulla-mariadb-move-update-package.py
%{_sbindir}/medulla_mysql_exec_update.sh
%{_sbindir}/medulla_mysql_exec_uninstall_unnecessary_update_package.sh

%_docdir/pulse2/contrib/
%_datadir/mmc/conf/apache/pulse.conf
%config(noreplace) %_sysconfdir/httpd/conf.d/pulse.conf
%_var/lib/pulse2/file-transfer
#FIXME: Move on the correct package later
# Does not belong to here, lefover file.
%exclude %_sysconfdir/mmc/pulse2/atftpd/pcre.conf

# Split later in its own rpm
%python3_sitelib/pulse2/tests/test_utils.py

#--------------------------------------------------------------------

%package -n     pulse2-inventory-server
Summary:        Pulse 2 inventory server
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common = %version-%release
Requires:       python3-pulse2-common-database-inventory = %version-%release
Requires:       python3-mmc-base >= %mmc_version
Requires:       python3.11-pyOpenSSL

%description -n pulse2-inventory-server
This package contains Pulse 2 inventory server. It collects computers
inventories and insert them into the database.

%post -n pulse2-inventory-server
service pulse2-inventory-server start >/dev/null 2>&1 || :

%preun -n pulse2-inventory-server
service pulse2-inventory-server stop >/dev/null 2>&1 || :

%files -n pulse2-inventory-server
%config(noreplace) %{_sysconfdir}/mmc/pulse2/inventory-server/inventory-server.ini
%{_sysconfdir}/mmc/pulse2/inventory-server/OcsNGMap.xml
%{_sysconfdir}/mmc/pulse2/inventory-server/keys/
%{_sysconfdir}/mmc/pulse2/inventory-server/xml-fix/
%{_sbindir}/pulse2-inventory-server
%_mandir/man1/pulse2-inventory-server.1*
%python3_sitelib/pulse2/inventoryserver

#--------------------------------------------------------------------

%package -n     pulse2-package-server
Summary:        Pulse 2 package server
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common = %version-%release
Requires:       python3-mmc-core
Requires:       genisoimage
Requires:       python3.11-pyOpenSSL

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
%python3_sitelib/pulse2/package_server

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database-dyngroup
Summary:        Pulse 2 common dynamic groups database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common-database = %version-%release

Obsoletes:  python-pulse2-common-database-dyngroup < 4.7.0
Provides:   python-pulse2-common-database-dyngroup = %version-%release

%description -n python3-pulse2-common-database-dyngroup
This package contains Pulse 2 common dynamic groups database files.

%files -n python3-pulse2-common-database-dyngroup
%python3_sitelib/pulse2/database/dyngroup

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database-imaging
Summary:        Pulse 2 common imaging database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common-database = %version-%release

Obsoletes:  python-pulse2-common-database-imaging < 4.7.0
Provides:   python-pulse2-common-database-imaging= %version-%release

%description -n python3-pulse2-common-database-imaging
This package contains Pulse 2 common imaging database files

%files -n python3-pulse2-common-database-imaging
%python3_sitelib/pulse2/database/imaging

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database-inventory
Summary:        Pulse 2 common inventory database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common-database = %version-%release

Obsoletes:  python-pulse2-common-database-inventory < 4.7.0
Provides:   python-pulse2-common-database-inventory = %version-%release

%description -n python3-pulse2-common-database-inventory
This package contains Pulse 2 common inventory database files

%files -n python3-pulse2-common-database-inventory
%python3_sitelib/pulse2/database/inventory

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database-msc
Summary:        Pulse 2 common MSC database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common-database = %version-%release

Obsoletes:  python-pulse2-common-database-msc < 4.7.0
Provides:   python-pulse2-common-database-msc = %version-%release

%description -n python3-pulse2-common-database-msc
This package contains Pulse 2 common MSC database files

%files -n python3-pulse2-common-database-msc
%python3_sitelib/pulse2/database/msc

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database-admin
Summary:        Pulse 2 common admin database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common-database = %version-%release

Obsoletes:  python-pulse2-common-database-admin < 4.7.0
Provides:   python-pulse2-common-database-admin = %version-%release

%description -n python3-pulse2-common-database-admin
This package contains Pulse 2 common admin database files

%files -n python3-pulse2-common-database-admin
%python3_sitelib/pulse2/database/admin

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database-mastering
Summary:        Pulse 2 common mastering database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common-database = %version-%release

Obsoletes:  python-pulse2-common-database-mastering < 4.7.0
Provides:   python-pulse2-common-database-mastering = %version-%release

%description -n python3-pulse2-common-database-mastering
This package contains Pulse 2 common mastering database files

%files -n python3-pulse2-common-database-mastering
%python3_sitelib/pulse2/database/mastering

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database-mobile
Summary:        Pulse 2 common mobile database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common-database = %version-%release

Obsoletes:  python-pulse2-common-database-mobile < 4.7.0
Provides:   python-pulse2-common-database-mobile = %version-%release

%description -n python3-pulse2-common-database-mobile
This package contains Pulse 2 common mobile database files

%files -n python3-pulse2-common-database-mobile
%python3_sitelib/pulse2/database/mobile

#--------------------------------------------------------------------

%package -n     python3-pulse2-common-database
Summary:        Pulse 2 common database files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3-pulse2-common = %version-%release
Requires:       python3-sqlalchemy >= 0.6.3
Requires:       python3.11-mysqlclient

Obsoletes:  python-pulse2-common-database < 4.7.0
Provides:   python-pulse2-common-database = %version-%release

%description -n python3-pulse2-common-database
This package contains Pulse 2 common database files.

%files -n python3-pulse2-common-database
%python3_sitelib/pulse2/database/__init__.py
%python3_sitelib/pulse2/database/pulse/__init__.py
%python3_sitelib/pulse2/database/pulse/config.py

#--------------------------------------------------------------------

%package -n     pulse2-uuid-resolver
Summary:        Helper to resolve Pulse's UUID into IP address
Group:          System/Servers
Requires:       python3-pulse2-common = %version-%release

%description -n pulse2-uuid-resolver
This package contains a helper to resolve Pulse's UUID into IP address.

%files -n pulse2-uuid-resolver
%dir %{_sysconfdir}/mmc/pulse2/uuid-resolver
%attr(0644,root,root) %config(noreplace) %_sysconfdir/mmc/pulse2/uuid-resolver/uuid-resolver.ini
%_bindir/pulse2-uuid-resolver

#--------------------------------------------------------------------

%package -n     python3-pulse2-common
Summary:        Pulse 2 common files
Group:          System/Servers
Requires:       pulse2-common = %version-%release
Requires:       python3.11-twisted >= 2.4.0

Provides:       python3-pulse2-meta < 1.5.0
Obsoletes:      python3-pulse2-meta = %version-%release

Provides:       pulse2-common-client-apis < 1.5.0
Obsoletes:      pulse2-common-client-apis = %version-%release

Obsoletes:      python-pulse2-common < 4.7.0
Provides:       python-pulse2-common = %version-%release

%description -n python3-pulse2-common
This package contains Pulse 2 common files.

%files -n python3-pulse2-common
%python3_sitelib/pulse2/apis
%python3_sitelib/pulse2/imaging
%python3_sitelib/pulse2/managers
%python3_sitelib/pulse2/__init__.py
%python3_sitelib/pulse2/cache.py
%python3_sitelib/pulse2/consts.py
%python3_sitelib/pulse2/health.py
%python3_sitelib/pulse2/site.py
%python3_sitelib/pulse2/time_intervals.py
%python3_sitelib/pulse2/utils.py
%python3_sitelib/pulse2/version.py
%python3_sitelib/pulse2/xmlrpc.py
%python3_sitelib/pulse2/network.py

%doc %_docdir/pulse2
%doc %_docdir/medulla

#--------------------------------------------------------------------

%package -n mmc-agent
Summary:    Console agent
Group:      System/Servers
%if "%_vendor" == "Mageia"
Requires:   python3-base
Requires:   python3-OpenSSL
Requires:   python3-gobject
%else
Requires:   python3
Requires:   python3.11-pyOpenSSL
Requires:   python3.11-gobject
%endif
Requires:   python3-mmc-base
Requires:   logrotate
Requires(pre): python3-mmc-base
Requires:   python3-mmc-base
Requires:   ajax-php-file-manager
Requires:   python3-memory-profiler
Requires:   python3-posix-ipc
Requires:   python3.11-pyyaml
Requires:   python3.11-incremental
Requires:   python3.11-typing-extensions
Requires:   python3.11-zope-interface
Requires:   python3.11-constantly
Requires:   python3.11-hyperlink
Requires:   python3.11-sqlalchemy
Requires:   python3.11-configobj
Requires:   python3.11-pycryptodomex
Requires:   python3.11-magic
Requires:   python3.11-distro

%description -n mmc-agent
XMLRPC server of the Console API.
This is the underlying service used by the MMC web interface.

%files -n mmc-agent
%defattr(-,root,root,0755)
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
%dir %{python3_sitelib}/mmc
%{python3_sitelib}/mmc/agent.py*
%{python3_sitelib}/mmc/utils.py*
%{_docdir}/pulse2/contrib/monit/mmc-agent
%{_datadir}/mmc/providers.php

#--------------------------------------------------------------------

%package -n python3-mmc-core
Summary:    Console core
Group:      System/Servers
%if "%_vendor" == "Mageia"
Requires:   python3-base
%else
Requires:   python3.11
%endif
Requires:   python3.11-twisted

Obsoletes:  python-mmc-core < 4.7.0
Provides:   python-mmc-core = %version-%release

%description -n python3-mmc-core
Contains the mmc core python classes used by all other
modules.

%files -n python3-mmc-core
%defattr(-,root,root,0755)
%dir %{python3_sitelib}/mmc
%{python3_sitelib}/mmc/core
%{python3_sitelib}/mmc/support
%{python3_sitelib}/mmc/__init__.py*
%{python3_sitelib}/mmc/site.py*
%{python3_sitelib}/mmc/ssl.py*
%{python3_sitelib}/mmc/client
%dir %{python3_sitelib}/mmc/plugins
%{python3_sitelib}/mmc/plugins/__init__.py*

%{_docdir}/pulse2/contrib/audit

#--------------------------------------------------------------------

%package -n	    python3-mmc-base
Summary:	    Console base plugin
Group:      	System/Servers
%if "%_vendor" == "Mageia"
Requires:       python3-base
%else
Requires:       python3.11
%endif
Requires:  	python3-ldap
Requires:   	python3-mmc-plugins-tools
Requires:   	python3-mmc-core
Requires:   	python3-mmc-dashboard >= %{version}

Obsoletes:  python-mmc-base < 4.7.0
Provides:   python-mmc-base = %version-%release

%description -n	python3-mmc-base
Contains the base infrastructure for all MMC plugins:
 * support classes
 * base LDAP management classes

%post -n python3-mmc-base
sed -i 's!%%(basedn)s!%%(baseDN)s!g' %{_sysconfdir}/mmc/plugins/base.ini

%files -n python3-mmc-base
%defattr(-,root,root,0755)
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/plugins
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/base.ini
%attr(0755,root,root) %{_sbindir}/mds-report
%dir %{python3_sitelib}/mmc
%dir %{python3_sitelib}/mmc/plugins
%{python3_sitelib}/mmc/plugins/base
%{_docdir}/pulse2/contrib/base
%{_docdir}/pulse2/contrib/scripts/usertoken-example
%{_docdir}/pulse2/contrib/scripts/mmc-check-users-primary-group
%exclude %{python3_sitelib}/mmc/plugins/report

#--------------------------------------------------------------------

%package -n python3-mmc-ppolicy
Summary:    Console password policy plugin
Group:      System/Servers
%if "%_vendor" == "Mageia"
Requires:       python3-base
%else
Requires:       python3.11
%endif
Requires:   python3-mmc-core

Obsoletes:  python-mmc-ppolicy < 4.7.0
Provides:   python-mmc-ppolicy = %version-%release

%description -n python3-mmc-ppolicy
Contains the password policy python classes to handle
password policies in LDAP.

%files -n python3-mmc-ppolicy
%defattr(-,root,root,0755)
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/plugins
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/ppolicy.ini
%dir %{python3_sitelib}/mmc
%dir %{python3_sitelib}/mmc/plugins
%{python3_sitelib}/mmc/plugins/ppolicy
%{_docdir}/pulse2/contrib/ppolicy
%{_docdir}/pulse2/contrib/scripts/mmc-check-expired-passwords-example

#--------------------------------------------------------------------

%package -n python3-mmc-dashboard
Summary:    Console dashboard plugin
Group:      System/Servers
%if "%_vendor" == "Mageia"
Requires:   python3-base
%else
Requires:   python3.11
%endif
Requires:   python3-mmc-base >= %{version}
Requires:   python3-psutil >= 0.6.1
Requires:   python3-distro

Obsoletes:  python-mmc-dashboard < 4.7.0
Provides:   python-mmc-dashboard = %version-%release

%description -n python3-mmc-dashboard
Console dashboard plugin

%files -n python3-mmc-dashboard
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/dashboard.ini
%{python3_sitelib}/mmc/plugins/dashboard

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

%package -n python3-mmc-services
Summary:    Console services plugin
Group:      System/Servers
%if "%_vendor" == "Mageia"
Requires:   python3-base
%else
Requires:   python3.11
%endif
Requires:   python3-mmc-base >= %{version}
Requires:   python3-systemd-dbus
Requires:   python3-dbus

Obsoletes:  python-mmc-services < 4.7.0
Provides:   python-mmc-services = %version-%release

%description -n python3-mmc-services
Console services plugin

%files -n python3-mmc-services
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/services.ini
%{python3_sitelib}/mmc/plugins/services

%post -n python3-mmc-services
%if "%_vendor" == "Mageia"
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
%if "%_vendor" == "Mageia"
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
Requires:       openid-connect-php
Requires:       php-phpseclib3

%description -n mmc-web-base
Console web interface.

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
%{_datadir}/mmc/forgotpassword.php
%{_datadir}/mmc/license.php
%{_datadir}/mmc/logout/index.php
%{_datadir}/mmc/main.php
%{_datadir}/mmc/site.php
%{_datadir}/mmc/token.php
%{_datadir}/mmc/version.php
%{_datadir}/mmc/demobanner.php
%{_datadir}/mmc/graph/
%{_datadir}/mmc/img/
%{_datadir}/mmc/includes/
%{_datadir}/mmc/index.php
%{_datadir}/mmc/jsframework/
%{_datadir}/mmc/modules/base/
%{_datadir}/mmc/modules/xmppmaster/

#--------------------------------------------------------------------

%package -n	python3-mmc-plugins-tools
Summary:	Required tools for some MMC plugins
Group:		System/Servers
%if "%_vendor" == "Mageia"
Requires:	cdrkit-genisoimage
%else
Requires:       genisoimage
%endif

Obsoletes:  python-mmc-plugins-tools < 4.7.0
Provides:   python-mmc-plugins-tools = %version-%release

%description -n	python3-mmc-plugins-tools
Contains common tools needed by some plugins of mmc-agent package.

%files -n python3-mmc-plugins-tools
%defattr(-,root,root,0755)
%dir %{_libdir}/mmc
%dir %{_libdir}/mmc/backup-tools
%{_libdir}/mmc/backup-tools/cdlist
%{_libdir}/mmc/backup-tools/backup.sh

#--------------------------------------------------------------------

%if %with_report
%package -n python3-mmc-report
Summary:    Console report plugin
Group:      System/Servers
%if "%_vendor" == "Mageia"
Requires:   python3-base
%else
Requires:   python3.11
%endif
Requires:   python3-mmc-base >= %{version}
Requires:   python3-psutil >= 0.6.1
Requires:   python3-xlwt
Requires:   python3-weasyprint

Obsoletes:  python-mmc-report < 4.7.0
Provides:   python-mmc-report = %version-%release

%description -n python3-mmc-report
Console report plugin

%files -n python3-mmc-report
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/report.ini
%{_sysconfdir}/mmc/plugins/report
%{python3_sitelib}/mmc/plugins/report
%{_docdir}/pulse2/contrib/report

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

%package -n     mmc-web-admin
Summary:        Admin module for the MMC web interface
Group:          System/Servers
Requires:       mmc-web-base >= %{version}

%description -n mmc-web-admin
Admin module for the MMC web interface

%files -n mmc-web-admin
%{_datadir}/mmc/modules/admin


#--------------------------------------------------------------------

%package -n python3-mmc-mastering
Summary:    Mastering plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-pulse2-common-database-mastering = %version-%release

Obsoletes:  python-mmc-mastering < 4.7.0
Provides:   python-mmc-mastering = %version-%release

%description -n python3-mmc-mastering
This package contains the mastering plugin for the MMC agent.

%files -n python3-mmc-mastering
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/mastering.ini
%python3_sitelib/mmc/plugins/mastering
%{_docdir}/pulse2/contrib/mastering

#--------------------------------------------------------------------

%package -n     mmc-web-mastering
Summary:        Mastering module for the MMC web interface
Group:          System/Servers
Requires:       mmc-web-base >= %{version}

%description -n mmc-web-mastering
Mastering module for the MMC web interface

%files -n mmc-web-mastering
%{_datadir}/mmc/modules/mastering

#--------------------------------------------------------------------

%package -n python3-mmc-mobile
Summary:    Mobile plugin for the MMC agent
Group:      System/Servers
Requires:   pulse2-common = %version-%release
Requires:   python3-pulse2-common-database-mobile = %version-%release

Obsoletes:  python-mmc-mobile < 4.7.0
Provides:   python-mmc-mobile = %version-%release

%description -n python3-mmc-mobile
This package contains the mobile plugin for the MMC agent.

%files -n python3-mmc-mobile
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/mobile.ini
%python3_sitelib/mmc/plugins/mobile
%{_docdir}/pulse2/contrib/mobile

#--------------------------------------------------------------------

%package -n     mmc-web-mobile
Summary:        Mobile module for the MMC web interface
Group:          System/Servers
Requires:       mmc-web-base >= %{version}

%description -n mmc-web-mobile
Mobile module for the MMC web interface

%files -n mmc-web-mobile
%{_datadir}/mmc/modules/mobile

#--------------------------------------------------------------------

%package -n     python3-mmc-database
Summary:        Console database common files
Group:          System/Servers
Requires:       python3-mmc-base = %version-%release
Requires:       python3-sqlalchemy >= 0.6.3
%if "%_vendor" == "Mageia"
Requires:       python3-mysql
%else
Requires:       python3.11-mysqlclient
%endif

Obsoletes:  python-mmc-database < 4.7.0
Provides:   python-mmc-database = %version-%release

%description -n python3-mmc-database
Console database common files
Allow the use of SQL databases within MMC framework.

%files -n python3-mmc-database
%{python3_sitelib}/mmc/database
%endif

#--------------------------------------------------------------------

%prep
%setup -q  -n medulla-%version
sed -e 's/python python2 //' -i configure

%build

%configure2_5x --disable-python-check

%make_build

%install
%makeinstall

mkdir -p %buildroot%{_sbindir}

mkdir -p %buildroot%_var/lib/pulse2/packages

rm -rf %buildroot%{_sysconfdir}/init.d/pulse2-imaging-server

mkdir -p %buildroot%_prefix/lib/systemd/system

#cp %{SOURCE2} %buildroot%_prefix/lib/systemd/system
cp %{SOURCE3} %buildroot%_prefix/lib/systemd/system
cp %{SOURCE4} %buildroot%_prefix/lib/systemd/system

mkdir -p %buildroot%_sysconfdir/httpd/conf.d/
cp -fv %buildroot%_datadir/mmc/conf/apache/pulse.conf %buildroot%_sysconfdir/httpd/conf.d/

mkdir -p %buildroot%_var/lib/pulse2/file-transfer

cp services/contrib/glpi-92.sql %buildroot%_datadir/doc/pulse2/contrib/
cp services/contrib/glpi-94.sql %buildroot%_datadir/doc/pulse2/contrib/
cp services/contrib/glpi-95.sql %buildroot%_datadir/doc/pulse2/contrib/

rm -f %buildroot%python3_sitelib/pulse2/apis/clients/mirror.py
mv %buildroot%python3_sitelib/pulse2/apis/clients/mirror1.py %buildroot%python3_sitelib/pulse2/apis/clients/mirror.py

rm -f %buildroot%python3_sitelib/pulse2/apis/clients/mirror_api.py
mv %buildroot%python3_sitelib/pulse2/apis/clients/mirror_api1.py %buildroot%python3_sitelib/pulse2/apis/clients/mirror_api.py

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
find '%{buildroot}' -name '*.pyc' -o -name '*.pyo' | xargs rm -fv
rm -fv %buildroot%_sysconfdir/init.d/pulse2-cm
rm -fv %buildroot%_sysconfdir/init.d/pulse2-scheduler
