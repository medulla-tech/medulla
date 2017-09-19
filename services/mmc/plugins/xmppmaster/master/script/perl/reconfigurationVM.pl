#!/usr/bin/perl
use warnings;
use File::Copy;
use Getopt::Std;

$nb=0;
$os='';

$usage="Usage : $0  -h < (1) Debian - (2) RedHat - (3) Oracle VM > -d <dhcp 0/1> -i [IP] -m [Adresse Mac (oblogatoire pour redhat et oracleVM)] -n [Netmask] -g [Getway]";
$nboptionObligatoire=3;

%optionObligatoire= (

	'h' => 1,
	'd' => 1,
	'm' => 1
	
);
getopts( "h:d:i:m:n:g:", \%opts ) or &gestionErreur();

foreach $key( sort keys %opts ) {

	$nb=&controleParametre($key,\$nb);
}

if ($nb != $nboptionObligatoire) {

	&gestionErreur("Parametre insuffisant");
}

$os=$opts{'h'};
$dhcp=$opts{'d'};

if ($os ne '1' && $os ne '2' && $os ne '3') {

        &gestionErreur("Identification de la machine erronne");
}

$adresseMac=$opts{'m'};
&gestionErreur("AdessseMac obligatoire") if (!$adresseMac);

# controle des data si pas dhcp ( =0 ) 
if (!$dhcp ) {

	$ip=$opts{'i'};
	$adresseMac=$opts{'m'};
	$netmask=$opts{'n'};
	$getway=$opts{'g'};

	&gestionErreur("IP non renseignee") if (!$ip);
	&gestionErreur("Netmask non renseigne") if (!$netmask);
	&gestionErreur("getway non renseignee") if (!$getway);
	
}

@cmdSys=&debian($dhcp,$ip,$adresseMac,$netmask,$getway) if ($os eq 1);
@cmdSys=&redhat($dhcp,$ip,$adresseMac,$netmask,$getway) if ($os eq 2);
@cmdSys=&oraclevm($dhcp,$ip,$adresseMac,$netmask,$getway) if ($os eq 3);

# reboot
system(@cmdSys);
exit 0;


# =========================================
#               Fonctions 
# =========================================

