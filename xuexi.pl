use strict;
use warnings;
use FindBin qw($RealBin);
use lib "$RealBin";
use lib "$RealBin/src";
use lib "$RealBin/src/deps";
use LWP::UserAgent;

use Utils;

no Carp::Assert;
use FFI::Platypus;
use Data::Printer;
use Devel::StackTrace;

use Utils qw(makeCoordsFromTo);

# my $i = 0;
# print STDERR "Stack Trace:\n";
# while ( (my @call_details = (caller($i++))) ){
# print STDERR $call_details[1].":".$call_details[2]." in function ".$call_details[3]."\n";
# }

#
my $freq = 750;
my $duration = 300;

my $ffi = FFI::Platypus->new( api => 2, lib=>[undef], lang => 'Win32' );
my $address = $ffi->find_symbol("MessageBoxA");
print(sprintf("%X\n", $address));

use Devel::StackTrace;
my $trace = Devel::StackTrace->new;
# print $trace->as_string;

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

print("Account: " . p(%account) . "\n");
assert("") if DEBUG;

my $something;
if (defined $something) {
	print "something is defined\n";
} else {
	print "something is not defined\n";
}

my $coords = "\x3D\x82\xA3\xDC\x2A\x88";
my %from = (
	"x" => 256,
	"y" => 100,
);
my %to = (
	"x" => 0,
	"y" => 0,
);

my $char = {
	"pos" => \%from,
	"pos_to" => \%to
};
sub noparamundef {
	my ($caller, $isDead) = @_;
	if (defined $isDead) {
		print "isDead is defined\n";
	} else {
		print "isDead is not defined\n";
	}
}

noparamundef("yolo", 1);

print $char->{pos} . "\n";
%{$char->{pos}} = %to;
print np($char->{pos}) . "\n";
print $char->{pos} . "\n";
# print np($char) . "\n";

# my $ref = \%from;



