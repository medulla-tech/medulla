<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

class DoubleAutocomplete {
    function DoubleAutocomplete($module, $criterion, $value = '', $edition = false) {
        $this->module = $module;
        $this->criterion = $criterion;
        $this->val = $value;

        $first = explode('/', urldecode($criterion));
        $second = explode(':', $first[1]);

        $this->table = $first[0];
        $this->field1 = $second[0];
        $this->field2 = $second[1];
        $this->b_label = _T("Add", "dyngroup");
        $this->edition = $edition;
        if ($edition) {
            $this->b_label = _T("Modify", "dyngroup");
        }
    }
    
    function display() {
    ?>

    <td style="text-align:right;"><?php echo  $this->field1;?> : </td>
    <td>
        <input type="text" id="autocomplete" name="value" class="textfield" size="23" value="<?php echo $this->val?>" /> 
        <div id="autocomplete_choices" class="autocomplete">
            <ul>
                <li>A</li>
                <li>B</li>
            </ul>
        </div>
    </td>
    <td id='secondButton'>
        <input name="next" type="button" class="btnPrimary" value="<?php echo  _T("->", "dyngroup"); ?>" onClick="addSlave('autocomplete'); return false;"/>
    </td>
    </tr>
    </table>
     
    <div id='secondPart' style='visibility:hidden;'>
        <table><tr>
        <td id='secondPart1' style="text-align:right;"><?php echo  $this->field2;?> : </td>
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
            <input name="buser" type="submit" class="btnPrimary" value="<?php echo  $this->b_label; ?>" />   
        </td>
        </tr></table>
    </div>
   
    <script type="text/javascript">

    <!--
        function addSlave(id) {
            var autocomplete = document.getElementById(id);
            var value = autocomplete.getValue();
            autocomplete.setAttribute('readonly', true);

            /* slave */
            new Ajax.Autocompleter('autocomplete2','autocomplete2_choices',
                'main.php?module=base&submod=computers&action=ajaxAutocompleteSearch&modulename=<?php echo  $this->module ?>&criterion=<?php echo  $this->criterion ?>&value1='+value, {paramName: "value"});
                
            var secondPart = document.getElementById('secondPart');

            var secondButton = document.getElementById('secondButton');
            var secondPart3 = document.getElementById('secondPart3');
            var secondPart2 = document.getElementById('secondPart2');
            var secondPart1 = document.getElementById('secondPart1');
            
            var parent = secondButton.parentNode;
            parent.replaceChild(secondPart3, secondButton);
            parent.insertBefore(secondPart2, secondPart3);
            parent.insertBefore(secondPart1, secondPart2);
        }
        
        //primary
        <?php
            include_once("modules/dyngroup/includes/xmlrpc.php");
        ?>
        new Ajax.Autocompleter('autocomplete','autocomplete_choices',
            'main.php?module=base&submod=computers&action=ajaxAutocompleteSearch&modulename=<?php echo  $this->module ?>&criterion=<?php echo  $this->criterion ?>', {paramName: "value"});
    -->
    </script>
    <?php
    }
}

?>