#-----------------------------------------#
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
		
		$nb+=$optionObligatoire{$cle};
	}
	
	return $nb;
}
#-----------------------------------------#
sub debian($$$$$) {

	($dhcp,$ip,$adresseMac,$netmask,$getway)=@_;
	
	$date_save=`date +'%Y%m%d%H%M%S'`;
	chomp $date_save;
	
	$fichier_ip_debian='/etc/network/interfaces';
    $fichier_ip_debian_sav=$fichier_ip_debian."_du_$date_save";
    $fichier_ip_debian_new=$fichier_ip_debian.".new";
   
	# sauvegarde du fichier
	&sauvegarde_fic("$fichier_ip_debian" , "$fichier_ip_debian_sav");
	
	# recherche de la carte
	$cmd="ifconfig |grep -i 'HWaddr $adresseMac'|cut -f1,1 -d' '";
	$eth=`$cmd`;
	chomp $eth;
	$eth=~s/ +//g;

	# si pas dhcp
	if (!$dhcp) {
	
		# modification IP
		$trouve=0;
		$nbModifAFaire=0;
	}
	
	open(IN,"$fichier_ip_debian") or die "$!";
	open(OUT,">$fichier_ip_debian_new") or die "$!";
	
	# pas dhcp demande
	if (!$dhcp) {
	
		# recherche si on est en dhcp 
		$rechercheDhcp=`grep dhcp $fichier_ip_debian`;
		chomp $rechercheDhcp;

		# on est pas en dhcp reseau
		if (!$rechercheDhcp) {
		
			while(defined($enreg=<IN>)) {
					
				chomp $enreg;
				if ($enreg=~/$eth/) {
				
					$trouve=1;
				}
				else {
						
					if ($trouve) {
						
						if (defined($ip) && $enreg=~/address/gi) {
								
							$enreg="address $ip";
							$nbModifAFaire++;
						}
						elsif (defined($netmask) && $enreg=~/netmask/gi) {
					
							$enreg="netmask $netmask";
							$nbModifAFaire++;
						}
						elsif ($enreg=~/gateway/gi) {
					
							$enreg="gateway $getway";
							$nbModifAFaire++;
						}
		
						# reinitialisation du compteur si les modif sont effectuees
						$trouve=0 if ($nbModifAFaire==3);
					}
				}
				print OUT $enreg,"\n";
			}
		}
		else {
			# en est en dhcp on bascule en static
			print OUT "auto $eth\n";
			print OUT "iface $eth inet static\n";
			print OUT "address $ip\n";
#-----------------------------------------------------------
# il faut verifier si ca fonctionne sans network
# sinon il faut décommenter le code ci-dessous
#-----------------------------------------------------------			
#			# recuperation de IP du reseau
#			$network=`hostname -I`;
#			chomp $network;
#			print OUT "network $network\n";
#---------------------------------------------------------

			print OUT "netmask $netmask\n";
			print OUT "gateway $getway\n";
		}
	}
	else {
		# dhcp demande
		print OUT "auto $eth\n";
		print OUT "iface $eth inet dhcp\n";
	
	}
	
	close(IN);
	rename("$fichier_ip_debian_new","$fichier_ip_debian");
	
	@cmdSys="/etc/init.d/networking restart";

	return @cmdSys;
}
#-----------------------------------------#
sub redhat($$$$$) {

	($dhcp,$ip,$adresseMac,$netmask,$getway)=@_;
	
	($fichier_ip,$fichier_ip_new,$fichier_ip_sav)=&constructionFicIP();
	
	# modification IP et NETMASK
	$ipadrTrouve=0;
	$maskTrouve=0;
	$getWayTrouve=0;
	$bootprotoTrouve=0;
	
	$tmp=`basename $fichier_ip`;
	chomp $tmp;
	($a,$eth)=split /-/,$tmp;
	

	open(OUT,">$fichier_ip_new") or die "$!";

  
	# sauvegarde du fichier
	&sauvegarde_fic("$fichier_ip", "$fichier_ip_sav");
	
	open(IN,"$fichier_ip") or die "$!";
	
	# recherche si on est en dhcp 
	$rechercheDhcp=`grep dhcp $fichier_ip`;
	chomp $rechercheDhcp;
    
	
	
	# si dhcp non demande
	if (!$dhcp) {
	
		# on est pas en dhcp reseau
		if (!$rechercheDhcp) {
		
			while(defined($enreg=<IN>)) {
				
				chomp $enreg;
				if (defined($ip) && $enreg=~/IPADDR/i) {
					
					$enreg="IPADDR=$ip";
					$ipadrTrouve=1;
				}
				if (defined($netmask) && $enreg=~/NETMASK/i) {
					
					$enreg="NETMASK=$netmask";
					$maskTrouve=1;
							
				}
				if ($enreg=~/GATEWAY=/i ) {
				
					$enreg="GATEWAY=$getway";
					$getWayTrouve=1;
				}
		
				if ($enreg=~/BOOTPROTO/) {
		
					$enreg="BOOTPROTO=static";
					$bootprotoTrouve=1;
				}
				print OUT $enreg,"\n";
			}
			# si parametrage manquant on les crees
			print OUT "IPADDR=$ip\n" if ( !$ipadrTrouve && defined($ip));
			print OUT "NETMASK=$netmask\n" if ( !$maskTrouve && defined($netmask));
			print OUT "GATEWAY=$getway\n" if ( !$getWayTrouve );
			print OUT "BOOTPROTO=static\n" if ( !$bootprotoTrouve );
			
		}
		else {
			# en est en dhcp on bascule en static
			print OUT "DEVICE=$eth\n";
			print OUT "BOOTPROTO=static\n";
			print OUT "ONBOOT=yes\n";
			print OUT "NETMASK=$netmask\n";
			print OUT "GATEWAY=$getway\n";
			print OUT "IPADDR=$ip\n";
			print OUT "USERCTL=no\n";
			#-----------------------------------------------------------
			# il faut verifier si ca fonctionne sans network
			# sinon il faut décommenter le code ci-dessous
			#-----------------------------------------------------------			
			#			# recuperation de IP du reseau
			#			$network=`hostname -I`;
			#			chomp $network;
			#			print OUT "network=$network\n";
			#---------------------------------------------------------
		}
	}
	else {
		# si dhcp demande
		print OUT 'DEVICE='.$eth,"\n";
		print OUT 'ONBOOT=yes',"\n";
		print OUT 'BOOTPROTO=dhcp',"\n";
	}
	
	# on renome le fichier new  
	rename("$fichier_ip_new","$fichier_ip");
	
	@cmdSys="/etc/init.d/network restart";
	
	return @cmdSys;
}
#-----------------------------------------#
sub oraclevm($$$$$) {

	($dhcp,$ip,$adresseMac,$netmask,$getway)=@_;
	
	($fichier_ip,$fichier_ip_new,$fichier_ip_sav)=&constructionFicIP();
	
	$tmp=`basename $fichier_ip`;
	chomp $tmp;
	($a,$eth)=split /-/,$tmp;
	
	# sauvegarde du fichier
	&sauvegarde_fic("$fichier_ip", "$fichier_ip_sav");
	
	open(OUT,">$fichier_ip_new") or die "$!";
	
	# si pas dhcp
	if (!$dhcp) {
	
		print OUT "PEERDNS=no\n";
		print OUT "GATEWAY=$getway\n";
		print OUT "NETMASK=$netmask\n";
		print OUT "IPADDR=$ip\n";
		print OUT "BOOTPROTO=static\n";
		print OUT "ONBOOT=yes\n";
		print OUT "NM_CONTROLLED=no\n";
		print OUT "DEVICE=$eth\n";
	}
	else {
		# si dhcp
		print OUT 'DEVICE="'.$eth.'"',"\n";
		print OUT 'ONBOOT="yes"',"\n";
		print OUT 'BOOTPROTO="dhcp"',"\n";
	}
	# on renome le fichier new  
	rename("$fichier_ip_new","$fichier_ip");
	
	@cmdSys="/etc/init.d/network restart";
	
	return @cmdSys;
}
#-----------------------------------------#
sub constructionFicIP() {

	$date_save=`date +'%Y%m%d%H%M%S'`;
	chomp $date_save;
	
	$rep='/etc/sysconfig/network-scripts';
	
    # recherche du fichier ifcfg
	$cmd="ifconfig -a |grep -i  $adresseMac";
	$fichier_ip_redhat=`$cmd`;
	chomp $fichier_ip_redhat;

	($fichier_ip_redhat)=split(/ /,$fichier_ip_redhat);
    $fichier_ip_redhat=~s/ +//g;
	$fichier_ip_redhat='ifcfg-'.$fichier_ip_redhat;
	
	$fichier_ip_redhat=$rep.'/'.$fichier_ip_redhat;
    $fichier_ip_redhat_sav=$fichier_ip_redhat."_du_$date_save";
    $fichier_ip_redhat_new=$fichier_ip_redhat.".new";

	return $fichier_ip_redhat,$fichier_ip_redhat_new,$fichier_ip_redhat_sav;
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