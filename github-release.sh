#!/bin/bash

VERSION=$(cat nginx-version)
USER="fabregas4you"
REPO="nginx-build"
DATE=`date +%Y%m%d%H%M`

# create release
github-release release \
  --user $USER \
  --repo $REPO \
  --tag $VERSION \
  --name "NGINX-$VERSION" \
  --description "release $DATE"

# upload files
echo "Custom NGINX Build with ModSecurity" >> description.md
echo "" >> description.md
for i in $(ls -1 *.rpm)
do
  echo "* $i" >> description.md
  echo "  * $(openssl sha256 $i)" >> description.md
  github-release upload --user $USER \
    --repo $REPO \
    --tag $VERSION \
    --name "$i" \
    --file $i
done

# edit description
github-release edit \
  --user $USER \
  --repo $REPO \
  --tag $VERSION \
  --description "$(cat description.md)"
