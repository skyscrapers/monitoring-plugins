#!/bin/bash
# ==============================================================================
# CPU Utilization Statistics plugin for Nagios
#
# Written by	:	Steve Bosek
# Patched by  	: 	Bas van der Doorn,Philipp Lemke
# Release	: 	2.3.6
# Creation date	: 	8 September 2007
# Revision date : 	5 August 2011
# Package       : 	BU Plugins
# Description   : 	Nagios plugin (script) to check cpu utilization
#			statistics.
#		  	This script has been designed and written on Unix
#			plateform (Linux, Aix, Solaris),
#			requiring iostat as external program. The locations of
#			these can easily be changed by editing the variables
#			$IOSTAT at the top of the script.
#			The script is used to query 6 of the key cpu statistics
#			(user,system,iowait,steal,nice,idle) at the same time.
#
# USAGE		: 	./check_cpu_stats.sh [-w <user,system,iowait>] [-c <user,system,iowait>] ( [ -i <intervals in second> ] [ -n <report number> ])
#
# Exemple: ./check_cpu_stats.sh
#          ./check_cpu_stats.sh -w 70,40,30 -c 90,60,40
#          ./check_cpu_stats.sh -w 70,40,30 -c 90,60,40 -i 3 -n 5
#
# ----------------------------------------------------------------------------------------
#
# TODO:  	- Support for MacOSX
#					- Search Binary Path (iostat,sar) or Add Path parameter when other as default
#
# ========================================================================================
#
# HISTORY :
#     Release	|     Date		|    Authors	 		|	Description
# -------------+------------+------------------+------------------------------------------------------------------------------------
#  2.0				| 16.02.08	| Steve Bosek		| Solaris support and new parameters
#               															 New Parameters : - iostat seconds intervals
#               																 - iostat report number
#  2.1 				| 08.06.08 	| Steve Bosek 		| Bug perfdata and convert comma in point for Linux result
#  2.1.1 			| 05.12.08 	| Steve Bosek   	| Fixed improperly terminated string that was left open at line 130
#  2.1.2			| 06.12.08 	| Bas van der Doorn 	| Fixed linux steal reported as idle, comparisons
#  2.2				| 06.12.08	| Bas van der Doorn	| Capable systems will output nice and steal data
#  2.2.1			| 06.12.08	| Steve Bosek		| Add for uniform Unix output nice and steal data on all perfdata
#  2.3   			| 11.12.08  | Steve Bosek   |  Add Threshold for user and system output with format -w user,system,iowait -c user,system,iowait
#                                       Add Default parameters value for threshold if not define
#                                       Add check for ${TAB_WARNING_THRESHOLD[@]} and ${TAB_CRITICAL_THRESHOLD[@]}
#                                       Add verify for Critical CPU Threshold lower as Warning CPU threshold
# 2.3.1 | 16.12.08 | Steve Bosek   |    Potability AIX,SOLARIS,LINUX for table initialisation (TAB_WARNING_THRESHOLD and TAB_CRITICAL_THRESHOLD)
# 2.3.2 | 22.12.08  | Steve Bosek  |    Strict Guideline Nagios for perfdata
# 2.3.3	| 08.02.08	| Philipp Lemke		| Add HP-UX support (tested on HP-UX B.11.23 U ia64) - steve bosek : uniform perfdata
# 2.3.4 | 29.03.09  | Steve Bosek  |   Bug in line 176: return only critical state for warning condition for USER Stats.
# 2.3.5 | 05.05.09 | Steve Bosek | Bug fix in NAGIOS_DATA for HP-UX
# 2.3.6 | 05.08.11 | Steve Bosek | Bug fix in NAGIOS_DATA : replace comma with semicolon in perfdata - compatibility with pnp
# -----------------------------------------------------------------------------------------


# Paths to commands used in this script.  These may have to be modified to match your system setup.

IOSTAT="/usr/bin/iostat"
#Needed for HP-UX
SAR="/usr/bin/sar"

# Nagios return codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

