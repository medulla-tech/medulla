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

if (isset($detailArr["uid"][0])) { //if user exist
    $primary = getUserPrimaryGroup($detailArr["uid"][0]);
    $secondary = getUserSecondaryGroups($detailArr["uid"][0]);
    $user_uid = $detailArr["uid"][0];
} else {
    $primary = getUserDefaultPrimaryGroup();
    $secondary = array();
    $user_uid = "";
}
sort($secondary);

?>
   <table cellspacing="0">
    <tr>
     <td width="40%" style="text-align:right">
      <?php echo  _("Primary group"); ?>
     </td>
     <td>
      <input type="text" id="primary_autocomplete" name="primary_autocomplete" value="<?php echo  $primary; ?>" class="textfield" size="23" onkeypress="return validOnEnter(this, event);" />
      <div id="primary_autocomplete_choices" class="autocomplete">
       <ul>
        <li>A</li>
        <li>B</li>
       </ul>
      </div>
     </td>
    </tr>
   </table>
   <table cellspacing="0">
    <tr><td width="40%" style="text-align:right; vertical-align: top;"><?php echo  _("Groups"); ?> </td><td>
        <select multiple="multiple" size="10" class="list" name="groupsselected[]" id="select">
            <?php
            foreach ($secondary as $group)
            {
                echo "<option value=\"".$group."\">".$group."</option>\n";
            }
            ?>
        </select>
        <input name="bdelgroups" type="submit" class="btnPrimary" value="<?php echo  _("Delete"); ?>" onclick="delEltInSelectBox(); return false;"/>

    </td>
    </tr>
    <tr><td style="text-align:right;"><?php echo  _("Add user to group");?></td><td>

    <input type="text" id="autocomplete" name="autocomplete" class="textfield" size="23" onkeypress="return validOnEnter(this,event);" />
    <div id="autocomplete_choices" class="autocomplete">
        <ul>
            <li>A</li>
            <li>B</li>
        </ul>
    </div>
    <input name="baddgroup" type="submit" class="btnPrimary" value="<?php echo  _("Add"); ?>" onclick="addElt($F('autocomplete')); return false;"/>
    </td></tr>
    </table>

    <script type="text/javascript">

    <!--

        var groups = new Array();
        <?php
            foreach (get_groups($error) as $group)
            {
                echo "groups.push('" . htmlentities($group[0], ENT_QUOTES) . "');\n";
            }
        ?>
        new Ajax.Autocompleter('autocomplete','autocomplete_choices','modules/base/users/ajaxAutocompleteGroup.php?uid=<?php echo  $user_uid; ?>', {paramName: "value"});
        new Ajax.Autocompleter('primary_autocomplete','primary_autocomplete_choices','modules/base/users/ajaxAutocompleteGroup.php', {paramName: "value"});

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
                window.alert("<?php echo  _("This group doesn't exist"); ?>");
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
            for(var i =len-1; i>=0; i = i - 1) {
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

    -->
    </script>
