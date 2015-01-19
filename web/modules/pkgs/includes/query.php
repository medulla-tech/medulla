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
function addQuery($Form, $p, $pack, $field = 'Installed+software', $limit = 3, $extracriterion = '', $style = '') {
    
    // Sorry for this shit code :(
    if (is_array($pack[$p[0]]))
        $pack[$p[0]] = $pack[$p[0]][0];
    
    $module = (in_array('inventory', $_SESSION['modulesList'])) ? 'inventory' : 'glpi';
    $criterion = clean ( quickGet ( 'add_param' ) );
    $auto = new Autocomplete($p[0], 'main.php?module=pkgs&submod=pkgs&action=ajaxAutocompleteSearch', 
            $module, $field, $value = $pack[$p[0]]/*quickGet ( 'value' )*/, $limit, $extracriterion);
    $tooltip = _T(
            'Please type 3 characters for suggestion.<br>
            Wildcard is \'%\', %text% matches any string containing \'text\'.<br>
            If unsure, leave Vendor and Version fields blank.', 
            pkgs);
    $Form->add(
            new TrFormElement($p[1], $auto, 
                    array('class' => 'associateinventory', 'style' => $style, 'tooltip' => $tooltip)), 
            array("value" => $pack[$p[0]]));
}

/*
 * Get correct dyngroup fields
 */
function getQFields() {
    if (in_array('inventory', $_SESSION['modulesList'])) {
        return array(
            'Qvendor' => 'Software/Company',
            'Qsoftware' => 'Software/ProductName:ProductVersion',
            'Qversion' => 'Software/ProductName:ProductVersion',
        );
    }
    return array(
        'Qvendor' => 'Vendors',
        'Qsoftware' => 'Installed+software',
        'Qversion' => 'Software versions',
    );
}
function addQuerySection($Form, $p) {
    /* ================= BEGIN QUERY ===================== */
    $span = new SpanElement(_T("Query", "pkgs"), "pkgs-title");
    $Form->add(new TrFormElement("", $span), array());

    $check = '';
    $style = 'display:none';
    if ($p['associateinventory'] == 1){
        $check = 'checked';
        $style = '';
    }

    $Form->add(
            new TrFormElement(_T('Associate inventory', 'pkgs'), 
                    new CheckboxTpl('associateinventory')), 
            array("value" => $check)
        );

    $Qfields = getQFields();

    addQuery($Form, array('Qvendor', _T('Vendor', 'pkgs')), $p, $Qfields['Qvendor'], 3, '', $style);
    addQuery($Form, array('Qsoftware', _T('Software', 'pkgs')), $p, $Qfields['Qsoftware'], 3, 
            'Qvendor', $style);
    addQuery($Form, array('Qversion', _T('Version', 'pkgs')), $p, $Qfields['Qversion'], 2, 'Qsoftware', 
            $style);

    $Bool = new TrFormElement(_T('Bool', 'pkgs'), new InputTpl('boolcnd'));
    $Bool->setStyle("display:none");
    $Form->add($Bool, array("value" => $p['boolcnd']));
    /* ================= END QUERY ===================== */
    /* =================   BEGIN LICENSE   ===================== */
    $Form->add(
            new TrFormElement(_T('Number of licenses', 'pkgs'), new InputTpl('licenses'), 
                    array('class' => 'associateinventory', 'style' => $style)), 
            array("value" => $p['licenses'])
    );
    /* ==================   END LICENSE   ====================== */
}
?>
<script type="text/javascript">
    jQuery(function() { // load this piece of code when page is loaded
        // Set easySuggest on software field with the new ajax url
        jQuery('#associateinventory').change(function() {
            if (jQuery(this).is(":checked")) {
                jQuery('.associateinventory').show();
                console.log("here");
            }
            else {
                jQuery('.associateinventory').hide();
            }
        });
        jQuery('#associateinventory').change();
    });
</script>

