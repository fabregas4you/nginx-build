#!/bin/env bash
HOME=/var/tmp
NGINX_VERSION=$(cat nginx-version)
OPENSSL_VERSION=$(cat openssl-version)
V_FILES="nginx-version openssl-version"
_CFLAGS="-DDEFAULT_USER=\\\"nobody\\\" -DDEFAULT_GROUP=\\\"nobody\\\""
_CPPFLAGS="-I/usr/include/apr-1 -I/usr/include/httpd"

if [ -z "$NGINX_VERSION" -a -z "$OPENSSL_VERSION" ]; then
  echo "required nginx-version and openssl-version file."
  exit 1
fi

cd $HOME/rpmbuild/SOURCES && curl -LO http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz && \
curl -LO https://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz && \
git clone https://github.com/SpiderLabs/ModSecurity.git mod_security && \
cd mod_security && ./autogen.sh && CFLAGS=$_CFLAGS CPPFLAGS=$_CPPFLAGS \
./configure --enable-standalone-module ; make

rpmbuild -ba $HOME/rpmbuild/SPECS/nginx1x.spec

cp $HOME/rpmbuild/RPMS/x86_64/* /shared/
cp $HOME/rpmbuild/SRPMS/* /shared/
