#!/usr/bin/perl -w
#
# $Id: inifile.pl 2307 2005-06-13 09:40:44Z root $
#
# Linbox Rescue Server
# Copyright (C) 2005  Linbox FAS
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# Cette structure est organisee comme indique ci-dessous. Les elements 'name'
# sont les noms des sections.
#
#   %conf = (
#       'order' => [ 'name1', 'name2', 'nameN', ...] ,
#
#       'data'  => {
#           'name1' => [ 'key1', 'val1', 'key2', 'val2', .... 'keyN', 'valN' ],
#
#           'name2' => [ 'key1', 'val1', .... 'keyN', 'valN' ],
#
#           'nameN' => [ 'key1', 'val1', .... 'keyN', 'valN' ],
#       }
#
#   );
#
#

# iniNew(\%conf)
# Creation et init d'une structure inifile vide.
#
sub iniNew
{
my $conf = shift ;

 %$conf = () ;
 $$conf{'order'} = [ ] ;
 $$conf{'data'} = { } ;

1;
}


# bool iniLoad ($filename, \%conf)
# Charge un fichier ini dans la structure %conf donnee en arg.
#
sub iniLoad
{
my ($file,$conf) = @_ ;

my @order ;
my %data ;

my @blks ;
my $buf ;
my @bl ;
my ($line, $k, $v) ;
my @ls ;
my $secname = "-" ; # S'il y a des lignes avant la 1ere section.

 open(FF, $file) or die "iniLoad: '$file': $!\n" ;
	while (<FF>) {
		s/^[ \t]+// ;
		s/[ \t\n]+$/\n/ ;
		
		$buf .= $_ ;
	}
 close(FF) ;

 # Init structure:
 %{$conf} = () ;


 # Ajout d'un '\n' au debut de buf. Sinon le
 # split ne marche pas dans certains cas:
 #
 $buf = "\n" . $buf ;
 @blks = split(m/(\n\[.+?\])/s, $buf) ;
 
 while (scalar(@blks)) {
 	$buf = shift(@blks) ;
 	$buf =~ s/^\n+// ;
 	$buf =~ s/\n+$// ;
	@bl = split(m/\n/, $buf ) ;
 	
	if (not defined($bl[0])) {
		next ;
	}
 	elsif (grep(m/^\[.+]$/, $bl[0]) and scalar(@bl)==1) {
 		$secname = $bl[0] ;
 		$secname =~ s/[\[\]]//g ;
 		push @order, $secname ;
 	}
 	else {
 		@ls = () ;
 		foreach $line (@bl) {
 			($k, $v) = split(m/[ \t]*=[ \t]*/, $line, 2) ;
 			push @ls, $k, $v ;
 		}
 	
 		$data{$secname} = [ @ls ] ;
 	}
 }

 # Structure finale:
 $$conf{'order'} = [ @order ] ;
 $$conf{'data'} = { %data } ;

1;
}


# bool iniHasSection (\%conf, $section)
# Retourne 1 si la section $section existe, 0 sinon.
#
sub iniHasSection
{
 my ($conf,$section) = @_ ;
 return 1 if (exists(${$conf}{'data'}{$section}) ) ;
 return 0 ;
}



# @names iniGetSections (\%conf) ;
# Retourne les noms de sections dans leur ordre d'apparition.
#
sub iniGetSections
{
	return @{ ${$_[0]}{'order'} } ;
}


# iniDeleteSection (\%conf, $section)
# Suppression d'une section et de son contenu.
# Retourne 1 si OK, ou 0 si erreur.
#
sub iniDeleteSection
{
my ($conf,$section) = @_ ;
my @neworder ;

 return 0 if (not iniHasSection($conf,$section)) ;
 
 delete $$conf{'data'}{$section} ;

 @neworder = grep { $_ ne $section } @{ $$conf{'order'} } ;
 $$conf{'order'} = [ @neworder ] ;

1;
}


# iniAddSection(\%conf, $section)
# Ajout d'une nouvelle section vide.
# Retourne 1 si OK, ou 0 si erreur.
#
sub iniAddSection
{
my ($conf,$section) = @_ ;

 return 0 if (iniHasSection($conf,$section)) ;

 push @{ $$conf{'order'} }, $section ;
 
 $$conf{'data'}{$section} = [] ;  # La valeur de la clef doit etre une liste.
 
1;
}



# @keys iniGetKeys(\%conf, $section)
# Retourne toutes les clefs d'une section dans leur ordre d'apparition.
# Note: Il peut y avoir plusieurs clefs identiques. L'indice d'une clef dans
# la liste renvoyee correspond bien a l'indice a utiliser avec iniGet().
#
sub iniGetKeys
{
my ($conf,$section) = @_ ;
my ($k,$i) ;
my $lsref ;
my @out = () ;

  return () if (not iniHasSection($conf,$section)) ;

  $lsref = $$conf{'data'}{$section} ;
  
  for ($i=0;  $i<scalar(@$lsref);  $i+=2) {
  	$k = $$lsref[$i] ;
  	push @out, $k ;
  }

 return @out ;
}


# bool iniHasKey (\%conf, $section, $key)
# Retourne 1 si la clef $key existe, dans la section $section.
#
sub iniHasKey
{
 my ($conf,$section,$key) = @_ ;
 my @clefs = iniGetKeys($conf,$section)  ;

 map { $_ = lc($_) } @clefs ;
 $key = lc($key) ;

 return 1 if ( grep { $_ eq $key } @clefs ) ;
 return 0 ;
}


