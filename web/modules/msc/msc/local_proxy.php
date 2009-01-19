<?

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

require_once("modules/dyngroup/includes/groups.inc.php");
require_once("modules/msc/includes/mscoptions_xmlrpc.php"); # to read msc.ini

class DisplayComputerSelector extends HtmlElement {

    function DisplayComputerSelector($machines, $members, $diff, $gid) {
        $this->machines = $machines;
        $this->members = $members;
        $this->diff = $diff;
        $this->gid = $gid;
    }

    function display($params = array()) {
?>

<h2><?= _T("Local Proxy Settings", "msc");?></h2>
<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr>
 <td style="border: none;">
  <div class="list">
    <h3><?= _T("Computers in this command", "msc");?></h3>
    <select multiple size="15" class="list" name="machines[]">
    <?php
    foreach ($this->diff as $idx => $machine) {
        if ($machine == "") { unset($this->machines[$idx]); continue; }
        echo "<option value=\"".$idx."\">".$machine."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
 </td>
 <td style="border: none;">
  <div>
   <input type="image" name="bdelmachine" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" /><br/>
   <input type="image" name="baddmachine" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/>
  </div>
 </td>
 <td style="border: none;">
  <div class="list" style="padding-left: 10px;">
    <h3><?= _T("Local proxies", "msc"); ?></h3>
    <select multiple size="15" class="list" name="members[]">
    <?php
    foreach ($this->members as $idx => $member) {
        if ($member == "") { unset($this->members[$idx]); continue; }
        echo "<option value=\"".$idx."\">".$member."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
  <div class="clearer"></div>
 </td>
</tr>
</table>
</div>

<input type="hidden" name="lpmachines" value="<?php echo base64_encode(serialize($this->machines)); ?>" />
<input type="hidden" name="lpmembers" value="<?php echo base64_encode(serialize($this->members)); ?>" />

<style type="text/css">
<!--
#grouplist
{
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        padding: 10px 5px 5px 10px;
        margin: 0 5px 20px 0;
        width: 632px;
}

#grouplist div.list
{
        float: left;
}

select.list
{
        width: 250px;
}
-->
</style>


<?
    } /* display */

} /* class */


function format($computer) {
    return array(
                 "hostname" => $computer[1]["cn"][0],
                 "uuid" => $computer[1]["objectUUID"][0]
                 );
}

$id = quickGet('gid');
$group = new Group($id, true);

if (isset($_POST["lpmembers"])) {
    $right = unserialize(base64_decode($_POST["lpmembers"]));
    $machines = unserialize(base64_decode($_POST["lpmachines"]));
}

if (isset($_POST["bdelmachine_x"])) {
    if (isset($_POST["members"])) {
        foreach ($_POST["members"] as $member) {
            $ma = preg_split("/##/", $member);
            unset($right[$member]);
        }
    }
} elseif (isset($_POST["baddmachine_x"])) {
    if (isset($_POST["machines"])) {
        foreach ($_POST["machines"] as $machine) {
            $ma = preg_split("/##/", $machine);
            $right[$machine] = $ma[0];
        }
    }
} else {
    /* Computers list to diplay on the left */
    if ($group->isRequest()) {
        $list = getRestrictedComputersList(0, -1, array('gid' => $id), False);
        $list = array_map(format, $list);
    } else {
        $list = $group->members();
    }

    /* all computers of the group */
    $machines = array();
    foreach ($list as $machine) {
        $machines[$machine['hostname']."##".$machine['uuid']] = $machine['hostname'];
    }
    $right = array();
}

reset($right);
ksort($machines);

$left = array_diff_assoc($machines, $right);
natcasesort($left);

$f = new Form();
$f->push(new Table());

$rb = new RadioTpl("local_proxy_mode");
$rb->setChoices(array(_T('Serial', 'msc'), _T('Parallel', 'msc')));
$rb->setvalues(array('queue', 'split'));
if (!empty($_POST["local_proxy_mode"])) {
    $rb->setSelected($_POST["local_proxy_mode"]);
    unset($_POST["local_proxy_mode"]); // to prevent hidden field setting below
} else {
    $rb->setSelected(web_local_proxy_mode());
}
$f->add(new TrFormElement(_T('Local Proxy Mode', 'msc'), $rb));

$ni = new NumericInputTpl("max_clients_per_proxy");
$ni->setSize(2);
unset($_POST["max_clients_per_proxy"]); // to prevent hidden field setting below

$tr = new TrFormElement(_T('Max. clients per proxy', 'msc'), $ni, array("value" =>"rien", "required" => True));
$f->add($tr);

$d = new DisplayComputerSelector($machines, $right, $left, $group->id);
$f->add(new TrFormElement(_T('Proxies selection', 'msc'), $d));

/* Add hidden input field to propagate the POST values from the previous
   page */
foreach($_POST as $key => $value) {
    if (!in_array($key, array("machines", "members", "lpmachines", "lpmembers", "baddmachine", "baddmachine_x", "baddmachine_y", "bdelmachine", "bdelmachine_x", "bdelmachine_y")))
        $f->add(new HiddenTpl($key), array("value" => $value, "hide" => True));
}

$f->pop();
$f->addValidateButton("bconfirmproxy");
$f->addCancelButton("bback");
$f->display();

?>