#########################################################################
#  OpenKore - Network subsystem
#  This module contains functions for sending messages to the server.
#
#  This software is open source, licensed under the GNU General Public
#  License, version 2.
#  Basically, this means that you're allowed to modify and distribute
#  this software. However, if you distribute modified versions, you MUST
#  also distribute the source code.
#  See http://www.gnu.org/licenses/gpl.html for the full license.
#########################################################################
# jRO (Japan)
# Servertype overview: https://openkore.com/wiki/ServerType
package Network::Send::jRO;

use strict;
use Network::Send::ServerType0;
use base qw(Network::Send::ServerType0);
use Globals qw(%config);
use Log qw(debug);

sub new {
	my ($class) = @_;
	my $self = $class->SUPER::new(@_);

	my %packets = (
		'027C' => ['master_login', 'V A16 Z8 A40 Z12 H*', [qw(version username unknown password unknown2 unknown3)]],# 190
	);
	$self->{packet_list}{$_} = $packets{$_} for keys %packets;

	my %handlers = qw(
		actor_look_at 0361
		actor_info_request 0368
		char_create 0A39
		item_drop 0363
		item_take 0362
		master_login 027C
		send_equip 0998
		storage_item_add 0364
		storage_item_remove 0365
        character_move 035F
	);
	$self->{packet_lut}{$_} = $handlers{$_} for keys %handlers;

	return $self;
}

sub sendMasterLogin {
	my ($self, $username, $password, $master_version, $version) = @_;
	my $msg;

    my $unknown = "";
    my $unknown2 = "";
    my $unknown3 = "03218defcb8eca5275048b9dbfbb";
	$msg = $self->reconstruct({
		switch => 'master_login',
		version => $version || $self->version,
		username => $username,
        unknown => $unknown,
		password => $password,
        unknown2 => $unknown2,
        unknown3 => $unknown3,
	});

	$self->sendToServer($msg);
	debug "Sent sendMasterLogin \n", "sendPacket", 2;
}

1;
