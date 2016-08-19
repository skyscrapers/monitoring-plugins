monitoring-plugins
==================

Monitoring (Nagios) plugins that Skyscrapers uses.

## Requirements

- Ruby + Ruby-dev
- FPM
- Ruby (for FPM)

In case of docker run it is only needed Docker.

## Usage
If you want to test the build locally you can run the following commands:
```
apt-get install ruby-dev
gem install fpm
./scripts/build.sh
```

Once you are happy with the packages you want to add change the version in scripts/build.sh and push the code.
The code will be automatically build and pushed by travis-ci
### Usage with docker

```
./build-docker.sh
```

### Test framework

For new developments tox/nosetests is setup. Test can be added to /test folder

Run the test
```
./build-test-docker.sh
```


## Plugins

- check_apachestatus_auto.pl
- check_autoscalegroup.py
- check_awsLaunchconf.py
- check_cassandra.pl
- check_cassandra_cluster.sh
- check_clamscansites
- check_cloudwatch.py
- check_couchdb
- check_couchbase.py
- check_couchbase_buckets.py (https://github.com/ebruAkagunduz/nagios-plugin-couchbase)
- check_cpu_stats.sh (https://exchange.nagios.org/directory/Plugins/System-Metrics/CPU-Usage-and-Load/check_cpu_stats-2Esh/details)
- check_dir
- check_elasticsearch
- check_elasticsearch_snapshot.py
- check_elb.py
- check_elb_registration
- check_file_ages_in_dirs
- check_file_content.pl
- check_freshclam
- check_md_raid
- check_memory (https://exchange.icinga.org/exchange/check_linux_memory)
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
- check_ssllabs.pl (https://www.unixadm.org/nagios/check_sslscan)
- check_succes_bacula
- check_supervisorctl.sh
- check_users.py
- check_glusterfs (https://exchange.nagios.org/directory/Plugins/System-Metrics/File-System/GlusterFS-checks/details)