# Plugin parameters value if not define
LIST_WARNING_THRESHOLD=${LIST_WARNING_THRESHOLD:="70,40,30,10"}
LIST_CRITICAL_THRESHOLD=${LIST_CRITICAL_THRESHOLD:="90,60,40"}
INTERVAL_SEC=${INTERVAL_SEC:="1"}
NUM_REPORT=${NUM_REPORT:="3"}
# Plugin variable description
PROGNAME=$(basename $0)
RELEASE="Revision 2.3.6"
AUTHOR="(c) 2008 Steve Bosek (steve.bosek@gmail.com)"

if [ `uname` = "HP-UX" ];then
	if [ ! -x $SAR ]; then
        echo "UNKNOWN: sar not found or is not executable by the nagios user."
        exit $STATE_UNKNOWN
	fi
else
	if [ ! -x $IOSTAT ]; then
	echo "UNKNOWN: iostat not found or is not executable by the nagios user."
	exit $STATE_UNKNOWN
	fi
fi

# Functions plugin usage
print_release() {
    echo "$RELEASE $AUTHOR"
}


print_usage() {
        echo ""
        echo "$PROGNAME $RELEASE - CPU Utilization check script for Nagios"
        echo ""
        echo "Usage: check_cpu_stats.sh -w -c (-i -n)"
        echo ""
        echo "  -w  Warning threshold in % for warn_user,warn_system,warn_iowait,warn_steal CPU (default : 70,40,30,10)"
        echo "  Exit with WARNING status if cpu exceeds warn_n"
        echo "  -c  Critical threshold in % for crit_user,crit_system,crit_iowait CPU (default : 90,60,40)"
        echo "  Exit with CRITICAL status if cpu exceeds crit_n"
        echo "  -i  Interval in seconds for iostat (default : 1)"
        echo "  -n  Number report for iostat (default : 3)"
        echo "  -h  Show this page"
        echo ""
    echo "Usage: $PROGNAME"
    echo "Usage: $PROGNAME --help"
    echo ""
    exit 0
}

print_help() {
	print_usage
        echo ""
        echo "This plugin will check cpu utilization (user,system,CPU_Iowait,idle in %)"
        echo ""
	exit 0
}

# Parse parameters
while [ $# -gt 0 ]; do
    case "$1" in
        -h | --help)
            print_help
            exit $STATE_OK
            ;;
        -v | --version)
                print_release
                exit $STATE_OK
                ;;
        -w | --warning)
                shift
                LIST_WARNING_THRESHOLD=$1
                ;;
        -c | --critical)
               shift
                LIST_CRITICAL_THRESHOLD=$1
                ;;
        -i | --interval)
               shift
               INTERVAL_SEC=$1
                ;;
        -n | --number)
               shift
               NUM_REPORT=$1
                ;;
        *)  echo "Unknown argument: $1"
            print_usage
            exit $STATE_UNKNOWN
            ;;
        esac
shift
done





# List to Table for warning threshold (compatibility with
#set +A TAB_WARNING_THRESHOLD `echo $LIST_WARNING_THRESHOLD | sed 's/,/ /g'`
#if [ "${#TAB_WARNING_THRESHOLD[@]}" -ne "4" ]; then
#  echo "ERROR : Bad count parameter in Warning Threshold"
#  exit $STATE_WARNING
#else
TAB_WARNING_THRESHOLD=(`echo $LIST_WARNING_THRESHOLD | sed 's/,/ /g'`)
if [ "${#TAB_WARNING_THRESHOLD[@]}" -ne "4" ]; then
echo "ERROR : Bad count parameter in Warning Threshold"
exit $STATE_WARNING
else
USER_WARNING_THRESHOLD=`echo ${TAB_WARNING_THRESHOLD[0]}`
SYSTEM_WARNING_THRESHOLD=`echo ${TAB_WARNING_THRESHOLD[1]}`
IOWAIT_WARNING_THRESHOLD=`echo ${TAB_WARNING_THRESHOLD[2]}`
CPU_STEAL_THRESHOLD=`echo ${TAB_WARNING_THRESHOLD[3]}`

fi

