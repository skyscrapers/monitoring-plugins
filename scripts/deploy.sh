#!/bin/bash
eval "$(ssh-agent -s)" # Start the ssh agent
echo "`sudo ls -la `"
chmod 600 travis.key # This key should have push access
scp -i travis.key -o StrictHostKeyChecking=no skyscrapers-monitoring-plugins_*_all.deb travis@repo02.int.skyscrape.rs:
ssh -i travis.key -o StrictHostKeyChecking=no travis@repo02.int.skyscrape.rs "sudo /aptly/travis_update.sh"
rm travis.key
