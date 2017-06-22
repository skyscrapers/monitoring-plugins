#!/bin/bash

VERSION=1.3.45

rm -rf *.deb

chmod 755 check_*

fpm -s dir -t deb -n skyscrapers-monitoring-plugins -v ${VERSION} -a all \
  --description "Monitoring plugins that Skyscrapers uses" \
  -x "**/.git/**" -x "**/README.md" -x "**/LICENSE" -x "**/.git" -x "**/build.sh" \
  -x "**/build" -x "**/dist" -x "**/scripts" -x "**/tests" \
  -x "**/skymonitoringplugins.egg-info" -x "**/.tox"\
  -x "*build*.sh" \
  -x "**/Docker*" \
  -x "**/.project" \
  -x "**/tox.ini" \
  -x "**/circle*" \
  -x "**/git*" \
  -x "**/*.pyc" \
  -x "**/*.py~" \
  .=/usr/lib/nagios/plugins
