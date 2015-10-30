#!/bin/bash

VERSION=1.2.1

rm -rf *.deb

chmod 755 check_*

fpm -s dir -t deb -n skyscrapers-monitoring-plugins -v ${VERSION} -a all \
  --description "Monitoring plugins that Skyscrapers uses" \
  -x "**/.git/**" -x "**/README.md" -x "**/LICENSE" -x "**/.git" -x "**/build.sh" \
  .=/usr/lib/nagios/plugins
