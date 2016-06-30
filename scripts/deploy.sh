#!/bin/bash
eval "$(ssh-agent -s)" # Start the ssh agent
echo "`ls -la scripts/`"
chmod 600 scripts/travis.key # This key should have push access
scp -i scripts/travis.key -o StrictHostKeyChecking=no skyscrapers-monitoring-plugins_*_all.deb travis@puppetmaster02.int.skyscrape.rs:
ssh -i scripts/travis.key -o StrictHostKeyChecking=no travis@repo02.int.skyscrape.rs "sudo aptly repo add skyscrapers skyscrapers-monitoring-plugins_*_all.deb;aptly publish update -gpg-key=\"74AD2F75\" skyscrapers s3:repo.int.skyscrape.rs; rm ./skyscrapers-monitoring-plugins_*_all.deb"
rm scripts/travis.key
