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
%define version                4.0

Summary:	Management Console
Name:		mmc-core
Version:	%{version}
%if %use_git
Release:        0.%git.1%{?dist}
%else
Release:        5%{?dist}
%endif
License:	GPL
Group:		System/Servers
URL:		https://github.com/pulse-project/pulse
Source0:        %{name}-%{version}.tar.gz
Source1:        output.py
Source2:        get_file.php
Patch1:         0001-Add-pre-post-deluser-hooks.patch
Patch2:         mmc-core-3.1.85-remove-startwith.patch
BuildRequires:	python-devel
BuildRequires:	gettext
BuildRequires:	gettext-devel

%description
Console agent & web interface with base and password policies modules.

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

%description -n mmc-agent
XMLRPC server of the Console API.
This is the underlying service used by the MMC web interface.

%post -n mmc-agent
# Workaround segfaults in the services plugin
# https://qa.mandriva.com/show_bug.cgi?id=66109
sed -i 's/^#multithreading = 1/multithreading = 0/' %{_sysconfdir}/mmc/agent/config.ini
%if %_vendor == "Mageia"
%_post_service mmc-agent
%else
service mmc-agent start >/dev/null 2>&1 || :
%endif

%preun -n mmc-agent
# Stop mmc-agent on uninstall
if [ $1 -eq 0 ]; then
   %if %_vendor == "Mageia"
       %_preun_service mmc-agent
   %else
       service mmc-agent stop >/dev/null 2>&1 || :
   %endif
fi

# Filetriggers to restart mmc-agent if a new module is installed.
%transfiletriggerin -n mmc-agent --  %{py_puresitedir}/mmc
[ -z \$MMC_AGENT ] && service mmc-agent restart


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

%description -n mmc-web-base
Console web interface designed by Linbox.

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
%setup -q -n %{name}-%{version}

cp %{SOURCE1}   agent/mmc/plugins/base
cp %{SOURCE2}   web/modules/base/computers
   
%build
%configure2_5x --disable-python-check --with-systemddir=%{_unitdir} --enable-systemd

%make

%install
%makeinstall_std

# logrotate configuration
install -d %{buildroot}%{_sysconfdir}/logrotate.d

# install log rotation stuff
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

# Cleanup
rm -f `find %{buildroot} -name *.pyo`
