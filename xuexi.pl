use strict;
use warnings;
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

my $freq = 750;
my $duration = 300;


my $ffi = FFI::Platypus->new( api => 2, lib=>[undef], lang => 'Win32' );
my $address = $ffi->find_symbol("MessageBoxA");
print(sprintf("%X\n", $address));


my %args = (
	skillHandle => "swag",
	lv => 10,
);

$args{giveup}{time} = 1345;
$args{giveup}{timeout} = 20;

p %args;
my $trace = Devel::StackTrace->new;
my $test = 11;
$test = 456 unless (2<1 && "swag" eq "swag");

my @testarray = ("print", "abcd", "last");

foreach (@testarray)
{
	if ($_ eq "abcd")
	{
		last;
	}
	print;
}
