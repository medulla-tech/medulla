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

class Autocomplete {
    function Autocomplete($module, $criterion, $value = '', $edition = false) {
        $this->module = $module;
        $this->criterion = $criterion;
        $this->val = $value;
        $this->b_label = _T("Add", "dyngroup");
        if ($edition) {
            $this->b_label = _T("Modify", "dyngroup");
        }
    }
    
    function display() {
    ?>

    <td style="text-align:right;"><?php echo  _T("Add a value", "dyngroup");?></td><td>

    <input type="text" id="autocomplete" name="value" class="textfield" size="23" value="<?php echo $this->val?>" /> 
    <div id="autocomplete_choices" class="autocomplete">
        <ul>
            <li>A</li>
            <li>B</li>
        </ul>
    </div>
    <input name="buser" type="submit" class="btnPrimary" value="<?php echo  $this->b_label; ?>"/> 
    </td></tr>
    </table>
    
    <script type="text/javascript">

    <!--
        var groups = new Array();
        new Ajax.Autocompleter('autocomplete','autocomplete_choices',
            'main.php?module=base&submod=computers&action=ajaxAutocompleteSearch&modulename=<?php echo  $this->module ?>&criterion=<?php echo  $this->criterion ?>', {paramName: "value", frequency: 2.0});
    -->
    </script>
    <?php
    }
}

?>