# List to Table for critical threshold
#set +A TAB_CRITICAL_THRESHOLD `echo $LIST_CRITICAL_THRESHOLD | sed 's/,/ /g'`
#if [ "${#TAB_CRITICAL_THRESHOLD[@]}" -ne "3" ]; then
#  echo "ERROR : Bad count parameter in CRITICAL Threshold"
#  exit $STATE_WARNING
TAB_CRITICAL_THRESHOLD=( `echo $LIST_CRITICAL_THRESHOLD | sed 's/,/ /g'` )
if [ "${#TAB_CRITICAL_THRESHOLD[@]}" -ne "3" ]; then
echo "ERROR : Bad count parameter in Critical Threshold"
exit $STATE_CRITICAL
else
USER_CRITICAL_THRESHOLD=`echo ${TAB_CRITICAL_THRESHOLD[0]}`
SYSTEM_CRITICAL_THRESHOLD=`echo ${TAB_CRITICAL_THRESHOLD[1]}`
IOWAIT_CRITICAL_THRESHOLD=`echo ${TAB_CRITICAL_THRESHOLD[2]}`
fi

if [ ${TAB_WARNING_THRESHOLD[0]} -ge ${TAB_CRITICAL_THRESHOLD[0]} -o ${TAB_WARNING_THRESHOLD[1]} -ge ${TAB_CRITICAL_THRESHOLD[1]} -o ${TAB_WARNING_THRESHOLD[2]} -ge ${TAB_CRITICAL_THRESHOLD[2]} ]; then
  echo "ERROR : Critical CPU Threshold lower as Warning CPU Threshold "
  exit $STATE_WARNING
fi


