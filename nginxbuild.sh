#!/bin/env bash
HOME=/var/tmp
NGINX_VERSION=$(cat nginx-version)
OPENSSL_VERSION=$(cat openssl-version)
V_FILES="nginx-version openssl-version"

if [ -z "$NGINX_VERSION" -a -z "$OPENSSL_VERSION" ]; then
  echo "required nginx-version and openssl-version file."
  exit 1
fi

# cd $HOME/rpmbuild/SOURCES && curl -LO http://cache.ruby-lang.org/pub/ruby/$(echo $RUBY_VERSION | sed -e 's/\.[0-9]$//')/ruby-$RUBY_VERSION.tar.gz
cd $HOME/rpmbuild/SOURCES && curl -LO http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz && \
curl -LO https://www.openssl.org/source/openssl-$OPENSSL_VERSION.tar.gz && \
git clone https://github.com/SpiderLabs/ModSecurity.git mod_security && \
cd mod_security && ./autogen.sh && ./configure --enable-standalone-module ; make

cd $HOME
echo $V_FILES
cp $V_FILES $HOME/rpmbuild/SOURCES && \
rpmbuild -ba $HOME/rpmbuild/SPECS/nginx1x.spec

cp $HOME/rpmbuild/RPMS/x86_64/* /shared/
# cp $HOME/rpmbuild/SRPMS/* /shared/
