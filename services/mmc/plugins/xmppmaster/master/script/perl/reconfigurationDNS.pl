#!/usr/bin/perl

#---------------------------------#
#	2 cas :
#       - Un dns ou Liste de dns
#       - vide ( fichier nul)
#---------------------------------#
use warnings;
use File::Copy;
use Getopt::Std;


$usage="Usage : $0 -h < (1) Debian - (2) RedHat - (3) Oracle VM > -d <dns-1,dns-n> ";
$nboptionObligatoire=2;

%optionObligatoire= (

	'h' => 1,
	'd' => 1,
);
getopts( "h:d:", \%opts );

$nb=0;
foreach $key( sort keys %opts ) {

	$nb+=&controleParametre($key,\$nb);
}

if ($nb ne $nboptionObligatoire) {

	&gestionErreur("Parametre insuffisant");
}

$os=$opts{'h'};
# ================================
# Affectation des variables
# ================================
if ($os ne '1' && $os ne '2' && $os ne '3') {

        &gestionErreur("Identification de la machine erronne");
}

@dns=split(/,/,$opts{'d'}) if (defined($opts{'d'}));

$fichier_dns='/etc/resolv.conf';
#$fichier_dns='J:/siveo/perl/test/resolv.conf';

&debian($fichier_dns,@dns) if ($os eq '1'); 
&redhat($fichier_dns,@dns) if ($os eq '2');
&oracle_vm($fichier_dns,@dns) if ($os eq '3');

# restart du service reseau
@cmdSys="/etc/init.d/networking restart";
system(@cmdSys);

exit 0;


# =========================================
#               Fonctions 
# =========================================
sub print_usage() {

	print"$usage\n";
}
#-----------------------------------------#
sub gestionErreur($) {

	($message)=@_;
	print $message,"\n";
	print "\n";
    print_usage();
    exit 1;
}
#-----------------------------------------#
sub controleParametre($$) {

	($cle)=@_;

	if (exists($optionObligatoire{$cle})) {
		
		$nb=$optionObligatoire{$cle};
	}
	
	return $nb;
}
#-----------------------------------------#
sub debian($$$) {

	# Modification du fichier resolv.conf
	($fichier_dns,@dns)=@_;
	
	&updateResolvConf($fichier_dns,@dns);
}
#-----------------------------------------#
sub redhat($$$) {

	# Modification du fichier resolv.conf
	($fichier_dns,@dns)=@_;
          
	&updateResolvConf($fichier_dns,@dns);
}
#-----------------------------------------#
sub oravle_vm($$$) {

# Modification du fichier resolv.conf
	($fichier_dns,@dns)=@_;
          
	&updateResolvConf($fichier_dns,@dns);
}
#-----------------------------------------#
sub updateResolvConf($$) {

	($fichier_dns,@dns)=@_;
	
	$date_save=`date +'%Y%m%d%H%M%S'`;
	chomp $date_save;
	
	# Modification du fichier resolv.conf
	$fichier_sav=$fichier_dns."_du_$date_save";
        
	# sauvegarde du fichier
	&sauvegarde_fic("$fichier_dns" , "$fichier_sav");

	# chargement des dns
	if (@dns) {
		
		open(OUT,">$fichier_dns") or die "$!";
	
		while(@dns) {
		
			$dns_tmp=shift @dns;
			print OUT "nameserver $dns_tmp\n";
		}
		close(OUT);
	}
	else {
		# purge du fichier et recreation a vide
		unlink("$fichier_dns");
		system("touch $fichier_dns");
	}

}
#-----------------------------------------#
sub sauvegarde_fic() {

    # sauvegarde du fichier si existant
	if (-s $_[0]) {

		$fic_backup=`basename $_[1]`;
		chomp $fic_backup;
		$fic_backup='backup_'.$fic_backup;
	
		if (!copy("$_[0]","$fic_backup")) {

			print "sauvegarde du fichier $_[0] vers $fic_backup impossible\n";
			exit 1;
			}
		else {

			print "sauvegarde du fichier $fic_backup OK\n";
		}
	}
	return 0;
}