# CPU Utilization Statistics Unix Plateform ( Linux,AIX,Solaris are supported )
case `uname` in
	Linux ) CPU_REPORT=`iostat -c $INTERVAL_SEC $NUM_REPORT | sed -e 's/,/./g' | tr -s ' ' ';' | sed '/^$/d' | tail -1`
			CPU_REPORT_SECTIONS=`echo ${CPU_REPORT} | grep ';' -o | wc -l`
			CPU_USER=`echo $CPU_REPORT | cut -d ";" -f 2`
			CPU_NICE=`echo $CPU_REPORT | cut -d ";" -f 3`
			CPU_SYSTEM=`echo $CPU_REPORT | cut -d ";" -f 4`
			CPU_IOWAIT=`echo $CPU_REPORT | cut -d ";" -f 5`
		if [ ${CPU_REPORT_SECTIONS} -ge 6 ]; then
			CPU_STEAL=`echo $CPU_REPORT | cut -d ";" -f 6`
			CPU_IDLE=`echo $CPU_REPORT | cut -d ";" -f 7`
			NAGIOS_DATA="user=${CPU_USER}% system=${CPU_SYSTEM}%, iowait=${CPU_IOWAIT}%, idle=${CPU_IDLE}%, nice=${CPU_NICE}%, steal=${CPU_STEAL}% | CpuUser=${CPU_USER}%;${TAB_WARNING_THRESHOLD[0]};${TAB_CRITICAL_THRESHOLD[0]};0; CpuSystem=${CPU_SYSTEM}%;${TAB_WARNING_THRESHOLD[1]};${TAB_CRITICAL_THRESHOLD[1]};0; CpuIowait=${CPU_IOWAIT}%;${TAB_WARNING_THRESHOLD[2]};${TAB_CRITICAL_THRESHOLD[2]};0; CpuIdle=${CPU_IDLE}%;0;0;0; CpuNice=${CPU_NICE}%;0;0;0; CpuSteal=${CPU_STEAL}%;0;0;0;"
		else
			CPU_IDLE=`echo $CPU_REPORT | cut -d ";" -f 6`
			NAGIOS_DATA="user=${CPU_USER}% system=${CPU_SYSTEM}%, iowait=${CPU_IOWAIT}%, idle=${CPU_IDLE}%, nice=${CPU_NICE}%, steal=0.00% | CpuUser=${CPU_USER}%;${TAB_WARNING_THRESHOLD[0]};${TAB_CRITICAL_THRESHOLD[0]};0; CpuSystem=${CPU_SYSTEM}%;${TAB_WARNING_THRESHOLD[1]};${TAB_CRITICAL_THRESHOLD[1]};0; CpuIowait=${CPU_IOWAIT}%;${TAB_WARNING_THRESHOLD[2]};${TAB_CRITICAL_THRESHOLD[2]};0; CpuIdle=${CPU_IDLE}%;0;0;0; CpuNice=${CPU_NICE}%;0;0;0; CpuSteal=0.0%;0;0;0;"
		fi
            ;;
 	AIX ) CPU_REPORT=`iostat -t $INTERVAL_SEC $NUM_REPORT | sed -e 's/,/./g'|tr -s ' ' ';' | tail -1`
			CPU_USER=`echo $CPU_REPORT | cut -d ";" -f 4`
			CPU_SYSTEM=`echo $CPU_REPORT | cut -d ";" -f 5`
			CPU_IOWAIT=`echo $CPU_REPORT | cut -d ";" -f 7`
			CPU_IDLE=`echo $CPU_REPORT | cut -d ";" -f 6`
			NAGIOS_DATA="user=${CPU_USER}% system=${CPU_SYSTEM}%, iowait=${CPU_IOWAIT}%, idle=${CPU_IDLE}%, nice=0.00%, steal=0.00% | CpuUser=${CPU_USER}%;${TAB_WARNING_THRESHOLD[0]};${TAB_CRITICAL_THRESHOLD[0]};0; CpuSystem=${CPU_SYSTEM}%;${TAB_WARNING_THRESHOLD[1]};${TAB_CRITICAL_THRESHOLD[1]};0; CpuIowait=${CPU_IOWAIT}%;${TAB_WARNING_THRESHOLD[2]};${TAB_CRITICAL_THRESHOLD[2]};0; CpuIdle=${CPU_IDLE}%;0;0;0; CpuNice=0.0%;0;0;0; CpuSteal=0.0%;0;0;0;"
            ;;
  	SunOS ) CPU_REPORT=`iostat -c $INTERVAL_SEC $NUM_REPORT | tail -1`
      			CPU_USER=`echo $CPU_REPORT | awk '{ print $1 }'`
			      CPU_SYSTEM=`echo $CPU_REPORT | awk '{ print $2 }'`
			      CPU_IOWAIT=`echo $CPU_REPORT | awk '{ print $3 }'`
			      CPU_IDLE=`echo $CPU_REPORT | awk '{ print $4 }'`
			      NAGIOS_DATA="user=${CPU_USER}% system=${CPU_SYSTEM}%, iowait=${CPU_IOWAIT}%, idle=${CPU_IDLE}%, nice=0.00%, steal=0.00% | CpuUser=${CPU_USER}%;${TAB_WARNING_THRESHOLD[0]};${TAB_CRITICAL_THRESHOLD[0]};0; CpuSystem=${CPU_SYSTEM}%;${TAB_WARNING_THRESHOLD[1]};${TAB_CRITICAL_THRESHOLD[1]};0; CpuIowait=${CPU_IOWAIT}%;${TAB_WARNING_THRESHOLD[2]};${TAB_CRITICAL_THRESHOLD[2]};0; CpuIdle=${CPU_IDLE}%;0;0;0; CpuNice=0.0%;0;0;0; CpuSteal=0.0%;0;0;0;"
            ;;
    HP-UX) CPU_REPORT=`$SAR $INTERVAL_SEC $NUM_REPORT | grep Average`
			      CPU_USER=`echo $CPU_REPORT | awk '{ print $2 }'`
            CPU_SYSTEM=`echo $CPU_REPORT | awk '{ print $3 }'`
            CPU_IOWAIT=`echo $CPU_REPORT | awk '{ print $4 }'`
            CPU_IDLE=`echo $CPU_REPORT | awk '{ print $5 }'`
            NAGIOS_DATA="user=${CPU_USER}% system=${CPU_SYSTEM}% iowait=${CPU_IOWAIT}% idle=${CPU_IDLE}% nice=0.00% steal=0.00% | CpuUser=${CPU_USER}%;${TAB_WARNING_THRESHOLD[0]};${TAB_CRITICAL_THRESHOLD[0]};0; CpuSystem=${CPU_SYSTEM}%;${TAB_WARNING_THRESHOLD[1]};${TAB_CRITICAL_THRESHOLD[1]};0; CpuIowait=${CPU_IOWAIT};${TAB_WARNING_THRESHOLD[2]};${TAB_CRITICAL_THRESHOLD[2]};0; CpuIdle=${CPU_IDLE}%;0;0;0; CpuNice=0.0%;0;0;0; CpuSteal=0.0%;0;0;0;"
            ;;
    #  MacOS X test
   # Darwin ) CPU_REPORT=`iostat -w $INTERVAL_SEC -c $NUM_REPORT | tail -1`
    #  		CPU_USER=`echo $CPU_REPORT | awk '{ print $4 }'`
	#		CPU_SYSTEM=`echo $CPU_REPORT | awk '{ print $5 }'`
	#		CPU_IDLE=`echo $CPU_REPORT | awk '{ print $6 }'`
      #      NAGIOS_DATA="user=${CPU_USER}% system=${CPU_SYSTEM}% iowait=0.00% idle=${CPU_IDLE}% nice=0.00% steal=0.00% | CpuUser=${CPU_USER}%;${TAB_WARNING_THRESHOLD[0]};${TAB_CRITICAL_THRESHOLD[0]};0; CpuSystem=${CPU_SYSTEM}%;${TAB_WARNING_THRESHOLD[1]};${TAB_CRITICAL_THRESHOLD[1]};0; CpuIowait=0.0%;0;0;0; CpuIdle=${CPU_IDLE}%;0;0;0; CpuNice=0.0%;0;0;0; CpuSteal=0.0%;0;0;0;"
         #   ;;
	*) 		echo "UNKNOWN: `uname` not yet supported by this plugin. Coming soon !"
			exit $STATE_UNKNOWN
	    ;;
	esac

