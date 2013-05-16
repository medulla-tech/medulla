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

require_once("modules/dyngroup/includes/groups.inc.php");
require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require_once("modules/msc/includes/mscoptions_xmlrpc.php"); # to read msc.ini

/**
 * Input with a bigger check for a valid numeric value
 */
class MyNumericInputTpl extends InputTpl {

    function MyNumericInputTpl($name) {
        $this->InputTpl($name, '/^[1-9][0-9]*$/');
        $this->size = 2;
    }
}


class ProxySelector extends HtmlElement {

    function ProxySelector($machines, $members, $diff, $gid, $proxy_number,$local_proxy_selection_mode) {
        $this->machines = $machines;
        $this->members = $members;
        $this->diff = $diff;
        $this->gid = $gid;
        $this->proxy_number = $proxy_number;
        $this->local_proxy_selection_mode = $local_proxy_selection_mode;
    }

    function display($params = array()) {
?>

<div id="grouplist">

<script lang=javascript>
function disableLocalProxyForm() {
    changeObjectDisplay('localproxytable', 'none');
    changeObjectDisplay('container_input_proxy_number', 'inline');
}
function enableLocalProxyForm() {
    changeObjectDisplay('localproxytable', 'inline');
    changeObjectDisplay('container_input_proxy_number', 'none');
}
</script>
<input type="radio" name="local_proxy_selection_mode" value="semi_auto" onClick="javascript:disableLocalProxyForm();" <?php echo  $this->local_proxy_selection_mode == "manual" ? "" : "checked"; ?>><?php echo  _T("Random (indicate number of proxies) : ", "msc"); ?>
<?php
$num = new MyNumericInputTpl("proxy_number");
$num->display(array('value' => $this->proxy_number));
?>
<br />
<input type="radio" name="local_proxy_selection_mode" value="manual" onClick="javascript:enableLocalProxyForm();" <?php echo  $this->local_proxy_selection_mode == "manual" ? "checked" : ""; ?>><?php echo  _T("Or designate the proxies manually below : ", "msc"); ?></input>
    <table style="border: none;" cellspacing="0" id='localproxytable'>
    <tr>
     <td style="border: none;">
      <div class="list">
        <h3><?php echo  _T("Computers in this command", "msc"); ?></h3>
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
        <h3><?php echo  _T("Local proxies", "msc"); ?></h3>
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
</input>
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


<?php
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

$f = new ValidatingForm();
$f->push(new Table());
$trOptions = array('firstColWidth' => '200px');

$rb = new RadioTpl("proxy_mode");
$rb->setChoices(array(_T('Single with fallback', 'msc'), _T('Multiple', 'msc')));
$rb->setvalues(array('single', 'multiple'));
if (!empty($_POST["proxy_mode"])) {
    $proxy_mode = $_POST["proxy_mode"];
    unset($_POST["proxy_mode"]); // to prevent hidden field setting below
} else {
    $proxy_mode = web_local_proxy_mode();
}
$rb->setSelected($proxy_mode);
$f->add(new TrFormElement(_T('Local Proxy Mode', 'msc'), $rb, $trOptions));

if (!empty($_POST["max_clients_per_proxy"])) {
    $max_clients_per_proxy_value = $_POST["max_clients_per_proxy"];
    unset($_POST["max_clients_per_proxy"]); // to prevent hidden field setting below
} else {
    $max_clients_per_proxy_value = web_max_clients_per_proxy();
}
$f->add(new TrFormElement(
            _T('Maximum number of simultaneous connections to a proxy', 'msc'),
            new MyNumericInputTpl("max_clients_per_proxy"),
            $trOptions
        ), array(
            "value" => $max_clients_per_proxy_value,
            "required" => True,
        )
    );

if (!empty($_POST["proxy_number"])) {
    $proxy_number = $_POST["proxy_number"];
    unset($_POST["proxy_number"]); // to prevent hidden field setting below
} else {
    $proxy_number = web_proxy_number();
}
if (!empty($_POST["local_proxy_selection_mode"])) {
    $local_proxy_selection_mode = $_POST["local_proxy_selection_mode"];
    unset($_POST["local_proxy_selection_mode"]); // to prevent hidden field setting below
} else {
    $local_proxy_selection_mode = web_proxy_selection_mode();
}
$d = new ProxySelector($machines, $right, $left, $group->id, $proxy_number, $local_proxy_selection_mode);
$f->add(new TrFormElement(_T('Local proxies selection', 'msc'), $d, $trOptions));

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
if ($local_proxy_selection_mode != "manual") {
    ?>
<script lang=javascript>
disableLocalProxyForm(); // table is disabled when entering the page
</script></script>
    <?php } elseif ($local_proxy_selection_mode == "manual") { ?>
<script lang=javascript>
enableLocalProxyForm(); // table is disabled when entering the page
</script></script>
    <?php }
?>
