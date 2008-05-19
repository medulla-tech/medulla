<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

class DoubleAutocomplete {
    function DoubleAutocomplete($module, $criterion) {
        $this->module = $module;
        $this->criterion = $criterion;

        $first = explode('/', urldecode($criterion));
        $second = explode(':', $first[1]);

        $this->table = $first[0];
        $this->field1 = $second[0];
        $this->field2 = $second[1];
    }
    
    function display() {
    ?>

    <td style="text-align:right;"><?= $this->field1;?> : </td>
    <td>
        <input type="text" id="autocomplete" name="value" class="textfield" size="23" /> 
        <div id="autocomplete_choices" class="autocomplete">
            <ul>
                <li>A</li>
                <li>B</li>
            </ul>
        </div>
    </td>
    <td id='secondButton'>
        <input name="next" type="button" class="btnPrimary" value="<?= _T("->"); ?>" onClick="addSlave('autocomplete'); return false;"/>
    </td>
    </tr>
    </table>
     
    <div id='secondPart' style='visibility:hidden;'>
        <table><tr>
        <td id='secondPart1' style="text-align:right;"><?= $this->field2;?> : </td>
        <td id='secondPart2'>
            <input type="text" id="autocomplete2" name="value2" class="textfield" size="23" /> 
            <div id="autocomplete2_choices" class="autocomplete">
                <ul>
                    <li>A</li>
                    <li>B</li>
                </ul>
            </div>
        </td>
        <td id='secondPart3'>
            <input name="buser" type="submit" class="btnPrimary" value="<?= _T("Add"); ?>" />   
        </td>
        </tr></table>
    </div>
   
    <script type="text/javascript">

    <!--
        function addSlave(id) {
            var autocomplete = document.getElementById(id);
            var value = autocomplete.getValue();
            autocomplete.setAttribute('readonly', true);
            var secondButton = document.getElementById('secondButton');
            var secondPart3 = document.getElementById('secondPart3');
            var secondPart2 = document.getElementById('secondPart2');
            var secondPart1 = document.getElementById('secondPart1');
            
            var parent = secondButton.parentNode;
            parent.replaceChild(secondPart3, secondButton);
            parent.insertBefore(secondPart2, secondPart3);
            parent.insertBefore(secondPart1, secondPart2);
            // slave
            var groups2 = new Array();
            new Ajax.Autocompleter('autocomplete2','autocomplete2_choices',
                'main.php?module=base&submod=computers&action=ajaxAutocompleteSearchWhere&value1='+value+'&modulename=<?= $this->module ?>&criterion=<?= $this->criterion ?>', {paramName: "value2"});
        }
        
        //primary
        var groups = new Array();
        <?php
            include_once("modules/dyngroup/includes/xmlrpc.php");
            /*foreach (getPossiblesValuesForCriterionInModuleFuzzy($this->module, $this->criterion, '') as $res)
            {   
                echo "groups.push('" . htmlentities($res, ENT_QUOTES) . "');\n";
            }*/
        ?>
        new Ajax.Autocompleter('autocomplete','autocomplete_choices',
            'main.php?module=base&submod=computers&action=ajaxAutocompleteSearch&modulename=<?= $this->module ?>&criterion=<?= $this->criterion ?>', {paramName: "value"});
    -->
    </script>
    <?php
    }
}

?>