# Add for integer shell issue
CPU_USER_MAJOR=`echo $CPU_USER| cut -d "." -f 1`
CPU_SYSTEM_MAJOR=`echo $CPU_SYSTEM | cut -d "." -f 1`
CPU_IOWAIT_MAJOR=`echo $CPU_IOWAIT | cut -d "." -f 1`
CPU_IDLE_MAJOR=`echo $CPU_IDLE | cut -d "." -f 1`
CPU_STEAL_MAJOR=`echo $CPU_STEAL | cut -d "." -f 1`

# Return
if [ ${CPU_USER_MAJOR} -ge $USER_CRITICAL_THRESHOLD ]; then
    echo "CPU STATISTICS CRITICAL : ${NAGIOS_DATA}"
		exit $STATE_CRITICAL
		elif [ ${CPU_SYSTEM_MAJOR} -ge $SYSTEM_CRITICAL_THRESHOLD ]; then
		echo "CPU STATISTICS CRITICAL : ${NAGIOS_DATA}"
		exit $STATE_CRITICAL
    elif [ ${CPU_IOWAIT_MAJOR} -ge $IOWAIT_CRITICAL_THRESHOLD ]; then
		echo "CPU STATISTICS CRITICAL : ${NAGIOS_DATA}"
		exit $STATE_CRITICAL
		elif [ ${CPU_STEAL_MAJOR} -ge $CPU_STEAL_THRESHOLD ]; then
		echo "CPU STATISTICS WARNING : ${NAGIOS_DATA}"
		exit $STATE_WARNING
    elif [ ${CPU_USER_MAJOR} -ge $USER_WARNING_THRESHOLD ] && [ ${CPU_USER_MAJOR} -lt $USER_CRITICAL_THRESHOLD ]; then
		echo "CPU STATISTICS WARNING : ${NAGIOS_DATA}"
		exit $STATE_WARNING
	  elif [ ${CPU_SYSTEM_MAJOR} -ge $SYSTEM_WARNING_THRESHOLD ] && [ ${CPU_SYSTEM_MAJOR} -lt $SYSTEM_CRITICAL_THRESHOLD ]; then
		echo "CPU STATISTICS WARNING : ${NAGIOS_DATA}"
		exit $STATE_WARNING
	  elif  [ ${CPU_IOWAIT_MAJOR} -ge $IOWAIT_WARNING_THRESHOLD ] && [ ${CPU_IOWAIT_MAJOR} -lt $IOWAIT_CRITICAL_THRESHOLD ]; then
		echo "CPU STATISTICS WARNING : ${NAGIOS_DATA}"
		exit $STATE_WARNING
else
		echo "CPU STATISTICS OK : ${NAGIOS_DATA}"
		exit $STATE_OK
fi
