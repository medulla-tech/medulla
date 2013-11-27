<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once ("modules/pkgs/includes/autocomplete.php");
function addQuery($Form, $p, $pack, $field = 'Installed+software', $limit = 3, $extracriterion = '') {
    $module = clean ( quickGet ( 'req' ) );
    $criterion = clean ( quickGet ( 'add_param' ) );
    $auto = new Autocomplete ( $p [0], 'main.php?module=pkgs&submod=pkgs&action=ajaxAutocompleteSearch', "glpi", $field, $value = $pack [$p [0]]/*quickGet ( 'value' )*/, $limit, $extracriterion, $subedition );
    $Form->add ( new TrFormElement ( $p [1], $auto, array (
            "value" => $pack [$p [0]]
    ) ) );
    //     $Form->pop();
}
function addQuerySection($Form, $p){
    /* ================= BEGIN QUERY ===================== */
    $Fquery = new DivForModule ( _T ( "Query", "pkgs" ) );
    $Tquery = new Table ();

    addQuery ( $Tquery, array (
    'Qvendor',
    _T ( 'Vendor', 'pkgs' )
    ), $p, 'Vendors' );
    addQuery ( $Tquery, array (
    'Qsoftware',
    _T ( 'Software', 'pkgs' )
    ), $p, 'Installed+software', 3, 'Qvendor' );
    addQuery ( $Tquery, array (
    'Qversion',
    _T ( 'Version', 'pkgs' )
    ), $p, 'Software versions', 1, 'Qsoftware' );
    $Fquery->push ( $Tquery );

    $Form->push ( $Fquery );
    $Bool = new TrFormElement ( _T ( 'Bool', 'pkgs' ), new InputTpl ( 'boolcnd' ) );
    $Bool->setStyle ( "display:none" );

    $Form->add ( $Bool, array (
            "value" => $p ['boolcnd']
    ) );
    /* =================     END QUERY    ===================== */
}
?>
