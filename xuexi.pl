use strict;
use warnings;
use FindBin qw($RealBin);
use lib "$RealBin";
use lib "$RealBin/src";
use lib "$RealBin/src/deps";

use Utils;

no Carp::Assert;
use FFI::Platypus;
use Data::Printer;
use Devel::StackTrace;

	# my $i = 0;
	# print STDERR "Stack Trace:\n";
	# while ( (my @call_details = (caller($i++))) ){
		# print STDERR $call_details[1].":".$call_details[2]." in function ".$call_details[3]."\n";
	# }

my %firstHash = (
	"Newton"	=>	"Issac",
	"Einstein"	=>	"Albert",
	1 =>	"Charles",
);
#
my $freq = 750;
my $duration = 300;

my $ffi = FFI::Platypus->new( api => 2, lib=>[undef], lang => 'Win32' );
my $address = $ffi->find_symbol("MessageBoxA");
print(sprintf("%X\n", $address));
#

use Devel::StackTrace;
my $trace = Devel::StackTrace->new;
# print $trace->as_string;

my $some = 41;
print sprintf("%v02X\n",$some);

my %account = (
	"number" => "6666",
	"opened" => "2010-11-11",
	"owners" => [
		{
			"name" => "yolo",
			"DOB" => "2222-04-04",
		},
		{
			"name" => "swag",
			"DOB" => "1111-09-09",
		},
	]
);

my $owners = $account{owners};
p ${$owners}[0]->{DOB};

my $test = 0x41;
my $result = Utils::getHex($test);
p $result;
assert("") if DEBUG;