# $val iniGetVal(\%conf,$section,$key)
# Retourne la valeur $val de la clef $key dans la section $section.
# Si plrs clefs $key de meme nom existent seule la val de la premiere clef
# rencontree est retournee.
# Retourne une chaine vide si clef non trouvee.
#
sub iniGetVal
{
my ($conf,$section,$key) = @_ ;
my ($k,$v,$i) ;
my $lsref ;

  return "" if (not iniHasSection($conf,$section)) ;
    
  $lsref = $$conf{'data'}{$section} ;
  $key = lc($key) ;
  $v = "" ;
  
  for ($i=0 ;  $i < scalar(@$lsref)  ;  $i += 2) {
  	$k = lc( $$lsref[$i] ) ;
  	if ($k eq $key ) {
  		$v = $$lsref[$i+1] ;
  		last ;
  	}
  }

return $v ;
}


# iniSetVal(\%conf,$section,$key,$val)
# Affectation de $val a la clef $key dans la section $section.
# La clef est ajoutee si elle n'existe pas.
# Retourne 1 si OK, ou 0 si erreur.
#
sub iniSetVal
{
my ($conf,$section,$key,$val) = @_ ;
my ($k,$i,$found) ;
my $lsref ;

  return 0 if (not iniHasSection($conf,$section)) ;
    
  $lsref = $$conf{'data'}{$section} ;
  $key = lc($key) ;
  $found = 0 ;
    
  for ($i=0 ;  $i < scalar(@$lsref)  ;  $i += 2) {
  	$k = lc( $$lsref[$i] ) ;
  	if ($k eq $key ) {
  		$$lsref[$i+1] = $val ;
  		$found = 1 ;
  		last ;
  	}
  }

  if (not $found) {
  	push @$lsref, $key, $val ;
  }

1 ;
}



# ($key,$val) iniGet(\%conf,$section,$pos)
# Retourne 2 elements $key+$val de la clef se trouvant à la position $pos
# dans la section $section. La 1ere clef est à la position 0.
# Retourne un couple vide si erreur.
#
sub iniGet
{
my ($conf,$section,$keypos) = @_ ;
my ($k,$v,$realpos) ;
my $lsref ;

  return ("","") if (not iniHasSection($conf,$section)) ;
    
  $lsref = $$conf{'data'}{$section} ;
  $realpos = $keypos * 2 ;

  if (defined($$lsref[$realpos+1])) {
  	$k = $$lsref[$realpos] ;
  	$v = $$lsref[$realpos+1] ;
  }
  else {
  	($k,$v) = ("","") ;
  }

return ($k,$v) ;
}


# iniSet(\%conf,$section,$pos,$key,$val)
# Modifie $key et $val qui se trouvent à la position $pos dans la section
# $section. La 1ere clef est à la position 0.
# Retourne 1 si OK, ou 0 si erreur.
#
sub iniSet
{
my ($conf,$section,$keypos,$key,$val) = @_ ;
my ($lsref,$realpos) ;

  return 0 if (not iniHasSection($conf,$section)) ;
    
  $lsref = $$conf{'data'}{$section} ;
  $realpos = $keypos * 2 ;

  if (defined($$lsref[$realpos+1])) {
  	$$lsref[$realpos]   = $key ;
  	$$lsref[$realpos+1] = $val ;
  }
  else {
  	return 0 ;
  }

return 1 ;
}



# @vals iniGetValues (\%conf, $section, $key1, $key2, $key3, ...)
# Retourne une liste de valeurs correspondant a une liste de clefs donnees.
#
sub iniGetValues
{
my $conf = shift ;
my $section = shift ;

my @vals = () ;
my ($k,$v) ;

 return if (not iniHasSection($conf,$section)) ;

 foreach $k (@_) {
 	$v = iniGetVal($conf, $section, $k) ;

 	if (length($v)) {
 		push @vals, $v ;
 	}
 	else {
 		push @vals, '' ;
 	}
 }

 return @vals ;
}


# iniSave ($file, \%conf)
# Sauvegarde dans le fichier $file d'une structure %conf chargee avec
# iniLoad() . Si certaines valeurs contiennent plrs lignes, alors la
# paire key=val est repetee en autant de lignes necessaires.
#
sub iniSave
{
my ($file,$conf) = @_ ;
my ($s,$k,$v,$i) ;

my @sections = iniGetSections($conf) ;
my (@clefs, @pairs) ;

 open(FF, "> $file") or die "$!" ;

	foreach $s (@sections) {
		print FF "[$s]\n" ;
		
		@clefs = iniGetKeys($conf,$s) ;
		
		for ($i=0; $i<scalar(@clefs); $i++) {
			($k,$v) = iniGet($conf,$s,$i) ;
			if (length($v)) {
				# Uniquement les valeurs non nulles
				@pairs = split(m/\n/,$v) ;
				@pairs = map { $_ = "$k=$_" } @pairs ;
				print FF join("\n", @pairs), "\n" ;
			}
		}
		
		print FF "\n" ;
	}

 close(FF) ;

1;
}



# End Of Module ///////////////////////////////////////////////////////////////
1;
#//////////////////////////////////////////////////////////////////////////////
