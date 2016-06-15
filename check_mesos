#!/usr/bin/env python
import nagiosplugin
import argparse
import logging
import re
import requests
from urlparse import urlparse

INFINITY = float('inf')
HEALTHY = 1
UNHEALTHY = -1

log = logging.getLogger("nagiosplugin")

class MesosMaster(nagiosplugin.Resource):
  def __init__(self, baseuri, frameworks):
    self.baseuri = baseuri
    self.frameworks = frameworks

  def build_redirection(self, master_uri, location):
    original = urlparse(master_uri)
    redirect = urlparse(location)
    if redirect.scheme == '':
      return original.scheme + ':' + location
    else: # version <0.23
      return location

  def probe(self):
    master_uri=self.baseuri
    log.debug('Looking at %s for redirect', master_uri)

    try:
      response = requests.head(master_uri + '/master/redirect', timeout=5, allow_redirects=False)
      if response.status_code != 307:
        yield nagiosplugin.Metric('leader redirect', UNHEALTHY)
      log.info('Redirect response is %s', response)
      master_uri = self.build_redirection(master_uri, response.headers['Location'])
      # yield the leader redirect later, the summary takes the first check which we want to be 'master health'
    except requests.exceptions.RequestException, e:
      log.error('leader redirect %s', e)
      yield nagiosplugin.Metric('leader redirect', UNHEALTHY)
      return

    log.debug('Base URI is redirected to %s', master_uri)

    response = requests.get(master_uri + '/health', timeout=5)
    log.info('Response from %s is %s', response.request.url, response)
    if response.status_code in [200, 204]:
      yield nagiosplugin.Metric('master health', HEALTHY)
    else:
      yield nagiosplugin.Metric('master health', UNHEALTHY)

    response = requests.get(master_uri + '/master/state.json', timeout=5)
    log.info('Response from %s is %s', response.request.url, response)
    if response.encoding is None:
      response.encoding = "UTF8"
    state = response.json()

    has_leader = len(state.get('leader', '')) > 0

    yield nagiosplugin.Metric('active slaves', state['activated_slaves'])
    yield nagiosplugin.Metric('active leader', 1 if has_leader else 0)

    # now we can yield the redirect status, from above
    yield nagiosplugin.Metric('leader redirect', HEALTHY)

    for framework_regex in self.frameworks:
      framework = None
      for candidate in state['frameworks']:
        if re.search(framework_regex, candidate['name']) is not None:
          framework = candidate

      unregistered_time = INFINITY

      if framework is not None:
        unregistered_time = framework['unregistered_time']
        if not framework['active'] and unregistered_time == 0:
          unregistered_time = INFINITY
      yield nagiosplugin.Metric('framework ' + framework_regex, unregistered_time, context='framework')


@nagiosplugin.guarded
def main():
  argp = argparse.ArgumentParser()
  argp.add_argument('-H', '--host', required=True,
                    help='The hostname of a Mesos master to check')
  argp.add_argument('-P', '--port', default=5050,
                    help='The Mesos master HTTP port - defaults to 5050')
  argp.add_argument('-n', '--slaves', default=1,
                    help='The minimum number of slaves the cluster must be running')
  argp.add_argument('-F', '--framework', default=[], action='append',
                    help='Check that a framework is registered matching the given regex, may be specified multiple times')
  argp.add_argument('-v', '--verbose', action='count', default=0,
                    help='increase output verbosity (use up to 3 times)')

  args = argp.parse_args()

  unhealthy_range = nagiosplugin.Range('%d:%d' % (HEALTHY - 1, HEALTHY + 1))
  slave_range = nagiosplugin.Range('%s:' % (args.slaves,))

  check = nagiosplugin.Check(
              MesosMaster('http://%s:%d' % (args.host, int(args.port)), args.framework),
              nagiosplugin.ScalarContext('leader redirect', unhealthy_range, unhealthy_range),
              nagiosplugin.ScalarContext('master health', unhealthy_range, unhealthy_range),
              nagiosplugin.ScalarContext('active slaves', slave_range, slave_range),
              nagiosplugin.ScalarContext('active leader', '1:1', '1:1'),
              nagiosplugin.ScalarContext('framework', '0:0', '0:0'))
  check.main(verbose=args.verbose)

if __name__ == '__main__':
  main()
