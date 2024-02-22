package fileReload;

use strict;
use warnings;

use Plugins;
use Utils;
use Log qw(debug message warning error);
use DDP;
use Commands qw(run);

use Time::HiRes qw(time);
use YAML qw(LoadFile);
use File::Spec;

my %PAUSE;
$PAUSE{time} = 0;
$PAUSE{timeout} = 1;

my $config_file = "reloadList.yaml";
my $file_handle;
my %reloadList;

sub myLog {
	my ($message, $domain, $level) = @_;
	message("[fileReload] " . $message, $domain, $level);
}

Plugins::register('fileReload', 'reload file upon change', \&onUnload);

my $hooks = Plugins::addHooks(
	['configModify', \&onConfigModify],
	['mainLoop_post', \&onMainLoop_post],
);

sub onUnload {
	Plugins::delHooks($hooks);
	Settings::removeFile($file_handle) if (defined $file_handle);

	undef %PAUSE;
	undef $config_file;
	undef $file_handle;
	undef %reloadList;
}

sub onConfigModify
{
}

sub executeCommands {
	my $commands = $_[0];

	foreach my $element (@{$commands}) {
		my $copy = $element;
		Commands::run($copy);
	}
}

sub onMainLoop_post {
	# Scan every 1 seconds
	if (timeOut(\%PAUSE) && (keys(%reloadList) > 0)) {
		for my $key (keys(%reloadList)) {
			if (!-e $key) {
				myLog("Skip file $key that doesn't exists\n");
				next;
			}
			if ($reloadList{$key}->{commands} && (@{$reloadList{$key}->{commands}} == 0)) {
				myLog("Skip file $key that has no commands\n");
				next;
			}

			my $lastModified = (stat($key))[9];
			if ($lastModified != $reloadList{$key}->{lastModified}) {
				# Update last modified
				$reloadList{$key}->{lastModified} = $lastModified;
				executeCommands($reloadList{$key}->{commands});
			}
		}
		# Reset timeout
		$PAUSE{time} = time;
	}
}

sub readConfig {
	# This always return a handle even if the file doesn't exist
	$file_handle = Settings::addControlFile(
		$config_file,
		loader => [\&parseReloadList, \%reloadList],
		internalName => 'reloadList.yaml',
		mustExist => 0,
	);
	# Looks like this allows parser to be called when you reload a file so the
	# changes take effect immediately
	Settings::loadByHandle($file_handle);
}


sub parseReloadList {
	my $filePath = shift;
	my $loaderSecondParam = shift;

	my $converted = LoadFile($filePath);
	# Returns a ref to the first document and dereference it
	myLog("Number of reload entires: " . keys(%{$converted}) . "\n");

	foreach my $file (keys(%$converted)) {
		# Skip nonexistent files but not removing them from the hash
		if (!(-e $file)) {
			myLog("File $file doesn't exists, skipping...\n");
			next;
		}
		# Create a new ref to anonymous hash
		my $newValue = {
			commands => $converted->{$file},
			lastModified => (stat($file))[9],
		};
		# Add new value
		$converted->{$file} = $newValue;
		# myLog("New value for $file: " . np($converted) . "\n");
	}

	%{$loaderSecondParam} = %{$converted};

	return 1;
}

# Parse config when plugin is loaded/reloaded
readConfig();

1;
