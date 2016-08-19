#!/bin/bash
#
# Author        : N.Hashimoto
# E-mail	: mrhashnao@gmail.com
# Description   : Verify node joinning cassandra multinode cluster, and
#		  send alert if the number of live node is less than the specified number.
#
# ------------------------------------------------------------
# functions
# ------------------------------------------------------------
# print help
usage() {
cat << EOF
Usage: $0 -H <host> -P <port> -w <warning> -c <critical>

 -H <host> IP address or hostname of the cassandra node to connect, localhost by default.
 -P <port> JMX port, 7199 by default.
 -w <warning> alert warning state, if the number of live nodes is less than <warning>.
 -c <critical> alert critical state, if the number of live nodes is less than <critical>.
 -h show command option
 -V show command version

EOF
exit 3
}

# Checking the status, outputting the nagios status code
check_status() {
case $retval in
  0 )
  echo "OK - Live Node:$live_node - ${verbose[*]} | ${performance[*]}"
  exit 0
  ;;

  1 )
  echo "WARNING - Live Node:$live_node - ${verbose[*]} | ${performance[*]}"
  exit 1
  ;;

  2 )
  echo "CRITICAL - Live Node:$live_node - ${verbose[*]} | ${performance[*]}"
  exit 2
  ;;

  3 )
  echo "UNKNOWN - Live Node:$live_node - ${verbose[*]} | ${performance[*]}"
  exit 3
  ;;

esac
}


# ------------------------------------------------------------
# variables
# ------------------------------------------------------------
export LANG=C
opt_v=1.00
date=$(date '+%Y%m%d')

host="localhost"
port="7199"

#PROGNAME=`basename $0`
#PROGPATH=`echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,'`
#REVISION=`echo '$Revision: 1749 $' | sed -e 's/[^0-9.]//g'`
. /usr/local/nagios/libexec/utils.sh

# option definitions
while getopts "c:w:H:P:hV" opt ; do
  case $opt in
  c )
  critical="$OPTARG"
  ;;

  w )
  warning="$OPTARG"
  ;;

  H )
  host="$OPTARG"
  ;;

  P )
  port="$OPTARG"
  ;;

  h )
  usage
  ;;

  V )
  echo "`basename $0` $opt_v" ; exit 0
  ;;

  * )
  usage
  ;;

  esac
done
shift `expr $OPTIND - 1`

# verify warning and critical are number
expr $warning + 1 >/dev/null 2>&1
if [ "$?" -lt 2 ]; then
  true
else
  echo "-c <critical> $critical must be number."
  exit 3
fi

expr $critical + 1 >/dev/null 2>&1
if [ "$?" -lt 2 ]; then
  true
else
  echo "-c <critical> $critical must be number."
  exit 3
fi

# verify warning is less than critical
if [ "$warning " -lt "$critical" ]; then
  echo "-w <warning> $warning must be less than -c <critical> $critical."
  exit 3
fi


# ------------------------------------------------------------
# begin script
# ------------------------------------------------------------
# check the number of live node, status and performance
live_node=$(nodetool -h $host -p $port ring | grep -c 'Up')
verbose=($(nodetool -h $host -p $port ring | awk '/Up/ {print $1":"$4","$5","$6$7","$8 " " }'))
performance=($(nodetool -h $host -p $port ring | awk '/Up/ {print "Load_"$1"="$6$7,"Owns_"$1"="$8}'))

# unless live node is number, reply unknown code
expr $live_node + 1 >/dev/null 2>&1
if [ "$?" -lt 2 ]; then
  true
else
  retval=3
fi

# verify the number of live node is less than critical, warning
if [ "$live_node" -le "$critical" ]; then
  retval=2
else
  if [ "$live_node" -le "$warning" ]; then
    retval=1
  else
    retval=0
  fi
fi

check_status
