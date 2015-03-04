monitoring-plugins
==================

Monitoring (Nagios) plugins that Skyscrapers uses.

## Requirements

- Ruby + Ruby-dev
- FPM
- Ruby (for FPM)

## Usage

```
apt-get install ruby-dev
gem install fpm
./build.sh
```

## Plugins

- check_apachestatus_auto.pl
- check_autoscalegroup.py
- check_awsLaunchconf.py
- check_clamscansites
- check_cloudwatch.py
- check_couchdb
- check_dir
- check_elasticsearch
- check_elb.py
- check_elb_registration
- check_file_ages_in_dirs
- check_file_content.pl
- check_freshclam
- check_md_raid
- check_mount
- check_nginx
- check_phy_raid
- check_pid
- check_postfix_problems
- check_postfix_queue
- check_postgres.pl
- check_puppet
- check_reboot
- check_redis.pl
- check_ro_mounts
- check_shorewall
- check_shorewall6
- check_ssl_certificate
- check_succes_bacula
- check_supervisorctl.sh
