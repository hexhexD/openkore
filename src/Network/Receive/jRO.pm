#########################################################################
#  OpenKore - Network subsystem
#  Copyright (c) 2006 OpenKore Team
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
package Network::Receive::jRO;

use strict;
use Log qw(message warning error debug);
use base qw(Network::Receive::ServerType0);

sub new {
	my ($class) = @_;
	my $self = $class->SUPER::new(@_);
	my %packets = (
		'009D' => ['item_exists', 'a4 V C v3 C2', [qw(ID nameID identified x y amount subx suby)]],
		'01C8' => ['item_used', 'a2 V a4 v C', [qw(ID itemID actorID remaining success)]],
		'0A0A' => ['storage_item_added', 'a2 V V C4 a16 a25', [qw(ID amount nameID type identified broken upgrade cards options)]],
		'0A37' => ['inventory_item_added', 'a2 v V C3 a16 V C2 a4 v a25 C v', [qw(ID amount nameID identified broken upgrade cards type_equip type fail expire unknown options favorite viewID)]], # 69 bytes long and still a work in progress.
		'0A4D' => ['account_server_info', 'v a4 a4 a4 a4 a26 C x17 a*', [qw(len sessionID accountID sessionID2 lastLoginIP lastLoginTime accountSex serverInfo)]],
		'0ADD' => ['item_appeared', 'a4 V v C v2 C2 v C v', [qw(ID nameID type identified x y subx suby amount show_effect effect_type )]],
		# '02C2' => ['gameguard_unknown'],
		# '02A3' => ['gameguard_unknown'],
		# '02BD' => ['gameguard_unknown'],
		# '0B67' => ['gameguard_danger'],
		# '0B30' => ['gameguard_danger'],
	);

	foreach my $switch (keys %packets) {
		$self->{packet_list}{$switch} = $packets{$switch};
	}

	my %handlers = qw(
	);

	$self->{packet_lut}{$_} = $handlers{$_} for keys %handlers;
	$self->{npc_store_info_pack} = "V V C V";
	$self->{vender_items_list_item_pack} = 'V v2 C V C3 a16 a32';

	return $self;
}

# sub gameguard_unknown {
	# warning("Received unknown gameguard packet\n");
# }

# sub gameguard_danger {
	# die("Received dangerous gameguard pacekt\n")
# }

1;
