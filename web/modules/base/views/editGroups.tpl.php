<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
   <table>
    <tr><td width="40%" style="text-align:right; vertical-align: top;"><?= _("Groups"); ?> </td><td>
        <select multiple size="10" class="list" name="groupsselected[]" id="select">
            <?php
            if ($detailArr["uid"][0]){ //if user exist
                $sorted = getAllGroupsFromUser($detailArr["uid"][0]);
                }
            else { //else we set the default group
                $sorted = array();
                $sorted[] = get_default_group();
            }

            //sorting group
            sort($sorted);
            foreach ($sorted as $group)
                {
                echo "<option value=\"".$group."\">".$group."</option>\n";
            }
            ?>
        </select>
        <input name="buser" type="submit" class="btnPrimary" value="<?= _("Delete"); ?>" onClick="delEltInSelectBox(); return false;"/>

    </td>
    <tr><td style="text-align:right;"><?= _("Add a group");?></td><td>

    <input type="text" id="autocomplete" name="autocomplete" class="textfield" size="23" onkeypress="return validOnEnter(this,event);" />
    <div id="autocomplete_choices" class="autocomplete">
        <ul>
            <li>A</li>
            <li>B/<li>
        </ul>
    </div>
    <input name="buser" type="submit" class="btnPrimary" value="<?= _("Add"); ?>" onClick="addElt($F('autocomplete')); return false;"/>
    </td></tr>
    </table>

    <script type="text/javascript">

        var groups = new Array();
        <?php
            foreach (get_groups($error) as $group)
            {
                echo "groups.push('$group[0]');\n";
            }
        ?>
        //new Ajax.Autocompleter('autocomplete','autocomplete_choices','main.php?module=base&submod=users&action=ajaxAutocompleteGroup');

        new Ajax.Autocompleter('autocomplete','autocomplete_choices','modules/base/users/ajaxAutocompleteGroup.php', {paramName: "value"});

        function validOnEnter(field,event) {
            if (event.keyCode==13) {
                //addElt(field.value);
                //field.value ='';
                //field.focus();
                return false;

            }
            return true;
        }

        //add an element in selectbox
        function addElt(elt) {
            if (eltInArr(elt,groups)) {
                addEltInSelectBox(elt);
                $('autocomplete').value = '';
            }
            else {
                window.alert("<?= _("This group doesn't exist"); ?>");
            }
        }

        //verify if an element is in an array
        function eltInArr(elt,array) {
            for(var i =0; i<array.length; i++) {
                if (array[i] == elt) return true;
            }
            return false;
        }

        function addEltInSelectBox(elt) {
            var tmp = new Array();
            var len = document.getElementById('select').options.length;
            for(var i =0; i<len; i++) {
                    tmp.push(document.getElementById('select').options[0].value);
                    document.getElementById('select').options[0] = null;

            }
            if (!eltInArr(elt,tmp)) {
                tmp.push(elt);
            }

            tmp.sort();

            for(var i = 0; i<tmp.length; i++) {
                document.getElementById('select').options[i] = new Option(tmp[i],tmp[i]);
            }

        }

        function delEltInSelectBox() {
            var len = document.getElementById('select').options.length;
            for(var i =len-1; i>=0; i--) {
                if (document.getElementById('select').options[i].selected) {
                    document.getElementById('select').options[i] = null;
                }
            }
        }

       function selectAll() {
            var len = document.getElementById('select').options.length;
            for(var i = 0 ; i<len; i++) {
                document.getElementById('select').options[i].selected = true;
            }
       }
    </script>
