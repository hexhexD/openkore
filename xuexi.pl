use strict;
use warnings;
use FindBin qw($RealBin);
use lib "$RealBin";
use lib "$RealBin/src";
use lib "$RealBin/src/deps";
use LWP::UserAgent;
use JSON::Tiny qw(encode_json);

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

assert("") if DEBUG;

my %content = ('username' => '[OpenKore-Bot]', 'content' => "hahaahha");
my $json = encode_json(\%content);
# my $json = encode_json({content => "Me and Friend"});
LWP::UserAgent->new->post(
	'https://discord.com/api/webhooks/1171953378646032500/gOiKFII_3igNJhzlE5uGDCWUmqfwrPU2LdjPXdOv38-M-G6ozipsBjHev7s_GyUew2LY',
	'Content-Type' => 'application/json',
	'User-Agent' => 'Mozilla/4.0',
	'Content' => "$json",
);

