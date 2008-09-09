<?
/* 
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: widgets.inc.php 279 2008-08-12 13:13:06Z nrueff $
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
    function RenderedMSCBundleChoice() { }
    function treatPost() {
        $members = unserialize(base64_decode($_POST["lmembers"]));
        $nonmemb = unserialize(base64_decode($_POST["lnonmemb"]));
        $this->list = unserialize(base64_decode($_POST["list"]));
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
<form action="<? echo $this->request_uri; ?>" method="post">
<input name='name' value='<?= $this->name ?>' type='hidden'/>
<div id="grouplist">
<table style="border: none;" cellspacing="0">
<tr>
 <td style="border: none;">
  <div class="list">
    <h3><?= $this->title_left; ?></h3>
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
    <h3><?= $this->title_right; ?></h3>
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
<input type="submit" name="bsort_bundle" class="btnPrimary" value="<?= _T("Set order", "msc"); ?>" />
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
}

class RenderedMSCBundleChoiceM extends RenderedMSCBundleChoice {
    function RenderedMSCBundleChoiceM($machine) {
        $this->machine = $machine;
        $this->title_right = _T('Actions in bundle', 'msc');
        $this->title_left = _T('Possible action', 'msc');
        $this->request_uri = urlStr('base/computers/msctabs', array('tab'=>"tabbundle", 'uuid'=>$this->machine->uuid, 'hostname'=>$this->machine->hostname));
        $this->treatPost();
    }

    function loadList() {
        $filter = array('machine'=>$this->machine->hostname, 'uuid'=>$this->machine->uuid);
        list($count, $packages) = advGetAllPackages($filter, 0, -1);
        $this->list = array();
        foreach ($packages as $c_package) {
            $p_api = new ServerAPI($c_package[2]);
            $this->list[$c_package[0]['id'].'##'.base64_encode(serialize($p_api->toURI()))] = $c_package[0]['label'] . " (" . $c_package[0]['version'] . ")";
        }
    }

    function display() {
        parent::display_start();
        parent::display_end();
    }
}

class RenderedMSCBundleChoiceG extends RenderedMSCBundleChoice {
    function RenderedMSCBundleChoiceG($group) {
        $this->group = $group;
        $this->title_right = _T('Actions in bundle', 'msc');
        $this->title_left = _T('Possible action', 'msc');
        $this->request_uri = urlStr('base/computers/groupmsctabs', array('tab'=>"grouptabbundle", 'gid'=>$this->group->id));
        $this->treatPost();
    }

    function loadList() {
        $filter = array('group'=>$this->group->id); 
        list($count, $packages) = advGetAllPackages($filter, 0, -1);
        $this->list = array();
        foreach ($packages as $c_package) {
            $p_api = new ServerAPI($c_package[2]);
            $this->list[$c_package[0]['id'].'##'.base64_encode(serialize($p_api->toURI()))] = $c_package[0]['label'] . " (" . $c_package[0]['version'] . ")";
        }
    }

    function display() {
        parent::display_start();
        parent::display_end();
    }
}

// SORT BUNDLE WIDGETS
class RenderedMSCBundleSortParent {
    function RenderedMSCBundleSortParent() {
        $this->input_pre = 'si_';
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
                $id_papi = preg_replace("/^".$this->input_pre."/", "", $k);
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
        foreach ($this->members as $pid => $plabel) {
            $orders[$pid] = $i;
            $i++;
        }
        $this->display_ordered($orders);
    }
    function display_ordered($orders) {
        $f = new ValidatingForm();
        $f->push(new Table());

        foreach ($this->members as $pid => $plabel) {
            $select = new SelectItem($this->input_pre.$pid);
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
        $f->addButton('blaunch_bundle', _T("Launch bundle", "msc"), "btnPrimary");
        $f->addButton('badvanced_bundle', _T("Advanced launch bundle", "msc"), "btnSecondary");
        $f->display();
    }
}

class RenderedMSCBundleSort extends RenderedMSCBundleSortParent {
    function RenderedMSCBundleSort() {
        parent::RenderedMSCBundleSortParent();
    }
    function display_options($f) {
        $f->add(new HiddenTpl("lmembers"),                              array("value" => base64_encode(serialize($this->members)), "hide" => True));
        $f->add(new HiddenTpl("create_directory"),                      array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("start_script"),                          array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("clean_on_success"),                      array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("delete_file_after_execute_successful"),  array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("next_connection_delay"),                 array("value" => web_def_delay(),                   "hide" => True));
        $f->add(new HiddenTpl("max_connection_attempt"),                array("value" => web_def_attempts(),                "hide" => True));
        $f->add(new HiddenTpl("maxbw"),                                 array("value" => web_def_maxbw(),                   "hide" => True));
        $f->add(new HiddenTpl("copy_mode"),                             array("value" => web_def_mode(),                    "hide" => True));
        $f->add(new HiddenTpl("deployment_intervals"),                  array("value" => web_def_deployment_intervals(),    "hide" => True));

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
        $f->add(new TrFormElement(_T('Command title', 'msc'),                               new InputTpl('ltitle')), array("value" => $name));
        $f->add(new TrFormElement(_T('Wake on lan', 'msc'),                                 new CheckboxTpl("do_wol")), array("value" => $_GET['do_wol'] == 'on' ? 'checked' : ''));
        $f->add(new TrFormElement(_T('Start inventory', 'msc'),                             new CheckboxTpl("do_inventory")), array("value" => $_GET['do_inventory'] == 'on' ? 'checked' : ''));
        $f->add(new TrFormElement(_T('Start the script', 'msc'),                            new CheckboxTpl("start_script")), array("value" => 'checked'));   
        $f->add(new TrFormElement(_T('Delete files after a successful execution', 'msc'),   new CheckboxTpl("clean_on_success")), array("value" => 'checked'));
        $f->add(new TrFormElement(_T('Delay betwen connections (minuts)', 'msc'),           new InputTpl("next_connection_delay")), array("value" => $_GET['next_connection_delay']));
        $f->add(new TrFormElement(_T('Maximum number of connection attempt', 'msc'),        new InputTpl("max_connection_attempt")), array("value" => $_GET['max_connection_attempt']));
        $f->add(new TrFormElement(_T('Command parameters', 'msc'),                          new InputTpl('parameters')), array("value" => ''));                                 
        $f->add(new TrFormElement(_T('Start date', 'msc'),                                  new DynamicDateTpl('start_date')), array('ask_for_now' => 1));                      
        $f->add(new TrFormElement(_T('End date', 'msc'),                                    new DynamicDateTpl('end_date')), array('ask_for_never' => 1));                      
        $f->add(new TrFormElement(_T('Deployment interval', 'msc'),                         new InputTpl('deployment_intervals')), array("value" => $_GET['deployment_intervals']));
        $f->add(new TrFormElement(_T('Max bandwidth (b/s)', 'msc'),                         new NumericInputTpl('maxbw')), array("value" => web_def_maxbw()));
        $rb = new RadioTpl("copy_mode");
        $rb->setChoices(array(_T('push', 'msc'), _T('push / pull', 'msc')));
        $rb->setvalues(array('push', 'push_pull'));
        $rb->setSelected($_GET['copy_mode']);
        $f->add(new TrFormElement(_T('Copy Mode', 'msc'), $rb));
    

        $f->add(new HiddenTpl("create_directory"),                      array("value" => 'on',                              "hide" => True));
        $f->add(new HiddenTpl("delete_file_after_execute_successful"),  array("value" => 'on',                              "hide" => True));
    }
}

class RenderedMSCBundleSortAdvM extends RenderedMSCBundleSortAdv {
    function RenderedMSCBundleSortAdvM($machine, $members) {
        parent::RenderedMSCBundleSortAdv();
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

class RenderedMSCBundleSortAdvG extends RenderedMSCBundleSortAdv {
    function RenderedMSCBundleSortAdvG($group, $members) {
        parent::RenderedMSCBundleSortAdv();
        $this->group = $group;
        $this->members = $members;
        $this->initCount();
    }
    function getHidden() {
        return array(array(new HiddenTpl("gid"), array("value" => $this->group->id, "hide" => True)));
    }
}

?>
