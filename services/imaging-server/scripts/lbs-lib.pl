#!/usr/bin/perl
#
# $Id: lbs-lib.pl 4962 2009-02-20 16:10:10Z nicolas $
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

require "inifile.pl" ;

#/////////////////////////////////////////////////////////////////////////////
# G L O B A L S
#/////////////////////////////////////////////////////////////////////////////


$_lbslibversion = "1.5.0" ;
$_lbsdebug      = 0 ;
$WOL_EXTENSION  = "wol";

%_errors_en = (
        'RAW' =>                q($1),
        'MAC_BAD'=>             q('$1': Invalid MAC address.),
        'MAC_UNK' =>            q('$1': Unknown MAC address.),
        'MAC_EXISTS' =>         q('$1': MAC address already existing.),
        'HOST_UNK' =>           q('$1': Unknown host.),
        'HOST_USED' =>          q('$1': Name already used.),
        'CANT_INCLUDE' =>       q(Can't include '$1'.),
        'CANT_SAVE' =>          q(Can't save '$1'.),
        'CANT_WRITE' =>         q(Can't write '$1'.),
        'CANT_GETUNIQUE' =>     q(Can't get unique name.),
        'CANT_OPEN' =>          q('$1': Open failed.),
        'SECT_UNK' =>           q('$1': Unknown section.),
        'ITEM_UNK' =>           q('$1': Inknown item.),
        'ITEM_NF' =>            q('$1': Item not found.),
        'MENU_CANTAPPEND' =>    q('$1': Can't append menu.),
        'FILE_NF' =>            q('$1': No such file or directory.),
        'FILE_LOAD' =>          q('$1': Loading failed.),
        'FILE_REMOVE' =>        q('$1': Remove failed.),
        'FILE_EXISTS' =>        q('$1': File already exists.),
        'ENTRY_EXISTS' =>       q('$1': Entry already exists.),
        'IMG_NF' =>             q('$1': Image not found.),
        'IMG_NFINTO' =>         q('$1': Image not found into '$2'),
        'IMG_EXISTS' =>         q('$1': Image already exists.),
        'IMG_USEDBYMENU' =>     q('$1': Image currently used by menu '$2'.),
        'IMG_USEDBYHOST' =>     q('$1': Image used by host '$2'.),
        'IMG_EMPTYBASE'  =>     q(No base images found into '$1'.),
        'IMG_MVLINKINVAL' =>    q(Image '$1': invalid move operation.),
        'LINK_NF' =>            q('$1': Link not found.),
) ;


%_errors_fr = (
        'RAW' =>                q($1),
        'MAC_BAD'=>             q('$1': Adresse MAC invalide.),
        'MAC_UNK' =>            q('$1': Adresse MAC inconnue.),
        'MAC_EXISTS' =>         q('$1': Adresse MAC déjà existante.),
        'HOST_UNK' =>           q('$1': Machine inconnue.),
        'HOST_USED' =>          q('$1': Nom de machine déjà utilisé.),
        'CANT_INCLUDE' =>       q(Inclusion de '$1' impossible.),
        'CANT_SAVE' =>          q(Sauvegarde de '$1' impossible.),
        'CANT_WRITE' =>         q(Ecriture dans '$1' impossible.),
        'CANT_GETUNIQUE' =>     q(Impossible d'obtenir un nom unique.),
        'CANT_OPEN' =>          q('$1': Ouverture impossible.),
        'SECT_UNK' =>           q('$1': Section inconnue.),
        'ITEM_UNK' =>           q('$1': Item inconnu.),
        'ITEM_NF' =>            q('$1': Item introuvable.),
        'MENU_CANTAPPEND' =>    q(Ajout du menu '$1' impossible.),
        'FILE_NF' =>            q('$1': Fichier ou repertoire introuvable.),
        'FILE_LOAD' =>          q(Erreur de chargement de '$1'.),
        'FILE_REMOVE' =>        q(Erreur lors de l'effacement de '$1'.),
        'FILE_EXISTS' =>        q('$1': Fichier ou répertoire déjà existant.),
        'ENTRY_EXISTS' =>       q('$1': Entrée déjà existante.),
        'IMG_NF' =>             q('$1': Image introuvable.),
        'IMG_NFINTO' =>         q('$1': Image introuvable dans '$2'),
        'IMG_EXISTS' =>         q('$1': Image déjà existante.),
        'IMG_USEDBYMENU' =>     q('$1': Image en cours d'utilisation dans le menu '$2'.),
        'IMG_USEDBYHOST' =>     q('$1': image utilisée par la machine '$2'.),
        'IMG_EMPTYBASE'  =>     q(Il n'y a aucune image de base dans '$1'.),
        'IMG_MVLINKINVAL' =>    q(Image '$1': Déplacement de lien invalide.),
        'LINK_NF' =>            q('$1': Lien introuvable.),
) ;

%_lbserr = (
        'href' => \%_errors_en ,
        'func' => 'None' ,
        'mesg' => 'OK' ,
        'flag' => 0 ,
) ;

# @_protected_locals = qw(Backup-B Backup-L) ;
# @_protected_bases  = qw(Local-Disk Local-FLoppy Util-MemTest Util-Mbr) ;

#/////////////////////////////////////////////////////////////////////////////
# D E B U G
#/////////////////////////////////////////////////////////////////////////////


#/////////////////////////////////////////////////////////////////////////////
# E R R O R
#/////////////////////////////////////////////////////////////////////////////

# $mesg textSub(\%href,$label,[$substitutes]*)
#
sub textSub
{
my $href = shift ;
my $label = shift ;
my ($i,$j,$mesg) ;

 if (not exists($$href{$label})) {
        $mesg = "Unknown message label '$label'" ;
        if (scalar @_) { $mesg .= ", with args: " . join(",",@_) ;}
        return $mesg ;
 }
 else {
        $mesg = $$href{$label} ;
        for($i=0; $i<@_; $i++) {
                $j = $i+1 ;
                $mesg =~ s/\$$j/$_[$i]/g ;
        }
 }

 return $mesg ;
}


# lbsError($func, $label, [$args]*)
# Enregistre un message d'erreur $label. $func doit etre le nom de la fct
# appelante. $label est un code erreur existant. $args sont des valeurs
# optionnelles à substituer dans le message final si celui-ci le necessite.
#
sub lbsError
{
my $func = shift ;
my $label = shift ;
my $mesg ;

 $mesg = textSub( $_lbserr{'href'}, $label, @_) ;

 $_lbserr{'func'} = $func ;
 $_lbserr{'mesg'} = $mesg ;
 $_lbserr{'flag'} = 1 ;

1;
}


# lbsClearError(void)
# Effacement des messages d'erreur, et reset du flag d'erreur.
#
sub lbsClearError
{
        $_lbserr{'func'} = 'None' ;
        $_lbserr{'mesg'} = 'OK' ;
        $_lbserr{'flag'} = 0 ;
}


# lbsGetError
# Retourne le dernier message d'erreur enregistre.
#
sub lbsGetError
{
my $buf ;

        if ($_lbsdebug == 0) {
                return $_lbserr{'mesg'} ;
        }
        else {
                $buf = sprintf "Function %s:\n %s\n",
                               $_lbserr{'func'} , $_lbserr{'mesg'} ;
                return $buf ;
        }
}

# bool lbsErrorFlag(void)
# Retourne 1 si des erreurs se sont produites, ou 0 sinon.
#
sub lbsErrorFlag
{
        return $_lbserr{'flag'} ;
}


#/////////////////////////////////////////////////////////////////////////////
# U T I L
#/////////////////////////////////////////////////////////////////////////////

# @result listExclude ( \@liste, \@a_exclure )
# Supprimer les elements du 1er tableau qui sont presents dans le 2eme.
# Arguments: Deux references de tableaux (de mots) A et B
#            B contient la liste des mots que l'on veut exclure de A
# Retourne ce qui reste de A
# Note: Les listes A et B ne sont pas modifiées.
#
sub listExclude
{

my @result ;                            # Ce qui reste de $liste
my $liste   = $_[0] ;           # Liste de mots
my $exclure = $_[1] ;           # Mots à exclure de $liste
my ($i, $j, $flag) ;

        for $i (@$liste) {
                $flag=0 ;

                for $j (@$exclure) {
                        if ( $i eq $j ) { $flag=1; last ;}
                }

                if ($flag==0) { push @result, $i ;}
        }

return @result ;
}


# @commons listCommon (\@liste1, \@liste2)
# Retourne la liste des éléments presents à la fois dans @liste1 et @liste2.
# Arguments: 2 references de listes.
# Retourne:  liste des elements communs.
#
# NOTE: Cette routine suppose que dans une liste, chaque element est unique.
# D'où la presence de l'instruction 'last' juste après le 'push' .
#
sub listCommon
{
my $gauche = shift ;
my $droite = shift ;
my @out = () ;
my ($i,$j) ;

        for $i (@$gauche) {
                for $j (@$droite) {
                        if ( $i eq $j ) {
                                push @out, $i ;
                                last ;
                        }
                }
        }

return @out ;
}


# fileLoad($src, \$data)
# Retourne le nb d'octets lus.
#
sub fileLoad
{
my ($src,$data) = @_ ;
my $buf ;

 $$data = "" ;

 if (not open(F,$src)) {
        lbsError("fileLoad",'RAW', "$src: $!") ;
        return 0 ;
 }
        while(read(F,$buf,16384)) {
                $$data .= $buf ;
        }

 close(F) ;

return length($$data) ;
}


# fileSave($dest, \$data)
#
sub fileSave
{
my ($dest,$data) = @_ ;

 if (not open(F, "> $dest")) {
        lbsError("fileSave",'RAW',"$dest: $!") ;
        return 0 ;
 }
 print F $$data ;
 close(F) ;

1;
}


# $newstr addEmptyLine($text)
# Retourne une chaine terminee par une ligne vide. (Un double \n).
#
sub addEmptyLine
{
my $buf = $_[0] . "\n\n" ;

 $buf =~ s/\n+$/\n\n/s ;

return $buf ;
}


# $dir getDirName($path)
# Equivalent de la commande shell 'dirname'.
#
sub getDirName
{
 my @ls ;
 my $out ;

 if (not length($_[0])) {
        $out = "." ;
 }
 else {
        @ls = split( m(/+) , $_[0] ) ;
        pop(@ls) ;
        if (not scalar(@ls)) {
                if (grep(m(^/),$_[0])) {
                        $out = "/" ;
                }
                else {
                        $out = "." ;
                }
        }
        else {
                $out = join('/',@ls) || '/' ;
        }
 }

return $out ;
}


# $new encodeCP850($text)
#
#
sub encodeCP850
{
my $tbl_cp850="\x83\x84\x85\x82\x88\x89\x8a\x8b\x8c\x93\x94\x81\x96\x97\x98\x87";
my $tbl_latin="\xe2\xe4\xe0\xe9\xea\xeb\xe8\xef\xee\xf4\xf6\xfc\xfb\xf9\xff\xe7";

#my $tbl_cp850="\x203\x204\x205\x202\x210\x211\x212\x213\x214\x223\x224\x201\x226\x227\x230\x207";
#my $tbl_latin="\x342\x344\x340\x351\x352\x353\x350\x357\x356\x364\x366\x374\x373\x371\x377\x347";
#my $tbl_ascii="aaaeeeeiioouuuyc";

$_ = shift ;

 eval "tr/$tbl_latin/$tbl_cp850/" ;

return $_ ;
}

# $mac macFileName ($mac)
# Formatage d'une adresse MAC, pour servir de nom de fichier.
# Typiquement on supprime les ':', et on met le tout en majuscules.
#
sub toMacFileName
{
my $mac = shift ;
 $mac = uc($mac) ;
 $mac =~ s/:+//g ;
 return $mac ;
}


# @dirs readSubDirs($dirpath)
# Retourne la liste des sous-repertoires d'un repertoire $dirpath.
# Cela peut-etre des sous-reperts, ou des liens symboliques pointant vers
# des repertoires.
# Ne retourne rien si erreur.
#
sub readSubDirs
{
my $dirpath = shift ;
my @lsdir ;

 if (not opendir(REP,$dirpath)) {
        lbsError("readSubDirs",'RAW',"$dirpath: $!") ;
        return ;
 }
        @lsdir = grep !/^\.\.?$/, readdir(REP) ;

 closedir(REP) ;

 return grep { -d "$dirpath/$_" } @lsdir ;
}


#/////////////////////////////////////////////////////////////////////////////
# I N I T
#/////////////////////////////////////////////////////////////////////////////

# lbsSetLang($lang)
#
sub lbsSetLang
{
my $lang = shift ;

 if ($lang eq "fr") {
        $_lbserr{'href'} = \%_errors_fr ;
 }
 else {
        $_lbserr{'href'} = \%_errors_en ;
 }

1;
}


#/////////////////////////////////////////////////////////////////////////////
# E T H E R
#/////////////////////////////////////////////////////////////////////////////

# bool etherLoad ($etherfile, \%einfo)
# Arg: nom du fichier ether, et reference d'un hash.
# Retourne 1 si ok, et remplissage de %einfo.
# Ne retourne rien si erreur.
#
sub etherLoad
{
my $etherfile = shift ;
my $hdl = shift ;

my @buf ;

 %{$hdl} = () ;

 if (not -f $etherfile) {
        lbsError("etherLoad", 'FILE_NF', $etherfile) ;
        return ;
 }

 if (not open FILE, "$etherfile") {
        lbsError("etherLoad", 'RAW',"$etherfile: $!") ;
        return ;
 }

        while (<FILE>) {
                chomp() ;
                next if (not grep(m/^[ \t]*[\w]+/,$_)) ;

                # Trim left/right:
                s/^[ \t]+// ;
                s/[ \t]+$// ;

                @buf = split(m/[ \t]+/, $_, 3) ;

                $$hdl{ $buf[0] } = [ $buf[1], $buf[2] ] ;

        }

 close(FILE) ;

return 1 ;
}

# bool etherSize(\%einfo)
# Retourne le nombre de machines enregistrees.
#
sub etherSize
{
        return scalar( keys %{$_[0]} ) ;
}



# @list etherGetMacs(\%einfo)
# Retourne la liste des adresses MAC des machines.
# Se base sur la structure retournee par etherLoad().
#
sub etherGetMacs
{
 return sort( keys %{$_[0]} ) ;
}

# @list etherGetMacsFilterName(\%einfo, $regexp)
# Retourne la liste des adresses MAC des machines.
# Se base sur la structure retournee par etherLoad().
#
sub etherGetMacsFilterName
{
 my $ref = $_[0];
 my $re = $_[1];
 return sort( grep ( $ref->{$_}[1] =~ /$re/ , keys(%$ref) ) ) ;
}


# $name etherGetNameByMac (\%einfo, $mac)
# Retourne un nom d'hote à partir de son adresse MAC.
# Se base sur la structure retournee par etherLoad().
#
sub etherGetNameByMac
{
my $einfo = shift ;
my $mac = shift ;

 if ( exists($$einfo{$mac}) ) {
        return $$einfo{$mac}[1] ;
 }
 else {
        lbsError("etherGetNameByMac","MAC_BAD", $mac) ;
        return ;
 }
}

# $name etherGetIpByMac (\%einfo, $mac)
# Retourne d'adresse IP d'un hote à partir de son adresse MAC.
# Se base sur la structure retournee par etherLoad().
#
sub etherGetIpByMac
{
my $einfo = shift ;
my $mac = shift ;

 if ( exists($$einfo{$mac}) ) {
        return $$einfo{$mac}[0] ;
 }
 else {
        lbsError("etherGetIpByMac","MAC_BAD", $mac) ;
        return ;
 }
}


# $macaddr etherGetMacByName (\%einfo, $name, $isshortname ?)
# Retourne une adresse MAC a partir d'un nom d'hote.
# Se base sur la structure retournee par etherLoad().
# si shortname est defini, tronque chaque nom en version courte (nom netbios
# en principe)
#
sub etherGetMacByName
{
my $einfo = shift ;
my $name = shift ;
my $isshortname = shift ;
my ($k,$v, $l) ;

        # Ne pas differencier maj/min:
        $name = lc($name) ;

        foreach $k ( keys %{$einfo} ) {
                $v = ${$einfo}{$k} ;
                $l = lc( $$v[1] ) ;
                $l =~ s|.*/|| if defined($isshortname);
                return $k if ($l eq $name) ;
        }

 # Echec:
 lbsError("etherGetMacByName","HOST_UNK", $name) ;

 return ;
}



# @list etherGetNames(\%einfo)
# Retourne la liste des noms des machines
# Se base sur la structure retournee par etherLoad().
#
sub etherGetNames
{
my $k ;
my @out ;

        foreach $k (etherGetMacs($_[0])) {
                push @out, etherGetNameByMac($_[0], $k) ;
        }

return sort(@out) ;
}



# etherSave($etherfile, \%einfo)
# Inverse de etherLoad() : on ecrase le fichier ether avec le contenu
# de %einfo
# Retourne 1 si OK, ou 0 si erreur.
#
sub etherSave
{
my $etherfile = shift ;
my $einfo = shift ;

my ($mac,$ip,$name) ;

 if (not -f $etherfile) {
        lbsError("etherSave", "FILE_NF", $etherfile) ;
 }

 if (not open ETHER, ">$etherfile") {
         lbsError("etherSave","RAW","$!") ;
         return 0;
 }

        print ETHER "# MAC_ADDRESS     IP_ADDRESS    HOSTNAME\n\n" ;

        foreach $mac ( etherGetMacs($einfo) ) {
                $ip = etherGetIpByMac($einfo, $mac) ;
                $name = etherGetNameByMac($einfo, $mac) ;

                print ETHER "$mac $ip $name\n" ;
        }

 close(ETHER) ;

1;
}


# etherAdd(\%einfo, $mac, $ip, $name)
# Ajout d'une nvelle entree $mac dans le fichier ether.
# Retourne 1 si OK, ou 0 si erreur.
#
sub etherAdd
{
my ($einfo, $mac, $ip, $name) = @_ ;

        if (defined(etherGetMacByName($einfo, $name))) {
                lbsError("etherAdd","HOST_USED",$name) ;
                return 0 ;
        }

        if (exists($$einfo{$mac})) {
                lbsError("etherAdd","MAC_EXISTS",$mac) ;
                return 0 ;
        }

        $$einfo{$mac} = [ $ip, $name ] ;
        return 1 ;
1;
}



# etherDelete(\%einfo, $macaddr)
# Effacer l'entree $macaddr de la structure %einfo
# Retourne 1 si succes, ou 0 si erreur.
#
sub etherDelete
{
my $einfo = shift ;
my $mac = shift ;

        if (exists($$einfo{$mac})) {
                delete $$einfo{$mac} ;
                return 1 ;
        }
        else {
                lbsError("etherDelete","MAC_UNK",$mac) ;
                return 0;
        }
}


#//////////////////////////////////////////////////////////////////////////////
# I T E M S
#//////////////////////////////////////////////////////////////////////////////


# bool itemHasKey($text, $itemkey)
# Retourne 1 si la clef $itemkey est presente dans $text.
# Retourne 0 sinon.
#
sub itemHasKey
{
my ($text,$ikey) = @_ ;
my $l ;
my @lines ;

        @lines = split(m/\n/, $text) ;
        foreach $l (@lines) {
                next if (not length($l)) ;
                $l =~ s/^[ \t]+// ;
                return 1 if (grep(m/^$ikey/,$l)) ;
        }

return 0 ;
}


# $itemval itemGetVal($text,$itemkey)
# Retourne la valeur d'un item present dans la chaine $texte.
# $itemkey est la clef (title, partcopy, chainloader,...) de l'item pour
# lequel on recherhe la valeur. Elle se situe normalement en debut de ligne.
# Ne retourne rien si item non trouve.
#
sub itemGetVal
{
my ($text, $itemkey) = @_ ;
my ($l,$a,$b) ;
my @lines ;

        @lines = split(m/\n/, $text) ;
        foreach $l (@lines) {
                next if (not length($l)) ;
                $l =~ s/^[ \t]+// ;
                ($a,$b) = split(m/ +/,$l,2) ;

                if ($a eq $itemkey) {
                        return $b ;
                }
        }

return ;  # Echec
}


# $newtext itemChangeVal($text,$itemkey,$itemval)
# Remplace dans $text la valeur de $itemkey, par $itemval.
# Retourne le texte modifie, ou $text si $itemkey non trouve.
#
sub itemChangeVal
{
my ($text,$itemkey,$itemval) = @_ ;
my ($l,$a,$b,$i) ;
my @lines ;

        @lines = split(m/\n/, $text) ;
        for ($i=0;  $i<scalar(@lines);  $i++) {
                $l = $lines[$i] ;
                next if (not length($l)) ;
                $l =~ s/^[ \t]+// ;
                ($a,$b) = split(m/ +/,$l,2) ;

                if ($a eq $itemkey) {
                        $lines[$i] = "$itemkey $itemval" ;
                }
        }

return join("\n", @lines) ;
}


#//////////////////////////////////////////////////////////////////////////////
# H O S T   C O N F I G U R A T I O N   F I L E
#//////////////////////////////////////////////////////////////////////////////

# hdrNew(\%hdr)
# Creation et init d'une structure %hdr vide.
#
sub hdrNew
{
my $hdr = shift ;
my %ini ;

 iniNew(\%ini) ;

 %$hdr = (
        'file'  => undef ,
        'ini'   => { %ini },
        'inc'   => { },
 ) ;

1;
}


# hdrLoad($file, \%hdr)
#
sub hdrLoad
{
my ($file,$hdr) = @_ ;
my %ini = () ;
my @sections ;
my ($s,$k,$v,$p,$i,$f,$buf) ;
my @clefs ;
my %inc = () ;

  if (not -f $file) {
        lbsError("hdrLoad","FILE_NF", $file) ;
        return 0 ;
  }

  if (not iniLoad($file,\%ini)) {
        lbsError("hdrLoad","FILE_LOAD",$file) ;
        return 0 ;
  }

  $p = getDirName($file) ;
  @sections = iniGetSections(\%ini) ;

  # Loading included files:
  foreach $s (@sections) {
        @clefs = iniGetKeys(\%ini, $s) ;
        for ($i=0; $i<scalar(@clefs); $i++) {
                ($k,$v) = iniGet(\%ini,$s,$i) ;
                if ($k eq "include") {

                        # Path relatif ou absolu?
                        if (grep m(^/), $v) {
                                $f = $v ;
                        }
                        else {
                                $f = "$p/$v" ;
                        }

                        if (not fileLoad($f, \$buf)) {
                                # Warning:
                                lbsError("hdrLoad","CANT_INCLUDE",$f) ;
                        }
                        else {
                                # No '\n' at end of file:
                                $buf =~ s/\n+$//s ;
                                $inc{$v} = $buf ;
                        }
                }
        }
  }

  # Final struct:
  %$hdr = () ;
  $$hdr{'file'} = $file ;
  $$hdr{'ini'} = { %ini } ;
  $$hdr{'inc'} = { %inc } ;

1;
}

# hdrSave($file, \%hdr)
#
sub hdrSave
{
my ($file,$hdr) = @_ ;
my ($k,$p,$f,$buf,$res) ;

my $incref = $$hdr{'inc'} ;
my $iniref = $$hdr{'ini'} ;

  if (not iniSave($file,$iniref)) {
        lbsError("hdrSave","CANT_SAVE",$file) ;
        return 0 ;
  }

  $res = 1 ;
  $p = getDirName($file) ;

  foreach $k (keys %{$incref}) {
        $buf = $$incref{$k} ;

        # Path relatif ou absolu?
        if (grep m(^/), $k) {
                $f = $k ;
        }
        else {
                $f = "$p/$k" ;
        }

        if (not fileSave("$f", \$buf)) {
                lbsError("hdrSave","CANT_WRITE",$f) ;
                $res = 0 ;
        }
  }

return $res ;
}



# @names hdrGetMenuNames (\%hdr)
# Retourne les noms des sections decrivant les menus. Elles ont toutes le
# prefixe 'menu' dans leur nom.
#
sub hdrGetMenuNames
{
 my $hdr = $_[0] ;
 return grep m/^menu/i, iniGetSections($$hdr{'ini'}) ;
}


# @menukeys @names hdrSelectMenuKey (\%hdr, $key)
# Retourne une liste contenant les valeurs de $key pour chaque menu de %hdr.
# Si un menu ne possede pas de clef $key, une chaine vide est utilisee comme
# valeur de retour.
#
sub hdrSelectMenuKey
{
my ($hdr,$key) = @_ ;
my ($s,$v) ;
my @out ;
my $iniref = $$hdr{'ini'} ;
my @sections = hdrGetMenuNames($hdr) ;

        for $s (@sections) {
                if (iniHasKey($iniref,$s,$key)) {
                        $v = iniGetVal($iniref,$s,$key) ;
                }
                else {
                        $v = "" ;
                }

                push @out, $v ;
        }

return @out ;
}


# hdrAddMenu(\%hdr, $menu)
# Ajout d'une section de type 'menu' dans la config %hdr.
# Retourne 1 si OK, ou 0 si erreur.
#
sub hdrAddMenu
{
my ($hdr,$menu) = @_ ;
 return iniAddSection($$hdr{'ini'},$menu) ;
}

# hdrDeleteMenu(\%hdr,$menu)
# Suppression d'un menu dans la config %hdr.
#
sub hdrDeleteMenu
{
 my ($hdr,$menu) = @_ ;
 return iniDeleteSection( $$hdr{'ini'}, $menu) ;
}

# hdrDeleteMenu(\%hdr,$sect)
# Suppression d'une section dans la config %hdr.
#
sub hdrDeleteSection
{
 my ($hdr,$sect) = @_ ;
 return iniDeleteSection( $$hdr{'ini'}, $sect) ;
}


# $menu hdrFindMenu(\%hdr, $key, $val)
# Retourne le nom du menu (c.a.d de la  section) contenant une clef $key
# de valeur $val.
# Retourne undef si echec.
#
sub hdrFindMenu
{
my ($hdr,$key,$val) = @_ ;

my $iniref = $$hdr{'ini'} ;
my @menus = hdrGetMenuNames($hdr) ;
my ($m,$v) ;

        for $m (@menus) {
                if (iniHasKey($iniref,$m,$key)) {
                        $v = iniGetVal($iniref,$m,$key) ;
                        return $m if ($v eq $val) ;
                }
        }

return undef ;
}



# $name hdrUniqueName (\%hdr)
# Retourne un nom de menu ne faisant pas partie des noms existants dans %hdr.
#
sub hdrUniqueName
{
my $hdr = shift ;
my @menus = hdrGetMenuNames($hdr) ;
my $top ;
my @lst ;

 @lst = map { lc } @menus ;
 # 20090220: behavior changed with perl 5.10
 # http://search.cpan.org/~rgarcia/perl-5.10.0/pod/perl5100delta.pod#substr()_lvalues_are_no_longer_fixed-length
 @lst = map { substr($_,4) } @lst ;
 @lst = sort { $a <=> $b } @lst ;  # Forcer un tri de type numerique

 $top = pop @lst ;
 $top++ ;

 if (grep { $_ eq $top } @menus) {
        lbsError("hdrUniqueName","CANT_GETUNIQUE") ;
        return ;
 }

return "menu" . $top ;
}



# $val hdrGetVal(\%hdr, $section, $key)
# Recup de la valeur d'une clef dans une section.
#
sub hdrGetVal
{
my ($hdr,$section,$key) = @_ ;

 return iniGetVal($$hdr{'ini'},$section,$key) ;
}

# hdrSetVal(\%hdr, $section, $key,$val)
# Modif de la valeur d'une clef dans une section.
#
sub hdrSetVal
{
my ($hdr,$section,$key,$val) = @_ ;

 return iniSetVal($$hdr{'ini'}, $section, $key, $val) ;
}



# int hdrFindMenuItem(\%hdr, $section, $itemkey)
# Localisation d'un item dans une $section. Retourne un couple de valeurs.
# La 1ere valeur indique l'endroit ou se trouve l'item:
#
#  0 : $itemkey introuvable
#  1 : $itemkey dans header.lst
#  2 : $itemkey dans un include
#
# La 2eme valeur est une adresse dont le type depend de la 1ere valeur:
#
#  Val1  Val2
#  0     $itemkey introuvable (val1=val2=0)
#  1     Un entier donnant la pos de la clef dans la $section.
#  2     Une clef de hachage associee au texte contenant $itemkey.
#
#
sub hdrFindMenuItem
{
my ($hdr,$section,$itemkey) = @_ ;
my ($k,$v,$i) ;
my @clefs ;

my $iniref = $$hdr{'ini'} ;
my $incref = $$hdr{'inc'} ;

 return (0,0) if (not iniHasSection($iniref,$section)) ;

 @clefs = iniGetKeys($iniref, $section) ;

 for ($i=0; $i<scalar(@clefs); $i++) {
        ($k,$v) = iniGet($iniref, $section, $i) ;

        if ($k eq "item") {
                return (1,$i) if (itemHasKey($v,$itemkey)) ;
        }
        elsif ($k eq "include") {
                return (2,$v) if (itemHasKey($$incref{$v},$itemkey)) ;
        }
 }

return (0,0) ;
}


# $val hdrGetMenuItem(\%hdr, $section, $item )
# Recup de la valeur d'un item d'une section $section.
# La recherche est effectuee sur les clefs 'item' et 'include' .
# Concernant 'include', la fct va chercher dans le fichier indique.
# Retourne la valeur trouvee, ou une chaine vide si echec.
#
sub hdrGetMenuItem
{
my ($hdr,$section,$item) = @_ ;
my @clefs ;
my ($i, $k, $v, $a) ;
my $iniref = $$hdr{'ini'} ;
my $incref = $$hdr{'inc'} ;

 if (not iniHasSection($iniref, $section)) {
        lbsError("hdrGetMenuItem","SECT_UNK",$section) ;
        return ;
 }

 $item = lc($item) ;

 @clefs = iniGetKeys($iniref, $section) ;
 for ($i=0; $i<scalar(@clefs); $i++) {
        ($k,$v) = iniGet($iniref, $section, $i) ;

        if ($k eq "item") {
                # Recherche dans header.lst
                if (defined($a = itemGetVal($v,$item))) {
                        return $a ;
                }
        }
        elsif ($k eq "include") {
                # Ou recherche dans les fichiers inclus:
                if (exists($$incref{$v})) {
                        if (defined($a = itemGetVal($$incref{$v},$item))) {
                                return $a ;
                        }
                }
        }
 }

return ;  # Echec
}


# hdrSetMenuItem(\%hdr, $section, $itemkey, $itemval)
#
#
sub hdrSetMenuItem
{
my ($hdr,$section,$itemkey,$itemval) = @_ ;
my ($where,$addr,$buf) ;
my $iniref = $$hdr{'ini'} ;
my $incref = $$hdr{'inc'} ;

 ($where,$addr) = hdrFindMenuItem($hdr,$section,$itemkey) ;

 if ($where == 0) {
        # Introuvable:
        iniSetVal($iniref,$section,"item","$itemkey $itemval") ;
 }
 elsif ($where == 1) {
        # Dans une clef 'item':
        iniSet($iniref,$section,$addr,"item","$itemkey $itemval") ;
 }
 elsif ($where == 2) {
        # Dans un 'include':
        $buf = $$incref{$addr} ;
        $$incref{$addr} = itemChangeVal($buf,$itemkey,$itemval) ;
 }
 else {
        # DEBUG
        lbsError("hdrSetMenuItem","RAW",
                 "BUG!: \$where==$where: invalid condition");
        die ;
 }

return 1 ;
}



# hdrGetMenuInfo (\%hdr, $section, \%info)
# Retourne diverses infos a partir d'une section de type 'menu'.
# Ces infos proviennent de plrs sources: des parametres du menu lui-meme,
# et des fichiers inclus s'il y en a.
# Retourne 1 si OK, ou 0 si erreur.
#
sub hdrGetMenuInfo
{
my ($hdr,$section,$info) = @_ ;
my ($t, $d, $res) ;
my $iniref = $$hdr{'ini'} ;

 if (not iniHasSection($iniref, $section)) {
        lbsError("hdrGetMenuInfo","SECT_UNK",$section) ;
        return 0 ;
 }

 # Init:
 $res = 1 ;
 %{$info} = () ;

 $$info{"def"}   = iniGetVal($iniref, $section, "def") ;
 $$info{"visu"}  = iniGetVal($iniref, $section, "visu") ;
 $$info{"image"} = iniGetVal($iniref, $section, "image") ;

 $t = hdrGetMenuItem($hdr, $section, "title") ;
 $d = hdrGetMenuItem($hdr, $section, "desc") ;

 if (not defined($d)) {
        $$info{"desc"} = "(nul)" ;
 }
 else {
        $$info{"desc"} = $d ;
 }

 # La presence d'un item 'title' est obligatoire:
 if (not defined($t)) {
        lbsError("hdrGetMenuInfo","ITEM_NF","title","section $section") ;
        $$info{"title"} = "(not found)" ;
        $res = 0 ;
 }
 else {
        $$info{"title"} = $t ;
        $res = 1 ;
 }

 return $res ;
}


# $string hdrConcatMenuItems(\%hdr, $section)
# Retourne une chaine dans laquelle sont concatenes tous les menuitems
# rencontres dans la section $section. Ceci concerne les clefs 'items' et
# 'include' .
# Une chaine vide peut etre retournee si aucun item n'est rencontre.
#
sub hdrConcatMenuItems
{
my ($hdr,$section) = @_ ;

my @clefs ;
my ($k,$v,$i) ;
my $iniref = $$hdr{'ini'} ;
my $incref = $$hdr{'inc'} ;
my @concat = () ;

 if (not iniHasSection($iniref, $section)) {
        lbsError("hdrConcatMenuItems","SECT_UNK",$section) ;
        return "" ;
 }

 @clefs = iniGetKeys($iniref, $section) ;
 for ($i=0; $i<scalar(@clefs); $i++) {
        ($k,$v) = iniGet($iniref, $section, $i) ;
        $k = lc($k) ;

        if ($k eq "item") {
                # Recherche dans header.lst
                push @concat, $v ;
        }
        elsif ($k eq "include") {
                # Ou recherche dans les fichiers inclus:
                if (exists($$incref{$v})) {
                        push @concat, $$incref{$v} ;
                }
        }
 }

return join("\n",@concat) ;
}


#//////////////////////////////////////////////////////////////////////////////
# H O S T   E N T R I E S   ---- previous ----
#//////////////////////////////////////////////////////////////////////////////


# bool hasBootMenu($home, $macaddr)
# Retourne 1 si la machine d'adresse $macaddr possede deja
# un fichier pour la config de son menu de boot.
#
sub hasBootMenu
{
my $mac = toMacFileName($_[1]) ;
my $path = $_[0] . "/cfg/" . $mac ;

        return 1 if (-f $path) ;

return 0
}


# @titles getBootMenuTitles($home, $macaddr)
# Recup des items 'title' du fichier de config de boot.
# La liste retournee est composee de 2 parties: le 1er element est le nom
# du menu par defaut. Les elements suivant sont les noms des menus.
#
sub getBootMenuTitles
{
my $home = $_[0] ;
my $mac = toMacFileName($_[1]) ;

my $menufile = $home . "/cfg/" . $mac ;
my @titles ;
my @buf ;
my $default_pos = 0 ;
my $default_name = "" ;

 # Retour d'une liste vide si pas de fichier:
 if (not -f $menufile) {
        lbsError("getBootMenuTitles","FILE_NF",$menufile) ;
        return [] ;
 }

 if (not open FF, "$menufile") {
        lbsError("getBootMenuTitles","RAW","$menufile: $!") ;
        return ;
 }

        while (<FF>) {
                chomp() ;
                if (grep(m/^default/, $_)) {
                        @buf = split(m/[ \t]+/, $_) ;
                        $default_pos = $buf[1] ;
                }
                if (grep(m/^title/, $_)) {
                        @buf = split(m/[ \t]+/, $_) ;
                        push @titles, $buf[1] ;
                }
         }

 close(FF) ;

 # Ajout du _nom_ du menu par defaut dans la liste finale:
 $default_name = $titles[$default_pos] ;
 unshift @titles, $default_name ;

return @titles ;
}



# makeUserMenu ($home, $macaddr)
# Genere le menu de demarrage d'une machine a partir de header.lst .
# Retourne 1 si OK, ou 0 si erreur.
#
sub makeUserMenu
  {
    my $home = $_[0] ;
    my $mac = toMacFileName($_[1]) ;

    my $defaultpos = 0 ;
    my @menus = () ;

    my $menupath = $home . "/cfg/" . $mac ;
    my $imagepath = $home . "/images/" . $mac ;
    my $menuheader = "" ;
    my $bootmenu = "" ;
    my $one = "" ;
    my $m ;
    my $numselect = 0 ;
    my %hdr ;
    my %minfo ;
    my $hostconf = $home . "/images/" . $mac . "/header.lst" ;
    my $imgname ;

    my $copynumdata;
    my $basenumdata ;

    # WOL requested ?
    if (-f $home . "/images/" . $mac . "/wol") {
      # check if the timestamp is not too old
      my $wol = $home . "/images/" . $mac . "/wol";
      my $ts = (stat($wol))[9];
      if (time() - $ts > 600) {
        # 10 minutes: the wol request has expired ...
        # we should tell the admin
      } else {
        # wol requested, use the alternate menu
        $hostconf = $home . "/images/" . $mac . "/header.lst.wol";
      }
      unlink($wol);
    }

    # Load header.lst
    if (not hdrLoad($hostconf, \%hdr)) {
      lbsError("makeUserMenu","FILE_LOAD",$hostconf) ;
      return 0 ;
    }

    if (-f "$imagepath/COPYNUM") {
      fileLoad("$imagepath/COPYNUM", \$copynumdata) ;
      chomp($copynumdata);
    } else {
      $copynumdata = "COPYNUM" ;
    }


    if (-f "$home/imgbase/BASENUM") {
      fileLoad("$home/imgbase/BASENUM", \$basenumdata) ;
      chomp($basenumdata);
    } else {
      $basenumdata = "BASENUM" ;
    }

    #
    my %conf = ();
    iniLoad("/etc/webmin/lbs/config", \%conf);
    my $revorestore = iniGetVal(\%conf, "-", "restore_type");
    my $revowait = iniGetVal(\%conf, "-", "mtftp_wait");
    my $grub_splashimage = iniGetVal(\%conf, "-", "grub_splashimage");
    my $grub_keymap = iniGetVal(\%conf, "-", "grub_keymap");

    #
    my $eth = "0";
    $eth = hdrGetVal(\%hdr, "header", "ethnum");
    my $kernelopts = "";
    $kernelopts = hdrGetVal(\%hdr, "header", "kernelopts");

    @menus = hdrGetMenuNames(\%hdr) ;

    foreach $m (@menus) {

      hdrGetMenuInfo(\%hdr, $m, \%minfo) ;

      if ($minfo{'visu'} eq "yes") {
        # Determiner la pos du menu par defaut:
        $defaultpos = $numselect if ($minfo{'def'} eq "yes") ;

        $one = hdrConcatMenuItems(\%hdr, $m) ;

        $one = encodeCP850($one) ;

        $imgname = $minfo{'image'} ;

        $one =~ s/MAC/$mac/ ;
        $one =~ s/PATH/$imagepath\/$imgname/g ;

        $one =~ s/COPYNUM/$copynumdata/ ;
        $one =~ s/BASENUM/$basenumdata/ ;


        if ($revorestore eq "" || $revorestore eq "0") {
          # tftp grub restore
          # nothing to do
        } else {
          # linux based restore
          if ($minfo{'image'} =~ /((Base|Local)-[0-9].*)/) {
            # base image restoration
            my $imgt = "imgbase";
            my $imgo = "revorestore";

            if ($revorestore eq "1") {
              $imgo = "revorestorenfs";
            } elsif ($revowait ne "0") {
              $imgo .= " revowait=$revowait";
            }
            if ($minfo{'image'} =~ /Local/) {
              $imgt = "images/$mac";
            }

            #print "$1 $revorestore \n";
            my $o_title = "";
            my $o_desc = "";
            foreach my $line (split (/\n/, $one)) {
              if ($line =~ /^\s*title /) {
                $o_title = $line;
              }
              if ($line =~ /^\s*desc /) {
                $o_desc = $line;
              }
            }
            $one = "$o_title\n$o_desc";
            if ($revorestore eq "1") {
              $one =~ s/(^\s*title.*)/$1 (NFS)/;
            } elsif ($revorestore eq "2") {
              $one =~ s/(^\s*title.*)/$1 (MTFTP)/;
            }
            $one .= "
kernel (nd)$home/bin/bzImage.initrd revosavedir=/$imgt/$imgname $imgo quiet revopost
initrd (nd)$home/bin/initrd.gz
";
            #print $one;
          }
        }



        $one = addEmptyLine($one) ;

        # adding of other linux boot options:
        if ($eth ne "0" && $eth ne "") {
          $one =~ s/(kernel \(nd\).* revo.*)/$1 revoeth$eth/;
        } else {
          # send the mac address on the command line to improve nic configuration
          $one =~ s/(kernel \(nd\).* revo.*)/$1 revomac=$mac/;
        }
        if ($kernelopts ne "") {
          $one =~ s/(kernel \(nd\).* revo.*)/$1 $kernelopts/;
        }

        $bootmenu .= $one ;

        $numselect++ ;
      }
    }

    $menuheader = hdrConcatMenuItems(\%hdr, "header") ;
    $menuheader =~ s/DEFNUM/$defaultpos/ ;
    if ($grub_keymap ne "") {
      $menuheader .= "\nkbd$grub_keymap\n";
    }
    if ($grub_splashimage ne "") {
      $menuheader .= "\nsplashimage (nd)$grub_splashimage\n";
    }
    $menuheader = addEmptyLine($menuheader) ;

    # Generation du fichier final:
    if (not open FF, "> $menupath") {
      lbsError("makeUserMenu","RAW","Writing '$menupath': $!") ;
      return 0 ;
    }

    print FF $menuheader ;
    print FF $bootmenu ;

    close(FF) ;

    return 1 ;
  }


# createEntry($lbs_home, $mac, $ip, $name)
# Creation d'une arborescence de base pour une nouvelle machine.
# On copie le repert skel/ et on cree un menu de conf par defaut.
#
sub createEntry
{
my ($home,$mac,$ip,$name) = @_ ;

my $macfile = toMacFileName($mac) ;
my $etherfile = "$home/etc/ether" ;
my $imgskel = "$home/imgskel" ;
my $hostdir = "$home/images/$macfile" ;
my %einfo ;
my $someone ;

 if (-e $hostdir) {
        lbsError("createEntry","ENTRY_EXISTS",$hostdir) ;
        return 0 ;
 }

 if (not etherLoad($etherfile, \%einfo)) {
        lbsError("createEntry","CANT_OPEN",$etherfile) ;
        return 0 ;
 }

 etherAdd(\%einfo, $mac, $ip, $name) or return 0 ;

 etherSave($etherfile, \%einfo) or return 0 ;

 if ( system("cp","-a","$imgskel", $hostdir)){
        lbsError("createEntry","RAW",$!) ;
        return 0 ;
 }

1;
}


# deleteEntry ($home, $macaddr)
# Efface les enregistrements d'une machine et toutes les données qui s'y
# rapportent.
# Arguments: le repertoire $home du LBS, et l'adresse MAC de la machine a
# effacer.
# Retourne 1 si OK, ou 0 si erreur.
#
sub deleteEntry
{
my ($home,$mac) = @_ ;

my %einfo ;
my $etherfile = $home . "/etc/ether" ;
my $macfile = toMacFileName($mac) ;

my $cfgfile =  $home . "/cfg/" . $macfile ;
my $inifile =  $home . "/log/" . $macfile . ".ini"  ;
my $inffile =  $home . "/log/" . $macfile . ".inf"  ;
my $imagedir = $home . "/images/" . $macfile ;

 # Suppression de l'entree dans ether:
 if (not etherLoad($etherfile, \%einfo)) {
        lbsError("deleteEntry","CANT_OPEN",$etherfile) ;
        return 0 ;
 }

 # Fichier des menus:
 unlink($cfgfile) if (-f $cfgfile) ;

 # Fichiers de log:
 unlink($inifile) ;
 unlink($inffile) ;

 # Repertoire des images:
 return 0 if (not -d $imagedir) ;
 if (system("rm", "-rf", "$imagedir")) {
        lbsError("deleteEntry","FILE_REMOVE",$imagedir) ;
        return 0 ;
 }

 etherDelete(\%einfo, $mac) ;
 etherSave($etherfile, \%einfo) ;

1;
}


# updateEntry($lbs_home, $macaddr)
# Fonction de mise a jour d'une entree.
# Pour l'instant, elle ne fait que creer le menu utilisateur final.
sub updateEntry
{
my ($home,$mac) = @_ ;

 if (not makeUserMenu($home,$mac)) {
        #lbsError("updateEntry","RAW","Problem making final user menu") ;
        return 0 ;
 }

 return 1 ;
}

#//////////////////////////////////////////////////////////////////////////////
# H O S T   D I R E C T O R I E S
#//////////////////////////////////////////////////////////////////////////////

# Fonctions: moveHdr2Local, moveLocal2Hdr, moveLocal2Base, moveBase2Hdr
#
# Les fonctions de deplacement d'image ci-dessus s'utilisent toutes de la
# meme maniere: elles s'appliquent a une machine particuliere, realisent des
# deplacements d'images entre le menu de demarrage (header.lst), le repertoire
# local de la machine, et le repertoire des images de base (imgbase/).
# Elles prennent au minimum 3 arguments:
#
#   $home:  le repertoire LBS racine.
#   $mac:   addresse MAC de la machine concernee.
#   $image: L'image que l'on veut deplacer. Le nom de catte image est le
#           nom de son sous-repertoire (ou du lien). Ex: Local-Disk .
#
# Un 4eme argument optionnel nomme $test, peut etre specifie. S'il vaut 1,
# alors la fonction realise toutes les verifications necessaires au
# deplacement de l'image, mais n'effectue pas reellement de deplacement.
# A utiliser pour savoir a l'avance si un deplacement est possible ou pas.
#
# Ces fonctions retournent 1 si OK, ou 0 si erreur.
#


# moveHdr2Local ($home, $mac, $image [, $test])
#
#
sub moveHdr2Local
{
my ($home,$mac,$image) = @_ ;
my $test = $_[3] || 0 ;

my $macfile = toMacFileName($mac) ;
my $hostdir = $home . "/images/" . $macfile ;
my $hostconf = $hostdir . "/header.lst" ;
my $menu ;
my %hdr ;

 if (not hdrLoad($hostconf, \%hdr)) {
        lbsError("moveHdr2Local","FILE_LOAD",$hostconf) ;
        return 0 ;
 }

 $menu = hdrFindMenu(\%hdr,"image",$image) ;
 if (not defined($menu) or not length($menu)) {
        lbsError("moveHdr2Local","IMG_NF",$image) ;
        return 0 ;
 }

 return 1 if ($test) ;

 hdrDeleteMenu(\%hdr, $menu) ;
 hdrSave($hostconf,\%hdr) ;

        # regular and scheduled menus should be sync before entering this menu
        # so either we should copy regular to scheduled, or
        # we commit the previous changes to the existing file
        if (-f "$hostconf.$WOL_EXTENSION") {
                hdrLoad("$hostconf.$WOL_EXTENSION", \%hdr);
                hdrDeleteMenu(\%hdr, $menu) ;
                hdrSave("$hostconf.$WOL_EXTENSION",\%hdr) ;
        } else {
                system("cp -a $hostconf $hostconf.$WOL_EXTENSION") ;
        }

1;
}


# moveLocal2Hdr($home, $mac, $image [, $test])
#
#
sub moveLocal2Hdr
{
my ($home,$mac,$image) = @_ ;
my $test = $_[3] || 0 ;

my $macfile = toMacFileName($mac) ;
my $hostdir = $home . "/images/" . $macfile ;
my $hostconf = $hostdir . "/header.lst" ;
my ($menu,$include) ;
my %hdr ;

 if (not hdrLoad($hostconf, \%hdr)) {
        lbsError("moveLocal2Hdr","FILE_LOAD",$hostconf) ;
        return 0 ;
 }

 $menu = hdrFindMenu(\%hdr,"image",$image) ;
 if (defined($menu)) {
        lbsError("moveLocal2Hdr","IMG_EXISTS",$image) ;
        return 0 ;
 }

 if (not -d "$hostdir/$image") {
        lbsError("moveLocal2Hdr","IMG_NF",$image) ;
        return 0 ;
 }

 return 1 if ($test) ;

 if (-f "$hostdir/$image/conf.txt") {
        $include = "$image/conf.txt" ;
 }
 else {
        $include = "" ;
 }

 $menu = hdrUniqueName(\%hdr) ;
 if (not hdrAddMenu(\%hdr, $menu)) {
        lbsError("moveLocal2Hdr","MENU_CANTAPPEND",$menu) ;
        return 0 ;
 }

 hdrSetVal(\%hdr, $menu, "def", "no") ;
 hdrSetVal(\%hdr, $menu, "visu", "yes") ;
 hdrSetVal(\%hdr, $menu, "image", $image) ;
 hdrSetVal(\%hdr, $menu, "include", $include) if (length($include)) ;

 hdrSave($hostconf,\%hdr) ;

        # regular and scheduled menus should be sync before entering this menu
        # so either we should copy regular to scheduled, or
        # we commit the previous changes to the existing file
        if (-f "$hostconf.$WOL_EXTENSION") {
                my %schedhdr;
                hdrLoad("$hostconf.$WOL_EXTENSION", \%schedhdr);
                hdrAddMenu(\%schedhdr, $menu);
                hdrSetVal(\%schedhdr, $menu, "def", "no") ;
                hdrSetVal(\%schedhdr, $menu, "visu", "yes") ;
                hdrSetVal(\%schedhdr, $menu, "image", $image) ;
                hdrSetVal(\%schedhdr, $menu, "include", $include) if (length($include)) ;
                hdrSave("$hostconf.$WOL_EXTENSION",\%schedhdr) ;
        } else {
                system("cp -a $hostconf $hostconf.$WOL_EXTENSION") ;
        }

1;
}




# moveLocal2Base ($home,$mac,$image [, $test])
#
#
sub moveLocal2Base
{
my ($home,$mac,$image) = @_ ;
my $test = $_[3] || 0 ;

my $macfile = toMacFileName($mac) ;
my $hostdir = $home . "/images/" . $macfile ;
my $imgbase = $home . "/imgbase" ;
my $hostconf = $hostdir . "/header.lst" ;
my ($menu, $newimg, $i, $n, @lsbuf, %hdr) ;

 if (not hdrLoad($hostconf, \%hdr)) {
        lbsError("moveLocal2Base","FILE_LOAD",$hostconf) ;
        return 0 ;
 }

 $menu = hdrFindMenu(\%hdr,"image",$image) ;
 if (defined($menu)) {
        lbsError("moveLocal2Base","IMG_USEDBYMENU",$image,$menu) ;
        return 0 ;
 }

 if (not -d "$hostdir/$image") {
        lbsError("moveLocal2Base","IMG_NF",$image) ;
        return 0 ;
 }

 if (-l "$hostdir/$image") {
        lbsError("moveLocal2Base","IMG_MVLINKINVAL",$image) ;
        return 0 ;
 }

        # --- Construction d'un nom unique:
        $n = 0 ;
        @lsbuf = () ;
        foreach $i (grep m/$macfile/, readSubDirs($imgbase)) {
                if ($i =~ m/.*\-([0-9]+)$/) {
                        push @lsbuf, $1 ;
                }
        }
        @lsbuf = sort { $a <=> $b } @lsbuf ; # Forcer un tri de type numerique
        $n = pop(@lsbuf) if (scalar @lsbuf);
        $n++ ;
        $newimg = "Base-" . $macfile . "-$n" ;

 if (-e "$imgbase/$newimg") {
        lbsError("moveLocal2Base","IMG_EXISTS","$imgbase/$newimg") ;
        return 0 ;
 }

 return 1 if ($test) ;

 if (system("mv","-f","$hostdir/$image","$imgbase/$newimg")) {
        lbsError("moveLocal2Base","RAW","system(): $!") ;
        return 0 ;
 }

1;
}


# moveBase2Hdr ($home,$mac,$image [, $test])
#
#
sub moveBase2Hdr
{
my ($home,$mac,$image) = @_ ;
my $test = $_[3] || 0 ;

my $macfile = toMacFileName($mac) ;
my $hostdir = $home . "/images/" . $macfile ;
my $imgbase = $home . "/imgbase" ;
my $hostconf = $hostdir . "/header.lst" ;
my %hdr ;
my ($menu,$include,$newlink) ;

 if (not -d "$imgbase/$image") {
        lbsError("moveBase2Hdr","IMG_NF","$imgbase/$image") ;
        return 0 ;
 }

 if (-e "$hostdir/$image") {
        lbsError("moveBase2Hdr","IMG_EXISTS", "$hostdir/$image") ;
        return 0 ;
 }

 if (not hdrLoad($hostconf, \%hdr)) {
        lbsError("moveBase2Hdr","FILE_LOAD",$hostconf) ;
        return 0 ;
 }

 $menu = hdrFindMenu(\%hdr,"image",$image) ;
 if (defined($menu)) {
        lbsError("moveBase2Hdr","IMG_USEDBYMENU",$image,$menu) ;
        return 0 ;
 }


 return 1 if ($test) ;


 if (not symlink("$imgbase/$image","$hostdir/$image")) {
        lbsError("moveBase2Hdr","RAW","'$hostdir/$image': $!") ;
        return 0 ;
 }

 if (-f "$hostdir/$image/conf.txt") {
        $include = "$image/conf.txt" ;
 }
 else {
        $include = "" ;
 }


 $menu = hdrUniqueName(\%hdr) ;
 if (not hdrAddMenu(\%hdr, $menu)) {
        lbsError("moveBase2Hdr","MENU_CANTAPPEND",$menu) ;
        return 0 ;
 }

 hdrSetVal(\%hdr, $menu, "def", "no") ;
 hdrSetVal(\%hdr, $menu, "visu", "yes") ;
 hdrSetVal(\%hdr, $menu, "image", $image) ;
 hdrSetVal(\%hdr, $menu, "include", $include) if (length($include)) ;

 hdrSave($hostconf,\%hdr) ;

        # regular and scheduled menus should be sync before entering this menu
        # so either we should copy regular to scheduled, or
        # we commit the previous changes to the existing file
        if (-f "$hostconf.$WOL_EXTENSION") {
                my %schedhdr;
                hdrLoad("$hostconf.$WOL_EXTENSION", \%schedhdr);
                hdrAddMenu(\%schedhdr, $menu);
                hdrSetVal(\%schedhdr, $menu, "def", "no") ;
                hdrSetVal(\%schedhdr, $menu, "visu", "no") ;
                hdrSetVal(\%schedhdr, $menu, "image", $image) ;
                hdrSetVal(\%schedhdr, $menu, "include", $include) if (length($include)) ;
                hdrSave("$hostconf.$WOL_EXTENSION",\%schedhdr) ;
        } else {
                system("cp -a $hostconf $hostconf.$WOL_EXTENSION") ;
        }

1;
}

#//////////////////////////////////////////////////////////////////////////////
# I M A G E S
#//////////////////////////////////////////////////////////////////////////////

# imgDeleteLocal($home,$mac,$image)
# Suppression d'une $image locale a une machine.
# Cela revient a effacer le repertoire ou le lien correspondant dans le
# repertoire de la machine $mac.
# Pour qu'une image (repertoire) locale soit effacable, elle ne doit pas
# etre utilisee dans un menu de demarrage.
# Retourne 1 si OK, ou 0 si erreur.
#
sub imgDeleteLocal
{
my ($home,$mac,$image) = @_ ;

my $macfile = toMacFileName($mac) ;
my $hostdir = $home . "/images/" . $macfile ;
my $hostconf = $hostdir . "/header.lst" ;
my $menu ;
my %hdr ;

 if (not hdrLoad($hostconf, \%hdr)) {
        lbsError("imgDeleteLocal","FILE_LOAD",$hostconf) ;
        return 0 ;
 }

 $menu = hdrFindMenu(\%hdr,"image",$image) ;
 if (defined($menu)) {
        lbsError("imgDeleteLocal","IMG_USEDBYHOST",$image,$mac) ;
        return 0 ;
 }

 if (not -d "$hostdir/$image") {
        lbsError("imgDeleteLocal","IMG_NF",$image) ;
        return 0 ;
 }


 if (-l "$hostdir/$image") {
        # Lien sym sur repertoire
        if (not unlink("$hostdir/$image")) {
                lbsError("imgDeleteLocal","RAW","'$image': $!") ;
                return 0 ;
        }
 }
 else {
        # Un vrai repertoire
        if (system("rm","-rf","$hostdir/$image")) {
                lbsError("imgDeleteLocal","RAW","'$image': $!") ;
                return 0 ;
        }
 }

1;
}



# imgBaseUsage($home,\%busage)
# Retourne des infos sur l'utilisation des images de base par les menus
# des machines.
# La struct %busage de reception des infos est un hache dont chaque clef est
# un nom d'image de base, et dont chaque valeur est une liste (eventuelle)
# de postes utilisant cette image  dans leur menu de demarrage.
# Exemple:
#
# %busage = (
#    "imageA"   => [ "poste1", "poste4" ] ,
#    "imageB"   => [ "poste1", "poste2" ] ,
#    "imageC"   => [ "poste2" ] ,
#    "imageD"   => [] ,
#    etc...
# );
#
# imageB: Utilisee dans les menus de poste1 et poste2.
# imageD: Utilisée dans aucun menu. Donc effacable par imgDeleteBase().
#
# Retourne 1 si OK, ou 0 si erreur.
#
#
sub imgBaseUsage
{
my ($home,$busage) = @_ ;

my ($etherfile,$hostdir, $hostconf) ;
my ($host, $mac, $macfile,$img) ;
my (%hdr, %einfo) ;
my (@lsmac, @lsbase, @lsused, @ls) ;

 %$busage = () ;

 @lsbase = readSubDirs("$home/imgbase") ;

 if (not scalar(@lsbase)) {
        lbsError("imgBaseUsage","IMG_EMPTYBASE","imgbase/") ;
        return 0 ;
 }

 # Init des clefs de busage:
 foreach $img (@lsbase) {
        $$busage{$img} = [] ;
 }

 etherLoad("$home/etc/ether", \%einfo) or return 0 ;
 @lsmac = etherGetMacs(\%einfo) ;

 foreach $mac (@lsmac) {
        $host = etherGetNameByMac(\%einfo, $mac) ;
        $macfile = toMacFileName($mac) ;
        $hostdir =  $home . "/images/" . $macfile ;
        $hostconf = $hostdir . "/header.lst" ;

        hdrLoad($hostconf, \%hdr) or next ;

        @ls = hdrSelectMenuKey(\%hdr, "image") ;
        @lsused = listCommon(\@lsbase, \@ls) ;

        foreach $img (@lsused) {
#               if (not exists $$busage{$img}) {
#                       $$busage{$img} = [] ;
#               }

                push @{$$busage{$img}}, $host ;
        }
 }

1;
}



# imgDeleteBase($home,$image)
# Effacement d'une $image de base dans imgbase/ et de tous les liens sur
# celle-ci dans les repertoires de chaque machine.
#
sub imgDeleteBase
{
my ($home,$image) = @_ ;

my $imgpath = "$home/imgbase/$image" ;
my @lsmac ;
my %einfo ;
my ($mac,$macfile,$hostdir) ;

 if (not -d $imgpath) {
        lbsError("imgDeleteBase","IMG_NF",$imgpath) ;
        return 0 ;
 }

 etherLoad("$home/etc/ether", \%einfo) or return 0 ;
 @lsmac = etherGetMacs(\%einfo) ;

 foreach $mac (@lsmac) {
        $macfile = toMacFileName($mac) ;
        $hostimage = "$home/images/$macfile/$image" ;

        if (-d $hostimage) {
                imgDeleteLocal($home,$mac,$image) or return 0 ;
        }
 }

 if (system("rm","-rf",$imgpath)) {
        lbsError("imgDeleteBase","RAW","'$imgpath': $!") ;
        return 0 ;
 }

 skelDeleteBaseLink ($home,$image);

1;
}

#//////////////////////////////////////////////////////////////////////////////
# I M G S K E L
#//////////////////////////////////////////////////////////////////////////////


# @links skelReadBaseLinks($home)
# Returns Symbolic links in $home/imgskel/ wich are pointing
# to $home/imgbase/ .
#
sub skelReadBaseLinks
{
my $skeldir = $_[0]."/imgskel" ;
my (@lsbuf,@out,$i) ;

        if (not opendir(SKELDIR, $skeldir)) {
                lbsError("skelReadBaseLinks","RAW","'$skeldir': $!");
                return ;
        }
                @lsbuf =  grep !/^\.\.?$/, readdir SKELDIR ;
        closedir(SKELDIR);

        # We want only links pointing to "imgbase/$i" :
        foreach $i (@lsbuf) {
                next if (not -l "$skeldir/$i");
                push(@out, $i) if (grep m(/imgbase/$i/?$), readlink "$skeldir/$i");
        }

 return @out ;
}


# skelAddBaseLink($home,$image)
# Ajout d'un lien vers une image de base dans imgskel/, et ajout du menu
# correspondant dans imgskel/header.lst .
# $image doit etre le basename de l'image de base vers laquelle etablir
# le lien. Retourne 1 si OK, ou 0 si echec.
#
sub skelAddBaseLink
{
my ($home,$image) = @_ ;

my $imgpath = "$home/imgbase/$image" ;
my $linkpath = "$home/imgskel/$image" ;
my $header = "$home/imgskel/header.lst" ;
my %hdr ;
my $m ;

 if (not -d $imgpath) {
        lbsError("skelAddBaseLink","IMG_NF",$imgpath) ;
        return 0 ;
 }

 if (-e $linkpath or -l $linkpath) {
        lbsError("skelAddBaseLink","FILE_EXISTS",$linkpath) ;
        return 0 ;
 }

 symlink("../../imgbase/$image", $linkpath) ;

 hdrLoad($header,\%hdr) or return 0 ;
        if (not defined hdrFindMenu(\%hdr,"image",$image)) {
                $m = hdrUniqueName(\%hdr) ;
                hdrAddMenu(\%hdr, $m) or return 0 ;
                hdrSetVal(\%hdr, $m,"def","no") ;
                hdrSetVal(\%hdr, $m,"visu","no") ;
                hdrSetVal(\%hdr, $m,"image",$image) ;
                hdrSetVal(\%hdr, $m,"include","$image/conf.txt") ;
        }
 hdrSave($header, \%hdr) or return 0 ;

1;
}


# skelDeleteBaseLink($home,$image)
# Delete an $image __link___ from $home/imgskel/ directory.
# Return 1 on success, or 0 if failed.
#
sub skelDeleteBaseLink
{
my ($home,$image) = @_ ;
my $linkpath = "$home/imgskel/$image" ;
my $header = "$home/imgskel/header.lst" ;
my (%hdr, $m) ;

 if (not -l $linkpath) {
        lbsError("skelDeleteBaseLink", "LINK_NF",$linkpath) ;
        return 0 ;
 }

 hdrLoad($header,\%hdr) or return 0 ;
        $m = undef ;
        if (defined($m = hdrFindMenu(\%hdr,"image",$image))) {
                hdrDeleteSection(\%hdr,$m);
        }
 hdrSave($header, \%hdr) or return 0 ;

 unlink($linkpath) ;

1;
}

# END OF MODULE ///////////////////////////////////////////////////////////////
1;
#//////////////////////////////////////////////////////////////////////////////
