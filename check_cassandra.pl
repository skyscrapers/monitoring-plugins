#!/usr/bin/perl
use strict;
use warnings;
use Getopt::Long;
use POSIX ':sys_wait_h';

my %messages = (
    bad_args         => ' bad arguments;',
    incorrect_args   => ' "warning" should be less than "critical";',
    node_tool_error  => ' cannot run %s;',
    node_down        => ' Cassandra node is DOWN',
    heap_usage       => ' %d%% heap used;'
);

my $help;
#Default threshold values:
my $heap_w = 85;
my $heap_c = 95;

my $GetOptions_result = GetOptions(
    'help'          => \$help,
    'heap_w=i'      => \$heap_w,
    'heap_c=i'      => \$heap_c,
);

if ( $GetOptions_result != 1 ) {
    mydie( $messages{'bad_args'} );
}
if ( $heap_w >= $heap_c ) {
    mydie( $messages{'incorrect_args'} );
}

if ($help) {
    print <<"HELP";
    Usage: $0 [--heap_w=percent] [--heap_c=percent]

       --heap_w warning value for Java heap usage in percents (default=85)
       --heap_c critical value for Java heap usage in percents (default=95)
HELP
    exit;
}

my $result             = 'OK';
my $result_description = '';
my $result_perf        = '';
my %result_rank        = (
    'OK'       => 0,
    'WARNING'  => 1,
    'CRITICAL' => 2,
);

my $host                = '127.0.0.1';
my $nodetool_path       = '/usr/share/cassandra/bin/nodetool';
my $nodetool_opts       = '2>&1';

check_cassandra_status();
print "CASSANDRA $result - $result_description | $result_perf\n";
exit $result_rank{$result};

sub check_cassandra_status {
    my $heap_usage      = 0;
    
    if ( !-x $nodetool_path ) {
        mydie( sprintf $messages{'node_tool_error'}, $nodetool_path );
    }
    my @return              = `$nodetool_path -h $host info $nodetool_opts`;
    my $current_exit_status = WEXITSTATUS($?);
    if ( $current_exit_status != 0 ){
        set_result('CRITICAL');
        $result_description .= $messages{'node_down'};
        return;
    }
    foreach my $line (@return) {
        if ( $line =~ m{^Heap Memory \(MB\)\s*:\s*([\d\,\.]+)\s/\s([\d\,\.]+)} ) {
            my $heap_used       = $1;
            my $heap_available  = $2;
            $heap_used          =~ s/\,/./;
            $heap_available     =~ s/\,/./;
            $heap_usage = 100 * $heap_used / $heap_available;
        }
    }
    if ( $heap_usage >= $heap_c ) {
        set_result('CRITICAL');
        $result_description .= sprintf $messages{'heap_usage'}, $heap_usage;
    }
    elsif ( $heap_usage >= $heap_w ) {
        set_result('WARNING');
        $result_description .= sprintf $messages{'heap_usage'}, $heap_usage;
    }
    $result_perf .= sprintf ("heap_mem=%.2f ", $heap_usage);
    return;
}

sub set_result {
    my ($new_result) = @_;

    if ( $result_rank{$result} < $result_rank{$new_result} ) {
        $result = $new_result;
        if ( $result_description eq '' ) {
            $result_description .= 'WARNING:';
        }
    }
    return;
}

sub mydie {
    my ($message) = @_;

    print "CASSANDRA CRITICAL - $message\n";
    exit 2;
}
