<?
/*
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

class RenderedMSCBundleChoice {
    function RenderedMSCBundleChoice() {
        $this->err = array();
    }
    function treatPost() {
        $members = isset($_POST["lmembers"])    ? unserialize(base64_decode($_POST["lmembers"]))    : null;
        $nonmemb = isset($_POST["lnonmemb"])    ? unserialize(base64_decode($_POST["lnonmemb"]))    : null;
        $this->list = isset($_POST["list"])     ? unserialize(base64_decode($_POST["list"]))        : null;
        if (!is_array($this->list)) {
            $this->loadList();
        }

        if (isset($_POST["bdeluser_x"])) {
            if (isset($_POST["members"])) {
                foreach ($_POST["members"] as $member) {
                    unset($members[$member]);
                }
            }
        } elseif (isset($_POST["badduser_x"])) {
            if (isset($_POST["nonmemb"])) {
                foreach ($_POST["nonmemb"] as $nm) {
                    $members[$nm] = $this->list[$nm];
                }
            }
        } elseif (isset($_POST["bconfirm"])) {
            header("Location: " . urlStrRedirect($this->set_order_uri, array('list'=>base64_encode(serialize($this->list)))));
        } else {
            $members = array();
            $nonmemb = $this->list;
        }
        ksort($members);
        reset($members);
        ksort($nonmemb);

        $this->diff = array_diff_assoc($nonmemb, $members);
        natcasesort($this->diff);
        $this->members = $members;
        $this->nonmemb = $nonmemb;
    }

    function display_start() {
?>
<form method="post">
<input name='name' value='<?php echo  $this->name ?>' type='hidden'/>
<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr>
 <td style="border: none;">
  <div class="list">
    <h3><?php echo  $this->title_left; ?></h3>
    <select multiple size="15" class="list" name="nonmemb[]">
    <?php
    foreach ($this->diff as $idx => $value) {
        print "<option value=\"".$idx."\">".$value."</option>\n";
    }
    ?>
    </select>
    <br/>
  </div>
 </td>
 <td style="border: none;">
  <div>
   <input type="image" name="bdeluser" style="padding: 5px;" src="img/common/icn_arrowleft.gif" value="<--" /><br/>
   <input type="image" name="badduser" style="padding: 5px;" src="img/common/icn_arrowright.gif" value = "-->"/>
  </div>
 </td>
 <td style="border: none;">
  <div class="list" style="padding-left: 10px;">
    <h3><?php echo  $this->title_right; ?></h3>
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

<input type="hidden" name="lnonmemb" value="<?php echo base64_encode(serialize($this->nonmemb)); ?>" />
<input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($this->members)); ?>" />
<input type="hidden" name="list" value="<?php echo base64_encode(serialize($this->list)); ?>" />
<?
    }

    function display_end() {
?>
<input type="submit" name="bsort_bundle" class="btnPrimary" value="<?php echo  _T("Set order", "msc"); ?>" />
</form>

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
    }

    function display_error() {
        if ($this->err) {
            new NotifyWidgetFailure(implode('<br/>', array_merge($this->err, array(_T("Please contact your administrator.", "msc")))));
        }
    }
}

class RenderedMSCBundleChoiceM extends RenderedMSCBundleChoice {
    function RenderedMSCBundleChoiceM($machine) {
        $this->machine = $machine;
        $this->title_right = _T('Actions in bundle', 'msc');
        $this->title_left = _T('Possible actions', 'msc');
        $this->treatPost();
    }

    function loadList() {
        $filter = array('machine'=>$this->machine->hostname, 'uuid'=>$this->machine->uuid);
        list($count, $packages) = advGetAllPackages($filter, 0, -1);
        $this->list = array();
        foreach ($packages as $c_package) {
            $p_api = new ServerAPI($c_package[2]);
            if ($c_package[0]['ERR'] && $c_package[0]['ERR'] == 'PULSE2ERROR_GETALLPACKAGE') {
                $this->err[] = sprintf(_T("MMC failed to contact package server %s.", "msc"), $c_package[0]['mirror']);
            } else {
                $this->list[$c_package[0]['id'].'##'.base64_encode(serialize($p_api->toURI()))] = $c_package[0]['label'] . " (" . $c_package[0]['version'] . ")";
            }
        }
    }

    function display() {
        parent::display_start();
        parent::display_end();
        parent::display_error();
    }
}

class RenderedMSCBundleChoiceG extends RenderedMSCBundleChoice {
    function RenderedMSCBundleChoiceG($group) {
        $this->group = $group;
        $this->title_right = _T('Actions in bundle', 'msc');
        $this->title_left = _T('Possible actions', 'msc');
        $this->treatPost();
    }

    function loadList() {
        $filter = array('group'=>$this->group->id);
        list($count, $packages) = advGetAllPackages($filter, 0, -1);
        $this->list = array();
        foreach ($packages as $c_package) {
            $p_api = new ServerAPI($c_package[2]);
            if ($c_package[0]['ERR'] && $c_package[0]['ERR'] == 'PULSE2ERROR_GETALLPACKAGE') {
                $this->err[] = sprintf(_T("MMC failed to contact package server %s.", "msc"), $c_package[0]['mirror']);
            } else {
                $this->list[$c_package[0]['id'].'##'.base64_encode(serialize($p_api->toURI()))] = $c_package[0]['label'] . " (" . $c_package[0]['version'] . ")";
            }
        }
    }

    function display() {
        parent::display_start();
        parent::display_end();
        parent::display_error();
    }
}

// SORT BUNDLE WIDGETS
class RenderedMSCBundleSortParent {
    function RenderedMSCBundleSortParent() {
        $this->input_pre = 'si_';
        $this->buttons = array(
            array('blaunch_bundle', _T("Launch Bundle", "msc"), "btnPrimary")
        );
    }
    function initCount() {
        $this->count_members = count($this->members);
        $this->c = array();
        $i = 1;
        while ($i < $this->count_members+1) { $this->c[] = $i; $i+=1; }
    }
    function get_sort_order() {
        $orders = array();
        foreach ($_POST as $k => $v) {
            if (preg_match("/^".$this->input_pre."/", $k)) {
                $id_papi = base64_decode(preg_replace("/^".$this->input_pre."/", "", $k));
                list($id, $papid) = preg_split('/##/', $id_papi);
                $p_api = new ServerAPI();
                $p_api->fromURI(unserialize(base64_decode($papid)));
                $orders[$id_papi] = array($p_api, $id, $v);
            }
        }
        return $orders;
    }
    function check_sort_order($orders) { # check if order is valid (no loop, no jumps, ...)
        return True;
    }
    function display() {
        $orders = array();
        $i = 1;
        if ($_POST["badvanced_bundle"] != '') { # advanced mode: keep previously given order if possible
            foreach ($this->members as $pid => $plabel) {
                $orders[$pid] = $_POST[$this->input_pre.base64_encode($pid)];
            }
        } else { # standard mode: generate order
            foreach ($this->members as $pid => $plabel) {
                $orders[$pid] = $i;
                $i++;
            }
        }
        $this->display_ordered($orders);
    }
    function display_ordered($orders) {
        $f = new ValidatingForm();
        $f->push(new Table());

        foreach ($this->members as $pid => $plabel) {
            $select = new SelectItem($this->input_pre.base64_encode($pid));
            $select->setElements($this->c);
            $select->setElementsVal($this->c);
            $select->setSelected($orders[$pid]);
            $f->add(new TrFormElement($plabel, $select, array()));
        }
        foreach ($this->getHidden() as $w) {
            $f->add($w[0], $w[1]);
        }
        $this->display_options($f);

        $f->pop();
        foreach ($this->buttons as $b) {
            $f->addButton($b[0], $b[1], $b[2]);
        }
        $f->display();
    }
}

class RenderedMSCBundleSort extends RenderedMSCBundleSortParent {
    function RenderedMSCBundleSort() {
        parent::RenderedMSCBundleSortParent();
        $this->buttons []= array('badvanced_bundle', _T("Advanced launch bundle", "msc"), "btnPrimary");
        $this->buttons []= array('bcancel_bundle', _T("Cancel bundle creation", "msc"), "btnSecondary");
    }
    function display_options($f) {
        $f->add(new HiddenTpl("lmembers"),                              array("value" => base64_encode(serialize($this->members)), "hide" => True));
        $f->add(new HiddenTpl("create_directory"),                      array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("start_script"),                          array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("clean_on_success"),                      array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("do_reboot"),                             array("value" => '',                                "hide" => True));
        $f->add(new HiddenTpl("bundle_title"),                          array("value" => get_new_bundle_title(count($this->members)),"hide" => True));
        $f->add(new HiddenTpl("next_connection_delay"),                 array("value" => web_def_delay(),                   "hide" => True));
        $f->add(new HiddenTpl("max_connection_attempt"),                array("value" => web_def_attempts(),                "hide" => True));
        $f->add(new HiddenTpl("maxbw"),                                 array("value" => web_def_maxbw(),                   "hide" => True));
        $f->add(new HiddenTpl("copy_mode"),                             array("value" => web_def_mode(),                    "hide" => True));
        $f->add(new HiddenTpl("deployment_intervals"),                  array("value" => web_def_deployment_intervals(),    "hide" => True));

        $halt = web_def_issue_halt_to();
        foreach ($halt as $h) {
            $f->add(new HiddenTpl("issue_halt_to_".$h),                 array("value" => 'on',                              "hide" => True));
        }

        $check = new TrFormElement(_T('awake', 'msc'), new CheckboxTpl("do_wol"));
        $f->add($check, array("value" => web_def_awake() ? "checked" : ""));
        $check = new TrFormElement(_T('invent.', 'msc'), new CheckboxTpl("do_inventory"));
        $f->add($check, array("value" => web_def_inventory() ? "checked" : ""));
    }
}

class RenderedMSCBundleSortM extends RenderedMSCBundleSort {
    function RenderedMSCBundleSortM($machine, $members) {
        parent::RenderedMSCBundleSort();
        $this->machine = $machine;
        $this->members = $members;
        $this->initCount();
    }
    function getHidden() {
        return array(
            array(new HiddenTpl("uuid"), array("value" => $this->machine->uuid, "hide" => True)),
            array(new HiddenTpl("hostname"), array("value" => $this->machine->hostname, "hide" => True))
        );
    }
}

class RenderedMSCBundleSortG extends RenderedMSCBundleSort {
    function RenderedMSCBundleSortG($group, $members) {
        parent::RenderedMSCBundleSort();
        $this->group = $group;
        $this->members = $members;
        $this->initCount();
    }
    function getHidden() {
        return array(array(new HiddenTpl("gid"), array("value" => $this->group->id, "hide" => True)));
    }
}

class RenderedMSCBundleSortAdv extends RenderedMSCBundleSortParent {
    function RenderedMSCBundleSortAdv() {
        parent::RenderedMSCBundleSortParent();
    }
    function display_options($f) {
        $f->add(new HiddenTpl("lmembers"),                              array("value" => base64_encode(serialize($this->members)), "hide" => True));
        $f->add(new TrFormElement(_T('Bundle title', 'msc'),                                new InputTpl('bundle_title')), array("value" => $_POST['bundle_title']));
        $f->add(new TrFormElement(_T('Wake on lan', 'msc'),                                 new CheckboxTpl("do_wol")), array("value" => $_POST['do_wol'] == 'on' ? 'checked' : ''));
        $f->add(new TrFormElement(_T('Start the script', 'msc'),                            new CheckboxTpl("start_script")), array("value" => 'checked'));
        $f->add(new TrFormElement(_T('Delete files after a successful execution', 'msc'),   new CheckboxTpl("clean_on_success")), array("value" => 'checked'));
        $f->add(new TrFormElement(_T('Start inventory', 'msc'),                             new CheckboxTpl("do_inventory")), array("value" => $_POST['do_inventory'] == 'on' ? 'checked' : ''));

        $f->add(new TrFormElement(_T('Halt client after', 'msc'),                           new CheckboxTpl("issue_halt_to_done", _T("done", "msc"))), array("value" => $_POST['issue_halt_to_done'] == 'on' ? 'checked' : ''));
        /*$f->add(new TrFormElement('',                                                       new CheckboxTpl("issue_halt_to_failed", _T("failed", "msc"))), array("value" => $_POST['issue_halt_to_failed'] == 'on' ? 'checked' : ''));
        $f->add(new TrFormElement('',                                                       new CheckboxTpl("issue_halt_to_over_time", _T("over time", "msc"))), array("value" => $_POST['issue_halt_to_over_time'] == 'on' ? 'checked' : ''));
        $f->add(new TrFormElement('',                                                       new CheckboxTpl("issue_halt_to_out_of_interval", _T("out of interval", "msc"))), array("value" => $_POST['issue_halt_to_out_of_interval'] == 'on' ? 'checked' : ''));*/

        $f->add(new TrFormElement(_T('Delay betwen connections (minutes)', 'msc'),          new InputTpl("next_connection_delay")), array("value" => $_POST['next_connection_delay']));
        $f->add(new TrFormElement(_T('Maximum number of connection attempt', 'msc'),        new InputTpl("max_connection_attempt")), array("value" => $_POST['max_connection_attempt']));
        $f->add(new TrFormElement(_T('Command parameters', 'msc'),                          new InputTpl('parameters')), array("value" => ''));
        $f->add(new TrFormElement(_T('Beginning of validity', 'msc'),                       new DynamicDateTpl('start_date')), array('ask_for_now' => 1));
        $f->add(new TrFormElement(_T('End of validity', 'msc'),                             new DynamicDateTpl('end_date')), array('ask_for_never' => 1));
        $f->add(new TrFormElement(_T('Deployment interval', 'msc'),                         new InputTpl('deployment_intervals')), array("value" => $_POST['deployment_intervals']));
        $f->add(new TrFormElement(_T('Max bandwidth (b/s)', 'msc'),                         new NumericInputTpl('maxbw')), array("value" => web_def_maxbw()));
        $f->add(new HiddenTpl("create_directory"),      array("value" => 'on',              "hide" => True));
        if (web_force_mode()) {
            $f->add(new HiddenTpl("copy_mode"),         array("value" => web_def_mode(),    "hide" => True));
        } else {
            $rb = new RadioTpl("copy_mode");
            $rb->setChoices(array(_T('push', 'msc'), _T('push / pull', 'msc')));
            $rb->setvalues(array('push', 'push_pull'));
            $rb->setSelected($_POST['copy_mode']);
            $f->add(new TrFormElement(_T('Copy Mode', 'msc'), $rb));
        }

        /* Only display local proxy button on a group and if allowed */
        if (isset($_GET['gid']) && strlen($_GET['gid']) && web_allow_local_proxy()) {
            $f->add(new TrFormElement(_T('Deploy using a local proxy', 'msc'),
                                      new CheckboxTpl("local_proxy")), array("value" => ''));
        }
    }
}

class RenderedMSCBundleSortAdvM extends RenderedMSCBundleSortAdv {
    function RenderedMSCBundleSortAdvM($machine, $members) {
        parent::RenderedMSCBundleSortAdv();
        $this->machine = $machine;
        $this->members = $members;
        $this->buttons []= array('bcancel_bundle', _T("Cancel bundle creation", "msc"), "btnSecondary");
        $this->initCount();
    }
    function getHidden() {
        return array(
            array(new HiddenTpl("uuid"), array("value" => $this->machine->uuid, "hide" => True)),
            array(new HiddenTpl("hostname"), array("value" => $this->machine->hostname, "hide" => True))
        );
    }
}

class RenderedMSCBundleSortAdvG extends RenderedMSCBundleSortAdv {
    function RenderedMSCBundleSortAdvG($group, $members) {
        parent::RenderedMSCBundleSortAdv();
        $this->group = $group;
        $this->members = $members;
        $this->buttons []= array('bcancel_bundle', _T("Cancel bundle creation", "msc"), "btnSecondary");
        $this->initCount();
    }
    function getHidden() {
        return array(array(new HiddenTpl("gid"), array("value" => $this->group->id, "hide" => True)));
    }
}

?>
