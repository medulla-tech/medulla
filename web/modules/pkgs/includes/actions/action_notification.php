<?php
/**
 * (c) 2018 Siveo, http://www.siveo.net
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

extract($_POST);
/*
Descriptor Type
---------------
{
    "action": "action_notification",
    "step": 2,
    "actionlabel": "2b70431b",
    "type": "kiosk",
    "message": "test3"
}
*/
$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1>Deployment notification</h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="action_notification" />
        <?php
        extract($_POST);
        $lab =  (isset($actionlabel))? $actionlabel : uniqid(); ?>

        <table id="tableToggle">

           <tr class="toggleable">
                <th>Step label : </th>
                <th>
                    <input type="text" name="actionlabel" value="<?php echo $lab;?>"/>
                <th></th>
                <th></th>
            </tr>

            <tr>
              <td>
                Notification Type
              </td>
              <td>
                  <select name="type">
                    <option value="machine">Machine</option>
                    <option value="user">User</option>
                    <option value="kiosk">Kiosk</option>
                  </select>
              </td>
              <td>
                Notification Message
              </td>
              <? if(isset($message))
              {
                  echo '
                  <td>
                      <input type="text" name="message" value="'.$message.'"/>
                  </td>';
              }
              else{
                  echo '<td>
                          <input type="text" name="message"/>
                      </td>';
              }?>
          </tr>
          <!-- Options for kiosk notification -->
          <tr class="suboption">
            <td>
              <?php if(isset($stat))
              {?>
                <input type="checkbox" checked
                    onclick="if(jQuery(this).is(':checked')){
                                jQuery(this).closest('td').next().find('input').prop('disabled',false);
                            }
                            else{
                                jQuery(this).closest('td').next().find('input').prop('disabled',true);
                            }" />Progresion Stat
              <?php }
              else{?>
                <input type="checkbox"
                    onclick="if(jQuery(this).is(':checked')){
                                jQuery(this).closest('td').next().find('input').prop('disabled',false);
                            }
                            else{
                                jQuery(this).closest('td').next().find('input').prop('disabled',true);
                            }" />Progresion Stat
              <?php }?>
            </td>
            <td>
              <?php if (isset($stat))
              {
                echo '<input type="number" min="0" max="100" name="stat" value="'.$_POST['stat'].'"/>';
              }
              else{
                echo '<input type="number" disabled min="0" max="100" value="0" name="stat" />';
              }?>

            </td>
            <td></td>
            <td></td>
          </tr>


    </table>

    </div>

    <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="Options" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });

</script>
