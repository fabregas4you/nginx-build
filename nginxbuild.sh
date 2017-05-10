#!/bin/env bash
HOME=/var/tmp
NGINX_VERSION=$(cat nginx-version)

if [ -z "$NGINX_VERSION" ]; then
  echo "required nginx-version file."
  exit 1
fi

# cd $HOME/rpmbuild/SOURCES && curl -LO http://cache.ruby-lang.org/pub/ruby/$(echo $RUBY_VERSION | sed -e 's/\.[0-9]$//')/ruby-$RUBY_VERSION.tar.gz
cd $HOME/rpmbuild/SOURCES && curl -LO http://nginx.org/download/nginx-$NGINX_VERSION.tar.gz

rpmbuild -ba $HOME/rpmbuild/SPECS/nginx1x.spec

cp $HOME/rpmbuild/RPMS/x86_64/* /shared/
cp $HOME/rpmbuild/SRPMS/* /shared/
