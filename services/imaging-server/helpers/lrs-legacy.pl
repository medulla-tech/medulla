#!/usr/bin/perl -w
#
# (c) 2003-2007 Linbox, http://www.linbox.com/
# (c) 2008-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

require "lrs-inifile.pl";

%_errors_en = (
               'RAW'             => q($1),
               'MAC_BAD'         => q('$1': Invalid MAC address.),
               'MAC_UNK'         => q('$1': Unknown MAC address.),
               'MAC_EXISTS'      => q('$1': MAC address already existing.),
               'HOST_UNK'        => q('$1': Unknown host.),
               'HOST_USED'       => q('$1': Name already used.),
               'CANT_INCLUDE'    => q(Can't include '$1'.),
               'CANT_SAVE'       => q(Can't save '$1'.),
               'CANT_WRITE'      => q(Can't write '$1'.),
               'CANT_GETUNIQUE'  => q(Can't get unique name.),
               'CANT_OPEN'       => q('$1': Open failed.),
               'SECT_UNK'        => q('$1': Unknown section.),
               'ITEM_UNK'        => q('$1': Inknown item.),
               'ITEM_NF'         => q('$1': Item not found.),
               'MENU_CANTAPPEND' => q('$1': Can't append menu.),
               'FILE_NF'         => q('$1': No such file or directory.),
               'FILE_LOAD'       => q('$1': Loading failed.),
               'FILE_REMOVE'     => q('$1': Remove failed.),
               'FILE_EXISTS'     => q('$1': File already exists.),
               'ENTRY_EXISTS'    => q('$1': Entry already exists.),
               'IMG_NF'          => q('$1': Image not found.),
               'IMG_NFINTO'      => q('$1': Image not found into '$2'),
               'IMG_EXISTS'      => q('$1': Image already exists.),
               'IMG_USEDBYMENU'  => q('$1': Image currently used by menu '$2'.),
               'IMG_USEDBYHOST'  => q('$1': Image used by host '$2'.),
               'IMG_EMPTYBASE'   => q(No base images found into '$1'.),
               'IMG_MVLINKINVAL' => q(Image '$1': invalid move operation.),
               'LINK_NF'         => q('$1': Link not found.),
              );

$_lbsdebug = 0;

%_lbserr = (
            'href' => \%_errors_en,
            'func' => 'None',
            'mesg' => 'OK',
            'flag' => 0,
           );

# updateEntry($lbs_home, $netboot, $macaddr)
# Fonction de mise a jour d'une entree.
# Pour l'instant, elle ne fait que creer le menu utilisateur final.
sub updateEntry
{
    my ($home, $netboot, $mac) = @_;

    if (not makeUserMenu($home, $netboot, $mac))
    {

        #lbsError("updateEntry","RAW","Problem making final user menu") ;
        return 0;
    }

    return 1;
}

# makeUserMenu ($base, $netboot, $macaddr)
# Genere le menu de demarrage d'une machine a partir de header.lst .
# Retourne 1 si OK, ou 0 si erreur.
#
sub makeUserMenu
{
    my $base    = $_[0];
    my $netboot = $_[1];
    my $mac     = toMacFileName($_[2]);

    my $defaultpos = 0;
    my @menus      = ();

    my $menupath   = $netboot . "/cfg/" . $mac;
    my $imagepath  = $base . "/images/" . $mac;
    my $menuheader = "";
    my $bootmenu   = "";
    my $one        = "";
    my $m;
    my $numselect = 0;
    my %hdr;
    my %minfo;
    my $hostconf = $base . "/images/" . $mac . "/header.lst";
    my $imgname;

    my $copynumdata;
    my $basenumdata;

    # WOL requested ?
    if (-f $base . "/images/" . $mac . "/wol")
    {

        # check if the timestamp is not too old
        my $wol = $base . "/images/" . $mac . "/wol";
        my $ts  = (stat($wol))[9];
        if (time() - $ts > 600)
        {

            # 10 minutes: the wol request has expired ...
            # we should tell the admin
        }
        else
        {

            # wol requested, use the alternate menu
            $hostconf = $base . "/images/" . $mac . "/header.lst.wol";
        }
        unlink($wol);
    }

    # Load header.lst
    if (not hdrLoad($hostconf, \%hdr))
    {
        lbsError("makeUserMenu", "FILE_LOAD", $hostconf);
        return 0;
    }

    if (-f "$imagepath/COPYNUM")
    {
        fileLoad("$imagepath/COPYNUM", \$copynumdata);
        chomp($copynumdata);
    }
    else
    {
        $copynumdata = "COPYNUM";
    }

    if (-f "$base/imgbase/BASENUM")
    {
        fileLoad("$base/imgbase/BASENUM", \$basenumdata);
        chomp($basenumdata);
    }
    else
    {
        $basenumdata = "BASENUM";
    }

    # FIXME originally taken from /etc/webmin/lbs/config, now forced to default values, should be read from somewhere else
    #MDV/NR my %conf = ();
    #MDV/NR iniLoad( "/etc/webmin/lbs/config", \%conf );
    #MDV/NR my $revorestore      = iniGetVal( \%conf, "-", "restore_type" );
    #MDV/NR my $revowait         = iniGetVal( \%conf, "-", "mtftp_wait" );
    #MDV/NR my $grub_splashimage = iniGetVal( \%conf, "-", "grub_splashimage" );
    #MDV/NR my $grub_keymap      = iniGetVal( \%conf, "-", "grub_keymap" );
    my $revorestore      = 0;
    my $revowait         = 5;
    my $grub_splashimage = '/pulse2/background/mandriva.xpm';
    my $grub_keymap      = '';

    #
    my $eth = "0";
    $eth = hdrGetVal(\%hdr, "header", "ethnum");
    my $kernelopts = "";
    $kernelopts = hdrGetVal(\%hdr, "header", "kernelopts");

    @menus = hdrGetMenuNames(\%hdr);

    foreach $m (@menus)
    {

        hdrGetMenuInfo(\%hdr, $m, \%minfo);

        if ($minfo{'visu'} eq "yes")
        {

            # Determiner la pos du menu par defaut:
            $defaultpos = $numselect if ($minfo{'def'} eq "yes");

            $one = hdrConcatMenuItems(\%hdr, $m);

            $one = encodeCP850($one);

            $imgname = $minfo{'image'};

            $one =~ s/MAC/$mac/;
            $one =~ s/PATH/$imagepath\/$imgname/g;

            $one =~ s/COPYNUM/$copynumdata/;
            $one =~ s/BASENUM/$basenumdata/;

            if ($revorestore eq "" || $revorestore eq "0")
            {

                # tftp grub restore
                # nothing to do
            }
            else
            {

                # linux based restore
                if ($minfo{'image'} =~ /((Base|Local)-[0-9].*)/)
                {

                    # base image restoration
                    my $imgt = "imgbase";
                    my $imgo = "revorestore";

                    if ($revorestore eq "1")
                    {
                        $imgo = "revorestorenfs";
                    }
                    elsif ($revowait ne "0")
                    {
                        $imgo .= " revowait=$revowait";
                    }
                    if ($minfo{'image'} =~ /Local/)
                    {
                        $imgt = "images/$mac";
                    }

                    #print "$1 $revorestore \n";
                    my $o_title = "";
                    my $o_desc  = "";
                    foreach my $line (split(/\n/, $one))
                    {
                        if ($line =~ /^\s*title /)
                        {
                            $o_title = $line;
                        }
                        if ($line =~ /^\s*desc /)
                        {
                            $o_desc = $line;
                        }
                    }
                    $one = "$o_title\n$o_desc";
                    if ($revorestore eq "1")
                    {
                        $one =~ s/(^\s*title.*)/$1 (NFS)/;
                    }
                    elsif ($revorestore eq "2")
                    {
                        $one =~ s/(^\s*title.*)/$1 (MTFTP)/;
                    }
                    $one .= "
kernel (nd)$netboot/bin/bzImage.initrd revosavedir=/$imgt/$imgname $imgo quiet revopost
initrd (nd)$netboot/bin/initrd.gz
";

                    #print $one;
                }
            }

            $one = addEmptyLine($one);

            # adding of other linux boot options:
            if ($eth ne "0" && $eth ne "")
            {
                $one =~ s/(kernel \(nd\).* revo.*)/$1 revoeth$eth/;
            }
            else
            {

                # send the mac address on the command line to improve nic configuration
                $one =~ s/(kernel \(nd\).* revo.*)/$1 revomac=$mac/;
            }
            if ($kernelopts ne "")
            {
                $one =~ s/(kernel \(nd\).* revo.*)/$1 $kernelopts/;
            }

            $bootmenu .= $one;

            $numselect++;
        }
    }

    $menuheader = hdrConcatMenuItems(\%hdr, "header");
    $menuheader =~ s/DEFNUM/$defaultpos/;
    if ($grub_keymap ne "")
    {
        $menuheader .= "\nkbd$grub_keymap\n";
    }
    if ($grub_splashimage ne "")
    {
        $menuheader .= "\nsplashimage (nd)$grub_splashimage\n";
    }
    $menuheader = addEmptyLine($menuheader);

    # Generation du fichier final:
    if (not open FF, "> $menupath")
    {
        lbsError("makeUserMenu", "RAW", "Writing '$menupath': $!");
        return 0;
    }

    print FF $menuheader;
    print FF $bootmenu;

    close(FF);

    return 1;
}

# $mac macFileName ($mac)
# Formatage d'une adresse MAC, pour servir de nom de fichier.
# Typiquement on supprime les ':', et on met le tout en majuscules.
#
sub toMacFileName
{
    my $mac = shift;
    $mac = uc($mac);
    $mac =~ s/:+//g;
    return $mac;
}

# hdrLoad($file, \%hdr)
#
sub hdrLoad
{
    my ($file, $hdr) = @_;
    my %ini = ();
    my @sections;
    my ($s, $k, $v, $p, $i, $f, $buf);
    my @clefs;
    my %inc = ();

    if (not -f $file)
    {
        lbsError("hdrLoad", "FILE_NF", $file);
        return 0;
    }

    if (not iniLoad($file, \%ini))
    {
        lbsError("hdrLoad", "FILE_LOAD", $file);
        return 0;
    }

    $p        = getDirName($file);
    @sections = iniGetSections(\%ini);

    # Loading included files:
    foreach $s (@sections)
    {
        @clefs = iniGetKeys(\%ini, $s);
        for ($i = 0 ; $i < scalar(@clefs) ; $i++)
        {
            ($k, $v) = iniGet(\%ini, $s, $i);
            if ($k eq "include")
            {

                # Path relatif ou absolu?
                if (grep m(^/), $v)
                {
                    $f = $v;
                }
                else
                {
                    $f = "$p/$v";
                }

                if (not fileLoad($f, \$buf))
                {

                    # Warning:
                    lbsError("hdrLoad", "CANT_INCLUDE", $f);
                }
                else
                {

                    # No '\n' at end of file:
                    $buf =~ s/\n+$//s;
                    $inc{$v} = $buf;
                }
            }
        }
    }

    # Final struct:
    %$hdr         = ();
    $$hdr{'file'} = $file;
    $$hdr{'ini'}  = {%ini};
    $$hdr{'inc'}  = {%inc};

    1;
}

# lbsError($func, $label, [$args]*)
# Enregistre un message d'erreur $label. $func doit etre le nom de la fct
# appelante. $label est un code erreur existant. $args sont des valeurs
# optionnelles à substituer dans le message final si celui-ci le necessite.
#
sub lbsError
{
    my $func  = shift;
    my $label = shift;
    my $mesg;

    $mesg = textSub($_lbserr{'href'}, $label, @_);

    $_lbserr{'func'} = $func;
    $_lbserr{'mesg'} = $mesg;
    $_lbserr{'flag'} = 1;

    1;
}

# lbsGetError
# Retourne le dernier message d'erreur enregistre.
#
sub lbsGetError
{
    my $buf;

    if ($_lbsdebug == 0)
    {
        return $_lbserr{'mesg'};
    }
    else
    {
        $buf = sprintf "Function %s:\n %s\n",
          $_lbserr{'func'}, $_lbserr{'mesg'};
        return $buf;
    }
}

# lbsDieError( [$msg] ) ;
# Termine le programme en affichant la derniere erreur rencontree.
# Si le message $msg est donne en arg, il est alors ajoute à la suite du
# message d'erreur.
#
sub lbsDieError
{
    my $msg = lbsGetError();

    if (defined($_[0]))
    {
        $msg .= " " . $_[0];
    }

    $msg .= "\n";
    $msg =~ s/\n+$/\n/s;

    die($msg);
}

# $mesg textSub(\%href,$label,[$substitutes]*)
#
sub textSub
{
    my $href  = shift;
    my $label = shift;
    my ($i, $j, $mesg);

    if (not exists($$href{$label}))
    {
        $mesg = "Unknown message label '$label'";
        if (scalar @_) { $mesg .= ", with args: " . join(",", @_); }
        return $mesg;
    }
    else
    {
        $mesg = $$href{$label};
        for ($i = 0 ; $i < @_ ; $i++)
        {
            $j = $i + 1;
            $mesg =~ s/\$$j/$_[$i]/g;
        }
    }

    return $mesg;
}

# $val hdrGetVal(\%hdr, $section, $key)
# Recup de la valeur d'une clef dans une section.
#
sub hdrGetVal
{
    my ($hdr, $section, $key) = @_;

    return iniGetVal($$hdr{'ini'}, $section, $key);
}

# hdrSetVal(\%hdr, $section, $key,$val)
# Modif de la valeur d'une clef dans une section.
#
sub hdrSetVal
{
    my ($hdr, $section, $key, $val) = @_;

    return iniSetVal($$hdr{'ini'}, $section, $key, $val);
}

# @names hdrGetMenuNames (\%hdr)
# Retourne les noms des sections decrivant les menus. Elles ont toutes le
# prefixe 'menu' dans leur nom.
#
sub hdrGetMenuNames
{
    my $hdr = $_[0];
    return grep m/^menu/i, iniGetSections($$hdr{'ini'});
}

# hdrGetMenuInfo (\%hdr, $section, \%info)
# Retourne diverses infos a partir d'une section de type 'menu'.
# Ces infos proviennent de plrs sources: des parametres du menu lui-meme,
# et des fichiers inclus s'il y en a.
# Retourne 1 si OK, ou 0 si erreur.
#
sub hdrGetMenuInfo
{
    my ($hdr, $section, $info) = @_;
    my ($t, $d, $res);
    my $iniref = $$hdr{'ini'};

    if (not iniHasSection($iniref, $section))
    {
        lbsError("hdrGetMenuInfo", "SECT_UNK", $section);
        return 0;
    }

    # Init:
    $res = 1;
    %{$info} = ();

    $$info{"def"}   = iniGetVal($iniref, $section, "def");
    $$info{"visu"}  = iniGetVal($iniref, $section, "visu");
    $$info{"image"} = iniGetVal($iniref, $section, "image");

    $t = hdrGetMenuItem($hdr, $section, "title");
    $d = hdrGetMenuItem($hdr, $section, "desc");

    if (not defined($d))
    {
        $$info{"desc"} = "(nul)";
    }
    else
    {
        $$info{"desc"} = $d;
    }

    # La presence d'un item 'title' est obligatoire:
    if (not defined($t))
    {
        lbsError("hdrGetMenuInfo", "ITEM_NF", "title", "section $section");
        $$info{"title"} = "(not found)";
        $res = 0;
    }
    else
    {
        $$info{"title"} = $t;
        $res = 1;
    }

    return $res;
}

# $val hdrGetMenuItem(\%hdr, $section, $item )
# Recup de la valeur d'un item d'une section $section.
# La recherche est effectuee sur les clefs 'item' et 'include' .
# Concernant 'include', la fct va chercher dans le fichier indique.
# Retourne la valeur trouvee, ou une chaine vide si echec.
#
sub hdrGetMenuItem
{
    my ($hdr, $section, $item) = @_;
    my @clefs;
    my ($i, $k, $v, $a);
    my $iniref = $$hdr{'ini'};
    my $incref = $$hdr{'inc'};

    if (not iniHasSection($iniref, $section))
    {
        lbsError("hdrGetMenuItem", "SECT_UNK", $section);
        return;
    }

    $item = lc($item);

    @clefs = iniGetKeys($iniref, $section);
    for ($i = 0 ; $i < scalar(@clefs) ; $i++)
    {
        ($k, $v) = iniGet($iniref, $section, $i);

        if ($k eq "item")
        {

            # Recherche dans header.lst
            if (defined($a = itemGetVal($v, $item)))
            {
                return $a;
            }
        }
        elsif ($k eq "include")
        {

            # Ou recherche dans les fichiers inclus:
            if (exists($$incref{$v}))
            {
                if (defined($a = itemGetVal($$incref{$v}, $item)))
                {
                    return $a;
                }
            }
        }
    }

    return;    # Echec
}

# $string hdrConcatMenuItems(\%hdr, $section)
# Retourne une chaine dans laquelle sont concatenes tous les menuitems
# rencontres dans la section $section. Ceci concerne les clefs 'items' et
# 'include' .
# Une chaine vide peut etre retournee si aucun item n'est rencontre.
#
sub hdrConcatMenuItems
{
    my ($hdr, $section) = @_;

    my @clefs;
    my ($k, $v, $i);
    my $iniref = $$hdr{'ini'};
    my $incref = $$hdr{'inc'};
    my @concat = ();

    if (not iniHasSection($iniref, $section))
    {
        lbsError("hdrConcatMenuItems", "SECT_UNK", $section);
        return "";
    }

    @clefs = iniGetKeys($iniref, $section);
    for ($i = 0 ; $i < scalar(@clefs) ; $i++)
    {
        ($k, $v) = iniGet($iniref, $section, $i);
        $k = lc($k);

        if ($k eq "item")
        {

            # Recherche dans header.lst
            push @concat, $v;
        }
        elsif ($k eq "include")
        {

            # Ou recherche dans les fichiers inclus:
            if (exists($$incref{$v}))
            {
                push @concat, $$incref{$v};
            }
        }
    }

    return join("\n", @concat);
}

# $new encodeCP850($text)
#
#
sub encodeCP850
{
    my $tbl_cp850 =
      "\x83\x84\x85\x82\x88\x89\x8a\x8b\x8c\x93\x94\x81\x96\x97\x98\x87";
    my $tbl_latin =
      "\xe2\xe4\xe0\xe9\xea\xeb\xe8\xef\xee\xf4\xf6\xfc\xfb\xf9\xff\xe7";

    #my $tbl_cp850="\x203\x204\x205\x202\x210\x211\x212\x213\x214\x223\x224\x201\x226\x227\x230\x207";
    #my $tbl_latin="\x342\x344\x340\x351\x352\x353\x350\x357\x356\x364\x366\x374\x373\x371\x377\x347";
    #my $tbl_ascii="aaaeeeeiioouuuyc";

    $_ = shift;

    eval "tr/$tbl_latin/$tbl_cp850/";

    return $_;
}

# $newstr addEmptyLine($text)
# Retourne une chaine terminee par une ligne vide. (Un double \n).
#
sub addEmptyLine
{
    my $buf = $_[0] . "\n\n";

    $buf =~ s/\n+$/\n\n/s;

    return $buf;
}

# END OF MODULE ///////////////////////////////////////////////////////////////
1;

#//////////////////////////////////////////////////////////////////////////////
