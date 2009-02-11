%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

Summary:	MMC web interface to interact with a MMC agent
Name:		mmc-web-base
Version:	2.3.1
Release:	1.RHEL4
License:	GPL
Group:		System/Servers
URL:		http://mds.mandriva.org/
Source0:	%{name}-%{version}.tar.gz
Patch0:		mmc-web-base-Makefile_fix.diff
Requires:	httpd >= 2.0.52
Requires:	php-xmlrpc
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Mandriva Management Console web interface designed by Linbox.

%prep

%setup -q -n %{name}-%{version}

for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

%patch0 -p0

%build

%install
rm -rf %{buildroot}

make DESTDIR=%{buildroot} install

install -d %{buildroot}%{_sysconfdir}/httpd/conf.d

cat > %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf << EOF

Alias /mmc %{_datadir}/mmc

<Directory "%{_datadir}/mmc">
    AllowOverride None
    Order allow,deny
    allow from all
    php_flag short_open_tag on
</Directory>

EOF

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart >/dev/null || :
fi
    
%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart >/dev/null || :
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%doc COPYING Changelog
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%attr(0640,root,apache) %config(noreplace) %{_sysconfdir}/mmc/mmc.ini
%{_datadir}/mmc/*

%changelog
* Tue May 20 2008  <cdelfosse@mandriva.com> - 2.3.1-1.RHEL4
- new upstream release

* Fri Jan 18 2008 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-1.RHEL4
- initial Redhat RHEL4 package.
