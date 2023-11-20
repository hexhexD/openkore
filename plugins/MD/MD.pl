package MD;

use strict;
use Plugins;
use Utils qw( existsInList getFormattedDate timeOut makeIP compactArray calcPosition distance);
use Time::HiRes qw(time);
use Log qw(warning message error debug);
use JSON::Tiny qw(encode_json);
use I18N qw(bytesToString);
use Globals;
use Misc;
use LWP::UserAgent;

Plugins::register('MD', 'Message discord and managa MDs', \&onUnload, \&onUnload);

my $hooks = Plugins::addHooks(
	['packet_privMsg', \&receivedPM],
	['disconnected',	\&disconnected], ['self_died',	\&self_died],
	['base_level_changed',	\&base_level_changed],
	['job_level_changed',	\&job_level_changed],
	['Network::Receive::map_changed',	\&map_changed],			
	['eventMacro/ppp', \&MD]
);

sub onUnload {
	Plugins::delHooks($hooks);
}

sub receivedPM {
	my ($self, $args) = @_;
	my $time = getFormattedDate(time);
	my $privMsg = $args->{privMsg};
	stripLanguageCode(\$privMsg);
	my $msg .= "```css\n";	
	$msg .= "================ [Openkore ChatLog] ===============\n";
	$msg .= "Time :".$time."\n",
	$msg .= "FROM :[".$args->{privMsgUser}."] : ".$privMsg."\n",
	$msg .= "====================================================```\n";
	$msg .= "```\n";	
	messageDiscord($msg);
}


sub disconnected {
	my $time = getFormattedDate(time);
	my $msg = "```OpenKore Status : Disconnect [".$time."]```\n",
	debug "Send disconnected To Discord!\n";
	messageDiscord($msg);
}
	
sub self_died {
	my $time = getFormattedDate(time);
	my $msg .= "```css\n";	
	$msg .= "================ [Openkore Notifier] ===============\n";
	$msg .= "Time :".$time."\n",
	$msg .= "Name: ".$char->{name}." \n",
	$msg .= "Status :".$char->{dead}."\n",
	$msg .= "Map: ".$field->name."\n",
	$msg .= "====================================================\n";
	$msg .= "```\n";	
	debug "Send self_died To Discord!\n";
	messageDiscord($msg);
}

sub base_level_changed {
	my ($self, $args) = @_;
	my $time = getFormattedDate(time);
	my $msg .= "```css\n";
	$msg .= "================ [Openkore Notifier] ===============\n";
	$msg .= "Time :".$time."\n",
	$msg .= "Name : ".$char->{name}."\n",
	$msg .= "LvUP! : ".$args->{level}."\n",
	$msg .= "====================================================\n";
	$msg .= "```\n";
	debug "Send base_level_changed To Discord!\n";
	messageDiscord($msg);
}

sub job_level_changed {
	my ($self, $args) = @_;
	my $time = getFormattedDate(time);
	my $msg .= "```css\n";	
	$msg .= "================ [Openkore Notifier] ===============\n";
	$msg .= "Time :".$time."\n",
	$msg .= "Name: ".$char->{name}."\n",
	$msg .= "JobLvUP! : ".$args->{level}."\n",
	$msg .= "====================================================\n";
	$msg .= "```\n";	
	messageDiscord($msg);
}

sub map_changed {
	my ($self, $args) = @_;
	my $time = getFormattedDate(time);
	return unless ($field->name ne $args->{oldMap});
	my $msg .= "```css\n";	
	$msg .= "=== [Openkore Notifier] ===\n";
	$msg .= "Time: ".$time."\n",
	$msg .= "Name: ".$char->{name}."\n",
	$msg .= "OldMap : ".$args->{oldMap}."\n",
	$msg .= "NewMap : ".$field->name."\n",		
	$msg .= "===========================\n";
	$msg .= "```\n";	
	debug "Send map_changed To Discord!\n";
	messageDiscord($msg);
}

sub messageDiscord {
	my ($msg) = @_;
	my %content = ('content' => $msg);
	my $json = encode_json(\%content);
	LWP::UserAgent->new->post(
	'https://discord.com/api/webhooks/1171953378646032500/gOiKFII_3igNJhzlE5uGDCWUmqfwrPU2LdjPXdOv38-M-G6ozipsBjHev7s_GyUew2LY', 
	'Content-Type' => 'application/json',
	'User-Agent' => 'Mozilla/4.0',
	'Content' => $json,
	);
}

sub runEventMacro {
	my ($macro) = @_;

	Commands::run("em stop");
	my $command = "em " . $macro . " -orphan reregister_safe";
	Commands::run($command);
}

sub MD {
	my ($caller) = @_;
	use Utils qw(getFormattedDate);
	use v5.10;

	my $logFile = $Settings::logs_folder . "/mdlog.txt";
	open(FH, ">>:utf8", $logFile) or die("Failed to open MD log file\n");

	message("caller is: ".$caller . "\n");
	my $prefix = "[".getFormattedDate(int(time))."]"." char ".$config{char}." [MD] ";

	if ($caller eq "start") {
		message("MD START\n");
		runEventMacro("sara");
		print(FH $prefix."Started with sara\n");
	}
	elsif ($caller eq "sara") {
		print(FH $prefix."Sara's memory done\n");
		Commands::run("autostorage");
		runEventMacro("ghost");
	}
	elsif ($caller eq "ghost") {
		print(FH $prefix."Ghost palace done\n");
		# TODO: weak char stops here
		runEventMacro("magic");
	}
	elsif ($caller eq "magic") {
		print(FH $prefix."Magic tournament done\n");
		Commands::run("autostorage");
		runEventMacro("sara2");
	}
	elsif ($caller eq "sara2") {
		print(FH $prefix."sara2 done\n");
		Commands::run("autostorage");
	}
	else {
		Commands::run("move 309 280");
		error "Unknown caller of MD function\n";
		die "MD function died"
	}

	close(FH);
}

1;