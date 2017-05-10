%define  nginx_user          nginx
%define  nginx_group         nginx
%define  nginx_home          %{_localstatedir}/lib/nginx
%define  nginx_home_tmp      %{nginx_home}/tmp
%define  nginx_confdir       %{_sysconfdir}/nginx
%define  nginx_datadir       %{_datadir}/nginx
%define  nginx_logdir        %{_localstatedir}/log/nginx
%define  nginx_webroot       %{nginx_datadir}/html
%define  openssl_version     1.0.2k

Name:              nginx
Epoch:             1
Version:           1.12.0
Release:           1%{?dist}
Summary:           A high performance web server and reverse proxy server
Group:             System Environment/Daemons
License:           BSD
URL:               http://nginx.org/
Source0:           http://nginx.org/download/%{name}-%{version}.tar.gz
Source1:           https://github.com/SpiderLabs/ModSecurity-nginx.git
Source10:          nginx.service
Source11:          logrotate
Source12:          nginx.conf
Source15:          nginx.init
Source16:          nginx.sysconf
Source20:          https://www.openssl.org/source/openssl-%{openssl_version}.tar.gz

# BuildRequires:     GeoIP-dGevel
# BuildRequires:     gd-devel
# BuildRequires:     perl-devel
# BuildRequires:     perl(ExtUtils::Embed)
BuildRequires:     libxslt-devel
BuildRequires:     openssl-devel >= 1.0.2
BuildRequires:     pcre-devel
BuildRequires:     zlib-devel
# Requires:          GeoIP
# Requires:          gd
# Requires:          perl(:MODULE_COMPAT_%(eval &quot;<code>%{__perl} -V:version</code>&quot;; echo $version))
Requires:          openssl >= 1.0.2
Requires:          pcre
Requires(pre):     shadow-utils
Provides:          webserver
 
Requires(post):    chkconfig
Requires(preun):   chkconfig, initscripts
Requires(postun):  initscripts

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%prep
git clone %{SOURCE1}
# tar zxvf %{SOURCE20}
%setup -q -D -a 20

./configure \
        --prefix=%{_sysconfdir}/nginx/ \
        --conf-path=%{_sysconfdir}/nginx/nginx.conf \
        --pid-path=%{_localstatedir}/run/%{name}.pid \
        --lock-path=%{_localstatedir}/lock/subsys/%{name} \
        --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp \
        --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp \
        --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp \
        --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp \
        --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp \
        --user=%{nginx_user} \
        --group=%{nginx_group} \
        --with-threads \
        --with-http_ssl_module \
        --with-http_realip_module \
        --with-http_addition_module \
        --with-http_sub_module \
        --with-http_gzip_static_module \
        --with-http_random_index_module \
        --with-http_secure_link_module \
        --with-http_stub_status_module \
        --with-mail \
        --with-mail_ssl_module \
        --with-file-aio \
        --with-debug \
        --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
        --with-openssl=%{_soucedir}/openssl-1.0.2k/
        $*
make %{?_smp_mflags}
%{__mv} %{_builddir}/%{name}-%{version}/objs/nginx \
        %{_builddir}/%{name}-%{version}/objs/nginx.debug

nstall
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor

find %{buildroot} -type f -name .packlist -exec rm -f '{}' \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f '{}' \;
find %{buildroot} -type f -empty -exec rm -f '{}' \;
find %{buildroot} -type f -iname '*.so' -exec chmod 0755 '{}' \;

install -p -D -m 0755 %{SOURCE15} \
    %{buildroot}%{_initddir}/nginx
install -p -D -m 0644 %{SOURCE16} \
    %{buildroot}%{_sysconfdir}/sysconfig/nginx
 
install -p -D -m 0644 %{SOURCE11} \
    %{buildroot}%{_sysconfdir}/logrotate.d/nginx
 
install -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
install -p -d -m 0700 %{buildroot}%{nginx_home}
install -p -d -m 0700 %{buildroot}%{nginx_home_tmp}
install -p -d -m 0700 %{buildroot}%{nginx_logdir}
install -p -d -m 0755 %{buildroot}%{nginx_webroot}
 
install -p -m 0644 %{SOURCE12} \
    %{buildroot}%{nginx_confdir}
rm -fr %{buildroot}%{_prefix}/html
 
install -p -D -m 0644 %{_builddir}/nginx-%{version}/man/nginx.8 \
    %{buildroot}%{_mandir}/man8/nginx.8

%pre
getent group %{nginx_group} &gt; /dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} &gt; /dev/null || \
    useradd -r -d %{nginx_home} -g %{nginx_group} \
    -s /sbin/nologin -c &quot;Nginx web server&quot; %{nginx_user}
exit 0
 
%post
if [ $1 -eq 1 ]; then
    /sbin/chkconfig --add %{name}
fi
if [ $1 -eq 2 ]; then
    # Make sure these directories are not world readable.
    chmod 770 %{nginx_home}
    chmod 770 %{nginx_home_tmp}
    chmod 770 %{nginx_logdir}
fi
 
%preun
if [ $1 -eq 0 ]; then
    /sbin/service %{name} stop &gt;/dev/null 2&gt;&amp;1
    /sbin/chkconfig --del %{name}
fi
 
%postun
if [ $1 -eq 2 ]; then
    /sbin/service %{name} upgrade || :
fi

%files
%doc LICENSE CHANGES README
%{_initddir}/nginx
%config(noreplace) %{_sysconfdir}/sysconfig/nginx
%{nginx_datadir}/
%{_sbindir}/nginx
%{_mandir}/man3/nginx.3pm*
%{_mandir}/man8/nginx.8*
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/nginx.conf
%config(noreplace) %{nginx_confdir}/nginx.conf.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/conf.d/virtual.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%dir %{perl_vendorarch}/auto/nginx
%{perl_vendorarch}/nginx.pm
%{perl_vendorarch}/auto/nginx/nginx.so
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
%attr(700,%{nginx_user},%{nginx_group}) %dir %{nginx_logdir}
 
%changelog
* Wed May 10 2017 shinichi fukuda &lt;s-fukuda@iij.ad.jp&gt; - 1.12.0-1
