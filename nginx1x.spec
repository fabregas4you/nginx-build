%define  nginx_user          nobody
%define  nginx_group         nobody
%define  nginx_ver           %(cat /var/tmp/rpmbuild/nginx-version)
%define  nginx_home          /opt/nginx
%define  nginx_conf          %{nginx_home}/conf
%define  nginx_ssl           %{nginx_home}/ssl
%define  nginx_etc           %{nginx_home}/etc
%define  nginx_data          %{nginx_home}/data
%define  nginx_logs          %{nginx_home}/logs
%define  nginx_webroot       %{nginx_data}/html
# %define  openssl_version     1.0.2k
%define  openssl_version     %(cat /var/tmp/rpmbuild/openssl-version)
%define  ModSecurity_nginx   %{_sourcedir}/mod_security/nginx/modsecurity

Name:              nginx
# Version:           1.12.0
Version:           %{nginx_ver} 
Release:           0%{?dist}
Summary:           A high performance web server and reverse proxy server
Group:             System Environment/Daemons
License:           MIT
URL:               http://nginx.org/
Source0:           http://nginx.org/download/%{name}-%{version}.tar.gz
# Source1:           https://github.com/SpiderLabs/ModSecurity-nginx.git
Source10:          nginx.service
Source11:          logrotate
Source12:          nginx.conf
Source15:          nginx.init
Source16:          nginx.sysconfig
Source20:          https://www.openssl.org/source/openssl-%{openssl_version}.tar.gz

# BuildRoot:         %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)
BuildRoot:         %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:     libxslt-devel
# BuildRequires:     openssl-devel >= 1.0.2
BuildRequires:     openssl-devel
BuildRequires:     pcre-devel
BuildRequires:     zlib-devel
# Requires:          openssl >= 1.0.2
Requires:          openssl
Requires:          pcre
Requires(pre):     shadow-utils
Provides:          webserver
 
Requires(post):    chkconfig
Requires(preun):   chkconfig, initscripts
Requires(postun):  initscripts

%description
UOM Multi-Domain Proxy

%prep
# %setup -q -D -a 20
%setup -q -D -b 20

%build
export DESTDIR=%{buildroot}

./configure \
        --prefix=%{nginx_home} \
        --conf-path=%{nginx_home}/nginx.conf \
        --pid-path=/var/run/%{name}.pid \
        --lock-path=/var/lock/subsys/%{name} \
        --user=%{nginx_user} \
        --group=%{nginx_group} \
        --with-threads \
        --with-select_module \
        --with-poll_module \
        --with-http_ssl_module \
        --with-http_realip_module \
        --with-http_addition_module \
        --with-http_sub_module \
        --with-http_gzip_static_module \
        --with-http_random_index_module \
        --with-http_secure_link_module \
        --with-http_stub_status_module \
        --with-http_degradation_module \
        --with-mail \
        --with-mail_ssl_module \
        --with-file-aio \
        --with-debug \
        --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
        --add-module=%{ModSecurity_nginx} \
        --with-openssl=%{_builddir}/openssl-%{openssl_version}
        $*
make %{?_smp_mflags}
%{__mv} %{_builddir}/%{name}-%{version}/objs/nginx \
        %{_builddir}/%{name}-%{version}/objs/nginx.debug

%install
# make install DESTDIR=%{buildroot} INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f '{}' \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f '{}' \;
find %{buildroot} -type f -empty -exec rm -f '{}' \;
find %{buildroot} -type f -iname '*.so' -exec chmod 0755 '{}' \;

install -p -d -m 0750 %{buildroot}%{nginx_home}
install -p -d -m 0750 %{buildroot}%{nginx_conf}
install -p -d -m 0750 %{buildroot}%{nginx_confd}
install -p -d -m 0750 %{buildroot}%{nginx_ssl}
install -p -d -m 0750 %{buildroot}%{nginx_etc}
install -p -d -m 0750 %{buildroot}%{nginx_data}
install -p -d -m 0750 %{buildroot}%{nginx_logs}
install -p -d -m 0750 %{buildroot}%{nginx_webroot}
install -p -D -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/logrotate.d/nginx

%if 0%{?centos} <= 6
install -p -D -m 0755 %{SOURCE15} %{buildroot}/%{_sysconfdir}/init.d/nginx
install -p -D -m 0644 %{SOURCE16} %{buildroot}/%{_sysconfdir}/sysconfig/nginx
%else
install -p -m 0755 %{SOURCE10} ${buildroot}/usr/lib/systemd/system/nginx.service
%endif

make install DESTDIR=${RPM_BUILD_ROOT} INSTALL="install -p"
install -d ${RPM_BUILD_ROOT}/%{nginx_home}/logs
install -d ${RPM_BUILD_ROOT}/%{nginx_home}/cache
install -d ${RPM_BUILD_ROOT}/%{nginx_home}/conf/customers
install -d ${RPM_BUILD_ROOT}/%{nginx_home}/conf/upstreams
install -d ${RPM_BUILD_ROOT}/%{nginx_home}/ssl/key
install -d ${RPM_BUILD_ROOT}/%{nginx_home}/ssl/crt

if [ -f ${RPM_BUILD_ROOT}/%{nginx_home}/conf/nginx.conf ]; then
  rm -f ${RPM_BUILD_ROOT}/%{nginx_home}/conf/nginx.conf
fi

%clean

%pre
if [ $1 = 0 ]; then
getent group %{nginx_group} &gt; /dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} &gt; /dev/null || \
    useradd -r -d %{nginx_home} -g %{nginx_group} \
    -s /sbin/nologin -c &quot;Nginx web server&quot; %{nginx_user}
# exit 0
fi

if [ -f %{nginx_home}/sbin/nginx ] ; then
  mv %{nginx_home}/sbin/nginx %{nginx_home}/sbin/nginx.old
fi
 
%post
%if 0%{?centos} <= 6
    /sbin/chkconfig --add %{name}
%else
    /usr/bin/systemctl enable nginx.service
%endif
 
%preun
%if 0%{?centos} <= 6
if [ $1 -eq 0 ]; then
   /sbin/service %{name} stop
   /sbin/chkconfig --del %{name}
fi
%else
if [ $1 = 0 ]; then
   /usr/bin/systemctl stop nginx.service
   /usr/bin/systemctl disable nginx.service
fi
%endif
 
%postun

%files
%defattr(-,root,root,-)
%doc LICENSE CHANGES README
# %config(noreplace) %{nginx_home}/conf/*

%if 0%{?centos} <= 6
%config(noreplace) /etc/sysconfig/nginx
%config(noreplace) /etc/logrotate.d/nginx
%endif

%config(noreplace) %{nginx_home}/*
# %{nginx_home}/sbin/nginx
# %{nginx_home}/html/*
# %{nginx_home}/logs
# %{nginx_home}/cache
# %{nginx_home}/ssl/crt
# %{nginx_home}/ssl/key

%if 0%{?centos} <= 6
  /etc/init.d/nginx
%else
  /usr/lib/systemd/system/nginx.service
%endif

%attr(750,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(750,%{nginx_user},%{nginx_group}) %dir %{nginx_logs}

%changelog
